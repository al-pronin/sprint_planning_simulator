from __future__ import annotations

import random
from dataclasses import dataclass

from src.feature import Feature, FeatureStage


@dataclass(slots=True)
class ReviewEngine:
    """
    Encapsulates review decision logic 👀

    Responsibilities:
        - Decide review outcome
        - Apply rejection flow
    """

    fail_probability: float = 0.3

    def process_review(self, feature: Feature) -> None:
        """
        Called when REVIEW stage is completed.

        Either:
            - Approves → feature continues to next stage
            - Rejects → feature goes back to DEVELOPMENT
        """
        print(f"👀 Reviewing {feature.name}...")

        if random.random() < self.fail_probability:
            print(f"❌ Review failed for {feature.name} → back to DEVELOPMENT")
            feature.move_to_stage(FeatureStage.DEVELOPMENT)
        else:
            print(f"✅ Review passed for {feature.name} 🎉")