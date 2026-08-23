"""Job Feed Syndication Service for Naukri, Indeed, Foundit, and Google for Jobs.

Generates standard ATS XML and JSON feeds for automatic job board aggregation.
"""

from __future__ import annotations

import html
from datetime import datetime, timezone
from typing import Any, Dict, List
import pandas as pd


def generate_indeed_xml_feed(jobs_df: pd.DataFrame, company_name: str = "Netizen Recruitment", base_app_url: str = "http://localhost:8501") -> str:
    """Generates standard Indeed / Google for Jobs compliant XML feed."""
    xml_items = []
    xml_items.append('<?xml version="1.0" encoding="utf-8"?>')
    xml_items.append("<source>")
    xml_items.append(f"  <publisher>{html.escape(company_name)}</publisher>")
    xml_items.append(f"  <publisherurl>{html.escape(base_app_url)}</publisherurl>")
    xml_items.append(f"  <lastBuildDate>{datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>")

    if not jobs_df.empty and "id" in jobs_df.columns:
        for _, row in jobs_df.iterrows():
            if str(row.get("status", "")).casefold() == "archived":
                continue
            
            job_id = str(row.get("id", ""))
            title = str(row.get("title", "Open Position"))
            dept = str(row.get("department", "General"))
            loc = str(row.get("location", "Pune, Maharashtra, India"))
            desc = str(row.get("job_description") or row.get("description", f"We are hiring a {title}."))
            exp = str(row.get("experience_required") or row.get("min_experience", "2+ years"))
            sal_min = str(row.get("salary_min", ""))
            sal_max = str(row.get("salary_max", ""))
            emp_type = str(row.get("employment_type", "Full Time"))
            
            app_url = f"{base_app_url}/?job_id={job_id}"

            xml_items.append("  <job>")
            xml_items.append(f"    <title><![CDATA[{title}]]></title>")
            xml_items.append(f"    <referenceNumber><![CDATA[{job_id}]]></referenceNumber>")
            xml_items.append(f"    <url><![CDATA[{app_url}]]></url>")
            xml_items.append(f"    <company><![CDATA[{company_name}]]></company>")
            xml_items.append(f"    <city><![CDATA[{loc.split(',')[0].strip()}]]></city>")
            xml_items.append("    <country><![CDATA[IN]]></country>")
            xml_items.append(f"    <category><![CDATA[{dept}]]></category>")
            xml_items.append(f"    <jobtype><![CDATA[{emp_type}]]></jobtype>")
            xml_items.append(f"    <experience><![CDATA[{exp}]]></experience>")
            if sal_min and sal_max:
                xml_items.append(f"    <salary><![CDATA[INR {sal_min} - {sal_max}]]></salary>")
            xml_items.append(f"    <description><![CDATA[{desc}]]></description>")
            xml_items.append("  </job>")

    xml_items.append("</source>")
    return "\n".join(xml_items)
