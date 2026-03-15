# Argentina — IVA (Impuesto al Valor Agregado) Guide

## Overview

Argentina's Value Added Tax, known as IVA (Impuesto al Valor Agregado), is a consumption tax levied on the sale of goods and provision of services within the country. It is administered by **AFIP** (Administración Federal de Ingresos Públicos), the federal tax authority. Argentina operates a multi-rate IVA system with standard, reduced, increased, and super-reduced rates. Since November 2025, the "IVA Simple" system (General Resolution 5705/2025) requires all VAT-registered businesses to use digitized, pre-filled monthly VAT returns (Form F 2051) based on e-invoice data.

## Tax Rates

- **Standard rate: 21%** — applies to most goods and services
- **Reduced rate: 10.5%** — applies to:
  - Meat, fruit, and vegetables
  - Agricultural services
  - Passenger transport (over 100 km)
  - Residential housing construction
  - Certain medical services and equipment
  - Books, newspapers, and periodicals
  - Interest on personal loans from financial institutions
- **Increased rate: 27%** — applies to:
  - Telecommunications services
  - Domestic gas supply
  - Water supply
  - Electricity for industrial/commercial users
- **Super-reduced rate: 2.5%** — applies to:
  - Certain printed or digital newspapers and magazines
  - Related advertising services
- **Zero-rated (0%)**:
  - Exports of goods and services
  - Digital services sold to customers outside Argentina
- **Exempt**:
  - Bread and milk
  - Books (certain categories)
  - Natural water
  - Medicine (certain categories)
  - Postage stamps
  - Education (public and accredited private institutions)
  - Medical and hospital care
  - Theatre, cinema, music, and sports event tickets
  - Local passenger transport under 100 km (taxis, buses)
  - International transportation
  - Residential and farm leasing
  - Government services
  - Religious institution cultural services
  - Aircraft for commercial/defence use
  - Ships and boats for government use

## Tax ID Format

**CUIT (Clave Única de Identificación Tributaria)**

- **Format:** 11 digits in the pattern `NN-NNNNNNNN-N`
- **Structure:**
  - First 2 digits: Type indicator (20 = male individual; 27 = female individual; 23/24/25/26 = either gender if duplicate; 30 or 33 = legal entity)
  - Next 8 digits: DNI number (individuals) or AFIP-assigned number (legal entities)
  - Last digit: Check digit calculated using Modulo 11 algorithm
- **Example:** `30-71234315-6`
- **Verification:** [AFIP Constancia de Inscripción](https://www.afip.gob.ar/genericos/constancias/)

## Invoice Requirements

1. Invoice type designation (A, B, C, E, M, or T depending on parties' tax status)
2. Pre-printed or electronically assigned CAE/CAEA authorization code
3. Issuer's legal name and CUIT number
4. Issuer's registered address
5. Issuer's IVA taxpayer category (Responsable Inscripto, Monotributista, etc.)
6. Date of issue
7. Sequential invoice number (format: point of sale + sequential number, e.g., 0001-00000001)
8. Buyer/recipient's legal name and CUIT (for Type A invoices)
9. Buyer's IVA taxpayer category
10. Description of goods or services
11. Quantity and unit price
12. Net taxable amount (broken down by tax rate)
13. IVA rate applied (21%, 10.5%, 27%, or 2.5%)
14. IVA amount
15. Total amount
16. Currency (if not ARS, exchange rate must be indicated)
17. CAE (Código de Autorización Electrónico) or CAEA code and expiration date
18. QR code (mandatory for electronic invoices)
19. Start and end date of service period (for service invoices)

## E-Invoicing

- **Status:** Mandatory for all VAT-registered taxpayers. Paper invoicing has been fully discontinued.
- **Platform:** AFIP's online portal or authorized third-party systems integrated with AFIP web services.
- **Format:** XML transmitted via AFIP web services (WSFE for domestic invoices, WSFEX for exports).
- **Authorization:** Each invoice must receive a CAE (Código de Autorización Electrónico) from AFIP before being delivered to the buyer.
- **IVA Simple (2025):** From November 2025, all VAT-registered businesses use pre-filled VAT returns (Form F 2051) generated automatically from e-invoice data in the Digital VAT Books.
- **Retention:** Electronic invoices must be stored for a minimum of 10 years.

## Key Rules

- **Invoice types matter:** Type A invoices are issued between Responsable Inscripto (registered) taxpayers. Type B invoices are issued to final consumers or exempt parties. Type C invoices are issued by Monotributistas (simplified tax regime). Using the wrong type triggers penalties.
- **Withholding and perception regimes:** Argentina has extensive IVA withholding and perception systems at both federal and provincial levels. Buyers designated as withholding agents must withhold IVA from payments.
- **Monthly filing:** VAT returns must be filed monthly, with the due date depending on the taxpayer's CUIT termination digit.
- **Fiscal credit recovery:** Input VAT credits can only be claimed if supported by valid electronic invoices with a CAE.
- **Provincial taxes (Ingresos Brutos):** In addition to national IVA, each province levies its own turnover tax. These are separate from IVA but affect pricing and compliance.
- **Digital services:** Non-resident digital service providers supplying Argentine consumers must register and charge 21% IVA, collected via intermediaries or payment platforms.
- **Export refunds:** Exporters may claim refunds of IVA paid on inputs related to exported goods/services.

## Common Pitfalls

1. **Issuing the wrong invoice type** — Using a Type A invoice when a Type B or C is required (or vice versa) can result in penalties and denial of input tax credits to the buyer.
2. **Missing or expired CAE** — Invoices without a valid CAE code are not legally valid. Always request and verify the CAE before delivering the invoice.
3. **Ignoring provincial withholding obligations** — Each province has its own IVA perception and Ingresos Brutos withholding rules, which are frequently updated and can create double taxation if not properly managed.
4. **Failing to distinguish exempt vs. zero-rated** — Exempt supplies do not allow recovery of input IVA, whereas zero-rated supplies (exports) do. Misclassifying these leads to lost credits or incorrect filings.
5. **Late filing of monthly VAT returns** — Penalties accrue quickly for late filings, and AFIP may suspend the taxpayer's CUIT.
6. **Not reconciling e-invoice data with IVA Simple returns** — Since November 2025, pre-filled VAT returns are generated from digital VAT book data. Discrepancies between actual invoices and the pre-filled return must be resolved before submission.
7. **Overlooking the 27% rate for utilities** — Telecoms, gas, water, and electricity for commercial/industrial users are taxed at 27%, not 21%. Misapplying the standard rate results in underpayment.
8. **Failure to include QR code on e-invoices** — QR codes are mandatory and must link to AFIP's verification service. Missing QR codes invalidate the invoice for the buyer's tax credit purposes.
