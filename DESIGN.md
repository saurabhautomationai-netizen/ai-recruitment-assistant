# DESIGN.md — ZERO Recruit (AI Recruitment Assistant)

> **Standard Design Specification Document for Google Stitch & AI Coding Agents**  
> *Repository*: `https://github.com/saurabhautomationai-netizen/ai-recruitment-assistant`  
> *Platform*: Enterprise AI Recruitment & Autonomous Talent Operations (ZERO Recruit)

---

## 1. Brand Identity & Visual Language

ZERO Recruit is an enterprise-grade Autonomous AI Recruitment Platform designed for elite staffing agencies and talent acquisition teams. The visual identity embodies **executive trust, surgical precision, and serene velocity**.

- **Aesthetic**: Executive Forest Minimalist (inspired by Linear, Vercel, and Refero high-density design patterns).
- **Feel**: Crisp, high-contrast, distraction-free, light-mode dominant with pearl-white elevated surfaces and deep pine-green primary controls.
- **Density**: High-density operational data layouts balanced with generous card padding and micro-border delineation.

---

## 2. Color Palette & Design Tokens

### Core Brand Colors
| Token Name | Hex Code | Semantic Role | Usage |
| :--- | :--- | :--- | :--- |
| `--color-primary` | `#162E20` | **Executive Forest Green** | Sidebar background, primary brand headers, active tabs, major button fills. |
| `--color-primary-hover` | `#0E1F15` | **Deep Pine** | Button hover states, active sidebar pill backgrounds. |
| `--color-canvas` | `#F3F4F1` | **Pearl White / Soft Mist** | Main page background, neutral canvas behind cards. |
| `--color-surface` | `#FFFFFF` | **Pure White Surface** | Elevated cards, Kanban columns, modals, inspectors, and data containers. |
| `--color-border` | `#E8EAE6` | **Subtle Slate Border** | Card outlines (1px solid), column separators, grid dividing lines. |
| `--color-accent-emerald` | `#059669` | **Emerald Pulse** | Success badges, ATS match scores (>= 80%), verified skills, primary highlights. |

### Typography Colors
| Token Name | Hex Code | Semantic Role |
| :--- | :--- | :--- |
| `--text-heading` | `#162E20` | Primary headings, candidate names, KPI values (font-weight: 800). |
| `--text-body` | `#334155` | Body copy, resume summaries, descriptions (font-weight: 400-500). |
| `--text-muted` | `#64748B` | Subtitles, metadata, timestamps, experience counters (font-weight: 500). |
| `--text-subtle` | `#94A3B8` | Column subheaders, inactive labels, placeholder text (font-weight: 600). |

### Status & Pipeline Tokens
| Pipeline Stage | Border / Accent | Background Tint | Meaning |
| :--- | :--- | :--- | :--- |
| **Shortlisted** | `#059669` (Emerald) | `#ECFDF5` | Candidate screened and qualified. |
| **Scheduled for Interview** | `#2563EB` (Cobalt Blue) | `#EFF6FF` | Interview invite dispatched or calendar slot reserved. |
| **Moved to Interview** | `#7C3AED` (Royal Violet) | `#F5F3FF` | Active technical / behavioral evaluation round. |
| **Selected Candidates** | `#16A34A` (Vibrant Green) | `#F0FDF4` | Offer extended, background check cleared, or hired. |
| **Rejected Candidates** | `#DC2626` (Ruby Red) | `#FEF2F2` | Disqualified with compliant GDPR feedback record. |

---

## 3. Typography Hierarchy

- **Primary Font Family**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif`
- **Monospace Family**: `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace`

| Element | Size | Weight | Line Height | Letter Spacing |
| :--- | :--- | :--- | :--- | :--- |
| **Page Title** | `28px` | `800` (Bold) | `1.2` | `-0.03em` |
| **Section Header** | `20px` | `800` (Bold) | `1.25` | `-0.02em` |
| **Card Header** | `15px` | `750` (Semi-Bold) | `1.3` | `-0.01em` |
| **Body Regular** | `13.5px` | `400-500` | `1.6` | `normal` |
| **Caption / Meta** | `11.5px` | `500-600` | `1.4` | `+0.01em` |
| **Badges / Tags** | `10.5px` | `750` | `1.0` | `+0.04em` (Uppercase) |

---

## 4. Component Design Specifications

### 4.1. Navigation Sidebar
- **Background**: `#162E20` (Forest Green).
- **Width**: `260px`.
- **Branding Header**: Brain emoji + **ZERO Recruit** in bold white typography with subtitle `AI Recruitment Assistant`.
- **Scope Selector**: Elevated white card displaying `Agency Master View` or `Recruiter Private Pipeline`.
- **Nav Items**: Clean list with rounded hover states (`border-radius: 8px`), icons, and emerald active indicators.

