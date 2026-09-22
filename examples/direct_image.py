## Script (Python): enable BytesIO and Pillow first.
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

image = Image.new("RGB", (800, 280), "#f4f6f8")
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((25, 25, 775, 255), radius=20, fill="#245da2")
draw.text((50, 70), "RestrictedPythonExtensions", fill="white", font=ImageFont.load_default(size=40))
draw.text((50, 150), "Pillow + BytesIO inside Script (Python)", fill="white", font=ImageFont.load_default(size=24))
output = BytesIO()
image.save(output, format="PNG")
context.REQUEST.RESPONSE.setHeader("Content-Type", "image/png")
return output.getvalue()
