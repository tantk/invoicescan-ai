"""Generate 5 additional demo invoices for testing."""

from PIL import Image, ImageDraw, ImageFont
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    font_lg = ImageFont.truetype("arial.ttf", 18)
    font_md = ImageFont.truetype("arial.ttf", 14)
    font_sm = ImageFont.truetype("arial.ttf", 11)
    font_xl = ImageFont.truetype("arial.ttf", 24)
    font_title = ImageFont.truetype("arial.ttf", 28)
except:
    font_lg = font_md = font_sm = font_xl = font_title = ImageFont.load_default()

BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BLUE = (0, 51, 153)
RED = (200, 0, 0)
GREEN = (0, 100, 0)
ORANGE = (200, 80, 0)
WHITE = (255, 255, 255)


def hline(draw, y, x1=50, x2=750):
    draw.line([(x1, y), (x2, y)], fill=(180, 180, 180), width=1)


# 1. Singapore GST Invoice
img = Image.new("RGB", (800, 1000), WHITE)
d = ImageDraw.Draw(img)
d.text((50, 30), "TAX INVOICE", fill=BLUE, font=font_title)
d.text((500, 30), "CloudSoft Pte Ltd", fill=BLACK, font=font_lg)
d.text((500, 55), "10 Anson Road #12-05", fill=GRAY, font=font_sm)
d.text((500, 70), "Singapore 079903", fill=GRAY, font=font_sm)
d.text((500, 85), "GST Reg: M90012345X", fill=BLUE, font=font_md)

hline(d, 115)
d.text((50, 125), "Bill To: Tan Wei Ming", fill=BLACK, font=font_md)
d.text((50, 145), "88 Market Street #15-01, Singapore 048948", fill=GRAY, font=font_sm)
d.text((450, 125), "Invoice: CS-2026-0891", fill=BLACK, font=font_md)
d.text((450, 145), "Date: 12 March 2026", fill=BLACK, font=font_sm)
d.text((450, 160), "Due: 11 April 2026 | Net 30", fill=BLACK, font=font_sm)
hline(d, 180)

y = 195
d.rectangle([(50, y), (750, y + 25)], fill=(230, 235, 245))
for text, x in [("Description", 55), ("Qty", 380), ("Rate (SGD)", 430), ("Amount", 620)]:
    d.text((x, y + 5), text, fill=BLUE, font=font_md)

items = [
    ("Cloud Hosting - AWS ap-southeast-1", "1 mo", "2,400.00", "2,400.00"),
    ("Software Development (React/Node)", "160 hrs", "95.00", "15,200.00"),
    ("UI/UX Design Services", "40 hrs", "120.00", "4,800.00"),
    ("SSL Certificate (2 year)", "3", "89.00", "267.00"),
    ("Domain Registration (.com.sg)", "2", "55.00", "110.00"),
]
y = 225
for desc, qty, rate, amt in items:
    d.text((55, y), desc, fill=BLACK, font=font_sm)
    d.text((380, y), qty, fill=BLACK, font=font_sm)
    d.text((440, y), rate, fill=BLACK, font=font_sm)
    d.text((620, y), amt, fill=BLACK, font=font_sm)
    y += 25

y += 10
hline(d, y)
y += 10
for label, val in [("Subtotal:", "22,777.00"), ("GST (9%):", "2,049.93")]:
    d.text((470, y), label, fill=GRAY, font=font_md)
    d.text((620, y), val, fill=BLACK, font=font_md)
    y += 22
hline(d, y)
y += 8
d.text((470, y), "Total Due:", fill=BLUE, font=font_lg)
d.text((600, y), "S$24,826.93", fill=BLUE, font=font_lg)

y += 45
d.text((50, y), "Bank: DBS Bank | Acc: 072-901234-5 | SWIFT: DBSSSGSG | PayNow: 201901234M", fill=GRAY, font=font_sm)
img.save("singapore_gst_invoice.png")
print("Created: singapore_gst_invoice.png")


# 2. UK Construction CIS Reverse Charge
img = Image.new("RGB", (800, 1000), WHITE)
d = ImageDraw.Draw(img)
d.text((50, 30), "INVOICE", fill=BLACK, font=font_title)
d.text((50, 65), "BuildRight Construction Ltd", fill=BLUE, font=font_lg)
d.text((50, 88), "42 Victoria Street, Manchester M1 2EQ", fill=GRAY, font=font_sm)
d.text((50, 103), "VAT: GB287654321 | CIS UTR: 12345 67890", fill=GRAY, font=font_sm)

