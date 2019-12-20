<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">

    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes"/>

    <xsl:include href="identity.xsl"/>

    <!-- newline param -->
    <xsl:variable name="newline">
        <xsl:text>&#xa;</xsl:text>
    </xsl:variable>

    <!-- one-tab -->
    <xsl:variable name="tab-1">
        <xsl:text>&#009;</xsl:text>
    </xsl:variable>

    <!-- trow-tab -->
    <xsl:variable name="tab-2">
        <xsl:text>&#009;&#009;</xsl:text>
    </xsl:variable>

    <!-- three-tab -->
    <xsl:variable name="tab-3">
        <xsl:text>&#009;&#009;&#009;</xsl:text>
    </xsl:variable>

    <!-- four-tab -->
    <xsl:variable name="tab-4">
        <xsl:text>&#009;&#009;&#009;&#009;</xsl:text>
    </xsl:variable>

    <!-- five-tab -->
    <xsl:variable name="tab-5">
        <xsl:text>&#009;&#009;&#009;&#009;&#009;</xsl:text>
    </xsl:variable>

    <xsl:template match="/segmentation/version">
        <version>
            <xsl:text>v0.8.0.dev0</xsl:text>
        </version>
    </xsl:template>

    <!-- primary descriptor -->
    <xsl:template match="/segmentation/primaryDescriptor">
        <primary_descriptor>
            <xsl:choose>
                <xsl:when test=".='threeDVolume'">
                    <xsl:text>three_d_volume</xsl:text>
                </xsl:when>
                <xsl:when test=".='meshList'">
                    <xsl:text>mesh_list</xsl:text>
                </xsl:when>
                <xsl:when test=".='shapePrimitiveList'">
                    <xsl:text>shape_primitive_list</xsl:text>
                </xsl:when>
            </xsl:choose>
        </primary_descriptor>
    </xsl:template>

    <!-- software -->
    <xsl:template match="/segmentation/software">
        <software_list>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-2"/>
            <software>
                <!-- when migrating software the existing software will always be index 0 -->
                <xsl:attribute name="id">0</xsl:attribute>
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-3"/>
                <xsl:copy-of select="./name"/>
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-3"/>
                <xsl:copy-of select="./version"/>
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-3"/>
                <processing_details>
                    <xsl:value-of select="./processingDetails"/>
                </processing_details>
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
            </software>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </software_list>
    </xsl:template>

    <!-- bounding box -->
    <xsl:template match="/segmentation/boundingBox">
        <bounding_box>
            <xsl:value-of select="."/>
        </bounding_box>
    </xsl:template>

    <!-- transform list -->
    <xsl:template match="/segmentation/transformList">
        <transform_list>
            <xsl:for-each select="transformationMatrix">
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
                <transformation_matrix>
                    <xsl:attribute name="id">
                        <xsl:value-of select="@id"/>
                    </xsl:attribute>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:copy-of select="rows"/>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:copy-of select="cols"/>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:copy-of select="data"/>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-2"/>
                </transformation_matrix>
            </xsl:for-each>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </transform_list>
    </xsl:template>

    <!-- global external references -->
    <xsl:template match="/segmentation/globalExternalReferences">
        <global_external_references>
            <xsl:for-each select="./ref">
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
                <ref>
                    <xsl:choose>
                        <xsl:when test="@id">
                            <xsl:attribute name="id">
                                <xsl:value-of select="@id"/>
                            </xsl:attribute>
                        </xsl:when>
                    </xsl:choose>
                    <xsl:attribute name="resource">
                        <xsl:value-of select="@type"/>
                    </xsl:attribute>
                    <xsl:attribute name="url">
                        <xsl:value-of select="@otherType"/>
                    </xsl:attribute>
                    <xsl:attribute name="accession">
                        <xsl:value-of select="@value"/>
                    </xsl:attribute>
                    <xsl:copy-of select="@label"/>
                    <xsl:copy-of select="@description"/>
                </ref>
            </xsl:for-each>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </global_external_references>
    </xsl:template>

    <!-- segments -->
    <xsl:template match="/segmentation/segmentList">
        <segment_list>
            <xsl:for-each select="./segment">
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
                <segment>
                    <xsl:copy-of select="@id"/>
                    <xsl:attribute name="parent_id">
                        <xsl:value-of select="@parentID"/>
                    </xsl:attribute>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <biological_annotation>
                        <xsl:copy-of select="$newline"/>
                        <xsl:copy-of select="$tab-4"/>
                        <xsl:copy-of select="./biologicalAnnotation/name"/>
                        <xsl:copy-of select="$newline"/>
                        <xsl:copy-of select="$tab-4"/>
                        <xsl:copy-of select="./biologicalAnnotation/description"/>
                        <xsl:copy-of select="$newline"/>
                        <xsl:copy-of select="$tab-4"/>
                        <external_references>
                            <xsl:for-each select="./biologicalAnnotation/externalReferences/ref">
                                <xsl:copy-of select="$newline"/>
                                <xsl:copy-of select="$tab-5"/>
                                <ref>
                                    <xsl:match select="@id">
                                        <xsl:attribute name="id">
                                            <xsl:value-of select="@id"/>
                                        </xsl:attribute>
                                    </xsl:match>
                                    <xsl:attribute name="resource">
                                        <xsl:value-of select="@type"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="url">
                                        <xsl:value-of select="@otherType"/>
                                    </xsl:attribute>
                                    <xsl:attribute name="accession">
                                        <xsl:value-of select="@value"/>
                                    </xsl:attribute>
                                    <xsl:copy-of select="@label"/>
                                    <xsl:copy-of select="@description"/>
                                </ref>
                            </xsl:for-each>
                            <xsl:copy-of select="$newline"/>
                            <xsl:copy-of select="$tab-4"/>
                        </external_references>
                        <xsl:copy-of select="$newline"/>
                        <xsl:copy-of select="$tab-3"/>
                    </biological_annotation>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <xsl:copy-of select="./colour"/>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-3"/>
                    <three_d_volume>
                        <xsl:copy-of select="$newline"/>
                        <xsl:copy-of select="$tab-4"/>
                        <lattice_id><xsl:value-of select="./threeDVolume/latticeId"/></lattice_id>
                        <xsl:copy-of select="$newline"/>
                        <xsl:copy-of select="$tab-4"/>
                        <xsl:copy-of select="./threeDVolume/value"/>
                        <xsl:copy-of select="$newline"/>
                        <xsl:choose>
                            <xsl:when test="./threeDVolume/transformId">
                                <xsl:copy-of select="$tab-4"/>
                                <transform_id>
                                    <xsl:value-of select="./threeDVolume/transformId"/>
                                </transform_id>
                                <xsl:copy-of select="$newline"/>
                            </xsl:when>
                        </xsl:choose>
                        <xsl:copy-of select="$tab-3"/>
                    </three_d_volume>
                    <xsl:copy-of select="$newline"/>
                    <xsl:copy-of select="$tab-2"/>
                </segment>
            </xsl:for-each>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </segment_list>
    </xsl:template>

    <!-- lattice list -->
    <xsl:template match="/segmentation/latticeList">
        <lattice_list>
            <xsl:for-each select="./lattice">
                <xsl:copy-of select="$newline"/>
                <xsl:copy-of select="$tab-2"/>
                <xsl:copy-of select="."/>
            </xsl:for-each>
            <xsl:copy-of select="$newline"/>
            <xsl:copy-of select="$tab-1"/>
        </lattice_list>
    </xsl:template>

</xsl:stylesheet>
