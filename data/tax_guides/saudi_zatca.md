# Saudi Arabia — VAT & ZATCA E-Invoicing Guide

## Overview
Saudi Arabia introduced 5% VAT in January 2018, increased to 15% in July 2020. ZATCA (Zakat, Tax and Customs Authority) mandates e-invoicing through the FATOORAH program.

## Tax Rate
- **Standard rate: 15%**
- **Zero-rated (0%)**: Exports, international transport, medicines/medical equipment (specific list), investment metals (gold, silver, platinum 99%+ purity)
- **Exempt**: Financial services, residential property rental, local passenger transport, life insurance

## E-Invoicing (FATOORAH)
### Phase 1 — Generation (since Dec 4, 2021)
- All VAT-registered taxpayers must generate e-invoices
- Must be generated in electronic format (no handwritten)
- Must include QR code (simplified invoices)

### Phase 2 — Integration (rolling out since Jan 1, 2023)
- Real-time reporting/clearance with ZATCA systems
- Tax invoices: clearance required (real-time validation before issuance)
- Simplified invoices: reporting within 24 hours
- Phased rollout by revenue threshold (currently >SAR 7M)

## Invoice Types
### Tax Invoice (B2B)
Required fields:
1. Seller name, address, VAT registration number
2. Buyer name, address, VAT registration number
3. Invoice number (sequential)
4. Invoice date and time of issue
5. Date of supply (if different)
6. Description of goods/services
7. Quantity and unit price
8. Discount amount (if any)
9. VAT rate per line item
10. VAT amount per line item
11. Total (excluding VAT)
12. Total VAT
13. Total (including VAT)
14. QR code (Phase 2)
15. Cryptographic stamp (Phase 2)
16. UUID
17. Previous invoice hash (Phase 2)

### Simplified Invoice (B2C)
For transactions ≤SAR 1,000 (or any B2C):
- Seller info + VAT number
- Invoice date
- Description
- Total including VAT
- QR code (mandatory — contains seller VAT, timestamp, total, VAT amount)

## QR Code Contents (TLV encoded)
1. Seller name
2. VAT registration number
3. Invoice timestamp
4. Invoice total (with VAT)
5. VAT amount
6. Hash of XML invoice
7. ECDSA digital signature
8. Public key

## Format
- XML (UBL 2.1 based)
- PDF/A-3 with embedded XML
- Must comply with ZATCA technical specifications

## Common Pitfalls
- Missing QR code on simplified invoices
- Not integrating with ZATCA for Phase 2 (penalties up to SAR 50,000)
- Incorrect VAT grouping (related entities)
- Not applying zero-rate to qualifying exports
- Backdating invoices (timestamp validation in Phase 2)
