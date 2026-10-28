"""
Script to generate high-aesthetic, professional 16:9 widescreen PowerPoint deck
for AROHA Investor Pitch (8 Slides with built-in presenter notes).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path: str):
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    BG_DARK = RGBColor(10, 15, 29)          # #0a0f1d Deep Navy / Dark slate
    CARD_BG = RGBColor(22, 32, 54)          # #162036 Card panels
    CARD_BORDER = RGBColor(45, 60, 95)      # Card outline
    CYAN = RGBColor(56, 189, 248)           # #38bdf8 Primary Accent
    PURPLE = RGBColor(168, 85, 247)         # #a855f7 Violet / Intelligence
    EMERALD = RGBColor(16, 185, 129)        # #10b981 High-ROI / Success
    AMBER = RGBColor(245, 158, 11)          # #f59e0b Warning / Focus
    TEXT_MAIN = RGBColor(241, 245, 249)     # #f1f5f9 Crisp White
    TEXT_MUTED = RGBColor(148, 163, 184)    # #94a3b8 Slate Grey
    WHITE = RGBColor(255, 255, 255)

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height
        )
        bg_shape.fill.solid()
        bg_shape.fill.fore_color.rgb = BG_DARK
        bg_shape.line.fill.background()
        return bg_shape

    def add_header(slide, slide_num, title, subtitle):
        # Header text frame
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(1.1))
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p_tag = tf.paragraphs[0]
        p_tag.text = f"SLIDE {slide_num:02d} // AROHA INVESTOR PITCH"
        p_tag.font.name = "Calibri"
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = CYAN

        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.name = "Calibri"
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_MAIN

        if subtitle:
            p_sub = tf.add_paragraph()
            p_sub.text = subtitle
            p_sub.font.name = "Calibri"
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title="", title_color=CYAN):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = CARD_BG
        shape.line.color.rgb = CARD_BORDER
        shape.line.width = Pt(1.2)

        tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.2), width - Inches(0.4), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        if title:
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = "Calibri"
            p.font.size = Pt(16)
            p.font.bold = True
            p.font.color.rgb = title_color
        return tf

    # ==========================================
    # SLIDE 1: Title & The Vision
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Big Title Header Center
    t1_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(3.0))
    t1_frame = t1_box.text_frame
    t1_frame.word_wrap = True

    p = t1_frame.paragraphs[0]
    p.text = "AROHA"
    p.font.name = "Calibri"
    p.font.size = Pt(56)
    p.font.bold = True
    p.font.color.rgb = CYAN

    p2 = t1_frame.add_paragraph()
    p2.text = "The Intelligence & Valuation Layer for Tech Skills"
    p2.font.name = "Calibri"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_MAIN

    p3 = t1_frame.add_paragraph()
    p3.text = "Eliminating speculation in career progression, hiring, and enterprise reskilling."
    p3.font.name = "Calibri"
    p3.font.size = Pt(16)
    p3.font.color.rgb = TEXT_MUTED

    # 3 Stat Cards on Title Slide
    stats = [
        ("17,400+", "Job Postings Benchmark", "Canonicalized Indian tech market dataset across all domains", CYAN),
        ("88.6%", "Salary Hike Accuracy", "Supervised ML predicting salary hike readiness from skill vectors", EMERALD),
        ("SkillPulse™", "0–100 Valuation Index", "Objective, explainable score calculating real compensation ROI", PURPLE),
    ]

    for i, (metric, label, desc, color) in enumerate(stats):
        col_left = Inches(1.0 + i * 3.9)
        tf = add_card(s1, col_left, Inches(4.5), Inches(3.6), Inches(2.3))
        
        p_val = tf.paragraphs[0]
        p_val.text = metric
        p_val.font.size = Pt(32)
        p_val.font.bold = True
        p_val.font.color.rgb = color

        p_lbl = tf.add_paragraph()
        p_lbl.text = label
        p_lbl.font.size = Pt(14)
        p_lbl.font.bold = True
        p_lbl.font.color.rgb = TEXT_MAIN

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = TEXT_MUTED

    notes1 = s1.notes_slide.notes_text_frame
    notes1.text = (
        "Presenter Script:\n"
        "Good morning investors. We are building AROHA. The Indian tech ecosystem employs over 5.4 million engineers, "
        "yet both talent and enterprises evaluate skills using 20-year-old, rear-view-mirror methods. "
        "AROHA is the objective valuation and intelligence layer that connects what skills are learned to what they are actually worth in the market."
    )

    # ==========================================
    # SLIDE 2: The Problem
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, 2, "The Trillion-Dollar Disconnect in Technical Talent", "Three structural failure points paralyzing modern career and workforce decisions")

    problems = [
        (
            "1. The Rear-View Mirror Trap",
            "Salary Portals (AmbitionBox, Glassdoor)",
            "• Historical averages reflect where people WERE 2-3 years ago, not what skills are worth TODAY.\n"
            "• Purely crowd-sourced with zero validation against active market postings.\n"
            "• Incapable of answering: 'If I learn PyTorch, what is my exact salary upside?'",
            AMBER
        ),
        (
            "2. The Incentive Conflict",
            "EdTech Giants (Scaler, UpGrad, Coursera)",
            "• Assessments exist solely as top-of-funnel lead generation to sell ₹1.5L–₹3L bootcamps.\n"
            "• Severe conflict of interest: platforms grade users down to sell courses.\n"
            "• Course completion certificates & badges carry zero quantifiable market salary signal.",
            PURPLE
        ),
        (
            "3. Enterprise Reskilling Blind Spot",
            "GCCs & Global IT Enterprises",
            "• Companies spending billions retraining thousands into AI, MLOps, and Cloud.\n"
            "• Completely blind to workforce skill readiness and true market capability.\n"
            "• Zero empirical metric to evaluate whether L&D budgets generate real organizational ROI.",
            CYAN
        ),
    ]

    for i, (title, sub, body, color) in enumerate(problems):
        col_left = Inches(0.8 + i * 3.95)
        tf = add_card(s2, col_left, Inches(1.8), Inches(3.75), Inches(5.0), title, color)
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(12)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MAIN

        p_body = tf.add_paragraph()
        p_body.text = body
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = TEXT_MUTED

    notes2 = s2.notes_slide.notes_text_frame
    notes2.text = (
        "Presenter Script:\n"
        "Right now, an engineer wanting to know what their skills are worth has two broken options: look at outdated crowd-sourced salary averages, "
        "or take an assessment from an EdTech company whose only goal is to sell them an expensive course. "
        "For enterprise leaders, it's worse—they are spending millions reskilling thousands of engineers into AI, with zero mathematical proof of market capability. "
        "This is the disconnect AROHA solves."
    )

    # ==========================================
    # SLIDE 3: The Product Experience (3-Step Engine)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, 3, "The Product Experience: 3-Step Valuation Journey", "How candidates and enterprises interact with AROHA: From raw input to quantified salary ROI")

    flow_steps = [
        (
            "STEP 1: Input Profile & Target Role",
            "Data Ingestion & NLP Normalization",
            "• User submits current technical skills (e.g., Python, SQL, Pandas) & target aspiration (e.g., Data Scientist).\n\n"
            "• Air-Gapped NLP Canonicalizer resolves 1,200+ messy acronyms, aliases & framework variations into clean standardized entities.\n\n"
            "• Zero third-party LLM latency or privacy leakage.",
            CYAN
        ),
        (
            "STEP 2: Benchmark & ML Scoring",
            "SkillPulse™ Mathematical Processing",
            "• Profile benchmarked against 17,400+ active Indian tech job postings & compensation curves.\n\n"
            "• SkillPulse™ Formula runs:\n"
            "  0.35(Demand) + 0.25(Versatility) + 0.25(Salary) + 0.15(Frontier Signal).\n\n"
            "• Supervised ML (88.6% accuracy) calculates exact salary hike probability.",
            PURPLE
        ),
        (
            "STEP 3: Actionable Valuation & Roadmap",
            "Quantified Output (Zero Course Selling)",
            "• SkillPulse™ Score (0–100): Transparent market rating (e.g. 74/100).\n\n"
            "• Real-Time Salary Benchmark: Current market worth (₹14.2 LPA vs ₹12.27L mean).\n\n"
            "• Prioritized Skill Gap Radar: Top 3 skills ranked by direct rupee ROI (e.g. +₹4.5L for Statistics, +₹3.2L for ML).",
            EMERALD
        ),
    ]

    for i, (title, sub, body, color) in enumerate(flow_steps):
        col_left = Inches(0.8 + i * 3.95)
        tf = add_card(s3, col_left, Inches(1.8), Inches(3.75), Inches(5.0), title, color)
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(12)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MAIN

        p_body = tf.add_paragraph()
        p_body.text = f"\n{body}"
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = TEXT_MUTED

    notes3 = s3.notes_slide.notes_text_frame
    notes3.text = (
        "Presenter Script:\n"
        "Here is how the product actually works in 3 simple steps: "
        "First, a developer or an enterprise HR uploads their current skills—say, Python and SQL—and selects a target role. "
        "Our NLP pipeline canonicalizes those skills in milliseconds without expensive LLM API calls. "
        "Second, our engine cross-references their profile against 17,400+ active job postings and computes their SkillPulse score from 0 to 100. "
        "Third, instead of selling them a ₹2 Lakh course, we output pure mathematical truth: their current market valuation, their hike probability, "
        "and the exact top 3 skills that will increase their salary the fastest."
    )

    # ==========================================
    # SLIDE 4: Core Product Modules & Enterprise Value
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, 4, "Four Core Product Modules Driving B2C & B2B Value", "Modular architecture powering individual career navigation and enterprise workforce intelligence")

    modules = [
        (
            "1. SkillPulse™ Valuation Card",
            "The 'CIBIL Score' for Tech Skills",
            "• Single 0–100 index measuring real market capability.\n"
            "• Accepted by HR and compensation committees.\n"
            "• Separates empirical facts [OBSERVED] from predictions [MODEL OUTPUT].",
            CYAN
        ),
        (
            "2. 'What-If' Salary Simulator",
            "Interactive Compensation Sandbox",
            "• Engineers toggle skills to simulate instant ₹ salary uplift.\n"
            "• Continuous salary curves across 5 experience tiers (₹3.8L to ₹26.2L+ LPA).\n"
            "• Direct answer to: 'If I learn PyTorch, what is my upside?'",
            EMERALD
        ),
        (
            "3. Dynamic Skill Gap Radar",
            "Personalized ROI-Ranked Roadmap",
            "• Ranks missing competencies by salary ROI, demand, & difficulty.\n"
            "• Statistics (+1.398 LR coefficient) identified as top driver.\n"
            "• Zero EdTech course-selling bias or sponsored content.",
            PURPLE
        ),
        (
            "4. Enterprise Workforce Audit",
            "B2B L&D & Reskilling Intelligence",
            "• Team skill heatmaps for GCCs & IT services giants.\n"
            "• Pinpoints organizational GenAI/Cloud readiness deficits.\n"
            "• Delivers empirical audit of L&D reskilling ROI.",
            AMBER
        ),
    ]

    for i, (title, sub, body, color) in enumerate(modules):
        row = i // 2
        col = i % 2
        left = Inches(0.8 + col * 5.95)
        top = Inches(1.8 + row * 2.55)
        tf = add_card(s4, left, top, Inches(5.75), Inches(2.35), title, color)
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(12)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MAIN

        p_body = tf.add_paragraph()
        p_body.text = f"\n{body}"
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = TEXT_MUTED

    notes4 = s4.notes_slide.notes_text_frame
    notes4.text = (
        "Presenter Script:\n"
        "AROHA is built on 4 core modules. Module 1 is the SkillPulse Valuation Card—think of it as the CIBIL score for engineering capability. "
        "Module 2 is our 'What-If' Salary Simulator: an engineer toggles skills and instantly sees their compensation curve shift. "
        "Module 3 is our Skill Gap Radar, which gives them an empirical roadmap showing that learning Statistics yields a 3.2x higher salary boost than learning another web framework. "
        "And Module 4 is our high-ACV enterprise engine: Global Capability Centers use our audit heatmaps to evaluate thousands of engineers and measure real reskilling ROI."
    )

    # ==========================================
    # SLIDE 5: Market Opportunity
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, 5, "Massive Addressable Market Fueled by AI Transformation", "Riding the tectonic shift in technical hiring and enterprise AI adoption")

    markets = [
        ("TAM: $6.2 Billion", "Global Workforce Analytics & Talent Intelligence", "16.4% CAGR globally as enterprises shift away from static job descriptions to skills-based organizations.", CYAN),
        ("SAM: $1.8 Billion", "Indian Tech Workforce & Corporate Reskilling", "5.4M active IT engineers; 1,580+ Global Capability Centers (GCCs) in India navigating mandatory GenAI transitions.", EMERALD),
        ("SOM: $120 Million", "Initial Beachhead (Data, AI & Cloud Roles)", "Targeting 450,000+ data science, cloud, and AI practitioners across Tier-1 tech hubs (Bengaluru, Hyderabad, Pune, NCR).", PURPLE),
    ]

    for i, (title, sub, desc, color) in enumerate(markets):
        left = Inches(0.8 + i * 3.95)
        tf = add_card(s5, left, Inches(1.8), Inches(3.75), Inches(5.0), title, color)
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(13)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MAIN

        p_desc = tf.add_paragraph()
        p_desc.text = f"\n{desc}"
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = TEXT_MUTED

    notes5 = s5.notes_slide.notes_text_frame
    notes5.text = (
        "Presenter Script:\n"
        "The timing couldn't be better. India's GCC ecosystem is expanding rapidly, and every single technology company is facing an urgent mandate: "
        "transition legacy software engineers into AI and MLOps. Our initial beachhead is the Indian data science and cloud engineering workforce—"
        "a $120M immediate opportunity, scaling into the broader $1.8B digital talent ecosystem."
    )

    # ==========================================
    # SLIDE 6: Business Model & Monetization
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, 6, "Three High-Margin, Complementary Revenue Engines", "Diversified monetization spanning high-ACV enterprise SaaS to programmatic API licensing")

    streams = [
        (
            "B2B Enterprise SaaS",
            "Workforce & Reskilling Intelligence",
            "• Target: GCCs, IT Services Giants (TCS, Infosys, Wipro), Tech Scaleups\n"
            "• Offering: Workforce skill health audits, internal mobility matching, upskilling ROI benchmarks\n"
            "• ACV: ₹5 Lakh – ₹25 Lakh / year\n"
            "• Contract: Annual recurring subscription with per-seat volume tiers",
            CYAN
        ),
        (
            "API & Data Licensing",
            "Talent Intelligence as a Service",
            "• Target: Job Portals (Cutshort, Naukri), ATS Providers, Recruitment Firms\n"
            "• Offering: Real-time skill scoring APIs, live compensation curve lookups, candidate match scoring\n"
            "• Model: Usage-based API tiers + Monthly developer retainer (₹50k–₹2L/mo)",
            PURPLE
        ),
        (
            "B2C Career Copilot",
            "Freemium Individual Pro Tier",
            "• Target: Mid-to-senior engineers, career switchers, active job hunters\n"
            "• Offering: Personal salary hike simulator, resume-to-salary audit, prioritized skill gap roadmap\n"
            "• Pricing: ₹499 – ₹999 / month or ₹3,999 / year\n"
            "• High virality driven by peer benchmarking",
            EMERALD
        ),
    ]

    for i, (title, sub, body, color) in enumerate(streams):
        left = Inches(0.8 + i * 3.95)
        tf = add_card(s6, left, Inches(1.8), Inches(3.75), Inches(5.0), title, color)
        
        p_sub = tf.add_paragraph()
        p_sub.text = sub
        p_sub.font.size = Pt(12)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MAIN

        p_body = tf.add_paragraph()
        p_body.text = f"\n{body}"
        p_body.font.size = Pt(11)
        p_body.font.color.rgb = TEXT_MUTED

    notes6 = s6.notes_slide.notes_text_frame
    notes6.text = (
        "Presenter Script:\n"
        "We monetize through a high-margin enterprise SaaS model selling workforce intelligence to GCCs and IT enterprises, "
        "complemented by high-volume API licensing to job portals, and a high-converting B2C freemium tier for ambitious engineers looking to negotiate higher compensation."
    )

    # ==========================================
    # SLIDE 7: Competitive Matrix & Moats
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, 7, "Competitive Moats: Why AROHA Wins", "The only neutral, mathematically transparent intelligence layer in the market")

    tf_mat = add_card(s7, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.9), "Competitive Landscape & Moats", CYAN)
    p_table = tf_mat.add_paragraph()
    p_table.text = (
        "DIMENSION                 | SALARY PORTALS (AmbitionBox) | EDTECH (Scaler, UpGrad)     | ENTERPRISE (Eightfold.ai)   | AROHA\n"
        "--------------------------+------------------------------+-----------------------------+-----------------------------+----------------------------\n"
        "Valuation Horizon         | Backward-looking (Historical)| Upsell-focused (Biased)     | Internal Enterprise Only    | Real-Time & Predictive\n"
        "Core Business Model       | Job ads & employer branding  | Sells ₹1.5L–₹3L bootcamps   | $100k+ annual contracts     | Independent Valuation SaaS\n"
        "Algorithm Transparency    | None (Raw user averages)     | Black-box course quizzes    | Proprietary deep neural net | 100% Explainable Math\n"
        "Market Grounding          | Unverified user submissions  | Synthetic academic tests    | Proprietary client resumes  | 17,400+ Active Market JDs\n"
        "Actionable Trajectory     | None                         | 'Buy our course'            | Internal enterprise tracks  | Empirical ROI Roadmap\n\n"
        "AROHA'S CORE MOATS:\n"
        "1. Complete Ecosystem Neutrality: We don't sell courses; we provide the objective currency that grades all courses and candidates.\n"
        "2. Explainable Trust Moat: Mathematical equations that can be defended directly in enterprise compensation committee reviews.\n"
        "3. Low-Friction REST Architecture: Modular, lightweight deployment in under 48 hours without months of enterprise IT friction."
    )
    p_table.font.name = "Consolas"
    p_table.font.size = Pt(9.5)
    p_table.font.color.rgb = TEXT_MAIN

    notes7 = s7.notes_slide.notes_text_frame
    notes7.text = (
        "Presenter Script:\n"
        "AmbitionBox shows where people were. Scaler shows what they want to sell you. Eightfold is an expensive black box. "
        "AROHA is the neutral, transparent GPS that sits in the middle as the single source of truth for skill value."
    )

    # ==========================================
    # SLIDE 8: The Ask & 18-Month Roadmap
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, 8, "The Ask & 18-Month Execution Plan", "Raising Seed Capital to become India's definitive technical talent intelligence layer")

    # Left: The Ask and Use of Funds
    tf_fund = add_card(s8, Inches(0.8), Inches(1.8), Inches(5.75), Inches(5.0), "Seeking $600K (₹5 Crore) Seed Capital", EMERALD)
    p_fund = tf_fund.add_paragraph()
    p_fund.text = (
        "18-Month Runway to Series A Traction\n\n"
        "Capital Deployment Allocation:\n"
        "• 50% Engineering & ML Infrastructure:\n"
        "  - Scale automated scraper pipeline to 500k+ monthly job postings.\n"
        "  - Deploy automated NLP continuous retraining pipelines.\n"
        "• 30% Enterprise GTM & Growth:\n"
        "  - B2B enterprise sales team targeting Bengaluru & Hyderabad GCCs.\n"
        "  - Strategic distribution pilots with hiring platforms & tech communities.\n"
        "• 20% Operations, Governance & Security:\n"
        "  - SOC2, ISO27001 data compliance for enterprise client readiness.\n"
        "  - Legal and core operating overhead."
    )
    p_fund.font.size = Pt(11)
    p_fund.font.color.rgb = TEXT_MUTED

    # Right: Milestones & Roadmap
    tf_road = add_card(s8, Inches(6.75), Inches(1.8), Inches(5.75), Inches(5.0), "18-Month Key Milestones", CYAN)
    p_road = tf_road.add_paragraph()
    p_road.text = (
        "Q1 – Q2: Platform Scale & Community Beachhead\n"
        "• Expand market ingestion to 500,000+ active tech job records.\n"
        "• Launch API pilots with 2 tech recruitment platforms.\n"
        "• Reach 25,000 monthly active B2C career simulator users.\n\n"
        "Q3 – Q4: Enterprise Monetization Validation\n"
        "• Sign first 15 paid enterprise GCC pilots (₹15L avg contract value).\n"
        "• Roll out self-serve B2C Pro subscription (1,500+ paying subscribers).\n"
        "• Introduce LLM-driven personalized resume audit engine.\n\n"
        "Q5 – Q6: Series A Readiness\n"
        "• Surpass ₹3.5 Crore ($420K) ARR across Enterprise SaaS & API licensing.\n"
        "• Expand coverage to Southeast Asia & Middle East GCC corridors.\n"
        "• Initiate Series A institutional financing round."
    )
    p_road.font.size = Pt(11)
    p_road.font.color.rgb = TEXT_MUTED

    notes8 = s8.notes_slide.notes_text_frame
    notes8.text = (
        "Presenter Script:\n"
        "We are raising $600k to expand our data ingestion to over 500,000 records, partner with 2 major tech talent marketplaces, "
        "and sign our first 20 enterprise GCC customers. We already have a working, tested product and validated machine learning models. "
        "We invite you to join us in building India's definitive talent intelligence infrastructure. Thank you."
    )

    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    out_dir = r"c:\Users\hstps\Videos\AROHA\output"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "AROHA_Investor_Pitch_Deck.pptx")
    try:
        create_deck(out_file)
    except PermissionError:
        fallback_file = os.path.join(out_dir, "AROHA_Investor_Pitch_Deck_v2.pptx")
        print(f"File locked by PowerPoint. Saving to fallback: {fallback_file}")
        create_deck(fallback_file)
