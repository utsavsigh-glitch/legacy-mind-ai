from __future__ import annotations

import shutil
import uuid
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .analyzer import analyze_workspace, safe_extract_name
from .ai_analyzer import generate_ai_analysis


BASE = Path(__file__).resolve().parents[1]

UPLOADS = BASE / "uploads"
WORKSPACES = BASE / "workspaces"

UPLOADS.mkdir(exist_ok=True)
WORKSPACES.mkdir(exist_ok=True)


app = FastAPI(
    title="LegacyMind AI",
    version="0.1.0",
    description=(
        "MVP API for legacy code analysis, security checks "
        "and modernization planning."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


PROJECTS = {}


@app.get("/")
def root():
    return {
        "name": "LegacyMind AI",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...)):

    filename = safe_extract_name(
        file.filename or "upload.zip"
    )

    project_id = str(uuid.uuid4())

    project_dir = WORKSPACES / project_id
    project_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    upload_path = UPLOADS / f"{project_id}_{filename}"

    try:

        # --------------------------------------------------
        # 1. Save uploaded file
        # --------------------------------------------------

        with upload_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # --------------------------------------------------
        # 2. Extract ZIP or save single source file
        # --------------------------------------------------

        if filename.lower().endswith(".zip"):

            with zipfile.ZipFile(upload_path) as archive:

                for member in archive.infolist():

                    member_name = Path(
                        member.filename
                    )

                    if member.is_dir():
                        continue

                    # Prevent path traversal attacks
                    if (
                        member_name.is_absolute()
                        or ".." in member_name.parts
                    ):
                        continue

                    destination = (
                        project_dir / member_name
                    )

                    destination.parent.mkdir(
                        parents=True,
                        exist_ok=True
                    )

                    with archive.open(member) as src:
                        with destination.open("wb") as dst:

                            shutil.copyfileobj(
                                src,
                                dst
                            )

        else:

            destination = (
                project_dir / filename
            )

            shutil.copy2(
                upload_path,
                destination
            )

        # --------------------------------------------------
        # 3. Existing static analysis
        # --------------------------------------------------

        result = analyze_workspace(
            project_dir
        )

        # --------------------------------------------------
        # 4. Groq AI analysis
        # --------------------------------------------------

        try:

            ai_analysis = generate_ai_analysis(
                project_dir
            )

        except Exception as exc:

            ai_analysis = {
                "status": "error",
                "message": str(exc),
            }

        # --------------------------------------------------
        # 5. Add AI result to existing analysis
        # --------------------------------------------------

        result["ai_analysis"] = ai_analysis

        # --------------------------------------------------
        # 6. Store project result
        # --------------------------------------------------

        PROJECTS[project_id] = result

        # --------------------------------------------------
        # 7. Return JSON response
        # --------------------------------------------------

        return JSONResponse(
            {
                "project_id": project_id,
                **result,
            }
        )

    except zipfile.BadZipFile:

        raise HTTPException(
            status_code=400,
            detail=(
                "The uploaded file is not a valid ZIP archive."
            ),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {exc}",
        )

    finally:

        # Remove temporary uploaded file
        upload_path.unlink(
            missing_ok=True
        )


@app.get("/api/analysis/{project_id}")
def get_analysis(project_id: str):

    result = PROJECTS.get(
        project_id
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Project not found. "
                "Analyze an upload first."
            ),
        )

    return {
        "project_id": project_id,
        **result,
    }


@app.delete("/api/analysis/{project_id}")
def delete_analysis(project_id: str):

    if project_id not in PROJECTS:

        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    PROJECTS.pop(
        project_id,
        None
    )

    shutil.rmtree(
        WORKSPACES / project_id,
        ignore_errors=True
    )

    return {
        "deleted": True
    }