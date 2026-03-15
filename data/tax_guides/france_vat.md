# France — TVA (Taxe sur la Valeur Ajoutee) & Factur-X E-Invoicing Guide

## Overview
France's VAT, known as TVA (Taxe sur la Valeur Ajoutee), is administered by the Direction Generale des Finances Publiques (DGFiP). France is implementing mandatory B2B e-invoicing and e-reporting starting September 1, 2026, as part of a major reform to modernize VAT collection, reduce fraud, and automate tax compliance. The system operates through certified Partner Dematerialization Platforms (Plateformes de Dematerialisation Partenaires / PDP) alongside the government's public invoicing portal Chorus Pro.

## Tax Rates
- **Standard rate: 20%** (taux normal)
- **Intermediate rate: 10%** (taux intermediaire) — restaurant meals (on-premises), prepared food takeaway, passenger transport, renovation of residential housing, accommodation, admission to cultural events (cinema, fairs), firewood, agricultural products not for food
- **Reduced rate: 5.5%** (taux reduit) — most food products, water supply, gas and electricity (subscriptions), books and e-books, cinema tickets, home energy renovation works, equipment for disabled persons, school meals, sanitary protection products
- **Super-reduced rate: 2.1%** (taux particulier) — reimbursable medicines, press publications (print and digital), first 140 performances of new theatrical/circus works, television license (contribution a l'audiovisuel public)
- **Zero-rated (0%)**: Intra-community supplies, exports
- **Exempt** (no TVA, no input credit): Financial and insurance services, medical services, education, residential rental, certain cultural activities by public bodies

## Tax ID Format
- **Numero de TVA intracommunautaire** (Intra-community VAT number):
  - Format: `FR` + 2-character key + 9-digit SIREN: `FRXX123456789`
  - The 2-character key can be two digits, two letters, or one of each (excluding O and I)
  - Example: `FR40303265045`
- **SIREN**: 9-digit company identification number (first 8 random + 1 check digit)
  - Example: `303265045`
- **SIRET**: 14 digits = SIREN (9 digits) + NIC (5-digit establishment code)
  - Example: `30326504500028`
  - The SIRET identifies a specific establishment; SIREN identifies the legal entity
- Verify at: https://ec.europa.eu/taxation_customs/vies/ (EU VIES system) or https://www.sirene.fr

## Invoice Requirements
1. Invoice date (date de facture)
2. Unique sequential invoice number (numero de facture)
3. Supplier's full name/business name and address
4. Supplier's SIREN or SIRET number
5. Supplier's intra-community VAT number (numero de TVA)
6. Buyer's full name/business name and address
7. Buyer's intra-community VAT number (for B2B)
8. Buyer's SIREN (required under 2026 e-invoicing mandate)
9. Date of supply or service completion (if different from invoice date)
10. Description of goods or services (nature, brand, reference)
11. Quantity and unit price (net of tax)
12. Any discounts, rebates, or price reductions
13. Net amount per VAT rate (base hors taxe)
14. VAT rate(s) applied (20%, 10%, 5.5%, 2.1%)
15. VAT amount per rate
16. Total amount including VAT (montant TTC)
17. Payment terms and due date
18. Late payment penalty rate and fixed recovery fee (EUR 40)
19. For reverse charge: "Autoliquidation" notation
20. For intra-EU: both parties' VAT IDs and reference to VAT exemption

## E-Invoicing — Factur-X / Chorus Pro / PDP
### September 2026 Mandate
France's mandatory B2B e-invoicing reform launches in two phases:

**Phase 1 — September 1, 2026:**
- All French VAT-registered businesses must be able to **receive** e-invoices
- Large enterprises (grandes entreprises) and mid-size enterprises (entreprises de taille intermediaire / ETI) must **issue** e-invoices

**Phase 2 — September 1, 2027:**
- Small enterprises (PME) and micro-enterprises must **issue** e-invoices

### Accepted Formats
Three structured formats are permitted, all compliant with EN 16931:
- **Factur-X** (hybrid PDF/A-3 with embedded XML CII) — the Franco-German standard, also known as ZUGFeRD in Germany
- **UBL** (Universal Business Language) XML
- **CII** (Cross-Industry Invoice) XML

Traditional paper invoices and standard PDFs are **not valid** for B2B domestic transactions once the mandate takes effect.

### Infrastructure
- **Chorus Pro**: The government-operated public portal (Portail Public de Facturation / PPF) — serves as the central hub and default platform
- **PDP (Plateformes de Dematerialisation Partenaires)**: Certified private platforms that can transmit, receive, and validate e-invoices on behalf of businesses. The DGFiP certifies and audits PDPs.
- **OD (Operateur de Dematerialisation)**: Service providers that help businesses prepare invoices but must route them through a PDP or Chorus Pro

### E-Reporting
Alongside e-invoicing, France mandates **e-reporting** for:
- B2C transactions (domestic)
- Cross-border B2B transactions (both sales and purchases)
- Payment data for B2C transactions

E-reporting data is transmitted to the tax authority via PDP or Chorus Pro, enabling near-real-time VAT monitoring.

### Factur-X Technical Details
- **Profiles**: Minimum, Basic, Basic WL, EN 16931 (Comfort), Extended
- **Format**: PDF/A-3 with embedded XML (CII syntax)
- **Human-readable AND machine-readable**: Allows visual rendering plus structured data extraction
- **EN 16931 compliant**: The EN 16931 (Comfort) profile meets the European standard
- **Interoperable**: Same format as German ZUGFeRD — cross-border Franco-German invoicing uses identical technical specifications

## Key Rules
- **Registration threshold**: EUR 91,900 for goods, EUR 36,800 for services (2026) — below threshold, franchise en base de TVA (VAT exemption) applies
- **Filing frequency**: Monthly CA3 returns (by the 19th-24th depending on company type); quarterly for businesses with annual VAT below EUR 4,000
- **Annual declaration**: CA12 for simplified regime businesses
- **Reverse charge (autoliquidation)**: Applies to services from non-EU suppliers, construction subcontracting, intra-community acquisitions
- **Domestic reverse charge**: Mandatory for construction subcontracting and energy certificates
- **Input VAT recovery**: Must be supported by valid e-invoices; 2-year statute of limitations for claiming missed deductions
- **Penalties for non-compliance with e-invoicing**: EUR 15 per invoice (capped at EUR 15,000 per year) for failure to issue in the correct format; EUR 250 per missing e-report (capped at EUR 15,000 per year)

## Common Pitfalls
1. **Not ready to receive e-invoices by September 2026**: ALL businesses must accept e-invoices from day one, even if they don't yet need to issue them
2. **Confusing SIREN and SIRET**: SIREN (9 digits) identifies the legal entity; SIRET (14 digits) identifies a specific establishment — e-invoicing requires both
3. **Using wrong Factur-X profile**: The Minimum profile does not satisfy EN 16931 requirements; use at least the EN 16931 (Comfort) profile for compliance
4. **Forgetting e-reporting for B2C and cross-border**: The mandate covers both e-invoicing (B2B domestic) and e-reporting (B2C and international) — many businesses overlook the reporting obligation
5. **Mixing up rates**: France has four non-zero rates (20%, 10%, 5.5%, 2.1%) — misapplying rates is common, especially for food (restaurant vs. takeaway vs. grocery)
6. **Late payment penalty omission**: French invoices must include the late payment interest rate and the EUR 40 fixed recovery indemnity — omission is a compliance violation
7. **PDP vs. OD confusion**: An OD (service provider) cannot transmit directly to the tax authority — invoices must go through a certified PDP or Chorus Pro
8. **Not including buyer's SIREN**: The 2026 mandate requires the buyer's SIREN on e-invoices, which many legacy systems do not capture
