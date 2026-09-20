"""Supported public APIs. Library internals are deliberately not exported."""

from .registry import Feature, register


def names(text):
    return tuple(text.split())


register(Feature(
    "bytesio", "io.BytesIO", "Binary streams in memory: read, write, seek and getvalue.",
    modules={"io": ("BytesIO",)},
    types={
        "io:BytesIO": names("read read1 readinto readinto1 readline readlines write writelines seek tell truncate flush getvalue getbuffer close closed readable writable seekable detach fileno isatty"),
        "builtins:memoryview": names("nbytes readonly format ndim itemsize shape strides contiguous c_contiguous f_contiguous tobytes tolist hex release cast toreadonly"),
    },
))

register(Feature(
    "pillow", "Pillow", "Direct imports of Image, ImageDraw, ImageFont, ImageOps and ImageEnhance.",
    distributions=("Pillow",), requires=("bytesio",),
    modules={
        "PIL.Image": names("new open frombytes blend composite alpha_composite merge Resampling Transpose Transform Dither Palette Quantize NEAREST BILINEAR BICUBIC LANCZOS"),
        "PIL.ImageDraw": ("Draw",),
        "PIL.ImageFont": names("truetype load_default"),
        "PIL.ImageOps": names("autocontrast colorize contain cover crop equalize expand fit flip grayscale invert mirror pad posterize scale solarize exif_transpose"),
        "PIL.ImageEnhance": names("Color Contrast Brightness Sharpness"),
    },
    classes={
        "PIL.Image:Image": names("size width height mode format info copy convert crop resize rotate transpose transform thumbnail paste alpha_composite blend close load getpixel putpixel getdata putdata getbbox getextrema getcolors getbands getchannel split merge point filter histogram quantize reduce putalpha save seek tell getexif"),
        "PIL.ImageDraw:ImageDraw": names("arc bitmap chord ellipse line pieslice point polygon rectangle regular_polygon rounded_rectangle text textbbox textlength multiline_text multiline_textbbox"),
        "PIL.ImageFont:ImageFont": names("getbbox getlength"),
        "PIL.ImageFont:FreeTypeFont": names("getbbox getlength getmetrics getname font_variant"),
        "PIL.ImageFont:TransposedFont": names("getbbox getlength"),
        "PIL.Image:Exif": names("get items keys values"),
        **{f"PIL.ImageEnhance:{name}": ("enhance",) for name in ("Color", "Contrast", "Brightness", "Sharpness")},
        **{f"PIL.Image:{name}": members for name, members in {
            "Resampling": names("NEAREST BOX BILINEAR HAMMING BICUBIC LANCZOS"),
            "Transpose": names("FLIP_LEFT_RIGHT FLIP_TOP_BOTTOM ROTATE_90 ROTATE_180 ROTATE_270 TRANSPOSE TRANSVERSE"),
            "Transform": names("AFFINE EXTENT PERSPECTIVE QUAD MESH"),
            "Dither": names("NONE ORDERED RASTERIZE FLOYDSTEINBERG"),
            "Palette": names("WEB ADAPTIVE"),
            "Quantize": names("MEDIANCUT MAXCOVERAGE FASTOCTREE LIBIMAGEQUANT"),
        }.items()},
    },
))

register(Feature(
    "reportlab", "ReportLab Canvas", "Canvas, text/path objects, ImageReader, page sizes, colors and fonts.",
    distributions=("reportlab",), requires=("bytesio",),
    modules={
        "reportlab.pdfgen.canvas": ("Canvas",),
        "reportlab.lib.utils": ("ImageReader",),
        "reportlab.lib.pagesizes": names("A0 A1 A2 A3 A4 A5 A6 B0 B1 B2 B3 B4 B5 B6 LETTER LEGAL ELEVENSEVENTEEN landscape portrait"),
        "reportlab.lib.units": names("inch cm mm pica"),
        "reportlab.lib.colors": names("Color CMYKColor PCMYKColor CMYKColorSep PCMYKColorSep HexColor black white red green blue yellow cyan magenta grey gray lightgrey darkgrey orange purple pink brown transparent"),
        "reportlab.pdfbase.pdfmetrics": names("registerFont registerFontFamily getFont getRegisteredFontNames stringWidth"),
        "reportlab.pdfbase.ttfonts": ("TTFont",),
    },
    classes={
        "reportlab.pdfgen.canvas:Canvas": names("save showPage getpdfdata setPageSize setPageRotation setTitle setAuthor setSubject setCreator setKeywords setFont setFontSize getAvailableFonts getPageNumber stringWidth drawString drawRightString drawCentredString drawAlignedString drawText beginText beginPath drawPath clipPath line lines grid rect roundRect circle ellipse arc wedge bezier drawImage drawInlineImage saveState restoreState translate rotate scale skew transform setDash setLineWidth setLineCap setLineJoin setMiterLimit setFillColor setFillColorRGB setFillColorCMYK setFillGray setStrokeColor setStrokeColorRGB setStrokeColorCMYK setStrokeGray setFillAlpha setStrokeAlpha bookmarkPage bookmarkHorizontalAbsolute addOutlineEntry linkAbsolute linkRect linkURL showBoundary"),
        "reportlab.pdfgen.textobject:PDFTextObject": names("setTextOrigin setTextTransform moveCursor setFont setLeading setCharSpace setWordSpace setHorizScale setTextRenderMode setRise setFillColor setFillColorRGB setFillColorCMYK setFillGray setStrokeColor setStrokeColorRGB setStrokeColorCMYK setStrokeGray textOut textLine textLines getX getY getCursor"),
        "reportlab.pdfgen.pathobject:PDFPathObject": names("moveTo lineTo curveTo arc arcTo rect ellipse circle roundRect close"),
        "reportlab.lib.utils:ImageReader": names("getSize getRGBData"),
        "reportlab.lib.colors:Color": names("red green blue alpha rgb rgba hexval int_rgb int_rgba clone"),
        "reportlab.lib.colors:CMYKColor": names("cyan magenta yellow black alpha density spotName cmyk cmyka rgb rgba clone"),
        "reportlab.pdfbase.ttfonts:TTFont": names("fontName stringWidth"),
    },
))

