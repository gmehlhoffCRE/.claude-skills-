"""Tiny layout model that emits both an InDesign IDML package and an HTML proof.

Coordinates are page-relative points (origin top-left of trim). Items may extend
past the trim into the bleed.
"""
import html
import math
import os
import re
import shutil
import struct
import zipfile
from xml.sax.saxutils import escape, quoteattr

FONT_FAMILY = "Helvetica Neue LT Pro"
WEIGHTS = {"Thin": ("35 Thin", 200), "Light": ("45 Light", 300), "Roman": ("55 Roman", 400),
           "Medium": ("65 Medium", 500), "Bold": ("75 Bold", 700)}

# name: (cmyk, rgb hex)
SWATCHES = {
    "Midnight": ((100, 93, 32, 33), "#001E5A"),
    "Goldenrod": ((0, 32, 100, 0), "#FFB600"),
    "Dark Gray": ((63, 55, 54, 28), "#595959"),
    "Light Gray": ((8, 6, 7, 0), "#E6E6E6"),
    "Stadium Blue": ((100, 90, 11, 1), "#243E8C"),
    "Bright Blue": ((86, 69, 0, 0), "#0056DA"),
    "Warm Orange": ((0, 60, 100, 0), "#FF8200"),
    "Paper": ((0, 0, 0, 0), "#FFFFFF"),
    "Black": ((0, 0, 0, 100), "#1A1A1A"),
}


def color_ref(name):
    if name is None:
        return "Swatch/None"
    return f"Color/{name}"


def tint_rgb(hexc, tint):
    if tint is None or tint >= 100:
        return hexc
    r, g, b = int(hexc[1:3], 16), int(hexc[3:5], 16), int(hexc[5:7], 16)
    t = tint / 100.0
    r, g, b = [round(255 - (255 - c) * t) for c in (r, g, b)]
    return f"#{r:02X}{g:02X}{b:02X}"


def css_color(name, tint=None):
    if name is None:
        return "transparent"
    return tint_rgb(SWATCHES[name][1], tint)


# ---------------------------------------------------------------- styles
class PStyle:
    def __init__(self, name, weight="Roman", size=10, leading=None, color="Black", tracking=0,
                 before=0, after=0, caps=False, align="left", bullet=None, bullet_color=None,
                 left_indent=0, first_indent=0, italic=False, keep_with_next=False):
        self.name, self.weight, self.size = name, weight, size
        self.leading = leading or round(size * 1.2, 2)
        self.color, self.tracking, self.before, self.after = color, tracking, before, after
        self.caps, self.align, self.bullet, self.bullet_color = caps, align, bullet, bullet_color
        self.left_indent, self.first_indent = left_indent, first_indent
        self.italic, self.keep_with_next = italic, keep_with_next


class CStyle:
    def __init__(self, name, weight=None, color=None, size=None, tracking=None, caps=None):
        self.name, self.weight, self.color, self.size = name, weight, color, size
        self.tracking, self.caps = tracking, caps


# ---------------------------------------------------------------- items
class Item:
    layer = "Art"


class Rect(Item):
    def __init__(self, x, y, w, h, fill=None, stroke=None, sw=0, tint=None, name=None):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.fill, self.stroke, self.sw, self.tint, self.name = fill, stroke, sw, tint, name


class Oval(Rect):
    pass


class Path(Item):
    """Polyline/polygon. points: [(x,y), ...]"""
    def __init__(self, points, closed=False, fill=None, stroke=None, sw=1, name=None):
        self.points, self.closed, self.fill, self.stroke, self.sw, self.name = points, closed, fill, stroke, sw, name


class Line(Path):
    def __init__(self, x1, y1, x2, y2, stroke="Goldenrod", sw=1, name=None):
        super().__init__([(x1, y1), (x2, y2)], False, None, stroke, sw, name)


class Image(Item):
    """Linked image fitted proportionally inside the frame. align: l/c/r, v: t/c/b"""
    def __init__(self, x, y, w, h, src, align="c", valign="c", name=None):
        self.x, self.y, self.w, self.h, self.src = x, y, w, h, src
        self.align, self.valign, self.name = align, valign, name


class Placeholder(Item):
    """Empty graphics frame for art the client will supply, with a non-printing label."""
    def __init__(self, x, y, w, h, label, fill="Light Gray", tint=None, dark=False, name=None, lpad=8):
        self.x, self.y, self.w, self.h, self.label, self.lpad = x, y, w, h, label, lpad
        self.fill, self.tint, self.dark, self.name = fill, tint, dark, name


