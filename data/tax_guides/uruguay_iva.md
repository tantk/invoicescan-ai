# Uruguay — IVA (Impuesto al Valor Agregado) Guide

## Overview
Uruguay's IVA (Impuesto al Valor Agregado) is administered by the DGI (Direccion General Impositiva). Uruguay has a relatively high standard IVA rate of 22%. The country has fully implemented mandatory electronic invoicing (CFE — Comprobantes Fiscales Electronicos) for all VAT taxpayers.

## Tax Rates
- **Standard rate: 22%** (tasa basica)
- **Reduced rate: 10%** (tasa minima) — basic food items (bread, pasta, rice, cooking oil, sugar), medicines, hotel accommodation services, health services, first sale of immovable property, agricultural products, passenger transport
- **Temporary tourism rate: 9%** — hospitality and tourism services (reduced from 22%, extended through April 30, 2026)
- **Zero-rated (0%)**: Exports of goods and services
- **Exempt (no IVA)**: Certain financial services, residential property rental, education services, agricultural machinery and inputs (specific list), diplomatic and consular supplies, certain cultural products

## Tax ID Format
- **RUT** (Registro Unico Tributario / Unique Tax Registry): 12-digit number
  - Format: `XX XXXXXXX XXX X` (varies by entity type)
  - The RUT serves as both the business identification number and the VAT number — there is no separate VAT registration number in Uruguay
- **Cedula de Identidad**: Used for individuals (8-digit national ID)
- Verify at: https://www.dgi.gub.uy

## Electronic Invoicing (CFE — Comprobantes Fiscales Electronicos)
### Mandatory Scope
- **All VAT taxpayers** must issue CFE — no paper invoices for VAT-registered businesses
- Since 2025, new VAT taxpayers must issue CFE from the moment of registration with no adaptation period
- Every CFE issued and approved by DGI is simultaneously a legal invoice for the buyer and a reported transaction to the tax authority

### CFE Types
- **e-Ticket**: B2C sales receipt
- **e-Factura**: B2B invoice
- **e-Nota de Credito**: Credit note (must be linked to the original CFE from March 3, 2026)
- **e-Nota de Debito**: Debit note
- **e-Remito**: Shipping/delivery document
- **e-Resguardo**: Withholding certificate
- **e-Factura de Exportacion**: Export invoice

### CFE Format and Validation
- **Format**: XML with digital signature (X.509 certificate)
- **Validation**: CFE must be transmitted to DGI for validation; DGI returns a CAE (Constancia de Autorizacion del CFE)
- **Printed representation**: Must include a QR code and the CAE for verification
- **Storage**: CFEs must be archived electronically for a minimum of 5 years

### 2026 Format Updates
- **March 3, 2026**: New fields, values, and validations for zones A, B, C, D, E, and G go live, plus updated printed representation format
- **April 15, 2026**: Mandatory enforcement of validations for zones F and K
- Credit Notes now require mandatory linkage to previously issued CFEs
- Standard codes (GTIN/EAN) usage is reinforced
- New logistics fields added to export invoices

## Invoice Required Fields (CFE Content)
1. CFE type and number
2. Date of issue
3. Issuer's RUT, name, and address
4. Recipient's RUT or cedula, name, and address (for e-Factura)
5. Description of goods or services
6. Quantity, unit of measure, and unit price
7. IVA rate per line item (22%, 10%, or exempt)
8. IVA amount per line item
9. Net amount per rate
10. Total IVA amount
11. Total amount inclusive of IVA
12. Currency (if not UYU, the exchange rate must be stated)
13. Digital signature
14. CAE (assigned after DGI validation)
15. QR code (on printed representation)

## Key Rules
- **Registration**: All businesses carrying out taxable activities must register with DGI and obtain a RUT. There is no general revenue threshold for registration — anyone performing taxable activities must register.
- **Filing frequency**: Monthly IVA returns for most taxpayers
- **Due date**: Varies by the last digit of the RUT — typically between the 16th and 25th of the following month
- **Tax point**: Generally the earlier of delivery of goods/performance of service or invoice issuance
- **Reverse charge**: Not commonly used domestically — imports of services may require self-assessment
- **Withholding taxes**: Certain large buyers (designated withholding agents) must withhold a percentage of IVA on payments to suppliers and remit to DGI
- **Tourism IVA refund**: Foreign tourists can claim a refund of IVA paid on hotel and restaurant services (reduced to 9% through April 2026)

## Common Pitfalls
1. **Mandatory CFE from day one**: New taxpayers have no adaptation period — e-invoicing is required immediately upon registration
2. **Credit note linkage**: From March 3, 2026, credit notes must reference the original CFE — unlinked credit notes will be rejected
3. **Two standard rates coexisting**: The temporary 9% tourism rate applies only to specific hospitality services — most services remain at 22%
4. **RUT is the VAT number**: There is no separate VAT registration — the RUT serves both corporate and VAT identification purposes
5. **Withholding agent obligations**: Large companies designated as withholding agents must withhold IVA on supplier payments — failure to withhold creates joint liability
6. **Export invoices**: Must use the specific e-Factura de Exportacion type with new logistics fields from March 2026
7. **QR code on printed copies**: Every printed representation of a CFE must include a QR code for verification — missing QR codes invalidate the document
8. **Monthly filing**: Uruguay requires monthly returns, not quarterly — missing a month creates immediate compliance issues
