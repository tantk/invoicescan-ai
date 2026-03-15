# Invoice Terms — Complete Reference Guide

Now I have all the research. Here is the exhaustive reference:

---

# EXHAUSTIVE INVOICE FIELD REFERENCE -- Beyond the Basics

This covers every specialized term, code, reference, and standard that can appear on an invoice, organized for building a comprehensive invoice AI agent.

---

## 1. DELIVERY / SHIPPING TERMS

### 1.1 Incoterms 2020 (ICC -- 11 Rules)

**Multimodal (any transport):**
| Term | Name | Seller Responsibility |
|------|------|----------------------|
| EXW | Ex Works | Goods available at seller's premises. Minimum seller obligation. |
| FCA | Free Carrier | Delivered to carrier at named place, export cleared. Two variants: (a) seller's premises, (b) other location. |
| CPT | Carriage Paid To | Seller pays carriage to destination. Risk transfers at handover to first carrier. |
| CIP | Carriage and Insurance Paid To | Like CPT + seller must buy maximum insurance (Institute Cargo Clauses A). |
| DAP | Delivered at Place | Delivered to buyer's location, ready for unloading. Seller bears all risk until arrival. |
| DPU | Delivered at Place Unloaded | Like DAP but seller also unloads. Replaced DAT from Incoterms 2010. |
| DDP | Delivered Duty Paid | Seller handles everything including import clearance, duties, and VAT/GST. Maximum seller obligation. |

**Sea/Inland Waterway Only:**
| Term | Name | Seller Responsibility |
|------|------|----------------------|
| FAS | Free Alongside Ship | Goods placed alongside vessel at port of loading. |
| FOB | Free on Board | Goods loaded on board vessel. Risk transfers when goods cross ship's rail. Not for containers -- use FCA. |
| CFR | Cost and Freight | Seller pays freight to destination port. Risk transfers at loading. |
| CIF | Cost, Insurance and Freight | Like CFR + seller buys minimum insurance (Institute Cargo Clauses C). |

**Agent handling:** Parse "Incoterms" or "Incoterms 2020" followed by a three-letter code and a named place (e.g., "CIF Shanghai" or "FOB Los Angeles"). Validate that sea-only terms (FAS, FOB, CFR, CIF) are not used with air or road freight.

### 1.2 FOB Variations (US Domestic / UCC Usage)

In US domestic trade, FOB has different meanings from Incoterms:

| Term | Meaning | Who Pays Freight | Who Bears Risk |
|------|---------|-----------------|----------------|
| FOB Shipping Point (FOB Origin) | Sale complete at seller's dock | Buyer | Buyer (from pickup) |
| FOB Destination | Sale complete at buyer's dock | Seller | Seller (until delivery) |
| FOB Shipping Point, Freight Prepaid | Seller prepays freight but risk transfers at origin | Seller pays, but adds to invoice | Buyer |
| FOB Shipping Point, Freight Collect | Buyer pays carrier directly | Buyer | Buyer |
| FOB Destination, Freight Prepaid | Seller pays and bears risk | Seller | Seller |
| FOB Destination, Freight Collect | Buyer pays carrier; seller bears risk until delivery | Buyer | Seller |
| FOB Destination, Freight Collect and Allowed | Buyer pays carrier; seller deducts freight from invoice | Net -- seller absorbs | Seller |

**Red flag:** If "FOB" appears without Incoterms context, determine whether it is UCC domestic or ICC international usage. The risk allocation is fundamentally different.

### 1.3 Freight Terms

| Term | Meaning |
|------|---------|
| Freight Prepaid | Shipper/seller has paid freight charges |
| Freight Collect | Consignee/buyer pays carrier at delivery |
| Freight Prepaid and Add | Seller pays freight then adds charge to invoice |
| Freight Prepaid/Collect Beyond | Seller prepays to a point; buyer pays the rest |
| Third-Party Freight | A party other than buyer or seller pays |
| Freight Allowed | Seller absorbs freight cost within product price |
| Freight Equalization | Seller charges freight as if shipping from a closer location to match competitors |

### 1.4 Shipping References on Invoices

- **Bill of Lading (B/L) number** -- critical for sea freight, proves shipment
- **Airway Bill (AWB) number** -- for air freight
- **CMR note number** -- road freight (Convention on the Contract for the International Carriage of Goods by Road)
- **Rail consignment note** -- CIM/SMGS formats
- **Shipping marks** -- identification marks on packages
- **Container number(s)** -- ISO 6346 format (4 letters + 7 digits)
- **Seal number(s)** -- tamper-evident seal identifiers
- **Packing list reference** -- separate document listing package contents
- **Vessel name / Voyage number** -- for ocean freight
- **Port of loading / Port of discharge**
- **Country of origin** -- where goods were manufactured

---

## 2. PAYMENT TERMS & METHODS

### 2.1 Net Terms

| Term | Meaning |
|------|---------|
| Due on Receipt / CIA (Cash in Advance) | Payment due immediately upon invoice receipt |
| Net 7 | Payment due in 7 days |
| Net 10 | Payment due in 10 days |
| Net 15 | Payment due in 15 days |
| Net 21 | Payment due in 21 days |
| Net 30 | Payment due in 30 days (most common) |
| Net 45 | Payment due in 45 days |
| Net 60 | Payment due in 60 days |
| Net 90 | Payment due in 90 days |
| Net 120 | Payment due in 120 days (extended terms) |

### 2.2 Early Payment Discount Notation

Format: **discount%/days Net total_days**

| Term | Meaning |
|------|---------|
| 1/10 Net 30 | 1% discount if paid within 10 days; full amount due in 30 |
| 2/10 Net 30 | 2% discount if paid within 10 days; full amount due in 30 |
| 2/10 Net 60 | 2% discount if paid within 10 days; full amount due in 60 |
| 3/7 Net 30 | 3% discount if paid within 7 days; full amount due in 30 |
| 2/15 Net 45 | 2% discount if paid within 15 days; full amount due in 45 |
| 3/10, 2/20, N/30 | Tiered: 3% in 10 days, 2% in 20 days, full in 30 |

**Validation rule:** The discount window must be shorter than the net period. The discount percentage should be reasonable (typically 0.5%--5%).

### 2.3 Date-Based Terms

| Term | Meaning |
|------|---------|
| EOM (End of Month) | Payment due at end of the month after invoice date. "Net 30 EOM" = 30 days after end of invoice month. |
| MFI (Month Following Invoice) | Payment due on a specific day of the month following invoice. "15 MFI" = due by the 15th of the next month. |
| ROG (Receipt of Goods) | Clock starts when buyer receives goods, not invoice date. "Net 30 ROG" = 30 days after goods received. |
| Prox / Proximo | Similar to EOM. "25th Prox" = due the 25th of next month. |
| COD (Cash on Delivery) | Payment due when goods arrive |
| CWO (Cash with Order) | Payment must accompany the order |
| CBS (Cash Before Shipment) | Payment required before goods are shipped |
| PIA (Payment in Advance) | Full payment before delivery |
| Accumulation Terms | Discounts applied when cumulative purchases reach a threshold over a period |
| Stage/Milestone Payments | Payment tied to completion of defined project phases |
| Progress Payments | Periodic payments based on percentage of work completed |

### 2.4 Payment Methods (UNCL 4461 Codes)