d.text((450, 65), "Invoice: BR-2026-0156", fill=BLACK, font=font_md)
d.text((450, 85), "Date: 08/03/2026", fill=BLACK, font=font_sm)
d.text((450, 100), "Due: 07/04/2026", fill=BLACK, font=font_sm)
hline(d, 120)

d.text((50, 130), "To: Premier Properties Group", fill=BLACK, font=font_md)
d.text((50, 148), "100 Deansgate, Manchester M3 2GP | VAT: GB198765432", fill=GRAY, font=font_sm)
d.text((50, 168), "Project: Manchester City Tower - Phase 2 | Ref: MCT-2025-089", fill=BLUE, font=font_sm)
hline(d, 185)

y = 195
d.rectangle([(50, y), (750, y + 25)], fill=(230, 235, 245))
d.text((55, y + 5), "Description", fill=BLUE, font=font_md)
d.text((550, y + 5), "Amount (GBP)", fill=BLUE, font=font_md)

items = [
    ("Structural steelwork - Level 14-16", "45,000.00"),
    ("Concrete formwork and pouring", "32,500.00"),
    ("Crane hire (2 weeks)", "8,200.00"),
    ("Scaffolding erection and dismantling", "6,800.00"),
    ("Site supervision (March)", "4,500.00"),
]
y = 225
for desc, amt in items:
    d.text((55, y), desc, fill=BLACK, font=font_sm)
    d.text((560, y), amt, fill=BLACK, font=font_sm)
    y += 25

y += 10
d.text((420, y), "Subtotal:", fill=GRAY, font=font_md)
d.text((560, y), "97,000.00", fill=BLACK, font=font_md)
y += 22
d.text((420, y), "CIS Deduction (20%):", fill=RED, font=font_md)
d.text((560, y), "-19,400.00", fill=RED, font=font_md)
y += 22
d.text((420, y), "VAT (20%):", fill=GRAY, font=font_md)
d.text((560, y), "0.00", fill=BLACK, font=font_md)
y += 25
hline(d, y)
y += 8
d.text((420, y), "Amount Due:", fill=BLUE, font=font_lg)
d.text((560, y), "77,600.00", fill=BLUE, font=font_lg)

y += 45
d.rectangle([(50, y), (750, y + 45)], fill=(255, 240, 240))
d.text((60, y + 5), "REVERSE CHARGE - CIS DOMESTIC REVERSE CHARGE APPLIES", fill=RED, font=font_md)
d.text((60, y + 25), "Customer to account for VAT to HMRC under S55A VATA 1994", fill=RED, font=font_sm)

y += 55
d.text((50, y), "Retainage: 5% (GBP 4,850.00) held until practical completion", fill=GRAY, font=font_sm)
img.save("uk_construction_cis_invoice.png")
print("Created: uk_construction_cis_invoice.png")


# 3. Australian GST Invoice
img = Image.new("RGB", (800, 1000), WHITE)
d = ImageDraw.Draw(img)
d.text((50, 30), "TAX INVOICE", fill=GREEN, font=font_title)
d.text((500, 30), "Outback Digital", fill=BLACK, font=font_lg)
d.text((500, 52), "ABN: 51 824 753 691", fill=GREEN, font=font_md)
d.text((500, 72), "123 George St, Sydney NSW 2000", fill=GRAY, font=font_sm)
d.text((500, 87), "hello@outbackdigital.com.au", fill=GRAY, font=font_sm)

hline(d, 110)
d.text((50, 120), "To: Fresh Harvest Organic Farms Pty Ltd", fill=BLACK, font=font_md)
d.text((50, 140), "ABN: 23 456 789 012 | 456 Rural Rd, Dubbo NSW 2830", fill=GRAY, font=font_sm)
d.text((450, 120), "Invoice: OD-2026-0234", fill=BLACK, font=font_md)
d.text((450, 140), "Date: 14/03/2026 | Due: 13/04/2026", fill=BLACK, font=font_sm)
hline(d, 160)

y = 175
d.rectangle([(50, y), (750, y + 25)], fill=(230, 245, 230))
for text, x in [("Description", 55), ("Hrs", 370), ("Rate", 420), ("GST", 520), ("Total", 640)]:
    d.text((x, y + 5), text, fill=GREEN, font=font_md)

