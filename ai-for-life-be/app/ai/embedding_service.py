from typing import List
from functools import lru_cache

try:
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore


MODEL_NAME = "intfloat/multilingual-e5-large"


@lru_cache(maxsize=1)
def _get_model():
    if SentenceTransformer is None:
        raise RuntimeError("sentence-transformers is not installed. Please install to use embeddings.")
    return SentenceTransformer(MODEL_NAME)


def _normalize_text(s: str) -> str:
    return (s or "").strip().lower()


def build_jd_text(title: str | None, company: str | None, location: str | None, description: str | None, experience_min: int | None, skills: List[str]) -> str:
    t = _normalize_text(title or "")
    c = _normalize_text(company or "")
    loc = _normalize_text(location or "")
    desc = (description or "").strip()
    desc = desc[:1000]
    sk = sorted({(s or "").strip().lower() for s in skills if (s or "").strip()})
    lines = [
        f"title: {t}" if t else "",
        f"skills: {', '.join(sk)}" if sk else "",
        f"experience_min: {int(experience_min)}" if (isinstance(experience_min, int) and experience_min >= 0) else "",
        f"location: {loc}" if loc else "",
        f"company: {c}" if c else "",
        f"description: {desc}" if desc else "",
    ]
    return "\n".join([l for l in lines if l])


def build_query_text(title: str | None, skills: List[str], experience: int | None, location: str | None) -> str:
    t = _normalize_text(title or "")
    loc = _normalize_text(location or "")
    sk = sorted({(s or "").strip().lower() for s in skills if (s or "").strip()})
    lines = [
        f"title: {t}" if t else "",
        f"skills: {', '.join(sk)}" if sk else "",
        f"experience: {int(experience)}" if (isinstance(experience, int) and experience >= 0) else "",
        f"location: {loc}" if loc else "",
    ]
    return "\n".join([l for l in lines if l])


def get_text_embedding(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return []
    model = _get_model()
    # E5 expects query/doc prefixes for better performance; here we embed docs/JDs
    input_text = f"passage: {text}"
    vec = model.encode(input_text, normalize_embeddings=True)
    return [float(x) for x in vec.tolist()]

def get_query_embedding(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return []
    model = _get_model()
    input_text = f"query: {text}"
    vec = model.encode(input_text, normalize_embeddings=True)
    return [float(x) for x in vec.tolist()]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    # vectors are normalized already; dot product equals cosine
    return float(sum(x * y for x, y in zip(a, b)))
