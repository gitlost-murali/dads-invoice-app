from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    invoice_data = request.form
    items = json.loads(invoice_data.get('items'))

    # Set up the PDF document
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=1*inch, bottomMargin=1*inch)
    story = []

    # Add header
    styles = getSampleStyleSheet()
    header = Paragraph("Invoice", styles['Heading1'])
    story.append(header)

    # Add invoice and delivery addresses, GST number, date, and vehicle number
    story.append(Paragraph("<b>Invoice Address:</b> " + invoice_data['invoice_address'], styles['Normal']))
    story.append(Paragraph("<b>Delivery Address:</b> " + invoice_data['delivery_address'], styles['Normal']))
    story.append(Paragraph("<b>GST Number:</b> " + invoice_data['gst_number'], styles['Normal']))
    story.append(Paragraph("<b>Date:</b> " + invoice_data['date'], styles['Normal']))
    story.append(Paragraph("<b>Vehicle Number:</b> " + invoice_data['vehicle_number'], styles['Normal']))

    # Add a spacer
    story.append(Spacer(1, 0.5 * inch))

    # Add items table
    items_data = [["Colour Name", "Lot ID", "No of pcs", "Total sft", "Rate", "Amount"]]
    for item in items:
        items_data.append([
            item['colorName'],
            item['lotId'],
            item['noOfPcs'],
            item['totalSft'],
            item['rate'],
            item['amount']
        ])
    items_table = Table(items_data)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(items_table)

    # Add a spacer
    story.append(Spacer(1, 0.5 * inch))

    # Add expenses section
    expenses_data = [
        ["Transport charges:", invoice_data['transport_charges']],
        ["Loading & Unloading charges:", invoice_data['loading_unloading_charges']],
        ["Sub Total:", invoice_data['sub_total']],
        ["GST @ 18%:", invoice_data['gst']],
        ["Grand Total:", invoice_data['grand_total']]
    ]
    for expense in expenses_data:
        expense_line = Paragraph("<b>" + expense[0] + "</b> " + expense[1], styles['Normal'])
        expense_line.style.alignment = TA_RIGHT
        story.append(expense_line)

    # Build and save the PDF
    doc.build(story)

    pdf_buffer.seek(0)
    return send_file(pdf_buffer, attachment_filename='invoice.pdf', as_attachment=True, mimetype='application/pdf')


if __name__ == "__main__":
    app.run()