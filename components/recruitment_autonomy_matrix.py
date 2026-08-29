"""
Recruitment Autonomy Matrix Component (ZERO Recruit)
Implements the 2D Capability and Workflow Matrix (Process Milestones vs. Autonomy Tiers)
strictly adhering to the Executive Forest Green and Pearl White design system.
"""

import streamlit as st


def render_recruitment_autonomy_matrix():
    """
    Renders the 2D Capability Grid showing human-led, human-assisted,
    and fully autonomous AI recruitment workflows.
    """
    st.markdown(
        """
        <div style="background: #ffffff; border: 1px solid #e8eae6; border-radius: 20px; padding: 24px; box-shadow: 0 2px 14px rgba(22, 46, 32, 0.04); margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 18px;">
                <div>
                    <div style="font-size: 20px; font-weight: 800; color: #162e20; letter-spacing: -0.02em;">
                        Recruitment Operations — The AI Autonomy Matrix
                    </div>
                    <div style="font-size: 13px; color: #55695c; margin-top: 3px;">
                        <b>12 of 18</b> recruitment workflows run fully autonomous, <b>4</b> human-assisted, <b>2</b> remain human-led.
                    </div>
                </div>
                <div style="display: flex; gap: 14px; align-items: center; font-size: 12px; font-weight: 600;">
                    <span style="display: flex; align-items: center; gap: 6px; color: #162e20;">
                        <span style="width: 10px; height: 10px; border-radius: 3px; background: #162e20; display: inline-block;"></span> Human-led
                    </span>
                    <span style="display: flex; align-items: center; gap: 6px; color: #2563eb;">
                        <span style="width: 10px; height: 10px; border-radius: 3px; background: #2563eb; display: inline-block;"></span> Human-assisted
                    </span>
                    <span style="display: flex; align-items: center; gap: 6px; color: #059669;">
                        <span style="width: 10px; height: 10px; border-radius: 3px; background: #059669; display: inline-block;"></span> Fully Autonomous
                    </span>
                </div>
            </div>

            <!-- Stage Columns Headers -->
            <div style="display: grid; grid-template-columns: 170px repeat(4, 1fr); gap: 12px; margin-bottom: 12px; font-size: 12px; font-weight: 750; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em;">
                <div style="color: #94a3b8; font-size: 11px;">AUTONOMY TIER</div>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 8px; border-left: 3px solid #162e20;">1. Sourcing & Intake</div>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 8px; border-left: 3px solid #2563eb;">2. Screen & Verify</div>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 8px; border-left: 3px solid #059669;">3. Assess & Interview</div>
                <div style="background: #f8fafc; padding: 8px 12px; border-radius: 8px; border-left: 3px solid #7c3aed;">4. Offer & Governance</div>
            </div>

            <!-- ROW 1: Human-Led -->
            <div style="display: grid; grid-template-columns: 170px repeat(4, 1fr); gap: 12px; margin-bottom: 14px;">
                <div style="background: #fafaf9; border: 1px solid #e7e5e4; border-radius: 12px; padding: 14px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 16px;">👤</span>
                        <span style="font-weight: 800; font-size: 13px; color: #162e20;">Human-led</span>
                    </div>
                    <div style="font-size: 11px; color: #78716c; margin-top: 4px;">Recruiter executive control</div>
                    <div style="margin-top: 8px;"><span style="background: #e7e5e4; color: #44403c; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">2 Tasks</span></div>
                </div>

                <div style="background: #fcfdfc; border: 1px solid #e8eae6; border-radius: 12px; padding: 12px 14px;">
                    <div style="font-weight: 700; font-size: 13px; color: #162e20;">Hiring Bar Calibration</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Role leveling & compensation band</div>
                    <div style="margin-top: 8px;"><span style="background: #f1f5f9; color: #475467; padding: 2px 7px; border-radius: 6px; font-size: 10px; font-weight: 600;">Manual Kickoff</span></div>
                </div>

                <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 12px 14px; opacity: 0.5; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #94a3b8;">
                    — Delegated to AI —
                </div>

                <div style="background: #fcfdfc; border: 1px solid #e8eae6; border-radius: 12px; padding: 12px 14px;">
                    <div style="font-weight: 700; font-size: 13px; color: #162e20;">Executive Culture Interview</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Final team alignment decision</div>
                    <div style="margin-top: 8px;"><span style="background: #f1f5f9; color: #475467; padding: 2px 7px; border-radius: 6px; font-size: 10px; font-weight: 600;">Human Decision</span></div>
                </div>

                <div style="background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 12px 14px; opacity: 0.5; display: flex; align-items: center; justify-content: center; font-size: 11px; color: #94a3b8;">
                    — Delegated to AI —
                </div>
            </div>

            <!-- ROW 2: Human-Assisted -->
            <div style="display: grid; grid-template-columns: 170px repeat(4, 1fr); gap: 12px; margin-bottom: 14px;">
                <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; padding: 14px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 16px;">🤖</span>
                        <span style="font-weight: 800; font-size: 13px; color: #1e40af;">Human-assisted</span>
                    </div>
                    <div style="font-size: 11px; color: #3b82f6; margin-top: 4px;">AI drafts, recruiter approves</div>
                    <div style="margin-top: 8px;"><span style="background: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">4 Tasks</span></div>
                </div>

                <div style="background: #fcfdfc; border: 1px solid #e8eae6; border-radius: 12px; padding: 12px 14px;">
                    <div style="font-weight: 700; font-size: 13px; color: #162e20;">Job Requisition Draft</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">GenAI auto-JD generator</div>
                    <div style="margin-top: 8px;"><span style="background: #eff6ff; color: #2563eb; padding: 2px 7px; border-radius: 6px; font-size: 10px; font-weight: 700;">1-Click Review</span></div>
                </div>

                <div style="background: #fcfdfc; border: 1px solid #e8eae6; border-radius: 12px; padding: 12px 14px;">
                    <div style="font-weight: 700; font-size: 13px; color: #162e20;">Shortlist Sanity Check</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Recruiter approves top 10%</div>
                    <div style="margin-top: 8px;"><span style="background: #eff6ff; color: #2563eb; padding: 2px 7px; border-radius: 6px; font-size: 10px; font-weight: 700;">Stage Sign-off</span></div>
                </div>

                <div style="background: #fcfdfc; border: 1px solid #e8eae6; border-radius: 12px; padding: 12px 14px;">
                    <div style="font-weight: 700; font-size: 13px; color: #162e20;">STAR Rubric Tuning</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Custom behavioral questions</div>
                    <div style="margin-top: 8px;"><span style="background: #eff6ff; color: #2563eb; padding: 2px 7px; border-radius: 6px; font-size: 10px; font-weight: 700;">Hybrid Kit</span></div>
                </div>

                <div style="background: #fcfdfc; border: 1px solid #e8eae6; border-radius: 12px; padding: 12px 14px;">
                    <div style="font-weight: 700; font-size: 13px; color: #162e20;">Offer Compensation</div>
                    <div style="font-size: 11px; color: #64748b; margin-top: 2px;">Salary counter-approval</div>
                    <div style="margin-top: 8px;"><span style="background: #eff6ff; color: #2563eb; padding: 2px 7px; border-radius: 6px; font-size: 10px; font-weight: 700;">Agency Margin</span></div>
                </div>
            </div>

            <!-- ROW 3: Fully Autonomous -->
            <div style="display: grid; grid-template-columns: 170px repeat(4, 1fr); gap: 12px;">
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%); border: 1px solid #86efac; border-radius: 12px; padding: 14px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 16px;">⚡</span>
                        <span style="font-weight: 800; font-size: 13px; color: #166534;">Fully Autonomous</span>
                    </div>
                    <div style="font-size: 11px; color: #15803d; margin-top: 4px;">Zero human latency</div>
                    <div style="margin-top: 8px;"><span style="background: #dcfce7; color: #15803d; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 700;">12 Tasks Active</span></div>
                </div>

                <!-- Column 1 Autonomous Tasks -->
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">📡 Job Syndication</div>
                        <div style="font-size: 10.5px; color: #55695c;">LinkedIn, Naukri, Indeed APIs</div>
                    </div>
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">🎯 Lead Gen Harvester</div>
                        <div style="font-size: 10.5px; color: #55695c;">Automated profile discovery</div>
                    </div>
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">🌐 Careers Portal Sync</div>
                        <div style="font-size: 10.5px; color: #55695c;">Real-time application intake</div>
                    </div>
                </div>

                <!-- Column 2 Autonomous Tasks -->
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">📄 Resume OCR & Parsing</div>
                        <div style="font-size: 10.5px; color: #55695c;">PDF/DOCX metadata extraction</div>
                    </div>
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">🔍 pgvector Match Score</div>
                        <div style="font-size: 10.5px; color: #55695c;">1536-dim semantic similarity</div>
                    </div>
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">🛡️ PII Masking Engine</div>
                        <div style="font-size: 10.5px; color: #55695c;">Blind hiring compliance</div>
                    </div>
                </div>

                <!-- Column 3 Autonomous Tasks -->
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">🧪 Assessment Dispatch</div>
                        <div style="font-size: 10.5px; color: #55695c;">9-industry dynamic testing</div>
                    </div>
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">📅 Self-Service Booking</div>
                        <div style="font-size: 10.5px; color: #55695c;">Cal.com & Google Calendar</div>
                    </div>
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">💬 Multi-Channel WhatsApp</div>
                        <div style="font-size: 10.5px; color: #55695c;">Instant automated reminders</div>
                    </div>
                </div>

                <!-- Column 4 Autonomous Tasks -->
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">📝 PDF Offer Generator</div>
                        <div style="font-size: 10.5px; color: #55695c;">Dynamic CTC & compensation</div>
                    </div>
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">🔒 GDPR / RTBF Purge</div>
                        <div style="font-size: 10.5px; color: #55695c;">Automated data retention</div>
                    </div>
                    <div style="background: repeating-linear-gradient(45deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.05) 10px, #ffffff 10px, #ffffff 20px); border: 1px solid #bbf7d0; border-radius: 12px; padding: 10px 12px;">
                        <div style="font-weight: 750; font-size: 12.5px; color: #162e20;">📊 EEO & OFCCP Audit</div>
                        <div style="font-size: 10.5px; color: #55695c;">Disparate impact calculation</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
