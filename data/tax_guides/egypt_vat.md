# Egypt — VAT Guide

## Overview
Egypt's VAT replaced the General Sales Tax in September 2016. Administered by the Egyptian Tax Authority (ETA). Egypt has implemented a mandatory e-invoicing system.

## Tax Rates
- **Standard rate: 14%**
- **Table tax**: Fixed amounts on specific goods (cement, steel, tobacco, telecom services) — applied IN ADDITION to VAT
- **Zero-rated (0%)**: Exports, goods/services to free zones
- **Exempt**: Basic food (bread, flour, dairy, tea, sugar), healthcare, education, financial services, residential rent, public transport, newspapers, agricultural equipment, natural gas for residential use

## VAT Registration
- **Mandatory**: Annual revenue >EGP 500,000
- **Simplified scheme**: Small businesses with revenue EGP 500K–10M can use simplified regime (0.5–1% of revenue instead of standard VAT)
- Tax Registration Number: 9 digits

## E-Invoicing & E-Receipt
### E-Invoice (B2B) — Mandatory
- Rolled out in phases since November 2020
- Now mandatory for all VAT-registered taxpayers
- SDK integration or ETA portal
- JSON format uploaded to ETA system
- UUID assigned by ETA for each invoice
- Digital signature required

### E-Receipt (B2C) — Mandatory
- Mandatory since 2023 in phases
- Point-of-sale integration with ETA
- Real-time transmission
- QR code on each receipt

### Required Fields
1. Issuer name, address, Tax Registration Number
2. Receiver name, address, Tax Registration Number (B2B)
3. Invoice type (I = invoice, C = credit, D = debit)
4. Date and time
5. Item description, Internal code, GS1/EGS code
6. Quantity, unit type
7. Unit price (net)
8. Discount per item
9. Tax type (T1 = VAT 14%, T2 = table tax, T3 = etc.)
10. Tax rate and amount per item
11. Total sales, total discount, total net, total tax, total amount
12. Digital signature
13. UUID from ETA

## Table Tax (Special Consumption)
Applied on specific items at fixed rates or amounts:
- Cement, iron/steel: various rates
- Telecom services: 8% (on top of 14% VAT)
- Passenger cars: 1–30% depending on engine size
- Air conditioning: 8%
- Tobacco products: fixed amount per unit
- Important: Table tax and VAT may apply simultaneously

## Common Pitfalls
- Table tax + VAT double layer on certain goods (need both calculated)
- E-invoice digital signature certificate management
- EGS (Egyptian Standard) item codes required for each product
- Simplified scheme: cannot claim input credits
- Credit notes must reference original invoice UUID
- Free zone transactions: specific documentation required
