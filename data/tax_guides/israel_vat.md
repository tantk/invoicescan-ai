# Israel — VAT (Ma'am / מע"מ) Guide

## Overview
Israel's Value Added Tax, known locally as Ma'am (מס ערך מוסף), is administered by the Israel Tax Authority (רשות המסים / Reshut HaMisim). The VAT system applies to most goods and services supplied within Israel and to imports. Israel operates a Continuous Transaction Controls (CTC) clearance model for invoice validation via the SHAAM platform, making it one of the most advanced real-time invoice verification systems globally.

## Tax Rates
- **Standard rate: 18%** (increased from 17% to 18% effective January 1, 2025; a proposed increase to 19% for 2026 was rejected)
- **Zero-rated (0%)**: Exports of goods, certain services provided to non-residents, fruits and vegetables (since January 2015), tourism services to incoming tourists
- **Exempt** (no VAT, no input credit): Financial services, residential rent below threshold, insurance premiums, sale of a going concern, certain educational services, public transport

## Tax ID Format
- **Osek Morsheh (עוסק מורשה)**: 9-digit business number (Mispar Osek / מספר עוסק)
  - Format: `XXXXXXXXX` (9 digits, last 2 are check digits)
  - Companies use their company registration number (Mispar Hevra / מספר חברה)
  - Example: `514713370`
- **Osek Patur (עוסק פטור)**: Exempt dealer — same 9-digit format but not authorized to charge VAT
  - Threshold: Annual turnover below ~120,000 NIS (updated periodically by the Tax Authority)
- Verify at: https://www.misim.gov.il (Israel Tax Authority portal)

## Invoice Requirements
### Tax Invoice (Heshbonit Mas / חשבונית מס)
1. The words "Tax Invoice" (חשבונית מס) prominently displayed
2. Supplier name, address, and Osek number (מספר עוסק)
3. Customer name and address
4. Customer's Osek number (for B2B transactions)
5. Sequential invoice number
6. Date of issue
7. Description of goods or services
8. Quantity and unit price
9. Total amount before VAT
10. VAT rate and VAT amount
11. Total amount including VAT
12. **Allocation number (מספר הקצאה)** from the SHAAM system — mandatory for invoices above threshold (see E-Invoicing section)

### Invoice/Receipt (Heshbonit Kabala)
- Combined invoice and receipt document commonly used for immediate payment transactions

## E-Invoicing
### SHAAM Platform — CTC Clearance Model
Israel implements a Continuous Transaction Controls (CTC) clearance model. Before an invoice is valid for input tax deduction, the supplier must obtain an **allocation number** from the Tax Authority's SHAAM platform.

### How It Works
1. Supplier sends invoice data to the Tax Authority via API or web portal in **JSON format**
2. The Tax Authority validates the data in real-time
3. Upon approval, an **allocation number (מספר הקצאה)** is assigned
4. The allocation number must appear on the invoice
5. Buyers can only deduct input VAT from invoices bearing a valid allocation number

### 2026 Mandatory Thresholds (Accelerated Timeline)
- **January 1, 2024**: Invoices above 25,000 NIS required allocation numbers
- **January 1, 2025**: Threshold dropped to 20,000 NIS
- **January 1, 2026**: Threshold drops to 10,000 NIS
- **June 1, 2026**: Threshold drops to 5,000 NIS
- Future phases expected to lower the threshold further toward full coverage

## Key Rules
- **Osek Morsheh vs. Osek Patur**: Businesses above the annual turnover threshold (~120,000 NIS) must register as Osek Morsheh and charge VAT. Below the threshold, businesses may register as Osek Patur and are exempt from charging VAT but cannot claim input VAT credits.
- **Filing frequency**: Monthly for most businesses; bi-monthly for small businesses
- **Input VAT deduction**: Allowed only with a valid tax invoice containing the supplier's Osek number and (where required) a SHAAM allocation number
- **Import VAT**: Charged at the standard rate on CIF value plus customs duties
- **Tourism and exports**: Zero-rated — tourists can reclaim VAT on purchases above 400 NIS at participating stores via the VAT refund scheme at Ben Gurion Airport
- **Nonprofit organizations (Amutot / מלכ"ר)**: Pay a wage-based levy instead of standard VAT
- **Reverse charge**: Applies to services received from non-residents

## Common Pitfalls
1. **Missing allocation number**: Invoices above the threshold without a SHAAM allocation number — buyer cannot deduct input VAT
2. **Osek Patur issuing tax invoices**: Exempt dealers (Osek Patur) are prohibited from issuing tax invoices or charging VAT
3. **Incorrect classification**: Confusing exempt vs. zero-rated supplies — zero-rated allows input credit, exempt does not
4. **Late VAT filing**: Penalties and interest accrue rapidly; monthly filing deadlines are the 15th of the following month
5. **Not accounting for the 2026 threshold changes**: The SHAAM allocation threshold drops twice in 2026 (January and June), catching businesses unprepared
6. **Mixed-use input VAT**: Failing to apportion input VAT between taxable and exempt activities
7. **Foreign supplier payments**: Forgetting to apply reverse charge and self-assess VAT on services from abroad
8. **Currency and rounding**: VAT on foreign-currency transactions must be calculated using the representative exchange rate on the date of supply
