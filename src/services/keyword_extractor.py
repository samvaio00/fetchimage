"""Extract keywords from SKU names for image searching."""

import re
from typing import List
from src.utils.logger import LoggerMixin


class KeywordExtractor(LoggerMixin):
    """Extract searchable keywords from SKU names."""

    STOPWORDS = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
    
    ABBREVIATIONS = {
        "l": "large", "m": "medium", "s": "small", "xl": "extra large",
        "xxl": "double extra large", "xs": "extra small",
        "blu": "blue", "blk": "black", "wht": "white", "grn": "green",
        "rd": "red", "org": "orange", "ylw": "yellow",
        "mens": "men", "womens": "women", "kids": "children",
        "pc": "piece", "pcs": "pieces", "pkg": "package",
        "in": "inch", "ft": "feet", "cm": "centimeter"
    }

    def __init__(self, min_length: int = 3, max_keywords: int = 5,
                 remove_numbers: bool = False, expand_abbreviations: bool = True):
        """Initialize keyword extractor."""
        self.min_length = min_length
        self.max_keywords = max_keywords
        self.remove_numbers = remove_numbers
        self.expand_abbreviations = expand_abbreviations

    def extract_keywords(self, sku_name: str) -> List[str]:
        """Extract keywords from SKU name."""
        self.logger.debug(f"Extracting keywords from: {sku_name}")
        
        cleaned = self.clean_text(sku_name)
        words = self.split_words(cleaned)
        words = self.remove_stopwords(words)
        
        if self.expand_abbreviations:
            words = [self.expand_abbreviation(w) for w in words]
        
        if self.remove_numbers:
            words = [w for w in words if not w.isdigit()]
        
        words = [w for w in words if len(w) >= self.min_length]
        keywords = words[:self.max_keywords]
        
        self.logger.debug(f"Extracted keywords: {keywords}")
        return keywords

    def clean_text(self, text: str) -> str:
        """Clean text by removing special characters."""
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s\-_]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def split_words(self, text: str) -> List[str]:
        """Split text into words using delimiters."""
        words = re.split(r'[-_\s]+', text)
        return [w for w in words if w]

    def remove_stopwords(self, words: List[str]) -> List[str]:
        """Remove common stopwords."""
        return [w for w in words if w.lower() not in self.STOPWORDS]

    def expand_abbreviation(self, word: str) -> str:
        """Expand common abbreviations."""
        return self.ABBREVIATIONS.get(word.lower(), word)
