import sys
from functools import partial

_print = partial(print, file=sys.stderr)

from lxml import etree

xsl_root = etree.parse('original_to_add_field.xsl')
transform = etree.XSLT(xsl_root)
_print(transform)
doc = etree.parse('original.xml')
_print(doc)
result_tree = transform(doc)
# output
_print(result_tree)
rs = str(result_tree)

output = etree.XML(str(result_tree))
pp = etree.tostring(output, pretty_print=True, xml_declaration=True, encoding='utf8')
sys.stderr.write(pp.decode('utf-8'))
