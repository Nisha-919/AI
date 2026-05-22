from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from PyPDF2 import PdfReader


class ScreenUnderstanding:
    def __init__(self):
        self._ocr_available = False
        try:
            import pytesseract  # noqa: F401

            self._ocr_available = True
        except Exception:
            self._ocr_available = False

    def extract_text_from_image(self, image_path: Path) -> str:
        if not self._ocr_available:
            return "OCR engine install nahi hai."
        try:
            import pytesseract

            image = cv2.imread(str(image_path))
            if image is None:
                return "Image read nahi ho paayi."
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            denoised = cv2.GaussianBlur(gray, (3, 3), 0)
            _, th = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            text = pytesseract.image_to_string(th)
            return text.strip() or "Koi text detect nahi hua."
        except Exception as exc:
            return f"OCR error: {exc}"

    @staticmethod
    def summarize_text(text: str, max_lines: int = 5) -> str:
        if not text.strip():
            return "Summarize karne ke liye text nahi mila."
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) <= max_lines:
            return "\n".join(lines)
        return "\n".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} aur lines)"

    @staticmethod
    def read_pdf(pdf_path: Path, max_pages: int = 5) -> str:
        try:
            reader = PdfReader(str(pdf_path))
            extracted = []
            for page in reader.pages[:max_pages]:
                extracted.append(page.extract_text() or "")
            return "\n".join(extracted).strip() or "PDF me readable text nahi mila."
        except Exception as exc:
            return f"PDF read error: {exc}"

    def summarize_pdf(self, pdf_path: Path) -> str:
        return self.summarize_text(self.read_pdf(pdf_path), max_lines=10)

    @staticmethod
    def active_window_title() -> Optional[str]:
        try:
            import win32gui

            handle = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(handle) or None
        except Exception:
            return None

    @staticmethod
    def detect_code_likelihood(text: str) -> float:
        indicators = ["def ", "class ", "{", "}", "import ", "public ", "return "]
        hits = sum(1 for token in indicators if token in text)
        return min(1.0, hits / len(indicators))

    @staticmethod
    def image_embedding(image_path: Path) -> Optional[np.ndarray]:
        image = cv2.imread(str(image_path))
        if image is None:
            return None
        resized = cv2.resize(image, (64, 64))
        hist = cv2.calcHist([resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
        normalized = cv2.normalize(hist, hist).flatten()
        return normalized
