# Colombia — IVA (VAT) & Electronic Invoicing Guide

## Overview
Colombia's IVA (Impuesto al Valor Agregado) is administered by DIAN (Dirección de Impuestos y Aduanas Nacionales). Colombia has a mature mandatory e-invoicing system.

## Tax Rates
- **Standard rate: 19%**
- **Reduced rate: 5%** (basic foodstuffs, agricultural inputs, some medical devices, feminine hygiene products, electric/hybrid vehicles, bicycles)
- **Zero-rated (0%)**: Exports
- **Exempt (no IVA, seller gets refund of input IVA)**: Basic groceries, medications, education, public transport, internet services ≤3 SMMLV, residential utilities (first tiers), agricultural machinery
- **Excluded (no IVA, no input credit)**: Certain government services, food produced directly

## Tax ID (NIT)
- NIT (Número de Identificación Tributaria): 9 digits + check digit
- Format: `XXX.XXX.XXX-X`
- RUT (Registro Único Tributario): registration document containing the NIT

## Electronic Invoice (Factura Electrónica de Venta)
Mandatory since November 1, 2020 for all taxpayers:
- XML format (UBL 2.1 based)
- Must be validated by DIAN before delivery to buyer
- Digital signature required (X.509 certificate)
- UUID assigned after DIAN validation
- CUFE (Código Único de Factura Electrónica) — unique hash per invoice

### Required Fields
1. Invoice number (authorized range from DIAN)
2. Date and time of issue
3. Date of validation by DIAN
4. Seller NIT, name, address, fiscal regime
5. Buyer NIT, name, address (B2B)
6. Item description, quantity, unit of measure
7. Unit price
8. IVA rate and amount per item
9. Withholding taxes (ReteFuente, ReteIVA, ReteICA) if applicable
10. Total before taxes
11. Total IVA
12. Total withholdings
13. Net amount payable
14. CUFE (unique invoice hash)
15. QR code

## Withholding Taxes on Invoices
Colombia has multiple withholding taxes that appear ON the invoice:
- **ReteFuente**: Income tax withholding (varies by transaction type: 1–20%)
- **ReteIVA**: IVA withholding (15% of IVA amount, by designated agents)
- **ReteICA**: Industry and commerce tax withholding (varies by municipality, typically 0.2–1.4%)
- Net payment = Invoice total – ReteFuente – ReteIVA – ReteICA

## Electronic Documents Ecosystem
- **Factura Electrónica**: Sales invoice
- **Nota Crédito**: Credit note
- **Nota Débito**: Debit note
- **Documento Soporte**: Support document for purchases from non-invoice-obligated sellers
- **Nómina Electrónica**: Electronic payroll (separate system)

## Filing
- Bimonthly IVA returns for most taxpayers
- Monthly for large taxpayers (Grandes Contribuyentes)
- Annual simplified regime if qualified

## Common Pitfalls
- Three types of withholding taxes on one invoice (confusing for foreigners)
- DIAN-authorized invoice numbering ranges: must request and manage
- CUFE calculation errors cause DIAN rejection
- ReteFuente rates vary by transaction type and buyer/seller size
- Municipal ReteICA rates differ city to city
- Support documents required when buying from informal/exempt sellers
