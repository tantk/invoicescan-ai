# Incoterms 2020 — Delivery Terms Reference

## Overview
Incoterms (International Commercial Terms) are standardized by the International Chamber of Commerce (ICC). They define who pays for shipping, insurance, duties, and at what point risk transfers from seller to buyer. The current version is **Incoterms 2020** (effective January 1, 2020).

## Why Incoterms Matter for Invoice Processing
- **Tax implications**: FOB Destination vs FOB Origin affects US sales tax nexus
- **Duty/customs**: DDP means seller paid duties (included in invoice), EXW means buyer pays
- **Cost allocation**: Determines what's included in the invoice total
- **Risk transfer**: Determines who bears loss during transit
- **Insurance**: Some terms require seller to insure, others don't

## The 11 Incoterms 2020

### ANY Mode of Transport (7 terms)

| Code | Name | Seller Pays | Risk Transfers | Key Point |
|------|------|-------------|----------------|-----------|
| **EXW** | Ex Works | Nothing beyond making goods available | At seller's premises | Buyer arranges everything. Minimum seller obligation. |
| **FCA** | Free Carrier | Delivery to carrier at named place | When handed to carrier | Most versatile term. Replaces FOB for non-sea freight. |
| **CPT** | Carriage Paid To | Freight to destination | When handed to first carrier (NOT at destination!) | Seller pays freight but risk transfers early. |
| **CIP** | Carriage and Insurance Paid To | Freight + insurance to destination | When handed to first carrier | Like CPT but seller must insure. Insurance: 110% of CIP value, Institute Cargo Clauses A. |
| **DAP** | Delivered at Place | All transport to destination (NOT unloaded) | At destination, before unloading | Seller bears all risk until arrival. Buyer pays import duty + unloading. |
| **DPU** | Delivered at Place Unloaded | All transport + unloading | After unloading at destination | Only term requiring seller to unload. New in 2020 (replaced DAT). |
| **DDP** | Delivered Duty Paid | Everything including import duty + taxes | At destination | Maximum seller obligation. Buyer just receives goods. Import VAT/GST usually included. |

### SEA/Waterway Transport Only (4 terms)

| Code | Name | Seller Pays | Risk Transfers | Key Point |
|------|------|-------------|----------------|-----------|
| **FAS** | Free Alongside Ship | Delivery alongside vessel at port | Alongside the ship | Rarely used. Buyer arranges loading. |
| **FOB** | Free On Board | Loading onto vessel at port of shipment | Once on board the ship | Most common for sea freight. Buyer pays ocean freight + insurance. |
| **CFR** | Cost and Freight | Freight to destination port | Once on board at origin (NOT at destination!) | Seller pays freight but risk transfers at loading. |
| **CIF** | Cost, Insurance, and Freight | Freight + insurance to destination port | Once on board at origin | Like CFR but seller must insure. Insurance: 110% of CIF value, Institute Cargo Clauses C (minimum). |

## Common Usage by Region

### US Domestic
- **FOB Origin** (FOB Shipping Point): Buyer pays freight, owns goods in transit. Title transfers at seller's dock.
- **FOB Destination**: Seller pays freight, owns goods until delivery. Title transfers at buyer's dock.
- **US tax impact**: FOB Destination = seller has nexus at delivery location (may trigger sales tax obligation).
- Note: US "FOB" usage differs from international Incoterms FOB (which is sea-only).

### International Trade
- **EXW**: Common for B2B where buyer has logistics capability
- **FOB**: Most common for sea container shipments
- **CIF**: Common for bulk commodities
- **DDP**: Common for e-commerce and when seller handles everything
- **FCA**: Increasingly replacing FOB for container shipping (ICC recommendation)

### EU/Europe
- **DDP within EU**: No customs duties (single market), but VAT applies at destination
- **DAP to EU from outside**: Buyer handles import clearance and duties
- **FCA**: Recommended for container shipments (risk transfers at container terminal, not ship's rail)

## Impact on Invoice Amounts

| Incoterm | What's IN the invoice total | What's NOT in the invoice |
|----------|----------------------------|--------------------------|
| EXW | Goods only | Freight, insurance, duties, loading |
| FOB | Goods + loading onto ship | Ocean freight, insurance, duties |
| CIF | Goods + freight + insurance | Import duties, unloading |
| DDP | Everything (goods + freight + insurance + duties + taxes) | Nothing — total is total |

## How to Read Incoterms on an Invoice

Format: `INCOTERM [Named Place]`

Examples:
- `FOB Shanghai` — seller's responsibility ends when loaded on ship in Shanghai
- `CIF Rotterdam` — price includes cost + insurance + freight to Rotterdam
- `DDP New York` — seller pays everything including US import duties
- `EXW Munich` — buyer picks up at seller's warehouse in Munich
- `FCA Seller's Warehouse, Chicago` — seller delivers to carrier at Chicago warehouse
- `DAP Buyer's Warehouse, Tokyo` — seller delivers to Tokyo, buyer unloads

## Red Flags to Watch For
- **EXW + seller charges shipping**: Contradictory — shipping should be buyer's cost under EXW
- **CIF + buyer pays insurance**: Contradictory — CIF includes insurance
- **DDP + separate duty line item**: Duties should already be included in DDP price
- **FOB used for air freight**: Technically incorrect — FOB is sea-only. Should be FCA.
- **No named place specified**: Invalid — Incoterms require a named location
- **Using Incoterms 2010 codes**: DAT was replaced by DPU in 2020
