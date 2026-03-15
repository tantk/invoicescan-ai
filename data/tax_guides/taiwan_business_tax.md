# Taiwan — Business Tax (Ying Ye Shui / 營業稅) & GUI Guide

## Overview
Taiwan's consumption tax is called Business Tax (營業稅 / Ying Ye Shui), governed by the Value-Added and Non-Value-Added Business Tax Act (加值型及非加值型營業稅法). It is administered by the Ministry of Finance (財政部) and collected by the National Taxation Bureaus (國稅局) across five regional jurisdictions (Taipei, Northern, Central, Southern, and Kaohsiung). Taiwan was one of the first countries in Asia to implement a fully mandatory centralized e-invoicing system — the Electronic Government Uniform Invoice (e-GUI / 電子發票) system.

## Tax Rates
- **Standard rate: 5%** (applicable to most goods and services, including digital services and SaaS)
- **Zero-rated (0%)**: Exports of goods, services relating to exports or services provided in Taiwan but used abroad, goods sold by duty-free shops, goods sold by bonded zone entities for direct export, international transportation, vessels and aircraft used in international transport and deep-sea fishing, maintenance services for international transport vessels/aircraft, goods and services sold to entities in export processing zones/science parks/bonded warehouses for export
- **Non-value-added business tax (special rates)**: Financial institutions (2% or 5% depending on the type of revenue), reinsurance enterprises (1%), small-scale businesses below the threshold (1% of gross receipts assessed by tax authorities)
- **Exempt**: Government bonds and securities transactions, medical services and medicines provided by hospitals/clinics, education services by schools and approved institutions, land transactions (subject to separate land value increment tax), social welfare services, residual/obsolete goods sold at government tender, farming/fishing/animal husbandry/forestry/mining products sold by primary producers, agricultural land and irrigation services, funeral and burial services by government or non-profits, goods imported by disabled persons for personal use

## Tax ID Format
- **GUI Number (統一編號 / Tong Yi Bian Hao / Unified Business Number / BAN)**:
  - Format: 8 digits: `XXXXXXXX`
  - Assigned by the Ministry of Economic Affairs upon business registration
  - Example: `04595257`
  - Used on all invoices, tax filings, and commercial transactions
  - Also referred to as BAN (Business Administration Number) or Tax ID
- Verify at: https://findbiz.nat.gov.tw (Ministry of Economic Affairs business search)

## Invoice Requirements — Government Uniform Invoice (GUI / 統一發票)
All businesses must issue Government Uniform Invoices for sales of goods or services. Invoice types include:

### Types of GUI
1. **Triplicate Uniform Invoice (三聯式統一發票)**: For B2B transactions — three copies (buyer, seller, tax authority)
2. **Duplicate Uniform Invoice (二聯式統一發票)**: For B2C transactions — two copies (buyer, seller)
3. **Special Uniform Invoice**: For specific transaction types (e.g., void/return, overseas sales)
4. **Electronic GUI (e-GUI / 電子發票)**: The mandatory electronic format for most businesses

### Required Fields
1. Seller's name (營業人名稱)
2. Seller's GUI number (統一編號)
3. Invoice date (發票日期)
4. Invoice number (發票號碼) — assigned by the Ministry of Finance in sequential blocks
5. Buyer's GUI number (for B2B; not required for B2C)
6. Description of goods or services
7. Quantity
8. Unit price
9. Amount (未稅金額 — before tax for B2B)
10. Business tax amount (稅額) — **must be itemized separately on B2B invoices**; not required to be itemized on B2C invoices
11. Total amount (含稅金額)
12. For zero-rated supplies: legal basis for zero-rating

**Important**: For B2B transactions, the business tax must be stated **separately** from the sales amount. For B2C transactions, the tax does not need to be separately itemized.

## E-Invoicing — e-GUI (電子發票)
### System Overview
Taiwan's e-GUI system is a centralized, mandatory e-invoicing platform operated by the Ministry of Finance through the **E-Invoice Integrated Service Platform (電子發票整合服務平台)**. It was one of Asia's earliest mandatory e-invoicing systems, with gradual rollout beginning in 2006.

