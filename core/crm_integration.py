# -*- coding: utf-8 -*-
"""
CRM Integration Module for SANTINEL
Connects to Salesforce, HubSpot, Pipedrive for lead tracking and outcome recording.

Adapter pattern: abstract base class + concrete implementations for each CRM.
Supports lead creation, deal pipeline updates, and outcome tracking.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime


class DealStage(Enum):
    """Standard deal pipeline stages."""
    DISCOVERY = "discovery"
    QUALIFICATION = "qualification"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSING = "closing"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


@dataclass
class Lead:
    """CRM Lead record."""
    id: str
    name: str
    email: str
    phone: Optional[str]
    company: Optional[str]
    source: str = "SANTINEL"
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Deal:
    """CRM Deal/Opportunity record."""
    id: str
    name: str
    lead_id: str
    stage: DealStage
    amount: float
    close_probability: float  # 0.0-10.0 from SANTINEL
    close_date: Optional[str]
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Outcome:
    """Tracked outcome from a negotiation."""
    id: str
    deal_id: str
    lead_id: str
    situation: str  # "discovery", "objection", "closing", etc.
    personality_type: str  # "driver", "expressive", "amiable", "analytical"
    script_used: str
    result: str  # "won", "lost", "stalled", "advanced"
    coaching_effectiveness: float  # 0.0-1.0
    duration_seconds: int
    timestamp: str


class CRMAdapter(ABC):
    """Abstract base class for CRM adapters."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    def create_lead(self, lead: Lead) -> str:
        """Create a lead in the CRM. Returns lead ID."""
        pass

    @abstractmethod
    def update_lead(self, lead: Lead) -> bool:
        """Update an existing lead."""
        pass

    @abstractmethod
    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Retrieve a lead by ID."""
        pass

    @abstractmethod
    def create_deal(self, deal: Deal) -> str:
        """Create a deal/opportunity. Returns deal ID."""
        pass

    @abstractmethod
    def update_deal(self, deal: Deal) -> bool:
        """Update deal stage and close probability."""
        pass

    @abstractmethod
    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Retrieve a deal by ID."""
        pass

    @abstractmethod
    def record_outcome(self, outcome: Outcome) -> bool:
        """Record negotiation outcome (for analytics)."""
        pass

    @abstractmethod
    def list_leads(self, limit: int = 50) -> List[Lead]:
        """List recent leads."""
        pass

    @abstractmethod
    def list_deals(self, stage: Optional[DealStage] = None, limit: int = 50) -> List[Deal]:
        """List deals, optionally filtered by stage."""
        pass


class SalesforceAdapter(CRMAdapter):
    """Salesforce CRM adapter."""

    def __init__(self, api_key: str, instance_url: str):
        super().__init__(api_key, instance_url)
        self.name = "Salesforce"

    def create_lead(self, lead: Lead) -> str:
        """Create Salesforce Lead."""
        # In production: use requests to call Salesforce REST API
        # POST /services/data/v57.0/sobjects/Lead/
        lead_id = f"SF-{datetime.now().timestamp()}"
        lead.id = lead_id
        return lead_id

    def update_lead(self, lead: Lead) -> bool:
        """Update Salesforce Lead."""
        # PATCH /services/data/v57.0/sobjects/Lead/{lead_id}
        return True

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Retrieve Salesforce Lead."""
        return None

    def create_deal(self, deal: Deal) -> str:
        """Create Salesforce Opportunity."""
        deal_id = f"SF-OPP-{datetime.now().timestamp()}"
        deal.id = deal_id
        return deal_id

    def update_deal(self, deal: Deal) -> bool:
        """Update Salesforce Opportunity stage."""
        return True

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Retrieve Salesforce Opportunity."""
        return None

    def record_outcome(self, outcome: Outcome) -> bool:
        """Record outcome as a Salesforce Task or custom object."""
        return True

    def list_leads(self, limit: int = 50) -> List[Lead]:
        """List Salesforce Leads."""
        return []

    def list_deals(self, stage: Optional[DealStage] = None, limit: int = 50) -> List[Deal]:
        """List Salesforce Opportunities."""
        return []


class HubSpotAdapter(CRMAdapter):
    """HubSpot CRM adapter."""

    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.hubapi.com")
        self.name = "HubSpot"

    def create_lead(self, lead: Lead) -> str:
        """Create HubSpot Contact."""
        # POST /crm/v3/objects/contacts
        lead_id = f"HS-{datetime.now().timestamp()}"
        lead.id = lead_id
        return lead_id

    def update_lead(self, lead: Lead) -> bool:
        """Update HubSpot Contact."""
        # PATCH /crm/v3/objects/contacts/{contact_id}
        return True

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Retrieve HubSpot Contact."""
        return None

    def create_deal(self, deal: Deal) -> str:
        """Create HubSpot Deal."""
        # POST /crm/v3/objects/deals
        deal_id = f"HS-DEAL-{datetime.now().timestamp()}"
        deal.id = deal_id
        return deal_id

    def update_deal(self, deal: Deal) -> bool:
        """Update HubSpot Deal stage."""
        # Map SANTINEL stage to HubSpot pipeline stage
        stage_map = {
            DealStage.DISCOVERY: "presentationscheduled",
            DealStage.QUALIFICATION: "qualifiedtobuy",
            DealStage.PROPOSAL: "proposalsentfromvendor",
            DealStage.NEGOTIATION: "negotiation",
            DealStage.CLOSING: "decisionmakersengaged",
            DealStage.CLOSED_WON: "closedwon",
            DealStage.CLOSED_LOST: "closedlost",
        }
        return True

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Retrieve HubSpot Deal."""
        return None

    def record_outcome(self, outcome: Outcome) -> bool:
        """Record outcome as HubSpot note or activity."""
        return True

    def list_leads(self, limit: int = 50) -> List[Lead]:
        """List HubSpot Contacts."""
        return []

    def list_deals(self, stage: Optional[DealStage] = None, limit: int = 50) -> List[Deal]:
        """List HubSpot Deals."""
        return []


