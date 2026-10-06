import sys, io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
src, out = sys.argv[1], sys.argv[2]
reader = PdfReader(src); n = len(reader.pages)
w, h = letter
buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=letter)
for i in range(n):
    if i >= 1:  # skip title page
        c.setFillGray(0.35)
        c.setFont('Times-Roman', 9.5); c.drawCentredString(w/2, 0.55*72, str(i+1))
        c.setFont('Times-Italic', 8.5); c.drawCentredString(w/2, h-0.55*72, 'What Shakespeare Observes About Being Human')
    c.showPage()
c.save(); buf.seek(0)
overlay = PdfReader(buf); writer = PdfWriter()
for i, p in enumerate(reader.pages):
    p.merge_page(overlay.pages[i]); wp = writer.add_page(p); wp.compress_content_streams()
writer.add_metadata({'/Title': 'What Shakespeare Observes About Being Human', '/Author': 'Erik Salo', '/Subject': 'A synthesis from the text of the complete works'})
writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
with open(out, 'wb') as f: writer.write(f)
print(n, "pages")