The UN/CEFACT UNCL 4461 code list defines 97+ payment means codes. Key ones for invoice processing:

| Code | Method | Notes |
|------|--------|-------|
| 1 | Instrument not defined | Unspecified |
| 10 | In cash | Physical cash |
| 20 | Cheque | Paper check |
| 21 | Banker's draft | Bank-issued draft |
| 23 | Bank cheque | Issued by banking establishment |
| 30 | Credit transfer | Wire transfer |
| 31 | Debit transfer | Debit-initiated transfer |
| 42 | Payment to bank account | Generic bank payment |
| 48 | Bank card | Generic card payment |
| 49 | Direct debit | Automatic pull payment |
| 50 | Payment by postgiro | Postal payment system |
| 54 | Credit card | Visa, Mastercard, etc. |
| 55 | Debit card | PIN-based card |
| 57 | Standing agreement | Pre-agreed payment mechanism |
| 58 | SEPA credit transfer | Euro area bank transfer |
| 59 | SEPA direct debit | Euro area direct debit |
| 60 | Promissory note | Written promise to pay |
| 68 | Online payment service | PayPal, etc. |
| 70 | Bill drawn by creditor on debtor | Bill of exchange |
| 97 | Clearing between partners | Netting / contra |
| ZZZ | Mutually defined | Custom arrangement |

ACH-specific codes (2-43) cover demand/savings CCD, CTP, CTX, PPD variants for US banking.

### 2.5 Retention / Holdback Terms

| Term | Meaning |
|------|---------|
| Retention Percentage | Typically 5--10% withheld from each progress payment |
| First Moiety | Half of retention released at Practical Completion |
| Second Moiety | Remainder released after Defects Liability Period (6--24 months) |
| Retention Bond | A bond that replaces cash retention, allowing full payment |
| Retention Release Certificate | Document authorizing release of retention funds |
| Practical Completion Certificate | Certifies the project is substantially complete |
| Defects Liability Period (DLP) | Contractual period (typically 6--24 months) for defect rectification |
| Performance Bond | Surety bond guaranteeing project completion (can replace retention) |
| Bank Guarantee for Retention | Bank-issued guarantee allowing early retention release |

### 2.6 Self-Billing and ERS

| Term | Meaning |
|------|---------|
| Self-Billing Invoice (SBI) | Buyer creates invoice on seller's behalf (UNCL 1001 code 389) |
| Evaluated Receipt Settlement (ERS) | Payment triggered by goods receipt, no supplier invoice required |
| Consignment Invoice | Invoice for goods held on consignment, billed upon consumption (code 395) |
| VMI (Vendor Managed Inventory) | Supplier manages stock levels; often paired with self-billing |

---

## 3. BANKING & FINANCIAL REFERENCES

### 3.1 Bank Account Identifiers

| Field | Format | Description |
|-------|--------|-------------|
| IBAN | Up to 34 alphanumeric | International Bank Account Number (ISO 13616). Starts with 2-letter country code + 2 check digits. |
| SWIFT/BIC | 8 or 11 characters | Bank Identifier Code (ISO 9362). Identifies the bank globally. |
| ABA Routing Number | 9 digits | US bank routing (Fedwire/ACH). |
| Sort Code | 6 digits | UK bank branch identifier |
| BSB Number | 6 digits | Australian bank-state-branch code |
| Account Number | Varies by country | Domestic account number |
| Bank Name | Free text | Name of the beneficiary's bank |
| Branch Name/Address | Free text | Physical branch location |

**Validation rules:** IBAN has built-in check digits (mod 97). SWIFT/BIC must match known BIC directory entries. ABA routing numbers have a checksum algorithm.

### 3.2 Trade Finance Instruments

| Instrument | Description | Invoice Reference |
|------------|-------------|-------------------|
| Letter of Credit (LC/DC) | Bank guarantee of payment upon presentation of conforming documents. Governed by UCP 600 (ICC). | LC number, issuing bank, LC date, expiry date |
| Standby Letter of Credit (SBLC) | Backup payment guarantee, activated only on default. | SBLC number, issuing bank |
| Bank Guarantee (BG) | Bank's commitment to pay if principal defaults. | BG number, amount, expiry |
| Documentary Collection -- D/P | Documents released to buyer against payment. "Documents against Payment." | Collection reference, remitting bank |
| Documentary Collection -- D/A | Documents released against acceptance of a time draft. "Documents against Acceptance." | Draft maturity date, accepting bank |
| Bill of Exchange | Order from creditor to debtor to pay a specified sum. Can be at sight or time draft. | Draft number, maturity, drawee |
| Promissory Note | Debtor's written promise to pay. | Note number, maturity date |
| Forfaiting | Purchase of receivables at a discount, without recourse. | Forfaiting agreement reference |
| Trade Credit Insurance | Insurance against buyer default. | Policy number, insurer, coverage limit |

### 3.3 SWIFT Message Types for Trade

| MT Code | Purpose |
|---------|---------|
| MT700 | Issue of a documentary credit |
| MT701 | Amendment of a documentary credit |
| MT710 | Advice of a third bank's documentary credit |
| MT760 | Guarantee / Standby Letter of Credit |
| MT798 | Trade finance messaging envelope |

---

## 4. DISCOUNTS & ALLOWANCES

### 4.1 Discount Types

| Type | Description | Tax Impact |
|------|-------------|------------|
| Trade Discount | Deduction from list/catalog price for trade channel partners. Not separately recorded in books -- invoice shows net price. | Reduces taxable base |
| Volume/Quantity Discount | Price reduction for large order quantities, often tiered. | Reduces taxable base |
| Cash Discount (Early Payment) | Reduction for paying before the due date (e.g., 2/10 Net 30). | Generally does not reduce VAT base in EU; varies by jurisdiction |
| Seasonal Discount | Discount for purchasing in off-peak season. | Reduces taxable base |
| Loyalty/Cumulative Discount | Based on total purchases over a period. May be settled via credit note. | Reduces taxable base via credit note |
| Introductory/New Product Discount | Incentive for buying new product lines. | Reduces taxable base |
| End-of-Range Discount | Clearance pricing for discontinued items. | Reduces taxable base |
| Sample Discount | Reduced or zero price for product samples. | May be treated as free supply for VAT |
| Defective Goods Allowance | Price reduction for goods received with defects. | Reduces taxable base; may require credit note |

### 4.2 Allowance Reason Codes (UNCL 5189)

| Code | Description |
|------|-------------|
| 41 | Bonus for works ahead of schedule |
| 42 | Other bonus |
| 60 | Manufacturer's consumer discount |
| 62 | Due to military status |
| 63 | Due to work accident |
| 64 | Special agreement |
| 65 | Production error discount |
| 66 | New outlet discount |
| 67 | Sample discount |
| 68 | End-of-range discount |
| 70 | Incoterm discount |
| 71 | Point of sales threshold allowance |
| 88 | Material surcharge/deduction |
| 95 | Discount |
| 100 | Special rebate |
| 102 | Fixed long term |
| 103 | Temporary |
| 104 | Standard |
| 105 | Yearly turnover |

### 4.3 Promotional Allowances

