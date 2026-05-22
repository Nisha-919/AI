from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import librosa
import numpy as np
from scipy.spatial.distance import cosine


@dataclass(slots=True)
class AuthResult:
    authorized: bool
    score: float
    reason: str


class VoiceAuthenticator:
    def __init__(self, threshold: float = 0.82):
        self.threshold = threshold
        self.reference_embedding: Optional[np.ndarray] = None

    @staticmethod
    def _embedding(audio_path: Path) -> np.ndarray:
        signal, sr = librosa.load(str(audio_path), sr=16_000)
        mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=40)
        delta = librosa.feature.delta(mfcc)
        features = np.concatenate([mfcc, delta], axis=0)
        return np.mean(features, axis=1)

    def register_reference(self, audio_path: Path) -> None:
        self.reference_embedding = self._embedding(audio_path)

    def verify(self, sample_audio_path: Path, passphrase_text: str, required_passphrase: str) -> AuthResult:
        if passphrase_text.strip().lower() != required_passphrase.strip().lower():
            return AuthResult(False, 0.0, "Passphrase mismatch")
        if self.reference_embedding is None:
            return AuthResult(False, 0.0, "Reference voice is not enrolled")
        sample_embedding = self._embedding(sample_audio_path)
        similarity = 1 - cosine(self.reference_embedding, sample_embedding)
        authorized = bool(similarity >= self.threshold)
        reason = "Authorized speaker" if authorized else "Voice mismatch"
        return AuthResult(authorized, float(similarity), reason)
