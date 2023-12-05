from io import BytesIO

from django.http import FileResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status


def generate_pdf_file_response(items: dict[str, list]) -> FileResponse:
    """Функция для генерации pdf."""
    buffer = BytesIO()
    pdf_canvas = canvas.Canvas(buffer)
    pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
    pdf_canvas.setFont('Verdana', 11)
    pdf_canvas.drawString(250, 750, 'Shopping Cart')
    pdf_canvas.setFont('Verdana', 9)
    pdf_canvas.drawString(0, 720, '—' * 80)
    page_number = 1
    y = 700
    for name, value in items.items():
        pdf_canvas.drawString(100, y, f'{name} ({value[1]}) — {value[0]}')
        y -= 20
        if y < 50:
            pdf_canvas.setFont('Verdana', 11)
            pdf_canvas.drawString(
                0, 30, f'{"—"*23}End of the page {page_number}{"—"*23}'
            )
            pdf_canvas.showPage()
            pdfmetrics.registerFont(TTFont('Verdana', 'Verdana.ttf'))
            pdf_canvas.setFont('Verdana', 11)
            pdf_canvas.setFont('Verdana', 9)
            y = 750
    pdf_canvas.setFont('Verdana', 11)
    pdf_canvas.drawString(250, y - 40, 'Happy shopping!')
    pdf_canvas.setFont('Verdana', 9)
    pdf_canvas.drawString(480, 10, 'Produced by Foodgram')
    pdf_canvas.showPage()
    pdf_canvas.save()
    buffer.seek(0)
    return FileResponse(
        buffer,
        as_attachment=True,
        filename='shopping_cart.pdf',
        status=status.HTTP_200_OK,
    )
