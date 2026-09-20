"""ImageBuffer adapted from the supplied GlobalModule."""

from io import BytesIO
from .responses import inline_filename as _inline_filename
from PIL import Image, ImageDraw, ImageFont


class ImageBuffer:

    _FONT_PATHS = {
        "DejaVuSans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "DejaVuSans-Bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Arial": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    }

    def __init__(self, width=1200, height=800, background="#ffffff"):
        self.width = int(width)
        self.height = int(height)
        self.image = Image.new("RGB", (self.width, self.height), self._color(background))
        self.draw = ImageDraw.Draw(self.image)

    @classmethod
    def fromBytes(cls, image_data):
        buffer = cls(1, 1)
        buffer.loadBytesAsCanvas(image_data)
        return buffer

    def _color(self, value, default=(0, 0, 0)):
        if value is None:
            return default
        if isinstance(value, tuple):
            return value
        value = str(value).strip()
        if value.startswith("#") and len(value) == 7:
            return (
                int(value[1:3], 16),
                int(value[3:5], 16),
                int(value[5:7], 16),
            )
        named = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "red": (220, 40, 40),
            "green": (35, 125, 75),
            "blue": (40, 95, 165),
            "gray": (140, 140, 140),
            "grey": (140, 140, 140),
        }
        return named.get(value.lower(), default)

    def _font(self, size=32, bold=False, font_path="", font_name=""):
        if font_path:
            return ImageFont.truetype(font_path, int(size))
        if font_name:
            font_path = self._FONT_PATHS.get(str(font_name), "")
            if font_path:
                return ImageFont.truetype(font_path, int(size))
        if bold:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        else:
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        try:
            return ImageFont.truetype(font_path, int(size))
        except Exception:
            return ImageFont.load_default()

    def _bytes_to_image(self, image_data):
        try:
            image_data = image_data.encode("latin-1")
        except AttributeError:
            pass
        return Image.open(BytesIO(image_data)).convert("RGBA")

    def _resample(self, name="bicubic"):
        name = str(name or "bicubic").lower()
        if name in ("nearest", "none"):
            return Image.NEAREST
        if name in ("lanczos", "antialias", "high"):
            return Image.LANCZOS
        return Image.BICUBIC

    def _fit(self, image, width, height, mode="contain"):
        width = int(width)
        height = int(height)
        src_w, src_h = image.size
        if mode == "cover":
            scale = max(float(width) / src_w, float(height) / src_h)
        else:
            scale = min(float(width) / src_w, float(height) / src_h)
        new_size = (max(1, int(src_w * scale)), max(1, int(src_h * scale)))
        resized = image.resize(new_size, Image.LANCZOS)
        if mode == "cover":
            left = max(0, (resized.size[0] - width) // 2)
            top = max(0, (resized.size[1] - height) // 2)
            return resized.crop((left, top, left + width, top + height))
        return resized

    def resizeCanvas(self, width, height, resample="bicubic"):
        self.width = int(width)
        self.height = int(height)
        self.image = self.image.resize((self.width, self.height), self._resample(resample))
        self.draw = ImageDraw.Draw(self.image)

    def cropCanvas(self, x1, y1, x2, y2):
        self.image = self.image.crop((int(x1), int(y1), int(x2), int(y2)))
        self.width, self.height = self.image.size
        self.draw = ImageDraw.Draw(self.image)

    def loadBytesAsCanvas(self, image_data):
        self.image = self._bytes_to_image(image_data)
        self.width, self.height = self.image.size
        self.draw = ImageDraw.Draw(self.image)
        return self.image.size

    def loadZopeImage(self, image_obj):
        return self._bytes_to_image(image_obj.data)

    def pasteRawImage(self, image, x, y, width=0, height=0, mode="contain", opacity=1.0):
        image = image.convert("RGBA")
        if width and height:
            image = self._fit(image, width, height, mode)
        elif width:
            ratio = float(width) / image.size[0]
            image = image.resize((int(width), int(image.size[1] * ratio)), Image.LANCZOS)
        elif height:
            ratio = float(height) / image.size[1]
            image = image.resize((int(image.size[0] * ratio), int(height)), Image.LANCZOS)
        if opacity < 1:
            alpha = image.getchannel("A").point(lambda p: int(p * float(opacity)))
            image.putalpha(alpha)
        self.image.paste(image, (int(x), int(y)), image)
        self.draw = ImageDraw.Draw(self.image)
        return image.size

    def pasteImage(self, image_obj, x, y, width=0, height=0, mode="contain", opacity=1.0):
        return self.pasteRawImage(
            self.loadZopeImage(image_obj),
            x,
            y,
            width=width,
            height=height,
            mode=mode,
            opacity=opacity,
        )

    def pasteImageBytes(self, image_data, x, y, width=0, height=0, mode="contain", opacity=1.0):
        return self.pasteRawImage(
            self._bytes_to_image(image_data),
            x,
            y,
            width=width,
            height=height,
            mode=mode,
            opacity=opacity,
        )

    def rectangle(self, x1, y1, x2, y2, fill="", outline="#000000", width=1):
        self.draw.rectangle(
            (int(x1), int(y1), int(x2), int(y2)),
            fill=self._color(fill, None) if fill else None,
            outline=self._color(outline) if outline else None,
            width=int(width),
        )

    def roundedRectangle(self, x1, y1, x2, y2, radius=12, fill="", outline="#000000", width=1):
        self.draw.rounded_rectangle(
            (int(x1), int(y1), int(x2), int(y2)),
            radius=int(radius),
            fill=self._color(fill, None) if fill else None,
            outline=self._color(outline) if outline else None,
            width=int(width),
        )

    def line(self, x1, y1, x2, y2, fill="#000000", width=1):
        self.draw.line(
            (int(x1), int(y1), int(x2), int(y2)),
            fill=self._color(fill),
            width=int(width),
        )

    def ellipse(self, x1, y1, x2, y2, fill="", outline="#000000", width=1):
        self.draw.ellipse(
            (int(x1), int(y1), int(x2), int(y2)),
            fill=self._color(fill, None) if fill else None,
            outline=self._color(outline) if outline else None,
            width=int(width),
        )

    def polygon(self, points, fill="", outline="#000000"):
        clean_points = []
        for point in points:
            clean_points.append((int(point[0]), int(point[1])))
        self.draw.polygon(
            clean_points,
            fill=self._color(fill, None) if fill else None,
            outline=self._color(outline) if outline else None,
        )

    def textSize(self, text, size=32, bold=False, font_path="", font_name=""):
        font = self._font(size=size, bold=bold, font_path=font_path, font_name=font_name)
        text = str(text)
        try:
            bbox = self.draw.textbbox((0, 0), text, font=font)
            return (bbox[2] - bbox[0], bbox[3] - bbox[1])
        except Exception:
            return self.draw.textsize(text, font=font)

    def text(self, x, y, text, size=32, fill="#000000", bold=False, align="left", font_path="", font_name=""):
        font = self._font(size=size, bold=bold, font_path=font_path, font_name=font_name)
        text = str(text)
        text_width = self.textSize(text, size=size, bold=bold, font_path=font_path, font_name=font_name)[0]
        x = int(x)
        if align == "center":
            x = x - text_width // 2
        elif align == "right":
            x = x - text_width
        self.draw.text((x, int(y)), text, font=font, fill=self._color(fill))

    def rotatedText(
        self,
        x,
        y,
        text,
        angle=0,
        size=32,
        fill="#000000",
        bold=False,
        align="left",
        font_path="",
        font_name="",
        center=False,
    ):
        font = self._font(size=size, bold=bold, font_path=font_path, font_name=font_name)
        text = str(text)
        try:
            bbox = font.getbbox(text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            offset_x = -bbox[0]
            offset_y = -bbox[1]
        except Exception:
            text_width, text_height = font.getsize(text)
            offset_x = 0
            offset_y = 0

        layer = Image.new("RGBA", (max(1, text_width), max(1, text_height)), (0, 0, 0, 0))
        layer_draw = ImageDraw.Draw(layer)
        layer_draw.text((offset_x, offset_y), text, font=font, fill=self._color(fill))
        layer = layer.rotate(float(angle), expand=1)

        x = int(x)
        y = int(y)
        if center:
            x = x - layer.size[0] // 2
            y = y - layer.size[1] // 2
        elif align == "center":
            x = x - layer.size[0] // 2
        elif align == "right":
            x = x - layer.size[0]

        self.image.paste(layer, (x, y), layer)
        self.draw = ImageDraw.Draw(self.image)
        return layer.size

    def fitText(
        self,
        x,
        y,
        text,
        max_width,
        max_size=72,
        min_size=8,
        fill="#000000",
        bold=False,
        align="left",
        font_path="",
        font_name="",
    ):
        size = int(max_size)
        min_size = int(min_size)
        while size > min_size:
            text_width = self.textSize(text, size=size, bold=bold, font_path=font_path, font_name=font_name)[0]
            if text_width <= int(max_width):
                break
            size = size - 1
        self.text(
            x,
            y,
            text,
            size=size,
            fill=fill,
            bold=bold,
            align=align,
            font_path=font_path,
            font_name=font_name,
        )
        return size

    def multilineText(self, x, y, text, size=24, fill="#000000", spacing=6, font_path="", font_name=""):
        font = self._font(size=size, font_path=font_path, font_name=font_name)
        self.draw.multiline_text(
            (int(x), int(y)),
            str(text),
            font=font,
            fill=self._color(fill),
            spacing=int(spacing),
        )

    def getvalue(self, format="JPEG", quality=90):
        output = BytesIO()
        image = self.image
        if str(format).upper() == "JPEG":
            image = image.convert("RGB")
        image.save(output, format=str(format).upper(), quality=int(quality))
        return output.getvalue()

    def toResponse(self, response, filename="image.jpg", format="JPEG", quality=90):
        content_type = "image/jpeg"
        if str(format).upper() == "PNG":
            content_type = "image/png"
        response.setHeader("Content-Type", content_type)
        response.setHeader("Content-Disposition", _inline_filename(filename))
        response.write(self.getvalue(format=format, quality=quality))
        return ""
