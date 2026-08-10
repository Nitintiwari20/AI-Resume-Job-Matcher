import io
import re
from typing import Dict, Any, List
import pypdf
import docx

class ResumeParser:
    def __init__(self):
        self.email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        self.phone_regex = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_regex = re.compile(r'linkedin\.com/in/[a-zA-Z0-9_-]+', re.IGNORECASE)
        self.github_regex = re.compile(r'github\.com/[a-zA-Z0-9_-]+', re.IGNORECASE)

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        text_content = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_content.append(extracted)
        return "\n".join(text_content)

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        docx_file = io.BytesIO(file_bytes)
        doc = docx.Document(docx_file)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_data:
                    full_text.append(" | ".join(row_data))
        return "\n".join(full_text)

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        emails = self.email_regex.findall(text)
        phones = self.phone_regex.findall(text)
        linkedin = self.linkedin_regex.findall(text)
        github = self.github_regex.findall(text)

        # Phone matches might return tuples if group regex is used
        phone_matches = []
        for p in self.phone_regex.finditer(text):
            phone_matches.append(p.group(0))

        return {
            "email": emails[0] if emails else None,
            "phone": phone_matches[0] if phone_matches else None,
            "linkedin": f"https://{linkedin[0]}" if linkedin else None,
            "github": f"https://{github[0]}" if github else None
        }

    def extract_sections(self, text: str) -> Dict[str, str]:
        sections = {
            "summary": "",
            "skills": "",
            "experience": "",
            "education": "",
            "projects": "",
            "certifications": ""
        }

        # Common headings
        heading_patterns = {
            "summary": r"(?:summary|profile|about me|objective)",
            "skills": r"(?:skills|technical skills|core competencies|technologies)",
            "experience": r"(?:experience|work experience|employment history|work history)",
            "education": r"(?:education|academic background|qualifications)",
            "projects": r"(?:projects|key projects|personal projects)",
            "certifications": r"(?:certifications|licenses|courses)"
        }

        lines = text.splitlines()
        current_section = "summary"
        section_buffers = {k: [] for k in sections.keys()}

        for line in lines:
            stripped = line.strip().lower()
            # Check if line looks like a section header
            matched_header = None
            if len(stripped) < 40:
                for section_name, pattern in heading_patterns.items():
                    if re.search(r'^\s*#*\s*' + pattern + r'\s*:?$', stripped, re.IGNORECASE):
                        matched_header = section_name
                        break
            
            if matched_header:
                current_section = matched_header
            else:
                section_buffers[current_section].append(line)

        for k in sections.keys():
            sections[k] = "\n".join(section_buffers[k]).strip()

        return sections

    def parse(self, text_or_bytes: str | bytes, filename: str = "") -> Dict[str, Any]:
        if isinstance(text_or_bytes, bytes):
            if filename.lower().endswith(".pdf"):
                raw_text = self.extract_text_from_pdf(text_or_bytes)
            elif filename.lower().endswith(".docx"):
                raw_text = self.extract_text_from_docx(text_or_bytes)
            else:
                raw_text = text_or_bytes.decode("utf-8", errors="ignore")
        else:
            raw_text = text_or_bytes

        contact = self.extract_contact_info(raw_text)
        sections = self.extract_sections(raw_text)

        # Estimate total word count & reading time
        words = raw_text.split()
        word_count = len(words)

        return {
            "raw_text": raw_text,
            "word_count": word_count,
            "contact": contact,
            "sections": sections
        }
