# Brazil — Nota Fiscal & Tax Guide

## Overview
Brazil has one of the world's most complex tax systems with overlapping federal, state, and municipal taxes. The Nota Fiscal Eletrônica (NF-e) is the mandatory electronic invoice.

## Tax Components
### Federal Taxes
- **IPI** (Industrialized Products Tax): 0–30%+ on manufactured goods
- **PIS** (Social Integration Program): 0.65% (cumulative) or 1.65% (non-cumulative)
- **COFINS** (Social Security Financing): 3% (cumulative) or 7.6% (non-cumulative)
- **IRRF** (Withholding Income Tax): 1–15% on services, royalties
- **IOF** (Financial Operations Tax): on credit, FX, insurance, securities
- **CSLL** (Social Contribution on Net Profit): 9–20%

### State Tax
- **ICMS** (Tax on Circulation of Goods and Services): 4–25% varies by state and product
  - Interstate rates: 4% (imported goods), 7% (South/Southeast to other regions), 12% (other combinations)
  - Intrastate: set by each state (typically 17–20%)
  - ICMS-ST (Substituição Tributária): tax collected upfront in supply chain

### Municipal Tax
- **ISS** (Service Tax): 2–5% on services, set by each municipality

## Tax Reform (EC 132/2023)
Major reform transitioning to a dual VAT system:
- **CBS** (Federal): replacing PIS + COFINS
- **IBS** (State/Municipal): replacing ICMS + ISS
- Transition period: 2026–2032
- Target combined rate: ~26.5%

## Nota Fiscal Types
- **NF-e (Modelo 55)**: Goods (B2B). Most common.
- **NFC-e (Modelo 65)**: Consumer (B2C, replaces paper receipts)
- **NFS-e**: Services (municipal level, varies by city)
- **CT-e**: Transport documents
- **MDF-e**: Cargo manifest

## NF-e Requirements
1. **Digital certificate**: ICP-Brasil A1 or A3
2. **SEFAZ authorization**: Must be validated by state tax authority BEFORE invoice is valid
3. **Access key**: 44-digit unique identifier
4. **XML format** with digital signature
5. **DANFE**: Auxiliary printed document (visual representation of the XML)

### Mandatory Fields
- Emitter CNPJ, state registration, name, address
- Recipient CNPJ/CPF, name, address
- NCM code (8-digit Mercosur product classification)
- CFOP code (fiscal operation code — determines tax treatment)
- Product description, quantity, unit price
- ICMS calculation: base, rate, amount
- IPI calculation: base, rate, amount
- PIS and COFINS: base, rate, amount
- Total values for each tax
- Payment method and installments

## CNPJ Format
14 digits: `XX.XXX.XXX/XXXX-XX`
- Digits 1-8: Company registration
- Digits 9-12: Branch number (0001 = headquarters)
- Digits 13-14: Check digits

## Common Pitfalls
- Wrong CFOP code changes entire tax treatment
- ICMS-ST: tax already collected upstream, must not double-charge
- Interstate ICMS differential (DIFAL) for B2C sales to other states
- ISS vs ICMS classification for mixed goods+services
- NFe rejection by SEFAZ due to schema validation errors
- Different municipalities have different NFS-e systems and formats
- Tax benefits/incentives vary by state (ICMS war between states)
