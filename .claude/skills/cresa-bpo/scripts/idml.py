import os, zipfile, itertools, importlib
from xml.sax.saxutils import escape, quoteattr
from PIL import Image
spec = importlib.import_module(os.environ.get("SPEC", "bpo_spec"))
LINKS = os.environ["LINKS"]

DOM = "18.0"
NS = 'xmlns:idPkg="http://ns.adobe.com/AdobeInDesign/idml/1.0/packaging"'
HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
FONT = "Helvetica Neue LT Pro"
_ids = itertools.count(0x200)
def uid(): return "u%x" % next(_ids)

LAYERS = [("ulayNotes", "Placeholder Notes", "Red", False), ("ulayContent", "Content", "LightBlue", True), ("ulayImages", "Images", "Green", True)]
LAYER_ID = {"Notes": "ulayNotes", "Content": "ulayContent", "Images": "ulayImages"}
HALF = spec.H / 2
stories = {}


def cref(name):
    if name in (None, "None"): return "Swatch/None"
    if name == "Paper": return "Color/Paper"
    return "Color/" + name.replace(" ", "")


def f(v): return ("%.3f" % v).rstrip("0").rstrip(".")


def path_xml(pts, closed=True):
    a = "".join(f'<PathPointType Anchor="{f(x)} {f(y)}" LeftDirection="{f(x)} {f(y)}" RightDirection="{f(x)} {f(y)}"/>' for x, y in pts)
    return (f'<Properties><PathGeometry><GeometryPathType PathOpen="{"false" if closed else "true"}"><PathPointArray>'
            f'{a}</PathPointArray></GeometryPathType></PathGeometry></Properties>')


def box(x, y, w, h):
    y = y - HALF
    return [(x, y), (x, y + h), (x + w, y + h), (x + w, y)]


def transp(op):
    return "" if op >= 100 else f'<TransparencySetting><BlendingSetting BlendMode="Normal" Opacity="{f(op)}"/></TransparencySetting>'


def runs_xml(paras):
    out = []
    for i, (st, runs) in enumerate(paras):
        pattrs = ""
        for _, o in runs:
            if "Justification" in o: pattrs = f' Justification="{o["Justification"]}"'
        x = f'<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/{escape(st)}"{pattrs}>'
        for j, (t, o) in enumerate(runs):
            ca = "".join(f' {k}={quoteattr(v)}' for k, v in o.items() if k != "Justification")
            x += f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"{ca}>'
            if t: x += f"<Content>{escape(t)}</Content>"
            if j == len(runs) - 1 and i < len(paras) - 1: x += "<Br/>"
            x += "</CharacterStyleRange>"
        out.append(x + "</ParagraphStyleRange>")
    return "".join(out)


def story(sid, inner):
    stories[sid] = (HDR + f'<idPkg:Story {NS} DOMVersion="{DOM}"><Story Self="{sid}" UserText="true" IsEndnoteStory="false" '
                    'AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n">'
                    '<StoryPreference OpticalMarginAlignment="false" OpticalMarginSize="12" FrameType="TextFrameType" '
                    'StoryOrientation="Horizontal" StoryDirection="LeftToRightDirection"/>'
                    '<InCopyExportOption IncludeGraphicProxies="true" IncludeAllResources="false"/>'
                    f'{inner}</Story></idPkg:Story>')


def text_frame(x, y, w, h, inner, layer, valign="TopAlign", inset=(0, 0, 0, 0), cols=1, gutter=12, fill=None, name=None):
    sid, fid = uid(), uid()
    story(sid, inner)
    return (f'<TextFrame Self="{fid}" ParentStory="{sid}" PreviousTextFrame="n" NextTextFrame="n" ContentType="TextType" '
            f'ItemLayer="{LAYER_ID[layer]}" Name={quoteattr(name or "$ID/")} FillColor="{cref(fill)}" StrokeColor="Swatch/None" StrokeWeight="0" '
            f'ItemTransform="1 0 0 1 0 0" AppliedObjectStyle="ObjectStyle/$ID/[Normal Text Frame]">{path_xml(box(x, y, w, h))}'
            f'<TextFramePreference TextColumnCount="{cols}" TextColumnGutter="{f(gutter)}" VerticalJustification="{valign}" '
            f'InsetSpacing="{" ".join(f(v) for v in inset)}" AutoSizingType="Off" FirstBaselineOffset="AscentOffset" '
            f'IgnoreWrap="false" UseFixedColumnWidth="false"/></TextFrame>')


