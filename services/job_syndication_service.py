"""Third-Party Job Board Ecosystem & Syndication Service.

Provides:
1. Google for Jobs JSON-LD Schema (schema.org/JobPosting) for organic search indexing.
2. Indeed & Aggregator XML Feed generation (Indeed XML standard format).
3. Multi-Portal Syndication Dispatch payloads (LinkedIn, Indeed, ZipRecruiter, Naukri).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from xml.sax.saxutils import escape

from services.sanitization_service import sanitize_text


def generate_google_jobs_json_ld(
    job: Dict[str, Any],
    company_name: str = "Netizen AI Automation Ltd.",
    company_url: str = "https://netizen.ai",
    careers_url: str = "http://127.0.0.1:8501",
) -> Dict[str, Any]:
    """Generate RFC/W3C compliant schema.org/JobPosting JSON-LD for Google for Jobs."""
    clean_title = sanitize_text(job.get("title", "Software Engineer"))
    clean_desc = sanitize_text(job.get("job_description") or job.get("description") or clean_title)
    clean_location = sanitize_text(job.get("location", "Remote"))
    clean_dept = sanitize_text(job.get("department", "Engineering"))
    job_id = str(job.get("id", "job_001"))

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    valid_through = (datetime.now(timezone.utc) + timedelta(days=60)).strftime("%Y-%m-%d")

    salary_min = float(job.get("salary_min") or 600000.0)
    salary_max = float(job.get("salary_max") or 1200000.0)

    schema = {
        "@context": "https://schema.org/",
        "@type": "JobPosting",
        "title": clean_title,
        "description": f"<p>{clean_desc}</p>",
        "identifier": {
            "@type": "PropertyValue",
            "name": company_name,
            "value": job_id,
        },
        "datePosted": now_iso,
        "validThrough": valid_through,
        "employmentType": "FULL_TIME",
        "hiringOrganization": {
            "@type": "Organization",
            "name": company_name,
            "sameAs": company_url,
        },
        "jobLocation": {
            "@type": "Place",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": clean_location,
                "addressCountry": "IN",
            },
        },
        "baseSalary": {
            "@type": "MonetaryAmount",
            "currency": "INR",
            "value": {
                "@type": "QuantitativeValue",
                "minValue": salary_min,
                "maxValue": salary_max,
                "unitText": "YEAR",
            },
        },
        "directApply": True,
        "url": f"{careers_url}/?job_id={job_id}",
    }
    return schema


def generate_indeed_xml_feed(
    jobs: List[Dict[str, Any]],
    company_name: str = "Netizen AI Automation Ltd.",
    careers_url: str = "http://127.0.0.1:8501",
) -> str:
    """Generate an Indeed Publisher XML feed with valid CDATA blocks."""
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        "<source>",
        f"  <publisher>{escape(company_name)}</publisher>",
        f"  <publisherurl>{escape(careers_url)}</publisherurl>",
        f"  <lastBuildDate>{datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>",
    ]

    for job in jobs:
        j_id = str(job.get("id", ""))
        title = escape(sanitize_text(job.get("title", "Role")))
        desc = escape(sanitize_text(job.get("job_description") or job.get("description") or title))
        loc = escape(sanitize_text(job.get("location", "Pune, India")))
        category = escape(sanitize_text(job.get("department", "Technology")))
        sal_min = str(job.get("salary_min") or "")
        sal_max = str(job.get("salary_max") or "")
        job_url = f"{careers_url}/?job_id={j_id}"

        lines.append("  <job>")
        lines.append(f"    <title><![CDATA[{title}]]></title>")
        lines.append(f"    <date><![CDATA[{datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}]]></date>")
        lines.append(f"    <referencenumber><![CDATA[{j_id}]]></referencenumber>")
        lines.append(f"    <url><![CDATA[{job_url}]]></url>")
        lines.append(f"    <company><![CDATA[{company_name}]]></company>")
        lines.append(f"    <city><![CDATA[{loc}]]></city>")
        lines.append("    <country><![CDATA[IN]]></country>")
        lines.append(f"    <description><![CDATA[{desc}]]></description>")
        lines.append(f"    <category><![CDATA[{category}]]></category>")
        if sal_min or sal_max:
            lines.append(f"    <salary><![CDATA[INR {sal_min} - {sal_max} per annum]]></salary>")
        lines.append("  </job>")

    lines.append("</source>")
    return "\n".join(lines)


def generate_linkedin_job_posting_payload(
    job: Dict[str, Any],
    company_urn: str = "urn:li:organization:9847123",
    company_name: str = "Netizen AI Automation Ltd.",
    careers_url: str = "http://127.0.0.1:8501",
) -> Dict[str, Any]:
    """Generate official LinkedIn Job Posting API v2 compliant payload."""
    clean_title = sanitize_text(job.get("title", "Software Engineer"))
    clean_desc = sanitize_text(job.get("job_description") or job.get("description") or clean_title)
    job_id = str(job.get("id", "job_001"))
    loc = sanitize_text(job.get("location", "Remote"))
    is_remote = "remote" in loc.lower()
    apply_url = f"{careers_url}/?job_id={job_id}&utm_source=linkedin&utm_medium=job_posting_api"

    sal_min = float(job.get("salary_min") or 600000.0)
    sal_max = float(job.get("salary_max") or 1400000.0)

    return {
        "externalJobPostingId": job_id,
        "title": clean_title,
        "description": clean_desc,
        "companyName": company_name,
        "company": company_urn,
        "location": loc,
        "workplaceTypes": ["urn:li:workplaceType:2"] if is_remote else ["urn:li:workplaceType:1"],
        "jobPostingOperationType": "CREATE",
        "employmentStatus": "FULL_TIME",
        "listedAt": int(datetime.now(timezone.utc).timestamp() * 1000),
        "applicationMethod": {
            "externalJobApplicationUrl": apply_url,
        },
        "compensation": {
            "currencyCode": "INR",
            "minAmount": sal_min,
            "maxAmount": sal_max,
            "period": "ANNUAL",
        },
        "tracking_source": "LINKEDIN_OFFICIAL_API",
        "status": "READY_FOR_DISPATCH",
    }


def generate_naukri_job_posting_payload(
    job: Dict[str, Any],
    company_name: str = "Netizen AI Automation Ltd.",
    careers_url: str = "http://127.0.0.1:8501",
) -> Dict[str, Any]:
    """Generate official Naukri.com / InfoEdge eApps JSON payload."""
    clean_title = sanitize_text(job.get("title", "Software Engineer"))
    clean_desc = sanitize_text(job.get("job_description") or job.get("description") or clean_title)
    job_id = str(job.get("id", "job_001"))
    loc = sanitize_text(job.get("location", "Pune"))
    skills = job.get("skills_required") or ["Python", "FastAPI", "SQL", "Cloud"]
    if isinstance(skills, list):
        keywords_str = ", ".join(skills)
    else:
        keywords_str = str(skills)

    sal_min = float(job.get("salary_min") or 600000.0)
    sal_max = float(job.get("salary_max") or 1400000.0)
    apply_url = f"{careers_url}/?job_id={job_id}&utm_source=naukri&utm_medium=job_portal"

    return {
        "jobReferenceId": job_id,
        "jobTitle": clean_title,
        "jobDescription": clean_desc,
        "companyName": company_name,
        "minExperienceYears": int(job.get("min_experience", 2)),
        "maxExperienceYears": int(job.get("max_experience", 6)),
        "minSalaryAnnualINR": sal_min,
        "maxSalaryAnnualINR": sal_max,
        "hideSalaryFromCandidate": False,
        "keywords": keywords_str,
        "locations": [loc],
        "functionalArea": "IT Software - Application Programming / Maintenance",
        "roleCategory": "Programming & Design",
        "vacancies": int(job.get("vacancies", 1)),
        "applyUrl": apply_url,
        "tracking_source": "NAUKRI_RESDEX_EAPPS_API",
        "status": "READY_FOR_DISPATCH",
    }


def generate_multi_board_broadcast_payload(
    job: Dict[str, Any],
    target_boards: Optional[List[str]] = None,
    company_name: str = "Netizen AI Automation Ltd.",
) -> Dict[str, Any]:
    """Format syndication payloads for LinkedIn, Naukri, Indeed, and ZipRecruiter with UTM tags."""
    if not target_boards:
        target_boards = ["linkedin", "naukri", "indeed", "ziprecruiter"]

    clean_title = sanitize_text(job.get("title", ""))
    job_id = str(job.get("id", ""))
    base_url = "http://127.0.0.1:8501"

    broadcast_data = {}
    for board in target_boards:
        if board == "linkedin":
            broadcast_data["linkedin"] = generate_linkedin_job_posting_payload(job, company_name=company_name, careers_url=base_url)
        elif board == "naukri":
            broadcast_data["naukri"] = generate_naukri_job_posting_payload(job, company_name=company_name, careers_url=base_url)
        else:
            utm_url = f"{base_url}/?job_id={job_id}&utm_source={board}&utm_medium=job_board&utm_campaign=hiring"
            broadcast_data[board] = {
                "title": clean_title,
                "job_reference_id": job_id,
                "company": company_name,
                "location": job.get("location", "Remote"),
                "apply_url": utm_url,
                "status": "READY_FOR_SYNDICATION",
                "syndicated_at": datetime.now(timezone.utc).isoformat(),
            }

    return {
        "job_id": job_id,
        "job_title": clean_title,
        "boards_syndicated": list(broadcast_data.keys()),
        "payloads": broadcast_data,
        "success": True,
    }