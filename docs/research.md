# InvoiceScan AI — Research Foundation

## Academic Grounding

InvoiceScan AI is informed by the latest research in document understanding, multimodal AI, and invoice processing. This document maps our technical decisions to the academic state of the art.

---

## Key Research That Validates Our Approach

### 1. Native Image Processing > OCR Pipelines

**Paper:** "Multi-Modal Vision vs. Text-Based Parsing: Benchmarking LLM Strategies for Invoice Processing" (Berghaus et al., 2025)

> Direct image processing by multimodal LLMs generally outperforms structured OCR-then-parse approaches, achieving 96%+ accuracy on clean invoices.

**How we apply it:** Our Layer 2 (Gemini Vision) processes invoice images directly for custom field extraction, avoiding OCR error propagation. Layer 1 (Document AI) uses Google's production-grade OCR+ML pipeline for standard fields, combining the best of both worlds.

### 2. OCR-Free Document Understanding

**Paper:** "Donut: OCR-free Document Understanding Transformer" (Kim et al., ECCV 2022)

> Transformer encoder-decoder architecture maps document images directly to structured output, eliminating OCR dependency entirely.

**How we apply it:** Gemini 2.5 Flash natively processes document images without a separate OCR step. Our two-layer architecture uses Document AI (with OCR) for grounded accuracy AND Gemini Vision (OCR-free) for flexibility.

### 3. Layout-Aware Extraction

**Paper:** "LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking" (Huang et al., ACM MM 2022)

> Joint pre-training of text, layout, and image features enables superior document understanding. Foundation for modern document AI.

**Paper:** "DocLLM: A Layout-Aware Generative Language Model" (JPMorgan, ACL 2024)

> Disentangled spatial attention captures layout without expensive image encoders. 15-61% improvement over base LLMs.

**How we apply it:** Google Document AI's Invoice Parser is built on these principles. Our grounding text preserves layout context (field positions, confidence scores) when injecting into the Gemini Live session.

### 4. Self-Improving with Implicit Labels

**Paper:** "LLMs in the Loop: Leveraging LLM Annotations for Active Learning" (2024)

> LLM-generated annotations within active learning loops reduce human labeling requirements while maintaining quality.

**Paper:** "Efficient Human-in-the-Loop Active Learning Framework" (2025)

> Maximizing annotation efficiency under limited budgets through strategic sample selection.

**How we apply it:** Our auto-uptraining pipeline uses implicit labels — when a user doesn't correct a Gemini Vision extraction, it's treated as an approved annotation. After 50+ approved samples (85%+ accuracy), the field can be uptrained into Document AI. This is a novel application of active learning principles to invoice extraction.

### 5. Configuration-Free Invoice Analysis

**Paper:** "CloudScan - A Configuration-Free Invoice Analysis System Using Recurrent Neural Networks" (Tradeshift, 2017)

> A single global model generalizes to unseen invoice layouts without per-template configuration. 0.891 F1 on seen layouts, 0.840 on unseen.

**How we apply it:** InvoiceScan AI requires zero configuration per invoice layout. Document AI handles any format, Gemini Vision extracts any custom field, and the tax engine auto-detects the country/industry. No templates, no rules, no setup.

### 6. Interpretable Reasoning

**Paper:** "LayoutLLM: Layout Instruction Tuning with Large Language Models" (CVPR 2024)

> "Layout Chain-of-Thought" (LayoutCoT) enables interpretable step-by-step reasoning about document structure.

**How we apply it:** Our agent's pipeline (detect → extract → verify → comply) mirrors chain-of-thought reasoning. The agent explains its analysis: "This is an Indian GST invoice. IGST applies because it crosses state lines. 18% on ₹8,90,000 = ₹1,60,200. Math checks out."

---

## Current State-of-the-Art Benchmarks

| Benchmark | Best Model | Score | Year |
|-----------|-----------|-------|------|
| **SROIE** (receipt KIE) | InternVL2-8B + mask pre-training | 97.0 ANLS | 2025 |
| **CORD** (receipt KIE) | Qwen2-VL-7B + mask pre-training | 97.3 ANLS | 2025 |
| **DocVQA** (document QA) | Qwen2.5-VL-72B | Matches GPT-4o | 2025 |
| **FUNSD** (form NER) | DocFormerv2 | SOTA | 2024 |
| **Invoice table extraction** | ExTTNet | 0.92 F1 | 2024 |
| **Clean invoice extraction** | GPT-5 Chat | 96%+ | 2025 |

