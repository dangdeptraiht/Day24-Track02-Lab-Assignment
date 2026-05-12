from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpArtifacts, NlpEngine
import spacy


class BlankVietnameseNlpEngine(NlpEngine):
    """Minimal Vietnamese NLP engine for regex/pattern recognizers."""

    engine_name = "blank_vi"

    def __init__(self):
        self.nlp = {"vi": spacy.blank("vi", config={"nlp": {"tokenizer": {"use_pyvi": False}}})}

    def load(self) -> None:
        return None

    def is_loaded(self) -> bool:
        return True

    def process_text(self, text: str, language: str) -> NlpArtifacts:
        doc = self.nlp[language](text)
        return NlpArtifacts(
            entities=[],
            tokens=doc,
            tokens_indices=[token.idx for token in doc],
            lemmas=[token.text.lower() for token in doc],
            nlp_engine=self,
            language=language,
        )

    def process_batch(self, texts, language: str, batch_size: int = 1, n_process: int = 1, **kwargs):
        for text in texts:
            yield text, self.process_text(text, language)

    def is_stopword(self, word: str, language: str) -> bool:
        return False

    def is_punct(self, word: str, language: str) -> bool:
        return all(char in ".,;:!?()[]{}'\"-/\\" for char in word)

    def get_supported_entities(self):
        return []

    def get_supported_languages(self):
        return ["vi"]

def build_vietnamese_analyzer() -> AnalyzerEngine:
    """Build AnalyzerEngine with Vietnamese custom recognizers."""
    cccd_pattern = Pattern(
        name="cccd_pattern",
        regex=r"\b\d{11,12}\b",
        score=0.9
    )
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        supported_language="vi",
        patterns=[cccd_pattern],
        context=["cccd", "căn cước", "chứng minh", "cmnd"]
    )

    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        supported_language="vi",
        patterns=[Pattern(
            name="vn_phone",
            regex=r"\b(?:0[35789]\d{8}|[35789]\d{8})\b",
            score=0.85
        )],
        context=["điện thoại", "sdt", "phone", "liên hệ"]
    )

    person_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        supported_language="vi",
        patterns=[Pattern(
            name="vn_person_name",
            regex=r"\b(?:Ông|Bà|Cô|Chị|Anh|ThS\.?|BS\.?)?\s*[A-ZÀ-Ỵ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỵ][a-zà-ỹ]+){1,3}\b",
            score=0.75
        )],
        context=["bệnh nhân", "họ tên", "bac si", "bác sĩ"]
    )

    analyzer = AnalyzerEngine(
        nlp_engine=BlankVietnameseNlpEngine(),
        supported_languages=["vi"],
    )
    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(person_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """Detect Vietnamese PII in free text."""
    results = analyzer.analyze(
        text=str(text),
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
    )
    return results
