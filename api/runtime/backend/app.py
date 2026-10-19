"""
FastAPI Application Entrypoint for AROHA
Team: Syntax Society
"""

import sys
from io import BytesIO
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse

from models.schemas import (
    RecommendationRequest,
    ExtractRequest,
    ExtractResponse
)
from services import (
    analytics_service,
    recommender_service,
    skill_extractor
)
from backend import database
from backend.auth import auth_router
from utils.constants import TARGET_ROLES

app = FastAPI(
    title="AROHA API",
    description="AI-Powered Workforce & Skill Intelligence Platform (Enterprise API)",
    version="1.0.0"
)

# Enable CORS for local cross-origin development if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Auth router
app.include_router(auth_router)

# Mount static files
STATIC_DIR = PROJECT_ROOT / "frontend" / "static"
TEMPLATES_DIR = PROJECT_ROOT / "frontend" / "templates"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# ----------------- Frontend Route ----------------- #

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse(
            "<h1>AROHA API</h1><p>Frontend template not yet found. Access <a href='/docs'>/docs</a> for API.</p>"
        )
    return FileResponse(str(index_file))

@app.get("/login", response_class=HTMLResponse)
async def serve_login_view():
    index_file = TEMPLATES_DIR / "index.html"
    if not index_file.exists():
        return HTMLResponse(
            "<h1>AROHA API</h1><p>Frontend template not yet found. Access <a href='/docs'>/docs</a> for API.</p>"
        )
    return FileResponse(str(index_file))

# ----------------- Core API Endpoints ----------------- #

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AROHA",
        "team": "Syntax Society",
        "database_records": database.get_total_jobs_count()
    }

@app.get("/api/dashboard")
async def get_dashboard():
    """Returns high-level summary KPIs for the landing dashboard."""
    return analytics_service.get_dashboard_summary()

@app.get("/api/skills")
async def get_all_skills():
    """Returns all unique skills indexed across the dataset."""
    skills = database.get_all_skills_list()
    return {"skills": skills, "count": len(skills)}

@app.get("/api/skills/{skill_name}")
async def get_skill_detail(skill_name: str):
    """Returns demand metrics, related skills, industry spread, and forecast."""
    profile = analytics_service.get_skill_profile(skill_name)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found in job market index.")
    return profile

@app.get("/api/roles")
async def get_all_roles():
    """Returns all supported career roles."""
    return {"roles": TARGET_ROLES}

@app.get("/api/roles/{role_name}")
async def get_role_detail(role_name: str):
    """Returns skills, salary benchmarks, and demand distribution for a career role."""
    detail = analytics_service.get_role_analysis(role_name)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Role '{role_name}' not found.")
    return detail

@app.get("/api/emerging")
async def get_emerging_skills():
    """Returns curated emerging & frontier skills with daily momentum, growth rates and forecast notes."""
    skills_list = list(analytics_service.EMERGING_SKILLS_CATALOG)
    today_date = skills_list[0]["as_of_date"] if skills_list else None
    return {
        "disclaimer": "Live Daily Index — Market momentum & growth rates synthesized daily from Indian tech GCC & startup trends.",
        "as_of_date": today_date,
        "market_status": "Daily Dynamic Momentum Active",
        "skills": skills_list
    }

class EmergingSkillOverrideRequest(BaseModel):
    skill_name: str
    signal_strength: float
    notes: Optional[str] = ""

@app.post("/api/emerging/override")
async def override_emerging_skill(payload: EmergingSkillOverrideRequest):
    """Allows admins, external scrapers or cron tasks to push live signal score overrides."""
    from services.emerging_service import emerging_service
    res = emerging_service.update_skill_override(
        skill_name=payload.skill_name,
        signal_strength=payload.signal_strength,
        notes=payload.notes or ""
    )
    return {"status": "success", "skill": payload.skill_name, "data": res}

@app.post("/api/recommend")
async def get_recommendation(payload: RecommendationRequest):
    """Computes personalized skill gap analysis and step-by-step roadmap."""
    return recommender_service.recommend_skills(
        target_role=payload.target_role,
        user_skills_input=payload.user_skills,
        experience_level=payload.experience_level or "Fresher"
    )

@app.post("/api/extract", response_model=ExtractResponse)
async def extract_skills_from_text(payload: ExtractRequest):
    """NLP Pipeline to extract and normalize skills from raw job descriptions."""
    result = skill_extractor.extractor.extract_skills(payload.text)
    return ExtractResponse(
        extracted_skills=result["extracted_skills"],
        raw_detected_count=result["raw_count"],
        matched_canonical_skills=result["extracted_skills"],
        top_matching_roles=result["role_alignments"],
        processing_time_ms=result["processing_time_ms"]
    )

@app.post("/api/extract-resume", response_model=ExtractResponse)
async def extract_skills_from_resume(file: UploadFile = File(...)):
    """Extract resume text in-memory and identify indexed skills. Files are never stored."""
    allowed_extensions = {".pdf", ".docx", ".txt"}
    filename = file.filename or "resume"
    extension = Path(filename).suffix.lower()
    if extension not in allowed_extensions:
        raise HTTPException(status_code=415, detail="Upload a PDF, DOCX, or TXT resume.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="The uploaded resume is empty.")
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Please upload a resume smaller than 5 MB.")

    try:
        if extension == ".txt":
            resume_text = contents.decode("utf-8", errors="ignore")
        elif extension == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(BytesIO(contents))
            resume_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            from docx import Document
            document = Document(BytesIO(contents))
            resume_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="We couldn't read that resume. Try a text-based PDF, DOCX, or TXT file.") from exc

    if len(resume_text.strip()) < 20:
        raise HTTPException(status_code=422, detail="No readable resume text was found. Try a text-based PDF or DOCX file.")

    result = skill_extractor.extractor.extract_skills(resume_text)
    return ExtractResponse(
        extracted_skills=result["extracted_skills"],
        raw_detected_count=result["raw_count"],
        matched_canonical_skills=result["extracted_skills"],
        top_matching_roles=result["role_alignments"],
        processing_time_ms=result["processing_time_ms"]
    )

@app.get("/api/dataset/sample")
async def get_dataset_sample(limit: int = 20):
    """Transparently inspect underlying sample job postings."""
    with database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs ORDER BY date DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cursor.fetchall()]
        return {
            "total_sample_shown": len(rows),
            "disclaimer": "Realistic benchmark mock dataset calibrated for Indian tech hubs (Bengaluru, Hyderabad, Pune, Gurugram, etc.)",
            "jobs": rows
        }
