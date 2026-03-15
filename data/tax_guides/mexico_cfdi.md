# Mexico — CFDI Electronic Invoicing Guide

## Overview
Mexico's CFDI (Comprobante Fiscal Digital por Internet) is one of the world's most mature e-invoicing systems. All businesses must issue CFDIs for every transaction.

## Tax Rates
- **IVA (Value Added Tax): 16%** standard rate
- **IVA 0%**: Food, medicine, exports, agricultural machinery
- **IVA Exempt**: Medical services, education, residential rent, land sales, books
- **IEPS (Special Production and Services Tax)**: Varies — tobacco (160%), alcohol (26.5–53%), sugary drinks (1 peso/liter), fuel, pesticides
- **ISR (Income Tax Withholding)**: 10–35% on services, royalties, rent

## CFDI 4.0 (Current Version — since July 1, 2023)
### Key Changes from 3.3
- Mandatory: RFC, name, fiscal regime, and postal code for BOTH issuer and receiver
- Mandatory: Export indicator field
- Mandatory: Tax object field per line item (subject to tax, not subject, yes with exemption)
- Payment complement updated to version 2.0

### Required Fields
1. **Issuer (Emisor)**: RFC, name, fiscal regime code
2. **Receiver (Receptor)**: RFC, name, fiscal regime code, fiscal domicile (ZIP), tax use (CFDI use code)
3. **General**: Version (4.0), issue date/time, payment form, payment method, subtotal, discount, currency, exchange rate, total, invoice type, export indicator, UUID
4. **Per line item (Concepto)**: Product/service code (SAT catalog), unit code, quantity, description, unit price, amount, tax object code, taxes transferred/withheld per item (IVA, ISR, IEPS)
5. **Digital signature (Sello)**: SHA-256 hash signed with CSD certificate
6. **PAC certification**: Timbre Fiscal Digital — UUID, certification date, PAC RFC, PAC seal

## RFC Format
- **Companies**: 3 letters + 6 digits (YYMMDD) + 3 chars: `ABC123456XY9`
- **Individuals**: 4 letters + 6 digits + 3 chars: `ABCD123456XY9`
- Generic RFC for general public: `XAXX010101000`
- Foreign without RFC: `XEXX010101000`

## CFDI Types
- **I (Ingreso)**: Income — standard sales invoice
- **E (Egreso)**: Credit note / refund
- **T (Traslado)**: Transfer of goods (no payment)
- **N (Nómina)**: Payroll
- **P (Pago)**: Payment receipt complement (for deferred payments)

## Payment Complements
For invoices not paid immediately (PPD — Pago en Parcialidades o Diferido):
- Issue CFDI with payment method PPD
- When payment received, issue Complemento de Pago (REP) linking to original UUID
- Required within 5 days of payment

## Cancellation Rules
- Invoices can be cancelled, but must include reason code:
  - 01: Issued with errors — must provide replacement UUID
  - 02: Issued with errors — no replacement needed
  - 03: Operation not carried out
  - 04: Related to global invoice operation
- Cancellation within same month: immediate
- After month-end: receiver has 3 days to accept/reject

## SAT Product/Service Catalog
- 53,000+ product/service codes
- Must match the nature of the goods/services sold
- Common codes: 43231500 (software), 80141600 (consulting), 84111500 (accounting)

## Common Pitfalls
- Wrong CFDI Use code (receiver must confirm their intended use)
- Missing payment complements for PPD invoices
- RFC validation failures (name must match SAT records exactly)
- Cancellation rejected by receiver (auto-accepted after 3 days)
- IEPS not properly separated from IVA
- Using wrong product/service catalog code
- Not including exchange rate for foreign currency invoices
