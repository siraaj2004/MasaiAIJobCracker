"""Minimal stdlib PDF writer for lesson notes (no external dependency)."""
import os

def _esc(s):
    return s.replace("\\", " ").replace("(", "[").replace(")", "]")

def make_pdf(title, lines, out_path):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    content_lines = ["BT /F1 18 Tf 50 800 Td (%s) Tj ET" % _esc(title[:80])]
    y = 770
    stream = [content_lines[0]]
    for ln in lines:
        for chunk in [ln[i:i+95] for i in range(0, max(len(ln), 1), 95)]:
            if y < 50: break
            stream.append("BT /F1 11 Tf 50 %d Td (%s) Tj ET" % (y, _esc(chunk)))
            y -= 16
    body = "\n".join(stream).encode("utf-8", "replace")
    objs = []
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objs.append(("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>").encode())
    objs.append(b"<< /Length " + str(len(body)).encode() + b" >>\nstream\n" + body + b"\nendstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n"); offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out)); out += ("%d 0 obj\n" % i).encode() + o + b"\nendobj\n"
    xref = len(out)
    out += ("xref\n0 %d\n0000000000 65535 f \n" % (len(objs)+1)).encode()
    for off in offsets: out += ("%010d 00000 n \n" % off).encode()
    out += ("trailer << /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF" % (len(objs)+1, xref)).encode()
    open(out_path, "wb").write(bytes(out))
    return out_path
