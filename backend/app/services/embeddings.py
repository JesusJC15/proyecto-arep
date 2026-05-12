from __future__ import annotations

from abc import ABC, abstractmethod
import hashlib
import math
import re
import unicodedata

import httpx


TOKEN_PATTERN = re.compile(r"[a-z0-9]{2,}")
SYNONYM_MAP = {
    "pecho": ["chest"],
    "toracico": ["chest"],
    "dolor": ["pain"],
    "molestia": ["pain"],
    "respirar": ["breathing"],
    "respiracion": ["breathing"],
    "tos": ["cough"],
    "fiebre": ["fever"],
    "desmayo": ["fainting"],
    "confusion": ["confusion"],
    "mareo": ["dizziness"],
    "fatiga": ["fatigue"],
    "presion": ["pressure"],
    "empeora": ["worsening"],
    "worsening": ["rapid", "worsening"],
    "breath": ["breathing"],
    "shortness": ["breathing"],
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.lower())
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    return ascii_text


def tokenize_text(value: str) -> list[str]:
    normalized = normalize_text(value)
    base_tokens = TOKEN_PATTERN.findall(normalized)
    expanded: list[str] = []
    for token in base_tokens:
        expanded.append(token)
        expanded.extend(SYNONYM_MAP.get(token, ()))
    if len(base_tokens) >= 2:
        expanded.extend(f"{left}_{right}" for left, right in zip(base_tokens, base_tokens[1:]))
    return expanded


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return numerator / (left_norm * right_norm)


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class LocalHashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str, dimensions: int = 96) -> None:
        self._model_name = model_name
        self.dimensions = dimensions

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_text(text) for text in texts]

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = tokenize_text(text)
        if not tokens:
            return vector
        for token in tokens:
            token_hash = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(token_hash[:4], "big") % self.dimensions
            sign = 1.0 if token_hash[4] % 2 == 0 else -1.0
            weight = 1.8 if "_" in token else 1.0
            vector[index] += sign * weight
        norm = math.sqrt(sum(item * item for item in vector))
        if norm == 0.0:
            return vector
        return [item / norm for item in vector]


class ExternalOpenAICompatibleEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_url: str, api_key: str, model_name: str) -> None:
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self._model_name = model_name

    @property
    def provider_name(self) -> str:
        return "external_openai_compatible"

    @property
    def model_name(self) -> str:
        return self._model_name

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                self.api_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self._model_name, "input": texts},
            )
            response.raise_for_status()
            payload = response.json()
        data = payload.get("data", [])
        return [item["embedding"] for item in sorted(data, key=lambda item: item["index"])]