items = [
    ("Website Redesign (WordPress)", "45", "A$150", "A$675", "A$7,425"),
    ("E-commerce Setup (WooCommerce)", "30", "A$150", "A$450", "A$4,950"),
    ("Logo Design & Branding", "12", "A$180", "A$216", "A$2,376"),
    ("SEO Audit & Optimization", "8", "A$160", "A$128", "A$1,408"),
    ("Photography (product shots)", "1 day", "A$800", "A$80", "A$880"),
    ("Google Ads Setup", "6", "A$140", "A$84", "A$924"),
]
y = 205
for desc, hrs, rate, gst, total in items:
    d.text((55, y), desc, fill=BLACK, font=font_sm)
    d.text((370, y), hrs, fill=BLACK, font=font_sm)
    d.text((420, y), rate, fill=BLACK, font=font_sm)
    d.text((520, y), gst, fill=BLACK, font=font_sm)
    d.text((640, y), total, fill=BLACK, font=font_sm)
    y += 22

y += 10
hline(d, y)
y += 8
for label, val in [("Subtotal:", "A$16,330.00"), ("GST (10%):", "A$1,633.00")]:
    d.text((470, y), label, fill=GRAY, font=font_md)
    d.text((620, y), val, fill=BLACK, font=font_md)
    y += 22
hline(d, y)
y += 8
d.text((470, y), "Total (inc GST):", fill=GREEN, font=font_lg)
d.text((610, y), "A$17,963", fill=GREEN, font=font_lg)

y += 40
d.text((50, y), "Bank: Commonwealth Bank | BSB: 062-000 | Acc: 1234 5678", fill=GRAY, font=font_sm)
d.text((50, y + 18), "Total price includes GST", fill=GRAY, font=font_sm)
img.save("australia_gst_invoice.png")
print("Created: australia_gst_invoice.png")


# 4. Indian Intrastate GST (CGST + SGST)
img = Image.new("RGB", (800, 1050), WHITE)
d = ImageDraw.Draw(img)
d.text((50, 25), "TAX INVOICE", fill=ORANGE, font=font_title)
d.text((50, 60), "Mumbai Office Supplies Pvt Ltd", fill=BLACK, font=font_lg)
d.text((50, 83), "Shop 12, Crawford Market, Mumbai 400001", fill=GRAY, font=font_sm)
d.text((50, 98), "GSTIN: 27AABCM1234F1ZQ | State: Maharashtra (27)", fill=ORANGE, font=font_sm)

d.text((450, 60), "Invoice: MOS/2026/0456", fill=BLACK, font=font_md)
d.text((450, 80), "Date: 15-03-2026", fill=BLACK, font=font_sm)
d.text((450, 95), "Place of Supply: Maharashtra (27)", fill=BLACK, font=font_sm)
hline(d, 118)

d.text((50, 125), "Bill To: Reliance Digital Hub", fill=BLACK, font=font_md)
d.text((50, 143), "Bandra West, Mumbai 400050 | GSTIN: 27AADCR5678H1Z9", fill=GRAY, font=font_sm)
hline(d, 165)

y = 175
d.rectangle([(50, y), (750, y + 22)], fill=(255, 240, 230))
for text, x in [("Item", 55), ("HSN", 260), ("Qty", 310), ("Rate", 350), ("Amt", 420), ("CGST 9%", 500), ("SGST 9%", 590), ("Total", 690)]:
    d.text((x, y + 3), text, fill=ORANGE, font=font_sm)

items = [
    ("HP LaserJet Pro M404dn", "8443", "2", "18,500", "37,000", "3,330", "3,330", "43,660"),
    ("A4 Paper 500sh x10", "4802", "10", "320", "3,200", "288", "288", "3,776"),
    ("Canon Ink Cartridge", "3215", "8", "890", "7,120", "640.80", "640.80", "8,402"),
    ("Logitech Wireless KB", "8471", "5", "1,450", "7,250", "652.50", "652.50", "8,555"),
    ("Ergonomic Office Chair", "9401", "3", "8,900", "26,700", "2,403", "2,403", "31,506"),
]
y = 200
for vals in items:
    positions = [55, 260, 315, 355, 420, 510, 600, 690]
    for val, x in zip(vals, positions):
        d.text((x, y), val, fill=BLACK, font=font_sm)
    y += 22

