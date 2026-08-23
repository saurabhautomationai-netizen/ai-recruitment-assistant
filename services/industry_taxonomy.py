"""Standardized Industry Taxonomy & Role Hierarchy for ZERO Recruit ATS.

Covers 9 core business verticals with 5-tier hierarchical levels (L1 to L5),
core skills, domain interview focus questions, and X-Ray search query templates.
"""

from typing import Dict, List, Any


INDUSTRY_TAXONOMY: Dict[str, Dict[str, Any]] = {
    "it_services": {
        "name": "IT Services & Software Engineering",
        "icon": "💻",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["Chief Technology Officer (CTO)", "Chief Information Officer (CIO)", "VP of Engineering"]},
            "L4": {"label": "Management Level", "titles": ["Engineering Manager", "Delivery Manager", "IT Director"]},
            "L3": {"label": "Lead Level", "titles": ["Technical Lead", "Scrum Master", "Principal Engineer", "Cloud Architect"]},
            "L2": {"label": "Senior Level", "titles": ["Senior Software Engineer", "Senior DevOps Specialist", "Senior QA Automation Engineer", "Senior Data Engineer"]},
            "L1": {"label": "Associate Level", "titles": ["Software Engineer", "Associate QA Engineer", "IT Support Analyst", "Junior Frontend Developer"]},
        },
        "roles": [
            "Full-Stack Developers (React/Node.js/Python)",
            "Cloud & DevOps Engineers (AWS/Azure/Kubernetes)",
            "Data Architects & Engineers",
            "Cybersecurity Analysts & SecOps",
            "UI/UX Designers & Product Owners",
            "AI Automation & LLM Ops Engineers",
        ],
        "default_skills": ["Python", "React", "TypeScript", "AWS", "Kubernetes", "PostgreSQL", "Docker", "REST APIs", "CI/CD"],
        "interview_questions": [
            "How do you design scalable distributed microservices with automated failover?",
            "Explain your strategy for securing cloud infrastructure and continuous deployment pipelines.",
            "Describe how you profile and optimize high-latency database queries.",
        ],
    },
    "finance": {
        "name": "Finance (Corporate & Enterprise)",
        "icon": "📊",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["Chief Financial Officer (CFO)", "VP of Finance", "Group Controller"]},
            "L4": {"label": "Management Level", "titles": ["Finance Director", "Tax Manager", "Treasury Manager", "FP&A Director"]},
            "L3": {"label": "Lead Level", "titles": ["Lead Financial Analyst", "Assistant Controller", "Senior Audit Lead"]},
            "L2": {"label": "Senior Level", "titles": ["Senior Accountant", "Senior Tax Specialist", "Senior FP&A Analyst"]},
            "L1": {"label": "Associate Level", "titles": ["Junior Accountant", "Accounts Payable/Receivable Specialist", "Billing Clerk"]},
        },
        "roles": [
            "Financial Planning & Analysis (FP&A) Managers",
            "Corporate Tax Specialists",
            "Treasury & Cash Management Analysts",
            "Internal Audit & Compliance Officers",
            "Strategic Pricing Analysts",
        ],
        "default_skills": ["Financial Modeling", "Corporate Tax", "FP&A", "Advanced Excel (VBA)", "SAP ERP", "Treasury Management", "Internal Audit"],
        "interview_questions": [
            "How do you approach multi-entity financial consolidation and variance analysis?",
            "Describe your method for evaluating cash runway, working capital, and treasury risks.",
            "How do you maintain strict internal controls and compliance under statutory audits?",
        ],
    },
    "marketing": {
        "name": "Marketing & Growth",
        "icon": "📈",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["Chief Marketing Officer (CMO)", "VP of Growth", "Brand Director"]},
            "L4": {"label": "Management Level", "titles": ["Marketing Director", "Product Marketing Manager (PMM)", "SEO Director"]},
            "L3": {"label": "Lead Level", "titles": ["Content Lead", "Growth Marketing Lead", "Creative Director"]},
            "L2": {"label": "Senior Level", "titles": ["Senior Performance Marketing Specialist", "Senior Copywriter", "Senior Social Media Strategist"]},
            "L1": {"label": "Associate Level", "titles": ["Digital Marketing Executive", "Content Writer", "Marketing Coordinator"]},
        },
        "roles": [
            "Performance Marketing / Media Buyers (Paid Ads)",
            "SEO & Content Strategists",
            "Product Marketing Managers (PMM)",
            "Marketing Automation Specialists (HubSpot/Marketo)",
            "Data & Web Analytics Experts",
        ],
        "default_skills": ["Performance Marketing", "Meta Ads", "Google Ads", "SEO", "HubSpot", "Google Analytics 4", "Copywriting", "A/B Testing"],
        "interview_questions": [
            "What is your framework for reducing Customer Acquisition Cost (CAC) while scaling paid media?",
            "Explain how you design a multi-touch attribution model across search, paid social, and organic funnels.",
            "Describe an end-to-end product launch campaign you executed that exceeded pipeline targets.",
        ],
    },
    "trading": {
        "name": "Trading (Capital Markets & Proprietary)",
        "icon": "📉",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["Head of Trading", "Chief Risk Officer (CRO)", "Managing Director - Capital Markets"]},
            "L4": {"label": "Management Level", "titles": ["Desk Manager", "Desk Head", "Quantitative Research Director"]},
            "L3": {"label": "Lead Level", "titles": ["Principal Trader", "Senior Quant Researcher", "Lead Algorithmic Trader"]},
            "L2": {"label": "Senior Level", "titles": ["Senior Quantitative Trader", "Senior Risk Analyst", "Senior Derivatives Trader"]},
            "L1": {"label": "Associate Level", "titles": ["Junior Trader", "Execution Trader", "Quantitative Analyst (Quant Modeler)"]},
        },
        "roles": [
            "Algorithmic / Quantitative Traders",
            "High-Frequency Trading (HFT) Developers (C++/Rust)",
            "Risk Management Analysts",
            "Market Makers",
            "Settlement & Clearing Specialists",
        ],
        "default_skills": ["Algorithmic Trading", "Quantitative Modeling", "C++", "Python", "Derivatives Pricing", "Risk Management (VaR)", "Order Execution Systems"],
        "interview_questions": [
            "Explain how you design market-making strategies that remain resilient during high-volatility spikes.",
            "How do you model and manage tail risk and delta/gamma exposures in complex options portfolios?",
            "What techniques do you employ to minimize order latency in ultra-low latency execution engines?",
        ],
    },
    "investments": {
        "name": "Investments (PE, VC & Asset Management)",
        "icon": "💰",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["Managing Partner", "Chief Investment Officer (CIO)", "Fund Manager"]},
            "L4": {"label": "Management Level", "titles": ["Investment Director", "Principal"]},
            "L3": {"label": "Lead Level", "titles": ["Vice President (VP) of Investments", "Senior Associate"]},
            "L2": {"label": "Senior Level", "titles": ["Investment Associate", "Portfolio Analyst"]},
            "L1": {"label": "Associate Level", "titles": ["Investment Analyst", "Research Associate"]},
        },
        "roles": [
            "Deal Sourcing Specialists",
            "Portfolio Managers",
            "Due Diligence Analysts",
            "Valuation & Financial Modeling Experts",
            "Investor Relations Managers",
        ],
        "default_skills": ["Private Equity", "Venture Capital", "LBO Modeling", "DCF Valuation", "Commercial Due Diligence", "Cap Table Management", "Investor Relations"],
        "interview_questions": [
            "Walk me through your investment thesis evaluation and LBO returns modeling (IRR/MOIC).",
            "How do you conduct commercial and technical due diligence on pre-revenue vs late-stage companies?",
            "What strategies do you use for portfolio company value creation and post-acquisition synergy?",
        ],
    },
    "bpo": {
        "name": "Business Process Outsourcing (BPO)",
        "icon": "📞",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["VP of Operations", "Center Head", "General Manager - BPO"]},
            "L4": {"label": "Management Level", "titles": ["Operations Manager", "Program Manager", "Quality Assurance Director"]},
            "L3": {"label": "Lead Level", "titles": ["Team Leader (TL)", "Assistant Team Leader", "WFM Lead"]},
            "L2": {"label": "Senior Level", "titles": ["Subject Matter Expert (SME)", "Senior Customer Service Representative", "Senior Quality Analyst"]},
            "L1": {"label": "Associate Level", "titles": ["Customer Service Associate", "Inbound/Outbound Agent", "Chat Support Executive"]},
        },
        "roles": [
            "Customer Experience (CX) Specialists",
            "Technical Support Representatives",
            "Quality Analysts (QA)",
            "Workforce Management (WFM) Schedulers",
            "Training & Onboarding Specialists",
        ],
        "default_skills": ["English Fluency", "UK/US Accent", "Customer Support", "CRM (Zendesk/Salesforce)", "Inbound/Outbound Calling", "SLA Adherence", "WFM", "Active Listening"],
        "interview_questions": [
            "How do you handle difficult international customers while sustaining First Contact Resolution (FCR)?",
            "What workforce management methodologies do you use to forecast call shrinkages and staffing needs?",
            "Explain your quality audit process for evaluating agent call recordings and CSAT benchmarks.",
        ],
    },
    "kpo": {
        "name": "Knowledge Process Outsourcing (KPO)",
        "icon": "🧠",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["Head of Research & Analytics", "Delivery Head", "VP of KPO Services"]},
            "L4": {"label": "Management Level", "titles": ["Research Manager", "Analytics Manager", "Principal Consultant"]},
            "L3": {"label": "Lead Level", "titles": ["Team Lead - Analytics", "Lead Research Analyst", "Senior Legal Consultant"]},
            "L2": {"label": "Senior Level", "titles": ["Senior Data Analyst", "Senior Market Researcher", "Legal Consultant", "Patent Analyst"]},
            "L1": {"label": "Associate Level", "titles": ["Research Associate", "Business Analyst", "IP/Patent Analyst"]},
        },
        "roles": [
            "Market Research Analysts",
            "Intellectual Property (IP) & Patent Specialists",
            "Equity Research Analysts",
            "Data Scientists & Advanced Analytics Engineers",
            "Legal Process Consultants",
        ],
        "default_skills": ["Secondary Research", "Equity Valuation", "Patent Landscaping", "Data Analysis", "Bloomberg", "Power BI", "Tableau", "Financial Modeling"],
        "interview_questions": [
            "How do you structure primary and secondary research reports for C-suite strategic decisions?",
            "Describe your process for conducting patent prior-art searches and freedom-to-operate (FTO) analysis.",
            "Explain how you synthesize large qualitative datasets into actionable quantitative business insights.",
        ],
    },
    "inside_sales": {
        "name": "Inside Sales & Business Development",
        "icon": "🎯",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["Chief Revenue Officer (CRO)", "VP of Inside Sales", "Global Sales Director"]},
            "L4": {"label": "Management Level", "titles": ["Inside Sales Manager", "Account Executive (AE) Manager", "Sales Ops Director"]},
            "L3": {"label": "Lead Level", "titles": ["Sales Team Lead", "Senior Account Executive (Closer)"]},
            "L2": {"label": "Senior Level", "titles": ["Account Executive (AE)", "Senior Sales Development Representative (SDR)"]},
            "L1": {"label": "Associate Level", "titles": ["Sales Development Representative (SDR)", "Business Development Representative (BDR)"]},
        },
        "roles": [
            "Inbound/Outbound Lead Generation Specialists",
            "Account Executives (Closers)",
            "Sales Operations Specialists",
            "Customer Success Managers (Upselling/Cross-selling)",
            "Sales Enablement Trainers",
        ],
        "default_skills": ["B2B SaaS Sales", "Cold Calling", "Lead Qualification (MEDDIC/BANT)", "HubSpot", "Salesforce", "Pipeline Velocity", "Objection Handling", "Closing"],
        "interview_questions": [
            "Walk me through your outbound discovery call framework from cold opener to scheduled demo.",
            "How do you handle severe pricing objections and negotiate enterprise deal terms?",
            "What strategies do you implement to maintain high quota attainment month-over-month?",
        ],
    },
    "healthcare_ops": {
        "name": "Healthcare Operations & Medical Billing",
        "icon": "🏥",
        "levels": {
            "L5": {"label": "Executive Level", "titles": ["Chief Operating Officer (COO) - Healthcare", "Chief Medical Officer", "Hospital Administrator"]},
            "L4": {"label": "Management Level", "titles": ["Operations Director", "Clinical Operations Manager", "Medical Records Director"]},
            "L3": {"label": "Lead Level", "titles": ["Clinical Supervisor", "Billing & Coding Lead", "Compliance Officer"]},
            "L2": {"label": "Senior Level", "titles": ["Senior Medical Coder", "Healthcare Quality Analyst", "Patient Relations Team Lead"]},
            "L1": {"label": "Associate Level", "titles": ["Medical Billing Executive", "Patient Care Coordinator", "Medical Transcriptionist"]},
        },
        "roles": [
            "Medical Coders (ICD-10 / CPT Specialists)",
            "Revenue Cycle Management (RCM) Analysts",
            "Clinical Data Managers",
            "Patient Care Coordinators",
            "Healthcare Compliance & Risk Officers",
        ],
        "default_skills": ["ICD-10 Coding", "CPT Coding", "Medical Billing", "HIPAA Compliance", "Claims Denial Management", "Revenue Cycle Management (RCM)", "EHR Systems"],
        "interview_questions": [
            "How do you handle complex insurance denial appeals under stringent timely filing regulations?",
            "Explain HIPAA privacy guidelines regarding electronic protected health information (ePHI).",
            "Describe your workflow for optimizing clean claims rate and reducing Days in A/R.",
        ],
    }
}


def get_all_job_presets() -> List[Dict[str, Any]]:
    """Return a flat list of ready-to-use job presets across all 9 verticals and levels."""
    presets = []
    for v_key, v_data in INDUSTRY_TAXONOMY.items():
        v_name = v_data["name"]
        v_icon = v_data["icon"]
        
        for lvl_key, lvl_data in v_data["levels"].items():
            lvl_label = lvl_data["label"]
            for title in lvl_data["titles"]:
                presets.append({
                    "vertical_key": v_key,
                    "vertical_name": v_name,
                    "level_code": lvl_key,
                    "level_label": lvl_label,
                    "display_name": f"{v_icon} {title} ({lvl_key} - {v_name})",
                    "title": title,
                    "department": v_name,
                    "skills": v_data["default_skills"],
                    "interview_questions": v_data["interview_questions"],
                })
    return presets
