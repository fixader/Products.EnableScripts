## Script (Python): enable BytesIO, Pillow and ReportLab Canvas first.
from io import BytesIO
from PIL import Image, ImageDraw
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader

image = Image.new("RGB", (400, 150), "white")
ImageDraw.Draw(image).text((20, 20), "Hello from RestrictedPythonExtensions", fill="black")
output = BytesIO()
canvas = Canvas(output)
canvas.drawImage(ImageReader(image), 30, 550, width=400, height=150)
canvas.save()
context.REQUEST.RESPONSE.setHeader("Content-Type", "application/pdf")
return output.getvalue()
