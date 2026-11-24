from __future__ import annotations

import copy
import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Inches, Pt, RGBColor


class MarkdownToDocxService:
    def convert_file(
        self,
        markdown_text: str,
        output_path: str | Path,
        title: str,
        *,
        include_cover: bool = False,
        include_toc: bool = False,
        page_breaks: bool = True,
        base_dir: str | Path | None = None,
    ) -> str:
        return self.convert_many(
            [(title, markdown_text)],
            output_path,
            title,
            include_cover=include_cover,
            include_toc=include_toc,
            page_breaks=page_breaks,
            base_dir=base_dir,
        )

    def convert_many(
        self,
        items: list[tuple[str, str]],
        output_path: str | Path,
        title: str,
        *,
        include_cover: bool = False,
        include_toc: bool = False,
        page_breaks: bool = True,
        base_dir: str | Path | None = None,
    ) -> str:
        document = Document()
        self._set_page_margins(document)
        self._apply_global_styles(document)

        if include_cover:
            self._add_cover_page(document, title, len(items))

        if include_toc:
            self._add_toc(document, items)

        for idx, (section_title, markdown_text) in enumerate(items):
            section_name = (section_title or "Sección").strip() or "Sección"
            if idx > 0 and page_breaks:
                document.add_page_break()

            first_non_empty = next((line.strip() for line in markdown_text.splitlines() if line.strip()), "")
            has_h1 = re.match(r"^#\s+", first_non_empty) is not None

            # Only add section title as H1 if the markdown doesn't already provide an H1 title
            if len(items) > 1 and not has_h1:
                h = document.add_heading(section_name, level=1)
                h.paragraph_format.keep_with_next = True
            elif len(items) == 1 and not has_h1:
                h = document.add_heading(section_name, level=1)
                h.paragraph_format.keep_with_next = True

            self._add_markdown_content(document, markdown_text, base_dir=base_dir)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        document.save(str(output_path))
        return str(output_path)

    def _set_page_margins(self, document: Document) -> None:
        for section in document.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

    def _apply_global_styles(self, document: Document) -> None:
        styles = document.styles

        # Normal style
        if "Normal" in styles:
            normal = styles["Normal"]
            normal.font.name = "Calibri"
            normal.font.size = Pt(10.5)
            normal.font.color.rgb = RGBColor(30, 41, 59)  # Slate dark #1E293B
            normal.paragraph_format.space_after = Pt(4)
            normal.paragraph_format.line_spacing = 1.15

        # Headings styling
        heading_configs = [
            ("Heading 1", Pt(18), RGBColor(30, 58, 138), Pt(16), Pt(6)),  # Deep Navy #1E3A8A
            ("Heading 2", Pt(14), RGBColor(37, 99, 235), Pt(14), Pt(4)),  # Royal Blue #2563EB
            ("Heading 3", Pt(12), RGBColor(51, 65, 85), Pt(10), Pt(3)),   # Slate #334155
            ("Heading 4", Pt(11), RGBColor(71, 85, 105), Pt(8), Pt(2)),   # Light Slate #475569
        ]
        for style_name, size, color, before, after in heading_configs:
            if style_name in styles:
                h = styles[style_name]
                h.font.name = "Calibri"
                h.font.size = size
                h.font.bold = True
                h.font.color.rgb = color
                h.paragraph_format.space_before = before
                h.paragraph_format.space_after = after
                h.paragraph_format.keep_with_next = True

    def _add_cover_page(self, document: Document, title: str, section_count: int) -> None:
        p_top = document.add_paragraph()
        p_top.paragraph_format.space_before = Pt(90)

        cover = document.add_paragraph()
        cover.paragraph_format.space_after = Pt(8)
        run = cover.add_run(title.strip() or "Reporte de Documentación")
        run.bold = True
        run.font.size = Pt(28)
        run.font.color.rgb = RGBColor(30, 58, 138)

        sub = document.add_paragraph()
        sub.paragraph_format.space_after = Pt(20)
        sub_run = sub.add_run("Documento técnico generado automáticamente")
        sub_run.font.size = Pt(12)
        sub_run.font.color.rgb = RGBColor(100, 116, 139)

        p_bar = document.add_paragraph()
        p_bar.paragraph_format.space_after = Pt(30)
        bar_xml = parse_xml(f"""
            <w:pBdr {nsdecls("w")}>
                <w:bottom w:val="single" w:sz="18" w:space="1" w:color="2563EB"/>
            </w:pBdr>
        """)
        p_bar._p.get_or_add_pPr().append(bar_xml)

        meta = document.add_paragraph()
        meta.paragraph_format.space_after = Pt(3)
        r_l = meta.add_run("Fecha de emisión: ")
        r_l.bold = True
        r_l.font.size = Pt(9.5)
        r_l.font.color.rgb = RGBColor(71, 85, 105)
        r_v = meta.add_run(datetime.now().strftime("%Y-%m-%d %H:%M"))
        r_v.font.size = Pt(9.5)
        r_v.font.color.rgb = RGBColor(71, 85, 105)

        document.add_page_break()

    def _add_toc(self, document: Document, items: list[tuple[str, str]]) -> None:
        toc_heading = document.add_heading("Índice de contenido", level=1)
        toc_heading.paragraph_format.space_after = Pt(12)

        for sec_name, sec_md in items:
            h1_match = re.search(r"^#\s+(.+)$", sec_md, re.MULTILINE)
            display_name = h1_match.group(1).strip() if h1_match else sec_name
            p = document.add_paragraph(style="List Bullet")
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(display_name)
            r.font.color.rgb = RGBColor(30, 58, 138)

        document.add_page_break()

    def _add_markdown_content(self, document: Document, markdown_text: str, *, base_dir: str | Path | None = None) -> None:
        base_dir = Path(base_dir) if base_dir else None
        lines = markdown_text.splitlines()
        index = 0

        while index < len(lines):
            line = lines[index].rstrip()
            stripped = line.strip()

            if not stripped:
                index += 1
                continue

            if stripped.startswith("```"):
                index = self._add_code_block(document, lines, index)
                continue

            heading_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
            if heading_match:
                heading_text = heading_match.group(2).strip()
                level = min(len(heading_match.group(1)), 6)
                h = document.add_heading(level=level)
                h.paragraph_format.keep_with_next = True
                self._append_inline_runs(h, heading_text)
                index += 1
                continue

            if re.match(r"^---\s*$|^___\s*$|^\*\*\*\s*$", stripped):
                self._add_horizontal_rule(document)
                index += 1
                continue

            if re.match(r"^>\s?", stripped):
                block_lines = []
                while index < len(lines) and re.match(r"^>\s?", lines[index].strip()):
                    block_text = lines[index].strip()
                    block_lines.append(block_text[1:].strip() if block_text.startswith(">") else block_text.strip())
                    index += 1
                quote_text = " ".join(block_lines).strip()
                self._add_blockquote(document, quote_text)
                continue

            if self._looks_like_table(lines, index):
                rows, alignments, new_index = self._consume_table(lines, index)
                if rows:
                    self._add_table(document, rows, alignments)
                index = new_index
                continue

            if re.match(r"^\d+\.\s+", stripped):
                items = []
                while index < len(lines) and re.match(r"^\d+\.\s+", lines[index].strip()):
                    num_match = re.match(r"^\d+\.\s+(.*)$", lines[index].strip())
                    items.append(num_match.group(1).strip() if num_match else lines[index].strip())
                    index += 1
                for item in items:
                    p = document.add_paragraph(style="List Number")
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.15
                    self._append_inline_runs(p, item)
                continue

            if re.match(r"^(?:[-*+])\s+", stripped):
                items = []
                while index < len(lines) and re.match(r"^(?:[-*+])\s+", lines[index].strip()):
                    bullet_match = re.match(r"^(?:[-*+])\s+(.*)$", lines[index].strip())
                    items.append(bullet_match.group(1).strip() if bullet_match else lines[index].strip())
                    index += 1
                for item in items:
                    p = document.add_paragraph(style="List Bullet")
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.15
                    self._append_inline_runs(p, item)
                continue

            if re.match(r"^!\[.*?\]\((.*?)\)\s*$", stripped):
                image_match = re.match(r"^!\[.*?\]\((.*?)\)\s*$", stripped)
                if image_match:
                    self._add_image(document, image_match.group(1), base_dir)
                    index += 1
                    continue

            # Standard paragraph
            paragraph_lines = []
            while index < len(lines):
                current = lines[index].rstrip()
                current_stripped = current.strip()
                if not current_stripped:
                    break
                if (
                    current_stripped.startswith("```")
                    or re.match(r"^(#{1,6})\s+", current_stripped)
                    or re.match(r"^(?:[-*+]|\d+\.)\s+", current_stripped)
                    or re.match(r"^>\s?", current_stripped)
                    or re.match(r"^---\s*$|^___\s*$|^\*\*\*\s*$", current_stripped)
                    or self._looks_like_table(lines, index)
                ):
                    break
                paragraph_lines.append(current_stripped)
                index += 1

            paragraph_text = " ".join(paragraph_lines).strip()
            if paragraph_text:
                p = document.add_paragraph()
                self._append_inline_runs(p, paragraph_text)

        if not document.paragraphs and not document.tables:
            document.add_paragraph("Sin contenido disponible.")

    def _is_table_separator(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped or "|" not in stripped:
            return False
        parts = stripped.strip("|").split("|")
        return len(parts) > 0 and all(re.match(r"^\s*:?-+:?\s*$", part) for part in parts)

    def _looks_like_table(self, lines: list[str], index: int) -> bool:
        if index >= len(lines):
            return False
        current = lines[index].strip()
        if "|" not in current:
            return False
        if self._is_table_separator(current):
            return True
        if index + 1 < len(lines) and self._is_table_separator(lines[index + 1]):
            return True
        return False

    def _consume_table(self, lines: list[str], index: int) -> tuple[list[list[str]], list[str], int]:
        rows: list[list[str]] = []
        alignments: list[str] = []

        current = lines[index].strip()
        if self._is_table_separator(current):
            index += 1
            return rows, alignments, index

        header_cells = [c.strip() for c in current.strip("|").split("|")]
        rows.append(header_cells)
        index += 1

        if index < len(lines) and self._is_table_separator(lines[index]):
            sep_parts = lines[index].strip().strip("|").split("|")
            for part in sep_parts:
                part = part.strip()
                if part.startswith(":") and part.endswith(":"):
                    alignments.append("center")
                elif part.endswith(":"):
                    alignments.append("right")
                else:
                    alignments.append("left")
            index += 1

        while index < len(lines):
            line = lines[index].rstrip()
            stripped = line.strip()
            if not stripped or "|" not in stripped:
                break
            if self._is_table_separator(stripped):
                index += 1
                continue
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            rows.append(cells)
            index += 1

        return rows, alignments, index

    def _add_table(self, document: Document, rows: list[list[str]], alignments: list[str] | None = None) -> None:
        if not rows:
            return

        alignments = alignments or []
        cols_count = max(len(row) for row in rows)
        if cols_count == 0:
            return

        normalized_rows: list[list[str]] = []
        for r in rows:
            padded = r + [""] * (cols_count - len(r))
            normalized_rows.append(padded)

        table = document.add_table(rows=0, cols=cols_count)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        # Table cell padding (dxa: 20 dxa = 1 pt)
        cell_margins = parse_xml(f"""
            <w:tblCellMar {nsdecls("w")}>
                <w:top w:w="120" w:type="dxa"/>
                <w:bottom w:w="120" w:type="dxa"/>
                <w:left w:w="160" w:type="dxa"/>
                <w:right w:w="160" w:type="dxa"/>
            </w:tblCellMar>
        """)
        table._tbl.tblPr.append(cell_margins)

        # Subtle slate borders
        borders = parse_xml(f"""
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/>
                <w:bottom w:val="single" w:sz="8" w:space="0" w:color="CBD5E1"/>
                <w:left w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                <w:insideH w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                <w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
            </w:tblBorders>
        """)
        table._tbl.tblPr.append(borders)

        # Calculate proportional column widths
        col_lens = [0] * cols_count
        for row in normalized_rows:
            for c_idx in range(cols_count):
                col_lens[c_idx] = max(col_lens[c_idx], len(row[c_idx]))
        col_lens = [max(l, 4) for l in col_lens]
        sum_lens = sum(col_lens)
        total_width_inches = 6.5
        col_widths = [Inches(max(0.6, total_width_inches * (l / sum_lens))) for l in col_lens]

        # Template shading elements for fast cloning
        shd_header = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E3A8A"/>')
        shd_odd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
        shd_even = parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFFFFF"/>')

        # Fill table cells using add_row for high performance (O(N) instead of O(N^2))
        for row_idx, row_data in enumerate(normalized_rows):
            is_header = (row_idx == 0)
            row = table.add_row()

            trPr = row._tr.get_or_add_trPr()
            trPr.append(OxmlElement("w:cantSplit"))
            if is_header:
                trPr.append(OxmlElement("w:tblHeader"))

            shd_template = shd_header if is_header else (shd_odd if row_idx % 2 == 1 else shd_even)

            for col_idx, cell_value in enumerate(row_data):
                cell = row.cells[col_idx]
                cell.width = col_widths[col_idx]
                cell._tc.get_or_add_tcPr().append(copy.deepcopy(shd_template))

                p = cell.paragraphs[0]
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.15

                align_str = alignments[col_idx] if col_idx < len(alignments) else "left"
                if align_str == "center":
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif align_str == "right":
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

                self._append_inline_runs(p, cell_value, is_header=is_header)

        after_p = document.add_paragraph()
        after_p.paragraph_format.space_before = Pt(2)
        after_p.paragraph_format.space_after = Pt(4)

    def _add_code_block(self, document: Document, lines: list[str], start_index: int) -> int:
        code_lines: list[str] = []
        index = start_index + 1
        while index < len(lines) and not lines[index].strip().startswith("```"):
            code_lines.append(lines[index])
            index += 1
        if index < len(lines):
            index += 1

        table = document.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        cell.width = Inches(6.5)

        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
        cell._tc.get_or_add_tcPr().append(shd)

        borders = parse_xml(f"""
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
                <w:left w:val="single" w:sz="20" w:space="0" w:color="2563EB"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>
            </w:tblBorders>
        """)
        table._tbl.tblPr.append(borders)

        cell_margins = parse_xml(f"""
            <w:tblCellMar {nsdecls("w")}>
                <w:top w:w="120" w:type="dxa"/>
                <w:bottom w:w="120" w:type="dxa"/>
                <w:left w:w="180" w:type="dxa"/>
                <w:right w:w="180" w:type="dxa"/>
            </w:tblCellMar>
        """)
        table._tbl.tblPr.append(cell_margins)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run("\n".join(code_lines))
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(15, 23, 42)

        after_p = document.add_paragraph()
        after_p.paragraph_format.space_before = Pt(2)
        after_p.paragraph_format.space_after = Pt(4)
        return index

    def _add_blockquote(self, document: Document, text: str) -> None:
        p = document.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15

        pBdr = parse_xml(f"""
            <w:pBdr {nsdecls("w")}>
                <w:left w:val="single" w:sz="18" w:space="10" w:color="2563EB"/>
            </w:pBdr>
        """)
        p._p.get_or_add_pPr().append(pBdr)
        self._append_inline_runs(p, text, is_quote=True)

    def _add_horizontal_rule(self, document: Document) -> None:
        p = document.add_paragraph()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        pBdr = parse_xml(f"""
            <w:pBdr {nsdecls("w")}>
                <w:bottom w:val="single" w:sz="8" w:space="1" w:color="CBD5E1"/>
            </w:pBdr>
        """)
        p._p.get_or_add_pPr().append(pBdr)

    def _add_image(self, document: Document, image_source: str, base_dir: str | Path | None) -> None:
        candidate = image_source.strip("\"'")
        if not candidate:
            return
        candidate_path = (Path(base_dir) / candidate).resolve() if base_dir else Path(candidate).resolve()
        if candidate_path.exists() and candidate_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}:
            try:
                p = document.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.add_run().add_picture(str(candidate_path), width=Inches(5.0))
            except Exception:
                document.add_paragraph(f"[Imagen: {candidate}]")
        else:
            document.add_paragraph(f"[Imagen no disponible: {candidate}]")

    def _append_inline_runs(self, paragraph, text: str, *, is_header: bool = False, is_quote: bool = False) -> None:
        text = text.strip()
        if not text:
            return

        tokens = re.split(r"(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|~~[^~]+~~|\[[^\]]+\]\([^\)]+\))", text)
        for token in tokens:
            if not token:
                continue

            # Code pill `...`
            if token.startswith("`") and token.endswith("`") and len(token) >= 2:
                run = paragraph.add_run(token[1:-1])
                run.font.name = "Consolas"
                run.font.size = Pt(9.0 if is_header else 9.5)
                run.bold = True
                if is_header:
                    run.font.color.rgb = RGBColor(255, 255, 255)
                else:
                    run.font.color.rgb = RGBColor(15, 23, 42)
                continue

            # Bold **...**
            if token.startswith("**") and token.endswith("**") and len(token) >= 4:
                run = paragraph.add_run(token[2:-2])
                run.bold = True
                if is_header:
                    run.font.color.rgb = RGBColor(255, 255, 255)
                    run.font.size = Pt(10)
                elif is_quote:
                    run.font.color.rgb = RGBColor(71, 85, 105)
                continue

            # Strikethrough ~~...~~
            if token.startswith("~~") and token.endswith("~~") and len(token) >= 4:
                run = paragraph.add_run(token[2:-2])
                run.font.strike = True
                if is_header:
                    run.font.color.rgb = RGBColor(255, 255, 255)
                continue

            # Italic *...*
            if token.startswith("*") and token.endswith("*") and not token.startswith("**") and len(token) >= 2:
                run = paragraph.add_run(token[1:-1])
                run.italic = True
                if is_header:
                    run.font.color.rgb = RGBColor(255, 255, 255)
                continue

            # Link [text](url)
            link_match = re.match(r"^\[([^\]]+)\]\(([^)]+)\)$", token)
            if link_match:
                label, _ = link_match.groups()
                run = paragraph.add_run(label)
                run.font.underline = True
                run.font.color.rgb = RGBColor(37, 99, 235)
                continue

            # Normal text
            run = paragraph.add_run(token)
            if is_header:
                run.bold = True
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(255, 255, 255)
            elif is_quote:
                run.italic = True
                run.font.color.rgb = RGBColor(71, 85, 105)
