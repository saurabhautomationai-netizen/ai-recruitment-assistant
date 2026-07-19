# AI Recruitment Assistant

An AI-powered recruitment management system designed to help recruiters manage candidates, jobs, applications, resume analysis, candidate scoring, and interview workflows from one dashboard.

The project combines a Streamlit dashboard, Supabase database, AI resume analysis, and recruitment automation workflows.

---

## Project Overview

The AI Recruitment Assistant reduces repetitive recruitment work by automatically collecting candidate information, parsing resumes, managing job openings, evaluating candidate-job fit, and presenting recruitment data through a centralized dashboard.

It is designed as a portfolio-ready, scalable recruitment automation system that can later be converted into a SaaS product.

---

## Current Features

### Candidate Management

- View all registered candidates
- Search and filter candidates
- View detailed candidate profiles
- Display contact and career information
- View education and previous companies
- Show candidate skills as visual skill tags
- Track candidate recruitment status

### AI Resume Analysis

- Extract structured information from resumes
- Generate AI resume summaries
- Identify technical and soft skills
- Display candidate experience and background
- Store parsed resume information in Supabase

### Candidate Evaluation

- Candidate score
- ATS score
- Fit score
- AI-generated strengths
- AI-generated concerns
- Hiring recommendation
- Suggested interview questions

### Job Management

- Create and manage job openings
- Store job descriptions
- Define required skills
- Track department and location
- Track salary range
- Track experience requirements
- Manage job status

### Application Management

- Connect candidates with available jobs
- Track application stages
- View candidate-job matching results
- Track recruitment pipeline progress

### Recruitment Automation

- Candidate form submission
- Resume upload and extraction
- Candidate data storage
- HR email notification
- Candidate WhatsApp confirmation
- Job creation workflow

---

## Technology Stack

### Frontend

- Python
- Streamlit
- Custom HTML and CSS

### Backend

- Supabase
- PostgreSQL

### AI and Automation

- OpenAI
- n8n
- AI resume parsing
- Candidate-job matching
- Automated candidate scoring

### Integrations

- Gmail
- WhatsApp
- Google Drive
- Supabase API

### Development Tools

- Visual Studio Code
- Git
- GitHub
- OpenAI Codex

---

## Project Structure

```text
ai-recruitment-assistant/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── components/
│   ├── __init__.py
│   └── metric_cards.py
│
├── services/
│   ├── __init__.py
│   ├── database.py
│   └── supabase_service.py
│
└── pages/