register(Feature(
    "platypus", "ReportLab Platypus", "Document layout: paragraphs, tables, flowables and styles.",
    distributions=("reportlab",), requires=("reportlab",),
    modules={
        "reportlab.platypus": names("SimpleDocTemplate BaseDocTemplate Paragraph Spacer Table LongTable TableStyle Image PageBreak KeepTogether KeepInFrame Flowable Frame PageTemplate NextPageTemplate"),
        "reportlab.lib.styles": names("getSampleStyleSheet ParagraphStyle ListStyle"),
        "reportlab.lib.enums": names("TA_LEFT TA_CENTER TA_RIGHT TA_JUSTIFY"),
    },
    classes={
        "reportlab.platypus.doctemplate:BaseDocTemplate": names("build addPageTemplates width height"),
        "reportlab.platypus.doctemplate:SimpleDocTemplate": names("build width height"),
        "reportlab.platypus.flowables:Flowable": names("wrap split drawOn width height"),
        "reportlab.platypus.tables:Table": names("setStyle wrap split drawOn"),
        "reportlab.platypus.tables:TableStyle": names("add getCommands"),
        "reportlab.lib.styles:StyleSheet1": names("add get list"),
        "reportlab.lib.styles:ParagraphStyle": names("name fontName fontSize leading alignment spaceBefore spaceAfter leftIndent rightIndent firstLineIndent textColor backColor clone"),
    },
))

register(Feature(
    "pdf_helpers", "PDF helpers", "PdfBuffer and send_pdf_response from your original GlobalModule.",
    requires=("bytesio",),
    classes={"Products.EnableScripts.pdf_helpers:PdfBuffer": names("buffer write getvalue seek tell flush toResponse")},
    exports={name: f"Products.EnableScripts.pdf_helpers:{name}" for name in ("PdfBuffer", "send_pdf_response")},
))

register(Feature(
    "image_helpers", "Image helpers", "Your ImageBuffer drawing, text, resizing and response helpers.",
    distributions=("Pillow",), requires=("bytesio",),
    classes={"Products.EnableScripts.image_helpers:ImageBuffer": names("image draw width height fromBytes resizeCanvas cropCanvas loadBytesAsCanvas loadZopeImage pasteRawImage pasteImage pasteImageBytes rectangle roundedRectangle line ellipse polygon textSize text rotatedText fitText multilineText getvalue toResponse")},
    exports={"ImageBuffer": "Products.EnableScripts.image_helpers:ImageBuffer"},
))

register(Feature(
    "zope_images", "Save images in Zope", "save_image_object, with Zope permission checks before replacement or creation.",
    exports={"save_image_object": "Products.EnableScripts.zope_helpers:save_image_object"},
))