| Type | Description |
|------|-------------|
| Co-op Advertising Allowance | Seller contributes to buyer's advertising costs |
| Display/Merchandising Allowance | Allowance for in-store displays |
| Slotting Fee/Allowance | Payment for shelf space placement (retail) |
| Trade Promotion Deduction | Buyer deducts promotional amounts from payment |
| Rebate | Retrospective volume-based refund, typically via credit note |

### 4.4 Pre-Tax vs Post-Tax Discount Rules

- **Pre-tax discounts (trade discounts):** Reduce the taxable base. VAT/GST calculated on discounted amount.
- **Post-tax discounts (cash/settlement discounts):** In most EU jurisdictions, VAT is calculated on the full amount. If discount is taken, a credit note may be needed to adjust the VAT. Some jurisdictions (e.g., Germany) allow VAT on the expected discounted amount upfront.
- **Agent handling:** Always determine whether a discount applies before or after tax calculation. Flag mismatches between discount treatment and jurisdictional rules.

---

## 5. CHARGES, FEES & SURCHARGES

### 5.1 Charge Reason Codes (UNCL 7161) -- Key Categories

There are 223+ codes. The most invoice-relevant ones:

**Shipping & Logistics:**
| Code | Description |
|------|-------------|
| FC | Freight service |
| DL | Delivery |
| SAA | Shipping and handling |
| HD | Handling |
| FAC | Freight extraordinary handling |
| FAB | Freight equalization |
| ADT | Pick-up |
| RE | Re-delivery |
| RV | Loading |
| ADZ | Direct delivery |
| AEA | Diversion |
| TT | Transportation -- third party billing |
| TV | Transportation by vendor |

**Packaging:**
| Code | Description |
|------|-------------|
| PC | Packing |
| PL | Palletizing |
| ABL | Additional packaging |
| ABR | Containerisation |
| ABS | Carton packing |
| ABT | Hessian wrapped |
| ABU | Polyethylene wrap packing |
| SAD | Special packaging |
| SG | Shrink-wrap |
| NAA | Non-returnable containers |
| RAD | Returnable container |

**Processing & Treatment:**
| Code | Description |
|------|-------------|
| ACG | Enamelling treatment |
| ACH | Heat treatment |
| ACI | Plating treatment |
| ACJ | Painting |
| PAA | Phosphatizing (steel treatment) |
| ACL | Priming |
| ACM | Preservation treatment |

**Administrative & Financial:**
| Code | Description |
|------|-------------|
| AEM | Clerical or administrative services |
| FI | Financing |
| IS | Invoicing |
| AEP | Copyright fee collection |
| DAQ | Documentary credits transfer commission |
| ER | Exchange rate guarantee |
| AEN | Guarantee |

**Environmental & Recycling:**
| Code | Description |
|------|-------------|
| AEO | Collection and recycling |
| AEV | Environmental protection service |
| AEW | Environmental clean-up service |
| CAV | Battery collection and recycling |
| CAW | Product take back fee |

**Quality & Inspection:**
| Code | Description |
|------|-------------|
| IF | Inspection |
| CAE | Certificate of conformance |
| TAC | Testing |
| CAX | Quality control released |

**Other Common Charges:**
| Code | Description |
|------|-------------|
| AAT | Rush delivery |
| AEL | Small order processing service |
| DAN | Minimum order not fulfilled charge |
| RAF | Restocking |
| ABD | Overtime |
| AJ | Adjustments |
| PRV | Price variation |
| AEK | Cash on delivery |
| WH | Warehousing |
| AED | Handling of hazardous cargo |
| LAA | Labour |
| IAA | Installation |
| IAB | Installation and warranty |

### 5.2 Additional Invoice Charges Not in UNCL 7161

| Charge | Description |
|--------|-------------|
| Fuel Surcharge | Variable charge tied to fuel price index (common in logistics). Often expressed as percentage of base freight. |
| WEEE Fee | Waste Electrical and Electronic Equipment recycling levy (EU Directive 2012/19/EU) |
| EPR Fee | Extended Producer Responsibility fee (packaging waste, batteries, etc.) |
| Eco-tax / Green Levy | Environmental taxes varying by jurisdiction |
| Regulatory Cost Recovery | Charges to pass through regulatory compliance costs |
| Energy Surcharge | Broader than fuel -- covers all energy costs |
| Credit Card Surcharge | Convenience fee for card payments (legality varies by jurisdiction) |
| Currency Conversion Fee | Fee for processing foreign currency payments |
| Late Payment Interest | Statutory or contractual interest on overdue invoices |
| Fixed Recovery Cost | EUR 40 minimum under EU Late Payment Directive 2011/7/EU |
| Demurrage | Charge for exceeding free time at port/terminal |
| Detention | Charge for keeping containers/equipment beyond free time |
| Service Charge / Gratuity | Percentage-based charge for services (hospitality) |

### 5.3 Late Payment Interest (EU Directive 2011/7/EU)

- **Interest rate:** ECB reference rate + 8 percentage points (minimum)
- **When it starts:** 30 days after invoice receipt if no contractual terms
- **Maximum contractual payment term:** 60 days (B2B); 30 days for public authorities (extendable to 60 in exceptional cases)
- **Fixed recovery cost:** EUR 40 per invoice (minimum, regardless of interest)
- **Additional recovery costs:** Reasonable costs beyond the EUR 40 (lawyers, collection agencies)

---

## 6. LEGAL & COMPLIANCE REFERENCES

### 6.1 Purchase Order Matching

| Matching Type | Documents Compared | What is Checked |
|---------------|-------------------|-----------------|
| 2-Way Match | PO + Invoice | Prices, quantities, terms |
| 3-Way Match | PO + GRN + Invoice | Prices, quantities received, terms |
| 4-Way Match | PO + GRN + Inspection Report + Invoice | Plus quality acceptance |

**Tolerance rules:** Organizations set thresholds (e.g., +/- 3% or $100) for acceptable variances. Invoices within tolerance auto-approve; those outside tolerance route for manual review.

### 6.2 Legal Clauses on Invoices

| Clause | Description | Why It Matters |
|--------|-------------|----------------|
| Title Retention (Romalpa Clause) | Seller retains ownership until full payment. "Goods remain the property of [Seller] until paid in full." | Affects risk of buyer insolvency |
| Governing Law | "This invoice is governed by the laws of [jurisdiction]." | Determines which legal system applies |
| Dispute Resolution | Specifies arbitration vs litigation, forum selection. | Determines where/how disputes are resolved |
| Limitation of Liability | Caps total damages at contract value or a defined amount. | Limits financial exposure |
| Warranty Terms | States warranty period and conditions directly on invoice. | Creates enforceable obligations |
| Force Majeure | Excuses nonperformance due to unforeseeable events. | Affects delivery and payment obligations |
| Anti-Bribery Declaration | Compliance with FCPA, UK Bribery Act, etc. | Regulatory compliance requirement |
| Sanctions Compliance | Statement that transaction complies with applicable sanctions (OFAC, EU, UN). | Critical for cross-border trade |
| GDPR/Data Protection | Notice about processing of personal data on the invoice. | EU legal requirement |
| Assignment Restriction | "This invoice may not be assigned without prior written consent." | Affects factoring eligibility |
| Set-Off Prohibition | "Buyer may not deduct or set off amounts from this invoice." | Protects seller's right to full payment |
| Interest Clause | "Interest of X% per month will be charged on overdue amounts." | Contractual late payment terms |

### 6.3 Disputed Invoice Handling

