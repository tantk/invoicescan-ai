# Demo Video Script — 4 Minutes

## Equipment Needed
- Phone (for camera scan demo)
- Desktop browser (for upload demo)
- 5 demo invoices (in data/demo_invoices/)

---

## SCENE 1: THE PROBLEM (0:00 - 0:30)

**[Screen: montage of different invoices — US, Indian, German, Japanese, Malaysian]**

**Voiceover:**
"Every business in the world processes invoices. But invoices from India have compound GST taxes. German invoices have split VAT rates. A Singapore invoice from 2023 has a different tax rate than one from 2024.

Today, you either hire an accountant who knows every country's rules... or you guess and hope.

What if you could just scan an invoice with your phone — and talk to an AI that actually knows?"

---

## SCENE 2: SCAN & TALK — US Invoice (0:30 - 1:15)

**[Screen: Phone camera pointed at US construction invoice]**

**Action:** Open InvoiceScan AI on phone. Tap "Scan." Camera captures the invoice.

**[Screen: Document AI extracts fields instantly — vendor, total, tax appear in the UI]**

**Voiceover:**
"One tap. Document AI extracts everything — vendor, line items, tax, total — with confidence scores."

**[Screen: Agent starts speaking]**

**Agent voice:**
"This is a US invoice from Pacific Pipeline Solutions in San Jose, California. Total is two thousand three hundred twenty-nine dollars and seventy-one cents. I see California sales tax at eight point two five percent applied to materials only — labor is exempt. That's correct for California. Three line items and a permit fee."

**[User speaks into phone]**
"Is the retainage correct?"

**Agent voice:**
"The retainage is ten percent — two hundred forty-nine dollars and eighty cents. That's standard for construction projects."

---

## SCENE 3: MULTI-COUNTRY — Indian GST Invoice (1:15 - 2:00)

**[Screen: Upload Indian GST invoice on desktop]**

**Voiceover:**
"Now watch what happens with an invoice from a completely different country."

**[Screen: Fields appear — GSTIN numbers, HSN code, IGST breakdown]**

**Agent voice:**
"Switching to India GST. This is an interstate invoice from TechVista Solutions in Bangalore to Global Corp in Mumbai. Since it crosses state lines — Karnataka to Maharashtra — IGST applies at eighteen percent. I see one lakh sixty thousand two hundred rupees in IGST on a subtotal of eight lakh ninety thousand. The math checks out."

**[User speaks]**
"Check compliance."

**Agent voice:**
"Compliance check for India GST: Supplier GSTIN present — passed. Buyer GSTIN present — passed. HSN code 998314 for IT consulting — passed. Place of supply Maharashtra — passed. All seven mandatory fields present. This invoice is compliant."

---

## SCENE 4: THE AGENT LEARNS (2:00 - 2:30)

**[Screen: Back to the US construction invoice]**

**[User speaks]**
"You missed the project code on that construction invoice."

**Agent voice:**
"Let me look... Found it: Project Code PRJ-BAYVIEW-2026. Got it — I'll look for project codes on all construction invoices from now on. That's sample one of fifty toward Document AI uptraining. Once I have fifty confirmed extractions, this field will graduate to grounded accuracy."

**[Screen: Show the learned fields list updating]**

**Voiceover:**
"The agent learns what YOU care about. No training data needed. No annotation workbench. It just gets smarter with every scan."

---

## SCENE 5: ARCHITECTURE (2:30 - 3:15)

**[Screen: Architecture diagram]**

**Voiceover:**
"Here's how it works. Two layers of extraction."

**[Highlight Layer 1]**
"Layer one: Google Document AI extracts forty-six standard fields with confidence scores. This is the grounding — the source of truth."

**[Highlight Layer 2]**
"Layer two: Gemini Vision extracts any custom field on demand — a hundred forty fields across nine industry presets. Construction retainage, healthcare CPT codes, legal billable hours."

**[Highlight Self-Improving Loop]**
"The self-improving loop: every extraction is an implicit training label. After fifty confirmed samples, the field graduates from Gemini to Document AI. The agent literally uptrains its own model."

**[Highlight Tax Engine]**
"Fifty-seven countries with historical rate awareness. A twenty-nineteen Saudi invoice at five percent? Correct — the rate was five percent before July twenty-twenty."

**[Highlight Google Cloud services]**
"Built on seven Google Cloud services: Gemini Live API, Document AI, Vertex AI Search, Memory Bank, Agent Engine, Cloud Run, and Google Sheets."

---

## SCENE 6: GOOGLE SHEETS + CLOSE (3:15 - 4:00)

**[Screen: Google Sheets with logged invoices]**

**Voiceover:**
"Every scanned invoice is auto-logged to Google Sheets. Three dynamic sheets — Invoices, Line Items, Tax Breakdown. Columns create themselves as new field types appear. An Indian invoice adds CGST and SGST columns. A construction invoice adds retainage. No schema changes needed."

**[Screen: Show multiple invoices from different countries in the sheet]**

**[Screen: Final slide / logo]**

**Voiceover:**
"InvoiceScan AI. Fifty-seven countries. Sixteen tools. Gets smarter with every scan. Open source — zero cost — versus five hundred dollars a month for the alternatives.

Scan. Talk. Trust."

---

## Demo Data Needed

| # | Invoice | Country | Key Demo Points |
|---|---------|---------|----------------|
| 1 | US Construction | US | Sales tax on materials only, retainage, project code (learning demo) |
| 2 | Indian GST | India | IGST interstate, CGST/SGST, HSN code, compliance check |
| 3 | German reverse charge | Germany | Split 19%/7% rates, reverse charge for EU buyer |
| 4 | Malaysian receipt | Malaysia | SST service tax, restaurant format |
| 5 | Japanese qualified | Japan | Split 8%/10% rates, QIIN number, reduced rate items |

## Tips for Recording
- Use a real phone for the camera scan (not a simulator)
- Have invoices printed or on a second screen
- Test the voice conversation flow beforehand — the agent should respond naturally
- Record screen + voice simultaneously (OBS recommended)
- Have Google Sheets open in a split view to show real-time logging
- Architecture diagram as a clean image (export from the markdown)