# The supplied GlobalModule made *all* public names in these known modules
# available. Enumerate that installed version's API for granular checkboxes,
# rather than replacing it with a shorter list or a blanket allow_module().
def discover_legacy_apis():
    from dataclasses import replace
    from importlib import import_module
    from .registry import FEATURES, resolve

    extra_modules = {
        "reportlab": names("reportlab reportlab.rl_config reportlab.lib reportlab.pdfgen reportlab.pdfgen.common"),
        "platypus": names("reportlab.platypus.flowables"),
    }
    for key in ("reportlab", "platypus"):
        feature = FEATURES[key]
        modules = dict(feature.modules)
        for module_name in tuple(modules) + extra_modules.get(key, ()):
            try:
                module = import_module(module_name)
            except ImportError:
                continue
            modules[module_name] = tuple(sorted(set(modules.get(module_name, ())) | {
                name for name in vars(module) if not name.startswith("_")
            }))
        # Parent packages expose only child modules belonging to this feature;
        # otherwise a disabled Platypus integration could be reached via a
        # reportlab.platypus attribute on the parent.
        import types
        for module_name in modules:
            try:
                module = import_module(module_name)
            except ImportError:
                continue
            modules[module_name] = tuple(
                name for name in modules[module_name]
                if not isinstance(getattr(module, name, None), types.ModuleType)
            )
        classes = dict(feature.classes)
        if key == "reportlab":
            for path in ("reportlab.pdfgen.canvas:Canvas", "reportlab.lib.utils:ImageReader"):
                try:
                    cls = resolve(path)
                except ImportError:
                    continue
                classes[path] = tuple(sorted(set(classes[path]) | {
                    name for name in dir(cls) if not name.startswith("_")
                }))
        FEATURES[key] = replace(feature, modules=modules, classes=classes)

    # Kept separate so enabling BytesIO alone never opens io.open/FileIO.
    import io
    register(Feature(
        "io_extended", "io – extended compatibility", "Other public io exports from the original GlobalModule, including filesystem IO.",
        requires=("bytesio",),
        modules={"io": tuple(name for name in vars(io) if not name.startswith("_") and name != "BytesIO")},
        types={"io:StringIO": names("read readline readlines write writelines seek tell truncate flush getvalue close closed readable writable seekable")},
    ))


discover_legacy_apis()


def discovered_feature(key, title, description, module_names, class_paths=(),
                       type_paths=(), distributions=(), requires=(), extra_members=None):
    """Describe an explicitly supported library version, without granting it."""
    from importlib import import_module
    from types import ModuleType
    from .registry import resolve

    modules = {}
    classes = {}
    types = {}
    extra_members = extra_members or {}
    for module_name in module_names:
        try:
            module = import_module(module_name)
            modules[module_name] = tuple(sorted(
                name for name, value in vars(module).items()
                if not name.startswith("_") and not isinstance(value, ModuleType)
            ))
        except Exception:
            # An empty list still makes prepare() check whether import works.
            modules[module_name] = ()
    for paths, target in ((class_paths, classes), (type_paths, types)):
        for path in paths:
            try:
                cls = resolve(path)
                members = {name for name in dir(cls) if not name.startswith("_")}
            except Exception:
                members = set()
            target[path] = tuple(sorted(members | set(extra_members.get(path, ()))))
    register(Feature(key, title, description, modules, classes, types,
                     distributions, requires))


discovered_feature(
    "xml", "XML / ElementTree", "XML imports and element objects previously enabled on the lab server.",
    ("xml", "xml.etree", "xml.etree.ElementTree"),
    class_paths=("xml.etree.ElementTree:ElementTree",),
    type_paths=("xml.etree.ElementTree:Element", "xml.etree.ElementTree:XMLParser"),
    extra_members={"xml.etree.ElementTree:Element": names("tag text tail attrib")},
)

discovered_feature(
    "http", "HTTP / urllib", "URL parsing, HTTP requests and response objects from the lab GlobalModules.",
    ("urllib", "urllib.request", "urllib.error", "urllib.parse", "http", "http.client"),
    class_paths=("urllib.request:Request", "http.client:HTTPResponse", "http.client:HTTPConnection", "http.client:HTTPSConnection"),
    extra_members={"http.client:HTTPResponse": names("status reason headers version url")},
)

discovered_feature(
    "barcodes", "ReportLab barcodes", "Barcode, Code128 and ECC200 DataMatrix, including drawOn and inherited methods.",
    ("reportlab.graphics", "reportlab.graphics.barcode", "reportlab.graphics.barcode.common",
     "reportlab.graphics.barcode.code128", "reportlab.graphics.barcode.ecc200datamatrix"),
    class_paths=("reportlab.graphics.barcode.common:Barcode", "reportlab.graphics.barcode.common:MultiWidthBarcode",
                 "reportlab.graphics.barcode.code128:Code128", "reportlab.graphics.barcode.ecc200datamatrix:ECC200DataMatrix"),
    distributions=("reportlab",), requires=("reportlab",),
    extra_members={"reportlab.graphics.barcode.common:Barcode": names("value barWidth barHeight humanReadable")},
)

discovered_feature(
    "hubarcode", "Hubarcode DataMatrix", "The hubarcode modules enabled by the existing lab GlobalModules.",
    ("hubarcode", "hubarcode.datamatrix"),
    class_paths=("hubarcode.datamatrix:DataMatrixEncoder",),
    extra_members={"hubarcode.datamatrix:DataMatrixEncoder": names("matrix width height")},
)
