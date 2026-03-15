# Sweden — Moms (Mervardesskatt) Guide

## Overview
Sweden's VAT, known as Moms (Mervardesskatt), is administered by the Skatteverket (Swedish Tax Agency). Sweden has one of the highest standard VAT rates in the EU at 25%. The system follows EU VAT Directives with Swedish-specific implementations. Sweden uses the Peppol network extensively for e-invoicing, with B2G e-invoicing already mandatory and broader e-invoicing mandates under development as part of the EU ViDA (VAT in the Digital Age) initiative.

## Tax Rates
- **Standard rate: 25%** (normalskattesats)
- **Reduced rate: 12%** (reducerad skattesats) — food and non-alcoholic beverages (restaurant and catering), hotel and camping accommodation, minor repair services (bicycles, shoes, leather goods, clothing, household linen)
- **Reduced rate: 6%** (lag skattesats) — books (print and e-books), newspapers and magazines, admission to cultural events (concerts, theaters, museums, zoos), admission to sporting events, passenger transport, copyrights for literary/artistic works
- **Zero-rated (0%)**: Exports, intra-community supplies, international transport, prescription medicines
- **Exempt** (momsfritt, no input credit): Financial and insurance services, healthcare, education, residential rental, postal services (universal), certain cultural services by public institutions, lottery and gambling

### 2026 Rate Changes
- **Temporary food rate reduction**: From **April 1, 2026 to December 31, 2027**, most food products will be taxed at **6% instead of 12%** — a temporary measure to reduce food costs
- **Dance events**: From **July 1, 2026**, admission to certain dance events reduced from 25% to **6%**
- **Anti-fraud measures**: From **July 1, 2026**, Skatteverket gains expanded powers to deregister VAT registrations, void VIES numbers, and temporarily withhold VAT refunds if fraud is suspected

## Tax ID Format
- **Momsregistreringsnummer** (VAT registration number):
  - Format: `SE` + 12 digits: `SE123456789001`
  - First 10 digits: organisationsnummer (organization number)
  - Last 2 digits: `01` for the main VAT registration (can be `02`, `03`, etc. for additional registrations)
  - Example: `SE556012345601`
- **Organisationsnummer** (Organization number): 10 digits, format `XXXXXX-XXXX`
  - For companies: first digit is 5 or greater
  - For sole traders (enskild firma): based on personal identity number (personnummer)
  - Example: `556012-3456`
- Verify at: https://ec.europa.eu/taxation_customs/vies/ (EU VIES) or https://www.skatteverket.se

## Invoice Requirements
1. Invoice date (fakturadatum)
2. Unique sequential invoice number (fakturanummer)
3. Supplier's full name and address
4. Supplier's organisationsnummer
5. Supplier's momsregistreringsnummer (VAT number)
6. **F-skatt notation**: Statement that the supplier is approved for F-skatt (F-skattsedel) — indicates the supplier handles their own tax obligations
7. Buyer's full name and address
8. Buyer's VAT number (for B2B and intra-EU transactions)
9. Date of supply (leveransdatum) if different from invoice date
10. Description of goods or services
11. Quantity and unit price (net)
12. Net amount per Moms rate
13. Moms rate(s) applied (25%, 12%, 6%)
14. Moms amount per rate
15. Total amount including Moms
16. For exemptions: reference to the applicable Swedish or EU provision
17. For reverse charge: "Omvand skattskyldighet" notation
18. For intra-EU: both parties' VAT IDs and reference to exemption
19. Payment terms and bank details (bankgiro or plusgiro number)

### Simplified Invoice (forenklad faktura, <=4,000 SEK including Moms)
- Supplier name and address
- Supplier organisationsnummer
- Invoice date
- Description of goods/services
- Total amount including Moms
- Moms rate

## E-Invoicing
- **B2G**: Mandatory since April 1, 2019 (Act 2018:1277) — all invoices to Swedish public sector entities must be structured electronic invoices compliant with EN 16931
- **Format**: Peppol BIS Billing 3.0 — adopted as-is, without national modifications (Swedish CIUS)
- **B2B**: Not yet mandatory — electronic invoices widely used but paper/PDF still valid
- **Peppol**: Sweden is one of the most advanced Peppol adopters in Europe; Peppol network is the standard delivery channel for B2G and increasingly for B2B
- **SFTI (Single Face To Industry)**: Swedish standards body that manages procurement and invoicing standards, recommending Peppol BIS
- **ViDA implementation**: In February 2026, the Ministry of Finance appointed a commissioner to examine how EU ViDA requirements should be implemented in Swedish law; findings due by November 30, 2027. Mandatory intra-EU B2B e-invoicing expected by July 1, 2030.
- **Archiving**: Invoices must be stored for **7 years** (plus the current year, so effectively up to 8 calendar years)

## Key Rules
- **Registration threshold**: SEK 120,000 annual taxable turnover for domestic businesses. Non-resident businesses must register from the first taxable supply in Sweden (no threshold).
- **Filing frequency**: Monthly, quarterly, or annually — assigned by Skatteverket based on estimated annual turnover
  - Annual turnover > SEK 40 million: monthly
  - SEK 1 million - 40 million: quarterly (or monthly if elected)
  - Below SEK 1 million: annually
- **Tax point**: Generally the earlier of goods delivery/service completion or invoice issuance
- **Reverse charge (omvand skattskyldighet)**: Applies to services from non-resident suppliers, construction services (subcontractor to main contractor), and certain goods (gold, emission allowances)
- **F-skatt**: Suppliers approved for F-skatt handle their own income tax — buyers are not liable for withholding. The F-skatt notation is crucial on invoices.
- **ROT and RUT deductions**: Tax deductions for household services (RUT: cleaning, gardening, childcare) and renovation/construction work (ROT). The deduction is made directly on the invoice — buyer pays less, supplier claims the remainder from Skatteverket.
- **Intrastat**: Reporting required for intra-EU goods trade above thresholds
- **EC Sales List**: Required for intra-EU supplies of goods and services

## Common Pitfalls
1. **Temporary food rate**: Failing to apply the temporary 6% rate on food from April 1, 2026, or continuing to apply it after December 31, 2027
2. **F-skatt notation missing**: Omitting the F-skatt statement means the buyer must withhold 30% preliminary tax — suppliers should always confirm and display their F-skatt status
3. **Mixing up 12% and 6% items**: Restaurants serve food (12%) and may also sell books or tickets (6%) — each rate must be shown separately
4. **B2G invoicing format**: Sending PDF invoices to public sector entities — only structured electronic invoices (Peppol BIS Billing 3.0) are accepted since April 2019
5. **ROT/RUT errors**: Incorrectly calculating the deduction amount or applying it to ineligible services — Skatteverket audits these claims actively
6. **Non-resident registration**: Foreign businesses making taxable supplies in Sweden must register even for one-off transactions — no minimum threshold applies
7. **Organisationsnummer on invoice**: Using only the VAT number without the organisationsnummer — both are required on Swedish invoices
8. **Quarterly vs. monthly filing**: Businesses growing past SEK 40 million turnover must switch to monthly filing — missing this transition results in late filing penalties
