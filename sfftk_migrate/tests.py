import os
import sys
import unittest

from lxml import etree

from . import begin

replace_list = [
    ('\n', ''),
    ('\t', ''),
    (' ', ''),
]


def _replace(s, vals=replace_list):
    if s is None:
        return ''
    _s = s
    for u, v in vals:
        _s = _s.replace(u, v)
    return _s


def compare_elements(el1, el2):
    """Compare two elements and all their children

    :return: True or False
    """
    begin._check(el1, (etree._Element), TypeError)
    begin._check(el2, (etree._Element), TypeError)
    # https://stackoverflow.com/questions/7905380/testing-equivalence-of-xml-etree-elementtree
    if el1.tag != el2.tag:
        return False
    if _replace(el1.text) != _replace(el2.text):
        return False
    if _replace(el1.tail) != _replace(el2.tail):
        return False
    if el1.attrib != el2.attrib:
        return False
    if len(el1) != len(el2):
        return False
    return all(compare_elements(e1, e2) for e1, e2 in zip(el1, el2))


class TestUtils(unittest.TestCase):
    def test_check(self):
        """Test that _check works"""
        with self.assertRaisesRegex(TypeError, r"object '1' is not of class <class 'str'>"):
            begin._check(1, str, TypeError)

    def test_migrate(self):
        """Test that migrate works"""

        # exceptions
        with self.assertRaises(TypeError):
            begin.migrate(1, 2)
        with self.assertRaises(IOError):
            begin.migrate('file.xml', 'file.xsl')

    def test_parse_args(self):
        """Test correct arguments"""
        args = begin.parse_args("file.xml -t 1.0", use_shlex=True)
        self.assertEqual(args.input, "file.xml")
        self.assertEqual(args.target, "1.0")
        self.assertEqual(args.output, "file_1.0.xml")

    def test_get_stylesheet(self):
        """Given versions return the correct stylesheet to use"""
        stylesheet = begin.get_stylesheet("1", "2")
        self.assertEqual(os.path.basename(stylesheet), 'migrate_v1_to_v2.xsl')
        self.assertTrue(os.path.exists(stylesheet))
        begin._print(stylesheet)
        original = os.path.join(begin.XML, 'original.xml')
        _migrated = begin.migrate(original, stylesheet, segmentation_details=etree.XSLT.strparam("Nothing much"))
        migrated = etree.ElementTree(etree.XML(_migrated))
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        # self.assertTrue(False)

    def test_get_source_version(self):
        """Obtain the version in the original"""
        source_version = begin.get_source_version(os.path.join(begin.XML, 'original.xml'))
        self.assertEqual(source_version, '1')


class TestMigrations(unittest.TestCase):
    def test_original_to_add_field(self):
        """Test adding a field to the original"""
        original = os.path.join(begin.XML, 'original.xml')
        reference = etree.parse(os.path.join(begin.XML, 'add_field.xml'))
        stylesheet = os.path.join(begin.XSL, 'original_to_add_field.xsl')
        # we pass the value of the `details` param as follows:
        # A = reference.xpath(<xpath>)[0]
        # etree.XSLT.strparam(A) - handle a possibly quoted string
        details_text = reference.xpath('/segmentation/details/text()')[0]
        _migrated = begin.migrate(original, stylesheet, segmentation_details=etree.XSLT.strparam(details_text))  # bytes
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)

    def test_original_to_drop_field(self):
        """Test dropping a field from the original"""
        original = os.path.join(begin.XML, 'original.xml')
        reference = etree.parse(os.path.join(begin.XML, 'drop_field.xml'))
        stylesheet = os.path.join(begin.XSL, 'original_to_drop_field.xsl')
        with self.assertWarns(UserWarning):
            _migrated = begin.migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_rename_field(self):
        """Test changing a field by renaming it"""
        original = os.path.join(begin.XML, 'original.xml')
        reference = etree.parse(os.path.join(begin.XML, 'change_field_rename_field.xml'))
        stylesheet = os.path.join(begin.XSL, 'original_to_change_field_rename_field.xsl')
        _migrated = begin.migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        # sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        # sys.stderr.write('\n')
        # sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_add_attribute(self):
        """Test changing a field by adding an attribute"""
        original = os.path.join(begin.XML, 'original.xml')
        reference = etree.parse(os.path.join(begin.XML, 'change_field_add_attribute.xml'))
        stylesheet = os.path.join(begin.XSL, 'original_to_change_field_add_attribute.xsl')
        lang_text = reference.xpath('/segmentation/name/@lang')[0]
        _migrated = begin.migrate(original, stylesheet, segmentation_name_lang=etree.XSLT.strparam(lang_text))
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        # sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        # sys.stderr.write('\n')
        # sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_drop_attribute(self):
        """Test changing a field by dropping an attribute"""
        original = os.path.join(begin.XML, 'original.xml')
        reference = etree.parse(os.path.join(begin.XML, 'change_field_drop_attribute.xml'))
        stylesheet = os.path.join(begin.XSL, 'original_to_change_field_drop_attribute.xsl')
        _migrated = begin.migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_change_value(self):
        """Test changing a field by changing the value"""
        original = os.path.join(begin.XML, 'original.xml')
        reference = etree.parse(os.path.join(begin.XML, 'change_field_change_value.xml'))
        stylesheet = os.path.join(begin.XSL, 'original_to_change_field_change_value.xsl')
        _segment_name = reference.xpath('/segmentation/segment[@id=1]/name/text()')[0]
        _migrated = begin.migrate(original, stylesheet, segment_name=etree.XSLT.strparam(_segment_name))
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)

    def test_original_to_change_field_rename_attribute(self):
        """Test changing a field by renaming an attribute"""
        original = os.path.join(begin.XML, 'original.xml')
        reference = etree.parse(os.path.join(begin.XML, 'change_field_rename_attribute.xml'))
        stylesheet = os.path.join(begin.XSL, 'original_to_change_field_rename_attribute.xsl')
        _migrated = begin.migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)

    def test_original_list_to_change_value_list(self):
        """Test changing all the values for a list"""
        original = os.path.join(begin.XML, 'original_list.xml')
        reference = etree.parse(os.path.join(begin.XML, 'change_value_list.xml'))
        stylesheet = os.path.join(begin.XSL, 'original_to_change_value_list.xsl')
        _migrated = begin.migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)


