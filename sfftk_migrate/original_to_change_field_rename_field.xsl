<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes"/>

    <xsl:template match="/">
        <segmentation>
            <names>
                <xsl:value-of select="/segmentation/name"/>
            </names>
            <xsl:copy-of select="/segmentation/version"/>
            <xsl:copy-of select="segmentation/segment"/>
        </segmentation>
    </xsl:template>
</xsl:stylesheet>
