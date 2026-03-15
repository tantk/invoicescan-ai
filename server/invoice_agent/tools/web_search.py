"""Web search and page fetching tools for live tax information.

Layer 3 of the tax knowledge stack:
  1. Static TAX_REGIMES (instant, offline)
  2. Tax guides in Vertex AI Search (RAG, curated)
  3. Google Search + web fetch (real-time, any topic)

The agent uses these when:
- A tax rate may have changed since the knowledge base was last updated
- An invoice is from a country not in the static list
- The user asks about current regulations or recent changes
- Compliance rules need verification against official sources
"""

import logging
import re

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


async def search_tax_info(query: str) -> dict:
    """Search the web for current tax rates, rules, or compliance requirements.

    Use this when you need up-to-date tax information that may have changed,
    or for countries/topics not covered by the built-in tax engine.
    Adds "tax invoice compliance" to the query for better results.

    Args:
        query: What to search for. Be specific, e.g.,
               "current GST rate India 2026" or
               "Saudi Arabia ZATCA Phase 2 requirements"

    Returns:
        Search results with titles, snippets, and URLs.
    """
    # This is a placeholder — in production, use Google Custom Search API
    # or the ADK google_search tool. For the hackathon, the agent can
    # use the built-in Google Search tool from ADK if available.
    return {
        "note": (
            "Use the Google Search built-in tool or Vertex AI Search to look up: "
            f"'{query}'. The built-in tax engine may have outdated rates."
        ),
        "suggested_queries": [
            f"{query} site:gov official",
            f"{query} 2026 current rate",
            f"{query} compliance requirements",
        ],
    }


def fetch_tax_page(url: str) -> dict:
    """Fetch and extract text content from a tax authority or reference page.

    Use this to read official tax authority pages, rate tables, or
    compliance guides. Strips HTML and returns clean text.

    Args:
        url: The URL to fetch. Prefer official government/tax authority sites.

    Returns:
        Page title and extracted text content (truncated to 5000 chars).
    """
    try:
        headers = {
            "User-Agent": "InvoiceScanAI/1.0 (Tax Reference Lookup)",
        }
        with httpx.Client(timeout=15, follow_redirects=True) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script, style, nav elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else url
        text = soup.get_text(separator="\n", strip=True)

        # Clean up whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Truncate
        if len(text) > 5000:
            text = text[:5000] + "\n\n[... truncated — page is longer]"

        return {
            "url": url,
            "title": title,
            "content": text,
        }

    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return {
            "url": url,
            "error": f"Could not fetch page: {str(e)}",
        }


# ── Official Tax Authority URLs (for quick reference) ─────────────────────

TAX_AUTHORITY_URLS = {
    "US_IRS": "https://www.irs.gov",
    "EU_VIES": "https://ec.europa.eu/taxation_customs/vies/",
    "UK_HMRC": "https://www.gov.uk/government/organisations/hm-revenue-customs",
    "IN_GST": "https://www.gst.gov.in",
    "IN_GSTIN_VERIFY": "https://services.gst.gov.in/services/searchtp",
    "JP_NTA": "https://www.nta.go.jp",
    "JP_QIIN_VERIFY": "https://www.invoice-kohyo.nta.go.jp",
    "AU_ATO": "https://www.ato.gov.au",
    "AU_ABN_VERIFY": "https://abr.business.gov.au",
    "SA_ZATCA": "https://zatca.gov.sa",
    "BR_SEFAZ": "https://www.nfe.fazenda.gov.br",
    "MX_SAT": "https://www.sat.gob.mx",
    "CN_STA": "https://www.chinatax.gov.cn",
    "AE_FTA": "https://tax.gov.ae",
    "MY_IRB": "https://www.hasil.gov.my",
    "SG_IRAS": "https://www.iras.gov.sg",
    "ZA_SARS": "https://www.sars.gov.za",
    "KR_NTS": "https://www.nts.go.kr",
    "CA_CRA": "https://www.canada.ca/en/revenue-agency.html",
    "TH_RD": "https://www.rd.go.th",
    "ID_DJP": "https://www.pajak.go.id",
    "TR_GIB": "https://www.gib.gov.tr",
    "PH_BIR": "https://www.bir.gov.ph",
    "DE_BZST": "https://www.bzst.de",
    "NG_FIRS": "https://www.firs.gov.ng",
    "KE_KRA": "https://www.kra.go.ke",
    "EG_ETA": "https://www.eta.gov.eg",
    "VN_GDT": "https://www.gdt.gov.vn",
    "NZ_IRD": "https://www.ird.govt.nz",
    "CO_DIAN": "https://www.dian.gov.co",
    "IL_ITA": "https://www.gov.il/en/departments/israel_tax_authority",
    "PL_MF": "https://www.podatki.gov.pl",
    "IT_ADE": "https://www.agenziaentrate.gov.it",
    "FR_DGFIP": "https://www.impots.gouv.fr",
    "ES_AEAT": "https://www.agenciatributaria.es",
    "NL_TAX": "https://www.belastingdienst.nl",
    "SE_SKV": "https://www.skatteverket.se",
    "CH_FTA": "https://www.estv.admin.ch",
    "TW_MOF": "https://www.mof.gov.tw",
    "AR_AFIP": "https://www.afip.gob.ar",
    "CL_SII": "https://www.sii.cl",
    "PE_SUNAT": "https://www.sunat.gob.pe",
    "PK_FBR": "https://www.fbr.gov.pk",
    "BD_NBR": "https://nbr.gov.bd",
    "LK_IRD": "https://www.ird.gov.lk",
    "GH_GRA": "https://www.gra.gov.gh",
    "TZ_TRA": "https://www.tra.go.tz",
    "MA_DGI": "https://www.tax.gov.ma",
    "RO_ANAF": "https://www.anaf.ro",
    "NG_FIRS": "https://www.firs.gov.ng",
    "KE_KRA_ETIMS": "https://etims.kra.go.ke",
    "EG_ETA_EINV": "https://invoicing.eta.gov.eg",
    "VN_GDT_EINV": "https://hoadondientu.gdt.gov.vn",
}


def get_tax_authority_url(country_code: str) -> dict:
    """Get the official tax authority URL for a country.

    Useful when you need to direct the user to official sources or
    verify information against the authoritative source.

    Args:
        country_code: Two-letter country code or regime code (e.g., "IN", "US", "EU", "IN_GST").

    Returns:
        Tax authority name and URL, plus verification portal if available.
    """
    # Try direct match first
    urls = {}
    for key, url in TAX_AUTHORITY_URLS.items():
        if key.startswith(country_code.upper()):
            label = key.replace("_", " ")
            urls[label] = url

    if urls:
        return {"country_code": country_code, "authorities": urls}

    return {
        "country_code": country_code,
        "message": f"No pre-configured authority URL for '{country_code}'. Try searching online.",
    }
