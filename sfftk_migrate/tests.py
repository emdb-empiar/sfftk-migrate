import os
import sys
import unittest

from lxml import etree

from .begin import migrate, _check, _print

TEST_DATA_PATH = os.path.dirname(__file__)

XML = os.path.join(TEST_DATA_PATH, 'xml')
XSL = os.path.join(TEST_DATA_PATH, 'xsl')

replace_list = [
    ('\n', ''),
    ('\t', ''),
    (' ', ''),
]


def _replace(s, vals=replace_list):
    if s is None:
        return s
    _s = s
    for u, v in vals:
        _s = _s.replace(u, v)
    return _s


def compare_elements(el1, el2):
    """Compare two elements and all their children

    :return: True or False
    """
    _check(el1, (etree._Element), TypeError)
    _check(el2, (etree._Element), TypeError)
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
            _check(1, str, TypeError)

    def test_migrate(self):
        """Test that migrate works"""

        # exceptions
        with self.assertRaises(TypeError):
            migrate(1, 2)
        with self.assertRaises(IOError):
            migrate('file.xml', 'file.xsl')


class TestMigrations(unittest.TestCase):
    def test_original_to_add_field(self):
        """Test adding a field to the original"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'add_field.xml'))
        stylesheet = os.path.join(XSL, 'original_to_add_field.xsl')
        # we pass the value of the `details` param as follows:
        # A = reference.xpath(<xpath>)[0]
        # etree.XSLT.strparam(A) - handle a possibly quoted string
        details_text = reference.xpath('/segmentation/details/text()')[0]
        _migrated = migrate(original, stylesheet, segmentation_details=etree.XSLT.strparam(details_text))  # bytes
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
        self.assertTrue(same)

    def test_original_to_drop_field(self):
        """Test dropping a field from the original"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'drop_field.xml'))
        stylesheet = os.path.join(XSL, 'original_to_drop_field.xsl')
        with self.assertWarns(UserWarning):
            _migrated = migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_rename_field(self):
        """Test changing a field by renaming it"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_rename_field.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_rename_field.xsl')
        _migrated = migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        # sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        # sys.stderr.write('\n')
        # sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_add_attribute(self):
        """Test changing a field by adding an attribute"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_add_attribute.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_add_attribute.xsl')
        lang_text = reference.xpath('/segmentation/name/@lang')[0]
        _migrated = migrate(original, stylesheet, segmentation_name_lang=etree.XSLT.strparam(lang_text))
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        # sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        # sys.stderr.write('\n')
        # sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_drop_attribute(self):
        """Test changing a field by dropping an attribute"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_drop_attribute.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_drop_attribute.xsl')
        _migrated = migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_change_value(self):
        """Test changing a field by changing the value"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_change_value.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_change_value.xsl')
        _segment_name = reference.xpath('/segmentation/segment[@id=1]/name/text()')[0]
        _migrated = migrate(original, stylesheet, segment_name=etree.XSLT.strparam(_segment_name))
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))

    def test_original_to_change_field_rename_attribute(self):
        """Test changing a field by changing the value"""
        original = os.path.join(XML, 'original.xml')
        reference = etree.parse(os.path.join(XML, 'change_field_rename_attribute.xml'))
        stylesheet = os.path.join(XSL, 'original_to_change_field_rename_attribute.xsl')
        _migrated = migrate(original, stylesheet)
        migrated = etree.ElementTree(etree.XML(_migrated))
        same = compare_elements(reference.getroot(), migrated.getroot())
        self.assertTrue(same)
        sys.stderr.write('reference:\n' + etree.tostring(reference).decode('utf-8'))
        sys.stderr.write('\n')
        sys.stderr.write('migrated:\n' + etree.tostring(migrated).decode('utf-8'))