def table_xml(it):
    tid = uid(); colw, rows = it["colw"], it["rows"]
    x = (f'<Table Self="{tid}" HeaderRowCount="0" FooterRowCount="0" BodyRowCount="{len(rows)}" ColumnCount="{len(colw)}" '
         'AppliedTableStyle="TableStyle/$ID/[Basic Table]" TableDirection="LeftToRightDirection" '
         'TopBorderStrokeWeight="0" BottomBorderStrokeWeight="0" LeftBorderStrokeWeight="0" RightBorderStrokeWeight="0" SpaceBefore="0" SpaceAfter="0">')
    for r, row in enumerate(rows):
        x += f'<Row Self="{tid}Row{r}" Name="{r}" SingleRowHeight="{f(row["h"])}" MinimumHeight="{f(row["h"])}" AutoGrow="false"/>'
    for c, w in enumerate(colw):
        x += f'<Column Self="{tid}Column{c}" Name="{c}" SingleColumnWidth="{f(w)}"/>'
    for r, row in enumerate(rows):
        c = 0
        for cell in row["cells"]:
            span = cell.get("span", 1); t, l, b, rr = cell.get("inset", (2, 4, 2, 4)); bc, bw = cell.get("bottom", (None, 0))
            x += (f'<Cell Self="{tid}i{c}i{r}" Name="{c}:{r}" RowSpan="1" ColumnSpan="{span}" AppliedCellStyle="CellStyle/$ID/[None]" '
                  f'AppliedCellStylePriority="0" FillColor="{cref(cell.get("fill"))}" VerticalJustification="CenterAlign" '
                  f'TopInset="{f(t)}" LeftInset="{f(l)}" BottomInset="{f(b)}" RightInset="{f(rr)}" '
                  'TopEdgeStrokeWeight="0" LeftEdgeStrokeWeight="0" RightEdgeStrokeWeight="0" '
                  f'BottomEdgeStrokeWeight="{f(bw)}" BottomEdgeStrokeColor="{cref(bc)}" BottomEdgeStrokeType="StrokeStyle/$ID/Solid" '
                  f'ClipContentToCell="true">{runs_xml(cell["paras"])}</Cell>')
            c += span
    x += "</Table>"
    inner = ('<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle">'
             f'<CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">{x}</CharacterStyleRange></ParagraphStyleRange>')
    return text_frame(it["x"], it["y"], sum(colw) + 2, sum(r["h"] for r in rows) + 6, inner, it["layer"], name=it.get("name"))


def rect_xml(x, y, w, h, fill, layer, opacity=100, stroke=None, sw=0, content="Unassigned", name=None, inner=""):
    fit = ('<FrameFittingOption AutoFit="false" LeftCrop="0" TopCrop="0" RightCrop="0" BottomCrop="0" '
           'FittingOnEmptyFrame="FillProportionally" FittingAlignment="CenterAnchor"/>') if content == "GraphicType" else ""
    return (f'<Rectangle Self="{uid()}" ContentType="{content}" StoryTitle="$ID/" ItemLayer="{LAYER_ID[layer]}" Name={quoteattr(name or "$ID/")} '
            f'FillColor="{cref(fill)}" StrokeColor="{cref(stroke)}" StrokeWeight="{f(sw)}" ItemTransform="1 0 0 1 0 0" '
            f'AppliedObjectStyle="ObjectStyle/$ID/[None]">{path_xml(box(x, y, w, h))}{transp(opacity)}{fit}{inner}</Rectangle>')


