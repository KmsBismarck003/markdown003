from __future__ import annotations

from pathlib import Path
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import OUTPUT_DIR
from app.schemas import ConvertRequest
from app.services.docx_service import MarkdownToDocxService

app = FastAPI(title="Markdown DOCX local converter", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

converter = MarkdownToDocxService()


@app.get("/api/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/convert")
def convert_documents(payload: ConvertRequest):
    if not payload.files:
        raise HTTPException(status_code=400, detail="No Markdown input files were provided.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(payload.files, key=lambda item: item.relative_path or item.name)
    results: list[dict[str, str]] = []
    generated_paths: list[Path] = []

    if payload.mode == "individual":
        for file in files:
            output_name = safe_output_name(file.name)
            output_path = OUTPUT_DIR / output_name
            converter.convert_file(
                file.content,
                output_path,
                Path(file.name).stem,
                include_cover=payload.include_cover,
                include_toc=payload.include_toc,
                page_breaks=payload.page_breaks,
            )
            generated_paths.append(output_path)
            results.append({"name": output_name, "download_url": f"/api/download?file_name={quote(output_name)}"})
    elif payload.mode == "consolidated":
        document_name = payload.document_name or "markdown-report"
        output_name = safe_output_name(document_name)
        output_path = OUTPUT_DIR / output_name
        document_sections = [(Path(file.name).stem or "Sección", file.content) for file in files]
        converter.convert_many(
            document_sections,
            output_path,
            document_name,
            include_cover=payload.include_cover,
            include_toc=payload.include_toc,
            page_breaks=payload.page_breaks,
        )
        generated_paths.append(output_path)
        results.append({"name": output_name, "download_url": f"/api/download?file_name={quote(output_name)}"})
    else:
        grouped: dict[str, list] = {}
        for file in files:
            group_name = Path(file.relative_path or file.name).parent.as_posix() if (file.relative_path or file.name) else "root"
            grouped.setdefault(group_name or "root", []).append(file)

        for group_key, group_files in grouped.items():
            folder_name = Path(group_key).name if group_key not in {"", ".", "root"} else payload.document_name or "grouped-report"
            output_name = safe_output_name(folder_name)
            output_path = OUTPUT_DIR / output_name
            document_sections = [(Path(file.name).stem or "Sección", file.content) for file in group_files]
            converter.convert_many(
                document_sections,
                output_path,
                folder_name,
                include_cover=payload.include_cover,
                include_toc=payload.include_toc,
                page_breaks=payload.page_breaks,
            )
            generated_paths.append(output_path)
            results.append({"name": output_name, "download_url": f"/api/download?file_name={quote(output_name)}"})

    if len(generated_paths) > 1:
        zip_name = f"{(payload.document_name or 'markdown-report').strip() or 'markdown-report'}.zip"
        zip_path = OUTPUT_DIR / zip_name
        with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
            for path in generated_paths:
                archive.write(path, arcname=path.name)
        results.append({"name": zip_name, "download_url": f"/api/download?file_name={quote(zip_name)}"})

    return {"success": True, "results": results}


@app.get("/api/download")
def download_document(file_name: str = Query(..., min_length=1)):
    candidate = (OUTPUT_DIR / file_name).resolve()
    if not str(candidate).startswith(str(OUTPUT_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid requested file.")
    if not candidate.exists() or not candidate.is_file():
        raise HTTPException(status_code=404, detail="Requested document is not available.")

    is_zip = candidate.suffix.lower() == ".zip"
    media_type = (
        "application/zip"
        if is_zip
        else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    return FileResponse(
        candidate,
        media_type=media_type,
        filename=candidate.name,
    )


def safe_output_name(value: str) -> str:
    cleaned = Path(value).stem.strip()
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "-" for ch in cleaned)
    return (cleaned or "markdown-report") + ".docx"
