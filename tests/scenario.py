"""Each scenario runs in a fresh interpreter: security grants are global."""

import json
import sys
from pathlib import Path

from Products.PythonScripts.PythonScript import PythonScript
from Products.RestrictedPythonExtensions.policy import member_key, object_key, symbol_key
from Products.RestrictedPythonExtensions.registry import FEATURES
from Products.RestrictedPythonExtensions.runtime import activate


def run(source, **bound):
    script = PythonScript("restrictedpythonextensions_probe")
    script.write(source)
    assert not script.errors, script.errors
    return script._exec(bound, (), {})


def denied(source):
    try:
        run(source)
    except (ImportError, AttributeError) as exc:
        print(type(exc).__name__)
        return
    except Exception as exc:
        from AccessControl import Unauthorized
        from zExceptions import Unauthorized as ZopeUnauthorized
        if isinstance(exc, (Unauthorized, ZopeUnauthorized)):
            print(type(exc).__name__)
            return
        raise
    raise AssertionError("Restricted script unexpectedly had access")


def main(mode):
    if mode == "disabled":
        activate()
        denied("from io import BytesIO\nreturn BytesIO()")
        denied("from PIL import Image\nreturn Image.new('RGB', (2, 2))")
        denied("from reportlab.pdfgen.canvas import Canvas\nreturn Canvas")
    elif mode == "bytesio":
        activate(("bytesio",))
        assert run("from io import BytesIO\nb = BytesIO()\nb.write(b'abc')\nb.seek(0)\nreturn (b.read(), b.getvalue(), b.tell())") == (b"abc", b"abc", 3)
        assert run("from io import BytesIO\nb=BytesIO(b'abc')\nv=b.getbuffer()\nresult=(v.nbytes,v.tobytes())\nv.release()\nreturn result") == (3,b"abc")
        denied("from io import open\nreturn open")
        denied("from io import FileIO\nreturn FileIO")
    elif mode == "granular":
        activate(("pillow", "reportlab"), (
            member_key("reportlab.pdfgen.canvas:Canvas", "drawString"),
            symbol_key("PIL.Image", "open"),
            member_key("io:BytesIO", "truncate"),
        ))
        denied("from reportlab.pdfgen.canvas import Canvas\nfrom io import BytesIO\nc=Canvas(BytesIO())\nc.drawString(1, 1, 'denied')")
        denied("from PIL import Image\nreturn Image.open")
        denied("from io import BytesIO\nreturn BytesIO().truncate()")
        assert run("from PIL import Image\nreturn Image.new('RGB',(3,4)).size") == (3,4)
        assert run("from reportlab.pdfgen.canvas import Canvas\nfrom io import BytesIO\nb=BytesIO()\nc=Canvas(b)\nc.drawRightString(1,1,'ok')\nc.save()\nreturn b.getvalue()[:5]") == b"%PDF-"
    elif mode == "object_off":
        activate(("reportlab",), (object_key("reportlab.pdfgen.canvas:Canvas"),))
        denied("from reportlab.pdfgen.canvas import Canvas\nreturn Canvas")
    elif mode == "media":
        activate(FEATURES)
        result = run('''from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import red
buf = BytesIO()
im = Image.new('RGB', (200, 100), 'white')
draw = ImageDraw.Draw(im)
draw.text((10, 10), 'RestrictedPythonExtensions', font=ImageFont.load_default(), fill='black')
im = im.resize((400, 200), Image.Resampling.LANCZOS)
im = ImageOps.mirror(im)
im = ImageEnhance.Contrast(im).enhance(1.2)
im.save(buf, format='PNG')
buf.seek(0)
im2 = Image.open(buf)
pdf = BytesIO()
c = Canvas(pdf, pagesize=A4)
c.drawImage(ImageReader(im2), 25, 500, 400, 200)
c.setFillColor(red)
c.drawString(25, 740, 'RestrictedPythonExtensions: direct Pillow + ReportLab + BytesIO')
t = c.beginText(25, 460)
t.setFont('Helvetica', 12)
t.textLine('Generated inside a restricted Zope Python Script.')
c.drawText(t)
p = c.beginPath()
p.moveTo(25, 450)
p.lineTo(550, 450)
c.drawPath(p)
c.save()
return (im2.size, buf.getvalue(), pdf.getvalue())
''')
        assert result[0] == (400, 200)
        assert result[1].startswith(b"\x89PNG")
        assert result[2].startswith(b"%PDF-")
        output = Path(__file__).resolve().parents[1] / "test-output"
        output.mkdir(exist_ok=True)
        (output / "restricted-script.png").write_bytes(result[1])
        (output / "restricted-script.pdf").write_bytes(result[2])
        print(json.dumps({"image_size": result[0], "png_bytes": len(result[1]), "pdf_bytes": len(result[2])}))
    elif mode == "helpers":
        activate(("pdf_helpers", "image_helpers", "pillow"))
        assert run('''from Products.RestrictedPythonExtensions import PdfBuffer, ImageBuffer
p = PdfBuffer()
p.write(b'pdf helper')
im = ImageBuffer(120, 80)
im.rectangle(0,0,30,30,fill='blue')
im.roundedRectangle(40,0,75,30,fill='red')
im.ellipse(0,40,30,70,fill='green')
im.line(0,0,100,60)
im.polygon([(0,0),(10,10),(20,0)])
im.text(4,4,'Test',size=12)
im.rotatedText(60,40,'Rotate',angle=30,size=12)
im.multilineText(0,20,'A\\nB',size=10)
size = im.fitText(0,0,'fit',100)
data = im.getvalue(format='PNG')
clone = ImageBuffer.fromBytes(data)
clone.resizeCanvas(60,40)
clone.cropCanvas(0,0,30,20)
clone.pasteImageBytes(data,0,0,width=15,height=10)
return (p.getvalue(), clone.width, clone.height, clone.getvalue(format='PNG')[:4])
''') == (b"pdf helper", 30, 20, b"\x89PNG")
    elif mode == "platypus":
        activate(("platypus",))
        result = run('''from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
b = BytesIO()
styles = getSampleStyleSheet()
table = Table([['A','B'],['1','2']])
table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),1,colors.black)]))
doc = SimpleDocTemplate(b)
doc.build([Paragraph('RestrictedPythonExtensions', styles['Normal']), Spacer(1,12), table])
return b.getvalue()[:5]
''')
        assert result == b"%PDF-"
    elif mode == "xml":
        activate(("xml",))
        assert run('''from xml.etree.ElementTree import fromstring, tostring, Element
root = fromstring('<orders><order id="42">Hello</order></orders>')
order = root.find('order')
return (order.tag, order.get('id'), order.text, tostring(Element('ok')))
''') == ('order', '42', 'Hello', b'<ok />')
    elif mode == "barcodes":
        activate(("barcodes",))
        assert run('''from io import BytesIO
from reportlab.pdfgen.canvas import Canvas
from reportlab.graphics.barcode.code128 import Code128
from reportlab.graphics.barcode.ecc200datamatrix import ECC200DataMatrix
b = BytesIO()
c = Canvas(b)
Code128('123456').drawOn(c, 10, 10)
matrix = ECC200DataMatrix('RestrictedPythonExtensions', x=0, y=0)
matrix.validate()
matrix.encode()
matrix.drawOn(c, 10, 100)
c.save()
return b.getvalue()[:5]
''') == b'%PDF-'
    elif mode == "http":
        from http.server import BaseHTTPRequestHandler, HTTPServer
        from threading import Thread
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'restrictedpythonextensions-http-test')
            def log_message(self, *args):
                pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            activate(('http',))
            assert run(f'''from urllib.request import urlopen
from urllib.parse import urlencode
response = urlopen('http://127.0.0.1:{server.server_port}/', timeout=5)
body = response.read()
status = response.status
response.close()
return (body, status, urlencode({{'a': 'b c'}}))
''') == (b'restrictedpythonextensions-http-test', 200, 'a=b+c')
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
    else:
        raise ValueError(mode)


if __name__ == "__main__":
    main(sys.argv[1])
