"""Global tax engine — detect regime, validate calculations, check compliance.

This is the competitive advantage: handle ANY invoice from ANY country.
Detects the tax regime from invoice data, verifies math against that regime's
rules, and flags compliance issues.

Historical rate awareness: tax rates change over time. The engine checks
the invoice date and uses the rate that was valid at that time, not today's rate.
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

logger = logging.getLogger(__name__)


# ── Historical Rate Changes ───────────────────────────────────────────────
# Maps regime_code -> list of (effective_date, standard_rate, [reduced_rates])
# Sorted newest first. The engine walks this list to find the rate valid on
# the invoice date. Only notable changes are tracked.

RATE_HISTORY: dict[str, list[tuple]] = {
    "SG_GST": [
        (date(2024, 1, 1), 9.0, []),
        (date(2023, 1, 1), 8.0, []),
        (date(1994, 4, 1), 7.0, []),
    ],
    "ID_PPN": [
        (date(2025, 1, 1), 12.0, []),
        (date(2022, 4, 1), 11.0, []),
        (date(1984, 4, 1), 10.0, []),
    ],
    "CH_MWST": [
        (date(2024, 1, 1), 8.1, [2.6, 3.8]),
        (date(2018, 1, 1), 7.7, [2.5, 3.7]),
    ],
    "UK_VAT": [
        (date(2021, 10, 1), 20.0, [5.0]),    # Back to normal
        (date(2021, 4, 1), 20.0, [5.0]),      # Hospitality back to 12.5%
        (date(2020, 7, 15), 20.0, [5.0]),      # Hospitality temporary 5%
        (date(2011, 1, 4), 20.0, [5.0]),
        (date(2010, 1, 1), 17.5, [5.0]),
    ],
    "DE_UST": [
        (date(2021, 1, 1), 19.0, [7.0]),      # Back to normal
        (date(2020, 7, 1), 16.0, [5.0]),       # COVID temporary reduction
        (date(2007, 1, 1), 19.0, [7.0]),
    ],
    "SA_VAT": [
        (date(2020, 7, 1), 15.0, []),
        (date(2018, 1, 1), 5.0, []),
    ],
    "IN_GST": [
        (date(2017, 7, 1), 18.0, [0.0, 5.0, 12.0, 28.0]),
    ],
    "JP_CT": [
        (date(2019, 10, 1), 10.0, [8.0]),
        (date(2014, 4, 1), 8.0, []),
        (date(1997, 4, 1), 5.0, []),
    ],
    "AU_GST": [
        (date(2000, 7, 1), 10.0, []),
    ],
    "NZ_GST": [
        (date(2010, 10, 1), 15.0, []),
        (date(1989, 7, 1), 12.5, []),
    ],
    "AE_VAT": [
        (date(2018, 1, 1), 5.0, []),
    ],
    "TR_KDV": [
        (date(2023, 7, 10), 20.0, [1.0, 10.0]),
        (date(2019, 1, 1), 18.0, [1.0, 8.0]),
    ],
    "EG_VAT": [
        (date(2016, 9, 8), 14.0, []),
        (date(2016, 9, 7), 13.0, []),         # Brief transitional
    ],
    "NG_VAT": [
        (date(2020, 2, 1), 7.5, []),
        (date(1994, 1, 1), 5.0, []),
    ],
    "VN_VAT": [
        (date(2024, 1, 1), 10.0, [5.0, 8.0]),  # 8% temporary ended
        (date(2022, 2, 1), 10.0, [5.0, 8.0]),   # 8% temporary reduction
    ],
    "RO_TVA": [
        (date(2025, 8, 1), 21.0, [5.0, 11.0]),  # Increased from 19%
        (date(2017, 1, 1), 19.0, [5.0, 9.0]),
    ],
    "PL_VAT": [
        (date(2011, 1, 1), 23.0, [5.0, 8.0]),
        (date(2004, 5, 1), 22.0, [7.0]),
    ],
    # Bahrain doubled VAT
    "BH_VAT": [
        (date(2022, 1, 1), 10.0, []),
        (date(2019, 1, 1), 5.0, []),
    ],
    # Finland increased in 2024
    "FI_ALV": [
        (date(2024, 9, 1), 25.5, [10.0, 14.0]),
        (date(2013, 1, 1), 24.0, [10.0, 14.0]),
    ],
    # Hungary
    "HU_AFA": [
        (date(2012, 1, 1), 27.0, [5.0, 18.0]),
        (date(2009, 7, 1), 25.0, [5.0, 18.0]),
    ],
    # Netherlands accommodation rate change
    "NL_BTW": [
        (date(2026, 1, 1), 21.0, [9.0]),       # Accommodation to 21%
        (date(2019, 1, 1), 21.0, [9.0]),
        (date(2012, 10, 1), 21.0, [6.0]),
    ],
}


def get_rate_for_date(regime_code: str, invoice_date: Optional[date] = None) -> Optional[tuple]:
    """Look up the correct tax rate for an invoice date.

    Returns (standard_rate, reduced_rates) valid on that date,
    or None if no history exists (use current TaxRegime rate).
    """
    if regime_code not in RATE_HISTORY:
        return None

    if invoice_date is None:
        return None

    history = RATE_HISTORY[regime_code]
    for effective_date, std_rate, reduced in history:
        if invoice_date >= effective_date:
            return (std_rate, reduced)

    # Invoice predates all records — return oldest known
    if history:
        _, std_rate, reduced = history[-1]
        return (std_rate, reduced)

    return None


# ── Tax Regime Definitions ────────────────────────────────────────────────


@dataclass
class TaxRegime:
    """Defines rules for a country/region's tax system."""
    code: str
    name: str
    country: str
    tax_id_label: str
    tax_id_pattern: str  # regex
    standard_rate: float  # primary rate as percentage (current)
    reduced_rates: list[float] = field(default_factory=list)
    tax_components: list[str] = field(default_factory=list)  # e.g., ["CGST", "SGST"]
    compound: bool = False  # tax on tax
    required_fields: list[str] = field(default_factory=list)
    notes: str = ""


