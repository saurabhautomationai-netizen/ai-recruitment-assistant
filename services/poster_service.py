"""Generate high-impact visual hiring graphics and posters with scannable QR codes."""

import io
from PIL import Image, ImageDraw, ImageFont
import qrcode


def generate_job_banner_image(
    job_title: str,
    department: str = "General",
    location: str = "Remote",
    experience: str = "Experienced",
    skills: list[str] = None,
    salary: str = "",
    app_link: str = "",
    company_name: str = "TALENT ACQUISITION",
    recruiter_contact: str = "",
    theme: str = "blue",  # 'blue', 'teal', 'orange'
    **kwargs,
) -> bytes:
    """Create a 1080x1080 modern hiring graphic matching professional agency card templates (like Image 5)."""

    if skills is None:
        skills = []

    width, height = 1080, 1080

    # Color palettes
    if theme == "teal":
        bg_top = "#044E42"
        bg_bottom = "#064E3B"
        accent_blue = "#0D9488"
        card_bg = "#0F2922"
        gold_highlight = "#F59E0B"
        white = "#FFFFFF"
    elif theme == "orange":
        bg_top = "#9A3412"
        bg_bottom = "#7C2D12"
        accent_blue = "#EA580C"
        card_bg = "#431407"
        gold_highlight = "#FDE047"
        white = "#FFFFFF"
    else:  # Royal Blue (Default, exact match to Image 5)
        bg_top = "#1D4ED8"
        bg_bottom = "#0F172A"
        accent_blue = "#3B82F6"
        card_bg = "#1E293B"
        gold_highlight = "#FACC15"
        white = "#FFFFFF"

    image = Image.new("RGB", (width, height), color=bg_bottom)
    draw = ImageDraw.Draw(image)

    # Top header gradient banner
    draw.rectangle([0, 0, width, 300], fill=bg_top)
    draw.ellipse([750, -100, 1250, 400], fill=accent_blue)
    draw.ellipse([-150, 100, 350, 550], fill=accent_blue)

    try:
        font_super = ImageFont.truetype("arialbd.ttf", 26)
        font_hero = ImageFont.truetype("arialbd.ttf", 68)
        font_job = ImageFont.truetype("arialbd.ttf", 44)
        font_sub = ImageFont.truetype("arialbd.ttf", 22)
        font_card_title = ImageFont.truetype("arialbd.ttf", 24)
        font_card_body = ImageFont.truetype("arial.ttf", 20)
        font_pill = ImageFont.truetype("arialbd.ttf", 21)
        font_footer_large = ImageFont.truetype("arialbd.ttf", 28)
        font_footer_sub = ImageFont.truetype("arialbd.ttf", 22)
    except Exception:
        font_super = ImageFont.load_default()
        font_hero = font_super
        font_job = font_super
        font_sub = font_super
        font_card_title = font_super
        font_card_body = font_super
        font_pill = font_super
        font_footer_large = font_super
        font_footer_sub = font_super

    # 1. Top Agency Tag
    draw.text((60, 40), f"[ {str(company_name).upper()[:40]} ]", fill=gold_highlight, font=font_super)

    # 2. Main Title: WE ARE HIRING!
    draw.text((60, 75), "WE ARE", fill=white, font=font_hero)
    draw.text((60, 140), "HIRING!", fill=gold_highlight, font=font_hero)

    # 3. Main Role Banner Card (White Box with Bold Dark Text)
    draw.rounded_rectangle([60, 230, 1020, 320], radius=16, fill=white, outline=gold_highlight, width=3)
    role_title_text = str(job_title).upper()[:36]
    draw.text((90, 252), f"ROLE: {role_title_text}", fill="#0F172A", font=font_job)

    # Subtitle tagline
    draw.text((60, 335), "Join a High-Growth Team • Build Your Career • Fast-Track AI Screening!", fill="#93C5FD", font=font_sub)

    # 4. Top 2 Highlight Cards (Side by Side)
    card_y = 380
    card_w = 465
    card_h = 135

    # Card 1: Work Type / Location
    draw.rounded_rectangle([60, card_y, 60 + card_w, card_y + card_h], radius=14, fill=card_bg, outline=accent_blue, width=2)
    draw.text((90, card_y + 25), "LOCATION & TYPE", fill=gold_highlight, font=font_card_title)
    draw.text((90, card_y + 58), f"{location}", fill=white, font=font_card_title)
    draw.text((90, card_y + 90), f"Department: {department}", fill="#94A3B8", font=font_card_body)

    # Card 2: Compensation / Package
    draw.rounded_rectangle([555, card_y, 555 + card_w, card_y + card_h], radius=14, fill=card_bg, outline=accent_blue, width=2)
    draw.text((585, card_y + 25), "COMPENSATION", fill=gold_highlight, font=font_card_title)
    sal_text = salary if salary else "Competitive Package"
    draw.text((585, card_y + 58), f"{sal_text}", fill=white, font=font_card_title)
    draw.text((585, card_y + 90), "Performance-based growth", fill="#94A3B8", font=font_card_body)

    # 5. Middle 3 Specification Pill Cards
    pill_y = 535
    pill_w = 300
    pill_h = 100

    # Pill 1: Experience
    draw.rounded_rectangle([60, pill_y, 60 + pill_w, pill_y + pill_h], radius=12, fill=card_bg, outline="#475569", width=2)
    draw.text((80, pill_y + 20), "EXPERIENCE", fill=gold_highlight, font=font_pill)
    draw.text((80, pill_y + 55), f"{experience}", fill=white, font=font_pill)

    # Pill 2: Availability
    draw.rounded_rectangle([390, pill_y, 390 + pill_w, pill_y + pill_h], radius=12, fill=card_bg, outline="#475569", width=2)
    draw.text((410, pill_y + 20), "AVAILABILITY", fill=gold_highlight, font=font_pill)
    draw.text((410, pill_y + 55), "Immediate / 30 Days", fill=white, font=font_pill)

    # Pill 3: Key Skills Count
    draw.rounded_rectangle([720, pill_y, 720 + pill_w, pill_y + pill_h], radius=12, fill=card_bg, outline="#475569", width=2)
    draw.text((740, pill_y + 20), "KEY TECH STACK", fill=gold_highlight, font=font_pill)
    clean_skills = [str(s).strip() for s in skills if str(s).strip()]
    skills_preview = ", ".join(clean_skills[:3]) if clean_skills else "Domain Skills"
    draw.text((740, pill_y + 55), skills_preview[:20], fill=white, font=font_pill)

    # 6. "WHY JOIN US?" Feature Bar
    why_y = 655
    draw.rounded_rectangle([60, why_y, 1020, why_y + 60], radius=10, fill="#1E293B")
    draw.text((80, why_y + 18), "WHY JOIN US:   • High Career Growth   • Meritocracy   • Global Impact", fill="#E2E8F0", font=font_sub)

    # 7. Bottom CTA & Scannable QR Code Box
    bottom_y = 735
    bottom_h = 285
    draw.rounded_rectangle([60, bottom_y, 1020, bottom_y + bottom_h], radius=16, fill="#0F172A", outline=gold_highlight, width=2)

    # Generate QR Code
    qr_img = None
    if app_link and app_link.strip():
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=6,
                border=2,
            )
            qr.add_data(app_link.strip())
            qr.make(fit=True)
            qr_raw = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF").convert("RGB")
            qr_img = qr_raw.resize((230, 230))
        except Exception:
            qr_img = None

    if qr_img:
        image.paste(qr_img, (85, bottom_y + 25))
        draw.text((345, bottom_y + 35), "READY TO TAKE THE NEXT STEP?", fill=gold_highlight, font=font_footer_large)
        draw.text((345, bottom_y + 75), "Point phone camera at QR code to apply in 60s!", fill=white, font=font_card_title)
        
        display_link = app_link if len(app_link) < 46 else app_link[:43] + "..."
        draw.text((345, bottom_y + 115), f"Link: {display_link}", fill="#38BDF8", font=font_card_body)

        draw.rounded_rectangle([345, bottom_y + 155, 990, bottom_y + 245], radius=10, fill=card_bg, outline=accent_blue, width=1)
        draw.text((365, bottom_y + 175), f"FOR MORE INFO / HR CONTACT:", fill="#94A3B8", font=font_card_body)
        contact_display = recruiter_contact if recruiter_contact else "+91 98765 43210 (HR Helpline)"
        draw.text((365, bottom_y + 205), f"Call / WhatsApp: {contact_display}", fill=gold_highlight, font=font_footer_sub)
    else:
        draw.text((100, bottom_y + 50), "READY TO APPLY?", fill=gold_highlight, font=font_footer_large)
        draw.text((100, bottom_y + 100), f"Submit CV at: {app_link}", fill=white, font=font_card_title)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
