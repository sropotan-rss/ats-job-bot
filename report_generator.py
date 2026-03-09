from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def create_report(text, filename="report.pdf"):

    c = canvas.Canvas(filename, pagesize=A4)

    y = 800

    for line in text.split("\n"):

        c.drawString(40, y, line)

        y -= 20

        if y < 100:
            c.showPage()
            y = 800

    c.save()

    return filename