### Current Status (2026)
- **Mandatory** for all VAT-registered businesses (phased in since 2018-2019; now universal)
- **MIG 4.1 standard**: From 2026, e-invoices must comply with the MIG (Message Implementation Guide) version 4.1, replacing MIG 4.0
- **Format**: XML-based structured data transmitted to the MoF platform

### Transmission Requirements
- **B2B invoices**: Must be transmitted to the MoF E-Invoice Platform within **7 days** of issuance
- **B2C invoices**: Must be transmitted within **2 days** of issuance
- **Void/return invoices**: Must also be reported to the platform within prescribed deadlines

### e-GUI Infrastructure
- Businesses connect to the platform via API, certified e-invoice service providers, or the platform's web portal
- Each invoice is assigned a unique **track number (字軌號碼)** from pre-allocated number ranges provided by the tax authority
- E-invoices can be stored on cloud-based carriers: mobile phone barcodes, citizen digital certificates, or retailer membership cards (for B2C)
- Paper GUI receipts are still printed for B2C transactions where the consumer does not use a carrier, but the data is still transmitted electronically

### Lottery System (統一發票對獎)
Taiwan has a unique invoice lottery system to incentivize consumers to request receipts:
- Every two months, winning numbers are drawn for GUI invoices
- Prizes range from TWD 200 to TWD 10,000,000 (special prize)
- e-GUI invoices stored on cloud carriers are automatically checked against winning numbers
- This system dramatically improves B2C invoice compliance

### Penalties
- Failure to transmit e-invoices within deadlines: fines of **TWD 1,500 to TWD 15,000**
- Failure to issue GUI: penalty of **1-10 times the tax amount** evaded
- Issuing non-compliant invoices: fines and potential business registration consequences

## Key Rules
- **Registration threshold**: All businesses selling goods or services in Taiwan must register for business tax. Small-scale businesses (月營業額 below TWD 200,000 for goods or TWD 100,000 for services) are assessed on a flat-rate basis by the tax authority rather than self-filing.
- **Filing frequency**: Bi-monthly — covering January-February, March-April, May-June, July-August, September-October, November-December. Returns due by the **15th of the month** following the end of the bi-monthly period.
- **Input tax credit**: Available for VAT-type businesses — input tax on purchases can be deducted from output tax. Supporting GUI invoices must be properly obtained.
- **Non-deductible input tax**: Entertainment expenses, personal use items, passenger cars not used for business transportation
- **Withholding on payments to foreign entities**: When paying for services from foreign entities with no fixed place of business in Taiwan, the buyer must withhold and pay the 5% business tax on behalf of the foreign provider
- **Tax-exclusive pricing**: B2B invoices show tax-exclusive amounts with tax itemized; B2C invoices typically show tax-inclusive amounts
- **Currency**: All invoices and filings must be in New Taiwan Dollars (TWD/NTD)

## Common Pitfalls
1. **Missing B2B tax itemization**: Failing to separately state the business tax amount on B2B invoices — buyer cannot claim input tax credit without proper itemization
2. **e-GUI transmission deadlines**: Missing the 7-day (B2B) or 2-day (B2C) transmission deadlines to the MoF platform — triggers fines
3. **GUI number block management**: Running out of pre-allocated invoice number ranges without requesting new blocks in advance — cannot issue valid invoices
4. **Foreign service provider withholding**: Forgetting to withhold and remit 5% business tax when paying foreign service providers without a Taiwan presence
5. **Zero-rate documentation**: Claiming zero-rate on exports without maintaining sufficient supporting documents (shipping documents, customs declarations) — standard 5% rate will apply
6. **Small-scale business misclassification**: Businesses exceeding the small-scale thresholds (TWD 200,000/month for goods) must register for regular VAT filing — continuing on the flat-rate assessment is non-compliant
7. **Bi-monthly filing confusion**: Filing monthly instead of bi-monthly, or missing the 15th-of-month deadline — Taiwan's bi-monthly cycle is unique compared to most countries
8. **Invoice lottery receipts**: Businesses not issuing GUI for B2C transactions to avoid reporting — consumers actively demand GUI for the lottery, and non-issuance triggers complaints and audits
