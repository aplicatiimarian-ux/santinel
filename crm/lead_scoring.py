# -*- coding: utf-8 -*-
"""Lead scoring based on engagement metrics."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class LeadScore:
    """Lead qualification score."""
    email: str
    total_score: float  # 0-100
    engagement_score: float  # Email opens, clicks
    product_score: float  # Calls recorded, frameworks used
    behavioral_score: float  # Login frequency, trial conversion
    segment: str  # hot, warm, cold
    recommended_action: str


class LeadScoringEngine:
    """Score leads for sales prioritization."""

    def score_lead(self, user_data: dict) -> LeadScore:
        """Calculate lead score."""
        engagement = self._score_engagement(user_data)
        product = self._score_product(user_data)
        behavioral = self._score_behavioral(user_data)

        total = (engagement * 0.3) + (product * 0.4) + (behavioral * 0.3)
        segment = "hot" if total >= 70 else "warm" if total >= 40 else "cold"

        actions = {
            "hot": "Contact immediately - high conversion likelihood",
            "warm": "Nurture with content - consider for sales call",
            "cold": "Automated email sequence - re-engage later",
        }

        return LeadScore(
            email=user_data.get("email", ""),
            total_score=total,
            engagement_score=engagement,
            product_score=product,
            behavioral_score=behavioral,
            segment=segment,
            recommended_action=actions[segment],
        )

    def _score_engagement(self, user_data: dict) -> float:
        """Score email engagement (0-100)."""
        score = 0.0
        score += user_data.get("email_opens", 0) * 5  # 1 point per open
        score += user_data.get("email_clicks", 0) * 10  # 2 points per click
        score += user_data.get("newsletter_subscribed", False) * 20
        return min(score, 100)

    def _score_product(self, user_data: dict) -> float:
        """Score product usage (0-100)."""
        score = 0.0
        score += min(user_data.get("calls_recorded", 0) * 5, 50)  # Max 50 for calls
        score += min(user_data.get("frameworks_tried", 0) * 10, 50)  # Max 50 for frameworks
        return min(score, 100)

    def _score_behavioral(self, user_data: dict) -> float:
        """Score conversion likelihood (0-100)."""
        score = 50.0  # Base score

        # Login frequency
        logins_last_7 = user_data.get("logins_last_7_days", 0)
        if logins_last_7 >= 5:
            score += 25
        elif logins_last_7 >= 3:
            score += 15
        elif logins_last_7 >= 1:
            score += 5

        # Trial to paid conversion signals
        if user_data.get("trial_active", False):
            score += 20
        if user_data.get("billing_info_provided", False):
            score += 15

        return min(score, 100)


if __name__ == "__main__":
    engine = LeadScoringEngine()

    # Test leads
    leads = [
        {
            "email": "hot@example.com",
            "email_opens": 5,
            "email_clicks": 3,
            "newsletter_subscribed": True,
            "calls_recorded": 5,
            "frameworks_tried": 3,
            "logins_last_7_days": 6,
            "trial_active": True,
            "billing_info_provided": True,
        },
        {
            "email": "warm@example.com",
            "email_opens": 2,
            "email_clicks": 1,
            "newsletter_subscribed": False,
            "calls_recorded": 2,
            "frameworks_tried": 1,
            "logins_last_7_days": 2,
            "trial_active": True,
            "billing_info_provided": False,
        },
    ]

    print("LEAD SCORING:")
    for lead in leads:
        score = engine.score_lead(lead)
        print(f"\n{score.email}")
        print(f"  Total: {score.total_score:.0f}/100 ({score.segment.upper()})")
        print(f"  Action: {score.recommended_action}")