class Text(Item):
    """paras: list of (pstyle_name, runs); runs: str or list of (cstyle_name|None, str)."""
    def __init__(self, x, y, w, h, paras, inset=(0, 0, 0, 0), valign="top", name=None, layer="Art"):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.paras = [(p, [(None, r)] if isinstance(r, str) else r) for p, r in paras]
        self.inset, self.valign, self.name, self.layer = inset, valign, name, layer


# ---------------------------------------------------------------- document
class Doc:
    def __init__(self, name, w, h, npages, bleed=9, margin=36):
        self.name, self.w, self.h, self.bleed, self.margin = name, w, h, bleed, margin
        self.pages = [[] for _ in range(npages)]
        self.pstyles, self.cstyles = {}, {}
        # facing pages: page 0 alone (right), then pairs, last may be alone (left)
        self.spreads = [[0]]
        i = 1
        while i < npages:
            self.spreads.append(list(range(i, min(i + 2, npages))))
            i += 2

    def add_pstyle(self, s):
        self.pstyles[s.name] = s

    def add_cstyle(self, s):
        self.cstyles[s.name] = s

    def add(self, page, *items):
        self.pages[page].extend(items)

    def page_offset(self, pi):
        for sp in self.spreads:
            if pi in sp:
                if len(sp) == 1:
                    return 0 if pi == 0 else -self.w
                return -self.w if sp.index(pi) == 0 else 0
        raise ValueError(pi)