- **Disputed Amount** -- the portion of the invoice under dispute
- **Undisputed Amount** -- the portion that should be paid on time regardless
- **Dispute Reason Code** -- structured classification of the dispute
- **Dispute Resolution Timeline** -- contractual window for resolution (typically 30-60 days)

---

## 7. DOCUMENT CROSS-REFERENCES

### 7.1 Full Cross-Reference Document Types

| Reference | Abbreviation | Description | UBL Element |
|-----------|-------------|-------------|-------------|
| Purchase Order | PO | Buyer's order authorizing the purchase | cac:OrderReference |
| Sales Order | SO | Seller's confirmation of the order | cac:OrderReference/cbc:SalesOrderID |
| Delivery Note / Dispatch Note | DN | Accompanies goods during transport | cac:DespatchDocumentReference |
| Goods Received Note | GRN | Buyer's confirmation of receipt | cac:ReceiptDocumentReference |
| Proforma Invoice | PI | Preliminary invoice before final billing | cac:BillingReference |
| Credit Note | CN | Adjusts an invoice downward (refunds, corrections) | cac:BillingReference |
| Debit Note | DN | Adjusts an invoice upward (additional charges) | cac:BillingReference |
| Contract Number | -- | Reference to underlying contract | cac:ContractDocumentReference |
| Tender/Bid Reference | -- | Reference to the procurement bid | cac:OriginatorDocumentReference |
| Work Order | WO | Authorization to perform specific work | Free text or additional reference |
| Job Number / Project Number | -- | Internal project tracking identifier | cac:ProjectReference |
| Requisition Number | -- | Internal purchase requisition | Additional reference |
| Waybill Number | -- | Transport document reference | cac:AdditionalDocumentReference |
| Receiving Report | -- | Detailed inspection and acceptance record | cac:ReceiptDocumentReference |
| Statement of Work (SOW) | -- | Defines scope for service invoices | Contract reference |
| Change Order | CO | Modifies original PO/contract terms | Additional reference |
| Application for Payment | AIA G702 | Construction progress payment request | Additional reference |
| Schedule of Values | AIA G703 | Line-by-line breakdown of construction costs | Additional reference |

### 7.2 Invoice Type Codes (UNCL 1001 Subset)

| Code | Name | Description |
|------|------|-------------|
| 71 | Request for payment | Generic payment request |
| 80 | Debit note (goods/services) | Charge increase for goods/services |
| 82 | Metered services invoice | Utility-type metered billing |
| 84 | Debit note (financial) | Financial adjustment debit |
| 102 | Tax notification | Tax-related notice |
| 218 | Final payment request | Based on work completion |
| 219 | Payment request for completed units | Unit-based payment |
| 326 | Partial invoice | Invoice for partial delivery |
| 331 | Commercial invoice with packing list | Combined document |
| 380 | Commercial invoice | Standard invoice (most common) |
| 382 | Commission note | Agent commission |
| 383 | Debit note | General debit note |
| 384 | Corrected invoice | Revision of a prior invoice |
| 386 | Prepayment invoice | Advance payment request |
| 388 | Tax invoice | Invoice compliant with tax requirements |
| 389 | Self-billed invoice | Created by buyer on seller's behalf |
| 393 | Factored invoice | Invoice assigned to a factor |
| 395 | Consignment invoice | For consignment stock |
| 553 | Forwarder's invoice discrepancy report | Freight discrepancy |
| 575 | Insurer's invoice | Insurance billing |
| 623 | Forwarder's invoice | Freight forwarder billing |
| 780 | Freight invoice | Standalone freight charges |
| 817 | Claim notification | Claim for damages/losses |
| 870 | Consular invoice | Required by some importing countries |
| 875 | Partial construction invoice | Construction progress billing |
| 876 | Partial final construction invoice | Near-complete construction billing |
| 877 | Final construction invoice | Construction project completion |

---

## 8. QUALITY & CERTIFICATION REFERENCES

### 8.1 Certificates Referenced on Invoices

| Certificate | Abbreviation | Industry | Description |
|-------------|-------------|----------|-------------|
| Mill Test Report | MTR / MTC | Metals/Manufacturing | Certifies chemical composition and mechanical properties of metals. References standards like ASTM, ASME, EN 10204. |
| Certificate of Conformity | CoC | Manufacturing/Trade | Confirms goods meet specified standards or regulatory requirements. |
| Certificate of Analysis | CoA | Pharma/Chemical/Food | Confirms finished product meets quality and regulatory specs. Lists test results. |
| Certificate of Origin | CoO | International Trade | Declares country where goods were manufactured. Required by many customs authorities. |
| Inspection Certificate | -- | Various | Third-party or in-house inspection verification. |
| Test Report | -- | Engineering | Results of specific tests performed on goods. |
| Calibration Certificate | -- | Instrumentation | Proves measuring equipment is calibrated to standards. |
| Phytosanitary Certificate | -- | Agriculture | Confirms plant products are pest-free for import. |
| Fumigation Certificate | -- | Shipping | Proves cargo has been treated for pests. |
| Health Certificate | -- | Food/Livestock | Sanitary compliance for food and animal products. |
| Insurance Certificate | -- | Shipping/Trade | Proof of cargo insurance coverage. |
| Weight Certificate | -- | Bulk cargo | Certified weight of goods shipped. |

### 8.2 EN 10204 Material Certificate Types

| Type | Description |
|------|-------------|
| 2.1 | Declaration of compliance with the order (no test data) |
| 2.2 | Test report with results from non-specific inspection |
| 3.1 | Inspection certificate 3.1 -- test data from specific inspection by manufacturer |
| 3.2 | Inspection certificate 3.2 -- validated by manufacturer AND independent inspector |

### 8.3 Quality System References

| Standard | Scope |
|----------|-------|
| ISO 9001 | Quality management systems |
| ISO 14001 | Environmental management systems |
| ISO 45001 | Occupational health & safety |
| ISO 22000 / FSSC 22000 | Food safety management |
| AS9100 | Aerospace quality management |
| IATF 16949 | Automotive quality management |
| ISO 13485 | Medical device quality |
| GMP (Good Manufacturing Practice) | Pharma/food manufacturing |
| HACCP | Food safety hazard analysis |
| Organic certification | USDA Organic, EU Organic |
| Fair Trade certification | Fair Trade International |
| FSC / PEFC | Sustainable forestry certification |
| CE Marking | EU product safety conformity |
| UL Listing | US product safety testing |
| RoHS Compliance | Restriction of Hazardous Substances (EU) |
| REACH Compliance | Chemical safety (EU) |

---

## 9. REGULATORY CODES & STANDARDS

### 9.1 Product & Commodity Classification

