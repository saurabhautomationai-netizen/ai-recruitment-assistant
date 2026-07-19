import html
import json
from datetime import date, datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from components.candidate_communications import (
    MESSAGE_TYPES,
    build_candidate_messages,
)
from components.metric_cards import metric_card
from services.supabase_service import (
    create_interview,
    create_recruiter_note,
    get_applications,
    get_candidates,
    get_interviews,
    get_jobs,
    get_recruiter_notes,
    update_application_stage,
    update_interview,
)


st.set_page_config(
    page_title="AI Recruitment Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# Styling
# =========================================================
st.markdown(
    """
    <style>
        .stApp {
            background: #f5f7fb;
        }

        [data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e8ebf2;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.85);
        }

        .main-title {
            font-size: 32px;
            font-weight: 750;
            color: #152238;
            margin-bottom: 2px;
        }

        .main-subtitle {
            color: #6b7280;
            font-size: 15px;
            margin-bottom: 24px;
        }

        .metric-card {
            background: #ffffff;
            border: 1px solid #e8ebf2;
            border-radius: 16px;
            padding: 20px;
            min-height: 135px;
            box-shadow: 0 8px 24px rgba(32, 48, 74, 0.06);
        }

        .metric-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .metric-icon {
            font-size: 24px;
            background: #eef4ff;
            border-radius: 10px;
            padding: 8px 11px;
        }

        .metric-change {
            color: #16855b;
            background: #eaf8f1;
            border-radius: 20px;
            padding: 4px 9px;
            font-size: 12px;
            font-weight: 600;
        }

        .metric-value {
            color: #152238;
            font-size: 30px;
            font-weight: 750;
            margin-top: 14px;
        }

        .metric-title {
            color: #6b7280;
            font-size: 14px;
        }

        h1, h2, h3 {
            color: #152238;
        }

        .candidate-profile-card {
            background: #ffffff;
            border: 1px solid #e5e9f2;
            border-radius: 18px;
            padding: 24px;
            margin-top: 12px;
            margin-bottom: 20px;
            box-shadow: 0 8px 28px rgba(32, 48, 74, 0.07);
        }

        .candidate-profile-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 24px;
        }

        .candidate-identity {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .candidate-avatar {
            width: 58px;
            height: 58px;
            border-radius: 16px;
            background: #eef4ff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
        }

        .candidate-name {
            font-size: 25px;
            font-weight: 750;
            color: #152238;
            margin-bottom: 3px;
        }

        .candidate-role {
            color: #667085;
            font-size: 15px;
        }

        .candidate-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
        }

        .candidate-meta-item {
            background: #f7f9fc;
            border: 1px solid #e8ebf2;
            border-radius: 10px;
            padding: 8px 12px;
            color: #475467;
            font-size: 13px;
        }

        .status-badge {
            display: inline-block;
            border-radius: 20px;
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 650;
        }

        .status-pending {
            background: #fff4dd;
            color: #9a6700;
        }

        .status-shortlisted {
            background: #eaf8f1;
            color: #137a52;
        }

        .status-interview {
            background: #eaf2ff;
            color: #2457a6;
        }

        .status-rejected {
            background: #fff0f0;
            color: #b42318;
        }

        .status-selected {
            background: #e8f7ed;
            color: #067647;
        }

        .score-panel {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .score-box {
            min-width: 125px;
            background: #f8faff;
            border: 1px solid #e4e9f3;
            border-radius: 14px;
            padding: 14px;
            text-align: center;
        }

        .score-number {
            font-size: 25px;
            font-weight: 750;
            color: #152238;
        }

        .score-label {
            color: #667085;
            font-size: 12px;
            margin-top: 3px;
        }

        .skills-container {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
            margin-bottom: 18px;
        }

        .skill-chip {
            display: inline-block;
            background: #eef4ff;
            border: 1px solid #dce8ff;
            color: #2457a6;
            border-radius: 20px;
            padding: 6px 11px;
            font-size: 13px;
            font-weight: 550;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Sidebar
# =========================================================
with st.sidebar:
    st.markdown("## 🧠 ZERO Recruit")
    st.caption("AI Recruitment Assistant")

    selected_page = st.radio(
        "Navigation",
        [
            "Overview",
            "Candidates",
            "Applications",
            "Jobs",
            "Interviews",
            "AI Recruiter",
            "Analytics",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("Refresh database"):
        st.cache_data.clear()
        st.rerun()

    st.caption("Portfolio Version 1.0")


# =========================================================
# Load live database data
# =========================================================
raw_candidates = get_candidates()
raw_applications = get_applications()
raw_jobs = get_jobs()


# =========================================================
# Prepare joined candidate data
# =========================================================
def prepare_candidate_data(
    candidate_data: pd.DataFrame,
    application_data: pd.DataFrame,
    job_data: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine candidates, applications and jobs using the real
    Supabase database column names.
    """

    display_columns = [
        "Candidate",
        "Role",
        "Experience",
        "Candidate Score",
        "ATS Score",
        "Status",
        "Applied On",
    ]

    if candidate_data.empty:
        return pd.DataFrame(columns=display_columns)

    candidates_df = candidate_data.copy()

    candidates_df = candidates_df.rename(
        columns={
            "id": "candidate_id",
            "full_name": "Candidate",
            "years_experience": "Experience",
            "status": "candidate_status",
        }
    )

    # -----------------------------------------------------
    # Applications
    # -----------------------------------------------------
    if not application_data.empty:
        applications_df = application_data.copy()

        required_application_columns = [
            "candidate_id",
            "job_id",
            "candidate_score",
            "ats_score",
            "application_stage",
            "applied_at",
        ]

        available_application_columns = [
            column
            for column in required_application_columns
            if column in applications_df.columns
        ]

        applications_df = applications_df[
            available_application_columns
        ]

        if (
            "applied_at" in applications_df.columns
            and "candidate_id" in applications_df.columns
        ):
            applications_df["applied_at"] = pd.to_datetime(
                applications_df["applied_at"],
                errors="coerce",
            )

            applications_df = applications_df.sort_values(
                "applied_at",
                ascending=False,
            )

        if "candidate_id" in applications_df.columns:
            applications_df = applications_df.drop_duplicates(
                subset=["candidate_id"],
                keep="first",
            )

            candidates_df = candidates_df.merge(
                applications_df,
                on="candidate_id",
                how="left",
            )

    # -----------------------------------------------------
    # Jobs
    # -----------------------------------------------------
    if (
        not job_data.empty
        and "job_id" in candidates_df.columns
    ):
        jobs_df = job_data.copy()

        jobs_df = jobs_df.rename(
            columns={
                "id": "job_id",
                "title": "Role",
            }
        )

        job_columns = [
            column
            for column in [
                "job_id",
                "Role",
            ]
            if column in jobs_df.columns
        ]

        jobs_df = jobs_df[job_columns]

        if "job_id" in jobs_df.columns:
            candidates_df = candidates_df.merge(
                jobs_df,
                on="job_id",
                how="left",
            )

    # -----------------------------------------------------
    # Fallback values
    # -----------------------------------------------------
    if "Candidate" not in candidates_df.columns:
        candidates_df["Candidate"] = "Unknown candidate"

    if "Role" not in candidates_df.columns:
        candidates_df["Role"] = "Not assigned"

    candidates_df["Role"] = candidates_df["Role"].fillna(
        "Not assigned"
    )

    if "Experience" not in candidates_df.columns:
        candidates_df["Experience"] = None

    if "candidate_score" not in candidates_df.columns:
        candidates_df["candidate_score"] = 0

    if "ats_score" not in candidates_df.columns:
        candidates_df["ats_score"] = 0

    candidates_df["Candidate Score"] = pd.to_numeric(
        candidates_df["candidate_score"],
        errors="coerce",
    ).fillna(0)

    candidates_df["ATS Score"] = pd.to_numeric(
        candidates_df["ats_score"],
        errors="coerce",
    ).fillna(0)

    if "application_stage" in candidates_df.columns:
        candidates_df["Status"] = candidates_df[
            "application_stage"
        ]

        if "candidate_status" in candidates_df.columns:
            candidates_df["Status"] = candidates_df[
                "Status"
            ].fillna(
                candidates_df["candidate_status"]
            )
    elif "candidate_status" in candidates_df.columns:
        candidates_df["Status"] = candidates_df[
            "candidate_status"
        ]
    else:
        candidates_df["Status"] = "Pending Review"

    candidates_df["Status"] = candidates_df["Status"].fillna(
        "Pending Review"
    )

    def format_experience(value) -> str:
        if pd.isna(value) or str(value).strip() == "":
            return "Not provided"

        text = str(value).strip()

        if text.lower().endswith(
            ("year", "years", "month", "months")
        ):
            return text

        return f"{text} years"

    candidates_df["Experience"] = candidates_df[
        "Experience"
    ].apply(format_experience)

    if "applied_at" in candidates_df.columns:
        candidates_df["Applied On"] = pd.to_datetime(
            candidates_df["applied_at"],
            errors="coerce",
        ).dt.strftime("%d %b %Y, %I:%M %p")

        candidates_df["Applied On"] = candidates_df[
            "Applied On"
        ].fillna("Not available")
    else:
        candidates_df["Applied On"] = "Not available"


    return candidates_df[display_columns]


candidates = prepare_candidate_data(
    raw_candidates,
    raw_applications,
    raw_jobs,
)


# =========================================================
# Dashboard metrics
# =========================================================
def count_status(statuses: list[str]) -> int:
    """Count candidates matching one or more application stages."""

    if candidates.empty:
        return 0

    normalized_statuses = [
        status.strip().lower()
        for status in statuses
    ]

    return int(
        candidates["Status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .isin(normalized_statuses)
        .sum()
    )


total_candidates = len(candidates)
total_applications = len(raw_applications)

pending_count = count_status(
    [
        "Pending Review",
        "Applied",
    ]
)

shortlisted_count = count_status(
    [
        "Shortlisted",
    ]
)

interview_count = count_status(
    [
        "Interview",
        "Interview Scheduled",
    ]
)

selected_count = count_status(
    [
        "Selected",
        "Hired",
        "Joined",
    ]
)


if candidates.empty:
    average_candidate_score = 0
    average_ats_score = 0
else:
    average_candidate_score = round(
        candidates["Candidate Score"].mean(),
        1,
    )

    average_ats_score = round(
        candidates["ATS Score"].mean(),
        1,
    )


if raw_jobs.empty:
    open_jobs_count = 0
elif "status" in raw_jobs.columns:
    open_jobs_count = int(
        raw_jobs["status"]
        .astype(str)
        .str.strip()
        .str.lower()
        .eq("open")
        .sum()
    )
else:
    open_jobs_count = len(raw_jobs)


pipeline = pd.DataFrame(
    {
        "Stage": [
            "Applied",
            "Pending Review",
            "Shortlisted",
            "Interview",
            "Selected",
        ],
        "Candidates": [
            total_applications,
            pending_count,
            shortlisted_count,
            interview_count,
            selected_count,
        ],
    }
)


# =========================================================
# Reusable candidate table
# =========================================================
def show_candidate_table(
    candidate_df: pd.DataFrame,
) -> None:
    """Display a formatted candidate table."""

    if candidate_df.empty:
        st.info("No candidates found.")
        return

    st.dataframe(
        candidate_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Candidate Score": st.column_config.ProgressColumn(
                "Candidate Score",
                min_value=0,
                max_value=100,
                format="%d%%",
            ),
            "ATS Score": st.column_config.ProgressColumn(
                "ATS Score",
                min_value=0,
                max_value=100,
                format="%d%%",
            ),
        },
    )

def safe_value(
    row: pd.Series,
    column: str,
    default: str = "Not available",
) -> str:
    """Safely return a value from a pandas row."""

    if row.empty or column not in row.index:
        return default

    value = row[column]

    if value is None:
        return default

    if isinstance(value, float) and pd.isna(value):
        return default

    if str(value).strip() == "":
        return default

    return str(value)


def parse_stored_value(value):
    """Parse stored JSON when possible without failing on malformed data."""

    if value is None:
        return None

    if not isinstance(value, (dict, list, tuple, set)):
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass

    if not isinstance(value, str):
        return value

    text = value.strip()

    if not text:
        return None

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text


def evaluation_value(
    evaluation_data,
    field_names: tuple[str, ...],
):
    """Return the first available field from structured evaluation data."""

    if not isinstance(evaluation_data, dict):
        return None

    for field_name in field_names:
        value = parse_stored_value(
            evaluation_data.get(field_name)
        )

        if value not in (None, "", [], {}):
            return value

    return None


def display_items(value) -> list[str]:
    """Normalize stored scalar or list content for safe display."""

    parsed_value = parse_stored_value(value)

    if parsed_value is None:
        return []

    if isinstance(parsed_value, list):
        items = parsed_value
    else:
        items = [parsed_value]

    return [
        str(item).strip()
        for item in items
        if item is not None and str(item).strip()
    ]


def show_evaluation_detail(
    label: str,
    value,
) -> None:
    """Display one optional evaluation detail without inventing content."""

    st.markdown(f"**{label}**")
    items = display_items(value)

    if not items:
        st.caption("Not available")
    elif len(items) == 1:
        st.write(items[0])
    else:
        for item in items:
            st.markdown(f"- {item}")


def normalize_interview_questions(
    value,
) -> list[tuple[str | None, str]]:
    """Normalize stored interview questions and real category metadata."""

    parsed_value = parse_stored_value(value)

    if parsed_value is None:
        return []

    inherited_category = None

    if isinstance(parsed_value, dict):
        inherited_category = parsed_value.get("category")
        questions = parsed_value.get("questions", [])
    elif isinstance(parsed_value, list):
        questions = parsed_value
    else:
        questions = [parsed_value]

    if not isinstance(questions, list):
        questions = [questions]

    normalized_questions = []

    for question in questions:
        category = inherited_category

        if isinstance(question, dict):
            question_text = question.get(
                "question",
                question.get("text"),
            )
            category = question.get(
                "category",
                category,
            )
        else:
            question_text = question

        if question_text is None:
            continue

        question_text = str(question_text).strip()
        category_text = (
            str(category).strip()
            if category is not None
            else ""
        )

        if question_text:
            normalized_questions.append(
                (
                    category_text or None,
                    question_text,
                )
            )

    return normalized_questions


def show_interview_questions(value) -> None:
    """Display stored interview questions as clean cards."""

    questions = normalize_interview_questions(value)

    if not questions:
        st.info("No interview questions are available.")
        return

    categories = []

    for category, _ in questions:
        if category and category not in categories:
            categories.append(category)

    grouped_questions = [
        (category, [
            question
            for item_category, question in questions
            if item_category == category
        ])
        for category in categories
    ]

    unclassified_questions = [
        question
        for category, question in questions
        if category is None
    ]

    if unclassified_questions:
        grouped_questions.append(
            (None, unclassified_questions)
        )

    question_number = 1

    for category, category_questions in grouped_questions:
        if category:
            st.markdown(f"##### {category}")
        elif categories:
            st.markdown("##### Interview Questions")

        for question in category_questions:
            with st.container(border=True):
                st.markdown(f"**Question {question_number}**")
                st.write(question)

            question_number += 1

def get_status_class(status: str) -> str:
    """Return the CSS class for an application status."""

    normalized_status = str(status).strip().lower()

    if normalized_status in ["shortlisted", "shortlist"]:
        return "status-shortlisted"

    if normalized_status in [
        "interview",
        "interview scheduled",
    ]:
        return "status-interview"

    if normalized_status in ["rejected", "reject"]:
        return "status-rejected"

    if normalized_status in [
        "selected",
        "hired",
        "joined",
    ]:
        return "status-selected"

    return "status-pending"


def parse_skills(value) -> list[str]:
    """Convert skills stored as text, list, or JSON into a clean list."""

    if value is None:
        return []

    if isinstance(value, float) and pd.isna(value):
        return []

    if isinstance(value, list):
        return [
            str(skill).strip()
            for skill in value
            if str(skill).strip()
        ]

    if isinstance(value, dict):
        possible_skills = value.get(
            "skills",
            list(value.values()),
        )

        if isinstance(possible_skills, list):
            return [
                str(skill).strip()
                for skill in possible_skills
                if str(skill).strip()
            ]

    skill_text = str(value).strip()

    if not skill_text:
        return []

    try:
        parsed_value = json.loads(skill_text)

        if isinstance(parsed_value, list):
            return [
                str(skill).strip()
                for skill in parsed_value
                if str(skill).strip()
            ]

        if isinstance(parsed_value, dict):
            possible_skills = parsed_value.get(
                "skills",
                [],
            )

            if isinstance(possible_skills, list):
                return [
                    str(skill).strip()
                    for skill in possible_skills
                    if str(skill).strip()
                ]

    except json.JSONDecodeError:
        pass

    separators = ["\n", ";", "|"]

    for separator in separators:
        skill_text = skill_text.replace(
            separator,
            ",",
        )

    return [
        skill.strip()
        for skill in skill_text.split(",")
        if skill.strip()
    ]


def show_skill_chips(value) -> None:
    """Render candidate skills as visual chips."""

    skills = parse_skills(value)

    if not skills:
        st.info("No skills are available.")
        return

    chips_html = "".join(
        f'<span class="skill-chip">{html.escape(str(skill))}</span>'
        for skill in skills
        if str(skill).strip()
    )

    st.markdown(
        f"""
        <div class="skills-container">
            {chips_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# Overview page
# =========================================================
if selected_page == "Overview":
    st.markdown(
        '<div class="main-title">'
        "Recruitment Overview"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "Live hiring performance across candidates, jobs and applications."
        "</div>",
        unsafe_allow_html=True,
    )

    # Main KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Total Candidates",
            total_candidates,
            "Live database",
            "👥",
        )

    with col2:
        metric_card(
            "Open Jobs",
            open_jobs_count,
            "Live database",
            "💼",
        )

    with col3:
        metric_card(
            "Average Candidate Score",
            f"{average_candidate_score}%",
            "AI evaluation",
            "🧠",
        )

    with col4:
        metric_card(
            "Pending Reviews",
            pending_count,
            "Needs attention",
            "📋",
        )

    st.write("")

    # Secondary KPI cards
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        metric_card(
            "Applications",
            total_applications,
            "Live database",
            "📨",
        )

    with col6:
        metric_card(
            "Average ATS Score",
            f"{average_ats_score}%",
            "Resume compatibility",
            "📄",
        )

    with col7:
        metric_card(
            "Interviews",
            interview_count,
            "Pipeline stage",
            "📅",
        )

    with col8:
        metric_card(
            "Selected",
            selected_count,
            "Successful hires",
            "✅",
        )

    st.write("")

    # Charts
    chart_col, score_col = st.columns(
        [1.6, 1]
    )

    with chart_col:
        st.markdown("### Hiring Pipeline")

        if total_applications > 0:
            funnel_chart = px.funnel(
                pipeline,
                x="Candidates",
                y="Stage",
            )

            funnel_chart.update_layout(
                height=370,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20,
                ),
                paper_bgcolor="white",
                plot_bgcolor="white",
                showlegend=False,
            )

            st.plotly_chart(
                funnel_chart,
                width="stretch",
                config={
                    "displayModeBar": False,
                },
            )
        else:
            st.info(
                "No application pipeline data is available."
            )

    with score_col:
        st.markdown(
            "### Candidate Score Distribution"
        )

        scored_candidates = candidates[
            candidates["Candidate Score"] > 0
        ]

        if not scored_candidates.empty:
            score_chart = px.histogram(
                scored_candidates,
                x="Candidate Score",
                nbins=10,
            )

            score_chart.update_layout(
                height=370,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20,
                ),
                paper_bgcolor="white",
                plot_bgcolor="white",
                showlegend=False,
                xaxis_title="Candidate Score",
                yaxis_title="Candidates",
            )

            st.plotly_chart(
                score_chart,
                width="stretch",
                config={
                    "displayModeBar": False,
                },
            )
        else:
            st.info(
                "Candidate scores are not available yet."
            )

    # Top candidates
    st.markdown("### Top Candidates")

    if candidates.empty:
        st.info("No candidates are available.")
    else:
        top_candidates = candidates.sort_values(
            by="Candidate Score",
            ascending=False,
        ).head(5)

        show_candidate_table(top_candidates)

    # Recent applications
    st.markdown("### Recent Applications")

    if raw_applications.empty:
        st.info("No applications found.")
    else:
        application_display_columns = [
            column
            for column in [
                "candidate_id",
                "job_id",
                "application_stage",
                "candidate_score",
                "ats_score",
                "recommendation",
                "applied_at",
            ]
            if column in raw_applications.columns
        ]

        recent_applications = raw_applications[
            application_display_columns
        ].head(10)

        recent_applications = recent_applications.rename(
            columns={
                "candidate_id": "Candidate ID",
                "job_id": "Job ID",
                "application_stage": "Stage",
                "candidate_score": "Candidate Score",
                "ats_score": "ATS Score",
                "recommendation": "Recommendation",
                "applied_at": "Applied On",
            }
        )

        st.dataframe(
            recent_applications,
            width="stretch",
            hide_index=True,
            column_config={
                "Candidate Score": st.column_config.ProgressColumn(
                    "Candidate Score",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                ),
                "ATS Score": st.column_config.ProgressColumn(
                    "ATS Score",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                ),
            },
        )


# =========================================================
# Candidates page
# =========================================================
elif selected_page == "Candidates":
    st.markdown(
        '<div class="main-title">Candidates</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "Search candidates and review their complete recruitment profile."
        "</div>",
        unsafe_allow_html=True,
    )

    if candidates.empty or raw_candidates.empty:
        st.info("No candidates found.")

    else:
        # -------------------------------------------------
        # Candidate filters
        # -------------------------------------------------
        search_col, status_col, role_col = st.columns(
            [2, 1, 1]
        )

        with search_col:
            search_text = st.text_input(
                "Search candidates",
                placeholder=(
                    "Search by candidate, role, status, "
                    "experience or score"
                ),
            )

        available_statuses = sorted(
            candidates["Status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        with status_col:
            selected_status = st.selectbox(
                "Status",
                ["All"] + available_statuses,
            )

        available_roles = sorted(
            candidates["Role"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        with role_col:
            selected_role = st.selectbox(
                "Role",
                ["All"] + available_roles,
            )

        filtered_candidates = candidates.copy()

        if search_text:
            normalized_search = search_text.strip().lower()

            filtered_candidates = filtered_candidates[
                filtered_candidates.astype(str).apply(
                    lambda row: row.str.lower().str.contains(
                        normalized_search,
                        regex=False,
                    ).any(),
                    axis=1,
                )
            ]

        if selected_status != "All":
            filtered_candidates = filtered_candidates[
                filtered_candidates["Status"]
                == selected_status
            ]

        if selected_role != "All":
            filtered_candidates = filtered_candidates[
                filtered_candidates["Role"]
                == selected_role
            ]

        st.markdown("### Candidate Directory")

        show_candidate_table(filtered_candidates)

        st.divider()

        # -------------------------------------------------
        # Candidate profile selector
        # -------------------------------------------------
        st.markdown("### Candidate Profile")

        candidate_options = {}

        for _, candidate_row in raw_candidates.iterrows():
            candidate_id = str(
                candidate_row.get("id", "")
            )

            candidate_name = str(
                candidate_row.get(
                    "full_name",
                    "Unknown candidate",
                )
            )

            candidate_email = str(
                candidate_row.get(
                    "email",
                    "",
                )
            )

            option_label = candidate_name

            if candidate_email:
                option_label = (
                    f"{candidate_name} — {candidate_email}"
                )

            candidate_options[option_label] = candidate_id

        selected_candidate_label = st.selectbox(
            "Select a candidate",
            list(candidate_options.keys()),
        )

        selected_candidate_id = candidate_options[
            selected_candidate_label
        ]

        candidate_matches = raw_candidates[
            raw_candidates["id"].astype(str)
            == selected_candidate_id
        ]

        if candidate_matches.empty:
            st.error("The selected candidate could not be found.")

        else:
            selected_raw_candidate = candidate_matches.iloc[0]

            # ---------------------------------------------
            # Find candidate application
            # ---------------------------------------------
            selected_application = pd.Series(
                dtype="object"
            )

            if (
                not raw_applications.empty
                and "candidate_id"
                in raw_applications.columns
            ):
                application_matches = raw_applications[
                    raw_applications[
                        "candidate_id"
                    ].astype(str)
                    == selected_candidate_id
                ].copy()

                if not application_matches.empty:
                    if (
                        "applied_at"
                        in application_matches.columns
                    ):
                        application_matches[
                            "applied_at"
                        ] = pd.to_datetime(
                            application_matches[
                                "applied_at"
                            ],
                            errors="coerce",
                        )

                        application_matches = (
                            application_matches.sort_values(
                                "applied_at",
                                ascending=False,
                            )
                        )

                    selected_application = (
                        application_matches.iloc[0]
                    )

            # ---------------------------------------------
            # Find related job
            # ---------------------------------------------
            selected_job = pd.Series(dtype="object")

            selected_job_id = safe_value(
                selected_application,
                "job_id",
                "",
            )

            if (
                selected_job_id
                and not raw_jobs.empty
                and "id" in raw_jobs.columns
            ):
                job_matches = raw_jobs[
                    raw_jobs["id"].astype(str)
                    == selected_job_id
                ]

                if not job_matches.empty:
                    selected_job = job_matches.iloc[0]

            # ---------------------------------------------
            # Main profile values
            # ---------------------------------------------
            candidate_name = safe_value(
                selected_raw_candidate,
                "full_name",
                "Unknown candidate",
            )

            role = safe_value(
                selected_job,
                "title",
                "Not assigned",
            )

            experience = safe_value(
                selected_raw_candidate,
                "years_experience",
            )

            if experience != "Not available":
                experience_text = experience.lower()

                if not experience_text.endswith(
                    (
                        "year",
                        "years",
                        "month",
                        "months",
                    )
                ):
                    experience = f"{experience} years"

            selected_application_id = safe_value(
                selected_application,
                "id",
                "",
            )

            if selected_application.empty:
                application_stage = safe_value(
                    selected_raw_candidate,
                    "status",
                    "Pending Review",
                )
            else:
                application_stage = safe_value(
                    selected_application,
                    "application_stage",
                    "Pending Review",
                )

            action_message = st.session_state.get(
                "candidate_action_success"
            )

            if (
                action_message
                and action_message.get("application_id")
                == selected_application_id
            ):
                application_stage = action_message.get(
                    "stage",
                    application_stage,
                )

            candidate_score = pd.to_numeric(
                selected_application.get(
                    "candidate_score",
                    0,
                ),
                errors="coerce",
            )

            ats_score = pd.to_numeric(
                selected_application.get(
                    "ats_score",
                    0,
                ),
                errors="coerce",
            )

            if pd.isna(candidate_score):
                candidate_score = 0

            if pd.isna(ats_score):
                ats_score = 0

            applied_on = safe_value(
                selected_application,
                "applied_at",
            )

            if applied_on != "Not available":
                parsed_applied_on = pd.to_datetime(
                    applied_on,
                    errors="coerce",
                )

                if not pd.isna(parsed_applied_on):
                    applied_on = (
                        parsed_applied_on.strftime(
                            "%d %b %Y, %I:%M %p"
                        )
                    )

            # ---------------------------------------------
            # Candidate profile header
            # ---------------------------------------------
            status_class = get_status_class(
                application_stage
            )

            safe_candidate_name = html.escape(
                candidate_name
            )

            safe_role = html.escape(
                role
            )

            safe_experience = html.escape(
                experience
            )

            safe_application_stage = html.escape(
                application_stage
            )

            safe_applied_on = html.escape(
                applied_on
            )

            profile_header_html = (
                f'<div class="candidate-profile-card">'
                f'  <div class="candidate-profile-header">'
                f'    <div>'
                f'      <div class="candidate-identity">'
                f'        <div class="candidate-avatar">👤</div>'
                f'        <div>'
                f'          <div class="candidate-name">'
                f'            {safe_candidate_name}'
                f'          </div>'
                f'          <div class="candidate-role">'
                f'            {safe_role}'
                f'          </div>'
                f'        </div>'
                f'      </div>'
                f'      <div class="candidate-meta">'
                f'        <span class="candidate-meta-item">'
                f'          💼 {safe_experience}'
                f'        </span>'
                f'        <span class="candidate-meta-item">'
                f'          📅 Applied {safe_applied_on}'
                f'        </span>'
                f'        <span class="status-badge {status_class}">'
                f'          {safe_application_stage}'
                f'        </span>'
                f'      </div>'
                f'    </div>'
                f'    <div class="score-panel">'
                f'      <div class="score-box">'
                f'        <div class="score-number">'
                f'          {float(candidate_score):.0f}%'
                f'        </div>'
                f'        <div class="score-label">'
                f'          Candidate Score'
                f'        </div>'
                f'      </div>'
                f'      <div class="score-box">'
                f'        <div class="score-number">'
                f'          {float(ats_score):.0f}%'
                f'        </div>'
                f'        <div class="score-label">'
                f'          ATS Score'
                f'        </div>'
                f'      </div>'
                f'    </div>'
                f'  </div>'
                f'</div>'
            )

            st.markdown(
                profile_header_html,
                unsafe_allow_html=True,
            )

            # ---------------------------------------------
            # Candidate actions
            # ---------------------------------------------
            action_message = st.session_state.pop(
                "candidate_action_success",
                None,
            )

            if (
                action_message
                and action_message.get("application_id")
                == selected_application_id
            ):
                st.success(action_message["message"])

            st.markdown("### Candidate actions")

            if not selected_application_id:
                st.info(
                    "Candidate actions require an application record."
                )
            else:
                def set_application_stage(
                    new_stage: str,
                ) -> None:
                    try:
                        update_application_stage(
                            selected_application_id,
                            new_stage,
                        )
                    except Exception as error:
                        st.error(
                            "Could not update the application stage: "
                            f"{error}"
                        )
                        return

                    get_applications.clear()
                    st.session_state[
                        "candidate_action_success"
                    ] = {
                        "application_id": (
                            selected_application_id
                        ),
                        "message": (
                            "Application stage updated to "
                            f"{new_stage}."
                        ),
                        "stage": new_stage,
                    }
                    st.rerun()

                action_col1, action_col2, action_col3, action_col4 = (
                    st.columns(4)
                )

                with action_col1:
                    if st.button(
                        "Shortlist Candidate",
                        key=(
                            "shortlist_candidate_"
                            f"{selected_application_id}"
                        ),
                        width="stretch",
                    ):
                        set_application_stage("Shortlisted")

                with action_col2:
                    if st.button(
                        "Move to Interview",
                        key=(
                            "interview_candidate_"
                            f"{selected_application_id}"
                        ),
                        width="stretch",
                    ):
                        set_application_stage("Interview")

                with action_col3:
                    if st.button(
                        "Select Candidate",
                        key=(
                            "select_candidate_"
                            f"{selected_application_id}"
                        ),
                        width="stretch",
                    ):
                        set_application_stage("Selected")

                with action_col4:
                    with st.popover(
                        "Reject Candidate",
                        width="stretch",
                    ):
                        st.warning(
                            "Reject this candidate's selected "
                            "application?"
                        )

                        if st.button(
                            "Confirm rejection",
                            key=(
                                "confirm_reject_candidate_"
                                f"{selected_application_id}"
                            ),
                            type="primary",
                            width="stretch",
                        ):
                            set_application_stage("Rejected")

            # ---------------------------------------------
            # Interview scheduler
            # ---------------------------------------------
            st.markdown("### Interview Scheduler")

            interview_message = st.session_state.pop(
                "interview_scheduler_success",
                None,
            )

            if (
                interview_message
                and interview_message.get("application_id")
                == selected_application_id
            ):
                st.success(interview_message["message"])

            if not selected_application_id:
                st.info(
                    "An application record is required to schedule "
                    "an interview."
                )
            else:
                default_interview_datetime = (
                    datetime.now() + timedelta(minutes=30)
                ).replace(
                    second=0,
                    microsecond=0,
                )

                with st.container(border=True):
                    st.markdown("#### Schedule interview")

                    with st.form(
                        (
                            "interview_scheduler_"
                            f"{selected_application_id}"
                        ),
                        clear_on_submit=True,
                    ):
                        schedule_col1, schedule_col2 = st.columns(2)

                        with schedule_col1:
                            interview_date_value = st.date_input(
                                "Interview date",
                                value=(
                                    default_interview_datetime.date()
                                ),
                                min_value=date.today(),
                            )
                            interview_type = st.selectbox(
                                "Interview type",
                                [
                                    "Technical",
                                    "HR",
                                    "Managerial",
                                    "Final",
                                ],
                            )
                            interviewer = st.text_input(
                                "Interviewer name"
                            )

                        with schedule_col2:
                            interview_time_value = st.time_input(
                                "Interview time",
                                value=(
                                    default_interview_datetime.time()
                                ),
                            )
                            meeting_location = st.text_input(
                                "Meeting location or meeting link"
                            )
                            interview_notes = st.text_area(
                                "Interview notes"
                            )

                        schedule_submitted = st.form_submit_button(
                            "Save interview",
                            type="primary",
                            width="stretch",
                        )

                    if schedule_submitted:
                        scheduled_for = datetime.combine(
                            interview_date_value,
                            interview_time_value,
                        )
                        validation_errors = []

                        if scheduled_for < datetime.now():
                            validation_errors.append(
                                "Interview date and time cannot be "
                                "in the past."
                            )

                        if not interviewer.strip():
                            validation_errors.append(
                                "Interviewer name is required."
                            )

                        if not meeting_location.strip():
                            validation_errors.append(
                                "Meeting location or link is required."
                            )

                        if validation_errors:
                            for validation_error in validation_errors:
                                st.error(validation_error)
                        else:
                            interview_datetime = scheduled_for.isoformat(
                                timespec="minutes"
                            )

                            try:
                                create_interview(
                                    selected_application_id,
                                    interview_datetime,
                                    interviewer.strip(),
                                    {
                                        "interview_type": interview_type,
                                        "location": (
                                            meeting_location.strip()
                                        ),
                                        "notes": interview_notes.strip(),
                                    },
                                )
                            except Exception as error:
                                st.error(
                                    "Could not schedule the interview: "
                                    f"{error}"
                                )
                            else:
                                get_interviews.clear()
                                st.session_state[
                                    "interview_scheduler_success"
                                ] = {
                                    "application_id": (
                                        selected_application_id
                                    ),
                                    "message": (
                                        "Interview scheduled "
                                        "successfully."
                                    ),
                                }
                                st.rerun()

                st.markdown("#### Scheduled interviews")
                scheduled_interviews = get_interviews()

                if (
                    scheduled_interviews.empty
                    or "application_id"
                    not in scheduled_interviews.columns
                ):
                    candidate_interviews = pd.DataFrame()
                else:
                    candidate_interviews = scheduled_interviews[
                        scheduled_interviews[
                            "application_id"
                        ].astype(str)
                        == selected_application_id
                    ].copy()

                if candidate_interviews.empty:
                    st.info(
                        "No interviews are scheduled for this candidate."
                    )
                else:
                    if "interview_date" in candidate_interviews.columns:
                        candidate_interviews["_scheduled_for"] = (
                            pd.to_datetime(
                                candidate_interviews[
                                    "interview_date"
                                ],
                                errors="coerce",
                            )
                        )
                        candidate_interviews = (
                            candidate_interviews.sort_values(
                                "_scheduled_for",
                                ascending=True,
                                na_position="last",
                            )
                        )

                    for _, interview_row in (
                        candidate_interviews.iterrows()
                    ):
                        feedback_data = parse_stored_value(
                            interview_row.get("feedback")
                        )

                        if isinstance(feedback_data, dict):
                            scheduled_type = feedback_data.get(
                                "interview_type",
                                "Not available",
                            )
                            scheduled_location = feedback_data.get(
                                "location",
                                "Not available",
                            )
                            scheduled_notes = feedback_data.get(
                                "notes",
                                "Not available",
                            )
                        else:
                            scheduled_type = "Not available"
                            scheduled_location = "Not available"
                            scheduled_notes = (
                                feedback_data
                                if feedback_data
                                else "Not available"
                            )

                        scheduled_at = pd.to_datetime(
                            interview_row.get("interview_date"),
                            errors="coerce",
                        )

                        if pd.isna(scheduled_at):
                            scheduled_date = safe_value(
                                interview_row,
                                "interview_date",
                            )
                            scheduled_time = "Not available"
                        else:
                            scheduled_date = scheduled_at.strftime(
                                "%d %b %Y"
                            )
                            scheduled_time = scheduled_at.strftime(
                                "%I:%M %p"
                            )

                        with st.container(border=True):
                            st.write(
                                "**Interview type:**",
                                scheduled_type,
                            )
                            st.write(
                                "**Date:**",
                                scheduled_date,
                            )
                            st.write(
                                "**Time:**",
                                scheduled_time,
                            )
                            st.write(
                                "**Interviewer:**",
                                safe_value(
                                    interview_row,
                                    "interviewer",
                                ),
                            )
                            st.write(
                                "**Location or meeting link:**",
                                scheduled_location,
                            )
                            st.write(
                                "**Notes:**",
                                scheduled_notes or "Not available",
                            )
                            st.write(
                                "**Status:**",
                                safe_value(
                                    interview_row,
                                    "status",
                                ),
                            )

            # ---------------------------------------------
            # Recruiter notes
            # ---------------------------------------------
            st.markdown("### Recruiter Notes")

            recruiter_note_message = st.session_state.pop(
                "recruiter_note_success",
                None,
            )

            if (
                recruiter_note_message
                and recruiter_note_message.get("application_id")
                == selected_application_id
            ):
                st.success(recruiter_note_message["message"])

            if not selected_application_id:
                st.info(
                    "An application record is required to add "
                    "recruiter notes."
                )
            else:
                with st.container(border=True):
                    st.markdown("#### Add note")

                    with st.form(
                        f"recruiter_note_{selected_application_id}",
                        clear_on_submit=True,
                    ):
                        recruiter_name = st.text_input(
                            "Recruiter name"
                        )
                        recruiter_note = st.text_area("Note")
                        recruiter_note_submitted = (
                            st.form_submit_button(
                                "Save note",
                                type="primary",
                            )
                        )

                    if recruiter_note_submitted:
                        if not recruiter_note.strip():
                            st.error("Note text is required.")
                        elif not recruiter_name.strip():
                            st.error("Recruiter name is required.")
                        else:
                            try:
                                create_recruiter_note(
                                    selected_application_id,
                                    recruiter_note,
                                    recruiter_name,
                                )
                            except Exception as error:
                                st.error(
                                    "Could not save the recruiter note: "
                                    f"{error}"
                                )
                            else:
                                get_recruiter_notes.clear()
                                st.session_state[
                                    "recruiter_note_success"
                                ] = {
                                    "application_id": (
                                        selected_application_id
                                    ),
                                    "message": (
                                        "Recruiter note saved "
                                        "successfully."
                                    ),
                                }
                                st.rerun()

                st.markdown("#### Previous notes")
                recruiter_notes = get_recruiter_notes()

                if (
                    recruiter_notes.empty
                    or "application_id"
                    not in recruiter_notes.columns
                ):
                    selected_recruiter_notes = pd.DataFrame()
                else:
                    selected_recruiter_notes = recruiter_notes[
                        recruiter_notes[
                            "application_id"
                        ].astype(str)
                        == selected_application_id
                    ].copy()

                if selected_recruiter_notes.empty:
                    st.info("No recruiter notes are available.")
                else:
                    if "created_at" in selected_recruiter_notes.columns:
                        selected_recruiter_notes["_created_at"] = (
                            pd.to_datetime(
                                selected_recruiter_notes[
                                    "created_at"
                                ],
                                errors="coerce",
                                utc=True,
                            )
                        )
                        selected_recruiter_notes = (
                            selected_recruiter_notes.sort_values(
                                "_created_at",
                                ascending=False,
                                na_position="last",
                            )
                        )

                    for _, note_row in (
                        selected_recruiter_notes.iterrows()
                    ):
                        note_created_at = note_row.get("_created_at")
                        displayed_created_at = (
                            "Not available"
                            if note_created_at is None
                            or pd.isna(note_created_at)
                            else note_created_at.strftime(
                                "%d %b %Y, %I:%M %p UTC"
                            )
                        )

                        with st.container(border=True):
                            st.write(
                                safe_value(note_row, "note")
                            )
                            st.caption(
                                "Created: "
                                f"{displayed_created_at} · "
                                "Recruiter: "
                                f"{safe_value(note_row, 'recruiter_name')}"
                            )

            # ---------------------------------------------
            # Candidate communication drafts
            # ---------------------------------------------
            st.markdown("### Candidate Communication Actions")

            candidate_email = safe_value(
                selected_raw_candidate,
                "email",
                "",
            )
            candidate_phone = safe_value(
                selected_raw_candidate,
                "phone",
                "",
            )
            communication_interview = pd.Series(dtype="object")

            if (
                selected_application_id
                and not candidate_interviews.empty
            ):
                communication_interviews = candidate_interviews.copy()

                if "status" in communication_interviews.columns:
                    scheduled_mask = (
                        communication_interviews["status"]
                        .fillna("")
                        .astype(str)
                        .str.strip()
                        .str.casefold()
                        .eq("scheduled")
                    )
                    scheduled_rows = communication_interviews[
                        scheduled_mask
                    ]

                    if not scheduled_rows.empty:
                        communication_interviews = scheduled_rows

                if "interview_date" in communication_interviews.columns:
                    communication_interviews["_communication_date"] = (
                        pd.to_datetime(
                            communication_interviews[
                                "interview_date"
                            ],
                            errors="coerce",
                            utc=True,
                        )
                    )
                    future_interviews = communication_interviews[
                        communication_interviews[
                            "_communication_date"
                        ]
                        >= pd.Timestamp.now(tz="UTC")
                    ].sort_values("_communication_date")

                    if not future_interviews.empty:
                        communication_interviews = future_interviews

                if not communication_interviews.empty:
                    communication_interview = (
                        communication_interviews.iloc[0]
                    )

            communication_date = None
            communication_time = None
            communication_interviewer = None
            communication_location = None

            if not communication_interview.empty:
                communication_datetime = pd.to_datetime(
                    communication_interview.get("interview_date"),
                    errors="coerce",
                    utc=True,
                )

                if not pd.isna(communication_datetime):
                    communication_date = (
                        communication_datetime.strftime("%d %b %Y")
                    )
                    communication_time = (
                        communication_datetime.strftime("%I:%M %p UTC")
                    )

                communication_interviewer = safe_value(
                    communication_interview,
                    "interviewer",
                    "",
                )
                communication_metadata = parse_stored_value(
                    communication_interview.get("feedback")
                )

                if isinstance(communication_metadata, dict):
                    communication_location = (
                        communication_metadata.get("meeting_link")
                        or communication_metadata.get(
                            "meeting_location"
                        )
                        or communication_metadata.get("location")
                    )

            with st.container(border=True):
                selected_message_type = st.selectbox(
                    "Message type",
                    MESSAGE_TYPES,
                    key=(
                        "candidate_message_type_"
                        f"{selected_candidate_id}"
                    ),
                )
                message_drafts = build_candidate_messages(
                    selected_message_type,
                    candidate_name,
                    role,
                    application_stage,
                    communication_date,
                    communication_time,
                    communication_interviewer,
                    communication_location,
                )
                email_draft_col, whatsapp_draft_col = st.columns(2)

                with email_draft_col:
                    st.markdown("#### Email preview")
                    st.caption(
                        f"Recipient: {candidate_email or 'Not available'}"
                    )
                    email_subject = st.text_input(
                        "Email subject",
                        value=message_drafts["email_subject"],
                        key=(
                            "email_subject_"
                            f"{selected_candidate_id}_"
                            f"{selected_message_type}"
                        ),
                    )
                    email_body = st.text_area(
                        "Email message",
                        value=message_drafts["email_body"],
                        height=280,
                        key=(
                            "email_body_"
                            f"{selected_candidate_id}_"
                            f"{selected_message_type}"
                        ),
                    )

                    with st.container(border=True):
                        st.write("**Subject:**", email_subject)
                        st.text(email_body)

                    if st.button(
                        "Email Candidate",
                        key=(
                            "email_candidate_"
                            f"{selected_candidate_id}"
                        ),
                    ):
                        if not candidate_email:
                            st.error(
                                "Candidate email is not available."
                            )
                        else:
                            st.info(
                                "Email draft is ready. No email was sent."
                            )

                with whatsapp_draft_col:
                    st.markdown("#### WhatsApp preview")
                    st.caption(
                        f"Recipient: {candidate_phone or 'Not available'}"
                    )
                    whatsapp_body = st.text_area(
                        "WhatsApp message",
                        value=message_drafts["whatsapp_body"],
                        height=280,
                        key=(
                            "whatsapp_body_"
                            f"{selected_candidate_id}_"
                            f"{selected_message_type}"
                        ),
                    )

                    with st.container(border=True):
                        st.text(whatsapp_body)

                    if st.button(
                        "WhatsApp Candidate",
                        key=(
                            "whatsapp_candidate_"
                            f"{selected_candidate_id}"
                        ),
                    ):
                        if not candidate_phone:
                            st.error(
                                "Candidate phone number is not available."
                            )
                        else:
                            st.info(
                                "WhatsApp draft is ready. No message "
                                "was sent."
                            )

            # ---------------------------------------------
            # Contact and career information
            # ---------------------------------------------
            contact_col, career_col = st.columns(2)

            with contact_col:
                st.markdown(
                    "### Contact Information"
                )

                st.write(
                    f"**Email:** "
                    f"{safe_value(selected_raw_candidate, 'email')}"
                )

                st.write(
                    f"**Phone:** "
                    f"{safe_value(selected_raw_candidate, 'phone')}"
                )

                st.write(
                    f"**Location:** "
                    f"{safe_value(selected_raw_candidate, 'location')}"
                )

                linkedin_url = safe_value(
                    selected_raw_candidate,
                    "linkedin_url",
                    "",
                )

                github_url = safe_value(
                    selected_raw_candidate,
                    "github_url",
                    "",
                )

                portfolio_url = safe_value(
                    selected_raw_candidate,
                    "portfolio_url",
                    "",
                )

                resume_url = safe_value(
                    selected_raw_candidate,
                    "resume_url",
                    "",
                )

                if not resume_url:
                    resume_url = safe_value(
                        selected_raw_candidate,
                        "resume_drive_link",
                        "",
                    )

                button_col1, button_col2 = st.columns(2)

                with button_col1:
                    if resume_url:
                        st.link_button(
                            "View Resume",
                            resume_url,
                            width="stretch",
                        )

                    if linkedin_url:
                        st.link_button(
                            "LinkedIn",
                            linkedin_url,
                            width="stretch",
                        )

                with button_col2:
                    if github_url:
                        st.link_button(
                            "GitHub",
                            github_url,
                            width="stretch",
                        )

                    if portfolio_url:
                        st.link_button(
                            "Portfolio",
                            portfolio_url,
                            width="stretch",
                        )

            with career_col:
                st.markdown(
                    "### Career Information"
                )

                st.write(
                    f"**Current Company:** "
                    f"{safe_value(selected_raw_candidate, 'current_company')}"
                )

                st.write(
                    f"**Current CTC:** "
                    f"{safe_value(selected_raw_candidate, 'current_ctc')}"
                )

                st.write(
                    f"**Expected CTC:** "
                    f"{safe_value(selected_raw_candidate, 'expected_ctc')}"
                )

                st.write(
                    f"**Notice Period:** "
                    f"{safe_value(selected_raw_candidate, 'notice_period')}"
                )

            st.divider()

                        # ---------------------------------------------
            # Resume data
            # ---------------------------------------------
            skills_col, education_col = st.columns(2)

            with skills_col:
                st.markdown("### Skills")

                show_skill_chips(
                    selected_raw_candidate.get(
                        "skills",
                        None,
                    )
                )

                st.markdown("### Previous Companies")

                st.write(
                    safe_value(
                        selected_raw_candidate,
                        "previous_companies",
                    )
                )

            with education_col:
                st.markdown("### Education")

                st.write(
                    safe_value(
                        selected_raw_candidate,
                        "education",
                    )
                )

                st.markdown("### AI Resume Summary")

                st.write(
                    safe_value(
                        selected_raw_candidate,
                        "summary",
                    )
                )

            st.divider()

            # ---------------------------------------------
            # AI evaluation
            # ---------------------------------------------
            st.markdown(
                "### AI Candidate Evaluation"
            )

            evaluation_col, question_col = st.columns(2)

            with evaluation_col:
                stored_recommendation = parse_stored_value(
                    selected_application.get(
                        "recommendation",
                        None,
                    )
                )

                if isinstance(stored_recommendation, dict):
                    evaluation_data = stored_recommendation
                    recommendation = evaluation_value(
                        evaluation_data,
                        ("recommendation", "decision"),
                    )
                else:
                    evaluation_data = {}
                    recommendation = stored_recommendation

                confidence_score = evaluation_value(
                    evaluation_data,
                    ("confidence_score", "confidence"),
                )
                main_reasons = evaluation_value(
                    evaluation_data,
                    ("main_reasons", "reasons"),
                )
                strengths = evaluation_value(
                    evaluation_data,
                    ("strengths",),
                )
                concerns = evaluation_value(
                    evaluation_data,
                    ("concerns",),
                )
                next_action = evaluation_value(
                    evaluation_data,
                    (
                        "recommended_next_action",
                        "next_action",
                    ),
                )

                with st.container(border=True):
                    st.markdown(
                        "#### AI hiring recommendation"
                    )

                    recommendation_text = (
                        str(recommendation).strip()
                        if recommendation is not None
                        else ""
                    )

                    if not recommendation_text:
                        st.info("Recommendation not available")
                    elif recommendation_text.lower() in [
                        "reject",
                        "rejected",
                    ]:
                        st.error(recommendation_text)
                    elif recommendation_text.lower() in [
                        "shortlist",
                        "shortlisted",
                        "recommend",
                        "recommended",
                    ]:
                        st.success(recommendation_text)
                    else:
                        st.info(recommendation_text)

                    show_evaluation_detail(
                        "Confidence score",
                        confidence_score,
                    )
                    show_evaluation_detail(
                        "Main reasons",
                        main_reasons,
                    )
                    show_evaluation_detail(
                        "Strengths",
                        strengths,
                    )
                    show_evaluation_detail(
                        "Concerns",
                        concerns,
                    )
                    show_evaluation_detail(
                        "Recommended next action",
                        next_action,
                    )

            with question_col:
                st.markdown(
                    "#### Interview Questions"
                )

                show_interview_questions(
                    selected_application.get(
                        "interview_questions",
                        None,
                    )
                )


# =========================================================
# Applications page
# =========================================================
elif selected_page == "Applications":
    st.markdown(
        '<div class="main-title">'
        "Applications"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "View live application records from Supabase."
        "</div>",
        unsafe_allow_html=True,
    )

    if raw_applications.empty:
        st.info("No applications found.")
    else:
        displayed_applications = raw_applications.copy()

        for column in displayed_applications.columns:
            has_complex_values = displayed_applications[column].apply(
                lambda value: isinstance(value, (dict, list))
            ).any()

            if has_complex_values:
                displayed_applications[column] = (
                    displayed_applications[column].apply(
                        lambda value: json.dumps(value)
                        if isinstance(value, (dict, list))
                        else value
                    )
                )

        st.dataframe(
            displayed_applications,
            width="stretch",
            hide_index=True,
            column_config={
                "candidate_score": st.column_config.ProgressColumn(
                    "Candidate Score",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                ),
                "ats_score": st.column_config.ProgressColumn(
                    "ATS Score",
                    min_value=0,
                    max_value=100,
                    format="%d%%",
                ),
            },
        )


# =========================================================
# Jobs page
# =========================================================
elif selected_page == "Jobs":
    st.markdown(
        '<div class="main-title">'
        "Jobs"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "View open and closed jobs from Supabase."
        "</div>",
        unsafe_allow_html=True,
    )

    if raw_jobs.empty:
        st.info("No jobs found.")
    else:
        st.dataframe(
            raw_jobs,
            width="stretch",
            hide_index=True,
        )


# =========================================================
# Interviews page
# =========================================================
elif selected_page == "Interviews":
    st.markdown(
        '<div class="main-title">'
        "Interview Management"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "Review scheduled interviews, update outcomes and record feedback."
        "</div>",
        unsafe_allow_html=True,
    )

    interview_action_message = st.session_state.pop(
        "interview_management_success",
        None,
    )

    if interview_action_message:
        st.success(interview_action_message)

    all_interviews = get_interviews()

    if all_interviews.empty:
        st.info("No interviews are available.")
    else:
        def safe_identifier(value) -> str:
            """Return a safe identifier string for local joins."""

            if value is None or isinstance(
                value,
                (dict, list, tuple, set),
            ):
                return ""

            try:
                if pd.isna(value):
                    return ""
            except (TypeError, ValueError):
                return ""

            return str(value).strip()

        applications_by_id = {}

        if (
            not raw_applications.empty
            and "id" in raw_applications.columns
        ):
            for _, application_row in raw_applications.iterrows():
                application_id = safe_identifier(
                    application_row.get("id")
                )

                if application_id:
                    applications_by_id[application_id] = {
                        "candidate_id": safe_identifier(
                            application_row.get("candidate_id")
                        ),
                        "job_id": safe_identifier(
                            application_row.get("job_id")
                        ),
                    }

        candidate_names_by_id = {}

        if (
            not raw_candidates.empty
            and "id" in raw_candidates.columns
        ):
            for _, candidate_row in raw_candidates.iterrows():
                candidate_id = safe_identifier(
                    candidate_row.get("id")
                )
                candidate_name = candidate_row.get("full_name")

                if candidate_id:
                    candidate_names_by_id[candidate_id] = (
                        str(candidate_name).strip()
                        if candidate_name is not None
                        and str(candidate_name).strip()
                        else "Unknown Candidate"
                    )

        job_titles_by_id = {}

        if (
            not raw_jobs.empty
            and "id" in raw_jobs.columns
        ):
            for _, job_row in raw_jobs.iterrows():
                job_id = safe_identifier(job_row.get("id"))
                job_title = job_row.get("title")

                if job_id:
                    job_titles_by_id[job_id] = (
                        str(job_title).strip()
                        if job_title is not None
                        and str(job_title).strip()
                        else "Unknown Job"
                    )

        managed_interviews = all_interviews.copy()
        managed_interviews["_interview_id"] = (
            managed_interviews.get(
                "id",
                pd.Series("", index=managed_interviews.index),
            ).apply(safe_identifier)
        )
        managed_interviews["_application_id"] = (
            managed_interviews.get(
                "application_id",
                pd.Series("", index=managed_interviews.index),
            ).apply(safe_identifier)
        )

        def related_value(
            application_id: str,
            relationship: str,
        ) -> str:
            """Resolve a candidate or job through an application."""

            application = applications_by_id.get(
                application_id,
                {},
            )

            if relationship == "candidate":
                return candidate_names_by_id.get(
                    application.get("candidate_id", ""),
                    "Unknown Candidate",
                )

            return job_titles_by_id.get(
                application.get("job_id", ""),
                "Unknown Job",
            )

        managed_interviews["Candidate"] = managed_interviews[
            "_application_id"
        ].apply(lambda value: related_value(value, "candidate"))
        managed_interviews["Job"] = managed_interviews[
            "_application_id"
        ].apply(lambda value: related_value(value, "job"))
        managed_interviews["Interviewer"] = managed_interviews.get(
            "interviewer",
            pd.Series("", index=managed_interviews.index),
        ).fillna("").astype(str).str.strip()
        managed_interviews["Status"] = managed_interviews.get(
            "status",
            pd.Series("", index=managed_interviews.index),
        ).fillna("").astype(str).str.strip()
        managed_interviews["_scheduled_for"] = pd.to_datetime(
            managed_interviews.get(
                "interview_date",
                pd.Series(None, index=managed_interviews.index),
            ),
            errors="coerce",
            utc=True,
        )
        managed_interviews["_interview_day"] = managed_interviews[
            "_scheduled_for"
        ].dt.date

        status_options = sorted(
            value
            for value in managed_interviews["Status"].unique()
            if value
        )
        interviewer_options = sorted(
            value
            for value in managed_interviews["Interviewer"].unique()
            if value
        )
        job_options = sorted(managed_interviews["Job"].unique())
        date_options = sorted(
            value
            for value in managed_interviews[
                "_interview_day"
            ].dropna().unique()
        )

        filter_col1, filter_col2, filter_col3, filter_col4 = (
            st.columns(4)
        )

        with filter_col1:
            selected_interview_status = st.selectbox(
                "Interview status",
                ["All"] + status_options,
            )

        with filter_col2:
            selected_interviewer = st.selectbox(
                "Interviewer",
                ["All"] + interviewer_options,
            )

        with filter_col3:
            selected_interview_date = st.selectbox(
                "Interview date",
                [None] + date_options,
                format_func=lambda value: (
                    "All dates"
                    if value is None
                    else value.strftime("%d %b %Y")
                ),
            )

        with filter_col4:
            selected_interview_job = st.selectbox(
                "Job",
                ["All"] + job_options,
            )

        filtered_interviews = managed_interviews.copy()

        if selected_interview_status != "All":
            filtered_interviews = filtered_interviews[
                filtered_interviews["Status"]
                == selected_interview_status
            ]

        if selected_interviewer != "All":
            filtered_interviews = filtered_interviews[
                filtered_interviews["Interviewer"]
                == selected_interviewer
            ]

        if selected_interview_date is not None:
            filtered_interviews = filtered_interviews[
                filtered_interviews["_interview_day"]
                == selected_interview_date
            ]

        if selected_interview_job != "All":
            filtered_interviews = filtered_interviews[
                filtered_interviews["Job"]
                == selected_interview_job
            ]

        if filtered_interviews.empty:
            st.info("No interviews match the selected filters.")
        else:
            filtered_interviews = filtered_interviews.sort_values(
                "_scheduled_for",
                ascending=True,
                na_position="last",
            )

            def save_interview_update(
                interview_id: str,
                updates: dict,
                success_message: str,
            ) -> None:
                """Persist one interview update and refresh the page."""

                try:
                    update_interview(interview_id, updates)
                except Exception as error:
                    st.error(
                        "Could not update the interview: "
                        f"{error}"
                    )
                    return

                get_interviews.clear()
                st.session_state[
                    "interview_management_success"
                ] = success_message
                st.rerun()

            for _, interview_row in filtered_interviews.iterrows():
                interview_id = interview_row["_interview_id"]
                scheduled_for = interview_row["_scheduled_for"]
                stored_feedback = parse_stored_value(
                    interview_row.get("feedback")
                )

                if isinstance(stored_feedback, dict):
                    feedback_text = stored_feedback.get(
                        "feedback",
                        "",
                    )
                    interview_type = stored_feedback.get(
                        "interview_type",
                    )
                    meeting_location = stored_feedback.get(
                        "meeting_link",
                        stored_feedback.get(
                            "meeting_location",
                            stored_feedback.get("location"),
                        ),
                    )
                    interview_notes = stored_feedback.get(
                        "notes",
                    )
                elif stored_feedback is None:
                    feedback_text = ""
                    interview_type = None
                    meeting_location = None
                    interview_notes = None
                else:
                    feedback_text = str(stored_feedback)
                    interview_type = None
                    meeting_location = None
                    interview_notes = None

                rating_value = pd.to_numeric(
                    interview_row.get("rating"),
                    errors="coerce",
                )
                displayed_rating = (
                    "Not rated"
                    if pd.isna(rating_value)
                    else f"{int(rating_value)}/5"
                )
                if pd.isna(scheduled_for):
                    displayed_date = "Not available"
                    displayed_time = "Not available"
                else:
                    displayed_date = scheduled_for.strftime(
                        "%d %b %Y"
                    )
                    displayed_time = scheduled_for.strftime(
                        "%I:%M %p UTC"
                    )

                with st.container(border=True):
                    st.markdown(
                        f"#### {interview_row['Candidate']} — "
                        f"{interview_row['Job']}"
                    )
                    details_col1, details_col2 = st.columns(2)

                    with details_col1:
                        st.write(
                            "**Interviewer:**",
                            interview_row["Interviewer"]
                            or "Not available",
                        )
                        st.write(
                            "**Interview type:**",
                            interview_type or "Not available",
                        )
                        st.write(
                            "**Interview date:**",
                            displayed_date,
                        )
                        st.write(
                            "**Interview time:**",
                            displayed_time,
                        )
                        st.write(
                            "**Status:**",
                            interview_row["Status"]
                            or "Not available",
                        )

                    with details_col2:
                        st.write(
                            "**Meeting link or location:**",
                            meeting_location or "Not available",
                        )
                        st.write(
                            "**Notes:**",
                            interview_notes or "Not available",
                        )
                        st.write(
                            "**Feedback:**",
                            feedback_text or "Not available",
                        )
                        st.write("**Rating:**", displayed_rating)

                    with st.container(horizontal=True):
                        if st.button(
                            "Mark Scheduled",
                            key=f"scheduled_{interview_id}",
                        ):
                            save_interview_update(
                                interview_id,
                                {"status": "Scheduled"},
                                "Interview marked as Scheduled.",
                            )

                        if st.button(
                            "Mark Completed",
                            key=f"completed_{interview_id}",
                        ):
                            save_interview_update(
                                interview_id,
                                {"status": "Completed"},
                                "Interview marked as Completed.",
                            )

                        if st.button(
                            "Mark Cancelled",
                            key=f"cancelled_{interview_id}",
                        ):
                            save_interview_update(
                                interview_id,
                                {"status": "Cancelled"},
                                "Interview marked as Cancelled.",
                            )

                    with st.form(f"feedback_{interview_id}"):
                        edited_feedback = st.text_area(
                            "Feedback",
                            value=str(feedback_text or ""),
                            key=f"feedback_text_{interview_id}",
                        )
                        initial_rating = (
                            int(rating_value)
                            if not pd.isna(rating_value)
                            and 1 <= int(rating_value) <= 5
                            else 1
                        )
                        edited_rating = st.number_input(
                            "Rating",
                            min_value=1,
                            max_value=5,
                            value=initial_rating,
                            step=1,
                            key=f"rating_{interview_id}",
                        )
                        feedback_submitted = st.form_submit_button(
                            "Save feedback and rating"
                        )

                    if feedback_submitted:
                        validated_rating = int(edited_rating)

                        if validated_rating < 1 or validated_rating > 5:
                            st.error("Rating must be between 1 and 5.")
                        else:
                            if isinstance(stored_feedback, dict):
                                updated_feedback = dict(stored_feedback)
                                updated_feedback["feedback"] = (
                                    edited_feedback.strip()
                                )
                            else:
                                updated_feedback = edited_feedback.strip()

                            save_interview_update(
                                interview_id,
                                {
                                    "feedback": updated_feedback,
                                    "rating": validated_rating,
                                },
                                "Interview feedback and rating saved.",
                            )


# =========================================================
# Analytics page
# =========================================================
elif selected_page == "Analytics":
    st.markdown(
        '<div class="main-title">'
        "Recruitment Analytics"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-subtitle">'
        "Live recruitment metrics from candidates, jobs and applications."
        "</div>",
        unsafe_allow_html=True,
    )

    def normalize_stage_value(value) -> str:
        """Normalize a stage for analytics comparisons only."""

        if value is None or isinstance(
            value,
            (dict, list, tuple, set),
        ):
            return ""

        try:
            if pd.isna(value):
                return ""
        except (TypeError, ValueError):
            return ""

        return " ".join(
            str(value).strip().casefold().split()
        )

    stage_groups = {
        "Pending Review": {
            "applied",
            "new",
            "pending",
            "pending review",
        },
        "Shortlisted": {
            "shortlist",
            "shortlisted",
        },
        "Interview": {
            "interview",
            "interview scheduled",
            "interviewing",
        },
        "Selected": {
            "hired",
            "joined",
            "selected",
        },
        "Rejected": {
            "reject",
            "rejected",
        },
    }

    def stage_label(normalized_stage: str) -> str:
        """Return a readable label for a normalized stored stage."""

        if not normalized_stage:
            return "Unspecified"

        for label, values in stage_groups.items():
            if normalized_stage in values:
                return label

        return normalized_stage.title()

    def normalize_identifier(value) -> str:
        """Return a safe string identifier for joins."""

        if value is None or isinstance(
            value,
            (dict, list, tuple, set),
        ):
            return ""

        try:
            if pd.isna(value):
                return ""
        except (TypeError, ValueError):
            return ""

        return str(value).strip()

    candidate_status_by_id = {}

    if (
        not raw_candidates.empty
        and "id" in raw_candidates.columns
    ):
        for _, candidate_row in raw_candidates.iterrows():
            candidate_id = normalize_identifier(
                candidate_row.get("id")
            )

            if candidate_id:
                candidate_status_by_id[candidate_id] = (
                    normalize_stage_value(
                        candidate_row.get("status")
                    )
                )

    analytics_applications = raw_applications.copy()

    if analytics_applications.empty:
        analytics_applications = pd.DataFrame(
            columns=[
                "candidate_id",
                "job_id",
                "application_stage",
                "candidate_score",
                "ats_score",
            ]
        )

    if "application_stage" in analytics_applications.columns:
        analytics_applications["_normalized_stage"] = (
            analytics_applications["application_stage"].apply(
                normalize_stage_value
            )
        )
    else:
        analytics_applications["_normalized_stage"] = ""

    if "candidate_id" in analytics_applications.columns:
        missing_stage_mask = analytics_applications[
            "_normalized_stage"
        ].eq("")
        fallback_stages = (
            analytics_applications["candidate_id"]
            .apply(normalize_identifier)
            .map(candidate_status_by_id)
            .fillna("")
        )
        analytics_applications.loc[
            missing_stage_mask,
            "_normalized_stage",
        ] = fallback_stages[missing_stage_mask]

    analytics_applications["Stage"] = analytics_applications[
        "_normalized_stage"
    ].apply(stage_label)

    candidate_current_stages = pd.DataFrame(
        {
            "candidate_id": list(candidate_status_by_id.keys()),
            "_normalized_stage": list(
                candidate_status_by_id.values()
            ),
        }
    )

    if (
        not analytics_applications.empty
        and "candidate_id" in analytics_applications.columns
        and not candidate_current_stages.empty
    ):
        latest_applications = analytics_applications.copy()

        if "applied_at" in latest_applications.columns:
            latest_applications["_applied_at"] = pd.to_datetime(
                latest_applications["applied_at"],
                errors="coerce",
            )
            latest_applications = latest_applications.sort_values(
                "_applied_at",
                ascending=False,
                na_position="last",
            )

        latest_applications["candidate_id"] = (
            latest_applications["candidate_id"].apply(
                normalize_identifier
            )
        )
        latest_applications = latest_applications.drop_duplicates(
            subset=["candidate_id"],
            keep="first",
        )
        latest_stage_by_candidate = latest_applications.set_index(
            "candidate_id"
        )["_normalized_stage"]
        candidate_current_stages["_application_stage"] = (
            candidate_current_stages["candidate_id"].map(
                latest_stage_by_candidate
            )
        )
        has_application_stage = candidate_current_stages[
            "_application_stage"
        ].fillna("").ne("")
        candidate_current_stages.loc[
            has_application_stage,
            "_normalized_stage",
        ] = candidate_current_stages.loc[
            has_application_stage,
            "_application_stage",
        ]

    def count_applications_in(group: str) -> int:
        """Count applications in one normalized stage group."""

        return int(
            analytics_applications["_normalized_stage"].isin(
                stage_groups[group]
            ).sum()
        )

    def count_candidates_in(group: str) -> int:
        """Count candidates by latest application stage with fallback."""

        if candidate_current_stages.empty:
            return 0

        return int(
            candidate_current_stages["_normalized_stage"].isin(
                stage_groups[group]
            ).sum()
        )

    analytics_total_candidates = len(raw_candidates)
    analytics_total_applications = len(raw_applications)

    if raw_jobs.empty or "status" not in raw_jobs.columns:
        analytics_open_jobs = 0
    else:
        analytics_open_jobs = int(
            raw_jobs["status"].apply(
                normalize_stage_value
            ).eq("open").sum()
        )

    analytics_pending = count_applications_in("Pending Review")
    analytics_shortlisted = count_candidates_in("Shortlisted")
    analytics_interview = count_candidates_in("Interview")
    analytics_selected = count_candidates_in("Selected")
    analytics_rejected = count_candidates_in("Rejected")

    def average_application_score(column: str):
        """Average valid numeric application scores."""

        if column not in analytics_applications.columns:
            return None

        scores = pd.to_numeric(
            analytics_applications[column],
            errors="coerce",
        ).dropna()

        if scores.empty:
            return None

        return round(float(scores.mean()), 1)

    analytics_candidate_score = average_application_score(
        "candidate_score"
    )
    analytics_ats_score = average_application_score("ats_score")

    analytics_metrics = [
        (
            "Total Candidates",
            analytics_total_candidates,
            "Live database",
            "👥",
        ),
        (
            "Open Jobs",
            analytics_open_jobs,
            "Jobs marked open",
            "💼",
        ),
        (
            "Total Applications",
            analytics_total_applications,
            "Live database",
            "📨",
        ),
        (
            "Pending Review",
            analytics_pending,
            "Applications",
            "📋",
        ),
        (
            "Shortlisted",
            analytics_shortlisted,
            "Candidates",
            "⭐",
        ),
        (
            "In Interview",
            analytics_interview,
            "Candidates",
            "📅",
        ),
        (
            "Selected",
            analytics_selected,
            "Candidates",
            "✅",
        ),
        (
            "Rejected",
            analytics_rejected,
            "Candidates",
            "⛔",
        ),
        (
            "Average Candidate Score",
            (
                f"{analytics_candidate_score}%"
                if analytics_candidate_score is not None
                else "N/A"
            ),
            "Applications",
            "🧠",
        ),
        (
            "Average ATS Score",
            (
                f"{analytics_ats_score}%"
                if analytics_ats_score is not None
                else "N/A"
            ),
            "Applications",
            "📄",
        ),
    ]

    for metric_start in range(0, len(analytics_metrics), 5):
        metric_columns = st.columns(5)

        for metric_column, metric_values in zip(
            metric_columns,
            analytics_metrics[metric_start:metric_start + 5],
        ):
            with metric_column:
                metric_card(*metric_values)

        st.write("")

    funnel_data = pd.DataFrame(
        {
            "Stage": [
                "Applications",
                "Shortlisted",
                "Interview",
                "Selected",
            ],
            "Count": [
                analytics_total_applications,
                count_applications_in("Shortlisted"),
                count_applications_in("Interview"),
                count_applications_in("Selected"),
            ],
        }
    )

    if "job_id" in analytics_applications.columns:
        application_job_ids = analytics_applications[
            "job_id"
        ].apply(normalize_identifier)
    else:
        application_job_ids = pd.Series(
            "",
            index=analytics_applications.index,
            dtype="object",
        )

    job_titles_by_id = {}

    if (
        not raw_jobs.empty
        and "id" in raw_jobs.columns
        and "title" in raw_jobs.columns
    ):
        for _, job_row in raw_jobs.iterrows():
            job_id = normalize_identifier(job_row.get("id"))
            job_title = job_row.get("title")

            if (
                job_id
                and job_title is not None
                and str(job_title).strip()
            ):
                job_titles_by_id[job_id] = str(job_title).strip()

    applications_by_job = (
        application_job_ids.map(job_titles_by_id)
        .fillna("Unknown Job")
        .replace("", "Unknown Job")
        .value_counts()
        .rename_axis("Job")
        .reset_index(name="Applications")
    )

    stage_distribution = (
        analytics_applications["Stage"]
        .value_counts()
        .rename_axis("Stage")
        .reset_index(name="Applications")
    )

    funnel_col, job_col = st.columns([1, 1])

    with funnel_col:
        st.markdown("### Hiring funnel")

        if analytics_total_applications == 0:
            st.info("No application data is available for the funnel.")
        else:
            funnel_chart = px.funnel(
                funnel_data,
                x="Count",
                y="Stage",
            )
            funnel_chart.update_layout(
                height=390,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="white",
                plot_bgcolor="white",
                showlegend=False,
            )
            st.plotly_chart(
                funnel_chart,
                width="stretch",
                config={"displayModeBar": False},
            )

    with job_col:
        st.markdown("### Applications by job")

        if applications_by_job.empty:
            st.info("No application-to-job data is available.")
        else:
            job_chart = px.bar(
                applications_by_job,
                x="Applications",
                y="Job",
                orientation="h",
                text="Applications",
            )
            job_chart.update_layout(
                height=390,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="white",
                plot_bgcolor="white",
                showlegend=False,
                yaxis={"categoryorder": "total ascending"},
            )
            st.plotly_chart(
                job_chart,
                width="stretch",
                config={"displayModeBar": False},
            )

    st.markdown("### Application-stage distribution")

    if stage_distribution.empty:
        st.info("No application-stage data is available.")
    else:
        stage_chart = px.bar(
            stage_distribution,
            x="Stage",
            y="Applications",
            text="Applications",
        )
        stage_chart.update_layout(
            height=360,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False,
            xaxis_title="Application stage",
            yaxis_title="Applications",
        )
        st.plotly_chart(
            stage_chart,
            width="stretch",
            config={"displayModeBar": False},
        )


# =========================================================
# Temporary pages
# =========================================================
else:
    st.markdown(
        f'<div class="main-title">'
        f"{selected_page}"
        "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        f"The {selected_page} page will be built next."
    )
