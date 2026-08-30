# -*- coding: utf-8 -*-
"""
SANTINEL Email Campaigns
Onboarding email sequence for new users.

5-Email Campaign:
1. Welcome Email - Introduction to SANTINEL
2. First Call Email - How to record your first negotiation
3. Framework Intro - Deep dive into first framework
4. Script Library - Access to all scripts
5. Success Stories - Testimonials and case studies

Bilingual (EN + RO) support.
"""

from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class EmailTemplate:
    """Email template structure."""
    subject: str
    preview: str
    body: str
    cta_button: str
    cta_link: str
    send_delay_days: int


class EmailCampaigns:
    """5-email onboarding campaign for new users."""

    def __init__(self, language: str = "en"):
        self.language = language
        self.campaigns = self._init_campaigns()

    def _init_campaigns(self) -> Dict[str, EmailTemplate]:
        """Initialize all email templates."""
        if self.language == "ro":
            return {
                "welcome": EmailTemplate(
                    subject="Bine ai venit la SANTINEL! 🎯 Stăpânește negocierile",
                    preview="Coaching inteligent pentru negocieri - powered by AI",
                    body="""
Salut!

Bine ai venit la SANTINEL - platforma AI care te antrenează la negocieri.

Ce se întâmplă acum:
✓ Contul tău a fost creat și e gata de folosit
✓ Ai acces la 3 framework-uri gratuite: TA, EI, Attachment
✓ Poți înregistra până la 100 apeluri/lună

DE CE SANTINEL?
• 10 framework-uri psihologice pentru negocieri
• Predicție personalitate din voce
• Recomandări scenarii propulsate de ML
• Analitică avansată a performanței

PASUL URMĂTOR:
Înregistrează-ți primul apel de negociere și obține coaching real-time.

Cu plăcere,
Echipa SANTINEL
""",
                    cta_button="Accesează Platforma",
                    cta_link="https://app.santinel.ai/dashboard",
                    send_delay_days=0,
                ),
                "first_call": EmailTemplate(
                    subject="Cum să-ți înregistrezi primul apel 📞",
                    preview="4 pași pentru a obține coaching în timp real",
                    body="""
Salut [USER_NAME]!

Gata să-ți înregistrezi primul apel de negociere?

GHID RAPID (4 pași):
1. Mergi la "New Call" în platforma SANTINEL
2. Permite accesul la microfon
3. Incepe negocierea - SANTINEL va analiza în timp real
4. Vezi coaching imediat după apel

CE VEI VEDEA:
✓ Personalitate detectată
✓ Emoții și sentimente
✓ Semnale de acord/ezitare
✓ Scenarii recomandate
✓ Score de eficacitate

SFAT: Înregistrează apeluri regulate pentru a vedea cum te îmbunătățești!

Cu plăcere,
SANTINEL
""",
                    cta_button="Înregistrează Apelul Tău",
                    cta_link="https://app.santinel.ai/new-call",
                    send_delay_days=1,
                ),
                "framework_intro": EmailTemplate(
                    subject="Framework-ul 1: Analiza Tranzacțională 🧠",
                    preview="Cum să determini starea ego și să negociezi mai bine",
                    body="""
Salut [USER_NAME]!

Astazi te prezint TA (Transactional Analysis) - primele 3 state ego.

PARENT (Autoritate)
- "Iată cum ar trebui să procedezi..."
- Folosit pentru: directivitate, urmărire
- Risc: Poate subestima contraparte

ADULT (Neutru)
- "Acesta sunt faptele și opțiunile..."
- Folosit pentru: negociere rațională
- Avantaj: Construiește încredere

COPIL (Emoțional)
- "Simt că asta e cea mai bună cale..."
- Folosit pentru: empatia și intuiție
- Risc: Prea emoțional pentru unele situații

SFAT PRACTIC:
Folosește ADULT pentru negocieri, dar activează COPIL pentru raport.

Încearcă acum - SANTINEL va detecta starea ego din vocea ta!

Cu plăcere,
Echipa SANTINEL
""",
                    cta_button="Analizează Starea Ego",
                    cta_link="https://app.santinel.ai/frameworks/ta",
                    send_delay_days=3,
                ),
                "script_library": EmailTemplate(
                    subject="🎬 Biblioteca Scenario-urilor: 100+ Template-uri Gata",
                    preview="Scenarii testate pentru Driver, Expressive, Amiable, Analytical",
                    body="""
Salut [USER_NAME]!

Bună veste! Ai acces la biblioteca noastră de 100+ scenarii.

ORGANIZATE DUPĂ:
✓ Personalitate (4 tipuri DISC)
✓ Situație (cold call, discovery, objection, closing, follow-up)
✓ Industrie (tech, sales, HR, law, etc.)

EXEMPLE:
Driver/Closing: "Să finalizez asta acum..."
Expressive/Cold Call: "Sunt nerăbdător să îți arăt asta..."
Amiable/Objection: "Înțeleg îngrijorarea ta, să o rezolvăm..."
Analytical/Discovery: "Iată datele care arată..."

STAT:
Coaches care folosesc scenarii din SANTINEL au rata de succes de 85%!

Deschide biblioteca acum și copiază scenariile care te atrag.

Cu plăcere,
SANTINEL
""",
                    cta_button="Accesează Biblioteca",
                    cta_link="https://app.santinel.ai/scripts",
                    send_delay_days=5,
                ),
                "success_stories": EmailTemplate(
                    subject="📈 Cum au crescut alții cu SANTINEL: Povești de Succes",
                    preview="4 case studies reale - rata câștig crescută cu 40%+",
                    body="""
Salut [USER_NAME]!

POVEȘTI REALE DE LA UTILIZATORII SANTINEL:

CUVÂNT DE LA MARIA (VânzăriTech):
"Am crescut rata de închidere de la 45% la 78% în 3 luni.
SANTINEL mi-a arătat că negociez prea repede - trebuie mai multă empatiere."

CUVÂNT DE LA ION (Avocat):
"Analiza vocii m-a ajutat să identific când sunt prea agresiv.
Acum clienții se simt mai comfortabil și semnează mai ușor."

CUVÂNT DE LA ANDREEA (HR):
"10 framework-urile psihologice m-au ajutat să negociez salariu mai bine.
Echipa a crescut cu 3 oameni, toți din recomandări."

CUVÂNT DE LA ALEX (Antrenor):
"Folosesc SANTINEL pentru antrenarea clienților mei.
Rata de retenție a crescut cu 60% - asta e super putere!"

STATISTICI:
✓ 3,500+ utilizatori activi
✓ 78% rata de recomandare
✓ 40% creștere medie în ratele de succes
✓ 2 limbi, 5 industrii

POȚI FI URMĂTORUL CUVÂNT DE SUCCES!

Cu plăcere,
Echipa SANTINEL
""",
                    cta_button="Vezi Toate Povești",
                    cta_link="https://santinel.ai/case-studies",
                    send_delay_days=7,
                ),
            }
        else:
            # English versions
            return {
                "welcome": EmailTemplate(
                    subject="Welcome to SANTINEL! 🎯 Master Your Negotiations",
                    preview="Intelligent AI coaching for negotiations - powered by psychology",
                    body="""
Hi there!

Welcome to SANTINEL - the AI platform that coaches you through negotiations.

What happens now:
✓ Your account is created and ready to use
✓ You have access to 3 free frameworks: TA, EI, Attachment
✓ You can record up to 100 calls/month

WHY SANTINEL?
• 10 psychological frameworks for negotiations
• Personality prediction from voice
• ML-powered script recommendations
• Advanced performance analytics

NEXT STEP:
Record your first negotiation call and get real-time coaching.

Cheers,
The SANTINEL Team
""",
                    cta_button="Access Platform",
                    cta_link="https://app.santinel.ai/dashboard",
                    send_delay_days=0,
                ),
                "first_call": EmailTemplate(
                    subject="How to Record Your First Call 📞",
                    preview="4 steps to get real-time coaching",
                    body="""
Hi [USER_NAME]!

Ready to record your first negotiation call?

QUICK GUIDE (4 Steps):
1. Go to "New Call" in SANTINEL
2. Allow microphone access
3. Start negotiating - SANTINEL analyzes in real-time
4. See coaching immediately after the call

WHAT YOU'LL SEE:
✓ Detected personality
✓ Emotions and sentiment
✓ Agreement/hesitation signals
✓ Recommended scripts
✓ Effectiveness score

TIP: Record calls regularly to see how you improve!

Cheers,
SANTINEL
""",
                    cta_button="Record Your Call",
                    cta_link="https://app.santinel.ai/new-call",
                    send_delay_days=1,
                ),
                "framework_intro": EmailTemplate(
                    subject="Framework 1: Transactional Analysis 🧠",
                    preview="How to recognize ego states and negotiate better",
                    body="""
Hi [USER_NAME]!

Today I'm introducing TA (Transactional Analysis) - the first 3 ego states.

PARENT (Authority)
- "Here's how you should do this..."
- Use for: directiveness, accountability
- Risk: Can underestimate the other party

ADULT (Neutral)
- "Here are the facts and options..."
- Use for: rational negotiation
- Advantage: Builds trust

CHILD (Emotional)
- "I feel like this is the best path..."
- Use for: empathy and intuition
- Risk: Too emotional for some situations

PRACTICAL TIP:
Use ADULT for negotiations, but activate CHILD for rapport.

Try it now - SANTINEL will detect ego state from your voice!

Cheers,
The SANTINEL Team
""",
                    cta_button="Analyze Ego States",
                    cta_link="https://app.santinel.ai/frameworks/ta",
                    send_delay_days=3,
                ),
                "script_library": EmailTemplate(
                    subject="🎬 Script Library: 100+ Ready-Made Templates",
                    preview="Proven scripts for Driver, Expressive, Amiable, Analytical",
                    body="""
Hi [USER_NAME]!

Great news! You have access to our library of 100+ scripts.

ORGANIZED BY:
✓ Personality (4 DISC types)
✓ Situation (cold call, discovery, objection, closing, follow-up)
✓ Industry (tech, sales, HR, law, etc.)

EXAMPLES:
Driver/Closing: "Let me finalize this now..."
Expressive/Cold Call: "I'm excited to show you this..."
Amiable/Objection: "I understand your concern, let's solve it..."
Analytical/Discovery: "Here's the data that shows..."

STAT:
Coaches using scripts from SANTINEL have 85% success rate!

Open the library now and copy scripts that resonate.

Cheers,
SANTINEL
""",
                    cta_button="Access Library",
                    cta_link="https://app.santinel.ai/scripts",
                    send_delay_days=5,
                ),
                "success_stories": EmailTemplate(
                    subject="📈 How Others Grew with SANTINEL: Success Stories",
                    preview="4 real case studies - 40%+ increase in win rates",
                    body="""
Hi [USER_NAME]!

REAL STORIES FROM SANTINEL USERS:

FROM MARIA (Tech Sales):
"I increased my closing rate from 45% to 78% in 3 months.
SANTINEL showed me I was rushing - I needed more empathy."

FROM ION (Attorney):
"Voice analysis helped me spot when I'm too aggressive.
Now clients feel comfortable and sign easier."

FROM ANDREEA (HR):
"The 10 psychological frameworks helped me negotiate salary better.
My team grew by 3 people, all from referrals."

FROM ALEX (Coach):
"I use SANTINEL to train my clients.
Retention rate jumped 60% - it's a superpower!"

STATS:
✓ 3,500+ active users
✓ 78% recommendation rate
✓ 40% average increase in success rates
✓ 2 languages, 5 industries

YOU COULD BE THE NEXT SUCCESS STORY!

Cheers,
The SANTINEL Team
""",
                    cta_button="See All Stories",
                    cta_link="https://santinel.ai/case-studies",
                    send_delay_days=7,
                ),
            }

    def get_email_sequence(self) -> List[tuple]:
        """Get all emails in the sequence with send times."""
        sequence = []
        for email_type in ["welcome", "first_call", "framework_intro", "script_library", "success_stories"]:
            email = self.campaigns[email_type]
            send_time = datetime.now() + timedelta(days=email.send_delay_days)
            sequence.append((email_type, email, send_time))

        return sequence

    def render_email(self, email_type: str, user_name: str = "User") -> Dict[str, str]:
        """Render an email with user personalization."""
        email = self.campaigns[email_type]

        body = email.body.replace("[USER_NAME]", user_name)

        return {
            "subject": email.subject,
            "preview": email.preview,
            "body": body,
            "cta_button": email.cta_button,
            "cta_link": email.cta_link,
            "send_delay_days": email.send_delay_days,
        }

    def get_all_campaigns(self) -> Dict[str, Dict]:
        """Get all campaigns as dict."""
        result = {}
        for email_type in self.campaigns:
            result[email_type] = self.render_email(email_type)

        return result


if __name__ == "__main__":
    print("="*70)
    print("  SANTINEL 5-EMAIL ONBOARDING CAMPAIGN")
    print("="*70 + "\n")

    # English campaign
    print("ENGLISH CAMPAIGN:")
    print("-" * 70)
    en_campaigns = EmailCampaigns("en")
    for email_type, email, send_time in en_campaigns.get_email_sequence():
        print(f"\n{email_type.upper()} (Send: {send_time.strftime('%Y-%m-%d')})")
        print(f"Subject: {email.subject}")
        print(f"Preview: {email.preview}")

    # Romanian campaign
    print("\n\nROMANIAN CAMPAIGN:")
    print("-" * 70)
    ro_campaigns = EmailCampaigns("ro")
    for email_type, email, send_time in ro_campaigns.get_email_sequence():
        print(f"\n{email_type.upper()} (Send: {send_time.strftime('%Y-%m-%d')})")
        print(f"Subject: {email.subject}")
        print(f"Preview: {email.preview}")

    print("\n✓ 5-email onboarding campaign ready for deployment")
    print("✓ Bilingual (EN + RO) support")
    print("✓ Personalization tokens ([USER_NAME])")
    print("✓ CTA buttons and tracking links")
