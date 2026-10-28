"""
High-Quality 1280x720 30FPS Twitter/X Promo Video Generator for AROHA.
Renders 6 dynamic scenes explaining features and differentiation,
encoded directly to H.264 MP4 using imageio-ffmpeg.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

WIDTH = 1280
HEIGHT = 720
FPS = 30
TOTAL_DURATION = 42.0  # seconds
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)  # 1260 frames

# Load fonts
FONT_DIR = "C:/Windows/Fonts"
font_title = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 38)
font_large = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 54)
font_huge = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 72)
font_head = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 26)
font_sub = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 20)
font_body = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 17)
font_bold = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 18)
font_mono = ImageFont.truetype(os.path.join(FONT_DIR, "consolab.ttf"), 16)
font_badge = ImageFont.truetype(os.path.join(FONT_DIR, "segoeuib.ttf"), 13)
font_caption = ImageFont.truetype(os.path.join(FONT_DIR, "segoeui.ttf"), 18)

# Palette
BG_COLOR = (9, 13, 24)
CARD_BG = (19, 28, 48, 230)
CARD_BORDER = (45, 62, 98)
ACCENT_CYAN = (56, 189, 248)
ACCENT_PURPLE = (168, 85, 247)
ACCENT_GREEN = (16, 185, 129)
ACCENT_AMBER = (245, 158, 11)
ACCENT_RED = (239, 68, 68)
TEXT_WHITE = (241, 245, 249)
TEXT_MUTED = (148, 163, 184)
BORDER_SUBTLE = (30, 41, 65)

def draw_rounded_card(draw, xy, fill, outline=None, radius=12, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def draw_header(draw, badge_text, title_text, sub_text, badge_color=ACCENT_CYAN):
    # Badge
    b_w = len(badge_text) * 9 + 24
    draw.rounded_rectangle([60, 36, 60 + b_w, 64], radius=6, fill=(badge_color[0]//5, badge_color[1]//5, badge_color[2]//5), outline=badge_color, width=1)
    draw.text((72, 42), badge_text, font=font_badge, fill=badge_color)
    
    # Title
    draw.text((60, 76), title_text, font=font_title, fill=TEXT_WHITE)
    # Subhead
    if sub_text:
        draw.text((60, 124), sub_text, font=font_sub, fill=TEXT_MUTED)

def draw_bottom_bar(draw, frame_idx, caption_text):
    # Progress line
    progress = frame_idx / float(TOTAL_FRAMES)
    draw.line([(0, HEIGHT - 54), (WIDTH, HEIGHT - 54)], fill=(20, 28, 44), width=2)
    draw.line([(0, HEIGHT - 54), (int(WIDTH * progress), HEIGHT - 54)], fill=ACCENT_CYAN, width=3)

    # Caption box
    draw.rectangle([0, HEIGHT - 50, WIDTH, HEIGHT], fill=(6, 9, 16))
    draw.text((60, HEIGHT - 38), "AROHA // " + caption_text, font=font_caption, fill=ACCENT_CYAN)

    # Branding right
    draw.text((WIDTH - 150, HEIGHT - 38), "aroha.ai", font=font_caption, fill=TEXT_MUTED)

def render_scene_1(t, frame_idx):
    """Scene 1: 0s - 7s: The Hook & The Problem"""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    draw_header(draw, "THE PROBLEM IN TECH TALENT", "Why are Tech Salaries & Skills Still Broken?", 
                "Engineers and enterprises make career-defining decisions based on flawed signals.", ACCENT_RED)

    # Card 1: Salary Portals
    c1_rect = [60, 175, 620, 560]
    draw_rounded_card(draw, c1_rect, (28, 18, 26), outline=ACCENT_RED, radius=14, width=2)
    draw.text((85, 200), "❌  Salary Portals (AmbitionBox, Glassdoor)", font=font_head, fill=(248, 113, 113))
    
    bullets_p1 = [
        ("• Rear-View Mirror:", "Shows what people made 2-3 years ago."),
        ("• Unverified Data:", "Crowd-sourced submissions with zero validation."),
        ("• Zero Simulation:", "Cannot answer: 'If I learn PyTorch, what is my upside?'"),
        ("• Recruitment Ad Model:", "Funded by employers, creating conflict of interest.")
    ]
    y = 260
    for b_title, b_desc in bullets_p1:
        draw.text((85, y), b_title, font=font_bold, fill=TEXT_WHITE)
        draw.text((85, y + 24), b_desc, font=font_body, fill=TEXT_MUTED)
        y += 68

    # Card 2: EdTech Platforms
    c2_rect = [660, 175, 1220, 560]
    draw_rounded_card(draw, c2_rect, (28, 18, 34), outline=ACCENT_PURPLE, radius=14, width=2)
    draw.text((685, 200), "❌  EdTech Giants (Scaler, UpGrad, Coursera)", font=font_head, fill=(192, 132, 252))

    bullets_p2 = [
        ("• Conflict of Interest:", "Assessments designed to fail users and sell courses."),
        ("• Expensive Paywalls:", "High-pressure pitches for ₹1.5L – ₹3L bootcamps."),
        ("• Vanity Credentials:", "Certificates and completion badges carry zero market value."),
        ("• Academic Focus:", "Teaches toy syntax instead of production enterprise skills.")
    ]
    y = 260
    for b_title, b_desc in bullets_p2:
        draw.text((685, y), b_title, font=font_bold, fill=TEXT_WHITE)
        draw.text((685, y + 24), b_desc, font=font_body, fill=TEXT_MUTED)
        y += 68

    caption = "Existing platforms either show 3-year-old historical averages or sell biased ₹2 Lakh courses."
    draw_bottom_bar(draw, frame_idx, caption)
    return im

def render_scene_2(t, frame_idx):
    """Scene 2: 7s - 14s: Introducing AROHA"""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    draw_header(draw, "THE SOLUTION // CATEGORY DEFINER", "Meet AROHA: The Intelligence & Valuation Layer", 
                "Like CIBIL or FICO for tech capability: 100% objective, 0% course-selling.", ACCENT_CYAN)

    # 3 Stat Cards
    metrics = [
        ("17,400+", "Market Postings Ingested", "Active tech postings from Bengaluru, Hyderabad, Pune & NCR benchmarked daily.", ACCENT_CYAN),
        ("88.6%", "ML Hike Prediction Accuracy", "Supervised classification predicting salary band readiness from competency vectors.", ACCENT_GREEN),
        ("0 – 100", "SkillPulse™ Valuation Index", "Objective score linking skill demand, versatility, and real compensation uplift.", ACCENT_PURPLE)
    ]

    for i, (m_val, m_lbl, m_desc, color) in enumerate(metrics):
        x = 60 + i * 395
        rect = [x, 175, x + 370, 440]
        draw_rounded_card(draw, rect, (16, 24, 42), outline=color, radius=14, width=2)
        draw.text((x + 25, 205), m_val, font=font_huge, fill=color)
        draw.text((x + 25, 290), m_lbl, font=font_head, fill=TEXT_WHITE)
        draw.text((x + 25, 340), m_desc, font=font_body, fill=TEXT_MUTED)

    # Formula Box at bottom
    f_rect = [60, 465, 1220, 565]
    draw_rounded_card(draw, f_rect, (14, 20, 36), outline=(56, 189, 248, 120), radius=12, width=1)
    draw.text((85, 485), "PROPRIETARY SKILLPULSE™ ALGORITHM", font=font_badge, fill=ACCENT_CYAN)
    formula_str = "SkillPulse = 0.35 × Demand + 0.25 × Versatility + 0.25 × Salary Signal + 0.15 × Frontier Signal"
    draw.text((85, 515), formula_str, font=font_head, fill=TEXT_WHITE)

    caption = "AROHA benchmarks 17,400+ tech job records to compute an objective 0–100 valuation score."
    draw_bottom_bar(draw, frame_idx, caption)
    return im

def render_scene_3(t, frame_idx):
    """Scene 3: 14s - 21s: Feature Spotlight 1 & 2"""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    draw_header(draw, "CORE PRODUCT CAPABILITIES", "Features 1 & 2: Real-Time Compensation Intelligence", 
                "Giving engineers and leaders empirical answers instead of gut feel.", ACCENT_GREEN)

    # Feature 1 Card: What-If Simulator
    c1_rect = [60, 175, 620, 560]
    draw_rounded_card(draw, c1_rect, (16, 28, 44), outline=ACCENT_CYAN, radius=14, width=2)
    draw.text((85, 200), "⚡ Feature 1: 'What-If' Salary Simulator", font=font_head, fill=ACCENT_CYAN)
    draw.text((85, 240), "Simulate the exact compensation impact of adding new skills:", font=font_body, fill=TEXT_MUTED)

    # Interactive simulation mockup box
    box1 = [85, 275, 595, 420]
    draw_rounded_card(draw, box1, (10, 18, 30), outline=BORDER_SUBTLE, radius=8)
    draw.text((105, 290), "Current Stack: Python + SQL", font=font_bold, fill=TEXT_WHITE)
    draw.text((105, 318), "Current Valuation: ₹10.5 LPA  (Benchmark Base)", font=font_body, fill=TEXT_MUTED)
    draw.text((105, 350), "+ Added Skill: PyTorch + Docker (MLOps)", font=font_bold, fill=ACCENT_GREEN)
    draw.text((105, 380), "Projected Valuation: ₹16.8 LPA  (+₹6.3L / +60% Upside!)", font=font_head, fill=ACCENT_GREEN)

    draw.text((85, 440), "• Continuous empirical curves across 5 experience tiers (₹3.8L to ₹26.2L+).", font=font_body, fill=TEXT_WHITE)
    draw.text((85, 475), "• Grounded in 17,400+ live hiring postings across Indian hubs.", font=font_body, fill=TEXT_MUTED)
    draw.text((85, 510), "• Eliminates the guesswork when planning what to learn next.", font=font_body, fill=TEXT_MUTED)

    # Feature 2 Card: Predictive ML Models
    c2_rect = [660, 175, 1220, 560]
    draw_rounded_card(draw, c2_rect, (22, 20, 48), outline=ACCENT_PURPLE, radius=14, width=2)
    draw.text((685, 200), "🧠 Feature 2: Predictive Career ML (88.6%)", font=font_head, fill=(192, 132, 252))
    draw.text((685, 240), "Supervised machine learning predicting promotion readiness:", font=font_body, fill=TEXT_MUTED)

    box2 = [685, 275, 1195, 420]
    draw_rounded_card(draw, box2, (14, 12, 32), outline=BORDER_SUBTLE, radius=8)
    draw.text((705, 290), "Logistic Regression Accuracy: 88.6% (F1: 0.889)", font=font_bold, fill=TEXT_WHITE)
    draw.text((705, 320), "Random Forest Classifier: 85.7% Accuracy", font=font_body, fill=TEXT_MUTED)
    draw.text((705, 350), "Empirical Insight from ML Model:", font=font_bold, fill=ACCENT_AMBER)
    draw.text((705, 380), "Math & Statistics (+1.398 LR weight) drives 3.2x more salary boost than syntax!", font=font_body, fill=TEXT_WHITE)

    draw.text((685, 440), "• Classifies salary hike probability from core competency vectors.", font=font_body, fill=TEXT_WHITE)
    draw.text((685, 475), "• Proves that foundational math beats framework memorization.", font=font_body, fill=TEXT_MUTED)
    draw.text((685, 510), "• Auditable data provenance: separates observed facts from predictions.", font=font_body, fill=TEXT_MUTED)

    caption = "Interactive What-If simulator projects exact rupee salary uplift; Supervised ML predicts hikes with 88.6% accuracy."
    draw_bottom_bar(draw, frame_idx, caption)
    return im

def render_scene_4(t, frame_idx):
    """Scene 4: 21s - 28s: Feature Spotlight 3 & 4"""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    draw_header(draw, "CORE PRODUCT CAPABILITIES", "Features 3 & 4: Skill Gap Radar & Enterprise Audits", 
                "From individual career roadmaps to enterprise workforce reskilling at scale.", ACCENT_AMBER)

    # Feature 3: Dynamic Skill Gap Radar
    c1_rect = [60, 175, 620, 560]
    draw_rounded_card(draw, c1_rect, (20, 24, 40), outline=ACCENT_CYAN, radius=14, width=2)
    draw.text((85, 200), "🧭 Feature 3: Actionable Skill Gap Radar", font=font_head, fill=ACCENT_CYAN)
    draw.text((85, 240), "Prioritizes missing competencies by direct ROI, not course catalogs:", font=font_body, fill=TEXT_MUTED)

    # Top 3 skills mockup
    skills_list = [
        ("1. Statistics & Probability", "+₹4.2L Salary Boost", "Demand: High • Top ML predictor"),
        ("2. Machine Learning (Scikit/PyTorch)", "+₹3.5L Salary Boost", "48% Data Science postings"),
        ("3. Production MLOps (Docker/CI)", "+₹2.8L Salary Boost", "+142% Frontier hiring surge")
    ]
    sy = 275
    for rank_title, boost, detail in skills_list:
        draw_rounded_card(draw, [85, sy, 595, sy + 58], (12, 18, 30), outline=BORDER_SUBTLE, radius=6)
        draw.text((100, sy + 8), rank_title, font=font_bold, fill=TEXT_WHITE)
        draw.text((430, sy + 8), boost, font=font_bold, fill=ACCENT_GREEN)
        draw.text((100, sy + 32), detail, font=font_body, fill=TEXT_MUTED)
        sy += 68

    draw.text((85, 490), "• Transparent justification for every single recommended skill.", font=font_body, fill=TEXT_WHITE)
    draw.text((85, 520), "• Zero course affiliate links, zero sponsored spam.", font=font_body, fill=TEXT_MUTED)

    # Feature 4: Enterprise Workforce Audit
    c2_rect = [660, 175, 1220, 560]
    draw_rounded_card(draw, c2_rect, (26, 22, 34), outline=ACCENT_AMBER, radius=14, width=2)
    draw.text((685, 200), "🏢 Feature 4: Enterprise Workforce Audit", font=font_head, fill=ACCENT_AMBER)
    draw.text((685, 240), "B2B SaaS intelligence for GCCs & IT services leaders:", font=font_body, fill=TEXT_MUTED)

    box4 = [685, 275, 1195, 415]
    draw_rounded_card(draw, box4, (16, 14, 24), outline=BORDER_SUBTLE, radius=8)
    draw.text((705, 290), "GCC & IT Enterprise Mandate: AI Reskilling", font=font_bold, fill=TEXT_WHITE)
    draw.text((705, 320), "• Problem: L&D reports 'hours of video watched' with 0 proof of skill.", font=font_body, fill=TEXT_MUTED)
    draw.text((705, 350), "• AROHA Solution: Workforce skill health audits across 5,000+ devs.", font=font_bold, fill=ACCENT_AMBER)
    draw.text((705, 380), "• Result: Empirical verification of reskilling ROI & internal mobility.", font=font_body, fill=ACCENT_GREEN)

    draw.text((685, 440), "• ACV: ₹5 Lakh – ₹25 Lakh / year recurring enterprise contracts.", font=font_body, fill=TEXT_WHITE)
    draw.text((685, 475), "• API Data Licensing for job portals and ATS candidate matching.", font=font_body, fill=TEXT_MUTED)
    draw.text((685, 510), "• Solves the multi-billion-dollar enterprise reskilling blind spot.", font=font_body, fill=TEXT_MUTED)

    caption = "Dynamic Skill Gap Radar ranks missing skills by rupee ROI; Enterprise module audits org-wide AI readiness."
    draw_bottom_bar(draw, frame_idx, caption)
    return im

def render_scene_5(t, frame_idx):
    """Scene 5: 28s - 35s: Why We Are Different (The Moat)"""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    draw_header(draw, "THE COMPETITIVE MOAT", "Why AROHA Wins: Unmatched Neutrality & Math", 
                "The only objective, explainable intelligence layer in the market.", ACCENT_CYAN)

    # Comparison Table
    table_rect = [60, 175, 1220, 560]
    draw_rounded_card(draw, table_rect, (14, 20, 36), outline=BORDER_SUBTLE, radius=14, width=1)

    headers = [("DIMENSION", 60), ("SALARY PORTALS", 310), ("EDTECH PLATFORMS", 600), ("AROHA", 920)]
    for h_text, h_x in headers:
        draw.text((h_x + 20, 195), h_text, font=font_bold, fill=ACCENT_CYAN if h_text == "AROHA" else TEXT_MUTED)

    draw.line([(80, 230), (1200, 230)], fill=BORDER_SUBTLE, width=1)

    rows = [
        ("Time Horizon", "Backward Looking (2022)", "Course syllabus based", "Real-Time & Predictive", ACCENT_GREEN),
        ("Business Model", "Employer job advertising", "Sells ₹1.5L–₹3L bootcamps", "Independent Valuation SaaS", ACCENT_GREEN),
        ("Algorithm", "Unverified user averages", "Biased lead-gen quizzes", "100% Explainable Math", ACCENT_GREEN),
        ("Market Grounding", "Self-reported surveys", "Academic synthetic tests", "17,400+ Active Market JDs", ACCENT_GREEN),
        ("Actionable Output", "Static salary band", "'Buy our course'", "Empirical ROI Roadmap", ACCENT_GREEN),
    ]

    ry = 245
    for dim, c1, c2, aroha_val, a_color in rows:
        draw.text((80, ry), dim, font=font_bold, fill=TEXT_WHITE)
        draw.text((330, ry), "❌ " + c1, font=font_body, fill=(248, 113, 113))
        draw.text((620, ry), "❌ " + c2, font=font_body, fill=(192, 132, 252))
        draw.text((940, ry), "✅ " + aroha_val, font=font_bold, fill=a_color)
        draw.line([(80, ry + 42), (1200, ry + 42)], fill=(20, 28, 48), width=1)
        ry += 58

    caption = "AmbitionBox shows where you were. Scaler shows what they sell. AROHA is the objective truth."
    draw_bottom_bar(draw, frame_idx, caption)
    return im

def render_scene_6(t, frame_idx):
    """Scene 6: 35s - 42s: Vision & Call to Action"""
    im = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(im)

    # Big Center Banner
    draw.rounded_rectangle([60, 60, 280, 96], radius=8, fill=(16, 36, 60), outline=ACCENT_CYAN, width=1)
    draw.text((80, 70), "THE FUTURE OF TALENT", font=font_badge, fill=ACCENT_CYAN)

    draw.text((60, 120), "AROHA", font=font_huge, fill=ACCENT_CYAN)
    draw.text((60, 210), "Don't just prepare for today's jobs.", font=font_large, fill=TEXT_WHITE)
    draw.text((60, 275), "Build for tomorrow's skills.", font=font_large, fill=ACCENT_PURPLE)

    # 3 Bullet Pillars
    pillars = [
        ("🎯", "100% Explainable AI", "Defensible mathematical scoring with zero black-box bias."),
        ("🇮🇳", "Built for 5.4M Indian Tech Talent", "Benchmarked across 1,580+ Global Capability Centers (GCCs)."),
        ("🚀", "Empirical Career Acceleration", "Direct path to higher compensation bands without expensive courses.")
    ]
    py = 370
    for icon, p_title, p_sub in pillars:
        draw.text((60, py), icon, font=font_head, fill=TEXT_WHITE)
        draw.text((105, py), p_title, font=font_head, fill=TEXT_WHITE)
        draw.text((105, py + 34), p_sub, font=font_body, fill=TEXT_MUTED)
        py += 80

    # Right Card CTA
    cta_rect = [780, 120, 1220, 560]
    draw_rounded_card(draw, cta_rect, (16, 24, 46), outline=ACCENT_CYAN, radius=18, width=2)
    draw.text((815, 160), "BENCHMARK YOUR PROFILE", font=font_head, fill=ACCENT_CYAN)
    draw.text((815, 205), "Calculate your SkillPulse™ score today:", font=font_body, fill=TEXT_WHITE)

    draw.text((815, 260), "🔗 aroha.ai", font=font_large, fill=ACCENT_GREEN)
    draw.text((815, 335), "• Instant 0–100 Capability Valuation", font=font_body, fill=TEXT_MUTED)
    draw.text((815, 370), "• Continuous Salary Curve Benchmark", font=font_body, fill=TEXT_MUTED)
    draw.text((815, 405), "• Prioritized Skill Gap Roadmap", font=font_body, fill=TEXT_MUTED)
    draw.text((815, 440), "• Enterprise Workforce Health Audits", font=font_body, fill=TEXT_MUTED)

    draw_rounded_card(draw, [815, 485, 1185, 535], (56, 189, 248), radius=8)
    draw.text((875, 498), "Try AROHA Now →", font=font_head, fill=(9, 13, 24))

    caption = "Stop guessing what your tech skills are worth. Experience objective intelligence at aroha.ai"
    draw_bottom_bar(draw, frame_idx, caption)
    return im

def generate_video(output_mp4_path: str):
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"Using FFmpeg binary: {ffmpeg_exe}")
    print(f"Total Frames to render: {TOTAL_FRAMES} ({TOTAL_DURATION}s @ {FPS}fps)")

    writer = imageio_ffmpeg.write_frames(
        output_mp4_path,
        size=(WIDTH, HEIGHT),
        fps=FPS,
        quality=8,
        codec="libx264",
        pix_fmt_out="yuv420p"
    )
    writer.send(None)  # prime generator

    scenes = [
        (0.0, 7.0, render_scene_1),
        (7.0, 14.0, render_scene_2),
        (14.0, 21.0, render_scene_3),
        (21.0, 28.0, render_scene_4),
        (28.0, 35.0, render_scene_5),
        (35.0, 42.0, render_scene_6),
    ]

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / float(FPS)
        
        # Pick scene
        chosen_render = render_scene_6
        for s_start, s_end, s_render in scenes:
            if s_start <= t < s_end:
                chosen_render = s_render
                break

        img = chosen_render(t, frame_idx)
        frame_bytes = img.tobytes()
        writer.send(frame_bytes)

        if frame_idx % 150 == 0 or frame_idx == TOTAL_FRAMES - 1:
            pct = int((frame_idx + 1) / TOTAL_FRAMES * 100)
            print(f"Rendering progress: {pct}% ({frame_idx + 1}/{TOTAL_FRAMES} frames)")

    writer.close()
    print(f"\nVideo generated successfully at: {output_mp4_path}")

if __name__ == "__main__":
    out_dir = r"c:\Users\hstps\Videos\AROHA\output"
    os.makedirs(out_dir, exist_ok=True)
    out_video = os.path.join(out_dir, "aroha_twitter_pitch.mp4")
    generate_video(out_video)