def image_xml(it):
    fn = it["file"]; im = Image.open(LINKS + fn); pw, ph = im.size
    dpi = im.info.get("dpi", (300, 300))[0] or 300
    gw, gh = pw * 72 / dpi, ph * 72 / dpi
    s = max(it["w"] / gw, it["h"] / gh)
    tx = it["x"] + (it["w"] - gw * s) / 2; ty = it["y"] - HALF + (it["h"] - gh * s) / 2
    img = (f'<Image Self="{uid()}" ItemTransform="{f(s)} 0 0 {f(s)} {f(tx)} {f(ty)}" Space="$ID/#Links_RGB" '
           f'ActualPpi="{f(dpi)} {f(dpi)}" EffectivePpi="{round(dpi / s)} {round(dpi / s)}" ImageRenderingIntent="UseColorSettings" '
           'LocalDisplaySetting="Default" ImageTypeName="$ID/Portable Network Graphics (PNG)" AppliedObjectStyle="ObjectStyle/$ID/[None]" Visible="true" Name="$ID/">'
           f'<Properties><Profile type="string">$ID/None</Profile><GraphicBounds Left="0" Top="0" Right="{f(gw)}" Bottom="{f(gh)}"/></Properties>'
           f'<Link Self="{uid()}" AssetURL="$ID/" AssetID="$ID/" LinkResourceURI="file:Links/{fn}" '
           'LinkResourceFormat="$ID/Portable Network Graphics (PNG)" StoredState="Normal" LinkClassID="35906" LinkClientID="257" '
           'LinkResourceModified="false" LinkObjectModified="false" ShowInUI="true" CanEmbed="true" CanUnembed="true" '
           'CanPackage="true" ImportPolicy="NoAutoImport" ExportPolicy="NoAutoExport" LinkImportStamp="file 0 0" '
           f'LinkImportModificationTime="2026-01-01T00:00:00" LinkImportTime="2026-01-01T00:00:00" LinkResourceSize="0~{os.path.getsize(LINKS + fn):x}"/>'
           '</Image>')
    return rect_xml(it["x"], it["y"], it["w"], it["h"], None, it["layer"], content="GraphicType", name=it.get("name") or fn, inner=img)


def item_xml(it):
    t = it["t"]
    if t == "rect":
        return rect_xml(it["x"], it["y"], it["w"], it["h"], it["fill"], it["layer"], it["opacity"], it["stroke"], it["sw"], name=it.get("name"))
    if t == "placeholder":
        return rect_xml(it["x"], it["y"], it["w"], it["h"], "Placeholder", it["layer"], it["opacity"], content="GraphicType", name=it["name"])
    if t == "poly":
        pts = [(x, y - HALF) for x, y in it["pts"]]
        return (f'<Polygon Self="{uid()}" ContentType="Unassigned" StoryTitle="$ID/" ItemLayer="{LAYER_ID[it["layer"]]}" '
                f'FillColor="{cref(it["fill"])}" StrokeColor="Swatch/None" StrokeWeight="0" ItemTransform="1 0 0 1 0 0" '
                f'AppliedObjectStyle="ObjectStyle/$ID/[None]">{path_xml(pts)}</Polygon>')
    if t == "line":
        x1, y1, x2, y2 = it["p"]
        return (f'<GraphicLine Self="{uid()}" ContentType="Unassigned" StoryTitle="$ID/" ItemLayer="{LAYER_ID[it["layer"]]}" '
                f'FillColor="Swatch/None" StrokeColor="{cref(it["color"])}" StrokeWeight="{f(it["sw"])}" ItemTransform="1 0 0 1 0 0" '
                f'AppliedObjectStyle="ObjectStyle/$ID/[None]">{path_xml([(x1, y1 - HALF), (x2, y2 - HALF)], closed=False)}</GraphicLine>')
    if t == "image": return image_xml(it)
    if t == "text":
        return text_frame(it["x"], it["y"], it["w"], it["h"], runs_xml(it["paras"]), it["layer"], it["valign"], it["inset"], it["cols"], it["gutter"], it.get("fill"), it.get("name"))
    if t == "table": return table_xml(it)
    raise ValueError(t)


def graphic_xml():
    cols = ['<Color Self="Color/Black" Model="Process" Space="CMYK" ColorValue="0 0 0 100" ColorOverride="Specialblack" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Black" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>',
            '<Color Self="Color/Paper" Model="Process" Space="CMYK" ColorValue="0 0 0 0" ColorOverride="Specialpaper" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Paper" ColorEditable="true" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>',
            '<Color Self="Color/Registration" Model="Registration" Space="CMYK" ColorValue="100 100 100 100" ColorOverride="Specialregistration" AlternateSpace="NoAlternateColor" AlternateColorValue="" Name="Registration" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>']
    for n, (r, g, b) in spec.COLORS.items():
        cols.append(f'<Color Self="{cref(n)}" Model="Process" Space="RGB" ColorValue="{r} {g} {b}" ColorOverride="Normal" AlternateSpace="NoAlternateColor" '
                    f'AlternateColorValue="" Name={quoteattr("Cresa " + n)} ColorEditable="true" ColorRemovable="true" Visible="true" SwatchCreatorID="7937"/>')
    inks = "".join(f'<Ink Self="Ink/$ID/Process {c}" Name="$ID/Process {c}" Angle="{a}" ConvertToProcess="false" Frequency="70" NeutralDensity="{d}" PrintInk="true" TrapOrder="{i+1}" InkType="Normal"/>'
                   for i, (c, a, d) in enumerate([("Cyan", 75, 0.61), ("Magenta", 15, 0.76), ("Yellow", 0, 0.16), ("Black", 45, 1.7)]))
    strokes = "".join(f'<StrokeStyle Self="StrokeStyle/$ID/{s}" Name="$ID/{s}"/>' for s in ["Solid", "Dashed", "Dotted", "Wavy", "ThickThin", "ThinThick", "ThickThick", "ThinThin", "Japanese Dots"])
    return (HDR + f'<idPkg:Graphic {NS} DOMVersion="{DOM}">' + "".join(cols) + inks +
            '<Swatch Self="Swatch/None" Name="None" ColorEditable="false" ColorRemovable="false" Visible="true" SwatchCreatorID="7937"/>' + strokes + '</idPkg:Graphic>')


