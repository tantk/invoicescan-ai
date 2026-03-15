# Chile — IVA (Impuesto al Valor Agregado) Guide

## Overview

Chile's Value Added Tax, known as IVA (Impuesto al Valor Agregado), is a consumption tax levied on the sale of goods, provision of services, and imports. It is administered by the **SII** (Servicio de Impuestos Internos), Chile's Internal Revenue Service. Chile operates a single-rate system with no reduced rates — only standard, zero-rated, and exempt categories exist. Electronic invoicing has been mandatory for all taxpayers since 2018, with B2C coverage added in 2021.

## Tax Rates

- **Standard rate: 19%** — applies to most goods and services
- **Reduced rate:** None — Chile does not apply reduced IVA rates
- **Zero-rated (0%)**:
  - Exports of goods
  - Export of services (when meeting specific SII criteria)
  - International transport services
- **Exempt**:
  - Education services (primary, secondary, university)
  - Health services provided by public or accredited institutions
  - Public transport (urban buses, metro)
  - Residential property leases (unfurnished)
  - Cultural and sporting events (under certain conditions)
  - Insurance premiums (life insurance, health insurance)
  - Interest on financial instruments
  - Certain imported capital goods under investment incentive regimes
  - Sales by small-scale farmers under simplified regime

## Tax ID Format

**RUT (Rol Único Tributario)**

- **Format:** 8 digits followed by a hyphen and a check character (digit 0-9 or letter "K")
- **Pattern:** `NNNNNNNN-X` (where X is a digit or "K")
- **Check digit:** Calculated using the Modulo 11 algorithm
- **Example:** `76123456-K`
- **Verification:** [SII RUT Verification](https://zeus.sii.cl/cvc/stc/stc.html)

## Invoice Requirements

1. Document title clearly identifying the type (Factura Electrónica, Factura Exenta, Boleta, etc.)
2. Issuer's legal name (razón social)
3. Issuer's RUT number
4. Issuer's commercial name (nombre de fantasía, if applicable)
5. Issuer's registered address and economic activity
6. SII regional office where the issuer is registered
7. Invoice number (sequential, assigned by the SII through CAF — Código de Autorización de Folios)
8. Date of issue
9. Buyer's legal name and RUT (for Facturas; not required for Boletas to final consumers)
10. Buyer's address and economic activity
11. Detailed description of goods or services
12. Quantity and unit of measure
13. Unit price (net of IVA)
14. Discount amounts (if applicable)
15. Net taxable amount
16. IVA rate (19%)
17. IVA amount
18. Total amount including IVA
19. SII Electronic Stamp (Timbre Electrónico SII) — digital signature and barcode
20. Payment terms and conditions

## E-Invoicing

- **Status:** Mandatory for all taxpayers (B2B since 2018, B2C since 2021).
- **Format:** Electronic Tax Documents (DTE — Documento Tributario Electrónico) in XML format.
- **Platform:** SII manages the authorization and validation system. Invoices must be submitted to SII for validation before being sent to the buyer.
- **Validation model:** Pre-clearance — invoices are transmitted to SII first, validated, and only then delivered to the recipient in XML format.
- **Document types:**
  - Factura Electrónica (standard invoice)
  - Factura Electrónica Exenta (exempt invoice)
  - Boleta Electrónica (consumer receipt)
  - Nota de Crédito Electrónica (credit note)
  - Nota de Débito Electrónica (debit note)
  - Guía de Despacho Electrónica (delivery note)
  - Factura de Exportación Electrónica (export invoice)
- **Folio authorization (CAF):** Businesses must request authorized folio ranges from SII before issuing invoices.
- **Retention:** DTEs must be electronically archived for 6 years, ensuring integrity, access, and traceability.

## Key Rules

- **Single rate simplicity:** Chile's single 19% rate reduces classification complexity compared to multi-rate systems, but correct identification of exempt supplies remains critical.
- **Pre-clearance model:** Unlike post-audit models, every invoice must be validated by SII before delivery to the buyer. Businesses must maintain reliable connectivity.
- **Boletas vs. Facturas:** Boletas are issued to final consumers and do not require buyer identification. Facturas are issued to businesses and require full buyer details. Using the wrong document type affects the buyer's ability to claim input tax credits.
- **Credit and debit notes:** Any correction to an invoice must be documented with an electronic credit note or debit note referencing the original invoice.
- **Withholding on services:** Certain services are subject to IVA withholding by the buyer, particularly construction and temporary staffing services.
- **Digital services by non-residents:** Non-resident providers of digital services to Chilean consumers must register for IVA and charge the 19% rate since 2020.
- **Monthly filing:** IVA returns (Formulario 29) must be filed and paid monthly by the 12th of the following month.

## Common Pitfalls

1. **Failing to request CAF folios in advance** — Running out of authorized folio numbers means you cannot issue invoices until new ones are obtained from SII, potentially halting business operations.
2. **Issuing a Boleta instead of a Factura (or vice versa)** — Boletas do not allow the buyer to claim input tax credits. Always issue Facturas when selling to other registered taxpayers.
3. **Not submitting DTEs to SII before delivery** — Chile uses a pre-clearance model. Sending an invoice to the buyer before SII validation renders it invalid.
4. **Incorrectly classifying exempt vs. taxable supplies** — Some services that appear similar have different tax treatments (e.g., furnished vs. unfurnished property leases).
5. **Missing the monthly filing deadline** — Late filing of Formulario 29 triggers automatic interest (1.5% per month) and penalties that escalate rapidly.
6. **Ignoring export invoice requirements** — Export invoices (Factura de Exportación) have additional mandatory fields including port of departure, carrier details, and foreign currency specification.
7. **Failure to archive DTEs for 6 years** — SII may audit up to 6 years back. Inability to produce original DTEs results in denial of deductions and potential fines.
8. **Not issuing electronic delivery notes (Guías de Despacho)** — When goods are delivered before invoicing, an electronic Guía de Despacho is required. Transporting goods without one can result in fines and seizure.
