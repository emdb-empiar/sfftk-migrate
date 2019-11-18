<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes"/>

    <xsl:template match="segment/name">
        <xsl:for-each select=".">
            <xsl:copy>
                <xsl:text>This is </xsl:text><xsl:value-of select="."/>
            </xsl:copy>
        </xsl:for-each>
    </xsl:template>

    <xsl:include href="identity.xsl"/>

</xsl:stylesheet>
