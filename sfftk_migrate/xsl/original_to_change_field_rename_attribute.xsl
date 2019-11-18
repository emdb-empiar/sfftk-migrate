<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes"/>

    <xsl:include href="identity.xsl"/>

    <!-- rename all `id` attributes to `segment_id` -->
    <xsl:template match="@id">
        <xsl:attribute name="segment_id">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>

</xsl:stylesheet>
