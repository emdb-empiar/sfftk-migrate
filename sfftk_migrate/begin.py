import os
import sys
import warnings
from functools import partial

_print = partial(print, file=sys.stderr)

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__))
XSL = os.path.join(TEST_DATA_PATH, 'xsl')
XML = os.path.join(TEST_DATA_PATH, 'xml')

"""
Lessons learned in using `lxml`
---------------------------------
etree.parse() takes XML files/file objects and returns an ElementTree
etree.XML() takes a string and returns an Element regardless of the content
etree.ElementTree(root_element) converts an element into an ElementTree
etree.XSLT() takes an ElementTree or Element object and returns a transformer object
a transformer object should take an ElementTree (but seems to also take Element objects)
the result of a transformation is an _XSLTResultTree which behaves like an ElementTree but submits to str()
"""

from lxml import etree
import struct
import base64

# todo: editing complex elements
"""
from: https://lxml.de/xpathxslt.html#xslt-result-objects
It is possible to pass parameters, in the form of XPath expressions, to the XSLT template:

>>> xslt_tree = etree.XML('''\
... <xsl:stylesheet version="1.0"
...     xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
...     <xsl:param name="a" />
...     <xsl:template match="/">
...         <foo><xsl:value-of select="$a" /></foo>
...     </xsl:template>
... </xsl:stylesheet>''')
>>> transform = etree.XSLT(xslt_tree)
>>> doc_root = etree.XML('<a><b>Text</b></a>')

The parameters are passed as keyword parameters to the transform call. First, let's try passing in a simple integer expression:

>>> result = transform(doc_root, a="5")
>>> str(result)
'<?xml version="1.0"?>\n<foo>5</foo>\n'

"""


def _check(obj, klass, exception=Exception, message="object '{}' is not of class {}"):
    """
    Check that `obj` is of type `klass` else raise `exception`
    :param obj: some object
    :param type klass: some class
    :param Exception exception: the exception to raise
    """
    try:
        assert isinstance(obj, klass)
    except AssertionError:
        if message.find("{}"):
            raise exception(message.format(obj, klass))
        else:
            raise exception(message)


