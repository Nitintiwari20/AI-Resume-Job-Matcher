import io
import re
from typing import Dict, Any, List
import pypdf
import docx

class TextPreprocessor:
    """
    Data cleaning and text preprocessing utility module.
    Handles text normalization, stopword removal, contact detail extraction,
    and document text extraction from PDF, DOCX, and TXT files.
    """
    def __init__(self):
        self.email_regex = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
        self.phone_regex = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
        self.linkedin_regex = re.compile(r'linkedin\.com/in/[a-zA-Z0-9_-]+', re.IGNORECASE)
        self.github_regex = re.compile(r'github\.com/[a-zA-Z0-9_-]+', re.IGNORECASE)

    def clean_text(self, text: str) -> str:
        """Clean raw text: remove special characters, extra whitespaces, normalize spacing."""
        if not text:
            return ""
        # Replace newlines and tabs with spaces
        text_clean = re.sub(r'[\r\n\t]+', ' ', text)
        # Remove non-ASCII weird characters while keeping standard punctuation & code symbols (+, #)
        text_clean = re.sub(r'[^\x00-\x7F]+', ' ', text_clean)
        # Collapse multiple spaces
        text_clean = re.sub(r'\s+', ' ', text_clean).strip()
        return text_clean

    def extract_text_from_file(self, file_bytes: bytes, filename: str) -> str:
        """Extract text from uploaded PDF, DOCX, or TXT file."""
        fname_lower = filename.lower()
        if fname_lower.endswith(".pdf"):
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            extracted = [page.extract_text() for page in reader.pages if page.extract_text()]
            raw = "\n".join(extracted)
        elif fname_lower.endswith(".docx"):
            docx_file = io.BytesIO(file_bytes)
            doc = docx.Document(docx_file)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            raw = "\n".join(paragraphs)
        else:
            raw = file_bytes.decode("utf-8", errors="ignore")

        return self.clean_text(raw)

    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract email, phone, linkedin, and github handles."""
        emails = self.email_regex.findall(text)
        linkedin = self.linkedin_regex.findall(text)
        github = self.github_regex.findall(text)
        phones = [p.group(0) for p in self.phone_regex.finditer(text)]

        return {
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "linkedin": f"https://{linkedin[0]}" if linkedin else None,
            "github": f"https://{github[0]}" if github else None
        }

    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract structural sections from resume text."""
        sections = {
            "summary": "",
            "skills": "",
            "experience": "",
            "education": "",
            "projects": ""
        }
        heading_patterns = {
            "summary": r"(?:summary|profile|about me|objective)",
            "skills": r"(?:skills|technical skills|technologies)",
            "experience": r"(?:experience|work experience|employment history)",
            "education": r"(?:education|academic background)",
            "projects": r"(?:projects|key projects)"
        }

        lines = text.splitlines()
        current_section = "summary"
        buffers = {k: [] for k in sections.keys()}

        for line in lines:
            stripped = line.strip().lower()
            matched = None
            if len(stripped) < 40:
                for sec_name, pattern in heading_patterns.items():
                    if re.search(r'^\s*#*\s*' + pattern + r'\s*:?$', stripped, re.IGNORECASE):
                        matched = sec_name
                        break
            if matched:
                current_section = matched
            else:
                buffers[current_section].append(line)

        for k in sections.keys():
            sections[k] = " ".join(buffers[k]).strip()

        return sections
