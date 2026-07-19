import html
import json

import pandas as pd
import plotly.express as px
import streamlit as st

from components.metric_cards import metric_card
from services.supabase_service import (
    get_applications,
    get_candidates,
    get_jobs,
    update_application_stage,
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


def show_interview_questions(value) -> None:
    """Display interview questions stored as JSON, list, or text."""

    if value is None:
        st.info("No interview questions are available.")
        return

    if isinstance(value, float) and pd.isna(value):
        st.info("No interview questions are available.")
        return

    parsed_value = value

    if isinstance(value, str):
        try:
            parsed_value = json.loads(value)
        except json.JSONDecodeError:
            parsed_value = value

    if isinstance(parsed_value, dict):
        questions = parsed_value.get("questions", [])

        if isinstance(questions, list) and questions:
            for number, question in enumerate(
                questions,
                start=1,
            ):
                if isinstance(question, dict):
                    question_text = question.get(
                        "question",
                        str(question),
                    )
                else:
                    question_text = str(question)

                st.write(f"{number}. {question_text}")
        else:
            st.write(str(parsed_value))

    elif isinstance(parsed_value, list):
        for number, question in enumerate(
            parsed_value,
            start=1,
        ):
            if isinstance(question, dict):
                question_text = question.get(
                    "question",
                    str(question),
                )
            else:
                question_text = str(question)

            st.write(f"{number}. {question_text}")

    else:
        st.write(str(parsed_value))

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

            application_stage = safe_value(
                selected_application,
                "application_stage",
                safe_value(
                    selected_raw_candidate,
                    "status",
                    "Pending Review",
                ),
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
            selected_application_id = safe_value(
                selected_application,
                "id",
                "",
            )

            action_message = st.session_state.pop(
                "candidate_action_success",
                None,
            )

            if (
                action_message
                and action_message["application_id"]
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
                st.markdown("#### Recommendation")

                recommendation = safe_value(
                    selected_application,
                    "recommendation",
                )

                if recommendation.lower() in [
                    "reject",
                    "rejected",
                ]:
                    st.error(recommendation)

                elif recommendation.lower() in [
                    "shortlist",
                    "shortlisted",
                    "recommend",
                    "recommended",
                ]:
                    st.success(recommendation)

                else:
                    st.info(recommendation)

                if (
                    "matched_skills"
                    in selected_application.index
                ):
                    st.markdown(
                        "#### Matched Skills"
                    )

                    st.write(
                        safe_value(
                            selected_application,
                            "matched_skills",
                        )
                    )

                if (
                    "missing_skills"
                    in selected_application.index
                ):
                    st.markdown(
                        "#### Missing Skills"
                    )

                    st.write(
                        safe_value(
                            selected_application,
                            "missing_skills",
                        )
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
        st.dataframe(
            raw_applications,
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
