# Finland — ALV (Arvonlisavero) Guide

## Overview
Finland's VAT, known as ALV (Arvonlisavero), is administered by Vero (Verohallinto / Finnish Tax Administration). Finland has the highest standard VAT rate in the EU at 25.5%, following an increase from 24% effective September 1, 2024. The system follows EU VAT Directives with Finnish-specific implementations.

## Tax Rates
- **Standard rate: 25.5%** (increased from 24% on September 1, 2024 — the highest standard VAT rate in the EU)
- **Reduced rate: 14%** → **13.5%** (changed effective January 1, 2026) — foodstuffs and non-alcoholic beverages (not restaurant services), animal feed, restaurant and catering services (food component, not alcohol)
- **Reduced rate: 10%** — books (print and e-books), newspapers and magazines (print and electronic), domestic passenger transport, admission to cultural and entertainment events (concerts, theaters, museums, zoos, sporting events), hotel and accommodation, pharmaceutical products (non-prescription), copyrights for literary/artistic works
- **Zero-rated (0%)**: Exports of goods, intra-EU supplies of goods (with valid buyer VAT ID), international transport, vessels and aircraft for international trade
- **Exempt (no VAT, no input credit)**: Financial and insurance services, healthcare, education, residential property rental, social services, postal services (universal), certain cultural services by public institutions, lottery and gambling

### 2026 Rate Changes
- **Reduced rate adjustment**: From January 1, 2026, the 14% reduced rate decreased to **13.5%**, applying to foodstuffs, animal feed, and restaurant/catering services (food component)
- The standard rate remains **25.5%** (unchanged since September 2024)
- The 10% reduced rate remains **10%** (unchanged)

## Tax ID Format
- **Y-tunnus** (Business ID / FO-nummer in Swedish): 7 digits + check digit, format `XXXXXXX-X`
  - Example: `1234567-8`
- **ALV-numero** (VAT number / Momsnummer): Format `FI` + 8 digits (Y-tunnus without hyphen)
  - Example: `FI12345678`
- Verify at: https://ec.europa.eu/taxation_customs/vies/ (EU VIES) or https://www.ytj.fi

## Invoice Requirements
### Full VAT Invoice (arvonlisaverolasku)
1. Invoice date (laskun paivays)
2. Unique sequential invoice number (laskunumero)
3. Seller's full name and address
4. Seller's Y-tunnus (business ID)
5. Seller's ALV-numero (VAT number, FI + 8 digits)
6. Buyer's full name and address
7. Buyer's VAT number (for B2B and intra-EU transactions)
8. Date of supply (toimituspaiva) if different from invoice date
9. Description of goods or services
10. Quantity and unit price (exclusive of ALV)
11. Net amount per ALV rate
12. ALV rate(s) applied (25.5%, 13.5%, 10%)
13. ALV amount per rate
14. Total amount inclusive of ALV
15. For exempt supplies: reference to the applicable Finnish VAT Act section or EU VAT Directive provision
16. For reverse charge: "Kaannetty verovelvollisuus" notation
17. For intra-EU: both parties' VAT IDs and reference to the exemption
18. Payment terms and bank details (IBAN)

### Simplified Invoice (yksinkertaistettu lasku, for supplies up to EUR 400)
1. Seller's name and Y-tunnus
2. Invoice date
3. Description of goods or services
4. Total amount inclusive of ALV
5. ALV amount or rate

## E-Invoicing
- **B2G**: Mandatory — public sector entities require structured electronic invoices
- **B2B**: Not yet mandatory — widely used; Finland has high adoption of e-invoicing through Finvoice (domestic standard) and Peppol networks
- **Finvoice**: Finnish national e-invoice standard, widely used between banks and businesses
- **Peppol**: Increasingly used for both domestic and cross-border transactions
- **ViDA implementation**: Finland will implement EU ViDA (VAT in the Digital Age) requirements, with mandatory intra-EU B2B e-invoicing expected by July 1, 2030
- **Archiving**: Invoices must be stored for **10 years** (per Finnish Accounting Act)

## Key Rules
- **Registration threshold**: EUR 20,000 annual taxable turnover for domestic businesses (increased from EUR 15,000 effective January 1, 2025). Non-resident businesses must register from the first taxable supply in Finland (no threshold).
- **Filing frequency**: Monthly, quarterly, or annually — assigned by Vero based on annual turnover:
  - Annual turnover > EUR 100,000: monthly
  - EUR 30,000 – 100,000: quarterly (or monthly if elected)
  - Below EUR 30,000: annually (or quarterly/monthly if elected)
- **Tax point**: Generally when goods are delivered or services are performed
- **Reverse charge (kaannetty verovelvollisuus)**: Applies to services from non-resident suppliers, construction services (subcontractor to main contractor), and certain metal/scrap sales
- **Small business relief**: Below the EUR 20,000 threshold, businesses may opt out of VAT registration entirely
- **Intrastat**: Reporting required for intra-EU goods trade above thresholds
- **EC Sales List**: Required for intra-EU supplies of goods and services

## Common Pitfalls
1. **25.5% rate is the highest in the EU**: The increase from 24% to 25.5% occurred in September 2024 — systems must reflect the current rate
2. **13.5% rate for 2026**: The reduced rate for food changed from 14% to 13.5% on January 1, 2026 — update invoicing systems accordingly
3. **Restaurant food vs. groceries**: Restaurant/catering food is 13.5% (reduced); alcohol served in restaurants is 25.5% (standard) — each must be itemized separately
4. **10% rate scope**: Books, transport, hotels, and cultural events use 10% — do not confuse with the 13.5% food rate
5. **Non-resident registration**: Foreign businesses must register from the first taxable supply — no threshold applies
6. **Y-tunnus on invoices**: Both the Y-tunnus and the FI-prefixed VAT number should appear — they serve different purposes
7. **Archiving period**: Finland requires 10-year retention — longer than many EU countries
8. **Small business threshold change**: The threshold increased to EUR 20,000 in 2025 — businesses near the old EUR 15,000 threshold should verify their obligations
