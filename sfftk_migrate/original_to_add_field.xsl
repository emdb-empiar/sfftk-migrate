<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>

    <!--params-->
    <xsl:param name="details"/>

    <xsl:template match="/">
        <segmentation>
            <xsl:copy-of select="segmentation/name"/>
            <xsl:copy-of select="segmentation/version"/>
            <xsl:copy-of select="segmentation/segment"/>
            <details>
                <xsl:value-of select="$details"/>
            </details>
        </segmentation>
    </xsl:template>

</xsl:stylesheet>
