import os
import sys
from functools import partial

_print = partial(print, file=sys.stderr)

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


def migrate(original, stylesheet, **kwargs):
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
    stylesheet_doc = etree.parse(stylesheet)  # ElementTree
    transform = etree.XSLT(stylesheet_doc)  # transformer
    migrated = transform(original_doc, **kwargs)  # XSLTResultTree (like ElementTree)
    # _print("*" * 50)
    # _print(str(migrated))
    # _print("*" * 50)
    return etree.tostring(migrated, pretty_print=True, xml_declaration=True)


def main():
    migrated = migrate('original.xml', 'original_to_add_field.xsl')
    _print(type(migrated))
    # convert the migrated result to a byte sequence
    pp = etree.tostring(migrated, pretty_print=True, xml_declaration=True, encoding='utf-8')
    migrated_doc = etree.XML(pp)
    sys.stderr.write(pp.decode('utf-8'))

    return os.EX_OK


if __name__ == "__main__":
    sys.exit(main())
