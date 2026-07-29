"""FAQ matching engine.

Design choice: TF-IDF + cosine similarity, not an LLM call and not a
vector DB. At ~50-200 fixed FAQs this is the right tool:
  - Zero external API cost and zero network latency per message.
  - Deterministic - the same question always scores the same way,
    which matters for a support bot (no hallucinated answers).
  - Fast enough to run on the cheapest possible host; fits easily
    in memory, rebuilt in well under a second at startup.

If your FAQ set grows past a few thousand entries, or you need to
handle much fuzzier phrasing/typos across languages, swap this module
for sentence-transformers embeddings + a proper index (e.g. FAISS) -
the interface (`match(query, lang)`) can stay identical so nothing
else in the app needs to change.
"""

import json
import logging
import os
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import config

logger = logging.getLogger(__name__)

FAQ_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faqs.json")


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


class FaqMatcher:
    def __init__(self, faq_path: str = FAQ_PATH):
        self.faq_path = faq_path
        self._raw = {}
        self._categories = {}
        self._vectorizers = {}
        self._matrices = {}
        self._entries = {}
        self.load()

    def load(self):
        """(Re)build the in-memory index from the FAQ JSON file.

        Call this again at runtime (e.g. from an admin endpoint) after
        editing faqs.json to pick up changes without a full redeploy.
        """
        with open(self.faq_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._categories = data.get("categories", {})
        self._vectorizers = {}
        self._matrices = {}
        self._entries = {}

        for lang in config.SUPPORTED_LANGUAGES:
            entries = data.get(lang, [])
            self._entries[lang] = entries
            if not entries:
                continue
            questions = [_normalize(e["q"]) for e in entries]
            # English stopwords only apply cleanly to the "en" set; for
            # "hi" (Hinglish/Romanized Hindi) we skip stopword removal
            # since sklearn has no built-in list for it.
            stop_words = "english" if lang == "en" else None
            vectorizer = TfidfVectorizer(stop_words=stop_words)
            matrix = vectorizer.fit_transform(questions)
            self._vectorizers[lang] = vectorizer
            self._matrices[lang] = matrix

        logger.info(
            "FAQ index loaded: %s",
            {lang: len(v) for lang, v in self._entries.items()},
        )

    def categories(self, lang: str):
        return self._categories.get(lang, self._categories.get(config.DEFAULT_LANGUAGE, []))

    def entries_for_category(self, lang: str, category: str):
        entries = self._entries.get(lang, [])
        return [e for e in entries if e["category"].lower() == category.lower()]

    def match(self, query: str, lang: str):
        """Return (entry, score) for the best match, or (None, 0.0).

        Caller is responsible for comparing score against
        config.FAQ_MATCH_THRESHOLD and falling back to NO_MATCH.
        """
        vectorizer = self._vectorizers.get(lang)
        matrix = self._matrices.get(lang)
        entries = self._entries.get(lang)

        if vectorizer is None or matrix is None or not entries:
            return None, 0.0

        query_vec = vectorizer.transform([_normalize(query)])
        scores = cosine_similarity(query_vec, matrix)[0]
        best_idx = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        if best_score <= 0:
            return None, 0.0

        return entries[best_idx], best_score


# Single shared instance - loaded once per process at import time.
faq_matcher = FaqMatcher()
