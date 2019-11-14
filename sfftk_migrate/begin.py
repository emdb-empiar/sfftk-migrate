import sys

from lxml import etree

xsl_root = etree.parse('original_to_add_field.xsl')
transform = etree.XSLT(xsl_root)
print(transform, file=sys.stderr)
doc = etree.parse('original.xml')
print(doc, file=sys.stderr)
result_tree = transform(doc)
print(str(result_tree), file=sys.stderr)