class TestEMDBSFFMigrations(unittest.TestCase):
    def test_v0_7_0_dev0_to_v0_8_0_dev0(self):
        """Test migration from v0.7.0.dev0 to v0.8.0.dev0"""
        original = os.path.join(begin.XML, 'test7.sff')
        stylesheet = os.path.join(begin.XSL, 'migrate_v0.7.0.dev0_to_v0.8.0.dev0.xsl')
        # phase I migration using stylesheet
        _migrated = begin.migrate(original, stylesheet)
        # convert migration to an ElementTree object
        migrated = etree.ElementTree(etree.XML(_migrated))

        _original = etree.parse(original)

        segments = _original.xpath('/segmentation/segmentList/segment')
        begin._print(segments)
        segment_meshes = dict()
        for segment in segments:
            segment_meshes[int(segment.get("id"))] = dict()
            for mesh in segment.xpath('meshList/mesh'):
                _vertices, _normals, _triangles = begin.migrate_mesh(mesh)
                segment_meshes[int(segment.get("id"))][int(mesh.get("id"))] = _vertices, _normals, _triangles

        migrated_segments = migrated.xpath('/segmentation/segment_list/segment')
        for migrated_segment in migrated_segments:
            for migrated_mesh in migrated_segment.xpath('mesh_list/mesh'):
                _vertices, _normals, _triangles = segment_meshes[int(migrated_segment.get("id"))][
                    int(migrated_mesh.get("id"))]
                migrated_mesh.insert(0, _vertices)
                migrated_mesh.insert(1, _normals)
                migrated_mesh.insert(2, _triangles)

        # let's see what it looks like
        migrated_decoded = etree.tostring(migrated, xml_declaration=True, encoding='UTF-8', pretty_print=True).decode(
            'utf-8')
        # sys.stderr.write('migrated:\n' + migrated_decoded)
        with open(os.path.join(begin.XML, 'test7_v0.8.0.dev0.sff'), 'w') as f:
            f.write(migrated_decoded)

    def test_meshes_equal_v0_7_0_dev0_vs_v0_8_0_dev0(self):
        """Test that the mesh data is the same

        We only compare surface vertices. Normal vertices correspond one-to-one to surface vertices and are not relevant
        to triangles.
        """
        v7 = os.path.join(begin.XML, 'test7.sff')
        v8 = os.path.join(begin.XML, 'test7_v0.8.0.dev0.sff')
        fv7 = etree.parse(v7)
        fv8 = etree.parse(v8)
        fv7_segments = fv7.xpath('/segmentation/segmentList/segment')
        # extract vertices, normals and triangles
        fv7_segment_meshes = dict()
        for segment in fv7_segments:
            fv7_segment_meshes[int(segment.get("id"))] = dict()
            for mesh in segment.xpath('meshList/mesh'):
                fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))] = {
                    'surface_vertices': dict(),
                    'normal_vertices': dict(),
                    'triangles': dict(),
                }
                vertex_list = next(mesh.iter('vertexList'))
                for vertex in vertex_list:
                    if vertex.get('designation') == 'surface' or vertex.get('designation') is None:
                        fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['surface_vertices'][
                            int(vertex.get('vID'))] = tuple(map(lambda v: float(v.text), vertex.xpath('*')))
                    elif vertex.get('designation') == 'normal':
                        fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['normal_vertices'][
                            int(vertex.get('vID'))] = tuple(map(lambda v: float(v.text), vertex.xpath('*')))
                triangle_list = next(mesh.iter('polygonList'))
                for triangle in triangle_list:
                    # begin._print(tuple(map(lambda t: t.text, triangle.xpath('v'))))
                    vertex_ids = list(map(lambda p: int(p.text), triangle.xpath('v')))
                    if len(vertex_ids) == 3:
                        fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['triangles'][
                            int(triangle.get('PID'))] = tuple(vertex_ids), tuple()
                    elif len(vertex_ids) == 6:
                        fv7_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['triangles'][
                            int(triangle.get('PID'))] = tuple(vertex_ids[::2]), tuple(vertex_ids[1::2])
                    else:
                        pass
        # begin._print(fv7_segment_meshes)
        fv8_segments = fv8.xpath('/segmentation/segment_list/segment')
        # extract vertices, normals and triangles
        fv8_segment_meshes = dict()
        for segment in fv8_segments:
            fv8_segment_meshes[int(segment.get("id"))] = dict()
            for mesh in segment.xpath('mesh_list/mesh'):
                fv8_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))] = dict()
                vertices = next(mesh.iter('vertices'))
                # begin._print(vertices.keys())
                # begin._print(vertices.get("data").encode("ASCII"))
                vertex_list = begin._decode_data(vertices.get("data").encode('ASCII'),
                                                 int(vertices.get("num_vertices")), vertices.get("mode"),
                                                 vertices.get("endianness"))
                vertex_tuples = list(zip(vertex_list[::3], vertex_list[1::3], vertex_list[2::3]))
                # begin._print(data_vectors)
                fv8_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['surface_vertices'] = dict(
                    zip(range(len(vertex_tuples)), vertex_tuples))
                # begin._print(data_dict)
                normals = next(mesh.iter('normals'))
                normal_list = begin._decode_data(normals.get("data").encode('ASCII'), int(normals.get("num_normals")),
                                                 normals.get("mode"), normals.get('endianness'))
                normal_tuples = list(zip(normal_list[::3], normal_list[1::3], normal_list[2::3]))
                fv8_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['normal_vertices'] = dict(
                    zip(range(len(normal_tuples)), normal_tuples))
                triangles = next(mesh.iter('triangles'))
                triangle_list = begin._decode_data(triangles.get("data").encode('ASCII'),
                                                   int(triangles.get("num_triangles")),
                                                   triangles.get("mode"), triangles.get('endianness'))
                triangle_tuples = list(zip(triangle_list[::3], triangle_list[1::3], triangle_list[2::3]))
                fv8_segment_meshes[int(segment.get("id"))][int(mesh.get("id"))]['triangles'] = dict(
                    zip(range(len(triangle_tuples)), triangle_tuples))
        # begin._print(fv8_segment_meshes)
        # compare
        fv7_surface_vertices = list()
        for segment_id in fv7_segment_meshes:
            for mesh_id in fv7_segment_meshes[segment_id]:
                for triangle_id in fv7_segment_meshes[segment_id][mesh_id]['triangles']:
                    triangle = fv7_segment_meshes[segment_id][mesh_id]['triangles'][triangle_id]
                    # begin._print(triangle)
                    # begin._print(triangle)
                    s0, s1, s2 = triangle[0]
                    # n0, n1, n2 = triangle[1]
                    fv7_surface_vertices += [fv7_segment_meshes[segment_id][mesh_id]['surface_vertices'][s0],
                                             fv7_segment_meshes[segment_id][mesh_id]['surface_vertices'][s1],
                                             fv7_segment_meshes[segment_id][mesh_id]['surface_vertices'][s2]]
        fv8_surface_vertices = list()
        for segment_id in fv8_segment_meshes:
            for mesh_id in fv8_segment_meshes[segment_id]:
                for triangle_id in fv8_segment_meshes[segment_id][mesh_id]['triangles']:
                    triangle = fv8_segment_meshes[segment_id][mesh_id]['triangles'][triangle_id]
                    # begin._print(triangle)
                    s0, s1, s2 = triangle
                    fv8_surface_vertices += [fv8_segment_meshes[segment_id][mesh_id]['surface_vertices'][s0],
                                             fv8_segment_meshes[segment_id][mesh_id]['surface_vertices'][s1],
                                             fv8_segment_meshes[segment_id][mesh_id]['surface_vertices'][s2]]
        # begin._print(fv7_surface_vertices[1283])
        # begin._print(fv8_surface_vertices[1283])
        self.assertEqual(len(fv7_surface_vertices), len(fv8_surface_vertices))
        for u, v in zip(fv7_surface_vertices, fv8_surface_vertices):
            self.assertAlmostEqual(u[0], v[0])
            self.assertAlmostEqual(u[1], v[1])
            self.assertAlmostEqual(u[2], v[2])
