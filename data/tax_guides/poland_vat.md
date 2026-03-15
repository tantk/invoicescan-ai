# Poland — VAT (Podatek od Towarow i Uslug / PTU) & KSeF E-Invoicing Guide

## Overview
Poland's VAT system follows EU VAT Directives and is administered by the National Revenue Administration (Krajowa Administracja Skarbowa / KAS). Poland is implementing one of Europe's most ambitious mandatory e-invoicing systems — the National e-Invoice System (Krajowy System e-Faktur / KSeF), which becomes mandatory in 2026. KSeF represents a Continuous Transaction Controls (CTC) clearance model where structured invoices must pass through a government platform before being considered legally valid.

## Tax Rates
- **Standard rate: 23%**
- **Reduced rate: 8%** (residential construction and renovation up to 150 sqm, certain medical devices, restaurant and catering services, cultural/sports/recreation services, hotel accommodation, selected food products)
- **Reduced rate: 5%** (basic foodstuffs — meat, dairy, bread, cereals, juices; books and e-books; periodicals; certain hygiene products)
- **Zero-rated (0%)**: Intra-community supplies, exports of goods, international transport services, rescue vessels and lifeboats used at sea
- **Exempt** (no VAT, no input credit): Financial and insurance services, education, healthcare, postal services, residential rental, cultural services by public institutions

## Tax ID Format
- **NIP (Numer Identyfikacji Podatkowej)**: 10 digits, format `XXX-XXX-XX-XX` or `XXXXXXXXXX`
  - Example: `1234567890`
- **EU VAT Number**: `PL` + NIP (10 digits): `PL1234567890`
- **NIP-2 form**: Used by foreign businesses to apply for a Polish NIP
- Verify at: https://ppuslugi.mf.gov.pl (Polish Tax Portal) or EU VIES system

## Invoice Requirements
1. Invoice date (data wystawienia)
2. Sequential invoice number (numer faktury)
3. Supplier's full name and address
4. Supplier's NIP (tax ID)
5. Buyer's full name and address
6. Buyer's NIP (for B2B transactions)
7. Date of supply or payment (if different from invoice date)
8. Description of goods or services
9. Quantity and unit of measure
10. Unit price (net)
11. Discounts or rebates (if applicable)
12. Net amount per VAT rate
13. VAT rate (23%, 8%, 5%, 0%, ZW for exempt)
14. VAT amount per rate
15. Gross total amount
16. For reverse charge: notation "odwrotne obciążenie"
17. For intra-EU: both parties' VAT IDs and reference to exemption
18. Currency (if not PLN, exchange rate and PLN equivalent must be shown)

## E-Invoicing — KSeF (Krajowy System e-Faktur)
### Overview
KSeF is Poland's mandatory national e-invoicing platform implementing a CTC clearance model. Structured e-invoices in XML format are transmitted through KSeF, validated, and assigned a unique identification number before becoming legally valid.

### Mandatory Timeline (KSeF 2.0)
- **February 1, 2026**: Mandatory for large taxpayers (prior-year gross revenue exceeding PLN 200 million)
- **April 1, 2026**: Mandatory for all other VAT-registered businesses
- **January 1, 2027**: Mandatory for micro-taxpayers (monthly sales not exceeding PLN 10,000) and for B2C invoices upon buyer request
- **Grace period**: February 2026 through December 2026 — no financial penalties for KSeF errors during implementation phase

### Technical Details
- **Format**: FA(3) XML schema — structured e-invoice format defined by the Ministry of Finance
- **Transmission**: Via KSeF API, web portal, or authorized tax application
- **Invoice types in scope**: B2B domestic transactions, zero-rated supplies, exempt supplies — all must use KSeF
- **Out of scope**: B2C receipts/tickets (unless buyer requests a KSeF invoice), simplified invoices, fiscal receipts
- **Invoice identification**: Each invoice receives a unique KSeF number upon acceptance
- **Archiving**: KSeF stores invoices for 10 years; businesses are not required to maintain separate archives for KSeF-processed invoices
- **Cross-border**: Invoices for cross-border transactions are not required to go through KSeF but may be submitted voluntarily

### Penalties (from January 1, 2027)
- Failure to issue via KSeF: up to 100% of the VAT amount shown on the invoice
- Issuing invoices outside KSeF: the invoice is not considered a valid VAT invoice

## Key Rules
- **Registration threshold**: Annual turnover below PLN 200,000 — exempt from VAT (can opt in voluntarily)
- **Filing frequency**: Monthly VAT returns (JPK_V7M) due by the 25th of the following month; quarterly filing allowed for small taxpayers
- **JPK (Standard Audit File)**: Mandatory — all VAT records submitted electronically in JPK format alongside returns
- **Split payment mechanism (MPP)**: Mandatory for invoices over PLN 15,000 for specified goods/services (electronics, steel, construction, fuel)
- **Reverse charge**: Applies to services received from non-resident suppliers
- **SAF-T reporting**: Poland uses the JPK_V7M/JPK_V7K format combining VAT return and SAF-T in one filing
- **White list verification**: Before paying invoices over PLN 15,000, verify the supplier's bank account on the "White List" (Wykaz podatnikow VAT) — payments to unverified accounts result in lost input VAT deduction

## Common Pitfalls
1. **Missing the KSeF deadline**: Different go-live dates for large vs. standard taxpayers (February vs. April 2026)
2. **Sending PDF invoices for B2B after KSeF mandate**: Paper/PDF invoices are no longer legally valid for domestic B2B transactions once KSeF is mandatory
3. **White List non-compliance**: Paying invoices >PLN 15,000 to a bank account not on the White List — input VAT deduction denied
4. **Split payment errors**: Not using the split payment mechanism for mandatory categories results in penalties
5. **JPK filing mistakes**: Errors in the JPK_V7M file trigger automated queries from the tax authority
6. **Incorrect VAT rate on food products**: Confusion between 5% and 8% rates for food items depending on processing level
7. **Cross-border KSeF confusion**: Assuming cross-border invoices must go through KSeF (they do not, but domestic B2B always must)
8. **Not preparing systems for FA(3) schema**: The KSeF XML schema has expanded fields; legacy invoicing systems may not support all required data elements