| System | Full Name | Structure | Usage | On Invoice For |
|--------|-----------|-----------|-------|---------------|
| HS Code | Harmonized System | 6-digit minimum (up to 10 with national extensions) | Customs classification of traded goods in 200+ countries. Maintained by WCO. | Customs declarations, duty calculation |
| HTS Code | Harmonized Tariff Schedule | 10-digit (US extension of HS) | US import classification with duty rates | US customs compliance |
| TARIC Code | EU Tariff Code | 10-digit (EU extension of HS) | EU customs with measures, quotas, suspensions | EU customs compliance |
| UNSPSC | UN Standard Products and Services Code | 8-digit hierarchical (Segment/Family/Class/Commodity) | Procurement classification. Open standard. | Spend analysis, procurement |
| CPV | Common Procurement Vocabulary | Up to 8 digits | EU public procurement classification | EU tenders and public contracts |
| GTIN | Global Trade Item Number | 8, 12, 13, or 14 digits | Product barcode identifier (EAN/UPC). Managed by GS1. | Product identification on invoices |
| EAN | European Article Number | 13 digits (EAN-13) | Product barcode, now part of GTIN | Product identification |
| UPC | Universal Product Code | 12 digits (UPC-A) | North American product barcode, now part of GTIN | Product identification |
| NDC | National Drug Code | 10-11 digits | US FDA pharmaceutical identifier | Drug/pharma invoices |
| NAICS | North American Industry Classification System | 6 digits | Industry classification (US/CA/MX) | Industry reporting |
| SIC | Standard Industrial Classification | 4 digits | Legacy industry classification (largely replaced by NAICS) | Regulatory reporting |
| CAS Number | Chemical Abstracts Service Registry Number | Variable (e.g., 7732-18-5 for water) | Unique chemical substance identifier. 159M+ registered compounds. | Chemical invoices, safety compliance |
| UN Number | United Nations Number | 4 digits (e.g., UN 1203 for gasoline) | Dangerous goods identifier (<10,000 entries) | Hazardous materials transport |
| IMDG Code | International Maritime Dangerous Goods | Classification system | Sea transport of dangerous goods | Maritime shipping documents |
| ADR Number | European Agreement for Dangerous Goods | Classification system | Road transport of dangerous goods | Road freight documents |
| ATC Code | Anatomical Therapeutic Chemical | 7 characters | Pharmaceutical classification (WHO) | Pharma invoices |
| ECCN | Export Control Classification Number | 5 characters | US export control classification | Controlled goods exports |

### 9.2 Dangerous Goods Required Data

When invoicing dangerous goods, invoices/documents must include:
- UN Number (e.g., UN 3480)
- Proper Shipping Name (PSN)
- Hazard Class/Division (1-9)
- Packing Group (I, II, or III)
- Net quantity per package
- Emergency contact number
- Shipper's Declaration for Dangerous Goods (IATA for air)

### 9.3 Unit of Measure Codes

Invoices use UN/ECE Recommendation 20 (Rec20) codes:

| Code | Unit |
|------|------|
| C62 | Each/unit |
| KGM | Kilogram |
| LTR | Litre |
| MTR | Metre |
| MTK | Square metre |
| MTQ | Cubic metre |
| TNE | Metric ton |
| KWH | Kilowatt hour |
| HUR | Hour |
| DAY | Day |
| MON | Month |
| ANN | Year |
| SET | Set |
| PR | Pair |
| BX | Box |
| CT | Carton |
| PK | Pack |
| EA | Each |
| LBR | Pound |
| GLL | Gallon (US) |

---

## 10. CURRENCY & EXCHANGE

### 10.1 Multi-Currency Fields

| Field | UBL Element | Description |
|-------|-------------|-------------|
| Invoice Currency | cbc:DocumentCurrencyCode | Primary currency (ISO 4217) |
| Tax Currency | cbc:TaxCurrencyCode | Currency for VAT reporting if different |
| Exchange Rate | Via calculation | Conversion rate between currencies |
| Exchange Rate Date | -- | Date when rate was fixed |
| Base Currency Amount | -- | Amounts expressed in seller's/buyer's base currency |
| Transaction Currency Amount | -- | Amounts in the agreed transaction currency |

### 10.2 Currency Clauses

| Type | Description |
|------|-------------|
| Fixed Rate | Exchange rate locked at contract signing |
| Floating Rate | Exchange rate at date of invoice or payment |
| Rate at Invoice Date | Rate published by ECB/central bank on invoice issue date |
| Rate at Payment Date | Rate on the day payment is made |
| Split/Shared Risk | Variance beyond a threshold shared 50/50 between parties |
| Corridor Clause | Rate within a band is accepted; outside triggers renegotiation |
| Hedging Reference | Reference to a forward contract or option hedging the exchange risk |

### 10.3 Common ISO 4217 Currency Codes

USD, EUR, GBP, JPY, CHF, CAD, AUD, CNY, INR, BRL, MXN, KRW, SGD, HKD, NOK, SEK, DKK, PLN, CZK, HUF, TRY, ZAR, AED, SAR, THB, MYR, IDR, PHP, VND, TWD, NZD, etc.

---

## 11. TAX -- COMPLETE REFERENCE

### 11.1 Tax Category Codes (UNCL 5305)

| Code | Category | Description |
|------|----------|-------------|
| S | Standard rate | Normal VAT/GST rate applies |
| Z | Zero rated | Taxable but at 0% -- seller can reclaim input tax |
| E | Exempt | Not subject to tax -- seller cannot reclaim related input tax |
| AE | Reverse charge | Buyer self-assesses VAT |
| K | Intra-community supply (EEA) | VAT-free supply between EU member states |
| G | Free export item | Exported goods, VAT not charged |
| O | Outside scope | Services not within scope of tax |
| L | Canary Islands IGIC | Canary Islands indirect tax |
| M | Ceuta/Melilla IPSI | Special Spanish territory tax |
| B | Transferred (Italy) | VAT paid directly to tax authority, not seller |

### 11.2 Tax Types Beyond VAT

| Tax Type | Jurisdiction | Description |
|----------|-------------|-------------|
| VAT (Value Added Tax) | EU, UK, 175+ countries | Multi-stage consumption tax |
| GST (Goods and Services Tax) | India, Australia, Singapore, Canada, NZ, Malaysia | Similar to VAT |
| Sales Tax | US (state/local) | Single-stage tax at point of sale |
| Use Tax | US | Tax on goods used in state where no sales tax was collected |
| Withholding Tax (WHT) | Global | Payer withholds tax from payment to foreign supplier. Rate varies by treaty. |
| TDS (Tax Deducted at Source) | India | Indian variant of withholding tax for domestic payments |
| Excise Duty | Various | Tax on specific goods (alcohol, tobacco, fuel) |
| Customs Duty | Global | Import tariff based on HS classification |
| Stamp Duty | Various | Tax on legal documents/transactions |
| Environmental Tax / Carbon Tax | EU, various | Tax on emissions or polluting activities |
| Digital Services Tax (DST) | Various | Tax on digital service revenues |
| IEPS | Mexico | Special tax on certain products |
| ICMS / IPI / PIS / COFINS | Brazil | Multiple cascading taxes |

### 11.3 VAT Exemption Reason Codes (VATEX)

Over 60 codes referencing specific EU VAT Directive (2006/112/EC) articles:

| Code Pattern | Scope |
|-------------|-------|
| VATEX-EU-132-1A through 1Q | Public interest exemptions (postal, medical, education, sport, etc.) |
| VATEX-EU-143-1A through 1L | Exemptions on importation (diplomatic, military, gold, etc.) |
| VATEX-EU-148-A through G | International transport (vessels, aircraft fuel and services) |
| VATEX-EU-151-1A through 1E | Transactions treated as exports |
| VATEX-EU-AE | Reverse charge |
| VATEX-EU-IC | Intra-community supply |
| VATEX-EU-G | Export outside EU |
| VATEX-EU-O | Not subject to VAT |
| VATEX-EU-D, F, I, J | Margin scheme (second-hand goods, works of art, antiques) |
| VATEX-FR-* | France-specific exemptions (CGI articles) |

