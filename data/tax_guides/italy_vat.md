# Italy — IVA (Imposta sul Valore Aggiunto) & FatturaPA/SDI E-Invoicing Guide

## Overview
Italy's VAT, known as IVA (Imposta sul Valore Aggiunto), is administered by the Agenzia delle Entrate (Italian Revenue Agency). Italy was a pioneer in mandatory e-invoicing, implementing universal B2B and B2C e-invoicing via the Sistema di Interscambio (SDI) since January 1, 2019. All invoices must be issued in the standardized FatturaPA XML format and transmitted through SDI — making Italy one of the most mature and comprehensive CTC (Continuous Transaction Controls) systems in the world.

## Tax Rates
- **Standard rate: 22%** (aliquota ordinaria)
- **Reduced rate: 10%** (aliquota ridotta) — electricity for specific uses, certain drugs and pharmaceuticals, hotel accommodation, restaurant meals, meat/fish products, sugar, cocoa, selected transport services, renovation of residential buildings
- **Reduced rate: 5%** (aliquota ridotta) — certain health services, food herbs, urban hygiene/waste collection, passenger transport on seas/lakes/rivers, district heating services
- **Super-reduced rate: 4%** (aliquota super-ridotta) — basic foodstuffs (bread, pasta, milk, olive oil, fresh fruit and vegetables), books and newspapers, first-home purchases, certain medical aids and prosthetics
- **Zero-rated (0%)**: Intra-community supplies, exports
- **Exempt** (esente, no input credit): Financial and insurance services, medical services, education, postal services, residential rent, certain cultural activities

## Tax ID Format
- **Partita IVA** (VAT Number): 11 digits
  - Format: `IT` + 11 digits for EU purposes: `IT12345678901`
  - First 7 digits: unique taxpayer identifier
  - Digits 8-10: province/tax office code
  - Digit 11: check digit (Luhn algorithm variant)
  - Example: `IT02313821007` (Rome-based entity)
- **Codice Fiscale** (Tax Code): 16-character alphanumeric for individuals, 11 digits for companies
  - Both Partita IVA and Codice Fiscale must appear on invoices
- Verify at: https://telematici.agenziaentrate.gov.it/VerificaPI/ or EU VIES system

## Invoice Requirements
All invoices must be in FatturaPA XML format submitted through SDI. The required fields include:

1. Progressive invoice number (numero progressivo)
2. Invoice date (data fattura)
3. Supplier's full name/business name and address
4. Supplier's Partita IVA and Codice Fiscale
5. Buyer's full name/business name and address
6. Buyer's Partita IVA or Codice Fiscale (or Codice Destinatario / PEC for SDI routing)
7. **Codice Destinatario** (7-character recipient code for SDI routing) or **PEC address** (certified email)
8. Description of goods or services
9. Quantity and unit of measure
10. Unit price (net)
11. Total net amount per VAT rate
12. VAT rate (22%, 10%, 5%, 4%, or exempt code)
13. VAT amount per rate
14. Total gross amount
15. Payment terms and method
16. **Bollo (stamp duty)**: EUR 2.00 notation if invoice is VAT-exempt and exceeds EUR 77.47
17. For reverse charge: nature code (N6) indicating "inversione contabile"
18. For intra-EU: both parties' VAT IDs and exemption reference
19. **Regime fiscale** code (e.g., RF01 for ordinary, RF19 for forfettario/flat-rate)

## E-Invoicing — FatturaPA / SDI
### Sistema di Interscambio (SDI)
SDI is Italy's centralized e-invoicing clearance platform operated by the Agenzia delle Entrate. It functions as a mandatory intermediary for all invoices.

### How It Works
1. Supplier generates invoice in **FatturaPA XML format** (current version: v1.2.2, technical specs v1.9)
2. Invoice is digitally signed (XAdES-BES or CAdES-BES) and transmitted to SDI via:
   - SDI web portal
   - PEC (certified email)
   - SDI FTP channel
   - SDI web services (API/SOAP)
3. SDI performs automated validation (format, VAT IDs, syntax checks)
4. If accepted, SDI forwards the invoice to the recipient and simultaneously to the tax authority
5. SDI issues delivery receipts and notifications to both parties
6. Invoices must be transmitted within **12 days** of the transaction date (for immediate invoices) or by the **15th of the following month** (for deferred invoices)

### Scope
- **B2B domestic**: Mandatory since January 1, 2019
- **B2C domestic**: Mandatory since January 1, 2019 (consumer receives a courtesy copy; XML goes to SDI)
- **B2G (public administration)**: Mandatory since March 31, 2015 (FatturaPA was originally designed for this)
- **Cross-border**: Since July 1, 2022 — cross-border transactions must be reported through SDI using the TD17-TD19 document types (replacing the former Esterometro filing)
- **Flat-rate regime (forfettario)**: Mandatory since January 1, 2024 for all forfettario taxpayers

### FatturaPA Technical Details
- **Version**: FatturaPA v1.2.2 with technical specifications v1.9 (2025)
- **New document types**: TD29 (irregular supplier invoices), regime code RF20
- **File format**: XML, digitally signed
- **Over 100 data fields** defined in the schema
- **National CIUS**: FatturaPA is Italy's Core Invoice Usage Specification extending EN 16931

### Archiving (Conservazione Sostitutiva)
- All SDI-processed invoices must be stored electronically for **10 years**
- Both issuers and recipients responsible for compliant archiving
- Must guarantee integrity, readability, and accessibility throughout retention period
- Can use the free Agenzia delle Entrate conservation service or certified third-party providers

## Key Rules
- **Registration threshold**: No minimum threshold — all businesses performing taxable activities must register
- **Forfettario (flat-rate scheme)**: Available for individuals with revenue up to EUR 85,000/year; 15% flat tax (5% for first 5 years of new activity); no VAT charged but must still issue e-invoices through SDI
- **Filing frequency**: Monthly or quarterly VAT returns (Liquidazione IVA), plus annual declaration (Dichiarazione IVA)
- **Reverse charge**: Extensive use — construction subcontracting, energy, IT equipment, scrap metal, cleaning services
- **Split payment (scissione dei pagamenti)**: Public administration bodies pay the net amount to the supplier and remit the VAT directly to the Treasury
- **Intrastat reporting**: Required for intra-EU supplies above thresholds
- **Penalties**: 90% to 180% of the VAT amount for missing/incorrect invoices (Article 6, Legislative Decree 471/1997); reduced penalties available through voluntary disclosure (ravvedimento operoso)

## Common Pitfalls
1. **Incorrect Codice Destinatario or PEC**: Invoice delivery fails in SDI if the recipient code is wrong — invoice is parked in the "cassetto fiscale" but may not reach the buyer
2. **Missing bollo on exempt invoices**: Invoices exempt from IVA exceeding EUR 77.47 must include the EUR 2.00 bollo — omission triggers penalties
3. **12-day transmission window**: Immediate invoices must be sent to SDI within 12 days of the supply date — late submission incurs penalties
4. **Wrong regime code**: Using RF01 (ordinary) instead of RF19 (forfettario) or vice versa invalidates the invoice
5. **Cross-border reporting errors**: Since July 2022, failing to report cross-border transactions through SDI (using TD17-TD19) results in penalties replacing the old Esterometro fines
6. **Digital signature issues**: Expired or invalid digital certificates cause SDI rejection
7. **Archiving non-compliance**: Not maintaining 10-year electronic conservation — both parties can be penalized
8. **Split payment confusion**: Applying split payment to non-PA entities or failing to apply it to PA entities
