# India — GST (Goods and Services Tax) Guide

## Overview
India's GST replaced 17 indirect taxes in July 2017. It's a destination-based tax with a dual structure: Central GST (CGST) + State GST (SGST) for intrastate, or Integrated GST (IGST) for interstate.

## Tax Structure
- **0%**: Essential items (fresh food, healthcare, education)
- **5%**: Basic necessities (packaged food, transport, small restaurants)
- **12%**: Standard goods (processed food, business class air travel, state-run lotteries)
- **18%**: Most goods and services (IT services, telecom, financial services, restaurants in hotels >₹7,500/night)
- **28%**: Luxury/demerit goods (cars, tobacco, aerated drinks, cement, ACs)
- **Cess**: Additional cess on luxury goods (1–22% on top of 28%)

## How Tax Splits Work
- **Intrastate** (same state): CGST + SGST (each half the total rate). E.g., 18% = 9% CGST + 9% SGST
- **Interstate** (different states): IGST at full rate. E.g., 18% IGST
- **Cess**: Calculated on base + can be compound in some cases

## GSTIN Format
15-digit: `22AAAAA0000A1Z5`
- Digits 1-2: State code
- Digits 3-12: PAN number
- Digit 13: Entity number within state
- Digit 14: Z (default)
- Digit 15: Check digit

## HSN/SAC Codes
- HSN (Harmonized System of Nomenclature) for goods
- SAC (Services Accounting Code) for services
- 4-digit mandatory for turnover ≤₹5 crore
- 6-digit mandatory for turnover >₹5 crore

## Invoice Requirements (Rule 46 CGST Rules)
1. Invoice number (sequential, max 16 chars)
2. Invoice date
3. Supplier name, address, GSTIN
4. Recipient name, address, GSTIN (B2B)
5. Place of supply with state code
6. HSN/SAC code
7. Description of goods/services
8. Quantity and unit (UQC)
9. Taxable value
10. CGST/SGST/IGST rate and amount (separately)
11. Cess rate and amount (if applicable)
12. Total in figures and words
13. Signature/digital signature

## E-Invoicing
- Mandatory for businesses with AATO >₹5 crore
- Invoice Registration Portal (IRP) issues Invoice Reference Number (IRN)
- JSON format uploaded to IRP
- IRN + QR code must appear on invoice
- Real-time validation

## Common Pitfalls
- Incorrect state codes lead to wrong CGST/SGST vs IGST split
- HSN code mismatch triggers audit flags
- Input Tax Credit (ITC) denied without valid GSTIN on invoice
- Reverse charge mechanism applies to certain services
- Composition scheme dealers cannot issue tax invoices