# ================================================================ IDML writer
class IdmlWriter:
    def __init__(self, doc, template_dir, links_dir):
        self.d, self.tpl, self.links_dir = doc, template_dir, links_dir
        self.n = 0x2000
        self.stories = []  # (id, xml)
        self.used_links = set()

    def uid(self):
        self.n += 1
        return f"u{self.n:x}"

    # -- geometry helpers
    def sx(self, pi, x):
        return x + self.d.page_offset(pi)

    def sy(self, y):
        return y - self.d.h / 2

    @staticmethod
    def _pts(points):
        out = []
        for p in points:
            if len(p) == 2:
                a = l = r = p
            else:
                a, l, r = p
            out.append(f'<PathPointType Anchor="{a[0]:.3f} {a[1]:.3f}" LeftDirection="{l[0]:.3f} {l[1]:.3f}" '
                       f'RightDirection="{r[0]:.3f} {r[1]:.3f}" />')
        return "".join(out)

    def _geom(self, points, closed=True):
        return (f'<Properties><PathGeometry><GeometryPathType PathOpen="{"false" if closed else "true"}">'
                f'<PathPointArray>{self._pts(points)}</PathPointArray></GeometryPathType></PathGeometry></Properties>')

    def _rect_pts(self, pi, x, y, w, h):
        X, Y = self.sx(pi, x), self.sy(y)
        return [(X, Y), (X, Y + h), (X + w, Y + h), (X + w, Y)]

    def _oval_pts(self, pi, x, y, w, h):
        X, Y = self.sx(pi, x), self.sy(y)
        k = 0.5522847498
        rx, ry, cx, cy = w / 2, h / 2, X + w / 2, Y + h / 2
        return [((cx - rx, cy), (cx - rx, cy + k * ry), (cx - rx, cy - k * ry)),
                ((cx, cy + ry), (cx + k * rx, cy + ry), (cx - k * rx, cy + ry)),
                ((cx + rx, cy), (cx + rx, cy - k * ry), (cx + rx, cy + k * ry)),
                ((cx, cy - ry), (cx - k * rx, cy - ry), (cx + k * rx, cy - ry))]

    def _common(self, layer, name):
        nm = quoteattr(name) if name else '"$ID/"'
        return (f'ItemLayer="{self.layer_ids[layer]}" Locked="false" Visible="true" Name={nm} '
                f'ItemTransform="1 0 0 1 0 0"')

    def _paint(self, fill, stroke, sw, tint=None):
        s = f'FillColor="{color_ref(fill)}" StrokeColor="{color_ref(stroke)}" StrokeWeight="{sw if stroke else 0}"'
        if tint is not None and fill:
            s += f' FillTint="{tint}"'
        return s

    def item_xml(self, pi, it):
        u = self.uid()
        if isinstance(it, Oval):
            return (f'<Oval Self="{u}" ContentType="Unassigned" {self._common(it.layer, it.name)} '
                    f'AppliedObjectStyle="ObjectStyle/$ID/[None]" {self._paint(it.fill, it.stroke, it.sw, it.tint)}>'
                    f'{self._geom(self._oval_pts(pi, it.x, it.y, it.w, it.h))}</Oval>')
        if isinstance(it, Rect):
            return (f'<Rectangle Self="{u}" ContentType="Unassigned" {self._common(it.layer, it.name)} '
                    f'AppliedObjectStyle="ObjectStyle/$ID/[None]" {self._paint(it.fill, it.stroke, it.sw, it.tint)}>'
                    f'{self._geom(self._rect_pts(pi, it.x, it.y, it.w, it.h))}</Rectangle>')
        if isinstance(it, Path):
            pts = [(self.sx(pi, x), self.sy(y)) for x, y in it.points]
            tag = "GraphicLine" if (len(pts) == 2 and not it.closed) else "Polygon"
            return (f'<{tag} Self="{u}" ContentType="Unassigned" {self._common(it.layer, it.name)} '
                    f'AppliedObjectStyle="ObjectStyle/$ID/[None]" {self._paint(it.fill, it.stroke, it.sw)} '
                    f'EndCap="RoundEndCap" EndJoin="RoundEndJoin">'
                    f'{self._geom(pts, it.closed)}</{tag}>')
        if isinstance(it, Placeholder):
            frame = (f'<Rectangle Self="{u}" ContentType="GraphicType" {self._common("Art", it.name or it.label[:60])} '
                     f'AppliedObjectStyle="ObjectStyle/$ID/[Normal Graphics Frame]" '
                     f'{self._paint(it.fill, None, 0, it.tint)}>'
                     f'{self._geom(self._rect_pts(pi, it.x, it.y, it.w, it.h))}'
                     f'<FrameFittingOption AutoFit="false" FittingOnEmptyFrame="FillProportionally" '
                     f'FittingAlignment="CenterAnchor" /></Rectangle>')
            lbl_style = "zz Placeholder Label Light" if it.dark else "zz Placeholder Label"
            t = Text(it.x + it.lpad, it.y + 8, it.w - it.lpad - 8, it.h - 16, [(lbl_style, it.label)], valign="center",
                     name="Label: " + it.label[:40], layer="Placeholder Labels")
            return frame + self.item_xml(pi, t)
        if isinstance(it, Image):
            return self.image_xml(pi, it, u)
        if isinstance(it, Text):
            sid = self.uid()
            self.stories.append((sid, self.story_xml(sid, it)))
            vj = {"top": "TopAlign", "center": "CenterAlign", "bottom": "BottomAlign"}[it.valign]
            t, l, b, r = it.inset
            return (f'<TextFrame Self="{u}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" '
                    f'ContentType="TextType" {self._common(it.layer, it.name)} '
                    f'AppliedObjectStyle="ObjectStyle/$ID/[Normal Text Frame]" FillColor="Swatch/None" '
                    f'StrokeColor="Swatch/None" StrokeWeight="0">'
                    f'{self._geom(self._rect_pts(pi, it.x, it.y, it.w, it.h))}'
                    f'<TextFramePreference TextColumnCount="1" FirstBaselineOffset="AscentOffset" '
                    f'VerticalJustification="{vj}" AutoSizingType="Off"><Properties><InsetSpacing type="list">'
                    f'<ListItem type="unit">{t}</ListItem><ListItem type="unit">{l}</ListItem>'
                    f'<ListItem type="unit">{b}</ListItem><ListItem type="unit">{r}</ListItem>'
                    f'</InsetSpacing></Properties></TextFramePreference></TextFrame>')
        raise TypeError(it)

    def image_xml(self, pi, it, u):
        from PIL import Image as PILImage
        im = PILImage.open(it.src)
        pw, ph = im.size
        dpi = im.info.get("dpi", (72, 72))[0] or 72
        nw, nh = pw * 72 / dpi, ph * 72 / dpi  # native size in pt
        s = min(it.w / nw, it.h / nh)
        dw, dh = nw * s, nh * s
        ox = {"l": 0, "c": (it.w - dw) / 2, "r": it.w - dw}[it.align]
        oy = {"t": 0, "c": (it.h - dh) / 2, "b": it.h - dh}[it.valign]
        X, Y = self.sx(pi, it.x + ox), self.sy(it.y + oy)
        fname = os.path.basename(it.src)
        self.used_links.add(it.src)
        eff = round(dpi / s)
        fmt = "$ID/Portable Network Graphics (PNG)" if fname.lower().endswith(".png") else "$ID/JPEG"
        return (f'<Rectangle Self="{u}" ContentType="GraphicType" {self._common(it.layer, it.name or fname)} '
                f'AppliedObjectStyle="ObjectStyle/$ID/[Normal Graphics Frame]" FillColor="Swatch/None" '
                f'StrokeColor="Swatch/None" StrokeWeight="0">'
                f'{self._geom(self._rect_pts(pi, it.x, it.y, it.w, it.h))}'
                f'<Image Self="{self.uid()}" Space="$ID/#Links_RGB" ActualPpi="{dpi} {dpi}" EffectivePpi="{eff} {eff}" '
                f'ImageRenderingIntent="UseColorSettings" ImageTypeName="{fmt}" AppliedObjectStyle="ObjectStyle/$ID/[None]" '
                f'ItemTransform="{s:.6f} 0 0 {s:.6f} {X:.3f} {Y:.3f}" Visible="true" Name="$ID/">'
                f'<Properties><Profile type="string">$ID/None</Profile>'
                f'<GraphicBounds Left="0" Top="0" Right="{nw:.4f}" Bottom="{nh:.4f}" /></Properties>'
                f'<Link Self="{self.uid()}" AssetURL="$ID/" AssetID="$ID/" LinkResourceURI="file:Links/{fname}" '
                f'LinkResourceFormat="{fmt}" StoredState="Normal" LinkClassID="35906" LinkClientID="257" '
                f'LinkResourceModified="false" LinkObjectModified="false" ShowInUI="true" CanEmbed="true" '
                f'CanUnembed="true" CanPackage="true" ImportPolicy="NoAutoImport" ExportPolicy="NoAutoExport" />'
                f'<ImageIOPreference ApplyPhotoshopClippingPath="true" AllowAutoEmbedding="true" AlphaChannelName="$ID/" />'
                f'</Image></Rectangle>')

    def story_xml(self, sid, t):
        body = []
        for i, (ps, runs) in enumerate(t.paras):
            last = i == len(t.paras) - 1
            rs = []
            for j, (cs, txt) in enumerate(runs):
                cref = f"CharacterStyle/{cs}" if cs else "CharacterStyle/$ID/[No character style]"
                parts = txt.split("\n")
                inner = "".join(
                    (f"<Content>{escape(p)}</Content>" if p else "") + ("" if k == len(parts) - 1 else "<Content> </Content>")
                    for k, p in enumerate(parts))
                if j == len(runs) - 1 and not last:
                    inner += "<Br />"
                rs.append(f'<CharacterStyleRange AppliedCharacterStyle="{cref}">{inner}</CharacterStyleRange>')
            body.append(f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{escape(ps)}">{"".join(rs)}</ParagraphStyleRange>')
        return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<idPkg:Story xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="10.0">'
                f'<Story Self="{sid}" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">'
                '<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" '
                'StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection" />'
                f'{"".join(body)}</Story></idPkg:Story>')

    # -- resources
    def pstyle_xml(self, s):
        fs = WEIGHTS[s.weight][0] + (" Italic" if s.italic else "")
        just = {"left": "LeftAlign", "center": "CenterAlign", "right": "RightAlign"}[s.align]
        attrs = (f'Self="ParagraphStyle/{escape(s.name)}" Name={quoteattr(s.name)} Imported="false" '
                 f'NextStyle="ParagraphStyle/{escape(s.name)}" KeyboardShortcut="0 0" FontStyle="{fs}" '
                 f'PointSize="{s.size}" FillColor="{color_ref(s.color)}" Tracking="{s.tracking}" '
                 f'SpaceBefore="{s.before}" SpaceAfter="{s.after}" Justification="{just}" '
                 f'Capitalization="{"AllCaps" if s.caps else "Normal"}" LeftIndent="{s.left_indent}" '
                 f'FirstLineIndent="{s.first_indent}" Hyphenation="false" KeepWithNext="{1 if s.keep_with_next else 0}"')
        props = (f'<BasedOn type="string">$ID/[No paragraph style]</BasedOn>'
                 f'<PreviewColor type="enumeration">Nothing</PreviewColor>'
                 f'<AppliedFont type="string">{FONT_FAMILY}</AppliedFont>'
                 f'<Leading type="unit">{s.leading}</Leading>')
        if s.bullet:
            attrs += ' BulletsAndNumberingListType="BulletList" BulletsTextAfter="^t"'
            props += (f'<BulletChar BulletCharacterType="UnicodeOnly" BulletCharacterValue="{ord(s.bullet)}" />'
                      f'<BulletsCharacterStyle type="object">CharacterStyle/{escape(self.bullet_cstyle(s))}</BulletsCharacterStyle>'
                      f'<TabList type="list"><ListItem type="record"><Alignment type="enumeration">LeftAlign</Alignment>'
                      f'<AlignmentCharacter type="string">.</AlignmentCharacter><Leader type="string"></Leader>'
                      f'<Position type="unit">{s.left_indent}</Position></ListItem></TabList>')
        return f'<ParagraphStyle {attrs}><Properties>{props}</Properties></ParagraphStyle>'

    def bullet_cstyle(self, s):
        return f"Bullet {s.bullet_color or s.color}"

    def cstyle_xml(self, c):
        a = f'Self="CharacterStyle/{escape(c.name)}" Imported="false" KeyboardShortcut="0 0" Name={quoteattr(c.name)}'
        if c.weight:
            a += f' FontStyle="{WEIGHTS[c.weight][0]}"'
        if c.color:
            a += f' FillColor="{color_ref(c.color)}"'
        if c.size:
            a += f' PointSize="{c.size}"'
        if c.tracking is not None:
            a += f' Tracking="{c.tracking}"'
        if c.caps is not None:
            a += f' Capitalization="{"AllCaps" if c.caps else "Normal"}"'
        props = '<Properties><BasedOn type="string">$ID/[No character style]</BasedOn>'
        props += '<PreviewColor type="enumeration">Nothing</PreviewColor>'
        if c.weight:
            props += f'<AppliedFont type="string">{FONT_FAMILY}</AppliedFont>'
        return f'<CharacterStyle {a}>{props}</Properties></CharacterStyle>'

    def write(self, out_path):
        d = self.d
        tmp = out_path + ".d"
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.copytree(self.tpl, tmp)
        for sub in ("Spreads", "Stories", "MasterSpreads"):
            shutil.rmtree(os.path.join(tmp, sub), ignore_errors=True)
            os.makedirs(os.path.join(tmp, sub))

        self.layer_ids = {"Art": self.uid(), "Placeholder Labels": self.uid()}
        master_id = self.uid()

        # bullet character styles
        for s in d.pstyles.values():
            if s.bullet:
                nm = self.bullet_cstyle(s)
                if nm not in d.cstyles:
                    d.add_cstyle(CStyle(nm, color=s.bullet_color or s.color))
        # label styles for placeholders
        d.add_pstyle(PStyle("zz Placeholder Label", "Medium", 8, 10, "Dark Gray", 40, caps=True, align="center"))
        d.add_pstyle(PStyle("zz Placeholder Label Light", "Medium", 8, 10, "Paper", 40, caps=True, align="center"))

        # spreads
        spread_ids = []
        page_ids = []
        for si, sp in enumerate(d.spreads):
            sid = self.uid()
            spread_ids.append(sid)
            pages_xml, items_xml = [], []
            for pi in sp:
                pid = self.uid()
                page_ids.append(pid)
                off = d.page_offset(pi)
                m = d.margin
                pages_xml.append(
                    f'<Page Self="{pid}" GeometricBounds="0 0 {d.h} {d.w}" ItemTransform="1 0 0 1 {off} {-d.h / 2}" '
                    f'Name="{pi + 1}" AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" OverrideList="" '
                    f'AppliedMaster="{master_id}" MasterPageTransform="1 0 0 1 0 0" TabOrder="" '
                    f'GridStartingPoint="TopOutside" UseMasterGrid="true">'
                    f'<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
                    f'<MarginPreference ColumnCount="1" ColumnGutter="12" Top="{m}" Bottom="{m}" Left="{m}" Right="{m}" '
                    f'ColumnDirection="Horizontal" ColumnsPositions="0 {d.w - 2 * m}" /></Page>')
                for it in d.pages[pi]:
                    items_xml.append(self.item_xml(pi, it))
            binding = 0 if (len(sp) == 1 and sp[0] == 0) else 1
            xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                   '<idPkg:Spread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="10.0">'
                   f'<Spread Self="{sid}" FlattenerOverride="Default" AllowPageShuffle="true" ItemTransform="1 0 0 1 0 0" '
                   f'ShowMasterItems="true" PageCount="{len(sp)}" BindingLocation="{binding}" PageTransitionType="None" '
                   f'PageTransitionDirection="NotApplicable" PageTransitionDuration="Medium">'
                   + "".join(pages_xml) + "".join(items_xml) + '</Spread></idPkg:Spread>')
            with open(os.path.join(tmp, "Spreads", f"Spread_{sid}.xml"), "w", encoding="utf-8") as f:
                f.write(xml)

        # master
        mp = []
        for k, off in enumerate((-d.w, 0)):
            m = d.margin
            mp.append(f'<Page Self="{self.uid()}" GeometricBounds="0 0 {d.h} {d.w}" ItemTransform="1 0 0 1 {off} {-d.h / 2}" '
                      f'Name="A" AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" OverrideList="" AppliedMaster="n" '
                      f'MasterPageTransform="1 0 0 1 0 0" TabOrder="" GridStartingPoint="TopOutside" UseMasterGrid="true">'
                      f'<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
                      f'<MarginPreference ColumnCount="1" ColumnGutter="12" Top="{m}" Bottom="{m}" Left="{m}" Right="{m}" '
                      f'ColumnDirection="Horizontal" ColumnsPositions="0 {d.w - 2 * m}" /></Page>')
        with open(os.path.join(tmp, "MasterSpreads", f"MasterSpread_{master_id}.xml"), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    '<idPkg:MasterSpread xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="10.0">'
                    f'<MasterSpread Self="{master_id}" ItemTransform="1 0 0 1 0 0" OverriddenPageItemProps="" Name="A-Master" '
                    f'NamePrefix="A" BaseName="Master" ShowMasterItems="true" PageCount="2" PrimaryTextFrame="n">'
                    f'<Properties><PageColor type="enumeration">UseMasterColor</PageColor></Properties>'
                    + "".join(mp) + '</MasterSpread></idPkg:MasterSpread>')

        # stories
        for sid, xml in self.stories:
            with open(os.path.join(tmp, "Stories", f"Story_{sid}.xml"), "w", encoding="utf-8") as f:
                f.write(xml)

        # backing story (no XML structure)
        with open(os.path.join(tmp, "XML", "BackingStory.xml"), "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    '<idPkg:BackingStory xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging" DOMVersion="10.0">'
                    '<XmlStory Self="ubacking" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">'
                    '<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle">'
                    '<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">'
                    '<XMLElement Self="di3" MarkupTag="XMLTag/Root" />'
                    '</CharacterStyleRange></ParagraphStyleRange></XmlStory></idPkg:BackingStory>')

        # swatches
        gp = os.path.join(tmp, "Resources", "Graphic.xml")
        g = open(gp, encoding="utf-8").read()
        cols = []
        for nm, (cmyk, _) in SWATCHES.items():
            if nm in ("Paper", "Black"):
                continue
            cols.append(f'<Color Self="Color/{nm}" Model="Process" Space="CMYK" ColorValue="{" ".join(map(str, cmyk))}" '
                        f'ColorOverride="Normal" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="{nm}" '
                        f'ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937" />')
        g = g.replace("<Ink ", "".join(cols) + "<Ink ", 1)
        open(gp, "w", encoding="utf-8").write(g)

        # styles
        sp_ = os.path.join(tmp, "Resources", "Styles.xml")
        st = open(sp_, encoding="utf-8").read()
        st = st.replace("</RootCharacterStyleGroup>",
                        "".join(self.cstyle_xml(c) for c in d.cstyles.values()) + "</RootCharacterStyleGroup>", 1)
        st = st.replace("</RootParagraphStyleGroup>",
                        "".join(self.pstyle_xml(s) for s in d.pstyles.values()) + "</RootParagraphStyleGroup>", 1)
        open(sp_, "w", encoding="utf-8").write(st)

        # preferences
        pp = os.path.join(tmp, "Resources", "Preferences.xml")
        pr = open(pp, encoding="utf-8").read()
        def setattr_(tag, k, v):
            nonlocal pr
            pr = re.sub(rf'(<{tag}\b[^>]*?\b{k}=")[^"]*(")', rf'\g<1>{v}\g<2>', pr, count=1)
        for k, v in (("PageHeight", d.h), ("PageWidth", d.w), ("PagesPerDocument", len(d.pages)),
                     ("FacingPages", "true"), ("DocumentBleedTopOffset", d.bleed),
                     ("DocumentBleedBottomOffset", d.bleed), ("DocumentBleedInsideOrLeftOffset", d.bleed),
                     ("DocumentBleedOutsideOrRightOffset", d.bleed), ("DocumentBleedUniformSize", "true")):
            setattr_("DocumentPreference", k, v)
        open(pp, "w", encoding="utf-8").write(pr)

        # designmap
        dm_path = os.path.join(tmp, "designmap.xml")
        dm = open(dm_path, encoding="utf-8").read()
        dm = re.sub(r'\s*<idPkg:(MasterSpread|Spread|Story) src="[^"]*" />', "", dm)
        dm = re.sub(r'\s*<Layer .*?</Layer>', "", dm, flags=re.S)
        dm = re.sub(r'\s*<Section .*?</Section>', "", dm, flags=re.S)
        story_ids = [s for s, _ in self.stories]
        dm = re.sub(r'StoryList="[^"]*"', f'StoryList="{" ".join(story_ids + ["ubacking"])}"', dm, count=1)
        dm = re.sub(r'ActiveLayer="[^"]*"', f'ActiveLayer="{self.layer_ids["Art"]}"', dm, count=1)
        layers = (f'<Layer Self="{self.layer_ids["Placeholder Labels"]}" Name="Placeholder Labels (non-printing)" Visible="true" '
                  f'Locked="false" IgnoreWrap="true" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" '
                  f'Printable="false"><Properties><LayerColor type="enumeration">Red</LayerColor></Properties></Layer>'
                  f'<Layer Self="{self.layer_ids["Art"]}" Name="Art" Visible="true" Locked="false" IgnoreWrap="false" '
                  f'ShowGuides="true" LockGuides="false" UI="true" Expendable="true" Printable="true">'
                  f'<Properties><LayerColor type="enumeration">LightBlue</LayerColor></Properties></Layer>')
        refs = f'<idPkg:MasterSpread src="MasterSpreads/MasterSpread_{master_id}.xml" />'
        refs += "".join(f'<idPkg:Spread src="Spreads/Spread_{s}.xml" />' for s in spread_ids)
        refs += (f'<Section Self="{self.uid()}" Length="{len(d.pages)}" Name="" ContinueNumbering="true" '
                 f'IncludeSectionPrefix="false" Marker="" PageStart="{page_ids[0]}" SectionPrefix="">'
                 f'<Properties><PageNumberStyle type="enumeration">Arabic</PageNumberStyle></Properties></Section>')
        dm = dm.replace("<idPkg:BackingStory", layers + refs + "<idPkg:BackingStory", 1)
        dm = dm.replace('<idPkg:BackingStory src="XML/BackingStory.xml" />',
                        '<idPkg:BackingStory src="XML/BackingStory.xml" />'
                        + "".join(f'<idPkg:Story src="Stories/Story_{s}.xml" />' for s in story_ids), 1)
        # swatches into root color group
        add = "".join(f'<ColorGroupSwatch Self="cgs{k}" SwatchItemRef="Color/{nm}" />'
                      for k, nm in enumerate(n for n in SWATCHES if n not in ("Paper", "Black")))
        dm = re.sub(r'(<ColorGroup [^>]*IsRootColorGroup="true">)', r'\1' + add, dm, count=1)
        open(dm_path, "w", encoding="utf-8").write(dm)

        # zip: mimetype first, stored
        if os.path.exists(out_path):
            os.remove(out_path)
        with zipfile.ZipFile(out_path, "w") as z:
            z.write(os.path.join(tmp, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
            for root, _, files in os.walk(tmp):
                for fn in sorted(files):
                    full = os.path.join(root, fn)
                    arc = os.path.relpath(full, tmp)
                    if arc == "mimetype":
                        continue
                    z.write(full, arc, compress_type=zipfile.ZIP_DEFLATED)
        shutil.rmtree(tmp)
        # links
        os.makedirs(self.links_dir, exist_ok=True)
        for src in self.used_links:
            shutil.copy(src, self.links_dir)


# ================================================================ HTML proof
PROOF_FONT = "'Helvetica Neue LT Pro','Helvetica Neue','Inter',Arial,sans-serif"


def _pstyle_css(s):
    return (f"font-weight:{WEIGHTS[s.weight][1]};font-size:{s.size}pt;line-height:{s.leading}pt;"
            f"color:{css_color(s.color)};letter-spacing:{s.tracking / 1000}em;margin:{s.before}pt 0 {s.after}pt 0;"
            f"text-align:{s.align};{'text-transform:uppercase;' if s.caps else ''}"
            f"{'font-style:italic;' if s.italic else ''}"
            f"padding-left:{s.left_indent}pt;text-indent:{s.first_indent}pt;")


def _cstyle_css(c):
    css = ""
    if c.weight:
        css += f"font-weight:{WEIGHTS[c.weight][1]};"
    if c.color:
        css += f"color:{css_color(c.color)};"
    if c.size:
        css += f"font-size:{c.size}pt;"
    if c.tracking is not None:
        css += f"letter-spacing:{c.tracking / 1000}em;"
    if c.caps is not None:
        css += "text-transform:uppercase;" if c.caps else "text-transform:none;"
    return css


def item_html(doc, it, ox, show_labels=True):
    def box(x, y, w, h):
        return f"left:{x + ox}pt;top:{y}pt;width:{w}pt;height:{h}pt;"
    if isinstance(it, Oval) or isinstance(it, Rect):
        rad = "border-radius:50%;" if isinstance(it, Oval) else ""
        bd = f"box-shadow:inset 0 0 0 {it.sw}pt {css_color(it.stroke)};" if it.stroke else ""
        return f'<div class="i" style="{box(it.x, it.y, it.w, it.h)}background:{css_color(it.fill, it.tint)};{bd}{rad}"></div>'
    if isinstance(it, Path):
        xs = [p[0] for p in it.points]
        ys = [p[1] for p in it.points]
        pad = it.sw + 2
        x0, y0 = min(xs) - pad, min(ys) - pad
        w, h = max(xs) - x0 + pad, max(ys) - y0 + pad
        pts = " ".join(f"{x - x0},{y - y0}" for x, y in it.points)
        tag = "polygon" if it.closed else "polyline"
        return (f'<svg class="i" style="{box(x0, y0, w, h)}overflow:visible" viewBox="0 0 {w} {h}">'
                f'<{tag} points="{pts}" fill="{css_color(it.fill)}" stroke="{css_color(it.stroke)}" '
                f'stroke-width="{it.sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    if isinstance(it, Placeholder):
        col = "#fff" if it.dark else "#595959"
        lab = (f'<div style="position:absolute;inset:8pt 8pt 8pt {it.lpad}pt;display:flex;align-items:center;justify-content:center;'
               f'text-align:center;font:500 7.5pt/10pt {PROOF_FONT};letter-spacing:.04em;text-transform:uppercase;color:{col};'
               f'opacity:.85">{html.escape(it.label)}</div>') if show_labels else ""
        return (f'<div class="i" style="{box(it.x, it.y, it.w, it.h)}background:{css_color(it.fill, it.tint)};'
                f'background-image:repeating-linear-gradient(135deg,rgba(0,0,0,.035) 0 6pt,transparent 6pt 12pt)">{lab}</div>')
    if isinstance(it, Image):
        a = {"l": "left", "c": "center", "r": "right"}[it.align]
        v = {"t": "top", "c": "center", "b": "bottom"}[it.valign]
        return (f'<img class="i" src="file://{os.path.abspath(it.src)}" style="{box(it.x, it.y, it.w, it.h)}'
                f'object-fit:contain;object-position:{a} {v}">')
    if isinstance(it, Text):
        if it.layer == "Placeholder Labels" and not show_labels:
            return ""
        t, l, b, r = it.inset
        jc = {"top": "flex-start", "center": "center", "bottom": "flex-end"}[it.valign]
        ps = []
        for pn, runs in it.paras:
            s = doc.pstyles[pn]
            inner = ""
            if s.bullet:
                inner += (f'<span style="display:inline-block;width:{s.left_indent}pt;text-indent:0;'
                          f'color:{css_color(s.bullet_color or s.color)}">{s.bullet}</span>')
            for cs, txt in runs:
                tx = html.escape(txt).replace("\n", "<br>")
                inner += f'<span style="{_cstyle_css(doc.cstyles[cs])}">{tx}</span>' if cs else tx
            fi = (-s.left_indent if s.bullet else s.first_indent)
            css = _pstyle_css(s).replace(f"text-indent:{s.first_indent}pt", f"text-indent:{fi}pt")
            ps.append(f'<p style="{css}">{inner or "&nbsp;"}</p>')
        return (f'<div class="i t" data-name="{html.escape(it.name or "")}" style="{box(it.x, it.y, it.w, it.h)}'
                f'padding:{t}pt {r}pt {b}pt {l}pt;display:flex;flex-direction:column;justify-content:{jc}">'
                f'<div class="flow">{"".join(ps)}</div></div>')
    raise TypeError(it)


def proof_html(doc, sheets, show_bleed=False, show_labels=True):
    """sheets: list of lists of page indices laid side by side (e.g. [[0],[1,2],[3]])."""
    b = doc.bleed if show_bleed else 0
    css = [f"@font-face{{}}",
           "*{box-sizing:border-box}html,body{margin:0;padding:0;background:#fff}",
           f"body{{font-family:{PROOF_FONT};-webkit-print-color-adjust:exact;print-color-adjust:exact}}",
           ".sheet{position:relative;overflow:hidden;break-after:page}.sheet:last-child{break-after:auto}",
           ".i{position:absolute;margin:0}.t p{margin:0}.flow{width:100%}.flow p:last-child{margin-bottom:0 !important}"]
    out = []
    for k, sh in enumerate(sheets):
        W = doc.w * len(sh) + 2 * b
        H = doc.h + 2 * b
        css.append(f"@page s{k}{{size:{W}pt {H}pt;margin:0}} .s{k}{{page:s{k};width:{W}pt;height:{H}pt}}")
        items = []
        for j, pi in enumerate(sh):
            ox = b + j * doc.w
            # wrap page in clip box so bleed only shows on outer edges
            items.append(f'<div style="position:absolute;left:0;top:{b}pt;width:{W}pt;height:{doc.h}pt;overflow:visible">')
            items.extend(item_html(doc, it, ox, show_labels) for it in doc.pages[pi])
            items.append("</div>")
        out.append(f'<section class="sheet s{k}">{"".join(items)}</section>')
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{"".join(css)}</style></head><body>{"".join(out)}</body></html>'
