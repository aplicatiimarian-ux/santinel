#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SANTINEL Launch Demo - Full customer journey (EN + RO)."""

from marketing.email_campaigns import EmailCampaigns
from crm.lead_scoring import LeadScoringEngine
from billing.stripe_integration import StripeIntegration, Plan


def demo_english():
    """Customer journey in English."""
    print("\n" + "="*70)
    print("  CUSTOMER JOURNEY: ENGLISH")
    print("="*70 + "\n")

    # 1. Marketing - Landing page
    print("1. MARKETING: Land on page, see pricing")
    print("   → Freemium €0 | Pro €99/mo | Enterprise custom\n")

    # 2. Signup & Onboarding
    print("2. SIGNUP & EMAIL SEQUENCE:")
    en = EmailCampaigns("en")
    for email_type, email, _ in en.get_email_sequence()[:2]:
        print(f"   Day {email.send_delay_days}: {email.subject}\n")

    # 3. Product usage
    print("3. PRODUCT USAGE:")
    user = {
        "email": "coach@example.com",
        "email_opens": 4,
        "email_clicks": 2,
        "calls_recorded": 3,
        "frameworks_tried": 2,
        "logins_last_7_days": 5,
        "trial_active": True,
        "newsletter_subscribed": True,
        "billing_info_provided": True,
    }
    print(f"   ✓ Recorded 3 calls")
    print(f"   ✓ Used 2 frameworks")
    print(f"   ✓ Opened 4 emails\n")

    # 4. Lead scoring
    print("4. LEAD QUALIFICATION:")
    engine = LeadScoringEngine()
    score = engine.score_lead(user)
    print(f"   Score: {score.total_score:.0f}/100 ({score.segment.upper()})")
    print(f"   Action: {score.recommended_action}\n")

    # 5. Conversion
    print("5. CONVERSION:")
    stripe = StripeIntegration("sk_test_...")
    cust = stripe.create_subscription(user["email"], Plan.FREEMIUM)
    stripe.upgrade_to_pro(cust.customer_id)
    invoice = stripe.get_invoice(cust.customer_id)
    print(f"   ✓ Upgraded to Pro: €{invoice['amount']}/month")
    print(f"   ✓ Invoice sent: {user['email']}\n")


def demo_romanian():
    """Customer journey in Romanian."""
    print("\n" + "="*70)
    print("  CUSTOMER JOURNEY: ROMANIAN")
    print("="*70 + "\n")

    print("1. MARKETING: Pagina de start, vede prețurile")
    print("   → Gratuit €0 | Profesional €99/lună | Enterprise custom\n")

    print("2. SIGNUP & CAMPANIE EMAIL:")
    ro = EmailCampaigns("ro")
    for email_type, email, _ in ro.get_email_sequence()[:2]:
        print(f"   Ziua {email.send_delay_days}: {email.subject}\n")

    print("3. UTILIZARE PRODUS:")
    print(f"   ✓ A înregistrat 3 apeluri")
    print(f"   ✓ A folosit 2 framework-uri")
    print(f"   ✓ A deschis 4 emailuri\n")

    print("4. SCORING LEAD:")
    engine = LeadScoringEngine()
    user = {
        "email": "antrenor@example.com",
        "email_opens": 4,
        "email_clicks": 2,
        "calls_recorded": 3,
        "frameworks_tried": 2,
        "logins_last_7_days": 5,
        "trial_active": True,
        "newsletter_subscribed": True,
        "billing_info_provided": True,
    }
    score = engine.score_lead(user)
    print(f"   Score: {score.total_score:.0f}/100 ({score.segment.upper()})")
    print(f"   Acțiune: {score.recommended_action}\n")

    print("5. CONVERSIE:")
    stripe = StripeIntegration("sk_test_...")
    cust = stripe.create_subscription(user["email"], Plan.FREEMIUM)
    stripe.upgrade_to_pro(cust.customer_id)
    invoice = stripe.get_invoice(cust.customer_id)
    print(f"   ✓ Upgrade la Professional: €{invoice['amount']}/lună")
    print(f"   ✓ Factură trimisă: {user['email']}\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  SANTINEL LAUNCH DEMO")
    print("  Complete Customer Journey (EN + RO)")
    print("="*70)

    demo_english()
    demo_romanian()

    print("\n" + "="*70)
    print("  LAUNCH CHECKLIST")
    print("="*70)
    print("\n✓ Landing page (hero, features, pricing)")
    print("✓ 5-email onboarding campaign (bilingual)")
    print("✓ Content hub (4 articles, 5 videos, 3 case studies)")
    print("✓ Lead scoring (engagement-based)")
    print("✓ Stripe integration (Freemium→Pro→Enterprise)")
    print("✓ Customer journey demo (EN + RO)")
    print("\nREADY FOR LAUNCH! 🚀\n")
