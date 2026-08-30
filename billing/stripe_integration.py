# -*- coding: utf-8 -*-
"""Stripe payment integration for subscriptions."""

from dataclasses import dataclass
from enum import Enum


class Plan(Enum):
    """Subscription plans."""
    FREEMIUM = ("free", 0)
    PRO = ("pro", 99)
    ENTERPRISE = ("enterprise", 0)  # Custom pricing


@dataclass
class StripeCustomer:
    """Stripe customer."""
    customer_id: str
    email: str
    plan: Plan
    status: str  # active, cancelled, past_due
    billing_cycle_day: int


class StripeIntegration:
    """Handle Stripe payments."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.customers = {}

    def create_subscription(self, email: str, plan: Plan) -> StripeCustomer:
        """Create Stripe subscription."""
        customer_id = f"cust_{len(self.customers) + 1}"
        customer = StripeCustomer(
            customer_id=customer_id,
            email=email,
            plan=plan,
            status="active",
            billing_cycle_day=1,
        )
        self.customers[customer_id] = customer
        return customer

    def upgrade_to_pro(self, customer_id: str) -> StripeCustomer:
        """Upgrade from Freemium to Pro."""
        if customer_id in self.customers:
            self.customers[customer_id].plan = Plan.PRO
            self.customers[customer_id].status = "active"
        return self.customers.get(customer_id)

    def cancel_subscription(self, customer_id: str) -> bool:
        """Cancel subscription."""
        if customer_id in self.customers:
            self.customers[customer_id].status = "cancelled"
            return True
        return False

    def get_invoice(self, customer_id: str) -> dict:
        """Get customer invoice."""
        if customer_id not in self.customers:
            return None

        customer = self.customers[customer_id]
        _, price = customer.plan.value

        return {
            "customer_id": customer_id,
            "email": customer.email,
            "plan": customer.plan.name,
            "amount": price,
            "currency": "EUR",
            "status": customer.status,
        }


if __name__ == "__main__":
    stripe = StripeIntegration("sk_test_...")

    print("STRIPE INTEGRATION DEMO:")
    cust = stripe.create_subscription("user@example.com", Plan.FREEMIUM)
    print(f"✓ Created: {cust.customer_id} ({cust.plan.name})")

    stripe.upgrade_to_pro(cust.customer_id)
    invoice = stripe.get_invoice(cust.customer_id)
    print(f"✓ Upgraded: €{invoice['amount']}/month")