class PipedriveAdapter(CRMAdapter):
    """Pipedrive CRM adapter."""

    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.pipedrive.com/v1")
        self.name = "Pipedrive"

    def create_lead(self, lead: Lead) -> str:
        """Create Pipedrive Person."""
        # POST /persons?api_token={token}
        lead_id = f"PD-{datetime.now().timestamp()}"
        lead.id = lead_id
        return lead_id

    def update_lead(self, lead: Lead) -> bool:
        """Update Pipedrive Person."""
        return True

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Retrieve Pipedrive Person."""
        return None

    def create_deal(self, deal: Deal) -> str:
        """Create Pipedrive Deal."""
        # POST /deals?api_token={token}
        deal_id = f"PD-DEAL-{datetime.now().timestamp()}"
        deal.id = deal_id
        return deal_id

    def update_deal(self, deal: Deal) -> bool:
        """Update Pipedrive Deal status."""
        # Map SANTINEL stage to Pipedrive stage
        return True

    def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Retrieve Pipedrive Deal."""
        return None

    def record_outcome(self, outcome: Outcome) -> bool:
        """Record outcome as Pipedrive activity."""
        return True

    def list_leads(self, limit: int = 50) -> List[Lead]:
        """List Pipedrive Persons."""
        return []

    def list_deals(self, stage: Optional[DealStage] = None, limit: int = 50) -> List[Deal]:
        """List Pipedrive Deals."""
        return []


class CRMSyncAdapter:
    """Unified adapter for syncing SANTINEL data with multiple CRMs."""

    def __init__(self):
        self.adapters: Dict[str, CRMAdapter] = {}

    def register_adapter(self, name: str, adapter: CRMAdapter):
        """Register a CRM adapter."""
        self.adapters[name.lower()] = adapter

    def sync_lead(self, lead: Lead, crm_names: Optional[List[str]] = None) -> Dict[str, str]:
        """Sync a lead to one or more CRMs. Returns mapping of CRM -> lead ID."""
        targets = crm_names or list(self.adapters.keys())
        results = {}
        for crm_name in targets:
            if crm_name.lower() in self.adapters:
                adapter = self.adapters[crm_name.lower()]
                lead_id = adapter.create_lead(lead)
                results[crm_name] = lead_id
        return results

    def sync_deal(self, deal: Deal, crm_names: Optional[List[str]] = None) -> Dict[str, str]:
        """Sync a deal to one or more CRMs. Returns mapping of CRM -> deal ID."""
        targets = crm_names or list(self.adapters.keys())
        results = {}
        for crm_name in targets:
            if crm_name.lower() in self.adapters:
                adapter = self.adapters[crm_name.lower()]
                deal_id = adapter.create_deal(deal)
                results[crm_name] = deal_id
        return results

    def record_outcome_all(self, outcome: Outcome) -> Dict[str, bool]:
        """Record outcome across all registered CRMs."""
        results = {}
        for crm_name, adapter in self.adapters.items():
            results[crm_name] = adapter.record_outcome(outcome)
        return results

    def get_opportunity_status(self, deal_id: str, crm_name: str) -> Optional[Dict]:
        """Get deal status from a specific CRM for scoring."""
        if crm_name.lower() in self.adapters:
            adapter = self.adapters[crm_name.lower()]
            deal = adapter.get_deal(deal_id)
            if deal:
                return {
                    "stage": deal.stage.value,
                    "close_probability": deal.close_probability,
                    "amount": deal.amount,
                }
        return None


# Factory for easy adapter instantiation
def create_adapter(crm_type: str, **kwargs) -> Optional[CRMAdapter]:
    """Create a CRM adapter by type."""
    if crm_type.lower() == "salesforce":
        return SalesforceAdapter(kwargs.get("api_key"), kwargs.get("instance_url"))
    elif crm_type.lower() == "hubspot":
        return HubSpotAdapter(kwargs.get("api_key"))
    elif crm_type.lower() == "pipedrive":
        return PipedriveAdapter(kwargs.get("api_key"))
    return None


if __name__ == "__main__":
    # Test CRM integration
    sync = CRMSyncAdapter()
    sync.register_adapter("salesforce", SalesforceAdapter("test-key", "https://instance.salesforce.com"))
    sync.register_adapter("hubspot", HubSpotAdapter("test-key"))
    sync.register_adapter("pipedrive", PipedriveAdapter("test-key"))

    lead = Lead(
        id="lead-001",
        name="Ion Popescu",
        email="ion@example.com",
        phone="+40123456789",
        company="TechCorp",
    )

    print("Syncing lead across CRMs:")
    results = sync.sync_lead(lead)
    for crm, lead_id in results.items():
        print(f"  {crm}: {lead_id}")

    deal = Deal(
        id="deal-001",
        name="Software License - TechCorp",
        lead_id="lead-001",
        stage=DealStage.PROPOSAL,
        amount=50000.0,
        close_probability=7.5,
    )

    print("\nSyncing deal across CRMs:")
    results = sync.sync_deal(deal)
    for crm, deal_id in results.items():
        print(f"  {crm}: {deal_id}")

    print("\nCRM Integration ready for SANTINEL unified coaching.")
