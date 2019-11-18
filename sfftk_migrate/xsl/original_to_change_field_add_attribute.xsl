<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>

    <!--param-->
    <xsl:param name="segmentation_name_lang"/>

    <!-- add attribute to name-->
    <xsl:template match="/segmentation/name">
        <name>
            <xsl:attribute name="lang">
                <xsl:value-of select="$segmentation_name_lang"/>
            </xsl:attribute>
            <xsl:value-of select="/segmentation/name"/>
        </name>
    </xsl:template>

    <xsl:include href="identity.xsl"/>

</xsl:stylesheet>
