# Netherlands — BTW (Belasting over de Toegevoegde Waarde) Guide

## Overview
The Netherlands' VAT, known as BTW (Belasting over de Toegevoegde Waarde), is administered by the Belastingdienst (Dutch Tax and Customs Administration). The Netherlands follows EU VAT Directives and has a straightforward two-rate system (standard and reduced) with several notable rate changes taking effect in 2026, particularly for the accommodation sector.

## Tax Rates
- **Standard rate: 21%** (algemeen tarief)
- **Reduced rate: 9%** (verlaagd tarief) — food and non-alcoholic beverages, water supply, medicines, medical aids, books (including e-books), newspapers and magazines, online publications, hairdressing, painting and plastering of residential homes (older than 2 years), cultural events and admissions (museums, theaters, cinemas), sports facilities, camping accommodation, passenger transport, agricultural products, cut flowers and plants, renovation of residential housing
- **Zero-rated (0%)**: Intra-community supplies, exports, international transport of goods, services to entrepreneurs in other EU countries, work on goods for export to non-EU countries, international air and water passenger transport
- **Exempt** (vrijgesteld, no input credit): Education, healthcare, childcare, insurance, banking and financial services, residential property rental, postal services (universal), funeral services, sports services by non-profit organizations

### 2026 Rate Changes
- **Overnight accommodation**: Increased from 9% to 21% effective January 1, 2026 (hotels, B&Bs, hostels, holiday parks — but **camping stays at 9%**)
- **Culture, sports, and media**: Remain at 9% — a previously planned increase to 21% was repealed
- **Digital VAT refunds**: From January 1, 2026, VAT refunds to non-EU customers must be processed digitally

## Tax ID Format
- **BTW-identificatienummer** (VAT identification number):
  - Format: `NL` + 9 digits + `B` + 2 digits: `NL123456789B01`
  - The "B" separates the base number from the sub-number
  - Example: `NL004495445B01`
- **Omzetbelastingnummer** (turnover tax number): Used domestically, same structure without the NL prefix
- **KVK number** (Kamer van Koophandel / Chamber of Commerce): 8-digit registration number — not the same as BTW number but often referenced alongside it
- Verify at: https://ec.europa.eu/taxation_customs/vies/ (EU VIES)

## Invoice Requirements
1. Invoice date (factuurdatum)
2. Unique sequential invoice number (factuurnummer)
3. Supplier's full name and address
4. Supplier's BTW-identificatienummer (VAT number)
5. Buyer's full name and address
6. Buyer's BTW-identificatienummer (for B2B and intra-EU)
7. Date of supply (if different from invoice date)
8. Description of goods or services
9. Quantity and nature of goods, or extent of services
10. Unit price (net of BTW)
11. Net amount per BTW rate
12. BTW rate(s) applied (21%, 9%, or 0%)
13. BTW amount per rate
14. Total amount including BTW
15. Breakdown by rate if multiple rates apply on one invoice
16. For exemptions: reference to the applicable legal provision
17. For reverse charge: "BTW verlegd" notation
18. For intra-EU: both parties' VAT IDs and reference to exemption
19. For credit notes: reference to the original invoice number

**Timing**: Invoices must be sent no later than the **15th of the month** following the month in which the supply took place.

## E-Invoicing
- **B2G**: Mandatory since 2017 — all invoices to Dutch government entities must be in structured electronic format (UBL or Peppol BIS)
- **B2B**: Not yet mandatory — electronic invoices are accepted and encouraged but paper/PDF remains valid
- **Peppol**: Widely adopted for B2G; many Dutch businesses use the Peppol network for B2B as well
- **Format**: UBL-OEBL (based on UBL 2.1) is the dominant standard in the Netherlands
- **Simplerinvoicing**: Dutch e-invoicing network initiative, now largely merged with Peppol
- **ViDA**: Under the EU VAT in the Digital Age (ViDA) directive, mandatory B2B e-invoicing for intra-EU transactions expected by 2030; the Netherlands is monitoring this for domestic implementation timeline
- **Archiving**: Invoices must be stored for **7 years** (10 years for invoices related to real estate)

## Key Rules
- **Registration threshold**: None for domestic businesses — all businesses performing taxable activities must register. Small businesses scheme (kleineondernemersregeling / KOR) available if annual turnover is below EUR 20,000 — exempt from charging BTW but cannot deduct input BTW
- **Filing frequency**: Monthly or quarterly BTW returns depending on business size (assigned by Belastingdienst); annual return if very low turnover
- **Payment deadline**: BTW return and payment due by the last day of the month following the reporting period
- **Reverse charge**: Applies to services from non-resident suppliers, certain goods (e.g., mobile phones, game consoles above EUR 10,000), and construction subcontracting
- **Fiscal unity (fiscale eenheid)**: Related Dutch businesses can form a fiscal unity and be treated as a single VAT taxpayer — transactions within the group are disregarded for VAT
- **Import VAT deferral (Article 23 license)**: Businesses with an Article 23 license can defer import VAT to the VAT return instead of paying at customs — significant cash flow advantage
- **Margin scheme (margeregeling)**: For second-hand goods, art, antiques, and collector's items — VAT charged only on the profit margin
- **Intrastat**: Reporting required for intra-EU trade in goods above thresholds (arrival: EUR 1,000,000; dispatch: EUR 1,200,000 for 2026)

## Common Pitfalls
1. **Accommodation rate change**: Applying the old 9% rate to hotel stays after January 1, 2026 — the rate is now 21% (except camping, which remains 9%)
2. **Fiscal unity misunderstandings**: Transactions between fiscal unity members should not include BTW, but transactions with external parties require BTW on the full amount — errors in group billing are common
3. **Article 23 license not obtained**: Import-heavy businesses missing the significant cash flow benefit of deferring import VAT to the return
4. **Reverse charge notation missing**: Forgetting "BTW verlegd" on reverse charge invoices — buyer cannot self-assess without the notation
5. **Mixed supplies**: Incorrectly applying a single rate to a supply that includes both 21% and 9% components — must split and show each rate separately
6. **KOR exit**: Small businesses that exceed the EUR 20,000 threshold mid-year must deregister from KOR and start charging BTW retroactively from the start of the next quarter
7. **7-year retention confusion**: Some businesses unaware that real estate-related invoices must be kept for 10 years, not the standard 7
8. **Intra-EU services**: Forgetting to file the EC Sales List (Opgaaf ICL) for services supplied to VAT-registered businesses in other EU member states
