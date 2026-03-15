# Ecuador — IVA (Impuesto al Valor Agregado) Guide

## Overview
Ecuador's IVA (Impuesto al Valor Agregado) is administered by the SRI (Servicio de Rentas Internas / Internal Revenue Service). The IVA rate was increased from 12% to 15% effective April 1, 2024, following a national referendum approving the increase to fund public security. The SRI confirmed that the 15% rate remains in effect for 2026.

## Tax Rates
- **Standard rate: 15%** (increased from 12% on April 1, 2024 — confirmed to remain at 15% for 2026)
- **Zero-rated (0%)**: Unprocessed food products, agricultural inputs, medicines, feminine hygiene products, books and educational materials, exports of goods and services, raw materials for export production, agricultural machinery, certain renewable energy equipment
- **Exempt (IVA not applicable)**: Certain financial services, residential property transfers, public transport, education, healthcare, burial services, artistic and cultural events, membership fees for social/sports clubs

### Important Note on Rate History
- Pre-April 2024: 12% (longstanding rate)
- April 1, 2024 onward: 15% (post-referendum increase)
- The SRI circular dated December 26, 2025 confirmed 15% applies for 2026 unless modified by executive decree

## Tax ID Format
- **RUC** (Registro Unico de Contribuyentes / Unique Taxpayer Registry): 13 digits
  - Natural persons: 10-digit cedula + `001`
  - Private companies: First 2 digits (province code) + `9` + 6 digits + `001`
  - Public entities: First 2 digits (province code) + `6` + 6 digits + `001`
  - Format example: `1790012345001`
- **Cedula**: 10-digit national identity number (for individuals)
- Verify at: https://srienlinea.sri.gob.ec

## Electronic Invoicing (Comprobantes Electronicos)
### Mandatory Scope
- Mandatory for all VAT-registered taxpayers (except certain simplified regime small businesses)
- All electronic documents for transactions exceeding USD 4 must be issued electronically
- **Real-time transmission**: From January 1, 2026, all electronic documents must be transmitted to the SRI in real time, at the moment they are generated (previously, there was a grace period)

### Document Types
- **Factura**: Sales invoice
- **Nota de Credito**: Credit note
- **Nota de Debito**: Debit note
- **Comprobante de Retencion**: Withholding certificate
- **Guia de Remision**: Shipping guide / waybill
- **Liquidacion de Compra**: Purchase settlement (used when buying from informal sellers)

### Format and Validation
- **Format**: XML with digital signature (electronic certificate)
- **Validation**: Documents must be authorized by SRI before delivery to the buyer
- **Authorization number (clave de acceso)**: 49-digit unique code assigned to each authorized document
- **RIDE** (Representacion Impresa del Documento Electronico): The printable version of the e-document, which must include the authorization number and a barcode
- **Storage**: Electronic documents must be archived for a minimum of **7 years** in electronic format

## Invoice Required Fields
1. RUC of the issuer, trade name, and legal name
2. Sequential invoice number (authorized by SRI)
3. Authorization number (clave de acceso — 49 digits)
4. Date of issue
5. Buyer's RUC, cedula, or passport number
6. Buyer's name or business name
7. Description of goods or services
8. Quantity and unit price
9. Discount amount (if applicable)
10. IVA rate per line item (15%, 0%, or exempt)
11. IVA amount per line item
12. Subtotal per IVA rate
13. Total IVA amount
14. Total amount payable (including IVA)
15. Payment method and terms
16. Digital signature of the issuer
17. For exports: additional export-specific fields as required by SRI

## Withholding Taxes (Retenciones)
Ecuador has a withholding tax system where the BUYER withholds taxes:
- **Retencion de IVA**: Buyers designated as withholding agents must withhold 30%, 70%, or 100% of IVA depending on the transaction type and parties involved
- **Retencion de Impuesto a la Renta**: Income tax withholding at source, rates vary from 1% to 25% by transaction type
- **Comprobante de Retencion**: A withholding certificate must be issued within 5 business days of payment
- **Net payment**: Invoice total minus IVA withholding minus income tax withholding

## Key Rules
- **Registration**: No revenue threshold — any person or entity habitually or incidentally selling goods, providing services, or importing must register with the SRI and obtain an RUC
- **Simplified regime (RIMPE)**: Available for small businesses and entrepreneurs with annual income up to USD 300,000 — simplified obligations, lower rates
- **Filing frequency**: Monthly IVA returns for most taxpayers
- **Due date**: Based on the 9th digit of the RUC — ranges from the 10th to the 28th of the following month
- **Tax point**: Generally the date of delivery of goods or performance of services
- **Foreign digital services**: Non-resident providers of digital services to Ecuadorian consumers must register and charge 15% IVA

## Common Pitfalls
1. **15% rate is current**: The rate increased from 12% to 15% in April 2024 and remains at 15% for 2026 — do not apply the old 12% rate
2. **Real-time transmission from 2026**: All e-documents must be sent to SRI at the moment of generation — no more delayed batch transmissions
3. **Withholding obligations**: Buyers designated as withholding agents must issue retenciones within 5 business days — failure creates joint liability
4. **Zero-rated vs. exempt**: Zero-rated items (unprocessed food, medicines) allow input IVA recovery; exempt items do not
5. **49-digit authorization code**: Each e-document has a unique 49-digit clave de acceso — this must appear on the RIDE (printed version) and is essential for verification
6. **7-year archiving**: Electronic documents must be kept for 7 years — longer than many countries
7. **Sequential numbering**: Invoice numbers must be within SRI-authorized ranges — issuing outside the authorized range invalidates the document
8. **RIMPE eligibility**: Small businesses should verify RIMPE qualification annually — exceeding USD 300,000 requires switching to the general regime
