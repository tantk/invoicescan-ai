"""
Generate 5 realistic demo invoice images for InvoiceScan AI hackathon demo.
Uses Pillow to create professional-looking invoice PNGs.
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Font setup
FONT_DIR = "C:/Windows/Fonts"

def font(size, bold=False):
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

def font_jp(size, bold=False):
    name = "YuGothB.ttc" if bold else "YuGothR.ttc"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

def font_mono(size):
    return ImageFont.truetype(os.path.join(FONT_DIR, "consola.ttf"), size)

# Color palette
BLACK = (30, 30, 30)
DARK_GRAY = (60, 60, 60)
MID_GRAY = (120, 120, 120)
LIGHT_GRAY = (200, 200, 200)
VERY_LIGHT = (240, 240, 240)
WHITE = (255, 255, 255)
ACCENT_BLUE = (25, 60, 120)
ACCENT_TEAL = (0, 120, 130)
ACCENT_GREEN = (34, 120, 60)
ACCENT_RED = (180, 30, 30)
ACCENT_ORANGE = (200, 100, 20)
HEADER_BG = (25, 60, 120)
ROW_ALT = (245, 248, 252)


def draw_hline(draw, y, x1, x2, color=LIGHT_GRAY, width=1):
    draw.line([(x1, y), (x2, y)], fill=color, width=width)


def draw_rect(draw, x1, y1, x2, y2, fill=None, outline=None, width=1):
    if fill:
        draw.rectangle([(x1, y1), (x2, y2)], fill=fill)
    if outline:
        draw.rectangle([(x1, y1), (x2, y2)], outline=outline, width=width)


# ===========================================================================
# Invoice 1: US Construction Invoice
# ===========================================================================
def create_us_construction_invoice():
    W, H = 800, 1100
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    margin = 50

    # Header band
    draw_rect(draw, 0, 0, W, 90, fill=ACCENT_BLUE)
    draw.text((margin, 18), "PACIFIC PIPELINE SOLUTIONS", font=font(26, True), fill=WHITE)
    draw.text((margin, 55), "Plumbing  |  Pipefitting  |  General Contracting", font=font(12), fill=(180, 200, 230))

    # Contact info row
    y = 105
    draw.text((margin, y), "1234 Industrial Blvd, San Jose, CA 95112", font=font(10), fill=MID_GRAY)
    draw.text((margin, y + 16), "Tel: (408) 555-0192  |  Fax: (408) 555-0193  |  info@pacificpipeline.com", font=font(9), fill=MID_GRAY)
    draw.text((margin, y + 32), "CA License #: 987654  |  Bonded & Insured", font=font(9), fill=MID_GRAY)

    # INVOICE title
    y = 165
    draw.text((W - margin - 200, y), "INVOICE", font=font(32, True), fill=ACCENT_BLUE)

    # Invoice details box (right side)
    bx = W - margin - 230
    by = 205
    draw_rect(draw, bx, by, W - margin, by + 80, fill=VERY_LIGHT, outline=LIGHT_GRAY)
    labels = [
        ("Invoice #:", "PPS-2026-0342"),
        ("Date:", "March 10, 2026"),
        ("Due Date:", "April 9, 2026"),
        ("Terms:", "Net 30"),
    ]
    for i, (lbl, val) in enumerate(labels):
        draw.text((bx + 10, by + 5 + i * 18), lbl, font=font(10, True), fill=DARK_GRAY)
        draw.text((bx + 90, by + 5 + i * 18), val, font=font(10), fill=BLACK)

    # Bill To
    y = 210
    draw.text((margin, y), "BILL TO:", font=font(10, True), fill=ACCENT_BLUE)
    y += 20
    draw.text((margin, y), "Bay Area Properties LLC", font=font(12, True), fill=BLACK)
    draw.text((margin, y + 18), "5678 Market Street, Suite 200", font=font(10), fill=DARK_GRAY)
    draw.text((margin, y + 32), "San Francisco, CA 94103", font=font(10), fill=DARK_GRAY)

    # Project code highlight
    y = 310
    draw_rect(draw, margin, y, W - margin, y + 30, fill=(255, 248, 230), outline=ACCENT_ORANGE)
    draw.text((margin + 12, y + 7), "Project Code: PRJ-BAYVIEW-2026", font=font(12, True), fill=ACCENT_ORANGE)
    draw.text((margin + 310, y + 8), "Site: Bayview Residential Complex - Building C", font=font(10), fill=DARK_GRAY)

    # Table header
    y = 360
    cols = [margin, margin + 280, margin + 350, margin + 450, margin + 560, W - margin]
    headers = ["Description", "Unit", "Qty", "Rate", "Amount"]
    draw_rect(draw, margin, y, W - margin, y + 28, fill=ACCENT_BLUE)
    hx_positions = [cols[0] + 8, cols[1] + 5, cols[2] + 5, cols[3] + 5, cols[4] + 5]
    for i, hdr in enumerate(headers):
        draw.text((hx_positions[i], y + 6), hdr, font=font(10, True), fill=WHITE)

    # Line items
    items = [
        ("PVC Pipe 4\" Schedule 40", "ft", "200", "$3.50", "$700.00"),
        ("Copper Fittings Assorted", "ea", "24", "$12.00", "$288.00"),
        ("Labor - Pipe Installation", "hr", "16", "$85.00", "$1,360.00"),
        ("Permit Fee (City of San Jose)", "ea", "1", "$150.00", "$150.00"),
    ]
    y += 28
    for idx, item in enumerate(items):
        row_y = y + idx * 30
        if idx % 2 == 1:
            draw_rect(draw, margin, row_y, W - margin, row_y + 30, fill=ROW_ALT)
        draw_rect(draw, margin, row_y, W - margin, row_y + 30, outline=VERY_LIGHT)
        draw.text((hx_positions[0], row_y + 8), item[0], font=font(10), fill=BLACK)
        draw.text((hx_positions[1], row_y + 8), item[1], font=font(10), fill=DARK_GRAY)
        draw.text((hx_positions[2], row_y + 8), item[2], font=font(10), fill=DARK_GRAY)
        draw.text((hx_positions[3], row_y + 8), item[3], font=font(10), fill=DARK_GRAY)
        draw.text((hx_positions[4], row_y + 8), item[4], font=font(10, True), fill=BLACK)

    # Bottom line under table
    y = y + len(items) * 30
    draw_hline(draw, y, margin, W - margin, ACCENT_BLUE, 2)

    # Totals section (right-aligned)
    ty = y + 15
    tx_label = W - margin - 250
    tx_val = W - margin - 80
    totals = [
        ("Materials Subtotal:", "$988.00", False),
        ("Labor Subtotal:", "$1,360.00", False),
        ("Permit Fees:", "$150.00", False),
        ("Subtotal:", "$2,498.00", True),
        ("CA Sales Tax (8.25% on materials):", "$81.51", False),
    ]
    for lbl, val, is_bold in totals:
        f = font(10, is_bold)
        draw.text((tx_label, ty), lbl, font=f, fill=DARK_GRAY if not is_bold else BLACK)
        draw.text((tx_val, ty), val, font=f, fill=BLACK)
        ty += 20

    # Separator
    draw_hline(draw, ty + 2, tx_label, W - margin, LIGHT_GRAY)
    ty += 10

    draw.text((tx_label, ty), "Gross Total:", font=font(10), fill=DARK_GRAY)
    draw.text((tx_val, ty), "$2,579.51", font=font(10), fill=BLACK)
    ty += 22

    # Retainage highlight
    draw_rect(draw, tx_label - 5, ty - 3, W - margin + 5, ty + 18, fill=(255, 240, 240), outline=ACCENT_RED)
    draw.text((tx_label, ty), "Retainage (10%):", font=font(10, True), fill=ACCENT_RED)
    draw.text((tx_val, ty), "-$249.80", font=font(10, True), fill=ACCENT_RED)
    ty += 28

    # Total due
    draw_rect(draw, tx_label - 5, ty - 3, W - margin + 5, ty + 24, fill=ACCENT_BLUE)
    draw.text((tx_label + 5, ty + 2), "TOTAL DUE:", font=font(13, True), fill=WHITE)
    draw.text((tx_val - 10, ty + 2), "$2,329.71", font=font(13, True), fill=WHITE)

    # Notes
    ny = ty + 50
    draw.text((margin, ny), "Notes:", font=font(10, True), fill=ACCENT_BLUE)
    notes = [
        "• Retainage held per contract until project completion.",
        "• Sales tax applies to materials only; labor is exempt per CA Rev & Tax Code.",
        "• Payment by check or ACH. Wire transfers accepted (contact for details).",
        "• Late payments subject to 1.5% monthly finance charge.",
    ]
    for i, note in enumerate(notes):
        draw.text((margin, ny + 18 + i * 16), note, font=font(9), fill=MID_GRAY)

    # Footer
    draw_hline(draw, H - 60, margin, W - margin, LIGHT_GRAY)
    draw.text((margin, H - 50), "Thank you for your business!", font=font(10, True), fill=ACCENT_BLUE)
    draw.text((margin, H - 34), "Pacific Pipeline Solutions — Making connections that last.", font=font(9), fill=MID_GRAY)

    img.save(os.path.join(OUTPUT_DIR, "us_construction_invoice.png"))
    print("Created: us_construction_invoice.png")


# ===========================================================================
# Invoice 2: India GST Invoice
# ===========================================================================
def create_india_gst_invoice():
    W, H = 800, 1100
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    margin = 45

    # Top accent bar
    draw_rect(draw, 0, 0, W, 8, fill=ACCENT_TEAL)

    # Company header
    y = 20
    draw.text((margin, y), "TechVista Solutions Pvt Ltd", font=font(24, True), fill=ACCENT_TEAL)
    draw.text((margin, y + 34), "IT Consulting  |  Cloud Services  |  Digital Transformation", font=font(10), fill=MID_GRAY)
    y += 55
    draw.text((margin, y), "Regd. Office: #401, 4th Floor, Prestige Towers, MG Road, Bangalore, Karnataka - 560001", font=font(9), fill=DARK_GRAY)
    draw.text((margin, y + 15), "CIN: U72200KA2015PTC087654  |  PAN: AADCT1234F  |  Email: billing@techvista.in", font=font(9), fill=DARK_GRAY)
    y += 30
    draw_rect(draw, margin, y, W - margin, y + 22, fill=(230, 245, 240))
    draw.text((margin + 8, y + 4), "GSTIN: 29AADCT1234F1ZP", font=font(11, True), fill=ACCENT_TEAL)

    # TAX INVOICE title
    y += 35
    draw_rect(draw, W // 2 - 80, y, W // 2 + 80, y + 30, fill=ACCENT_TEAL)
    draw.text((W // 2 - 50, y + 6), "TAX INVOICE", font=font(14, True), fill=WHITE)

    # Invoice details + Bill To side by side
    y += 48
    # Left: Bill To
    draw.text((margin, y), "Bill To:", font=font(10, True), fill=ACCENT_TEAL)
    y2 = y + 18
    draw.text((margin, y2), "Global Corp India Pvt Ltd", font=font(12, True), fill=BLACK)
    draw.text((margin, y2 + 18), "14th Floor, One BKC, Bandra Kurla Complex", font=font(9), fill=DARK_GRAY)
    draw.text((margin, y2 + 32), "Mumbai, Maharashtra - 400051", font=font(9), fill=DARK_GRAY)
    draw.text((margin, y2 + 48), "GSTIN: 27AABCG5678H1Z9", font=font(10, True), fill=DARK_GRAY)

    # Right: invoice meta
    rx = W - margin - 230
    draw_rect(draw, rx, y, W - margin, y + 95, fill=VERY_LIGHT, outline=LIGHT_GRAY)
    meta = [
        ("Invoice No:", "TVS/2026/1089"),
        ("Date:", "05-03-2026"),
        ("Place of Supply:", "Maharashtra (27)"),
        ("HSN/SAC:", "998314"),
        ("Reverse Charge:", "No"),
    ]
    for i, (lbl, val) in enumerate(meta):
        draw.text((rx + 8, y + 5 + i * 17), lbl, font=font(9, True), fill=DARK_GRAY)
        draw.text((rx + 105, y + 5 + i * 17), val, font=font(9), fill=BLACK)

    # Table
    y = y + 115
    cols_x = [margin, margin + 40, margin + 330, margin + 400, margin + 490, W - margin]
    headers = ["#", "Description of Service", "Qty", "Rate (₹)", "Amount (₹)"]
    draw_rect(draw, margin, y, W - margin, y + 26, fill=ACCENT_TEAL)
    hx = [cols_x[0] + 5, cols_x[1] + 5, cols_x[2] + 5, cols_x[3] + 5, cols_x[4] + 5]
    for i, h in enumerate(headers):
        draw.text((hx[i], y + 5), h, font=font(10, True), fill=WHITE)

    items = [
        ("1", "Cloud Migration Consulting\n(Assessment, Planning & Execution)", "120 hrs", "3,500.00", "4,20,000.00"),
        ("2", "DevOps Implementation\n(CI/CD Pipeline Setup & Training)", "80 hrs", "4,000.00", "3,20,000.00"),
        ("3", "AWS License Procurement\n(Annual Enterprise Agreement)", "Lumpsum", "—", "1,50,000.00"),
    ]

    y += 26
    for idx, item in enumerate(items):
        row_h = 40
        row_y = y + idx * row_h
        if idx % 2 == 1:
            draw_rect(draw, margin, row_y, W - margin, row_y + row_h, fill=ROW_ALT)
        draw_rect(draw, margin, row_y, W - margin, row_y + row_h, outline=VERY_LIGHT)
        draw.text((hx[0], row_y + 5), item[0], font=font(10), fill=DARK_GRAY)
        # Description: possibly two lines
        desc_lines = item[1].split("\n")
        draw.text((hx[1], row_y + 4), desc_lines[0], font=font(10), fill=BLACK)
        if len(desc_lines) > 1:
            draw.text((hx[1], row_y + 20), desc_lines[1], font=font(8), fill=MID_GRAY)
        draw.text((hx[2], row_y + 5), item[2], font=font(10), fill=DARK_GRAY)
        draw.text((hx[3], row_y + 5), item[3], font=font(10), fill=DARK_GRAY)
        draw.text((hx[4], row_y + 5), item[4], font=font(10, True), fill=BLACK)

    y = y + len(items) * 40
    draw_hline(draw, y, margin, W - margin, ACCENT_TEAL, 2)

    # Totals
    ty = y + 12
    tx_l = W - margin - 270
    tx_v = W - margin - 100
    rows = [
        ("Taxable Amount:", "₹8,90,000.00", False),
        ("IGST @ 18%:", "₹1,60,200.00", False),
        ("CGST:", "—", False),
        ("SGST:", "—", False),
    ]
    for lbl, val, bold in rows:
        draw.text((tx_l, ty), lbl, font=font(10, bold), fill=DARK_GRAY)
        draw.text((tx_v, ty), val, font=font(10, bold), fill=BLACK)
        ty += 20

    draw_hline(draw, ty + 2, tx_l, W - margin, LIGHT_GRAY)
    ty += 10
    draw_rect(draw, tx_l - 5, ty - 2, W - margin + 5, ty + 22, fill=ACCENT_TEAL)
    draw.text((tx_l + 5, ty + 2), "Total:", font=font(12, True), fill=WHITE)
    draw.text((tx_v - 10, ty + 2), "₹10,50,200.00", font=font(12, True), fill=WHITE)

    # Amount in words
    ty += 38
    draw_rect(draw, margin, ty, W - margin, ty + 25, fill=(230, 245, 240), outline=LIGHT_GRAY)
    draw.text((margin + 8, ty + 5), "Amount in Words: ", font=font(9, True), fill=DARK_GRAY)
    draw.text((margin + 120, ty + 5), "Rupees Ten Lakh Fifty Thousand Two Hundred Only", font=font(9), fill=BLACK)

    # Tax breakdown table
    ty += 40
    draw.text((margin, ty), "Tax Breakup (Interstate Supply — Karnataka to Maharashtra)", font=font(9, True), fill=ACCENT_TEAL)
    ty += 18
    tax_headers = ["HSN/SAC", "Taxable Value", "IGST Rate", "IGST Amount", "Total"]
    tw = (W - 2 * margin) // len(tax_headers)
    draw_rect(draw, margin, ty, W - margin, ty + 22, fill=VERY_LIGHT, outline=LIGHT_GRAY)
    for i, th in enumerate(tax_headers):
        draw.text((margin + i * tw + 5, ty + 4), th, font=font(9, True), fill=DARK_GRAY)
    ty += 22
    tax_row = ["998314", "₹8,90,000.00", "18%", "₹1,60,200.00", "₹10,50,200.00"]
    for i, tv in enumerate(tax_row):
        draw.text((margin + i * tw + 5, ty + 4), tv, font=font(9), fill=BLACK)

    # Bank details
    ty += 35
    draw.text((margin, ty), "Bank Details:", font=font(10, True), fill=ACCENT_TEAL)
    ty += 18
    bank = [
        "Bank: HDFC Bank, MG Road Branch, Bangalore",
        "A/C No: 50200012345678",
        "IFSC: HDFC0001234",
        "Swift: HDFCINBBXXX",
    ]
    for b in bank:
        draw.text((margin, ty), b, font=font(9), fill=DARK_GRAY)
        ty += 14

    # Terms
    ty += 10
    draw.text((margin, ty), "Terms & Conditions:", font=font(9, True), fill=DARK_GRAY)
    ty += 15
    draw.text((margin, ty), "1. Payment due within 30 days.  2. Interest @ 18% p.a. on delayed payments.", font=font(8), fill=MID_GRAY)
    draw.text((margin, ty + 13), "3. Subject to Bangalore jurisdiction.  4. E&OE.", font=font(8), fill=MID_GRAY)

    # Signature area
    draw.text((W - margin - 200, ty + 30), "For TechVista Solutions Pvt Ltd", font=font(9, True), fill=DARK_GRAY)
    draw.text((W - margin - 200, ty + 60), "Authorized Signatory", font=font(9), fill=MID_GRAY)

    # Footer bar
    draw_rect(draw, 0, H - 30, W, H, fill=ACCENT_TEAL)
    draw.text((margin, H - 24), "This is a computer-generated invoice and does not require a physical signature.", font=font(8), fill=WHITE)

    img.save(os.path.join(OUTPUT_DIR, "india_gst_invoice.png"))
    print("Created: india_gst_invoice.png")


# ===========================================================================
# Invoice 3: German EU Invoice (Reverse Charge)
# ===========================================================================
def create_eu_german_invoice():
    W, H = 800, 1100
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    margin = 50

    # Minimal German style: dark header bar
    draw_rect(draw, 0, 0, W, 6, fill=(40, 40, 40))

    # Company name
    y = 25
    draw.text((margin, y), "Schmidt & Weber GmbH", font=font(26, True), fill=BLACK)
    draw.text((margin, y + 36), "Unternehmensberatung  •  Softwareentwicklung", font=font(10), fill=MID_GRAY)

    # Company details right
    rx = W - margin - 250
    draw.text((rx, y + 5), "Berliner Str. 45", font=font(10), fill=DARK_GRAY)
    draw.text((rx, y + 20), "80331 München, Deutschland", font=font(10), fill=DARK_GRAY)
    draw.text((rx, y + 35), "Tel: +49 89 123 456 78", font=font(10), fill=DARK_GRAY)
    draw.text((rx, y + 50), "info@schmidt-weber.de", font=font(10), fill=DARK_GRAY)

    # Tax IDs
    y = 95
    draw_hline(draw, y, margin, W - margin, LIGHT_GRAY)
    y += 8
    draw.text((margin, y), "USt-IdNr: DE287654321", font=font(10, True), fill=DARK_GRAY)
    draw.text((margin + 250, y), "Steuernummer: 143/123/45678", font=font(10), fill=MID_GRAY)
    draw.text((margin + 500, y), "HRB 123456 AG München", font=font(10), fill=MID_GRAY)

    # RECHNUNG title
    y = 130
    draw.text((margin, y), "RECHNUNG", font=font(28, True), fill=BLACK)

    # Invoice meta
    y = 170
    draw_rect(draw, W - margin - 230, y, W - margin, y + 60, fill=VERY_LIGHT, outline=LIGHT_GRAY)
    meta = [
        ("Rechnungsnummer:", "RE-2026-0891"),
        ("Rechnungsdatum:", "12.03.2026"),
        ("Leistungsdatum:", "01.03 - 10.03.2026"),
    ]
    for i, (lbl, val) in enumerate(meta):
        draw.text((W - margin - 222, y + 5 + i * 18), lbl, font=font(9, True), fill=DARK_GRAY)
        draw.text((W - margin - 95, y + 5 + i * 18), val, font=font(9), fill=BLACK)

    # Bill To
    draw.text((margin, y), "Rechnungsempfänger:", font=font(9, True), fill=MID_GRAY)
    y2 = y + 18
    draw.text((margin, y2), "Dubois Consulting SARL", font=font(12, True), fill=BLACK)
    draw.text((margin, y2 + 18), "15 Rue de Rivoli", font=font(10), fill=DARK_GRAY)
    draw.text((margin, y2 + 32), "75001 Paris, France", font=font(10), fill=DARK_GRAY)
    draw.text((margin, y2 + 48), "TVA Intracommunautaire: FR12345678901", font=font(10, True), fill=DARK_GRAY)

    # Table
    y = 300
    col_x = [margin, margin + 40, margin + 340, margin + 420, margin + 510, W - margin]
    headers = ["Pos.", "Bezeichnung", "Menge", "Einzelpreis", "Betrag"]
    draw_rect(draw, margin, y, W - margin, y + 26, fill=(40, 40, 40))
    hx = [col_x[0] + 5, col_x[1] + 5, col_x[2] + 5, col_x[3] + 5, col_x[4] + 5]
    for i, h in enumerate(headers):
        draw.text((hx[i], y + 5), h, font=font(10, True), fill=WHITE)

    items = [
        ("1", "Beratungsdienstleistung\n(Consulting Services)", "40 Std.", "€150,00", "€6.000,00"),
        ("2", "Fachbücher\n(Technical Reference Books)", "5 Stk.", "€45,00", "€225,00"),
        ("3", "Softwarelizenz\n(Annual Enterprise License)", "1 Stk.", "€2.400,00", "€2.400,00"),
    ]

    y += 26
    for idx, item in enumerate(items):
        row_h = 40
        row_y = y + idx * row_h
        if idx % 2 == 1:
            draw_rect(draw, margin, row_y, W - margin, row_y + row_h, fill=ROW_ALT)
        draw_rect(draw, margin, row_y, W - margin, row_y + row_h, outline=VERY_LIGHT)
        draw.text((hx[0], row_y + 5), item[0], font=font(10), fill=DARK_GRAY)
        desc_lines = item[1].split("\n")
        draw.text((hx[1], row_y + 4), desc_lines[0], font=font(10), fill=BLACK)
        if len(desc_lines) > 1:
            draw.text((hx[1], row_y + 20), desc_lines[1], font=font(8), fill=MID_GRAY)
        draw.text((hx[2], row_y + 5), item[2], font=font(10), fill=DARK_GRAY)
        draw.text((hx[3], row_y + 5), item[3], font=font(10), fill=DARK_GRAY)
        draw.text((hx[4], row_y + 5), item[4], font=font(10, True), fill=BLACK)

    y = y + len(items) * 40
    draw_hline(draw, y, margin, W - margin, BLACK, 2)

    # Totals
    ty = y + 15
    tx_l = W - margin - 260
    tx_v = W - margin - 90
    rows = [
        ("Nettobetrag:", "€8.625,00", False),
        ("USt. (0% — Reverse Charge):", "€0,00", False),
    ]
    for lbl, val, bold in rows:
        draw.text((tx_l, ty), lbl, font=font(10, bold), fill=DARK_GRAY)
        draw.text((tx_v, ty), val, font=font(10, bold), fill=BLACK)
        ty += 22

    draw_hline(draw, ty + 2, tx_l, W - margin, BLACK, 1)
    ty += 10
    draw_rect(draw, tx_l - 5, ty - 3, W - margin + 5, ty + 24, fill=(40, 40, 40))
    draw.text((tx_l + 5, ty + 2), "Gesamtbetrag:", font=font(13, True), fill=WHITE)
    draw.text((tx_v - 15, ty + 2), "€8.625,00", font=font(13, True), fill=WHITE)

    # Reverse charge notice
    ty += 45
    draw_rect(draw, margin, ty, W - margin, ty + 50, fill=(255, 248, 230), outline=ACCENT_ORANGE)
    draw.text((margin + 12, ty + 6), "Hinweis zur Steuerschuldnerschaft:", font=font(10, True), fill=ACCENT_ORANGE)
    draw.text((margin + 12, ty + 24), "Reverse Charge — Steuerschuldnerschaft des Leistungsempfängers", font=font(10), fill=DARK_GRAY)
    draw.text((margin + 12, ty + 38), "gemäß Art. 196 der Richtlinie 2006/112/EG (MwStSystRL).", font=font(10), fill=DARK_GRAY)

    # Bank details
    ty += 70
    draw.text((margin, ty), "Bankverbindung:", font=font(10, True), fill=BLACK)
    ty += 18
    bank = [
        "Kontoinhaber: Schmidt & Weber GmbH",
        "IBAN: DE89 3704 0044 0532 0130 00",
        "BIC: COBADEFFXXX (Commerzbank München)",
    ]
    for b in bank:
        draw.text((margin, ty), b, font=font(9), fill=DARK_GRAY)
        ty += 15

    # Payment terms
    ty += 15
    draw.text((margin, ty), "Zahlungsbedingungen: 14 Tage netto. Bitte geben Sie die Rechnungsnummer bei der Überweisung an.",
              font=font(9), fill=MID_GRAY)
    ty += 15
    draw.text((margin, ty), "Lieferung/Leistung gemäß Vertrag vom 15.01.2026, Referenz: V-2026-044.",
              font=font(9), fill=MID_GRAY)

    # Footer
    draw_rect(draw, 0, H - 50, W, H, fill=(40, 40, 40))
    draw.text((margin, H - 42), "Schmidt & Weber GmbH  |  Geschäftsführer: Dr. Klaus Schmidt, Maria Weber", font=font(8), fill=LIGHT_GRAY)
    draw.text((margin, H - 26), "Amtsgericht München HRB 123456  |  www.schmidt-weber.de", font=font(8), fill=LIGHT_GRAY)

    img.save(os.path.join(OUTPUT_DIR, "eu_german_invoice.png"))
    print("Created: eu_german_invoice.png")


# ===========================================================================
# Invoice 4: Malaysia Restaurant Receipt
# ===========================================================================
def create_malaysia_receipt():
    W, H = 600, 900
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    margin = 40

    # Receipt style: centered header
    def center_text(y, text, f, color=BLACK):
        bbox = draw.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), text, font=f, fill=color)

    # Top accent
    draw_rect(draw, 0, 0, W, 5, fill=ACCENT_RED)

    y = 20
    center_text(y, "TAN WEE KIAT RESTAURANT SDN BHD", font(16, True), ACCENT_RED)
    center_text(y + 25, "(Co. Reg: 201901012345)", font(9), MID_GRAY)
    center_text(y + 42, "No. 23, Jalan Bukit Bintang", font(10), DARK_GRAY)
    center_text(y + 57, "55100 Kuala Lumpur, Malaysia", font(10), DARK_GRAY)
    center_text(y + 74, "Tel: +60 3-2141 5678", font(10), DARK_GRAY)

    y += 95
    draw_rect(draw, margin, y, W - margin, y + 22, fill=VERY_LIGHT, outline=LIGHT_GRAY)
    center_text(y + 3, "SST Reg No: W10-1234-56789012", font(10, True), DARK_GRAY)

    # Dashed line
    y += 35
    for x in range(margin, W - margin, 8):
        draw.line([(x, y), (x + 4, y)], fill=LIGHT_GRAY, width=1)

    y += 10
    center_text(y, "*** TAX INVOICE / RECEIPT ***", font(12, True), BLACK)

    y += 30
    draw.text((margin, y), "Receipt #:", font=font(10, True), fill=DARK_GRAY)
    draw.text((margin + 85, y), "R-88901", font=font(10), fill=BLACK)
    draw.text((W - margin - 165, y), "Date:", font=font(10, True), fill=DARK_GRAY)
    draw.text((W - margin - 120, y), "14/03/2026", font=font(10), fill=BLACK)
    y += 18
    draw.text((margin, y), "Cashier:", font=font(10, True), fill=DARK_GRAY)
    draw.text((margin + 85, y), "Ahmad", font=font(10), fill=BLACK)
    draw.text((W - margin - 165, y), "Time:", font=font(10, True), fill=DARK_GRAY)
    draw.text((W - margin - 120, y), "13:42:18", font=font(10), fill=BLACK)
    y += 18
    draw.text((margin, y), "Table:", font=font(10, True), fill=DARK_GRAY)
    draw.text((margin + 85, y), "12", font=font(10), fill=BLACK)
    draw.text((W - margin - 165, y), "Pax:", font=font(10, True), fill=DARK_GRAY)
    draw.text((W - margin - 120, y), "3", font=font(10), fill=BLACK)

    # Dashed line
    y += 28
    for x in range(margin, W - margin, 8):
        draw.line([(x, y), (x + 4, y)], fill=LIGHT_GRAY, width=1)

    # Column headers
    y += 10
    draw.text((margin, y), "Item", font=font(10, True), fill=DARK_GRAY)
    draw.text((W - margin - 170, y), "Qty", font=font(10, True), fill=DARK_GRAY)
    draw.text((W - margin - 120, y), "Price", font=font(10, True), fill=DARK_GRAY)
    draw.text((W - margin - 55, y), "Amt", font=font(10, True), fill=DARK_GRAY)
    y += 5
    draw_hline(draw, y + 15, margin, W - margin, LIGHT_GRAY)

    items = [
        ("Nasi Lemak Special", "2", "12.00", "24.00"),
        ("Roti Canai", "3", "3.00", "9.00"),
        ("Teh Tarik", "3", "3.50", "10.50"),
        ("Char Kuey Teow", "1", "12.00", "12.00"),
        ("Air Bandung", "2", "4.00", "8.00"),
    ]

    y += 22
    for idx, item in enumerate(items):
        iy = y + idx * 26
        if idx % 2 == 1:
            draw_rect(draw, margin - 5, iy - 2, W - margin + 5, iy + 20, fill=ROW_ALT)
        draw.text((margin, iy), item[0], font=font(11), fill=BLACK)
        draw.text((W - margin - 165, iy), item[1], font=font(11), fill=DARK_GRAY)
        draw.text((W - margin - 120, iy), item[2], font=font(11), fill=DARK_GRAY)
        draw.text((W - margin - 55, iy), item[3], font=font(11), fill=BLACK)

    y = y + len(items) * 26 + 5
    for x in range(margin, W - margin, 8):
        draw.line([(x, y), (x + 4, y)], fill=LIGHT_GRAY, width=1)

    # Totals
    ty = y + 12
    tx_l = W - margin - 210
    tx_v = W - margin - 65

    draw.text((tx_l, ty), "Subtotal:", font=font(11), fill=DARK_GRAY)
    draw.text((tx_v, ty), "63.50", font=font(11), fill=BLACK)
    ty += 22
    draw.text((tx_l, ty), "Service Tax (8%):", font=font(11), fill=DARK_GRAY)
    draw.text((tx_v, ty), "5.08", font=font(11), fill=BLACK)
    ty += 22
    draw_hline(draw, ty, tx_l, W - margin, BLACK, 1)
    ty += 8

    draw_rect(draw, tx_l - 10, ty - 3, W - margin + 10, ty + 26, fill=ACCENT_RED)
    draw.text((tx_l, ty + 2), "TOTAL (RM):", font=font(13, True), fill=WHITE)
    draw.text((tx_v - 10, ty + 2), "68.58", font=font(13, True), fill=WHITE)

    ty += 40
    for x in range(margin, W - margin, 8):
        draw.line([(x, ty), (x + 4, ty)], fill=LIGHT_GRAY, width=1)

    # Payment info
    ty += 12
    draw.text((margin, ty), "Payment Method:", font=font(10, True), fill=DARK_GRAY)
    draw.text((margin + 125, ty), "CASH", font=font(10, True), fill=BLACK)
    ty += 20
    draw.text((margin, ty), "Cash Tendered:", font=font(10), fill=DARK_GRAY)
    draw.text((margin + 125, ty), "RM 70.00", font=font(10), fill=BLACK)
    ty += 18
    draw.text((margin, ty), "Change:", font=font(10), fill=DARK_GRAY)
    draw.text((margin + 125, ty), "RM 1.42", font=font(10), fill=BLACK)

    ty += 30
    for x in range(margin, W - margin, 8):
        draw.line([(x, ty), (x + 4, ty)], fill=LIGHT_GRAY, width=1)

    # GST summary
    ty += 12
    center_text(ty, "--- SST Summary ---", font(9, True), MID_GRAY)
    ty += 18
    draw.text((margin + 30, ty), "Tax Type", font=font(9, True), fill=DARK_GRAY)
    draw.text((margin + 160, ty), "Taxable Amt", font=font(9, True), fill=DARK_GRAY)
    draw.text((margin + 300, ty), "Tax Amt", font=font(9, True), fill=DARK_GRAY)
    ty += 16
    draw.text((margin + 30, ty), "Service Tax 8%", font=font(9), fill=DARK_GRAY)
    draw.text((margin + 160, ty), "RM 63.50", font=font(9), fill=DARK_GRAY)
    draw.text((margin + 300, ty), "RM 5.08", font=font(9), fill=DARK_GRAY)

    # Footer
    ty += 35
    center_text(ty, "Terima Kasih / Thank You!", font(12, True), ACCENT_RED)
    center_text(ty + 22, "Please come again", font(10), MID_GRAY)
    center_text(ty + 40, "WiFi: TWK-Guest  |  Password: ********", font(9), MID_GRAY)

    # Bottom bar
    draw_rect(draw, 0, H - 28, W, H, fill=ACCENT_RED)
    center_text(H - 22, "Follow us @tanweekhiat  |  www.twkrestaurant.my", font(8), WHITE)

    img.save(os.path.join(OUTPUT_DIR, "malaysia_receipt.png"))
    print("Created: malaysia_receipt.png")


# ===========================================================================
# Invoice 5: Japan Qualified Invoice (インボイス)
# ===========================================================================
def create_japan_qualified_invoice():
    W, H = 800, 1100
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    margin = 50

    # Use Japanese fonts
    fjp = font_jp(10)
    fjp_b = font_jp(10, True)
    fjp_title = font_jp(24, True)
    fjp_lg = font_jp(14, True)
    fjp_md = font_jp(12, True)
    fjp_sm = font_jp(9)
    fjp_sm_b = font_jp(9, True)
    fjp_xs = font_jp(8)

    INDIGO = (50, 50, 120)
    LIGHT_INDIGO = (240, 240, 252)

    # Top bar
    draw_rect(draw, 0, 0, W, 6, fill=INDIGO)

    # Title
    y = 20
    def center_text_jp(y, text, f, color=BLACK):
        bbox = draw.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), text, font=f, fill=color)

    center_text_jp(y, "請　求　書", fjp_title, INDIGO)
    center_text_jp(y + 35, "QUALIFIED INVOICE (適格請求書)", font(10, True), MID_GRAY)

    # Seller info (right side, top)
    y = 75
    rx = W - margin - 280
    draw.text((rx, y), "株式会社サクラテック", font=fjp_lg, fill=BLACK)
    draw.text((rx, y + 22), "Sakura Tech Co., Ltd.", font=font(9), fill=MID_GRAY)
    draw.text((rx, y + 38), "〒150-0001", font=fjp_sm, fill=DARK_GRAY)
    draw.text((rx, y + 52), "東京都渋谷区神宮前1-2-3 テックビル5F", font=fjp_sm, fill=DARK_GRAY)
    draw.text((rx, y + 68), "TEL: 03-1234-5678  FAX: 03-1234-5679", font=font(9), fill=DARK_GRAY)

    # QIIN
    y2 = y + 88
    draw_rect(draw, rx, y2, W - margin, y2 + 22, fill=LIGHT_INDIGO, outline=INDIGO)
    draw.text((rx + 8, y2 + 3), "登録番号 (QIIN): T1234567890123", font=fjp_sm_b, fill=INDIGO)

    # Buyer info (left side)
    y = 85
    draw.text((margin, y), "山田商事株式会社　御中", font=fjp_md, fill=BLACK)
    draw.text((margin, y + 22), "〒100-0005 東京都千代田区丸の内2-3-4", font=fjp_sm, fill=DARK_GRAY)
    draw.text((margin, y + 38), "購買部　山田太郎 様", font=fjp_sm, fill=DARK_GRAY)

    # Decorative underline for buyer
    draw_hline(draw, y + 20, margin, margin + 240, INDIGO, 2)

    # Invoice meta
    y = 190
    draw_hline(draw, y, margin, W - margin, LIGHT_GRAY)
    y += 10
    meta_items = [
        ("請求書番号:", "INV-2026-0456"),
        ("発行日:", "2026年3月8日"),
        ("お支払期限:", "2026年4月7日"),
        ("取引区分:", "課税取引"),
    ]
    for i, (lbl, val) in enumerate(meta_items):
        col = margin if i < 2 else margin + 320
        row = y + (i % 2) * 22
        draw.text((col, row), lbl, font=fjp_sm_b, fill=DARK_GRAY)
        draw.text((col + 95, row), val, font=fjp_sm, fill=BLACK)

    # Table
    y = 260
    col_positions = [margin, margin + 40, margin + 340, margin + 430, margin + 530, W - margin]
    headers = ["No.", "品　目", "数量", "単　価", "金　額", "税率"]
    draw_rect(draw, margin, y, W - margin, y + 28, fill=INDIGO)
    hx = [col_positions[0] + 5, col_positions[1] + 5, col_positions[2] + 5, col_positions[3] + 5, col_positions[4] + 5]
    # Adjust header positions
    header_x = [margin + 8, margin + 60, margin + 345, margin + 430, margin + 530, W - margin - 35]
    for i, h in enumerate(headers):
        draw.text((header_x[i], y + 5), h, font=fjp_sm_b, fill=WHITE)

    items = [
        ("1", "ソフトウェア開発", "1式", "¥500,000", "¥500,000", "10%"),
        ("", "(Software Development)", "", "", "", ""),
        ("2", "サーバー保守", "1ヶ月", "¥80,000", "¥80,000", "10%"),
        ("", "(Server Maintenance)", "", "", "", ""),
        ("3", "お弁当代（会議用）", "10個", "¥1,000", "¥10,000", "8%※"),
        ("", "(Lunch boxes for meeting)", "", "", "", ""),
    ]

    y += 28
    row_i = 0
    for idx, item in enumerate(items):
        is_sub = item[0] == ""
        row_h = 18 if is_sub else 24
        row_y = y
        if not is_sub:
            if row_i % 2 == 1:
                draw_rect(draw, margin, row_y, W - margin, row_y + 42, fill=ROW_ALT)
            draw_rect(draw, margin, row_y, W - margin, row_y + 42, outline=VERY_LIGHT)

        if is_sub:
            draw.text((header_x[1], row_y + 1), item[1], font=font(8), fill=MID_GRAY)
            y += row_h
        else:
            draw.text((header_x[0], row_y + 5), item[0], font=fjp_sm, fill=DARK_GRAY)
            draw.text((header_x[1], row_y + 4), item[1], font=fjp_sm_b if not is_sub else fjp_sm, fill=BLACK)
            draw.text((header_x[2], row_y + 5), item[2], font=fjp_sm, fill=DARK_GRAY)
            draw.text((header_x[3], row_y + 5), item[3], font=fjp_sm, fill=DARK_GRAY)
            draw.text((header_x[4], row_y + 5), item[4], font=fjp_sm_b, fill=BLACK)
            # Tax rate with special coloring for reduced rate
            color = ACCENT_RED if "※" in item[5] else DARK_GRAY
            draw.text((header_x[5], row_y + 5), item[5], font=fjp_sm_b, fill=color)
            y += row_h
            row_i += 1

    y += 8
    draw_hline(draw, y, margin, W - margin, INDIGO, 2)

    # Tax breakdown section
    ty = y + 15
    draw.text((margin, ty), "税率別内訳 (Tax Rate Breakdown)", font=fjp_sm_b, fill=INDIGO)
    ty += 22

    # Tax table
    tax_headers = ["税率", "対象金額", "消費税額"]
    tw = 180
    draw_rect(draw, margin, ty, margin + tw * 3, ty + 22, fill=LIGHT_INDIGO, outline=INDIGO)
    for i, th in enumerate(tax_headers):
        draw.text((margin + i * tw + 10, ty + 3), th, font=fjp_sm_b, fill=INDIGO)
    ty += 22

    tax_rows = [
        ("10%（標準税率）", "¥580,000", "¥58,000"),
        ("8%（軽減税率）※", "¥10,000", "¥800"),
    ]
    for i, row in enumerate(tax_rows):
        draw_rect(draw, margin, ty, margin + tw * 3, ty + 22, outline=LIGHT_GRAY)
        if i == 1:
            draw_rect(draw, margin, ty, margin + tw * 3, ty + 22, fill=(255, 248, 248))
        for j, val in enumerate(row):
            color = ACCENT_RED if "※" in val else BLACK
            draw.text((margin + j * tw + 10, ty + 3), val, font=fjp_sm, fill=color)
        ty += 22

    # Totals
    ty += 15
    tx_l = W - margin - 280
    tx_v = W - margin - 100

    total_rows = [
        ("小計 (税抜):", "¥590,000"),
        ("消費税合計:", "¥58,800"),
    ]
    for lbl, val in total_rows:
        draw.text((tx_l, ty), lbl, font=fjp_sm, fill=DARK_GRAY)
        draw.text((tx_v, ty), val, font=fjp_sm, fill=BLACK)
        ty += 22

    draw_hline(draw, ty, tx_l, W - margin, INDIGO, 1)
    ty += 8
    draw_rect(draw, tx_l - 5, ty - 3, W - margin + 5, ty + 28, fill=INDIGO)
    draw.text((tx_l + 10, ty + 3), "合計金額:", font=fjp_md, fill=WHITE)
    draw.text((tx_v - 20, ty + 3), "¥648,800", font=font_jp(14, True), fill=WHITE)

    # Reduced rate note
    ty += 45
    draw_rect(draw, margin, ty, W - margin, ty + 25, fill=(255, 248, 248), outline=ACCENT_RED)
    draw.text((margin + 10, ty + 5), "※軽減税率対象品目　(※ Items subject to reduced tax rate of 8%)", font=fjp_sm, fill=ACCENT_RED)

    # Bank details
    ty += 40
    draw.text((margin, ty), "お振込先:", font=fjp_sm_b, fill=INDIGO)
    ty += 18
    bank_info = [
        "三菱UFJ銀行　渋谷支店",
        "普通預金　口座番号: 1234567",
        "口座名義: カ）サクラテック",
    ]
    for b in bank_info:
        draw.text((margin + 15, ty), b, font=fjp_sm, fill=DARK_GRAY)
        ty += 16

    # Notes
    ty += 15
    draw.text((margin, ty), "備考:", font=fjp_sm_b, fill=DARK_GRAY)
    ty += 16
    notes = [
        "・本請求書は適格請求書等保存方式（インボイス制度）に基づき発行しています。",
        "・お支払期限までにお振込みをお願いいたします。",
        "・振込手数料は貴社にてご負担ください。",
    ]
    for n in notes:
        draw.text((margin, ty), n, font=fjp_xs, fill=MID_GRAY)
        ty += 14

    # Company seal area (right side)
    seal_x = W - margin - 100
    seal_y = ty - 50
    draw_rect(draw, seal_x, seal_y, seal_x + 70, seal_y + 70, outline=ACCENT_RED, width=2)
    # Draw circle for seal
    draw.ellipse([(seal_x + 5, seal_y + 5), (seal_x + 65, seal_y + 65)], outline=ACCENT_RED, width=2)
    draw.text((seal_x + 14, seal_y + 18), "サクラ", font=font_jp(11, True), fill=ACCENT_RED)
    draw.text((seal_x + 14, seal_y + 36), "テック", font=font_jp(11, True), fill=ACCENT_RED)

    # Footer
    draw_rect(draw, 0, H - 35, W, H, fill=INDIGO)
    draw.text((margin, H - 28), "この請求書は電子的に発行されたものであり、押印は省略しております。", font=fjp_xs, fill=(180, 180, 220))

    img.save(os.path.join(OUTPUT_DIR, "japan_qualified_invoice.png"))
    print("Created: japan_qualified_invoice.png")


# ===========================================================================
# Main
# ===========================================================================
if __name__ == "__main__":
    print(f"Output directory: {OUTPUT_DIR}")
    create_us_construction_invoice()
    create_india_gst_invoice()
    create_eu_german_invoice()
    create_malaysia_receipt()
    create_japan_qualified_invoice()
    print("\nAll 5 demo invoices generated successfully!")
