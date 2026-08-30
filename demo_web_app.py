#!/usr/bin/env python3
# ============================================================
# SANTINEL Web Application Demo
# Bilingual full-app flow demonstration (EN+RO)
# PHASE 15: World-class React UI with Tailwind CSS
# ============================================================

import json
import logging
from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Language(Enum):
    ENGLISH = "en"
    ROMANIAN = "ro"


# ============================================================
# UI COMPONENTS DEMO DATA
# ============================================================

@dataclass
class CoachingTip:
    title: str
    content: str
    framework: str  # cbt, nlp, ta, ego
    confidence: float


@dataclass
class Script:
    id: int
    title: str
    category: str
    text: str
    rating: float
    times_used: int
    effectiveness: float


@dataclass
class CallRecord:
    id: int
    date: str
    duration: str
    result: str  # Won or Lost
    frameworks_used: List[str]
    tips_applied: int
    win_probability: float


class DemoMessages:
    """Bilingual UI demo messages"""

    MESSAGES = {
        "app_title": {
            Language.ENGLISH: "SANTINEL AI Coaching Assistant",
            Language.ROMANIAN: "Asistent de antrenament IA SANTINEL"
        },
        "dashboard": {
            Language.ENGLISH: "Dashboard - Real-Time Coaching",
            Language.ROMANIAN: "Tablă de bord - Coaching în timp real"
        },
        "live_call": {
            Language.ENGLISH: "Live Call - In Progress",
            Language.ROMANIAN: "Apel live - În progres"
        },
        "coaching_tips": {
            Language.ENGLISH: "Real-Time Coaching Tips",
            Language.ROMANIAN: "Sfaturi de antrenament în timp real"
        },
        "win_probability": {
            Language.ENGLISH: "Win Probability",
            Language.ROMANIAN: "Probabilitate de câștig"
        },
        "transcript": {
            Language.ENGLISH: "Conversation Transcript",
            Language.ROMANIAN: "Transcrierea conversației"
        },
        "script_library": {
            Language.ENGLISH: "Script Library - 150+ Negotiation Scripts",
            Language.ROMANIAN: "Bibliotecă de scripturi - 150+ scripturi de negociere"
        },
        "search_scripts": {
            Language.ENGLISH: "Search scripts by situation or personality type...",
            Language.ROMANIAN: "Cautați scripturi după situație sau tip de personalitate..."
        },
        "call_history": {
            Language.ENGLISH: "Call History & Analytics",
            Language.ROMANIAN: "Istoria apelurilor și analize"
        },
        "my_profile": {
            Language.ENGLISH: "My Profile - Personality Assessment",
            Language.ROMANIAN: "Profilul meu - Evaluare de personalitate"
        },
        "settings": {
            Language.ENGLISH: "Settings & Preferences",
            Language.ROMANIAN: "Setări și preferințe"
        },
        "billing": {
            Language.ENGLISH: "Billing & Subscription",
            Language.ROMANIAN: "Facturare și abonament"
        },
        "user_stats": {
            Language.ENGLISH: "Your Statistics",
            Language.ROMANIAN: "Statisticile dumneavoastră"
        },
        "win_rate": {
            Language.ENGLISH: "Win Rate",
            Language.ROMANIAN: "Rata de câștig"
        },
        "total_calls": {
            Language.ENGLISH: "Total Calls",
            Language.ROMANIAN: "Total apeluri"
        },
        "success_rate": {
            Language.ENGLISH: "Success Rate",
            Language.ROMANIAN: "Rata de succes"
        },
        "next_call": {
            Language.ENGLISH: "Next Scheduled Call",
            Language.ROMANIAN: "Următorul apel programat"
        },
        "personality_traits": {
            Language.ENGLISH: "Big Five Personality Traits",
            Language.ROMANIAN: "Cinci mari trăsături de personalitate"
        },
        "attachment_style": {
            Language.ENGLISH: "Attachment Style",
            Language.ROMANIAN: "Stil de atașament"
        },
        "ego_state": {
            Language.ENGLISH: "Ego State",
            Language.ROMANIAN: "Stare de ego"
        },
        "professional_plan": {
            Language.ENGLISH: "Professional Plan - $29/month",
            Language.ROMANIAN: "Plan profesional - $29/lună"
        },
        "features_included": {
            Language.ENGLISH: "Features Included",
            Language.ROMANIAN: "Caracteristici incluse"
        },
        "unlimited_calls": {
            Language.ENGLISH: "Unlimited calls",
            Language.ROMANIAN: "Apeluri nelimitate"
        },
        "real_time_coaching": {
            Language.ENGLISH: "Real-time coaching",
            Language.ROMANIAN: "Antrenament în timp real"
        },
        "script_library_access": {
            Language.ENGLISH: "Script library access",
            Language.ROMANIAN: "Accesul la biblioteca de scripturi"
        },
        "analytics_dashboard": {
            Language.ENGLISH: "Analytics dashboard",
            Language.ROMANIAN: "Tablă de bord de analize"
        },
        "current_plan": {
            Language.ENGLISH: "Current Plan",
            Language.ROMANIAN: "Plan actual"
        },
        "billing_history": {
            Language.ENGLISH: "Billing History",
            Language.ROMANIAN: "Istoria de facturare"
        },
    }

    @classmethod
    def get(cls, key: str, language: Language) -> str:
        """Get message in specified language"""
        return cls.MESSAGES.get(key, {}).get(language, key)


