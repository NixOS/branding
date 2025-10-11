<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- Emit plain text so we fully control line breaks -->
  <xsl:output method="text" encoding="UTF-8"/>

  <!-- Config: spaces per indentation level -->
  <xsl:param name="indent" select="2"/>

  <!-- helpers -->
  <xsl:template name="repeat">
    <xsl:param name="ch"/>
    <xsl:param name="n" select="0"/>
    <xsl:if test="$n &gt; 0">
      <xsl:value-of select="$ch"/>
      <xsl:call-template name="repeat">
        <xsl:with-param name="ch" select="$ch"/>
        <xsl:with-param name="n" select="$n - 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <xsl:template name="pad">
    <xsl:param name="depth" select="0"/>
    <xsl:call-template name="repeat">
      <xsl:with-param name="ch" select="' '"/>
      <xsl:with-param name="n" select="$depth"/>
    </xsl:call-template>
  </xsl:template>

  <!-- entry -->
  <xsl:template match="/">
    <xsl:apply-templates select="node()">
      <xsl:with-param name="depth" select="0"/>
    </xsl:apply-templates>
  </xsl:template>

  <!-- elements -->
  <xsl:template match="*">
    <xsl:param name="depth" select="0"/>
    <xsl:variable name="padsp" select="$depth * $indent"/>

    <!-- opening tag on its own line -->
    <xsl:call-template name="pad"><xsl:with-param name="depth" select="$padsp"/></xsl:call-template>
    <xsl:text>&lt;</xsl:text><xsl:value-of select="name()"/><xsl:text>&gt;</xsl:text>
    <xsl:text>
</xsl:text>

    <!-- attributes (special first), each on its own line -->
    <xsl:apply-templates select="@points">
      <xsl:with-param name="pad" select="$padsp + $indent"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="@transform">
      <xsl:with-param name="pad" select="$padsp + $indent"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="@d">
      <xsl:with-param name="pad" select="$padsp + $indent"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="@viewBox">
      <xsl:with-param name="pad" select="$padsp + $indent"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="@*[name()!='points' and name()!='transform' and name()!='d' and name()!='viewBox']">
      <xsl:with-param name="pad" select="$padsp + $indent"/>
    </xsl:apply-templates>

    <!-- text nodes -->
    <xsl:apply-templates select="text()">
      <xsl:with-param name="depth" select="$depth + 1"/>
    </xsl:apply-templates>

    <!-- children -->
    <xsl:apply-templates select="node()[self::*]">
      <xsl:with-param name="depth" select="$depth + 1"/>
    </xsl:apply-templates>

    <!-- closing tag on its own line -->
    <xsl:call-template name="pad"><xsl:with-param name="depth" select="$padsp"/></xsl:call-template>
    <xsl:text>&lt;/</xsl:text><xsl:value-of select="name()"/><xsl:text>&gt;</xsl:text>
    <xsl:text>
</xsl:text>
  </xsl:template>

  <!-- text nodes (trim + own line) -->
  <xsl:template match="text()">
    <xsl:param name="depth" select="0"/>
    <xsl:variable name="t" select="normalize-space(.)"/>
    <xsl:if test="$t != ''">
      <xsl:variable name="padsp" select="$depth * $indent"/>
      <xsl:call-template name="pad"><xsl:with-param name="depth" select="$padsp"/></xsl:call-template>
      <xsl:text>#text: </xsl:text><xsl:value-of select="$t"/>
      <xsl:text>
</xsl:text>
    </xsl:if>
  </xsl:template>

  <!-- default attribute: one per line -->
  <xsl:template match="@*">
    <xsl:param name="pad" select="0"/>
    <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
    <xsl:text>@</xsl:text><xsl:value-of select="name()"/><xsl:text>: </xsl:text>
    <xsl:value-of select="normalize-space(.)"/>
    <xsl:text>
</xsl:text>
  </xsl:template>

    <!-- @points: one x y pair per line, with stable index -->
  <xsl:template match="@points">
    <xsl:param name="pad" select="0"/>
    <xsl:variable name="norm" select="normalize-space(translate(., ',', ' '))"/>

    <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
    <xsl:text>@points:</xsl:text>
    <xsl:text>
</xsl:text>

    <!-- start indexing at 1 -->
    <xsl:call-template name="emit-points-lines">
      <xsl:with-param name="s" select="$norm"/>
      <xsl:with-param name="pad" select="$pad + $indent"/>
      <xsl:with-param name="idx" select="1"/>
    </xsl:call-template>
  </xsl:template>

  <!-- Recursive tokenizer/pairer for points with index -->
  <xsl:template name="emit-points-lines">
    <xsl:param name="s"/>
    <xsl:param name="pad" select="0"/>
    <xsl:param name="idx" select="1"/>

    <xsl:variable name="sn" select="normalize-space($s)"/>
    <xsl:if test="$sn != ''">
      <xsl:variable name="x" select="substring-before(concat($sn,' '), ' ')"/>
      <xsl:variable name="rest1" select="normalize-space(substring-after(concat($sn,' '), ' '))"/>
      <xsl:variable name="y" select="substring-before(concat($rest1,' '), ' ')"/>
      <xsl:variable name="rest2" select="normalize-space(substring-after(concat($rest1,' '), ' '))"/>

      <xsl:call-template name="pad">
        <xsl:with-param name="depth" select="$pad"/>
      </xsl:call-template>

      <!-- Stable, zero-padded index: [0001], [0002], ... -->
      <xsl:text>[</xsl:text><xsl:value-of select="format-number($idx, '0000')"/><xsl:text>] </xsl:text>

      <xsl:value-of select="$x"/>
      <xsl:if test="$y != ''">
        <xsl:text> </xsl:text><xsl:value-of select="$y"/>
      </xsl:if>
      <xsl:text>
