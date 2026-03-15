# Costa Rica — IVA (Impuesto al Valor Agregado) Guide

## Overview
Costa Rica's IVA (Impuesto al Valor Agregado) replaced the former General Sales Tax (Impuesto General sobre las Ventas) effective July 1, 2019, under the Fiscal Strengthening Law (Ley de Fortalecimiento de las Finanzas Publicas, Law No. 9635). IVA is administered by the DGT (Direccion General de Tributacion / General Directorate of Taxation) under the Ministry of Finance (Ministerio de Hacienda). Costa Rica is notable for having a multi-rate structure with four reduced rates and mandatory e-invoicing.

## Tax Rates
- **Standard rate: 13%**
- **Reduced rate: 4%** — private health services, private insurance premiums (health-related), air tickets for domestic flights
- **Reduced rate: 2%** — pharmaceutical products and raw materials/equipment for their manufacture, private education services
- **Reduced rate: 1%** — goods in the "Canasta Basica Tributaria" (basic taxable basket — bread, milk, eggs, fruits, vegetables, rice, beans, tortillas, soft drinks), agricultural, livestock, and veterinary supplies, non-sport fishing supplies
- **Zero-rated (0%)**: Exports of goods and services, goods sold to free trade zones
- **Exempt (no IVA)**: Residential electricity and water supply (basic consumption tiers), public terrestrial transport, education (public), healthcare (public), residential property rental (up to 1.5 base salaries), basic food items in the "Canasta Basica" (non-taxable basket — separate from the 1% basket), financial services, cultural and sporting events (organized by the state)

### Additional Special Rates
- **10%**: Air ticket for international flights
- **0.5%**: Organic agricultural products and certain organic farming supplies (mentioned in some provisions)

## Tax ID Format
- **Cedula Juridica** (Legal ID for companies): 10 digits, format `X-XXX-XXXXXX`
  - First digit: entity type (3 = corporation, 4 = branch of foreign entity)
  - Example: `3-101-123456`
- **Cedula de Identidad** (National ID for individuals): 9 digits, format `X-XXXX-XXXX`
  - Example: `1-0234-0567`
- **NITE** (Numero de Identificacion Tributaria Especial): For non-residents
- **DIMEX**: Immigration identification for foreign residents
- Verify at: https://atv.hacienda.go.cr (Virtual Tax Administration)

## Mandatory Electronic Invoicing (Facturacion Electronica)
### Scope
- **Mandatory since 2018** for all VAT-registered entities, with limited exceptions for:
  - Simplified regime taxpayers
  - Agricultural regime taxpayers
  - Religious institutions, condominiums, unions, the state, political parties, public transport operators
- Costa Rica was an early adopter of mandatory e-invoicing in Latin America

### E-Invoice Specifications
- **Format**: XML (structured electronic document)
- **Digital signature**: Each invoice must include a digital signature using a certificate issued by an authorized certification authority
- **Unique key (clave numerica)**: 50-digit unique identifier assigned to each electronic document
- **Current version**: Format 4.4 (mandatory since September 1, 2025), introducing over 140 updates including:
  - Electronic Payment Receipts (REP)
  - Mandatory purchase invoices for foreign suppliers
  - New fields for tax exemptions
  - Digital endorsements by buyers for legal validation
- **Transmission**: Real-time to the Ministry of Finance via the ATV (Administracion Tributaria Virtual) system
- **Cryptographic key**: Obtained through the ATV portal for digital signing

### Document Types
- **Factura Electronica (FE)**: Standard sales invoice
- **Tiquete Electronico (TE)**: Simplified receipt (B2C, when buyer does not need tax credit)
- **Nota de Credito Electronica (NC)**: Credit note
- **Nota de Debito Electronica (ND)**: Debit note
- **Factura Electronica de Compra (FEC)**: Purchase invoice (issued by buyer for transactions with foreign suppliers)
- **Factura Electronica de Exportacion (FEE)**: Export invoice
- **Recepcion Electronica de Pago (REP)**: Electronic payment receipt (new in format 4.4)

## Invoice Required Fields
1. Issuer's cedula (juridica or identidad), name, trade name, and address
2. Recipient's cedula, name, and address (for Factura Electronica)
3. Unique key (clave numerica — 50 digits)
4. Sequential document number
5. Date and time of issue
6. Sales condition (cash, credit, consignment, etc.)
7. Payment method (transfer, card, cash, etc.)
8. Description of goods or services
9. Quantity, unit of measure, and unit price
10. Discount amount and reason (if applicable)
11. IVA rate per line item (13%, 10%, 4%, 2%, 1%, or exempt)
12. IVA amount per line item
13. Subtotal per rate
14. Total IVA amount
15. Total amount payable (including IVA)
16. Currency code (CRC or foreign currency with exchange rate)
17. Digital signature
18. Tax exemption details (if applicable — authorization number, percentage, and institution)
19. For exports: additional export-specific fields

## Key Rules
- **Registration**: All businesses and professionals performing taxable activities must register with the DGT. No general revenue threshold — registration is mandatory from the first taxable activity.
- **Filing frequency**: Monthly IVA returns
- **Due date**: 15th of the following month
- **Tax point**: Generally the date of delivery of goods or performance of services; for continuous services, the billing date
- **Input tax credit**: Fully recoverable for inputs related to taxable supplies at 13%; proportional recovery for mixed supplies; no recovery for inputs related to exempt supplies
- **Proportional credit for reduced rates**: When the output is taxed at a reduced rate (1%, 2%, or 4%), the input tax credit is limited proportionally
- **Foreign digital services**: Non-resident providers of digital services to Costa Rican consumers must register and charge 13% IVA through a simplified regime

## Common Pitfalls
1. **Five different positive rates**: Costa Rica has 13%, 10%, 4%, 2%, and 1% rates — each invoice line must use the correct rate for the specific good or service
2. **Canasta Basica confusion**: There are TWO baskets — the "Canasta Basica" (fully exempt) and the "Canasta Basica Tributaria" (taxed at 1%) — mixing them up causes incorrect tax treatment
3. **Proportional input credit**: When selling goods/services at reduced rates, the input IVA credit is capped proportionally — not the full 13% credit
4. **Format 4.4 mandatory**: Since September 2025, all e-invoices must use format version 4.4 — older formats are rejected by the ATV system
5. **Tiquete vs. Factura**: A Tiquete Electronico does not support the buyer's input tax credit — if the buyer needs a credit, a Factura Electronica must be issued instead
6. **Foreign supplier purchase invoices**: When purchasing from foreign suppliers, the buyer must issue a Factura Electronica de Compra (FEC) and self-assess IVA
7. **50-digit unique key**: Each document has a 50-digit clave numerica — this is essential for verification and must appear on all representations
8. **E-invoicing exemptions are narrow**: Most businesses must use e-invoicing — the exemptions (simplified regime, religious institutions, etc.) are very limited
9. **Health services at 4%**: Private health services use the 4% rate, while public health is exempt — the distinction depends on the provider's classification
