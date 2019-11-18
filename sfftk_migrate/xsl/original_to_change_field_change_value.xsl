<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>

    <xsl:include href="identity.xsl"/>

    <xsl:param name="segment_name"/>

    <xsl:template match="segment[@id=1]/name">
        <name>
            <xsl:value-of select="$segment_name"/>
        </name>
    </xsl:template>

</xsl:stylesheet>
