from django.templatetags.static import static


def get_default_image_url() -> str:
    """Return the URL of the default image."""
    return static("images/default-image.png")


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def generate_simple_pdf(title: str, lines: list[str]) -> bytes:
    """Generate a simple single-page PDF with a title and plain text lines."""
    max_lines = 46
    content_lines = [
        "BT",
        "/F1 16 Tf",
        "50 800 Td",
        f"({_escape_pdf_text(title)}) Tj",
        "/F1 11 Tf",
        "0 -28 Td",
    ]

    for index, line in enumerate(lines):
        if index >= max_lines:
            break
        content_lines.extend(
            [f"({_escape_pdf_text(str(line))}) Tj", "0 -16 Td"]
        )
    content_lines.append("ET")

    content_stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
        ),
        b"<< /Length "
        + str(len(content_stream)).encode("ascii")
        + b" >>\nstream\n"
        + content_stream
        + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    chunks = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = [0]

    for object_index, obj in enumerate(objects, start=1):
        offsets.append(sum(len(chunk) for chunk in chunks))
        chunks.append(f"{object_index} 0 obj\n".encode("ascii") + obj + b"\nendobj\n")

    xref_offset = sum(len(chunk) for chunk in chunks)
    xref = [f"xref\n0 {len(objects) + 1}\n".encode("ascii")]
    xref.append(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        xref.append(f"{offset:010d} 00000 n \n".encode("ascii"))

    trailer = (
        b"trailer\n"
        + f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n".encode("ascii")
        + b"startxref\n"
        + str(xref_offset).encode("ascii")
        + b"\n%%EOF\n"
    )

    return b"".join(chunks + xref + [trailer])
