"""Generate visual hiring banners for social media using Pillow."""

import io
from PIL import Image, ImageDraw, ImageFont


def generate_job_banner_image(
    job_title: str,
    department: str,
    location: str,
    experience: str,
    skills: list[str],
    salary: str = "",
    app_link: str = "",
) -> bytes:
    """Create a 1080x1080 modern hiring graphic for Instagram/LinkedIn."""

    width, height = 1080, 1080
    image = Image.new("RGB", (width, height), color="#0F172A")
    draw = ImageDraw.Draw(image)

    # Top accent bar
    draw.rectangle([0, 0, width, 24], fill="#3B82F6")

    # Background accent shapes
    draw.ellipse([750, -120, 1250, 380], fill="#1E293B")
    draw.ellipse([-220, 680, 350, 1250], fill="#1E293B")

    try:
        font_large = ImageFont.truetype("arial.ttf", 54)
        font_sub = ImageFont.truetype("arial.ttf", 32)
        font_badge = ImageFont.truetype("arialbd.ttf", 26)
        font_pill = ImageFont.truetype("arial.ttf", 24)
        font_footer = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        font_large = ImageFont.load_default()
        font_sub = font_large
        font_badge = font_large
        font_pill = font_large
        font_footer = font_large

    # Badge: WE'RE HIRING
    badge_bg = [80, 80, 340, 136]
    draw.rounded_rectangle(badge_bg, radius=12, fill="#EF4444")
    draw.text((105, 94), "🔥 WE'RE HIRING", fill="#FFFFFF", font=font_badge)

    # Department / Team
    draw.text((80, 170), f"{department.upper()} TEAM", fill="#94A3B8", font=font_badge)

    # Job Title
    title_text = str(job_title)[:45]
    draw.text((80, 225), title_text, fill="#FFFFFF", font=font_large)

    # Meta Tags (Location & Experience)
    meta_y = 315
    tag1 = f"📍 {location}"
    tag2 = f"💼 {experience}"
    draw.rounded_rectangle([80, meta_y, 80 + len(tag1) * 15 + 30, meta_y + 44], radius=8, fill="#334155")
    draw.text((95, meta_y + 8), tag1, fill="#F8FAFC", font=font_pill)

    offset_x = 80 + len(tag1) * 15 + 50
    draw.rounded_rectangle([offset_x, meta_y, offset_x + len(tag2) * 15 + 30, meta_y + 44], radius=8, fill="#334155")
    draw.text((offset_x + 15, meta_y + 8), tag2, fill="#F8FAFC", font=font_pill)

    # Divider line
    draw.line([80, 390, 1000, 390], fill="#334155", width=2)

    # Required Skills Section
    draw.text((80, 420), "KEY COMPETENCIES & TECH STACK", fill="#38BDF8", font=font_badge)

    skills_y = 475
    curr_x = 80
    for skill in skills[:8]:
        skill_str = str(skill).strip()
        if not skill_str:
            continue
        box_w = len(skill_str) * 15 + 36
        if curr_x + box_w > 1000:
            curr_x = 80
            skills_y += 56
        draw.rounded_rectangle([curr_x, skills_y, curr_x + box_w, skills_y + 40], radius=20, fill="#1E293B", outline="#475569", width=2)
        draw.text((curr_x + 18, skills_y + 8), skill_str, fill="#E2E8F0", font=font_pill)
        curr_x += box_w + 14

    # Compensation Section
    if salary:
        sal_y = skills_y + 75
        draw.text((80, sal_y), f"💰 Package: {salary}", fill="#10B981", font=font_sub)

    # Bottom CTA Box
    cta_box = [80, 880, 1000, 990]
    draw.rounded_rectangle(cta_box, radius=16, fill="#2563EB")
    draw.text((120, 905), "📲 Fast-Track AI Application Portal", fill="#FFFFFF", font=font_badge)
    short_link = app_link if len(app_link) < 55 else app_link[:52] + "..."
    draw.text((120, 945), short_link or "Apply now via your recruiter link", fill="#DBEAFE", font=font_footer)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
