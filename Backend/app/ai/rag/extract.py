"""Extract text from PDF, Word, text, and image files."""

import io
from pathlib import Path

import pytesseract
from PIL import Image

from . import loaders

UnsupportedDocument = loaders.UnsupportedDocument


def extract_image(data):
    """Extract text from an image using OCR."""

    image = Image.open(io.BytesIO(data))

    return pytesseract.image_to_string(image)


def extract_text(filename, content_type, data):
    """Extract text based on file type."""

    extension = Path(filename or "").suffix.lower()

    if extension in [".jpg", ".jpeg", ".png"] or (
        content_type and content_type.startswith("image/")
    ):
        return extract_image(data)

    return loaders.extract_text(filename, content_type, data)


def extract_path(path):
    """Extract text from a local file."""

    path = Path(path)

    return extract_text(
        path.name,
        None,
        path.read_bytes()
    )