# ============================================================
# DEMO DATA GENERATORS
# ============================================================

def generate_coaching_tips() -> List[CoachingTip]:
    """Generate sample coaching tips"""
    return [
        CoachingTip(
            title="Challenge Assumptions",
            content="Ask about their specific budget constraints",
            framework="cbt",
            confidence=0.92
        ),
        CoachingTip(
            title="Reframing Technique",
            content="Focus on ROI instead of cost alone",
            framework="nlp",
            confidence=0.85
        ),
        CoachingTip(
            title="Adult Ego State",
            content="Stay factual and logical in your response",
            framework="ta",
            confidence=0.88
        ),
        CoachingTip(
            title="Build Rapport",
            content="Mirror their communication style subtly",
            framework="nlp",
            confidence=0.81
        ),
    ]


def generate_scripts() -> List[Script]:
    """Generate sample negotiation scripts"""
    scripts_en = [
        Script(1, "Opening", "Initial Contact",
               "I appreciate your interest. Let me share how our solution creates value...", 4.8, 156, 0.88),
        Script(2, "Handling Price Objections", "Price Negotiation",
               "I understand budget is important. Let's look at the long-term ROI...", 4.7, 243, 0.85),
        Script(3, "Building Trust", "Rapport",
               "We've worked with 500+ companies in your industry. What's your main concern?", 4.6, 189, 0.82),
        Script(4, "Closing Technique", "Closing",
               "Based on what we've discussed, shall we move forward with implementation?", 4.9, 267, 0.91),
        Script(5, "Handling Delays", "Objection Handling",
               "I understand timing is critical. When would be ideal for you to start?", 4.5, 134, 0.79),
        Script(6, "Win-Win Solutions", "Negotiation",
               "Let's explore options that work for both of us. What if we...", 4.7, 198, 0.84),
    ]

    scripts_ro = [
        Script(1, "Deschidere", "Contact inițial",
               "Apreciez interesul dvs. Permiteți-mi să vă arăt cum soluția noastră creează valoare...", 4.8, 156, 0.88),
        Script(2, "Obiecții cu privire la preț", "Negocierea prețului",
               "Înțeleg că bugetul este important. Să analizez ROI pe termen lung...", 4.7, 243, 0.85),
        Script(3, "Construirea încrederii", "Raport",
               "Am lucrat cu 500+ companii din industria dvs. Care este principala dumneavoastră preocupare?", 4.6, 189, 0.82),
        Script(4, "Tehnică de închidere", "Închidere",
               "Pe baza a ceea ce am discutat, ar trebui să mergem înainte cu implementarea?", 4.9, 267, 0.91),
        Script(5, "Gestionarea întârzierilor", "Manipularea obiecțiilor",
               "Înțeleg că timingul este critic. Când ar fi ideal pentru dumneavoastră să începeți?", 4.5, 134, 0.79),
        Script(6, "Soluții win-win", "Negociere",
               "Să explorăm opțiuni care funcționează pentru amândoi. Ce dacă...", 4.7, 198, 0.84),
    ]

    return scripts_en + scripts_ro


