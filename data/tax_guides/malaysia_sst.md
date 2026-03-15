# Malaysia — SST & E-Invoicing Guide

## Overview
Malaysia uses a Sales and Service Tax (SST) system, having repealed GST in 2018. The MyInvois e-invoicing system is rolling out in phases 2024–2025.

## Tax Structure
### Sales Tax
- **10%**: Most manufactured/imported goods
- **5%**: Basic food items, building materials, certain petroleum products
- **0%**: Exported goods, specific exempt goods
- Applies to manufacturers (threshold >RM 500,000 annual sales) and importers

### Service Tax
- **8%**: Most taxable services (increased from 6% in March 2024)
- **6%**: Food and beverage, telecommunications, parking, logistics
- Taxable services include: IT, management, consultancy, legal, accounting, hotels, restaurants, insurance, electricity, telecom

## SST Registration
- Sales Tax: Mandatory for manufacturers with taxable sales >RM 500,000
- Service Tax: Mandatory for prescribed service providers >RM 500,000 (hotels >RM 500,000, restaurants >RM 1,500,000, F&B >RM 1,500,000)
- Registration number format: varies by type

## MyInvois E-Invoicing
### Phased Rollout
- **August 1, 2024**: Annual revenue >RM 100 million
- **January 1, 2025**: Annual revenue >RM 25 million
- **July 1, 2025**: All remaining businesses

### Format
- XML or JSON
- Submitted via MyInvois portal or API
- LHDN (Inland Revenue Board) validates and returns unique identifier
- QR code generated after validation

### Required Fields
1. Seller name, TIN, BRN, SST registration number
2. Buyer name, TIN, BRN
3. Invoice number and date
4. Description of goods/services
5. Unit price, quantity
6. Tax type, rate, and amount
7. Total excluding tax
8. Total tax
9. Total including tax
10. Currency
11. Payment mode
12. E-invoice code and validation link (post-validation)

## TIN (Tax Identification Number)
- Individuals: starts with 'IG' or 'OG'
- Companies: starts with 'C' or 'CS'
- Format being standardized under MyInvois

## Common Pitfalls
- Misclassifying services between 6% and 8% tiers
- Not registering when exceeding threshold
- Manufacturing vs trading classification affects Sales Tax applicability
- Tourism Tax (TTx) on accommodation is SEPARATE from SST (RM 10/night)
- Digital services by foreign providers: 8% service tax (since 2020)
- MyInvois rejection due to invalid TIN or format errors
