# Spain — IVA (Impuesto sobre el Valor Anadido) & SII/VeriFactu Guide

## Overview
Spain's VAT, known as IVA (Impuesto sobre el Valor Anadido), is administered by the Agencia Estatal de Administracion Tributaria (AEAT). Spain operates two complementary real-time reporting systems: SII (Suministro Inmediato de Informacion) for large taxpayers and VeriFactu for all other businesses. As of 2026, Spain is implementing VeriFactu compliance requirements alongside its established SII system, creating one of Europe's most comprehensive real-time VAT monitoring frameworks.

**Note**: The Canary Islands (IGIC tax, not IVA), Ceuta, and Melilla (IPSI tax) have separate indirect tax regimes and are not covered by mainland IVA rules.

## Tax Rates
- **Standard rate: 21%** (tipo general)
- **Reduced rate: 10%** (tipo reducido) — food and beverages for human/animal consumption (excluding alcohol and tobacco), water, hotel and restaurant services, passenger transport, admission to cultural and sporting events, housing renovation, funeral services, hairdressing, certain agricultural supplies
- **Super-reduced rate: 4%** (tipo superreducido) — bread, flour, milk, cheese, eggs, fruit and vegetables, books and newspapers, medicines, vehicles for disabled persons, subsidized housing (VPO)
- **Temporarily reduced**: Basic food staples (bread, milk, eggs, fruit, vegetables, cereals, cheese) were temporarily at 0% through 2024; rates are being restored to their standard reduced/super-reduced levels in 2025-2026
- **Zero-rated (0%)**: Intra-community supplies, exports, international transport
- **Exempt** (exento, no input credit): Financial and insurance services, medical/dental services, education, residential rental, postal services, cultural services by public bodies

## Tax ID Format
- **NIF (Numero de Identificacion Fiscal)**: 9 characters
  - **Individuals (Spanish)**: 8 digits + letter: `12345678Z`
  - **Foreign residents (NIE)**: letter + 7 digits + letter: `X1234567L` (prefixes X, Y, or Z)
  - **Companies (CIF)**: letter + 7 digits + check character: `B12345678`
    - First letter indicates entity type: A (SA/corporation), B (SL/limited), etc.
  - Note: CIF has been officially replaced by NIF, but the term CIF is still commonly used
- **EU VAT Number**: `ES` + NIF: `ESB12345678`
- Verify at: https://ec.europa.eu/taxation_customs/vies/ (EU VIES) or https://www.agenciatributaria.es

## Invoice Requirements
1. Invoice number (numero de factura) — sequential within each calendar year
2. Invoice date (fecha de expedicion)
3. Date of supply (fecha de operacion) if different from invoice date
4. Supplier's full name/business name and address
5. Supplier's NIF/CIF
6. Buyer's full name/business name and address
7. Buyer's NIF/CIF (mandatory for B2B)
8. Description of goods or services
9. Quantity and unit price (net of IVA)
10. Taxable base (base imponible) per VAT rate
11. IVA rate(s) applied (21%, 10%, 4%)
12. IVA amount per rate (cuota tributaria)
13. Total amount including IVA
14. Applicable income tax withholding (retencion IRPF) if applicable (e.g., 15% for autónomos)
15. For reverse charge: "Inversion del sujeto pasivo" notation
16. For intra-EU: both parties' VAT IDs and exemption reference
17. **QR code** (mandatory from 2026 under VeriFactu regulation)
18. **VeriFactu legend**: "Factura verificable en la sede electronica de la AEAT" or "VERI*FACTU" if the invoice is VeriFactu-compliant

## E-Invoicing & Real-Time Reporting

### SII (Suministro Inmediato de Informacion)
SII is a near-real-time VAT reporting system for large taxpayers.

**Who must use SII:**
- Businesses with annual turnover exceeding EUR 6,010,121.04
- VAT groups (grupos de IVA)
- Businesses registered in REDEME (monthly VAT refund scheme)
- Voluntary opt-in available for other taxpayers

**How SII works:**
- Invoice data (not the full invoice) is reported electronically to AEAT
- **Issued invoices**: Must be reported within **4 calendar days** of issuance (excluding Sundays and national holidays)
- **Received invoices**: Must be reported within **4 calendar days** of recording (excluding Sundays and national holidays)
- Submissions via AEAT's SII web service using XML format
- SII users are exempt from filing Forms 347 (annual), 340, and 390
- SII users must file **monthly** VAT returns (Modelo 303)
- AEAT provides **Pre303**: pre-populated monthly VAT return drafted from SII data

### VeriFactu (Sistema de Emision de Facturas Verificables)
VeriFactu is the new compliance framework for invoicing systems, effective from 2026.

**Timeline:**
- **January 1, 2026**: Companies subject to Corporate Income Tax must comply
- **July 1, 2026**: All other businesses, including sole traders (autonomos), must comply

**Requirements:**
- Billing software must ensure **integrity, traceability, and inalterability** of invoice records
- Every invoice must include a **QR code** for verification
- Two compliance modes:
  1. **VeriFactu mode**: Real-time transmission of invoice data to AEAT (recommended)
  2. **Non-VeriFactu mode**: Local secure storage with strict audit trail requirements — must still generate QR codes and maintain tamper-proof records
- Invoices in VeriFactu mode carry the legend "VERI*FACTU"

**Note**: Businesses already using SII are exempt from VeriFactu requirements, as SII provides equivalent (and more detailed) real-time reporting.

### Structured E-Invoicing (B2B)
- Spain has announced mandatory B2B e-invoicing for all businesses, expected to be phased in during 2026-2027
- B2G e-invoicing (FACe platform, Facturae 3.2.2 format) has been mandatory since 2015

## Key Rules
- **Registration threshold**: No minimum for domestic businesses performing taxable activities; non-residents must register from the first taxable supply
- **Filing frequency**: Quarterly (Modelo 303) for most businesses; monthly for SII-obligated businesses and those in REDEME
- **Annual summary**: Modelo 390 (except SII users)
- **Recargo de equivalencia**: Special surcharge regime for retailers — additional charge on top of IVA (5.2% on 21%, 1.4% on 10%, 0.5% on 4%) — retailer does not file VAT returns
- **Prorrata**: Input VAT apportionment rules when making both taxable and exempt supplies
- **Modelo 347**: Annual declaration of operations with third parties exceeding EUR 3,005.06 (SII users exempt)
- **Withholding (IRPF)**: Autonomos typically apply 15% income tax withholding on professional service invoices (7% in first 3 years of activity)

## Common Pitfalls
1. **SII 4-day deadline**: Missing the 4-calendar-day reporting window triggers penalties — weekends count, only Sundays and national holidays are excluded
2. **Canary Islands confusion**: IGIC (7% general rate) applies in the Canary Islands, not IVA — issuing an IVA invoice to a Canary Islands customer is incorrect
3. **VeriFactu QR code omission**: From 2026, all invoices must include a QR code regardless of whether the business uses VeriFactu or non-VeriFactu mode
4. **Recargo de equivalencia errors**: Forgetting to apply the surcharge when selling to retailers in this regime, or retailers incorrectly trying to deduct input VAT
5. **IRPF withholding confusion**: Not all invoices require withholding — only professional services from autonomos to businesses, not product sales
6. **Temporary food rate restoration**: Businesses continuing to apply the temporary 0% rate on basic foods after the relief period ends
7. **SII vs. VeriFactu overlap**: Businesses in SII do not need VeriFactu, but businesses leaving SII must immediately comply with VeriFactu
8. **Modelo 347 filing**: Non-SII businesses forgetting to report third-party operations above EUR 3,005.06 in the annual declaration