y += 10
hline(d, y)
y += 8
for label, val in [("Taxable Value:", "Rs.81,270"), ("CGST (9%):", "Rs.7,314.30"), ("SGST (9%):", "Rs.7,314.30")]:
    d.text((420, y), label, fill=GRAY, font=font_md)
    d.text((590, y), val, fill=BLACK, font=font_md)
    y += 22
hline(d, y)
y += 8
d.text((420, y), "Grand Total:", fill=ORANGE, font=font_lg)
d.text((580, y), "Rs.95,898.60", fill=ORANGE, font=font_lg)
y += 28
d.text((420, y), "In Words: Rupees Ninety Five Thousand", fill=GRAY, font=font_sm)
d.text((420, y + 14), "Eight Hundred Ninety Eight and Sixty Paise", fill=GRAY, font=font_sm)

y += 40
d.text((50, y), "Bank: HDFC | A/c: 50200087654321 | IFSC: HDFC0001234", fill=GRAY, font=font_sm)
img.save("india_cgst_sgst_invoice.png")
print("Created: india_cgst_sgst_invoice.png")


# 5. US Restaurant Receipt (multi-tax + tip)
img = Image.new("RGB", (500, 850), WHITE)
d = ImageDraw.Draw(img)
d.text((130, 20), "THE RUSTIC TABLE", fill=BLACK, font=font_lg)
d.text((130, 45), "Farm-to-Table Cuisine", fill=GRAY, font=font_md)
d.text((100, 65), "789 Main Street, Austin, TX 78701", fill=GRAY, font=font_sm)
d.text((160, 80), "Tel: (512) 555-0198", fill=GRAY, font=font_sm)
hline(d, 100, 30, 470)

d.text((30, 108), "Server: Maria | Table: 14", fill=BLACK, font=font_sm)
d.text((30, 123), "Date: 03/15/2026 7:42 PM | Check #88234 | Guests: 4", fill=BLACK, font=font_sm)
hline(d, 140, 30, 470)

items = [
    ("Wagyu Beef Burger x2", "38.00"),
    ("Grilled Salmon", "28.00"),
    ("Caesar Salad (large)", "16.00"),
    ("Truffle Mac & Cheese", "22.00"),
    ("Sweet Potato Fries x2", "14.00"),
    ("Craft Beer (IPA) x3", "27.00"),
    ("Glass of Cabernet x2", "24.00"),
    ("Sparkling Water x2", "8.00"),
    ("Chocolate Lava Cake", "14.00"),
    ("Creme Brulee", "12.00"),
]
y = 150
for item, price in items:
    d.text((30, y), item, fill=BLACK, font=font_sm)
    d.text((380, y), "$" + price, fill=BLACK, font=font_sm)
    y += 18

hline(d, y + 5, 30, 470)
y += 12
d.text((30, y), "Subtotal:", fill=BLACK, font=font_md)
d.text((370, y), "$203.00", fill=BLACK, font=font_md)
y += 20
d.text((30, y), "TX State Tax (6.25%):", fill=GRAY, font=font_sm)
d.text((370, y), "$12.69", fill=BLACK, font=font_sm)
y += 18
d.text((30, y), "Austin City Tax (2.00%):", fill=GRAY, font=font_sm)
d.text((370, y), "$4.06", fill=BLACK, font=font_sm)
y += 22
hline(d, y, 30, 470)
y += 5
d.text((30, y), "Total:", fill=BLACK, font=font_lg)
d.text((350, y), "$219.75", fill=BLACK, font=font_lg)

y += 35
hline(d, y, 30, 470)
y += 8
d.text((30, y), "Suggested Gratuity:", fill=GRAY, font=font_md)
y += 22
d.text((30, y), "18% = $36.54", fill=BLACK, font=font_sm)
d.text((170, y), "20% = $40.60", fill=BLACK, font=font_sm)
d.text((310, y), "25% = $50.75", fill=BLACK, font=font_sm)
y += 28
d.text((30, y), "Tip: _______________", fill=BLACK, font=font_md)
y += 25
d.text((30, y), "Total: _______________", fill=BLACK, font=font_md)
y += 25
d.text((30, y), "Signature: _______________", fill=BLACK, font=font_md)
y += 35
d.text((110, y), "Thank you for dining with us!", fill=GRAY, font=font_md)

img.save("us_restaurant_receipt.png")
print("Created: us_restaurant_receipt.png")

print("\nAll 5 invoices created!")