</xsl:text>

      <!-- Recurse with next index -->
      <xsl:call-template name="emit-points-lines">
        <xsl:with-param name="s" select="$rest2"/>
        <xsl:with-param name="pad" select="$pad"/>
        <xsl:with-param name="idx" select="$idx + 1"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!-- @viewBox: one number per line -->
  <xsl:template match="@viewBox">
    <xsl:param name="pad" select="0"/>
    <!-- Normalize commas to spaces, collapse whitespace -->
    <xsl:variable name="norm" select="normalize-space(translate(., ',', ' '))"/>

    <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
    <xsl:text>@viewBox:</xsl:text>
    <xsl:text>
</xsl:text>

    <xsl:call-template name="emit-space-tokens">
      <xsl:with-param name="s" select="$norm"/>
      <xsl:with-param name="pad" select="$pad + $indent"/>
    </xsl:call-template>
  </xsl:template>

  <!-- helper: print space-separated tokens, one per line -->
  <xsl:template name="emit-space-tokens">
    <xsl:param name="s"/>
    <xsl:param name="pad" select="0"/>

    <xsl:variable name="sn" select="normalize-space($s)"/>
    <xsl:if test="$sn != ''">
      <xsl:variable name="tok" select="substring-before(concat($sn,' '), ' ')"/>
      <xsl:variable name="rest" select="normalize-space(substring-after(concat($sn,' '), ' '))"/>

      <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
      <xsl:value-of select="$tok"/>
      <xsl:text>
</xsl:text>

      <xsl:call-template name="emit-space-tokens">
        <xsl:with-param name="s" select="$rest"/>
        <xsl:with-param name="pad" select="$pad"/>
      </xsl:call-template>
    </xsl:if>
  </xsl:template>

  <!-- @transform: one operation per line (split on ')') -->
  <xsl:template match="@transform">
    <xsl:param name="pad" select="0"/>
    <xsl:variable name="t" select="normalize-space(translate(., ',', ' '))"/>

    <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
    <xsl:text>@transform:</xsl:text>
    <xsl:text>
</xsl:text>

    <xsl:call-template name="emit-transform-lines">
      <xsl:with-param name="s" select="$t"/>
      <xsl:with-param name="pad" select="$pad + $indent"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="emit-transform-lines">
    <xsl:param name="s"/>
    <xsl:param name="pad" select="0"/>

    <xsl:variable name="sn" select="normalize-space($s)"/>
    <xsl:if test="$sn != ''">
      <xsl:choose>
        <xsl:when test="contains($sn, ')')">
          <xsl:variable name="head" select="normalize-space(substring-before($sn, ')'))"/>
          <xsl:variable name="tail" select="substring-after($sn, ')')"/>

          <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
          <xsl:value-of select="$head"/><xsl:text>)</xsl:text>
          <xsl:text>
</xsl:text>

          <xsl:call-template name="emit-transform-lines">
            <xsl:with-param name="s" select="$tail"/>
            <xsl:with-param name="pad" select="$pad"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
          <xsl:value-of select="$sn"/>
          <xsl:text>
</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <!-- @d: one path command per line (newline after each command) -->
  <xsl:template match="@d">
    <xsl:param name="pad" select="0"/>
    <xsl:variable name="s" select="normalize-space(.)"/>

    <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
    <xsl:text>@d:</xsl:text>
    <xsl:text>
</xsl:text>

    <xsl:call-template name="emit-d-lines">
      <xsl:with-param name="s" select="$s"/>
      <xsl:with-param name="pad" select="$pad + $indent"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="emit-d-lines">
    <xsl:param name="s"/>
    <xsl:param name="pad" select="0"/>

    <xsl:if test="string-length($s) &gt; 0">
      <xsl:variable name="c" select="substring($s,1,1)"/>
      <xsl:variable name="rest" select="substring($s,2)"/>

      <xsl:choose>
        <xsl:when test="contains('MmLlHhVvCcSsQqTtAaZz',$c)">
          <xsl:call-template name="pad"><xsl:with-param name="depth" select="$pad"/></xsl:call-template>
          <xsl:value-of select="$c"/>
          <xsl:call-template name="emit-d-tail">
            <xsl:with-param name="s" select="$rest"/>
          </xsl:call-template>
          <xsl:text>
</xsl:text>

          <xsl:call-template name="emit-d-lines">
            <xsl:with-param name="s" select="$rest"/>
            <xsl:with-param name="pad" select="$pad"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="emit-d-lines">
            <xsl:with-param name="s" select="substring($s,2)"/>
            <xsl:with-param name="pad" select="$pad"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template name="emit-d-tail">
    <xsl:param name="s"/>
    <xsl:if test="string-length($s) &gt; 0">
      <xsl:variable name="c" select="substring($s,1,1)"/>
      <xsl:choose>
        <xsl:when test="contains('MmLlHhVvCcSsQqTtAaZz',$c)"/>
        <xsl:otherwise>
          <xsl:value-of select="$c"/>
          <xsl:call-template name="emit-d-tail">
            <xsl:with-param name="s" select="substring($s,2)"/>
          </xsl:call-template>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
