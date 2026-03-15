# Turkey — VAT & E-Fatura Guide

## Overview
Turkey's VAT (KDV - Katma Değer Vergisi) has three rates. Turkey has one of the most advanced e-invoicing systems globally, mandatory since 2014 for large taxpayers.

## Tax Rates
- **20%**: Standard rate (increased from 18% on July 10, 2023)
- **10%**: Basic foodstuffs, tourism, health, residential property
- **1%**: Agricultural products, some food items, newspapers, social housing, second-hand motor vehicles
- **0%**: Exports, international transport, services for foreign clients used abroad

## Tax ID (VKN)
- **Tax Identification Number (VKN)**: 10 digits for companies
- **T.C. Kimlik No**: 11 digits for individuals (national ID)

## E-Invoice (e-Fatura) System
### Who Must Use It
- Gross revenue >TRY 3 million in previous year: mandatory e-Fatura
- Specific sectors regardless of revenue: fuel, tobacco, pharmaceutical, vehicle dealers
- All taxpayers must use e-Arşiv (electronic archive) for non-e-Fatura transactions

### E-Fatura Format
- UBL-TR 1.2 (Turkish localization of UBL)
- XML with mandatory digital signature or financial seal (mali mühür)
- Transmitted via GIB (Revenue Administration) portal or private integrators
- Real-time: processed within seconds

### E-Fatura Types
- **SATIS**: Sales invoice
- **IADE**: Return invoice
- **TEVKIFAT**: Withholding invoice
- **ISTISNA**: Exception/exemption invoice
- **OZELMATRAH**: Special tax base invoice
- **IHRACKAYITLI**: Export-registered invoice

### Required Fields
1. Invoice number and date
2. Seller name, address, VKN
3. Buyer name, address, VKN
4. Item description
5. Quantity and unit
6. Unit price
7. KDV rate per item
8. KDV amount per item
9. Withholding rate and amount (if applicable)
10. Total excluding KDV
11. Total KDV
12. Grand total
13. Notes/special codes
14. QR code (mandatory since September 2023)
15. Digital signature or financial seal

## KDV Withholding (Tevkifat)
Certain transactions require the buyer to withhold portion of KDV:
- **Full withholding (10/10)**: Specific professional services to government
- **Partial withholding**: 3/10 to 9/10 depending on transaction type
  - 5/10: Cleaning, security, catering services
  - 7/10: Construction, metal/plastic industry
  - 9/10: Scrap metal, waste
- Buyer remits withheld amount directly to tax authority

## E-Arşiv (Electronic Archive)
- For invoices not covered by e-Fatura (B2C, small transactions)
- Must be issued electronically and stored
- Threshold: all taxpayers since 2020
- Internet sales: mandatory e-Arşiv regardless of amount

## Key Rules
- 10-year document retention requirement
- KDV returns filed monthly (26th of following month)
- Input KDV offset against output KDV; excess carried forward (no cash refund except exports)
- Special Consumption Tax (ÖTV) is separate from KDV (applied on fuel, alcohol, tobacco, luxury goods)

## Common Pitfalls
- Not applying KDV withholding when required (significant penalties)
- Wrong e-Fatura type code for the transaction
- QR code missing (mandatory since September 2023)
- Digital signature expired or invalid
- Not issuing e-Arşiv for B2C when required
- Confusing KDV with ÖTV (Special Consumption Tax)