def migrate_mesh(mesh, vertices_mode="float32", triangles_mode="uint32", endianness="little"):
    """Given a mesh from the v0.7.0.dev0 we convert it to a mesh in v0.8.0.dev0"""

    ENDIANNESS = {
        "little": "<",
        "big": ">",
    }
    MODE = {
        "int8": "b",
        "uint8": "B",
        "int16": "h",
        "uint16": "H",
        "int32": "i",
        "uint32": "I",
        "int64": "q",
        "uint64": "Q",
        "float32": "f",
        "float64": "d"
    }

    # assertions
    try:
        assert endianness in ["little", "big"]
    except AssertionError:
        raise ValueError("invalid endianness: {}".format(endianness))
    try:
        assert triangles_mode in ["int8", "uint8", "int16", "uint16", "int32", "uint32", "int64", "uint64"]
    except AssertionError:
        raise ValueError("invalid triangles mode: {}".format(triangles_mode))
    try:
        assert vertices_mode in ["float32", "float64"]
    except AssertionError:
        raise ValueError("invalid vertices mode: {}".format(vertices_mode))

    surface_vertex_dict = dict()  # dictionary to remap vertex ids
    surface_vertices = list()
    normal_vertices = list()
    vertex_list = next(mesh.iter("vertexList"))
    i = 0
    for vertex in vertex_list.iter("v"):
        designation = vertex.get("designation")
        x, y, z = vertex.xpath("*")
        # 'surface' vertex by default
        if designation is None or designation == "surface":
            surface_vertex_dict[int(vertex.get("vID"))] = len(surface_vertices) // 3  # len = index
            surface_vertices += [float(x.text), float(y.text), float(z.text)]
        else:
            normal_vertices += [float(x.text), float(y.text), float(z.text)]
    # _print(surface_vertex_dict)
    # sanity check: normal_vertices should have the same length as surface_vertices list if it exists
    if normal_vertices:
        try:
            assert len(surface_vertices) == len(normal_vertices)
        except AssertionError:
            raise ValueError("surface and normal vertice lists are of different length")
    bin_surface_vertices = struct.pack(
        "{}{}{}".format(ENDIANNESS[endianness], len(surface_vertices), MODE[vertices_mode]), *surface_vertices)
    base64_surface_vertices = base64.b64encode(bin_surface_vertices)
    bin_normal_vertices = struct.pack(
        "{}{}{}".format(ENDIANNESS[endianness], len(normal_vertices), MODE[vertices_mode]), *normal_vertices)
    base64_normal_vertices = base64.b64encode(bin_normal_vertices)
    surface_vertices_element = etree.Element("vertices", num_vertices=str(len(surface_vertices) // 3), mode=vertices_mode,
                                             endianness=endianness, data=base64_surface_vertices)
    surface_vertices_element.tail = "\n\t\t\t\t\t"
    normal_vertices_element = etree.Element("normals", num_normals=str(len(normal_vertices) // 3), mode=vertices_mode,
                                            endianness=endianness, data=base64_normal_vertices)
    normal_vertices_element.tail = "\n\t\t\t\t\t"

    # work on triangles
    triangles = list()
    triangle_list = next(mesh.iter("polygonList"))
    for triangle in triangle_list.iter("P"):
        vertex_indices = triangle.xpath("*")
        if len(vertex_indices) == 3:  # no normals
            _v1, _v2, _v3 = vertex_indices
            v1 = int(_v1.text)
            v2 = int(_v2.text)
            v3 = int(_v3.text)
        elif len(vertex_indices) == 6:  # s, n, s, n, s, n
            _v1, _n1, _v2, _n2, _v3, _n3 = vertex_indices
            # get the new index
            v1 = surface_vertex_dict[int(_v1.text)]
            v2 = surface_vertex_dict[int(_v2.text)]
            v3 = surface_vertex_dict[int(_v3.text)]
        else:
            raise ValueError("invalid polygon: should have 3 or 6 vertices only")

        triangles += [v1, v2, v3]
    # sanity check: there should be no triangle with a vertex id larger than the length of vertices/normals
    try:
        assert max(triangles) < len(surface_vertices)
    except AssertionError:
        raise ValueError("triangle with non-existent vertex found!")
    bin_triangles = struct.pack("{}{}{}".format(ENDIANNESS[endianness], len(triangles), MODE[triangles_mode]), *triangles)
    base64_triangles = base64.b64encode(bin_triangles)
    triangles_element = etree.Element("triangles", num_triangles=str(len(triangles) // 3), mode=triangles_mode,
                                      endianness=endianness, data=base64_triangles)
    triangles_element.tail = "\n\t\t\t\t"

    return surface_vertices_element, normal_vertices_element, triangles_element


def migrate(original, stylesheet, verbose=False, **kwargs):
    """
    Migrate `original` according to `stylesheet`

    :param str original: the name of an XML file
    :param str stylesheet: the name of an XSLT file
    :return: the transformed XML document
    :rtype: bytes
    """
    _check(original, str, TypeError)
    _check(stylesheet, str, TypeError)
    original_doc = etree.parse(original)  # ElementTree
    original_elements = set([original_doc.getpath(element) for element in original_doc.iter()])
    # _print('original_doc:', original_elements)
    stylesheet_doc = etree.parse(stylesheet)  # ElementTree
    transform = etree.XSLT(stylesheet_doc)  # transformer
    migrated = transform(original_doc, **kwargs)  # XSLTResultTree (like ElementTree)
    migrated_elements = set([migrated.getpath(element) for element in migrated.iter()])
    # _print('migrated_doc:', migrated_elements)
    dropped_fields = original_elements.difference(migrated_elements)
    # _print('difference:', dropped_fields)
    if dropped_fields and len(original_elements) > len(migrated_elements) and verbose:
        warnings.warn(
            UserWarning('the migration has resulted in the following fields being dropped: {}'.format(
                ', '.join(dropped_fields))),
        )
    return etree.tostring(migrated, pretty_print=True, xml_declaration=True)


def get_source_version(fn):
    """
    Return the version of the document

    The version will always be in /segmentation/version

    :param str fn: filename as a string
    :return: version
    :rtype: str
    """
    source_tree = etree.parse(fn)
    source_version = source_tree.xpath("/segmentation/version/text()")[0]
    return source_version


def do_migrate(args):
    source = get_source_version(args.original)
    stylesheet = get_stylesheet(source, args.target)
    migrated = migrate(args.original, stylesheet)  # bytes
    with open(args.output, 'w') as m:
        m.write(migrated.encode('utf-8'))
        m.flush()
    return os.EX_OK


def get_stylesheet(source, target, prefix="migrate"):
    stylesheet = os.path.join(XSL,
                              "{prefix}_v{source}_to_v{target}.xsl".format(prefix=prefix, source=source, target=target))
    assert os.path.exists(os.path.join(XSL, stylesheet))
    return stylesheet


def parse_args(args, use_shlex=True):
    if use_shlex:
        import shlex
        _args = shlex.split(args)
    import argparse
    parser = argparse.ArgumentParser(prog='sff-migrate', description='Upgrade EMDB-SFF files to more recent schema')
    parser.add_argument('input', help='input XML file')
    parser.add_argument('-t', '--target', required=True, help='the target version to migrate to')
    parser.add_argument('-o', '--output', required=False, help='output file [default: <input>_<target>.xml]')

    args = parser.parse_args(_args)

    if args.output is None:
        input_fn = args.input.split('.')
        root, ext = '.'.join(input_fn[:-1]), input_fn[-1]
        args.output = os.path.join(
            os.path.dirname(args.input),
            '{root}_{target}.{ext}'.format(
                root=root,
                target=args.target,
                ext=ext
            )
        )
    return args


def main():
    # migrated = migrate('original.xml', 'original_to_add_field.xsl')
    _migrated = migrate(os.path.join(XML, 'original.xml'), os.path.join(XSL, 'original_to_drop_field.xsl'))  # bytes
    # convert the migrated result to a byte sequence
    migrated = etree.ElementTree(etree.XML(_migrated))
    pp = etree.tostring(migrated, pretty_print=True, xml_declaration=True, encoding='utf-8')
    sys.stderr.write(pp.decode('utf-8'))

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