### 11.4 Reverse Charge Mechanism

- Buyer self-assesses VAT instead of seller charging it
- Invoice must state "Reverse charge" or the relevant legal basis
- Tax category code = AE
- No VAT amount shown on invoice
- Used for: cross-border B2B services, construction (domestic reverse charge in UK/EU), certain goods

### 11.5 Self-Billing for Tax

- Buyer creates the tax invoice on behalf of the seller
- Both parties must have a written self-billing agreement
- Invoice must be marked as self-billed (type code 389)
- Seller must not issue their own invoice for the same supply

### 11.6 Withholding Tax on Invoices

| Element | Description |
|---------|-------------|
| WHT Rate | Percentage withheld (varies: 0--30%+, depends on treaty) |
| WHT Amount | Calculated amount withheld |
| Net Payment | Invoice amount minus WHT |
| WHT Certificate Reference | TDS certificate (e.g., India Form 16A) or equivalent |
| Tax Treaty Reference | Applicable double tax agreement |
| WHT Exemption Certificate | Certificate reducing or eliminating WHT |

---

## 12. CREDIT MANAGEMENT

### 12.1 Factoring & Assignment

| Element | Description |
|---------|-------------|
| Notice of Assignment (NOA) | Formal notice that invoice receivables have been assigned to a factor. "This invoice has been assigned to [Factor Name]. Payment must be made to [Factor's account details]." |
| Factor Name & Details | Name, address, bank details of the factoring company |
| Assignment Date | Date the receivable was assigned |
| Recourse / Non-Recourse | Whether the seller retains risk of buyer non-payment |
| UCC Filing Reference | US Uniform Commercial Code filing securing the assignment |
| Notification Clause | Buyer is legally bound to pay the factor once notified |

### 12.2 Credit Insurance

| Element | Description |
|---------|-------------|
| Credit Insurer | Company providing credit insurance (e.g., Euler Hermes, Coface, Atradius) |
| Policy Number | Insurance policy reference |
| Coverage Limit | Maximum insured amount per buyer |
| Coverage Percentage | Typically 75-95% of invoice value |
| Waiting Period | Days after due date before claim can be filed |

### 12.3 Set-Off / Contra / Netting

| Term | Description |
|------|-------------|
| Set-Off | Buyer deducts amounts owed to them by the seller from the invoice payment |
| Contra Entry | Mutual debts between parties offset against each other |
| Netting | Aggregating multiple invoices/credit notes to settle a single net amount |
| Multilateral Netting | Netting across multiple entities within a corporate group |
| Netting Agreement | Formal agreement governing the netting process |

---

## 13. ELECTRONIC INVOICE STANDARDS & METADATA

### 13.1 EN 16931 Business Terms (BT-1 through BT-165)

The European Standard defines 165 business terms in groups:

| BT Range | Group | Key Fields |
|----------|-------|------------|
| BT-1 to BT-8 | Invoice Header | Invoice number, issue date, due date, type code, currency, tax point date, tax currency, buyer reference |
| BT-9 to BT-10 | Payment | Payment due date, buyer reference |
| BT-11 to BT-13 | References | Project reference, contract reference, PO reference |
| BT-14 to BT-18 | Document References | Sales order, receiving advice, despatch advice, tender/lot reference, invoiced object ID |
| BT-19 to BT-20 | Accounting | Buyer accounting reference, payment terms |
| BT-21 to BT-22 | Notes | Invoice note subject code, invoice note |
| BT-23 to BT-24 | Process | Business process type (ProfileID), Specification identifier (CustomizationID) |
| BT-25 to BT-26 | Billing Reference | Preceding invoice number, preceding invoice issue date |
| BT-27 to BT-43 | Seller | Name, trading name, identifiers, VAT ID, tax registration, address, contact |
| BT-44 to BT-58 | Buyer | Name, trading name, identifiers, VAT ID, address, contact |
| BT-59 to BT-63 | Payee & Tax Rep | Payee name, payee ID, tax representative name, VAT ID, address |
| BT-70 to BT-80 | Delivery | Deliver-to name, location ID, date, period, address |
| BT-81 to BT-91 | Payment Means | Payment means code, payment means text, remittance info, account ID/name, BIC, mandate reference, bank creditor ID, debited account |
| BT-92 to BT-105 | Allowances & Charges | Document-level allowance/charge amounts, base, percentage, VAT category, VAT rate, reason code, reason text |
| BT-106 to BT-115 | Monetary Totals | Sum of line net, total allowances, total charges, net total, VAT amounts, total with VAT, prepaid, payable rounding, amount due |
| BT-116 to BT-121 | VAT Breakdown | Taxable amount, tax amount, category code, rate, exemption reason text, exemption reason code |
| BT-122 to BT-125 | Additional Documents | Document reference, description, external location (URI), attached document (binary) |
| BT-126 to BT-165 | Invoice Lines | Line ID, note, object ID, quantity, UoM, net amount, order line ref, accounting reference, period, line allowances/charges, price, item name/description, identifiers, classification, country of origin, item attributes |

### 13.2 E-Invoice Format Standards

| Standard | Region | Format | Description |
|----------|--------|--------|-------------|
| UBL 2.1 (ISO/IEC 19845) | Global | XML | Universal Business Language -- most widely adopted syntax |
| UN/CEFACT CII | Global | XML | Cross-Industry Invoice -- alternative syntax for EN 16931 |
| Peppol BIS Billing 3.0 | EU/Global | UBL 2.1 XML | Peppol network standard. CIUS of EN 16931. |
| ZUGFeRD 2.x / Factur-X | DE/FR/EU | PDF/A-3 + XML | Hybrid: human-readable PDF with embedded CII XML. |
| XRechnung | Germany | UBL or CII XML | German CIUS of EN 16931 for public sector. XML only (no PDF). |
| FatturaPA (SDI) | Italy | XML | Italian e-invoice format via Sistema di Interscambio |
| SII / TicketBAI | Spain | XML | Spanish tax reporting / Basque Country e-invoice |
| FATOORAH (ZATCA) | Saudi Arabia | XML or PDF/A-3+XML | Arabic + XML, digitally signed, cryptographic stamp |
| MyInvois | Malaysia | UBL 2.1 (XML/JSON) | 55 data fields, 37 mandatory. Via LHDN platform. |
| GST e-Invoice (India) | India | JSON | 50 mandatory fields, schema GST INV-01, IRN generation. QR code required. |
| CFDI | Mexico | XML | Comprobante Fiscal Digital por Internet. Via PAC providers. |
| NF-e | Brazil | XML | Nota Fiscal Eletronica. Per SEFAZ. |
| E-Fatura | Turkey | UBL-TR | Turkish e-invoice via GIB. |
| KSeF | Poland | XML | National e-Invoice System (Krajowy System e-Faktur) |
| AS2/X12 810 | US/Global | EDI | ANSI X12 standard for B2B invoice exchange |
| EDIFACT INVOIC | Global | EDI | UN/EDIFACT invoice message |

### 13.3 EDI 810 (ANSI X12) Invoice Segments

