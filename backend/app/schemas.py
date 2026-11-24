from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MarkdownFile(BaseModel):
    name: str = Field(..., min_length=1)
    content: str = ""
    relative_path: str = ""
    size: int = 0


class ConvertRequest(BaseModel):
    files: list[MarkdownFile] = Field(default_factory=list)
    mode: Literal["individual", "consolidated", "grouped"] = "individual"
    document_name: str = "markdown-report"
    include_cover: bool = False
    include_toc: bool = False
    page_breaks: bool = True
    sort_order: Literal["as-selected", "alphabetical"] = "as-selected"