STYLE_NAMES = {"45 Light": "HelveticaNeueLTPro-Lt", "55 Roman": "HelveticaNeueLTPro-Roman", "75 Bold": "HelveticaNeueLTPro-Bd"}


def fonts_xml():
    fonts = "".join(f'<Font Self="di1Font{i}" FontFamily="{FONT}" Name="{FONT} {s}" PostScriptName="{ps}" Status="Installed" FontStyleName="{s}" '
                    f'FontType="OpenTypeCFF" WritingScript="0" FullName="{FONT} {s}" FullNameNative="{FONT} {s}" FontStyleNameNative="{s}" PlatformName="$ID/" Version="" TypekitID="$ID/"/>'
                    for i, (s, ps) in enumerate(STYLE_NAMES.items()))
    return HDR + f'<idPkg:Fonts {NS} DOMVersion="{DOM}"><FontFamily Self="di1" Name="{FONT}">{fonts}</FontFamily></idPkg:Fonts>'


def styles_xml():
    ps = []
    for n, (fs, size, lead, c, j, ex) in spec.PSTYLES.items():
        extra = f' SpaceAfter="{f(ex["SpaceAfter"])}"' if "SpaceAfter" in ex else ""
        tabs = ""
        if "Tab" in ex:
            tabs = (f'<TabList type="list"><ListItem type="record"><Alignment type="enumeration">LeftAlign</Alignment><AlignmentCharacter type="string">.</AlignmentCharacter>'
                    f'<Leader type="string"></Leader><Position type="unit">{f(ex["Tab"])}</Position></ListItem></TabList>')
        ps.append(f'<ParagraphStyle Self="ParagraphStyle/{escape(n)}" Name={quoteattr(n)} Imported="false" NextStyle="ParagraphStyle/{escape(n)}" KeyboardShortcut="0 0" '
                  f'FontStyle="{fs}" PointSize="{f(size)}" FillColor="{cref(c)}" Justification="{j}" Hyphenation="false" SpaceBefore="0"{extra}>'
                  f'<Properties><BasedOn type="object">ParagraphStyle/$ID/NormalParagraphStyle</BasedOn><Leading type="unit">{f(lead)}</Leading>'
                  f'<AppliedFont type="string">{FONT}</AppliedFont>{tabs}</Properties></ParagraphStyle>')
    return (HDR + f'<idPkg:Styles {NS} DOMVersion="{DOM}">'
            '<RootCharacterStyleGroup Self="u79"><CharacterStyle Self="CharacterStyle/$ID/[No character style]" Imported="false" SplitDocument="false" EmitCss="true" '
            'StyleUniqueId="$ID/" IncludeClass="true" ExtendedKeyboardShortcut="0 0 0" Name="$ID/[No character style]"/></RootCharacterStyleGroup>'
            '<RootParagraphStyleGroup Self="u78"><ParagraphStyle Self="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[No paragraph style]" Imported="false" '
            'KeyboardShortcut="0 0" FontStyle="55 Roman" PointSize="12"><Properties><Leading type="enumeration">Auto</Leading>'
            f'<AppliedFont type="string">{FONT}</AppliedFont></Properties></ParagraphStyle>'
            '<ParagraphStyle Self="ParagraphStyle/$ID/NormalParagraphStyle" Name="$ID/NormalParagraphStyle" Imported="false" NextStyle="ParagraphStyle/$ID/NormalParagraphStyle" '
            'KeyboardShortcut="0 0" FontStyle="55 Roman" PointSize="10"><Properties><BasedOn type="string">$ID/[No paragraph style]</BasedOn>'
            f'<PreviewColor type="enumeration">Nothing</PreviewColor><AppliedFont type="string">{FONT}</AppliedFont></Properties></ParagraphStyle>'
            + "".join(ps) + '</RootParagraphStyleGroup>'
            '<RootCellStyleGroup Self="u8b"><CellStyle Self="CellStyle/$ID/[None]" AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]" Name="$ID/[None]"/></RootCellStyleGroup>'
            '<RootTableStyleGroup Self="u8d"><TableStyle Self="TableStyle/$ID/[No table style]" Name="$ID/[No table style]"/>'
            '<TableStyle Self="TableStyle/$ID/[Basic Table]" Name="$ID/[Basic Table]"><Properties><BasedOn type="string">$ID/[No table style]</BasedOn></Properties></TableStyle></RootTableStyleGroup>'
            '<RootObjectStyleGroup Self="u98">'
            '<ObjectStyle Self="ObjectStyle/$ID/[None]" Name="$ID/[None]" AppliedParagraphStyle="ParagraphStyle/$ID/[No paragraph style]" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0"/>'
            '<ObjectStyle Self="ObjectStyle/$ID/[Normal Graphics Frame]" Name="$ID/[Normal Graphics Frame]" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0"><Properties><BasedOn type="string">ObjectStyle/$ID/[None]</BasedOn></Properties></ObjectStyle>'
            '<ObjectStyle Self="ObjectStyle/$ID/[Normal Text Frame]" Name="$ID/[Normal Text Frame]" FillColor="Swatch/None" StrokeColor="Swatch/None" StrokeWeight="0"><Properties><BasedOn type="string">ObjectStyle/$ID/[None]</BasedOn></Properties></ObjectStyle>'
            '<ObjectStyle Self="ObjectStyle/$ID/[Normal Grid]" Name="$ID/[Normal Grid]"><Properties><BasedOn type="string">ObjectStyle/$ID/[None]</BasedOn></Properties></ObjectStyle>'
            '</RootObjectStyleGroup></idPkg:Styles>')


