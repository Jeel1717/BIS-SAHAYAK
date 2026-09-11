"""
BIS Sahayak — Official BIS Source Registry
Chapter 14: Large-Scale Knowledge Expansion

All URLs are:
  - Official BIS domain (bis.gov.in) only
  - Publicly accessible without login
  - Free to read under government public information policy
  - Strictly official: authoritative HTML portals and official Gazette/guideline PDFs
  - Zero third-party sources

Coverage:
  A. Consumer Protection & Grievance Redressal
  B. Gold & Silver Hallmarking, HUID & AHC Centres
  C. Product Certification (Scheme-I ISI Mark, Scheme-II CRS, Simplified Procedure)
  D. Mandatory Certification & Quality Control Orders (QCOs)
  E. Indian Standards & Standards Formulation (TC Handbook, Know Your Standard)
  F. Laboratory Services & Laboratory Recognition Scheme (LRS)
  G. BIS Legislation (BIS Act 2016) & Regional Administration
"""

from app.ingestion.pipeline import SourceConfig

BIS_SOURCES: list[SourceConfig] = [

    # ── A. CONSUMER PROTECTION & GRIEVANCE REDRESSAL ─────────────────────────

    SourceConfig(
        url="https://www.bis.gov.in/consumer-overview/for-consumers-faq/?lang=en",
        title="BIS Consumer FAQ — Frequently Asked Questions for Consumers",
        document_type="FAQ",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/consumer-overview/consumer-protection/?lang=en",
        title="BIS Consumer Protection — Rights, Quality Assurance and Consumer Awareness",
        document_type="Consumer Guide",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/consumer-overview/consumer-awareness/?lang=en",
        title="BIS Consumer Awareness — Public Education and Standards Promotion",
        document_type="Consumer Guide",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2023/06/Guidelines.pdf",
        title="BIS Guidelines for Dealing with Complaints Related to Quality of BIS Certified Products",
        document_type="Consumer Grievance Guidelines",
        version_or_effective_date="2023",
    ),

    # ── B. GOLD & SILVER HALLMARKING, HUID & AHC CENTRES ──────────────────────

    SourceConfig(
        url="https://www.bis.gov.in/hallmarking-overview/?lang=en",
        title="BIS Hallmarking Overview — Gold and Silver Hallmarking Scheme",
        document_type="Scheme Overview",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/hallmarking-overview/consumer-protection/?lang=en",
        title="BIS Hallmarking — Consumer Protection and Hallmark Authentication",
        document_type="Consumer Guide",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/hallmarking-overview/hallmarking-faqs/?lang=en",
        title="BIS Hallmarking FAQ — Purity, HUID and Certification Questions",
        document_type="FAQ",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2020/12/brief-on-Hallmarking.pdf",
        title="BIS Brief on Gold and Silver Hallmarking Scheme — Standards IS 1417 & IS 2112",
        document_type="Hallmarking Overview",
        version_or_effective_date="2020",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2026/07/GuidelinesForAHCs.pdf",
        title="BIS Guidelines for Recognition and Operation of Assaying and Hallmarking Centres (AHC)",
        document_type="Hallmarking Guidelines",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2022/01/Guidelines-on-testing-of-unhallmarked-gold-jewellery-and-artefacts-of-the-consumer-by-the-Assaying-and-Hallmarking-Centres.pdf",
        title="BIS Guidelines on Testing of Unhallmarked Gold Jewellery for Consumers at AHCs",
        document_type="Consumer Hallmarking Guide",
        version_or_effective_date="2022",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2024/01/Revised-Guidelines-for-JEWELLERS-Jan-24.pdf",
        title="BIS Guidelines for Jewellers — Registration, Display and Gold & Silver Hallmarking",
        document_type="Industry Hallmarking Guide",
        version_or_effective_date="2024",
    ),

    # ── C. PRODUCT CERTIFICATION & MANDATORY REGISTRATION ─────────────────────

    SourceConfig(
        url="https://www.bis.gov.in/product-certification-overview/?lang=en",
        title="BIS Product Certification Overview — Schemes, Standards Mark and Process",
        document_type="Scheme Overview",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/product-certification-overview/scheme-i/?lang=en",
        title="BIS Product Certification Scheme I — ISI Mark Certification Regulations",
        document_type="Scheme Information",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/product-certification-overview/scheme-ii/?lang=en",
        title="BIS Product Certification Scheme II — Compulsory Registration Scheme (CRS) Self Declaration",
        document_type="Scheme Information",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2021/04/List-of-Products-Under-Simplified-Procedure.pdf",
        title="BIS Product Certification — Simplified Procedure for Grant of Licence and Products List",
        document_type="Certification Guidelines",
        version_or_effective_date="2021",
    ),

    # ── D. MANDATORY CERTIFICATION & QUALITY CONTROL ORDERS ───────────────────

    SourceConfig(
        url="https://www.bis.gov.in/product-certification-overview/products-under-compulsory-certification/?lang=en",
        title="BIS Products Under Compulsory Certification — Statutory Mandatory BIS List",
        document_type="Regulatory List",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2021/06/qc-order-June-2021-2.pdf",
        title="BIS Quality Control Orders (QCO) — Mandatory Certification Requirements and Penalties",
        document_type="Regulatory Order",
        version_or_effective_date="2021",
    ),

    # ── E. INDIAN STANDARDS & STANDARDS FORMULATION ───────────────────────────

    SourceConfig(
        url="https://www.bis.gov.in/know-your-standard/?lang=en",
        title="BIS Know Your Standard — Public Standards Information Portal",
        document_type="Standards Information",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2024/06/Handbook-for-TC-Members.pdf",
        title="BIS Handbook for Technical Committee Members — Formulation and Development of Indian Standards",
        document_type="Standards Process Guide",
        version_or_effective_date="2024",
    ),

    # ── F. CONFORMITY ASSESSMENT & LABORATORIES ───────────────────────────────

    SourceConfig(
        url="https://www.bis.gov.in/laboratory-overview/testing-facilities/?lang=en",
        title="BIS Testing Facilities — Central, Regional and Branch Lab Services",
        document_type="Laboratory Information",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/wp-content/uploads/2020/06/LRS_23062020.pdf",
        title="BIS Laboratory Recognition Scheme (LRS) — Outside Testing Laboratories Guidelines",
        document_type="Laboratory Regulation",
        version_or_effective_date="2020",
    ),

    # ── G. BIS LEGISLATION & ADMINISTRATION ───────────────────────────────────

    SourceConfig(
        url="https://www.bis.gov.in/the-bureau/about-bis/?lang=en",
        title="About BIS — Bureau of Indian Standards Structure, Role and Functions",
        document_type="About BIS",
        version_or_effective_date="2024",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/the-bureau/bis-act-2016/?lang=en",
        title="Bureau of Indian Standards Act 2016 — Statutory Framework, Penalties and Authorities",
        document_type="Legislation",
        version_or_effective_date="2016",
    ),
    SourceConfig(
        url="https://www.bis.gov.in/the-bureau/regional-offices/?lang=en",
        title="BIS Regional Offices and Branch Offices — Nationwide Public Directory",
        document_type="Directory",
        version_or_effective_date="2024",
    ),
]
