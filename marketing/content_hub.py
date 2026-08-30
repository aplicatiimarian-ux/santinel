# -*- coding: utf-8 -*-
"""
SANTINEL Content Hub
Educational resources: blog articles, video tutorials, case studies.
"""

CONTENT_HUB = {
    "blog_articles": [
        {
            "id": "psychology-of-negotiation",
            "title": "The Psychology of Negotiation: Why People Say Yes",
            "description": "Deep dive into behavioral economics and negotiation tactics",
            "content": "Negotiations are psychology. Here's what research says about decision-making, persuasion, and trust...",
            "author": "Dr. Marius",
            "date": "2026-08-15",
            "read_time": "8 min",
            "tags": ["psychology", "negotiation", "behavioral-econ"],
        },
        {
            "id": "disc-personalities",
            "title": "Understanding DISC Personalities in Sales",
            "description": "How to recognize and adapt to Driver, Expressive, Amiable, Analytical",
            "content": "Every personality has different triggers. Here's how to recognize and communicate with each type...",
            "author": "Dr. Marius",
            "date": "2026-08-10",
            "read_time": "10 min",
            "tags": ["personality", "disc", "sales"],
        },
        {
            "id": "emotional-intelligence",
            "title": "Emotional Intelligence: The Secret Weapon in Negotiations",
            "description": "Why managing emotions wins deals",
            "content": "Emotional intelligence is the difference between a good negotiator and a great one...",
            "author": "Dr. Marius",
            "date": "2026-08-05",
            "read_time": "7 min",
            "tags": ["ei", "emotions", "soft-skills"],
        },
        {
            "id": "voice-analysis",
            "title": "What Your Voice Reveals: Micro-Signals in Negotiation",
            "description": "How AI detects personality, urgency, and hesitation from tone",
            "content": "Pitch, pace, energy - they tell a story. Learn to listen...",
            "author": "Dr. Marius",
            "date": "2026-07-30",
            "read_time": "9 min",
            "tags": ["voice", "ai", "signal-detection"],
        },
    ],
    "video_tutorials": [
        {
            "id": "intro-to-frameworks",
            "title": "Introduction to SANTINEL: 10 Frameworks Overview",
            "description": "2-minute overview of all frameworks",
            "duration": "2:45",
            "thumbnail": "intro-frameworks.jpg",
        },
        {
            "id": "ta-ego-states",
            "title": "TA Framework: Ego States Explained",
            "description": "Parent, Adult, Child - when to use each",
            "duration": "5:30",
            "thumbnail": "ta-states.jpg",
        },
        {
            "id": "ei-competencies",
            "title": "EI Framework: 5 Emotional Intelligence Competencies",
            "description": "Self-awareness, regulation, motivation, empathy, social skills",
            "duration": "6:15",
            "thumbnail": "ei-competencies.jpg",
        },
        {
            "id": "voice-analysis-live",
            "title": "Live Demo: Recording Your First Call with SANTINEL",
            "description": "Step-by-step walkthrough of voice analysis",
            "duration": "7:00",
            "thumbnail": "demo-live.jpg",
        },
        {
            "id": "script-matching",
            "title": "Using AI-Recommended Scripts for Your Personality",
            "description": "How to get personalized script recommendations",
            "duration": "4:20",
            "thumbnail": "scripts.jpg",
        },
    ],
    "case_studies": [
        {
            "id": "maria-tech-sales",
            "title": "Maria: How Tech Sales Coach Grew Win Rate from 45% to 78%",
            "company": "TechCorp",
            "industry": "Technology",
            "role": "Sales Director",
            "challenge": "Low closing rate, rushing negotiations, missing rapport-building",
            "solution": "Used TA framework to recognize Parent/Adult/Child patterns. Implemented AI script recommendations.",
            "results": "78% closing rate (+73%), team morale improved, 3 promotions",
            "duration_months": 3,
            "quote": "SANTINEL showed me I was being too aggressive. I learned to balance directiveness with empathy.",
        },
        {
            "id": "ion-attorney",
            "title": "Ion: Law Firm Partner Negotiates Better with Voice Insights",
            "company": "LawFirm",
            "industry": "Legal",
            "role": "Senior Partner",
            "challenge": "Clients felt intimidated, better settlement rates needed",
            "solution": "Used voice analysis to detect when tone was too aggressive. Adjusted based on client personality (DISC).",
            "results": "Settlement rate +45%, client retention +60%, billable hours increased",
            "duration_months": 2,
            "quote": "Voice analysis was eye-opening. I didn't realize how aggressive I sounded.",
        },
        {
            "id": "andreea-hr",
            "title": "Andreea: HR Manager Masters Salary Negotiations with Behavioral Economics",
            "company": "GlobalCorp",
            "industry": "HR",
            "role": "HR Director",
            "challenge": "Candidates often rejected offers, team cost-per-hire high",
            "solution": "Applied behavioral economics framework. Reframed offers to emphasize loss-aversion.",
            "results": "95% offer acceptance rate, team grew from 10 to 13 people, improved morale",
            "duration_months": 4,
            "quote": "Understanding loss aversion changed everything about how I present compensation packages.",
        },
    ],
}

class ContentHub:
    """Manage educational content."""

    def __init__(self):
        self.content = CONTENT_HUB

    def get_blog_articles(self):
        """Get all blog articles."""
        return self.content["blog_articles"]

    def get_video_tutorials(self):
        """Get all video tutorials."""
        return self.content["video_tutorials"]

    def get_case_studies(self):
        """Get all case studies."""
        return self.content["case_studies"]

    def get_article_by_id(self, article_id: str):
        """Get specific article."""
        for article in self.content["blog_articles"]:
            if article["id"] == article_id:
                return article
        return None

    def get_articles_by_tag(self, tag: str):
        """Get articles by tag."""
        return [a for a in self.content["blog_articles"] if tag in a.get("tags", [])]

    def get_featured_content(self):
        """Get featured content for homepage."""
        return {
            "featured_article": self.content["blog_articles"][0],
            "featured_video": self.content["video_tutorials"][0],
            "featured_case_study": self.content["case_studies"][0],
        }


if __name__ == "__main__":
    print("="*70)
    print("  SANTINEL CONTENT HUB")
    print("="*70 + "\n")

    hub = ContentHub()

    print("BLOG ARTICLES:")
    for article in hub.get_blog_articles():
        print(f"  • {article['title']} ({article['read_time']})")

    print("\nVIDEO TUTORIALS:")
    for video in hub.get_video_tutorials():
        print(f"  • {video['title']} ({video['duration']})")

    print("\nCASE STUDIES:")
    for study in hub.get_case_studies():
        print(f"  • {study['title']}")

    print("\n✓ Content hub ready with 4 articles, 5 videos, 3 case studies")