| Segment | Name | Purpose |
|---------|------|---------|
| ISA | Interchange Control Header | Sender/receiver IDs, authorization, version |
| GS | Functional Group Header | Sender/receiver codes, date/time |
| ST | Transaction Set Header | Identifies document type (810) |
| BIG | Beginning Segment for Invoice | Invoice date, invoice number, PO number, PO date |
| NTE | Note/Special Instruction | Free text notes |
| CUR | Currency | Currency codes and exchange rates |
| REF | Reference Identification | Various references (contract, BOL, etc.) |
| N1 | Name | Party identification (buyer, seller, ship-to, etc.) |
| N2-N4 | Address | Additional name/address lines, city/state/zip |
| ITD | Terms of Sale/Deferred Payment | Payment terms, discount percentage, days, net days |
| DTM | Date/Time Reference | Various dates |
| IT1 | Baseline Item Data | Line item: quantity, UoM, unit price, product IDs |
| PID | Product/Item Description | Free-form or structured item description |
| TXI | Tax Information | Tax type, amount, percentage |
| SAC | Service, Promotion, Allowance, Charge | Discounts, surcharges, freight charges |
| TDS | Total Monetary Value Summary | Total invoice amount |
| TXI | Tax Information (summary) | Tax totals |
| CTT | Transaction Totals | Number of line items |
| SE | Transaction Set Trailer | Segment count |
| GE | Functional Group Trailer | Transaction set count |
| IEA | Interchange Control Trailer | Group count |

### 13.4 EDIFACT INVOIC Message Segments

| Segment | Name | Purpose |
|---------|------|---------|
| UNH | Message Header | Message identification |
| BGM | Beginning of Message | Document type, invoice number, function |
| DTM | Date/Time/Period | Invoice date, delivery date, payment date |
| PAI | Payment Instructions | Payment method |
| ALI | Additional Information | Country of origin, duty regime |
| FTX | Free Text | Notes, terms, descriptions |
| RFF | Reference | PO number, contract number, etc. |
| NAD | Name and Address | Seller, buyer, ship-to, etc. |
| FII | Financial Institution Information | Bank details |
| CUX | Currencies | Currency codes and exchange rates |
| PAT | Payment Terms Basis | Payment terms details |
| TDT | Transport Information | Transport mode, carrier, vessel |
| TOD | Terms of Delivery | Incoterms |
| LOC | Location | Delivery location |
| LIN | Line Item | Product identification |
| QTY | Quantity | Quantities |
| MOA | Monetary Amount | Amounts at various levels |
| PRI | Price Details | Unit prices |
| TAX | Tax Details | Tax type, rate, amount |
| ALC | Allowance or Charge | Discounts and surcharges |
| UNS | Section Control | Separates detail from summary |
| CNT | Control Total | Hash totals for validation |
| UNT | Message Trailer | Segment count |

### 13.5 Digital Signatures & Security

| Element | Description |
|---------|-------------|
| XML Digital Signature (XAdES) | XML Advanced Electronic Signature per EU eIDAS regulation |
| PDF Digital Signature (PAdES) | PDF signature standard |
| Cryptographic Stamp (ZATCA) | Saudi Arabia requires cryptographic hash stamp on e-invoices |
| Hash Value / Checksum | SHA-256 or similar hash of invoice data for integrity verification |
| Certificate Reference | X.509 certificate identifier used for signing |
| Timestamp | Trusted timestamp proving when signature was created |
| QR Code | Machine-readable code containing key invoice data for verification |

### 13.6 QR Code Content on Invoices

Typical QR code contents vary by jurisdiction:

**India GST:** Supplier GSTIN, Buyer GSTIN, Invoice Number, Date of Invoice, Invoice Value, Number of Line Items, HSN Code, Unique IRN (Invoice Registration Number)

**Saudi Arabia ZATCA:** Seller name, VAT registration number, Invoice date/time, Invoice total with VAT, VAT amount (Phase 1). Phase 2 adds cryptographic stamp and UUID.

**Swiss QR-bill:** IBAN, Amount, Currency, Creditor name/address, Reference type (QRR or SCOR/ISO 11649), Reference number, Unstructured message, Billing information

### 13.7 Creditor Reference (ISO 11649)

- Format: "RF" + 2 check digits + up to 21 alphanumeric characters
- Example: RF18 5390 0754 7034
- Check digit uses same MOD 97 algorithm as IBAN
- Used in SEPA payments for structured remittance information
- Allows automatic reconciliation of payments to invoices

---

## 14. CONSTRUCTION-SPECIFIC INVOICE FIELDS

### 14.1 AIA Billing (US Construction Industry)

| Form | Name | Contents |
|------|------|----------|
| G702 | Application and Certificate for Payment | Summary: original contract sum, change orders to date, contract sum to date, total completed and stored, retainage, total earned less retainage, previous certificates, current payment due, balance to finish |
| G703 | Continuation Sheet | Line-by-line Schedule of Values: item number, description, scheduled value, work completed from previous application, work completed this period, materials presently stored, total completed and stored to date, percentage complete, balance to finish, retainage |

### 14.2 Construction-Specific Line Items

| Field | Description |
|-------|-------------|
| Schedule of Values (SOV) | Detailed cost breakdown by work category |
| Percentage Complete | % of each SOV line item completed |
| Materials Stored On-Site | Value of materials delivered but not yet installed |
| Materials Stored Off-Site | Value of materials at remote storage |
| Change Order Number | Modification to original contract scope |
| Variation Number | UK equivalent of change order |
| Certified Amount | Amount approved by architect/engineer for payment |
| Retention Amount | Amount held back per retention terms |
| Lien Waiver Reference | Waiver of mechanic's lien rights (conditional or unconditional) |
| Sworn Statement | Contractor's list of all subcontractors and suppliers with amounts owed |
| Substantial Completion Date | Date when project is sufficiently complete for intended use |

---

## 15. AGENT HANDLING GUIDELINES

### 15.1 Red Flags & Validation Rules

| Check | Rule | Red Flag |
|-------|------|----------|
| Invoice Number | Must be unique and sequential per supplier | Duplicate numbers, gaps in sequence |
| Dates | Issue date <= due date; delivery date <= issue date typically | Future-dated invoices, dates far in the past |
| PO Matching | Invoice PO reference must match a valid PO | No PO reference, PO number not found |
| Tax Calculation | Tax = taxable amount x rate (within rounding tolerance) | Math errors exceeding $0.01-$1.00 tolerance |
| Tax ID Validation | VAT/GST numbers must pass format and checksum validation | Invalid format, failed VIES/GST validation |
| Currency | Must be valid ISO 4217 code | Unrecognized currency codes |
| IBAN | Must pass MOD 97 check digit validation | Failed checksum |
| Bank Details Changed | Compare to master data | New or changed bank details (potential fraud) |
| Duplicate Detection | Same supplier + same amount + same date (+/- window) | Potential duplicate invoice |
| Amount Threshold | Unusually large amounts vs historical pattern | Statistical outlier |
| Round Amounts | Exact round numbers (e.g., $10,000.00) | Potential fabrication |
| Discount Terms | Discount % < 100; discount days < net days | Impossible discount terms |
| Exchange Rate | Must be within reasonable range of published rate | Rate significantly deviating from ECB/market rate |
| Retention Rate | Typically 5-10% | Unusual retention percentages |
| HS Code Format | 6+ digits | Invalid format or code not in HS database |
| UNCL Codes | Must match valid values in respective code lists | Unrecognized payment means, tax category, charge/allowance codes |

