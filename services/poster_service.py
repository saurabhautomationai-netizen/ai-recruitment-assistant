"""Generate high-impact visual hiring graphics and posters with scannable QR codes."""

import io
from PIL import Image, ImageDraw, ImageFont
import qrcode


def generate_job_banner_image(
    job_title: str,
    department: str,
    location: str,
    experience: str,
    skills: list[str],
    salary: str = "",
    app_link: str = "",
    company_name: str = "TALENT ACQUISITION",
    recruiter_contact: str = "",
    theme: str = "teal",  # 'teal', 'blue', 'orange'
) -> bytes:
    """Create a 1080x1080 modern hiring graphic matching professional agency templates."""

    width, height = 1080, 1080

    # Color palettes
    if theme == "blue":
        bg_main = "#0B2545"
        accent_color = "#00B4D8"
        gold_color = "#FFD166"
        sub_card = "#134074"
    elif theme == "orange":
        bg_main = "#C2410C"
        accent_color = "#FDBA74"
        gold_color = "#FEF08A"
        sub_card = "#9A3412"
    else:  # Teal (Default, from user template)
        bg_main = "#064E3B"
        accent_color = "#34D399"
        gold_color = "#FBBF24"
        sub_card = "#047857"

    image = Image.new("RGB", (width, height), color=bg_main)
    draw = ImageDraw.Draw(image)

    # Decorative geometric background shapes
    draw.ellipse([700, -150, 1300, 450], fill=sub_card)
    draw.ellipse([-200, 650, 400, 1250], fill=sub_card)
    draw.rectangle([0, 0, width, 18], fill=gold_color)

    try:
        font_company = ImageFont.truetype("arialbd.ttf", 26)
        font_hero = ImageFont.truetype("arialbd.ttf", 74)
        font_subhero = ImageFont.truetype("ariali.ttf", 46)
        font_role = ImageFont.truetype("arialbd.ttf", 38)
        font_sec = ImageFont.truetype("arialbd.ttf", 26)
        font_bullet = ImageFont.truetype("arial.ttf", 26)
        font_pill = ImageFont.truetype("arialbd.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except Exception:
        font_company = ImageFont.load_default()
        font_hero = font_company
        font_subhero = font_company
        font_role = font_company
        font_sec = font_company
        font_bullet = font_company
        font_pill = font_company
        font_small = font_company

    # 1. Company / Agency Header
    draw.text((70, 55), str(company_name).upper()[:40], fill=gold_color, font=font_company)

    # 2. Main Hero Title: WE ARE HIRING!
    draw.text((70, 100), "WE ARE", fill="#FFFFFF", font=font_hero)
    draw.text((70, 175), "HIRING!", fill=gold_color, font=font_hero)

    # Magnifying Glass / Search icon graphic on the right
    draw.ellipse([880, 95, 990, 205], outline="#FFFFFF", width=12)
    draw.line([965, 180, 1030, 245], fill="#FFFFFF", width=14)

    # 3. Subheading: Join Our Team
    draw.text((70, 270), "Join Our Team", fill="#E0E7FF", font=font_subhero)

    # Divider bar
    draw.line([70, 335, 1010, 335], fill=accent_color, width=3)

    # 4. Job Title Card
    draw.rounded_rectangle([70, 355, 1010, 435], radius=14, fill="#0F172A", outline=gold_color, width=2)
    draw.text((95, 375), f"ROLE: {str(job_title).upper()[:42]}", fill="#FFFFFF", font=font_role)

    # 5. Specifications & Requirements Section
    draw.text((70, 460), "SPECIFICATIONS & ROLE DETAILS :", fill=gold_color, font=font_sec)

    specs = [
        f"Location: {location}",
        f"Experience Required: {experience}",
    ]
    if salary:
        specs.append(f"Compensation: {salary}")
    
    clean_skills = [str(s).strip() for s in skills if str(s).strip()][:6]
    if clean_skills:
        specs.append(f"Key Tech Stack: {', '.join(clean_skills)}")

    curr_y = 505
    for idx, spec in enumerate(specs, start=1):
        # Draw clean solid bullet dot
        draw.ellipse([70, curr_y + 6, 84, curr_y + 20], fill=accent_color)
        draw.text((100, curr_y), spec[:65], fill="#F8FAFC", font=font_bullet)
        curr_y += 44

    # 6. Bottom Application Section with Working QR Code
    bottom_box_top = 750
    draw.rounded_rectangle([70, bottom_box_top, 1010, 1010], radius=16, fill="#0F172A", outline=accent_color, width=2)

    # Generate QR Code for the application URL
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
            qr_img = qr_raw.resize((210, 210))
        except Exception:
            qr_img = None

    if qr_img:
        image.paste(qr_img, (95, bottom_box_top + 25))
        draw.text((330, bottom_box_top + 35), "SCAN WITH PHONE CAMERA TO APPLY", fill=gold_color, font=font_sec)
        draw.text((330, bottom_box_top + 75), "Point your camera at the QR code to open the 60s application portal.", fill="#CBD5E1", font=font_small)
        
        display_link = app_link if len(app_link) < 48 else app_link[:45] + "..."
        draw.text((330, bottom_box_top + 115), f"Link: {display_link}", fill=accent_color, font=font_small)

        if recruiter_contact:
            draw.text((330, bottom_box_top + 155), f"HR Contact / WhatsApp: {recruiter_contact}", fill="#F8FAFC", font=font_sec)
        else:
            draw.text((330, bottom_box_top + 155), "Fast-Track AI Screening Enabled", fill="#38BDF8", font=font_sec)
    else:
        draw.text((110, bottom_box_top + 45), "HOW TO APPLY :", fill=gold_color, font=font_sec)
        draw.text((110, bottom_box_top + 90), f"Submit your CV at: {app_link}", fill="#FFFFFF", font=font_bullet)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
