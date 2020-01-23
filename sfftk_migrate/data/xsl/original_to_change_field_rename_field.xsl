<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes"/>

    <xsl:template match="/segmentation/name">
        <names>
            <xsl:value-of select="/segmentation/name"/>
        </names>
    </xsl:template>

    <xsl:include href="identity.xsl"/>

</xsl:stylesheet>