TAX_REGIMES = {
    # ── United States ─────────────────────────────────────────────────
    "US": TaxRegime(
        code="US",
        name="US Sales Tax",
        country="United States",
        tax_id_label="EIN/FEIN",
        tax_id_pattern=r"\d{2}-\d{7}",
        standard_rate=0.0,  # Varies by jurisdiction
        tax_components=["State Tax", "County Tax", "City Tax", "Special District Tax"],
        required_fields=["supplier_name", "invoice_id", "invoice_date", "total_amount"],
        notes="Rates vary by state/county/city (0-13%). No federal sales tax. Some items exempt.",
    ),

    # ── European Union (VAT) ──────────────────────────────────────────
    "EU_VAT": TaxRegime(
        code="EU_VAT",
        name="EU VAT",
        country="European Union",
        tax_id_label="VAT Number",
        tax_id_pattern=r"[A-Z]{2}\d{8,12}",
        standard_rate=20.0,  # Varies 17-27% by member state
        reduced_rates=[5.0, 9.0, 10.0, 12.0, 13.0],
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "receiver_name", "receiver_tax_id",
            "invoice_id", "invoice_date", "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="Must show both seller and buyer VAT numbers. Reverse charge for B2B cross-border.",
    ),

    # ── United Kingdom ────────────────────────────────────────────────
    "UK_VAT": TaxRegime(
        code="UK_VAT",
        name="UK VAT",
        country="United Kingdom",
        tax_id_label="VAT Number",
        tax_id_pattern=r"GB\d{9}",
        standard_rate=20.0,
        reduced_rates=[5.0, 0.0],
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="Domestic reverse charge for construction (CIS). Making Tax Digital.",
    ),

    # ── India (GST) ───────────────────────────────────────────────────
    "IN_GST": TaxRegime(
        code="IN_GST",
        name="India GST",
        country="India",
        tax_id_label="GSTIN",
        tax_id_pattern=r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}",
        standard_rate=18.0,
        reduced_rates=[0.0, 5.0, 12.0, 28.0],
        tax_components=["CGST", "SGST", "IGST", "Cess"],
        compound=True,  # Cess can be on tax
        required_fields=[
            "supplier_name", "supplier_tax_id", "receiver_tax_id", "invoice_id",
            "invoice_date", "net_amount", "total_amount",
        ],
        notes="CGST+SGST for intrastate, IGST for interstate. HSN/SAC codes required.",
    ),

    # ── Japan ─────────────────────────────────────────────────────────
    "JP_CT": TaxRegime(
        code="JP_CT",
        name="Japan Consumption Tax",
        country="Japan",
        tax_id_label="QIIN (Qualified Invoice Issuer Number)",
        tax_id_pattern=r"T\d{13}",
        standard_rate=10.0,
        reduced_rates=[8.0],  # Food & beverages
        tax_components=["Consumption Tax"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="8% for food/beverages, 10% standard. QIIN required for input tax credits.",
    ),

    # ── Australia ─────────────────────────────────────────────────────
    "AU_GST": TaxRegime(
        code="AU_GST",
        name="Australia GST",
        country="Australia",
        tax_id_label="ABN",
        tax_id_pattern=r"\d{2}\s?\d{3}\s?\d{3}\s?\d{3}",
        standard_rate=10.0,
        tax_components=["GST"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_amount",
        ],
        notes="ABN mandatory. Tax invoice required for sales >A$82.50. GST = 1/11 of total.",
    ),

    # ── China ─────────────────────────────────────────────────────────
    "CN_VAT": TaxRegime(
        code="CN_VAT",
        name="China VAT (Fapiao)",
        country="China",
        tax_id_label="Tax Registration Number",
        tax_id_pattern=r"\d{15,20}",
        standard_rate=13.0,
        reduced_rates=[6.0, 9.0, 0.0],
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="Fapiao system. Special VAT fapiao needed for input credits. QR code mandatory.",
    ),

    # ── Saudi Arabia ──────────────────────────────────────────────────
    "SA_VAT": TaxRegime(
        code="SA_VAT",
        name="Saudi Arabia VAT (ZATCA)",
        country="Saudi Arabia",
        tax_id_label="TRN (Tax Registration Number)",
        tax_id_pattern=r"3\d{14}",
        standard_rate=15.0,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="ZATCA e-invoicing mandatory. QR code + digital signature required.",
    ),

    # ── Brazil ────────────────────────────────────────────────────────
    "BR_NF": TaxRegime(
        code="BR_NF",
        name="Brazil Nota Fiscal",
        country="Brazil",
        tax_id_label="CNPJ",
        tax_id_pattern=r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}",
        standard_rate=0.0,  # Multiple taxes, no single rate
        tax_components=["ICMS", "IPI", "PIS", "COFINS", "ISS"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="Multiple overlapping federal/state/municipal taxes. SEFAZ real-time validation.",
    ),

    # ── Mexico ────────────────────────────────────────────────────────
    "MX_CFDI": TaxRegime(
        code="MX_CFDI",
        name="Mexico CFDI",
        country="Mexico",
        tax_id_label="RFC",
        tax_id_pattern=r"[A-Z&Ñ]{3,4}\d{6}[A-Z\d]{3}",
        standard_rate=16.0,
        reduced_rates=[0.0, 8.0],
        tax_components=["IVA", "ISR", "IEPS"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="CFDI 4.0 mandatory. PAC certification + UUID required.",
    ),

    # ── UAE ────────────────────────────────────────────────────────────
    "AE_VAT": TaxRegime(
        code="AE_VAT",
        name="UAE VAT",
        country="UAE",
        tax_id_label="TRN",
        tax_id_pattern=r"\d{15}",
        standard_rate=5.0,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="5% standard VAT. Simplified invoice allowed under AED 10,000.",
    ),

    # ── Malaysia ───────────────────────────────────────────────────────
    "MY_SST": TaxRegime(
        code="MY_SST",
        name="Malaysia SST",
        country="Malaysia",
        tax_id_label="SST Registration Number",
        tax_id_pattern=r"[A-Z]\d{2}-\d{4}-\d{8}",
        standard_rate=10.0,  # Sales tax; service tax is 8%
        reduced_rates=[5.0, 6.0, 8.0],
        tax_components=["Sales Tax", "Service Tax"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="Sales Tax (5-10%) and Service Tax (6-8%). MyInvois e-invoicing rollout.",
    ),

    # ── Singapore ──────────────────────────────────────────────────────
    "SG_GST": TaxRegime(
        code="SG_GST",
        name="Singapore GST",
        country="Singapore",
        tax_id_label="GST Registration Number",
        tax_id_pattern=r"\d{9}[A-Z]",
        standard_rate=9.0,
        tax_components=["GST"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="9% GST (raised from 8% in Jan 2024).",
    ),

    # ── South Africa ───────────────────────────────────────────────────
    "ZA_VAT": TaxRegime(
        code="ZA_VAT",
        name="South Africa VAT",
        country="South Africa",
        tax_id_label="VAT Number",
        tax_id_pattern=r"4\d{9}",
        standard_rate=15.0,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="Full tax invoice for >R5,000. Abridged invoice for <=R5,000.",
    ),

    # ── South Korea ───────────────────────────────────────────────────
    "KR_VAT": TaxRegime(
        code="KR_VAT",
        name="South Korea VAT",
        country="South Korea",
        tax_id_label="BRN (Business Registration Number)",
        tax_id_pattern=r"\d{3}-\d{2}-\d{5}",
        standard_rate=10.0,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="10% VAT. Mandatory e-tax invoice via NTS HomeTax. Next-day transmission.",
    ),

    # ── Canada ────────────────────────────────────────────────────────
    "CA_GST": TaxRegime(
        code="CA_GST",
        name="Canada GST/HST",
        country="Canada",
        tax_id_label="BN (Business Number)",
        tax_id_pattern=r"\d{9}\s?RT\s?\d{4}",
        standard_rate=5.0,  # GST only; HST varies 13-15% by province
        reduced_rates=[13.0, 15.0],  # HST rates
        tax_components=["GST", "HST", "PST", "QST"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="GST 5% federal. HST 13-15% in some provinces. PST/QST separate in others.",
    ),

    # ── Thailand ──────────────────────────────────────────────────────
    "TH_VAT": TaxRegime(
        code="TH_VAT",
        name="Thailand VAT",
        country="Thailand",
        tax_id_label="Tax ID",
        tax_id_pattern=r"\d{13}",
        standard_rate=7.0,  # Reduced from 10% since 1999
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="7% (legally 10%, reduced by decree). Withholding tax on services complicates payments.",
    ),

    # ── Indonesia ─────────────────────────────────────────────────────
    "ID_PPN": TaxRegime(
        code="ID_PPN",
        name="Indonesia PPN (VAT)",
        country="Indonesia",
        tax_id_label="NPWP",
        tax_id_pattern=r"\d{2}\.?\d{3}\.?\d{3}\.?\d-?\d{3}\.?\d{3}",
        standard_rate=12.0,  # Increased from 11% on Jan 1, 2025
        tax_components=["PPN", "PPnBM"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="12% PPN (since Jan 2025). Mandatory e-Faktur via DJP. PPnBM for luxury goods.",
    ),

    # ── Turkey ────────────────────────────────────────────────────────
    "TR_KDV": TaxRegime(
        code="TR_KDV",
        name="Turkey KDV (VAT)",
        country="Turkey",
        tax_id_label="VKN (Tax ID)",
        tax_id_pattern=r"\d{10}",
        standard_rate=20.0,  # Increased from 18% in July 2023
        reduced_rates=[1.0, 10.0],
        tax_components=["KDV"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="20% standard. Mandatory e-Fatura (UBL-TR). KDV withholding on many services.",
    ),

    # ── Philippines ───────────────────────────────────────────────────
    "PH_VAT": TaxRegime(
        code="PH_VAT",
        name="Philippines VAT",
        country="Philippines",
        tax_id_label="TIN",
        tax_id_pattern=r"\d{3}-\d{3}-\d{3}-\d{3}",
        standard_rate=12.0,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="12% VAT. Separate Sales Invoice (goods) vs Official Receipt (services). BIR permit required.",
    ),

    # ── Germany ───────────────────────────────────────────────────────
    "DE_UST": TaxRegime(
        code="DE_UST",
        name="Germany USt/MwSt (VAT)",
        country="Germany",
        tax_id_label="USt-IdNr",
        tax_id_pattern=r"DE\d{9}",
        standard_rate=19.0,
        reduced_rates=[7.0],
        tax_components=["USt"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="19% standard, 7% reduced. Mandatory B2B e-invoicing from 2025 (XRechnung/ZUGFeRD).",
    ),

    # ── Nigeria ───────────────────────────────────────────────────────
    "NG_VAT": TaxRegime(
        code="NG_VAT",
        name="Nigeria VAT",
        country="Nigeria",
        tax_id_label="TIN",
        tax_id_pattern=r"\d{8}-\d{4}",
        standard_rate=7.5,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="7.5% VAT. No registration threshold — ALL businesses must register.",
    ),

    # ── Kenya ─────────────────────────────────────────────────────────
    "KE_VAT": TaxRegime(
        code="KE_VAT",
        name="Kenya VAT",
        country="Kenya",
        tax_id_label="KRA PIN",
        tax_id_pattern=r"[A-Z]\d{9}[A-Z]",
        standard_rate=16.0,
        reduced_rates=[8.0],
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="16% VAT. Mandatory eTIMS e-invoicing with QR code since Sept 2024.",
    ),

    # ── Egypt ─────────────────────────────────────────────────────────
    "EG_VAT": TaxRegime(
        code="EG_VAT",
        name="Egypt VAT",
        country="Egypt",
        tax_id_label="Tax Registration Number",
        tax_id_pattern=r"\d{9}",
        standard_rate=14.0,
        tax_components=["VAT", "Table Tax"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="14% VAT. Table tax may apply ON TOP of VAT for certain goods. Mandatory e-invoicing.",
    ),

    # ── Vietnam ───────────────────────────────────────────────────────
    "VN_VAT": TaxRegime(
        code="VN_VAT",
        name="Vietnam VAT (GTGT)",
        country="Vietnam",
        tax_id_label="Tax Code",
        tax_id_pattern=r"\d{10}(\d{3})?",
        standard_rate=10.0,
        reduced_rates=[5.0, 8.0],
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="10% standard (8% temporary for some goods). Mandatory e-invoicing since July 2022.",
    ),

    # ── New Zealand ───────────────────────────────────────────────────
    "NZ_GST": TaxRegime(
        code="NZ_GST",
        name="New Zealand GST",
        country="New Zealand",
        tax_id_label="IRD Number",
        tax_id_pattern=r"\d{8,9}",
        standard_rate=15.0,
        tax_components=["GST"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="15% GST. Very broad base — most things taxable. GST = 3/23 of inclusive price.",
    ),

    # ── Colombia ──────────────────────────────────────────────────────
    "CO_IVA": TaxRegime(
        code="CO_IVA",
        name="Colombia IVA",
        country="Colombia",
        tax_id_label="NIT",
        tax_id_pattern=r"\d{9}-?\d",
        standard_rate=19.0,
        reduced_rates=[5.0],
        tax_components=["IVA", "ReteFuente", "ReteIVA", "ReteICA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="19% IVA. Up to 3 withholding taxes on one invoice (ReteFuente, ReteIVA, ReteICA). Mandatory e-invoicing via DIAN.",
    ),

    # ── Israel ────────────────────────────────────────────────────────
    "IL_VAT": TaxRegime(
        code="IL_VAT",
        name="Israel VAT (Ma'am)",
        country="Israel",
        tax_id_label="Tax File Number",
        tax_id_pattern=r"\d{9}",
        standard_rate=18.0,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="18% VAT. SHAAM CTC clearance model mandatory 2026. Zero-rated exports.",
    ),

    # ── Poland ────────────────────────────────────────────────────────
    "PL_VAT": TaxRegime(
        code="PL_VAT",
        name="Poland VAT",
        country="Poland",
        tax_id_label="NIP",
        tax_id_pattern=r"PL\d{10}|\d{10}",
        standard_rate=23.0,
        reduced_rates=[5.0, 8.0],
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "receiver_tax_id", "invoice_id",
            "invoice_date", "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="23% standard. KSeF mandatory e-invoicing. 8% construction/food service, 5% basic food/books.",
    ),

    # ── Italy ─────────────────────────────────────────────────────────
    "IT_IVA": TaxRegime(
        code="IT_IVA",
        name="Italy IVA",
        country="Italy",
        tax_id_label="Partita IVA",
        tax_id_pattern=r"IT\d{11}|\d{11}",
        standard_rate=22.0,
        reduced_rates=[4.0, 5.0, 10.0],
        tax_components=["IVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "receiver_tax_id", "invoice_id",
            "invoice_date", "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="22% standard. Mandatory e-invoicing via SDI (FatturaPA XML) since 2019. First EU country with full B2B mandate.",
    ),

    # ── France ────────────────────────────────────────────────────────
    "FR_TVA": TaxRegime(
        code="FR_TVA",
        name="France TVA",
        country="France",
        tax_id_label="Numéro de TVA",
        tax_id_pattern=r"FR\d{2}\d{9}|FR[A-Z]{2}\d{9}",
        standard_rate=20.0,
        reduced_rates=[2.1, 5.5, 10.0],
        tax_components=["TVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="20% standard. Mandatory B2B e-invoicing from 2026 (Factur-X/Chorus Pro). 5.5% food/books, 10% restaurants/transport.",
    ),

    # ── Spain ─────────────────────────────────────────────────────────
    "ES_IVA": TaxRegime(
        code="ES_IVA",
        name="Spain IVA",
        country="Spain",
        tax_id_label="NIF/CIF",
        tax_id_pattern=r"ES[A-Z]\d{8}|ES\d{8}[A-Z]",
        standard_rate=21.0,
        reduced_rates=[4.0, 10.0],
        tax_components=["IVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="21% standard. SII real-time invoice reporting mandatory for large companies. Canary Islands use IGIC (7%) not IVA.",
    ),

    # ── Netherlands ───────────────────────────────────────────────────
    "NL_BTW": TaxRegime(
        code="NL_BTW",
        name="Netherlands BTW",
        country="Netherlands",
        tax_id_label="BTW-nummer",
        tax_id_pattern=r"NL\d{9}B\d{2}",
        standard_rate=21.0,
        reduced_rates=[9.0],
        tax_components=["BTW"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="21% standard, 9% reduced (food, books, medicine, hotels, culture). KvK number often on invoices.",
    ),

    # ── Sweden ────────────────────────────────────────────────────────
    "SE_MOMS": TaxRegime(
        code="SE_MOMS",
        name="Sweden Moms",
        country="Sweden",
        tax_id_label="Momsregistreringsnummer",
        tax_id_pattern=r"SE\d{12}",
        standard_rate=25.0,
        reduced_rates=[6.0, 12.0],
        tax_components=["Moms"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="25% standard (one of highest in world). 12% food/restaurants/hotels. 6% books/newspapers/transport/culture.",
    ),

    # ── Switzerland ───────────────────────────────────────────────────
    "CH_MWST": TaxRegime(
        code="CH_MWST",
        name="Switzerland MWST/TVA",
        country="Switzerland",
        tax_id_label="MWST/TVA/IVA Number",
        tax_id_pattern=r"CHE-?\d{3}\.?\d{3}\.?\d{3}\s?MWST|CHE-?\d{3}\.?\d{3}\.?\d{3}",
        standard_rate=8.1,
        reduced_rates=[2.6, 3.8],
        tax_components=["MWST"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="8.1% standard (increased from 7.7% Jan 2024). NOT in EU. 2.6% food/medicine/books/newspapers. 3.8% hotels.",
    ),

    # ── Taiwan ────────────────────────────────────────────────────────
    "TW_BT": TaxRegime(
        code="TW_BT",
        name="Taiwan Business Tax",
        country="Taiwan",
        tax_id_label="GUI Number (Unified Business Number)",
        tax_id_pattern=r"\d{8}",
        standard_rate=5.0,
        tax_components=["Business Tax"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="5% Business Tax. Government Uniform Invoice (GUI) system. E-invoice via MIC platform.",
    ),

    # ── Argentina ─────────────────────────────────────────────────────
    "AR_IVA": TaxRegime(
        code="AR_IVA",
        name="Argentina IVA",
        country="Argentina",
        tax_id_label="CUIT",
        tax_id_pattern=r"\d{2}-\d{8}-\d",
        standard_rate=21.0,
        reduced_rates=[10.5, 27.0],
        tax_components=["IVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="21% standard. 27% utilities. 10.5% construction/transport/some food. Mandatory e-invoicing via AFIP.",
    ),

    # ── Chile ─────────────────────────────────────────────────────────
    "CL_IVA": TaxRegime(
        code="CL_IVA",
        name="Chile IVA",
        country="Chile",
        tax_id_label="RUT",
        tax_id_pattern=r"\d{1,2}\.?\d{3}\.?\d{3}-?[\dkK]",
        standard_rate=19.0,
        tax_components=["IVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="19% IVA. Mandatory DTE e-invoicing via SII since 2014. One of earliest e-invoicing mandates in world.",
    ),

    # ── Peru ──────────────────────────────────────────────────────────
    "PE_IGV": TaxRegime(
        code="PE_IGV",
        name="Peru IGV",
        country="Peru",
        tax_id_label="RUC",
        tax_id_pattern=r"\d{11}",
        standard_rate=18.0,  # 16% IGV + 2% IPM
        tax_components=["IGV", "IPM"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="18% (16% IGV + 2% IPM municipal). Mandatory CPE e-invoicing via SUNAT.",
    ),

    # ── Pakistan ──────────────────────────────────────────────────────
    "PK_ST": TaxRegime(
        code="PK_ST",
        name="Pakistan Sales Tax",
        country="Pakistan",
        tax_id_label="NTN/STRN",
        tax_id_pattern=r"\d{7}-?\d",
        standard_rate=18.0,
        reduced_rates=[0.0, 5.0, 10.0, 12.0],
        tax_components=["Sales Tax", "FED"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="18% standard. FBR administers. IRIS e-invoicing for Tier-1 retailers. Provincial services tax varies.",
    ),

    # ── Bangladesh ────────────────────────────────────────────────────
    "BD_VAT": TaxRegime(
        code="BD_VAT",
        name="Bangladesh VAT",
        country="Bangladesh",
        tax_id_label="BIN (Business Identification Number)",
        tax_id_pattern=r"\d{13}",
        standard_rate=15.0,
        reduced_rates=[5.0, 7.5, 10.0],
        tax_components=["VAT", "SD"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="15% standard. EFD/SDC (Electronic Fiscal Device) mandatory for select sectors. SD (Supplementary Duty) on luxury items.",
    ),

    # ── Sri Lanka ─────────────────────────────────────────────────────
    "LK_VAT": TaxRegime(
        code="LK_VAT",
        name="Sri Lanka VAT",
        country="Sri Lanka",
        tax_id_label="TIN",
        tax_id_pattern=r"\d{9}",
        standard_rate=18.0,
        tax_components=["VAT", "SSCL", "NBT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="18% VAT. SSCL (Social Security Contribution Levy) 2.5%. Frequent rate changes — verify current rates.",
    ),

    # ── Ghana ─────────────────────────────────────────────────────────
    "GH_VAT": TaxRegime(
        code="GH_VAT",
        name="Ghana VAT",
        country="Ghana",
        tax_id_label="TIN",
        tax_id_pattern=r"[A-Z]\d{10}",
        standard_rate=15.0,  # VAT alone; combined with levies = 21.9%
        tax_components=["VAT", "NHIL", "GETFund", "COVID Levy"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="15% VAT + 2.5% NHIL + 2.5% GETFund + 1% COVID levy = 21% combined. E-VAT system. GRA certified invoicing.",
    ),

    # ── Tanzania ──────────────────────────────────────────────────────
    "TZ_VAT": TaxRegime(
        code="TZ_VAT",
        name="Tanzania VAT",
        country="Tanzania",
        tax_id_label="TIN",
        tax_id_pattern=r"\d{9}",
        standard_rate=18.0,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="18% VAT. Mandatory EFD (Electronic Fiscal Device) for all VAT-registered businesses. TRA administers.",
    ),

    # ── Morocco ───────────────────────────────────────────────────────
    "MA_TVA": TaxRegime(
        code="MA_TVA",
        name="Morocco TVA",
        country="Morocco",
        tax_id_label="ICE (Identifiant Commun de l'Entreprise)",
        tax_id_pattern=r"\d{15}",
        standard_rate=20.0,
        reduced_rates=[7.0, 10.0, 14.0],
        tax_components=["TVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="20% standard. 14% transport/energy. 10% hotels/restaurants/some food. 7% basic necessities/water. DGI administers.",
    ),

    # ── Romania ───────────────────────────────────────────────────────
    "RO_TVA": TaxRegime(
        code="RO_TVA",
        name="Romania TVA",
        country="Romania",
        tax_id_label="CUI/CIF",
        tax_id_pattern=r"RO\d{2,10}",
        standard_rate=19.0,
        reduced_rates=[5.0, 9.0],
        tax_components=["TVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "receiver_tax_id", "invoice_id",
            "invoice_date", "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="19% standard. Mandatory RO e-Factura (B2B) since 2024. 9% food/accommodation/restaurants. 5% housing/books.",
    ),

    # ── Bahrain ───────────────────────────────────────────────────────
    "BH_VAT": TaxRegime(
        code="BH_VAT",
        name="Bahrain VAT",
        country="Bahrain",
        tax_id_label="VAT Registration Number",
        tax_id_pattern=r"\d{15}",
        standard_rate=10.0,  # Doubled from 5% in Jan 2022
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="10% VAT (doubled from 5% in Jan 2022). Check invoice date — pre-2022 invoices are 5%.",
    ),

    # ── Oman ──────────────────────────────────────────────────────────
    "OM_VAT": TaxRegime(
        code="OM_VAT",
        name="Oman VAT",
        country="Oman",
        tax_id_label="VAT Number",
        tax_id_pattern=r"OM\d{10}",
        standard_rate=5.0,
        tax_components=["VAT"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="5% VAT since April 2021. Zero-rated: exports, international transport, education, healthcare.",
    ),

    # ── Denmark ───────────────────────────────────────────────────────
    "DK_MOMS": TaxRegime(
        code="DK_MOMS",
        name="Denmark Moms",
        country="Denmark",
        tax_id_label="CVR/SE Number",
        tax_id_pattern=r"DK\d{8}",
        standard_rate=25.0,
        tax_components=["Moms"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="25% — NO reduced rate (one of few EU countries with single rate). Newspapers zero-rated.",
    ),

    # ── Norway ────────────────────────────────────────────────────────
    "NO_MVA": TaxRegime(
        code="NO_MVA",
        name="Norway MVA",
        country="Norway",
        tax_id_label="MVA Number",
        tax_id_pattern=r"\d{9}MVA",
        standard_rate=25.0,
        reduced_rates=[12.0, 15.0],
        tax_components=["MVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="25% standard. 15% food. 12% transport/cinema/hotels. NOT EU but EEA member.",
    ),

    # ── Finland ───────────────────────────────────────────────────────
    "FI_ALV": TaxRegime(
        code="FI_ALV",
        name="Finland ALV",
        country="Finland",
        tax_id_label="ALV/FO Number",
        tax_id_pattern=r"FI\d{8}",
        standard_rate=25.5,  # Increased from 24% Sep 2024 — HIGHEST IN EU
        reduced_rates=[10.0, 14.0],
        tax_components=["ALV"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="25.5% (highest in EU, increased from 24% in Sep 2024). 14% food/restaurants. 10% books/transport/medicine.",
    ),

    # ── Hungary ───────────────────────────────────────────────────────
    "HU_AFA": TaxRegime(
        code="HU_AFA",
        name="Hungary ÁFA",
        country="Hungary",
        tax_id_label="Tax Number",
        tax_id_pattern=r"HU\d{8}|\d{8}-\d-\d{2}",
        standard_rate=27.0,  # HIGHEST VAT IN THE WORLD
        reduced_rates=[5.0, 18.0],
        tax_components=["ÁFA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "receiver_tax_id", "invoice_id",
            "invoice_date", "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="27% — HIGHEST VAT IN THE WORLD. 18% food service/catering. 5% food/books/new housing. Real-time RTIR reporting.",
    ),

    # ── Czech Republic ────────────────────────────────────────────────
    "CZ_DPH": TaxRegime(
        code="CZ_DPH",
        name="Czech Republic DPH",
        country="Czech Republic",
        tax_id_label="DIČ",
        tax_id_pattern=r"CZ\d{8,10}",
        standard_rate=21.0,
        reduced_rates=[12.0],
        tax_components=["DPH"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date",
            "net_amount", "total_tax_amount", "total_amount",
        ],
        notes="21% standard. 12% reduced (merged from 15%+10% in Jan 2024). Covers food, transport, books, accommodation.",
    ),

    # ── Hong Kong (NO VAT) ────────────────────────────────────────────
    "HK_NONE": TaxRegime(
        code="HK_NONE",
        name="Hong Kong (No VAT/GST)",
        country="Hong Kong",
        tax_id_label="BRN (Business Registration Number)",
        tax_id_pattern=r"\d{8}-\d{3}-\d{2}-\d{2}-\d",
        standard_rate=0.0,
        tax_components=[],
        required_fields=[
            "supplier_name", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="NO VAT, GST, or sales tax. Any tax charge on an HK invoice is likely an error or foreign tax.",
    ),

    # ── Uruguay ───────────────────────────────────────────────────────
    "UY_IVA": TaxRegime(
        code="UY_IVA",
        name="Uruguay IVA",
        country="Uruguay",
        tax_id_label="RUT/RUC",
        tax_id_pattern=r"\d{12}",
        standard_rate=22.0,
        reduced_rates=[10.0],
        tax_components=["IVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="22% standard. 10% reduced (hotels, health, some food). DGI e-invoicing (CFE) mandatory.",
    ),

    # ── Ecuador ───────────────────────────────────────────────────────
    "EC_IVA": TaxRegime(
        code="EC_IVA",
        name="Ecuador IVA",
        country="Ecuador",
        tax_id_label="RUC",
        tax_id_pattern=r"\d{13}",
        standard_rate=15.0,  # Increased from 12% Apr 2024
        tax_components=["IVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="15% IVA (increased from 12% in Apr 2024). Check invoice date for old rate. SRI e-invoicing mandatory.",
    ),

    # ── Costa Rica ────────────────────────────────────────────────────
    "CR_IVA": TaxRegime(
        code="CR_IVA",
        name="Costa Rica IVA",
        country="Costa Rica",
        tax_id_label="Cédula Jurídica",
        tax_id_pattern=r"\d{9,12}",
        standard_rate=13.0,
        reduced_rates=[1.0, 2.0, 4.0],
        tax_components=["IVA"],
        required_fields=[
            "supplier_name", "supplier_tax_id", "invoice_id", "invoice_date", "total_amount",
        ],
        notes="13% standard. 4% health services. 2% education. 1% basic food basket. Mandatory e-invoicing.",
    ),
}


# ── Industry Detection ────────────────────────────────────────────────────


INDUSTRY_MARKERS = {
    "construction": {
        "keywords": [
            "retainage", "retention", "change order", "progress billing",
            "aia g702", "aia g703", "schedule of values", "substantial completion",
            "contractor", "subcontractor", "lien waiver",
        ],
        "label": "Construction",
        "special_fields": ["retainage", "percent_complete", "contract_sum", "change_orders"],
    },
    "healthcare": {
        "keywords": [
            "cpt", "icd-10", "icd10", "hcpcs", "npi", "diagnosis",
            "cms-1500", "ub-04", "patient", "claim", "copay", "deductible",
            "prior authorization", "insurance",
        ],
        "label": "Healthcare",
        "special_fields": ["patient_id", "npi", "cpt_codes", "diagnosis_codes"],
    },
    "legal": {
        "keywords": [
            "billable hours", "matter number", "matter #", "timekeeper",
            "ledes", "utbms", "retainer", "paralegal", "associate", "partner",
            "court filing", "deposition",
        ],
        "label": "Legal",
        "special_fields": ["matter_number", "timekeeper", "hours", "billing_rate"],
    },
    "freight": {
        "keywords": [
            "bill of lading", "bol", "pro number", "container",
            "demurrage", "detention", "freight", "carrier", "vessel",
            "liftgate", "accessorial", "chargeable weight",
        ],
        "label": "Freight/Logistics",
        "special_fields": ["bol_number", "pro_number", "container_number", "weight"],
    },
    "saas": {
        "keywords": [
            "subscription", "monthly plan", "annual plan", "per seat",
            "api calls", "usage", "overage", "proration", "prorated",
            "billing period", "renewal", "tier", "license",
        ],
        "label": "SaaS/Technology",
        "special_fields": ["plan_name", "billing_period", "seats", "usage_quantity"],
    },
    "hospitality": {
        "keywords": [
            "folio", "room charge", "check-in", "check-out", "nightly rate",
            "occupancy tax", "lodging tax", "tourism tax", "resort fee",
            "minibar", "room service", "guest name",
        ],
        "label": "Hospitality",
        "special_fields": ["guest_name", "room_number", "checkin_date", "checkout_date"],
    },
    "manufacturing": {
        "keywords": [
            "bill of materials", "bom", "lot number", "batch number",
            "serial number", "part number", "heat number", "material grade",
            "inspection certificate",
        ],
        "label": "Manufacturing",
        "special_fields": ["part_number", "lot_number", "serial_number", "bom"],
    },
    "international_trade": {
        "keywords": [
            "fob", "cif", "ddp", "exw", "fca", "cpt", "cip", "dap", "dpu",
            "cfr", "fas", "incoterm", "port of loading", "port of discharge",
            "country of origin", "hs code", "tariff", "customs", "duty",
            "certificate of origin", "commercial invoice", "packing list",
            "letter of credit", "bill of lading", "airway bill",
        ],
        "label": "International Trade",
        "special_fields": [
            "incoterm", "incoterm_location", "port_of_loading",
            "port_of_discharge", "country_of_origin", "hs_code",
        ],
    },
}


# ── Detection Functions ───────────────────────────────────────────────────


def _detect_regime_from_tax_ids(fields: dict) -> Optional[str]:
    """Match tax ID patterns to identify the regime."""
    tax_id_fields = ["supplier_tax_id", "receiver_tax_id"]

    for field_name in tax_id_fields:
        if field_name not in fields:
            continue
        tax_id = fields[field_name].get("value", "") if isinstance(fields[field_name], dict) else str(fields[field_name])
        tax_id = tax_id.strip()

        if not tax_id:
            continue

        for code, regime in TAX_REGIMES.items():
            if re.search(regime.tax_id_pattern, tax_id):
                return code

    return None


def _detect_regime_from_fields(fields: dict) -> Optional[str]:
    """Detect regime from field names and values."""
    field_keys = set(fields.keys())
    all_text = " ".join(
        str(v.get("value", "") if isinstance(v, dict) else v)
        for v in fields.values()
    ).lower()

    # India GST: look for CGST/SGST/IGST fields or mentions
    gst_markers = {"cgst", "sgst", "igst", "gstin", "hsn"}
    if gst_markers & set(all_text.split()):
        return "IN_GST"

    # Japan: QIIN pattern
    if re.search(r"T\d{13}", all_text):
        return "JP_CT"

    # Australia: ABN
    if "abn" in all_text:
        return "AU_GST"

    # Brazil: CNPJ or NF-e
    if "cnpj" in all_text or "nota fiscal" in all_text:
        return "BR_NF"

    # Mexico: RFC or CFDI
    if "cfdi" in all_text or "rfc" in all_text.split():
        return "MX_CFDI"

    # Saudi: ZATCA
    if "zatca" in all_text:
        return "SA_VAT"

    # Italy: FatturaPA or SDI or Partita IVA
    if "fatturapa" in all_text or "sdi" in all_text.split() or re.search(r"\bIT\d{11}\b", all_text.upper()):
        return "IT_IVA"

    # Poland: KSeF or NIP
    if "ksef" in all_text or re.search(r"\bPL\d{10}\b", all_text.upper()):
        return "PL_VAT"

    # France: TVA or Factur-X
    if "factur-x" in all_text or re.search(r"\bFR\d{11}\b", all_text.upper()):
        return "FR_TVA"

    # Spain: SII or NIF/CIF
    if "sii" in all_text.split() or re.search(r"\bES[A-Z]\d{8}\b", all_text.upper()):
        return "ES_IVA"

    # Romania: RO e-Factura
    if "e-factura" in all_text or re.search(r"\bRO\d{2,10}\b", all_text.upper()):
        return "RO_TVA"

    # Netherlands: BTW
    if "btw" in all_text.split() or re.search(r"\bNL\d{9}B\d{2}\b", all_text.upper()):
        return "NL_BTW"

    # Sweden: Moms
    if "moms" in all_text or re.search(r"\bSE\d{12}\b", all_text.upper()):
        return "SE_MOMS"

    # Switzerland: MWST/TVA (check before generic EU)
    if "mwst" in all_text or re.search(r"CHE.?\d{3}\.?\d{3}\.?\d{3}", all_text.upper()):
        return "CH_MWST"

    # Germany specific
    if re.search(r"\bDE\d{9}\b", all_text.upper()) or "ust" in all_text.split():
        return "DE_UST"

    # Turkey: KDV or e-Fatura
    if "kdv" in all_text or "e-fatura" in all_text or "fatura" in all_text:
        return "TR_KDV"

    # Indonesia: PPN or Faktur Pajak or NPWP
    if "ppn" in all_text.split() or "faktur pajak" in all_text or "npwp" in all_text:
        return "ID_PPN"

    # Philippines: BIR or Official Receipt pattern
    if "bir" in all_text.split() or "official receipt" in all_text:
        return "PH_VAT"

    # South Korea: 사업자등록번호 or BRN pattern
    if re.search(r"\d{3}-\d{2}-\d{5}", all_text):
        return "KR_VAT"

    # Canada: GST/HST or BN RT pattern
    if "gst/hst" in all_text or "hst" in all_text.split() or re.search(r"\d{9}\s?RT", all_text.upper()):
        return "CA_GST"

    # Thailand: ใบกำกับภาษี (tax invoice in Thai) or 7% pattern
    if "ใบกำกับภาษี" in all_text:
        return "TH_VAT"

    # UK
    if re.search(r"\bGB\d{9}\b", all_text.upper()):
        return "UK_VAT"

    # EU VAT: pattern with country prefix (catch-all for EU)
    if re.search(r"\b[A-Z]{2}\d{8,12}\b", all_text.upper()):
        return "EU_VAT"

    return None


def _detect_regime_from_currency(fields: dict) -> Optional[str]:
    """Last resort: guess from currency."""
    currency = ""
    if "currency" in fields:
        currency = (fields["currency"].get("value", "") if isinstance(fields["currency"], dict) else str(fields["currency"])).upper().strip()

    currency_map = {
        "INR": "IN_GST", "₹": "IN_GST",
        "JPY": "JP_CT", "¥": "JP_CT",
        "AUD": "AU_GST", "A$": "AU_GST",
        "BRL": "BR_NF", "R$": "BR_NF",
        "MXN": "MX_CFDI",
        "SAR": "SA_VAT",
        "AED": "AE_VAT",
        "MYR": "MY_SST", "RM": "MY_SST",
        "SGD": "SG_GST", "S$": "SG_GST",
        "ZAR": "ZA_VAT",
        "GBP": "UK_VAT", "£": "UK_VAT",
        "KRW": "KR_VAT", "₩": "KR_VAT",
        "CAD": "CA_GST", "C$": "CA_GST",
        "THB": "TH_VAT", "฿": "TH_VAT",
        "IDR": "ID_PPN", "Rp": "ID_PPN",
        "TRY": "TR_KDV", "₺": "TR_KDV",
        "PHP": "PH_VAT", "₱": "PH_VAT",
        "EUR": "EU_VAT", "€": "EU_VAT",
        "NGN": "NG_VAT", "₦": "NG_VAT",
        "KES": "KE_VAT", "KSh": "KE_VAT",
        "EGP": "EG_VAT", "E£": "EG_VAT",
        "VND": "VN_VAT", "₫": "VN_VAT",
        "NZD": "NZ_GST", "NZ$": "NZ_GST",
        "COP": "CO_IVA", "COL$": "CO_IVA",
        "ILS": "IL_VAT", "₪": "IL_VAT",
        "PLN": "PL_VAT", "zł": "PL_VAT",
        "SEK": "SE_MOMS",
        "CHF": "CH_MWST",
        "TWD": "TW_BT", "NT$": "TW_BT",
        "ARS": "AR_IVA",
        "CLP": "CL_IVA",
        "PEN": "PE_IGV",
        "PKR": "PK_ST", "Rs": "PK_ST",
        "BDT": "BD_VAT", "৳": "BD_VAT",
        "LKR": "LK_VAT",
        "GHS": "GH_VAT", "GH₵": "GH_VAT",
        "TZS": "TZ_VAT",
        "MAD": "MA_TVA",
        "RON": "RO_TVA",
        "BHD": "BH_VAT",
        "OMR": "OM_VAT",
        "DKK": "DK_MOMS",
        "NOK": "NO_MVA",
        "HUF": "HU_AFA", "Ft": "HU_AFA",
        "CZK": "CZ_DPH", "Kč": "CZ_DPH",
        "HKD": "HK_NONE", "HK$": "HK_NONE",
        "UYU": "UY_IVA",
        "CRC": "CR_IVA", "₡": "CR_IVA",
    }
    return currency_map.get(currency)


def detect_industry(full_text: str) -> Optional[dict]:
    """Detect industry type from invoice text."""
    text_lower = full_text.lower()
    scores = {}

    for industry_id, markers in INDUSTRY_MARKERS.items():
        score = sum(1 for kw in markers["keywords"] if kw in text_lower)
        if score > 0:
            scores[industry_id] = score

    if not scores:
        return None

    best = max(scores, key=scores.get)
    markers = INDUSTRY_MARKERS[best]
    return {
        "industry": markers["label"],
        "industry_code": best,
        "confidence": min(scores[best] / 3, 1.0),  # Normalize
        "special_fields": markers["special_fields"],
        "matched_keywords": scores[best],
    }


# ── Agent Tools ───────────────────────────────────────────────────────────


def detect_invoice_type(invoice_id: str) -> dict:
    """Detect the tax regime, country, and industry of an invoice.

    Analyzes tax IDs, field patterns, currency, and text to identify
    which country's tax system applies and what industry the invoice is from.
    This determines which validation rules to apply.

    Args:
        invoice_id: The ID of the invoice to analyze.

    Returns:
        Detected regime, country, industry, and applicable tax rules.
    """
    from .invoice_parser import invoice_store

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    invoice = invoice_store[invoice_id]
    extracted = invoice.get("extracted_data", {})
    fields = extracted.get("fields", {})
    full_text = extracted.get("full_text", "")

    result = {
        "invoice_id": invoice_id,
        "detected_regime": None,
        "country": None,
        "industry": None,
        "tax_rules": None,
    }

    # Try detection methods in order of reliability
    regime_code = (
        _detect_regime_from_tax_ids(fields)
        or _detect_regime_from_fields(fields)
        or _detect_regime_from_currency(fields)
    )

    if regime_code and regime_code in TAX_REGIMES:
        regime = TAX_REGIMES[regime_code]
        result["detected_regime"] = regime.code
        result["country"] = regime.country
        result["tax_rules"] = {
            "name": regime.name,
            "tax_id_label": regime.tax_id_label,
            "standard_rate": f"{regime.standard_rate}%",
            "reduced_rates": [f"{r}%" for r in regime.reduced_rates] if regime.reduced_rates else [],
            "tax_components": regime.tax_components,
            "compound_tax": regime.compound,
            "notes": regime.notes,
        }
    else:
        result["detected_regime"] = "UNKNOWN"
        result["notes"] = "Could not determine tax regime. Ask the user which country this invoice is from."

    # Detect industry
    industry = detect_industry(full_text)
    if industry:
        result["industry"] = industry

    return result


def validate_compliance(invoice_id: str) -> dict:
    """Check if an invoice meets compliance requirements for its detected regime.

    Verifies that all mandatory fields are present, tax IDs are valid,
    and the invoice structure meets regional requirements.

    Args:
        invoice_id: The ID of the invoice to validate.

    Returns:
        Compliance report with passed checks, warnings, and errors.
    """
    from .invoice_parser import invoice_store

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    invoice = invoice_store[invoice_id]
    extracted = invoice.get("extracted_data", {})
    fields = extracted.get("fields", {})

    # First detect the regime
    detection = detect_invoice_type(invoice_id)
    regime_code = detection.get("detected_regime")

    result = {
        "invoice_id": invoice_id,
        "regime": regime_code,
        "country": detection.get("country", "Unknown"),
        "checks": [],
        "passed": 0,
        "warnings": 0,
        "errors": 0,
    }

    if regime_code and regime_code != "UNKNOWN" and regime_code in TAX_REGIMES:
        regime = TAX_REGIMES[regime_code]

        # Check required fields
        for req_field in regime.required_fields:
            if req_field in fields:
                value = fields[req_field].get("value", "") if isinstance(fields[req_field], dict) else str(fields[req_field])
                if value.strip():
                    result["checks"].append({
                        "field": req_field,
                        "status": "PASS",
                        "detail": f"Present: {value}",
                    })
                    result["passed"] += 1
                else:
                    result["checks"].append({
                        "field": req_field,
                        "status": "ERROR",
                        "detail": f"Required field '{req_field}' is empty.",
                    })
                    result["errors"] += 1
            else:
                result["checks"].append({
                    "field": req_field,
                    "status": "ERROR",
                    "detail": f"Required field '{req_field}' is missing.",
                })
                result["errors"] += 1

        # Validate tax ID format
        tax_id_value = ""
        if "supplier_tax_id" in fields:
            tax_id_value = fields["supplier_tax_id"].get("value", "") if isinstance(fields["supplier_tax_id"], dict) else str(fields["supplier_tax_id"])

        if tax_id_value:
            if re.search(regime.tax_id_pattern, tax_id_value):
                result["checks"].append({
                    "field": "tax_id_format",
                    "status": "PASS",
                    "detail": f"{regime.tax_id_label} '{tax_id_value}' matches expected format.",
                })
                result["passed"] += 1
            else:
                result["checks"].append({
                    "field": "tax_id_format",
                    "status": "WARNING",
                    "detail": f"{regime.tax_id_label} '{tax_id_value}' may not match expected format ({regime.tax_id_pattern}).",
                })
                result["warnings"] += 1

        # India GST specific: check for CGST/SGST or IGST
        if regime_code == "IN_GST":
            has_cgst = any("cgst" in k.lower() for k in fields)
            has_sgst = any("sgst" in k.lower() for k in fields)
            has_igst = any("igst" in k.lower() for k in fields)

            if has_cgst and has_sgst:
                result["checks"].append({
                    "field": "gst_structure",
                    "status": "PASS",
                    "detail": "Intrastate supply: CGST + SGST present.",
                })
                result["passed"] += 1
            elif has_igst:
                result["checks"].append({
                    "field": "gst_structure",
                    "status": "PASS",
                    "detail": "Interstate supply: IGST present.",
                })
                result["passed"] += 1
            else:
                result["checks"].append({
                    "field": "gst_structure",
                    "status": "WARNING",
                    "detail": "No CGST/SGST or IGST found. GST breakdown may be missing.",
                })
                result["warnings"] += 1

    else:
        result["checks"].append({
            "field": "regime_detection",
            "status": "WARNING",
            "detail": "Could not determine tax regime. Manual compliance check recommended.",
        })
        result["warnings"] += 1

    # Universal checks (apply to all invoices)
    if "invoice_id" not in fields:
        result["checks"].append({
            "field": "invoice_number",
            "status": "WARNING",
            "detail": "No invoice number detected. Most jurisdictions require this.",
        })
        result["warnings"] += 1

    if "invoice_date" not in fields:
        result["checks"].append({
            "field": "invoice_date",
            "status": "WARNING",
            "detail": "No invoice date detected. Required in all jurisdictions.",
        })
        result["warnings"] += 1

    result["summary"] = (
        f"{result['passed']} passed, {result['warnings']} warnings, {result['errors']} errors"
    )

    return result


def verify_tax_math(invoice_id: str) -> dict:
    """Verify tax calculations against the detected regime's rules.

    Handles all tax structures: simple, compound, split-rate, multi-jurisdiction.
    Checks subtotal + tax = total, validates tax rates against known rates,
    and flags any discrepancies.

    Args:
        invoice_id: The ID of the invoice to verify.

    Returns:
        Tax verification with calculations, expected vs actual, and discrepancies.
    """
    from .invoice_parser import invoice_store

    if invoice_id not in invoice_store:
        return {"error": f"Invoice '{invoice_id}' not found."}

    invoice = invoice_store[invoice_id]
    extracted = invoice.get("extracted_data", {})
    fields = extracted.get("fields", {})

    detection = detect_invoice_type(invoice_id)
    regime_code = detection.get("detected_regime")

    result = {
        "invoice_id": invoice_id,
        "regime": regime_code,
        "checks": [],
    }

    def _parse_amount(field_name):
        if field_name not in fields:
            return None
        val = fields[field_name]
        if isinstance(val, dict):
            val = val.get("value", "")
        val = str(val)
        # Strip currency symbols, commas, spaces
        cleaned = re.sub(r"[^\d.\-]", "", val.replace(",", ""))
        try:
            return float(cleaned)
        except ValueError:
            return None

    net = _parse_amount("net_amount")
    tax = _parse_amount("total_tax_amount")
    total = _parse_amount("total_amount")

    # Collect all tax component amounts
    tax_components = {}
    for field_key, field_val in fields.items():
        key_lower = field_key.lower()
        if any(t in key_lower for t in ["tax", "gst", "vat", "cgst", "sgst", "igst", "cess", "iva", "isr"]):
            if field_key in ("total_tax_amount", "total_amount", "net_amount"):
                continue
            amount = _parse_amount(field_key)
            if amount is not None:
                label = field_key.replace("_", " ").title()
                tax_components[label] = amount

    if tax_components:
        result["tax_components"] = tax_components
        component_total = sum(tax_components.values())
        result["tax_components_total"] = round(component_total, 2)

        if tax is not None:
            diff = abs(component_total - tax)
            if diff > 0.02:
                result["checks"].append({
                    "check": "tax_components_sum",
                    "status": "MISMATCH",
                    "detail": (
                        f"Sum of tax components ({component_total:.2f}) "
                        f"!= total tax ({tax:.2f}). Difference: {diff:.2f}"
                    ),
                })
            else:
                result["checks"].append({
                    "check": "tax_components_sum",
                    "status": "OK",
                    "detail": f"Tax components sum ({component_total:.2f}) matches total tax ({tax:.2f}).",
                })

    # Basic arithmetic check
    if net is not None and tax is not None and total is not None:
        expected = round(net + tax, 2)
        diff = abs(expected - total)

        if diff > 0.02:
            result["checks"].append({
                "check": "total_arithmetic",
                "status": "MISMATCH",
                "detail": f"Subtotal ({net:.2f}) + Tax ({tax:.2f}) = {expected:.2f}, but total shows {total:.2f}. Difference: {diff:.2f}",
            })
        else:
            result["checks"].append({
                "check": "total_arithmetic",
                "status": "OK",
                "detail": f"Subtotal ({net:.2f}) + Tax ({tax:.2f}) = {expected:.2f} matches total ({total:.2f}).",
            })

        # Estimate tax rate
        if net > 0:
            effective_rate = round((tax / net) * 100, 2)
            result["effective_tax_rate"] = f"{effective_rate}%"

            # Compare against known rates — use HISTORICAL rate if invoice date available
            if regime_code and regime_code in TAX_REGIMES:
                regime = TAX_REGIMES[regime_code]

                # Try to parse invoice date for historical rate lookup
                invoice_date_val = fields.get("invoice_date", {})
                if isinstance(invoice_date_val, dict):
                    invoice_date_val = invoice_date_val.get("value", "")
                invoice_date_str = str(invoice_date_val).strip()

                historical = None
                parsed_date = None
                if invoice_date_str:
                    # Try common date formats
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y"):
                        try:
                            parsed_date = date(*__import__('datetime').datetime.strptime(invoice_date_str, fmt).timetuple()[:3])
                            break
                        except ValueError:
                            continue

                if parsed_date:
                    historical = get_rate_for_date(regime_code, parsed_date)

                if historical:
                    hist_std, hist_reduced = historical
                    known_rates = [hist_std] + hist_reduced
                    rate_source = f"historical rate as of {parsed_date.isoformat()}"

                    # Check if current rate differs from historical
                    if abs(hist_std - regime.standard_rate) > 0.01:
                        result["checks"].append({
                            "check": "historical_rate",
                            "status": "INFO",
                            "detail": (
                                f"Invoice date {parsed_date.isoformat()}: {regime.name} rate was "
                                f"{hist_std}% (current rate is {regime.standard_rate}%). "
                                f"Using historical rate for verification."
                            ),
                        })
                else:
                    known_rates = [regime.standard_rate] + regime.reduced_rates
                    rate_source = "current rate"

                closest = min(known_rates, key=lambda r: abs(r - effective_rate))

                if abs(effective_rate - closest) < 0.5:
                    result["checks"].append({
                        "check": "tax_rate_match",
                        "status": "OK",
                        "detail": f"Effective rate {effective_rate}% matches {regime.name} {rate_source} of {closest}%.",
                    })
                else:
                    result["checks"].append({
                        "check": "tax_rate_match",
                        "status": "WARNING",
                        "detail": (
                            f"Effective rate {effective_rate}% doesn't match {regime.name} {rate_source} "
                            f"({', '.join(f'{r}%' for r in known_rates)}). "
                            f"Could be mixed rates, exemptions, or an error."
                        ),
                    })
    else:
        missing = []
        if net is None:
            missing.append("subtotal")
        if tax is None:
            missing.append("tax")
        if total is None:
            missing.append("total")
        result["checks"].append({
            "check": "total_arithmetic",
            "status": "INCOMPLETE",
            "detail": f"Cannot verify — missing: {', '.join(missing)}.",
        })

    return result
