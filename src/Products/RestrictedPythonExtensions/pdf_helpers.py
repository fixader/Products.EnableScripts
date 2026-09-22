"""PDF helpers adapted from the supplied GlobalModule."""

from io import BytesIO
from .responses import inline_filename as _inline_filename


class PdfBuffer:

    def __init__(self):
        self.buffer = BytesIO()

    def write(self, data):
        return self.buffer.write(data)

    def getvalue(self):
        return self.buffer.getvalue()

    def seek(self, pos):
        return self.buffer.seek(pos)

    def tell(self):
        return self.buffer.tell()

    def flush(self):
        pass

    def toResponse(self, response, filename="document.pdf"):
        response.setHeader("Content-Type", "application/pdf")
        response.setHeader("Content-Disposition", _inline_filename(filename))
        response.write(self.buffer.getvalue())
        return ""


def send_pdf_response(response, pdf_bytes, filename="document.pdf"):
    response.setHeader("Content-Type", "application/pdf")
    response.setHeader("Content-Disposition", _inline_filename(filename))
    response.write(pdf_bytes)
    return ""