### 15.2 Three-Way Match Tolerance Examples

| Field | Typical Tolerance |
|-------|------------------|
| Unit Price | +/- 1-5% or $0.01-$1.00 per unit |
| Quantity | +/- 0-10% (varies by industry) |
| Total Amount | +/- $1-$100 (depends on invoice size) |
| Tax Amount | +/- $0.01-$1.00 (rounding only) |

### 15.3 Data Extraction Priority

For AI agent processing, extract fields in this priority order:

1. **Critical / Always Extract:** Invoice number, date, due date, supplier name/ID, buyer name/ID, currency, line items (description, quantity, unit price, amount), subtotal, tax amount, total amount, payment terms
2. **High Priority:** PO reference, tax IDs (VAT/GST), bank details (IBAN/SWIFT), tax category and rates per line, delivery date, Incoterms
3. **Medium Priority:** Contract reference, delivery note reference, payment method code, allowances/charges, retention amount, exchange rate, HS codes, credit note references
4. **Lower Priority but Important:** QR code data, digital signature status, certificates referenced, shipping marks, dangerous goods codes, certification references, legal clauses

---

Sources:
- [Peppol BIS Billing 3.0 - UBL Invoice Syntax](https://docs.peppol.eu/poacc/billing/3.0/syntax/ubl-invoice/)
- [Peppol UNCL 4461 Payment Means Codes](https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL4461/)
- [Peppol VATEX Exemption Codes](https://docs.peppol.eu/poacc/billing/3.0/codelist/vatex/)
- [Peppol UNCL 5305 Tax Category Codes](https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5305/)
- [Peppol UNCL 1001 Invoice Type Codes](https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL1001-inv/)
- [Peppol UNCL 5189 Allowance Reason Codes](https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL5189/)
- [Peppol UNCL 7161 Charge Reason Codes](https://docs.peppol.eu/poacc/billing/3.0/codelist/UNCL7161/)
- [EN 16931 Business Terms Mapping](https://gflohr.github.io/e-invoice-eu/en/docs/other/business-terms/)
- [eInvoice Mandatory Fields (traffiqx.net)](https://www.traffiqx.net/en/academy-en?view=article&id=397:pflichtangaben-pflichtfelder-erechnungen-2&catid=24)
- [Know Your Incoterms - US Trade.gov](https://www.trade.gov/know-your-incoterms)
- [Incoterms 2020 Complete Guide (IncoDocsn)](https://incodocs.com/blog/incoterms-2020-explained-the-complete-guide/)
- [ICC Incoterms 2020](https://iccwbo.org/business-solutions/incoterms-rules/incoterms-2020/)
- [FOB Shipping Wikipedia](https://en.wikipedia.org/wiki/FOB_(shipping))
- [Freight Prepaid vs Collect (ATS)](https://www.atsinc.com/blog/freight-prepaid-freight-collect-definitions-differences)
- [Invoice Payment Terms (Billdu)](https://www.billdu.com/blog/understanding-invoice-payment-terms/)
- [Invoice Payment Terms (altLINE)](https://altline.sobanco.com/standard-invoice-payment-terms/)
- [Payment Terms (Stripe)](https://stripe.com/resources/more/what-are-payment-terms-a-primer-for-businesses)
- [Letters of Credit Guide (Trade Finance Global)](https://www.tradefinanceglobal.com/letters-of-credit/)
- [Documentary Collections (Trade Finance Global)](https://www.tradefinanceglobal.com/posts/documentary-collections-instructions-for-use/)
- [Discounts and Allowances (Wikipedia)](https://en.wikipedia.org/wiki/Discounts_and_allowances)
- [Trade Discount vs Cash Discount](https://www.enkash.com/resources/blog/trade-discount-difference-between-trade-discount-cash-discount)
- [Environmental Surcharges (SoftCo)](https://softco.com/glossary/environmental-surcharges/)
- [EU Late Payment Directive 2011/7](https://eur-lex.europa.eu/eli/dir/2011/7/oj/eng)
- [EU Late Payment Interest Calculator](https://www.paidnice.com/calculators/eu-late-payment-directive)
- [Construction Retainage (Procore)](https://www.procore.com/library/retainage)
- [AIA Billing G702/G703 Guide (Autodesk)](https://www.autodesk.com/blogs/construction/g702-g703-forms-aia-billing/)
- [Notice of Assignment in Factoring](https://resolvepay.com/blog/notice-of-assignment)
- [EDI 810 Invoice (Stedi)](https://www.stedi.com/edi/x12/transaction-set/810)
- [EDIFACT INVOIC Message (Seeburger)](https://www.seeburger.com/resources/good-to-know/edifact-invoic-message)
- [ZUGFeRD/Factur-X FAQ](https://zugferd.org/e-invoicing/1.0.0/faq.en.html)
- [XRechnung and ZUGFeRD (Storecove)](https://www.storecove.com/blog/en/zugferd-factur-x/)
- [3-Way Matching in AP (NetSuite)](https://www.netsuite.com/portal/resource/articles/accounting/three-way-matching.shtml)
- [2/3/4-Way Match Comparison (Planergy)](https://planergy.com/blog/2-way-match-vs-3-way-match-vs-4-way-match/)
- [Self-Billing Industries (OpenText)](https://blogs.opentext.com/four-examples-of-industries-using-self-billing/)
- [Evaluated Receipt Settlement (NCSU)](https://scm.ncsu.edu/scm-articles/article/what-is-evaluated-receipt-settlement)
- [Multi-Currency Invoicing (J.P. Morgan)](https://www.jpmorgan.com/insights/payments/fx-cross-border/fx-vendors-payment-currency)
- [Creditor Reference ISO 11649 (Wikipedia)](https://en.wikipedia.org/wiki/Creditor_Reference)
- [Swiss QR-Bill Implementation (SIX)](https://www.six-group.com/dam/download/banking-services/standardization/qr-bill/ig-qr-bill-v2.3-en.pdf)
- [Reverse Charge VAT (GetSphere)](https://www.getsphere.com/blog/reverse-charge-vat)
- [ZATCA e-Invoicing Saudi Arabia](https://zatca.gov.sa/en/E-Invoicing/Pages/default.aspx)
- [Malaysia e-Invoice Mandatory Fields](https://www.binarysemantics.com/blogs/what-are-the-53-mandatory-fields-of-e-invoice-in-malaysia/)
- [India GST e-Invoice](https://einvoice6.gst.gov.in/content/einvoice-mandate/)
- [Mill Test Reports (Evident Scientific)](https://ims.evidentscientific.com/en/insights/mill-test-reports-in-metal-manufacturing-a-comprehensive-guide)
- [Material Test Certificate (HQTS)](https://www.hqts.com/material-test-certificate/)
- [UNSPSC FAQs](https://www.unspsc.org/faqs)
- [CPV Codes Guide (Classifast)](https://blog.classifast.com/2025/10/cpv-codes-list/)
- [Dangerous Goods Declaration (Shipium)](https://hub.shipium.com/content/dangerous-goods-declaration/)
- [Withholding Tax Rates (PwC)](https://taxsummaries.pwc.com/quick-charts/withholding-tax-wht-rates)