MARGIN = '<MarginPreference ColumnCount="1" ColumnGutter="12" Top="36" Bottom="36" Left="36" Right="36" ColumnDirection="Horizontal" ColumnsPositions="0 720"/>'


def page_xml(pid, name, master):
    return (f'<Page Self="{pid}" TabOrder="" AppliedMaster="{master}" OverrideList="" MasterPageTransform="1 0 0 1 0 0" Name="{name}" '
            f'AppliedTrapPreset="TrapPreset/$ID/kDefaultTrapStyleName" GeometricBounds="0 0 {spec.H} {spec.W}" ItemTransform="1 0 0 1 0 {-HALF}" '
            f'GridStartingPoint="TopOutside" UseMasterGrid="true">{MARGIN}</Page>')


def build(out):
    spreads = []
    for i, items in enumerate(spec.PAGES):
        sid = f"us{i+1}"
        body = "".join(item_xml(it) for it in items)
        spreads.append((sid, HDR + f'<idPkg:Spread {NS} DOMVersion="{DOM}"><Spread Self="{sid}" PageTransitionType="None" PageTransitionDirection="NotApplicable" '
                        'PageTransitionDuration="Medium" ShowMasterItems="true" PageCount="1" BindingLocation="0" SpreadHidden="false" AllowPageShuffle="true" '
                        f'ItemTransform="1 0 0 1 0 0" FlattenerOverride="Default">{page_xml(f"up{i+1}", i + 1, "umA")}{body}</Spread></idPkg:Spread>'))
    layers = "".join(f'<Layer Self="{lid}" Name="{n}" Visible="true" Locked="false" IgnoreWrap="false" ShowGuides="true" LockGuides="false" UI="true" Expendable="true" '
                     f'Printable="{"true" if pr else "false"}"><Properties><LayerColor type="enumeration">{c}</LayerColor></Properties></Layer>' for lid, n, c, pr in LAYERS)
    design = (HDR + '<?aid style="50" type="document" readerVersion="6.0" featureSet="257" product="18.0(85)" ?>\n'
              f'<Document {NS} DOMVersion="{DOM}" Self="d" StoryList="{" ".join(stories)}" ZeroPoint="0 0" ActiveLayer="ulayContent" '
              'CMYKProfile="U.S. Web Coated (SWOP) v2" RGBProfile="sRGB IEC61966-2.1" SolidColorIntent="UseColorSettings" AfterBlendingIntent="UseColorSettings" '
              'DefaultImageIntent="UseColorSettings" RGBPolicy="PreserveEmbeddedProfiles" CMYKPolicy="CombinationOfPreserveAndSafeCmyk" AccurateLABSpots="false">'
              '<idPkg:Graphic src="Resources/Graphic.xml"/><idPkg:Fonts src="Resources/Fonts.xml"/><idPkg:Styles src="Resources/Styles.xml"/>'
              '<idPkg:Preferences src="Resources/Preferences.xml"/><idPkg:Tags src="XML/Tags.xml"/>'
              f'{layers}<idPkg:MasterSpread src="MasterSpreads/MasterSpread_umA.xml"/>'
              + "".join(f'<idPkg:Spread src="Spreads/Spread_{sid}.xml"/>' for sid, _ in spreads) +
              f'<Section Self="usec" Length="{len(spreads)}" Name="" ContinueNumbering="true" IncludeSectionPrefix="false" PageNumberStyle="Arabic" PageStart="up1" SectionPrefix="" Marker=""/>'
              '<idPkg:BackingStory src="XML/BackingStory.xml"/>' + "".join(f'<idPkg:Story src="Stories/Story_{s}.xml"/>' for s in stories) + '</Document>')
    master = (HDR + f'<idPkg:MasterSpread {NS} DOMVersion="{DOM}"><MasterSpread Self="umA" ItemTransform="1 0 0 1 0 0" OverriddenPageItemProps="" PrimaryTextFrame="n" '
              f'NamePrefix="A" BaseName="Master" ShowMasterItems="true" PageCount="1" PageColor="UseMasterColor">{page_xml("umAp", "A", "n")}</MasterSpread></idPkg:MasterSpread>')
    prefs = (HDR + f'<idPkg:Preferences {NS} DOMVersion="{DOM}"><DocumentPreference PageHeight="{spec.H}" PageWidth="{spec.W}" PagesPerDocument="{len(spec.PAGES)}" '
             'FacingPages="false" DocumentBleedTopOffset="9" DocumentBleedBottomOffset="9" DocumentBleedInsideOrLeftOffset="9" DocumentBleedOutsideOrRightOffset="9" '
             'DocumentBleedUniformSize="true" AllowPageShuffle="true" OverprintBlack="true" PageBinding="LeftToRight" ColumnDirection="Horizontal" Intent="PrintIntent"/>'
             f'{MARGIN}</idPkg:Preferences>')
    files = {"designmap.xml": design,
             "META-INF/container.xml": HDR + '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0"><rootfiles><rootfile full-path="designmap.xml" media-type="text/xml"/></rootfiles></container>',
             "Resources/Graphic.xml": graphic_xml(), "Resources/Fonts.xml": fonts_xml(), "Resources/Styles.xml": styles_xml(), "Resources/Preferences.xml": prefs,
             "MasterSpreads/MasterSpread_umA.xml": master,
             "XML/Tags.xml": HDR + f'<idPkg:Tags {NS} DOMVersion="{DOM}"><XMLTag Self="XMLTag/Root" Name="Root"><Properties><TagColor type="enumeration">LightBlue</TagColor></Properties></XMLTag></idPkg:Tags>',
             "XML/BackingStory.xml": HDR + f'<idPkg:BackingStory {NS} DOMVersion="{DOM}"><XmlStory Self="ubs" UserText="true" IsEndnoteStory="false" AppliedTOCStyle="n" TrackChanges="false" StoryTitle="$ID/" AppliedNamedGrid="n"><ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/$ID/NormalParagraphStyle"><CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]"/></ParagraphStyleRange></XmlStory></idPkg:BackingStory>'}
    for sid, x in spreads: files[f"Spreads/Spread_{sid}.xml"] = x
    for s, x in stories.items(): files[f"Stories/Story_{s}.xml"] = x
    with zipfile.ZipFile(out, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.adobe.indesign-idml-package", compress_type=zipfile.ZIP_STORED)
        for n, x in files.items(): z.writestr(n, x.encode("utf-8"), compress_type=zipfile.ZIP_DEFLATED)
    return files


if __name__ == "__main__":
    import sys
    print(len(build(sys.argv[1])), "parts")