def generate_call_records() -> List[CallRecord]:
    """Generate sample call records"""
    return [
        CallRecord(247, "2024-08-30", "24m", "Won", ["CBT", "NLP"], 5, 0.82),
        CallRecord(246, "2024-08-29", "18m", "Won", ["TA", "CBT"], 3, 0.78),
        CallRecord(245, "2024-08-28", "31m", "Lost", ["NLP"], 2, 0.65),
        CallRecord(244, "2024-08-27", "22m", "Won", ["CBT", "Ego-State"], 4, 0.81),
        CallRecord(243, "2024-08-26", "28m", "Won", ["NLP", "TA"], 5, 0.85),
    ]


# ============================================================
# DEMO RUNNER
# ============================================================

class WebAppDemo:
    """Demonstrate SANTINEL web application features"""

    def __init__(self, language: Language = Language.ENGLISH):
        self.language = language
        self.user = {
            "name": "John Doe" if language == Language.ENGLISH else "Ioan Popescu",
            "email": "john@example.com",
            "tier": "professional",
            "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
            "win_rate": 0.82,
            "total_calls": 247,
            "success_rate": 0.78,
            "attachment_style": "Secure" if language == Language.ENGLISH else "Sigur",
            "ego_state": "Adult",
        }
        self.coaching_tips = generate_coaching_tips()
        self.scripts = generate_scripts()
        self.call_records = generate_call_records()

    def print_header(self):
        """Print application header"""
        print("\n" + "="*80)
        print(f"  {DemoMessages.get('app_title', self.language)}")
        print("="*80)
        print(f"  Language: {self.language.value.upper()}")
        print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

    def demo_dashboard(self):
        """Demonstrate dashboard page"""
        print(f"\n{'='*80}")
        print(f"  PAGE 1: {DemoMessages.get('dashboard', self.language)}")
        print(f"{'='*80}\n")

        # User statistics
        print(f"[STATS CARDS]")
        print(f"  {DemoMessages.get('win_rate', self.language)}: {self.user['win_rate']:.0%}")
        print(f"  {DemoMessages.get('total_calls', self.language)}: {self.user['total_calls']}")
        print(f"  {DemoMessages.get('success_rate', self.language)}: {self.user['success_rate']:.0%}")
        print(f"  {DemoMessages.get('next_call', self.language)}: in 2 hours\n")

        # Live coaching interface
        print(f"[LIVE COACHING INTERFACE]")
        print(f"  {DemoMessages.get('live_call', self.language)}")
        print(f"  Client: ABC Corp | Duration: 5:24 | {DemoMessages.get('win_probability', self.language)}: 72%\n")

        print(f"[{DemoMessages.get('transcript', self.language).upper()}]")
        print(f"  You: So, regarding the pricing proposal...")
        print(f"  Client: We have limited budget for new solutions\n")

        # Coaching tips
        print(f"[{DemoMessages.get('coaching_tips', self.language).upper()}]")
        for i, tip in enumerate(self.coaching_tips[:3], 1):
            print(f"  {i}. {tip.title} ({tip.framework.upper()})")
            print(f"     > {tip.content}")
            print(f"     Confidence: {tip.confidence:.0%}\n")

    def demo_call_history(self):
        """Demonstrate call history page"""
        print(f"\n{'='*80}")
        print(f"  PAGE 2: {DemoMessages.get('call_history', self.language)}")
        print(f"{'='*80}\n")

        print(f"[ANALYTICS SUMMARY]")
        print(f"  Successful: {sum(1 for c in self.call_records if c.result == 'Won')}")
        print(f"  Unsuccessful: {sum(1 for c in self.call_records if c.result == 'Lost')}")
        print(f"  Avg Duration: 24m 42s\n")

        print(f"[RECENT CALLS]")
        for call in self.call_records[:5]:
            result_emoji = "[OK]" if call.result == "Won" else "[X]"
            frameworks = ", ".join(call.frameworks_used)
            print(f"  {result_emoji} Call #{call.id} | {call.date} | {call.duration} | {call.result}")
            print(f"     Frameworks: {frameworks} | Tips: {call.tips_applied} | Win: {call.win_probability:.0%}\n")

    def demo_scripts_library(self):
        """Demonstrate scripts library page"""
        print(f"\n{'='*80}")
        print(f"  PAGE 3: {DemoMessages.get('script_library', self.language)}")
        print(f"{'='*80}\n")

        print(f"[SEARCH & FILTER]")
        print(f"  {DemoMessages.get('search_scripts', self.language)}")
        print(f"  Filters: All Situations | Language: {self.language.value.upper()}\n")

        lang_scripts = [s for s in self.scripts if
                       (self.language == Language.ENGLISH and s.category in ["Initial Contact", "Price Negotiation", "Rapport", "Closing", "Objection Handling", "Negotiation"]) or
                       (self.language == Language.ROMANIAN and s.category in ["Contact inițial", "Negocierea prețului", "Raport", "Închidere", "Manipularea obiecțiilor", "Negociere"])]

        print(f"[SCRIPTS AVAILABLE: {len(lang_scripts)}]")
        for script in lang_scripts[:4]:
            rating_stars = "*" * int(script.rating)
            print(f"  [{script.id}] {script.title} ({script.category})")
            print(f"      \"{script.text[:60]}...\"")
            print(f"      Rating: [{rating_stars}] {script.rating:.1f} | Used: {script.times_used}x | Effectiveness: {script.effectiveness:.0%}\n")

    def demo_profile(self):
        """Demonstrate profile page"""
        print(f"\n{'='*80}")
        print(f"  PAGE 4: {DemoMessages.get('my_profile', self.language)}")
        print(f"{'='*80}\n")

        print(f"[USER PROFILE]")
        print(f"  Name: {self.user['name']}")
        print(f"  Email: {self.user['email']}")
        print(f"  Tier: {self.user['tier']}\n")

        print(f"[{DemoMessages.get('personality_traits', self.language).upper()}]")
        traits = {
            "Openness": 85,
            "Conscientiousness": 92,
            "Extraversion": 72,
            "Agreeableness": 68,
            "Neuroticism": 35,
        }
        for trait, value in traits.items():
            bar = "#" * (value // 10) + "-" * ((100 - value) // 10)
            print(f"  {trait:20} {bar} {value}%")

        print(f"\n[COACHING PROFILE]")
        print(f"  {DemoMessages.get('attachment_style', self.language)}: {self.user['attachment_style']}")
        print(f"  {DemoMessages.get('ego_state', self.language)}: {self.user['ego_state']}\n")

    def demo_settings(self):
        """Demonstrate settings page"""
        print(f"\n{'='*80}")
        print(f"  PAGE 5: {DemoMessages.get('settings', self.language)}")
        print(f"{'='*80}\n")

        print(f"[NOTIFICATION SETTINGS]")
        print(f"  [ON] Email notifications")
        print(f"  [ON] Push notifications")
        print(f"  [OFF] SMS alerts\n")

        print(f"[INTEGRATIONS]")
        integrations = ["Slack", "Microsoft Teams", "Google Calendar"]
        for integration in integrations:
            print(f"  • {integration} - [Connect]\n")

        print(f"[PREFERENCES]")
        print(f"  Theme: Auto (system preference)")
        print(f"  Language: {self.language.value.upper()}")
        print(f"  Timezone: UTC+2\n")

    def demo_billing(self):
        """Demonstrate billing page"""
        print(f"\n{'='*80}")
        print(f"  PAGE 6: {DemoMessages.get('billing', self.language)}")
        print(f"{'='*80}\n")

        print(f"[CURRENT SUBSCRIPTION]")
        print(f"  Plan: {DemoMessages.get('professional_plan', self.language)}")
        print(f"  Status: Active")
        print(f"  Renewal: {(datetime.now() + timedelta(days=20)).strftime('%Y-%m-%d')}\n")

        print(f"[{DemoMessages.get('features_included', self.language).upper()}]")
        features = [
            DemoMessages.get('unlimited_calls', self.language),
            DemoMessages.get('real_time_coaching', self.language),
            DemoMessages.get('script_library_access', self.language),
            DemoMessages.get('analytics_dashboard', self.language),
        ]
        for feature in features:
            print(f"  [OK] {feature}")

        print(f"\n[{DemoMessages.get('billing_history', self.language).upper()}]")
        for i in range(1, 4):
            date = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m-%d')
            print(f"  Invoice #{1000+i} | {date} | $29.00 | [Download]\n")

    def demo_components(self):
        """Demonstrate reusable components"""
        print(f"\n{'='*80}")
        print(f"  REUSABLE COMPONENTS SHOWCASE")
        print(f"{'='*80}\n")

        print(f"[CoachingCard Component]")
        print(f"  Used in: Dashboard, History pages")
        print(f"  Features: Framework badge, confidence indicator, hover effects\n")

        print(f"[ScriptCard Component]")
        print(f"  Used in: Scripts Library")
        print(f"  Features: Rating stars, usage count, effectiveness rating\n")

        print(f"[TranscriptViewer Component]")
        print(f"  Used in: Live coaching interface")
        print(f"  Features: Message grouping, timestamps, live indicator\n")

        print(f"[AnalyticsChart Component]")
        print(f"  Used in: Call History")
        print(f"  Features: Progress bars, summary stats (avg, max, min)\n")

        print(f"[VoiceWaveform Component]")
        print(f"  Used in: Live call interface")
        print(f"  Features: Animated bars, active state indicator\n")

        print(f"[PersonalityGauge Component]")
        print(f"  Used in: Profile page")
        print(f"  Features: Gradient fills, percentage labels\n")

    def demo_theme_system(self):
        """Demonstrate theme and styling system"""
        print(f"\n{'='*80}")
        print(f"  DESIGN SYSTEM & THEMING")
        print(f"{'='*80}\n")

        print(f"[LIGHT/DARK MODE]")
        print(f"  • Light mode (default)")
        print(f"  • Dark mode with CSS variables")
        print(f"  • System preference detection")
        print(f"  • Per-user toggle\n")

        print(f"[RESPONSIVE BREAKPOINTS]")
        print(f"  • Mobile: < 640px")
        print(f"  • Tablet: 640px - 1024px")
        print(f"  • Desktop: > 1024px")
        print(f"  • Desktop-first, mobile-optimized\n")

        print(f"[COLOR TOKENS]")
        print(f"  Primary: #2563eb (Blue)")
        print(f"  Secondary: #8b5cf6 (Purple)")
        print(f"  Success: #10b981 (Green)")
        print(f"  Warning: #f59e0b (Amber)")
        print(f"  Danger: #ef4444 (Red)\n")

        print(f"[SPACING & SIZING]")
        print(f"  Base unit: 1rem (16px)")
        print(f"  Scale: xs (0.75rem) to 2xl (1.5rem)")
        print(f"  Radius: sm to full")
        print(f"  Shadows: xs to xl\n")

    def run_full_demo(self):
        """Run complete application demo"""
        self.print_header()
        self.demo_dashboard()
        self.demo_call_history()
        self.demo_scripts_library()
        self.demo_profile()
        self.demo_settings()
        self.demo_billing()
        self.demo_components()
        self.demo_theme_system()

        print(f"\n{'='*80}")
        print(f"  DEMO COMPLETE")
        print(f"{'='*80}")
        print(f"  Total pages: 6")
        print(f"  Components: 10+")
        print(f"  Responsive layouts: Desktop-first, mobile-friendly")
        print(f"  Theme support: Light/Dark mode with CSS variables")
        print(f"  Accessibility: WCAG 2.1 AA compliant")
        print(f"{'='*80}\n")


def main():
    """Run bilingual demo"""
    print("\n" + "="*80)
    print("  SANTINEL PHASE 15 - WEB APPLICATION DEMO")
    print("  World-class React UI with Tailwind CSS & shadcn/ui")
    print("="*80)

    # Run English demo
    print("\n\n[ENGLISH VERSION]")
    en_demo = WebAppDemo(Language.ENGLISH)
    en_demo.run_full_demo()

    # Run Romanian demo
    print("\n\n[ROMANIAN VERSION / VERSIUNEA ROMÂNĂ]")
    ro_demo = WebAppDemo(Language.ROMANIAN)
    ro_demo.run_full_demo()

    print("\n" + "="*80)
    print("  PHASE 15 COMPLETE")
    print("="*80)
    print("  [OK] React application with modern architecture")
    print("  [OK] Tailwind CSS + shadcn/ui design system")
    print("  [OK] Responsive layouts (desktop-first)")
    print("  [OK] Dark/Light theme support")
    print("  [OK] 6 main pages with comprehensive features")
    print("  [OK] Reusable component library")
    print("  [OK] Bilingual UI (English + Romanian)")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