### How InvoiceScan AI Compares

InvoiceScan AI uses **Gemini 2.5 Flash** (competitive with these SOTA models) combined with **Google Document AI** (Google's production-grade invoice parser). Our contribution is not a new extraction model, but a **novel system architecture** that combines extraction with tax intelligence, voice interaction, and self-improvement.

---

## Novel Contributions of InvoiceScan AI

No existing academic work combines all of these:

| Contribution | Academic Precedent | Our Innovation |
|-------------|-------------------|----------------|
| Voice conversation about invoices | None | First real-time voice agent for invoice analysis |
| Global tax verification (57 countries) | V7 Labs (EU only) | 10x country coverage with historical rate awareness |
| Self-improving extraction pipeline | Active learning papers (general) | Applied to invoice field extraction with implicit labels |
| Two-layer extraction (grounded + flexible) | Hybrid OCR+LLM papers | Document AI (grounded) + Gemini Vision (flexible) with graduation |
| Industry-aware custom extraction | LayoutLM family (general) | 8 industry presets with 228 custom fields |
| Date-aware tax rate verification | None found | Checks invoice date against historical rate changes |

---

## Foundational Models & Architectures

### The LayoutLM Family (Microsoft, 2020-2022)

```
LayoutLM (2020)     → Text + Layout
LayoutLMv2 (2021)   → Text + Layout + Vision
LayoutXLM (2022)    → Multilingual extension
LayoutLMv3 (2022)   → Unified masking, no pre-trained CNN needed
```

These established the paradigm of joint text-layout-vision pre-training that all modern document AI builds upon, including Google's Document AI.

### The OCR-Free Wave (2022-2025)

```
Donut (2022)        → First OCR-free document understanding
Pix2Struct (2023)   → Screenshot-to-HTML pre-training
DocFormerv2 (2024)  → Token-to-line/grid pre-training
SmolDocling (2025)  → 256M params, competes with 27x larger models
```

Validates our use of Gemini Vision for direct image-to-structure extraction.

### LLM-Based Document Understanding (2024-2025)

```
DocLLM (JPMorgan)   → Disentangled spatial attention
LayoutLLM (CVPR)    → Layout Chain-of-Thought reasoning
LayTextLLM          → Bounding box as single token
DocLayLLM           → CoT pre-training + annealing
```

The frontier is moving toward LLM-based document understanding, which is exactly what InvoiceScan AI does with Gemini.

---

## Relevant Datasets

| Dataset | Size | Type | Relevance |
|---------|------|------|-----------|
| **FATURA** | 10,000 invoices, 50 layouts | Largest open invoice dataset | Primary benchmark target |
| **SROIE** | 973 receipts | Competition standard | We tested with these |
| **CORD** | 1,000 Indonesian receipts | Multilingual receipts | Southeast Asian coverage |
| **ReceiptSense** | 20,000 receipts | Arabic-English bilingual | Multilingual testing |
| **RVL-CDIP** | 400,000 documents | Document classification | Pre-training data |
| **DocLayNet** | 80,863 pages | Layout analysis | Layout benchmark |
| **XFUND** | 1,393 forms, 7 languages | Multilingual forms | Cross-language testing |

---

## Invoice Fraud Detection Research

| Technique | Result | Paper |
|-----------|--------|-------|
| Hybrid DL models | 98.7% accuracy, 94.3% precision | Financial Fraud Detection Survey (2025) |
| Continual learning | Adapts to evolving patterns without forgetting | Hemati & Schreyer (2022) |
| Federated learning | Privacy-preserving multi-client detection | Federated Continual Learning (2022) |
| Isolation Forest + One-Class SVM | 53,000+ anomalies flagged | University of Rochester |

**Future work for InvoiceScan AI:** Add fraud/duplicate detection as an agent tool.

---

## Market Validation

| Metric | Value | Source |
|--------|-------|--------|
| Invoice processing market (2025) | $40.82B | Business Research Company |
| AI invoice processing (2034) | $47.1B | Industry reports |
| Market CAGR | 32.6% | Industry reports |
| Manual cost per invoice | $12-30 | Gartner |
| Automated cost per invoice | $1-5 | Gartner |
| Processing time reduction | 62% (20.8 → 7.9 days) | Industry benchmarks |
| AI adoption in finance (2025) | 84% (up from 47% in 2024) | Parseur |
| Duplicate payment reduction with AI | Up to 80% | Xelix |
| Touchless processing rate (2025) | 52.8% | Industry benchmarks |

The invoice processing market is growing at 32.6% CAGR, with AI adoption nearly doubling in a single year. InvoiceScan AI targets this market with an open-source, voice-first approach that democratizes capabilities previously available only to enterprises paying $500+/month.

---

## References

### Invoice Extraction
1. Berghaus et al. "Multi-Modal Vision vs. Text-Based Parsing: Benchmarking LLM Strategies for Invoice Processing." arXiv, 2025. [2509.04469](https://arxiv.org/abs/2509.04469)
2. Yashwant et al. "Invoice Information Extraction: Methods and Performance Evaluation." arXiv, 2025. [2510.15727](https://arxiv.org/abs/2510.15727)
3. Khanchandani et al. "Automated Invoice Data Extraction: Using LLM and OCR." arXiv, 2025. [2511.05547](https://arxiv.org/abs/2511.05547)
4. Amari et al. "An Efficient Deep Learning-Based Approach to Automating Invoice Document Validation." IEEE/ACS, 2025. [2503.12267](https://arxiv.org/abs/2503.12267)
5. Palm et al. "CloudScan - A Configuration-Free Invoice Analysis System." arXiv, 2017. [1708.07403](https://arxiv.org/abs/1708.07403)
6. "ExTTNet: A Deep Learning Algorithm for Extracting Table Texts from Invoice Images." arXiv, 2024. [2402.02246](https://arxiv.org/abs/2402.02246)

### Document Understanding Models
7. Xu et al. "LayoutLM: Pre-training of Text and Layout for Document Image Understanding." KDD, 2020. [1912.13318](https://arxiv.org/abs/1912.13318)
8. Huang et al. "LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking." ACM MM, 2022. [2204.08387](https://arxiv.org/abs/2204.08387)
9. Xu et al. "LayoutXLM: Multimodal Pre-training for Multilingual Visually-rich Document Understanding." ACL Findings, 2022. [2104.08836](https://arxiv.org/abs/2104.08836)
10. Kim et al. "Donut: OCR-free Document Understanding Transformer." ECCV, 2022. [2111.15664](https://arxiv.org/abs/2111.15664)
11. Lee et al. "Pix2Struct: Screenshot Parsing as Pretraining." ICML, 2023. [2210.03347](https://arxiv.org/abs/2210.03347)
12. "DocLLM: A Layout-Aware Generative Language Model." ACL, 2024. [2401.00908](https://arxiv.org/abs/2401.00908)
13. Luo et al. "LayoutLLM: Layout Instruction Tuning with LLMs." CVPR, 2024. [2404.05225](https://arxiv.org/abs/2404.05225)
14. "SmolDocling: Ultra-compact VLM for End-to-End Document Conversion." arXiv, 2025. [2503.11576](https://arxiv.org/abs/2503.11576)

### Layout Analysis
15. Wang et al. "DLAFormer: An End-to-End Transformer for Document Layout Analysis." ICDAR, 2024. [2405.11757](https://arxiv.org/abs/2405.11757)
16. "DocGraphLM: Documental Graph Language Model for Information Extraction." SIGIR, 2023. [2401.02823](https://arxiv.org/abs/2401.02823)

### Active Learning & Self-Improvement
17. "LLMs in the Loop: Leveraging LLM Annotations for Active Learning." arXiv, 2024. [2404.02261](https://arxiv.org/abs/2404.02261)
18. "Efficient Human-in-the-Loop Active Learning Framework." arXiv, 2025. [2501.00277](https://arxiv.org/abs/2501.00277)
19. Zhang et al. "SAIL: Sample-Centric In-Context Learning for Document IE." AAAI, 2025. [2412.17092](https://arxiv.org/abs/2412.17092)

### Fraud Detection
20. "Year-over-Year Developments in Financial Fraud Detection via Deep Learning." arXiv, 2025. [2502.00201](https://arxiv.org/abs/2502.00201)
21. Hemati & Schreyer. "Continual Learning for Unsupervised Anomaly Detection in Continuous Auditing." arXiv, 2022. [2112.13215](https://arxiv.org/abs/2112.13215)

### Evaluation
22. "ANLS*: A Universal Document Processing Metric for Generative LLMs." arXiv, 2024. [2402.03848](https://arxiv.org/abs/2402.03848)

### Comprehensive Reviews
23. Rombach & Fettke. "Deep Learning based Key Information Extraction from Business Documents: Systematic Literature Review." ACM Computing Surveys, 2024. [2408.06345](https://arxiv.org/abs/2408.06345)