### 4.2. Metric / KPI Scorecards
- **Surface**: `#FFFFFF`, `border: 1px solid #E8EAE6`, `border-radius: 16px`.
- **Elevation**: `box-shadow: 0 2px 10px rgba(22, 46, 32, 0.04)`.
- **Layout**: Top row has metric label and delta chip (`+14.2% vs last month`); bottom row has bold numerical stat (`font-size: 26px; font-weight: 800; color: #162E20`).

### 4.3. Interactive 5-Stage Pipeline Kanban Board
- **Grid Layout**: 5 responsive columns with equal flex width.
- **Column Header**:
  - Distinct colored top-border line (`border-top: 4px solid <StageColor>`).
  - Stage icon, stage title (`font-size: 12.5px; font-weight: 800; color: #162E20`).
  - Count pill with tinted background matching the stage.
- **Candidate Cards**:
  - White background, `border: 1.5px solid #E8EAE6`, `border-radius: 14px`.
  - Candidate full name (`13.5px; font-weight: 750`), role, and verified experience years (`3y exp`).
  - ATS Match Score chip (`88% ATS` in emerald pill).
  - Quick action controls: `Inspect` button and inline `Move to Stage` selector.

### 4.4. Deep Candidate Intelligence Inspector Drawer
- **Container**: White surface with emerald border (`border: 1.5px solid #059669`, `border-radius: 20px`, `box-shadow: 0 4px 20px rgba(5, 150, 105, 0.08)`).
- **Header**: Candidate avatar badge, name, email, phone, ATS Score gauge (`88% ATS Score`), and Domain Alignment gauge (`92% Domain Match`).
- **Left Column**: Multi-bullet AI Executive Summary of Resume (Track record, core strengths, interview probe areas).
- **Right Column**: Domain-specific matching skills badges (`Matched` in green pills, `Gap / Stretch` in amber pills).
- **Bottom Controls**: `View Full Resume` expander and text download trigger.

### 4.5. 2D Recruitment Autonomy Matrix
- **Matrix Layout**: 4 Recruitment Phases (Sourcing, Screening, Interview, Placement) x 3 Autonomy Levels (Co-Pilot, Agentic Workflow, Full Autonomy).
- **Card States**:
  - Active autonomous agent cards have solid white background with emerald outline (`#059669`) and glowing pill tag (`LIVE`).
  - Planned / assisted cards feature diagonal hatched CSS textures.

---

## 5. Layout & Spacing System

- **Base Unit**: `4px` grid system.
- **Card Padding**: `16px` to `24px`.
- **Card Border Radius**:
  - Badges/Pills: `20px` (Pill shape).
  - Small Cards / Inputs: `10px` - `12px`.
  - Standard Cards: `14px` - `16px`.
  - Major Panels / Drawers: `20px`.
- **Spacing Scale**:
  - `xs`: `4px`
  - `sm`: `8px`
  - `md`: `16px`
  - `lg`: `24px`
  - `xl`: `32px`

---

## 6. Design Principles & Anti-Patterns

### Do:
- Use `#162E20` for primary actions and headings to preserve executive elegance.
- Maintain soft off-white background `#F3F4F1` so white cards `#FFFFFF` pop with subtle depth.
- Display clear numeric metrics (ATS score %, experience, time-to-hire) on every candidate view.
- Keep border outlines light (`#E8EAE6`) and avoid heavy black borders.

### Don't:
- Never use pure black (`#000000`) for text or backgrounds; use `#162E20` or `#334155`.
- Never use saturated neon backgrounds for alerts; always use soft pastel tints (`#ECFDF5`, `#EFF6FF`, `#FEF2F2`).
- Avoid cluttering cards with unstructured raw JSON or unparsed HTML.
- Avoid multiple competing primary green buttons in the same viewport.
