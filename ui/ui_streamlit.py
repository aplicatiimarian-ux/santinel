# ============================================================
# SANTINEL — STREAMLIT UI DASHBOARD
# Week 2: Real-time coaching display + session management
# ============================================================

import streamlit as st
import pandas as pd
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from module.session_complete import SessionManager
from bridge.aegis_bridge import AEGISBridge, ContextInjector

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="SANTINEL — AI Coaching",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE
# ============================================================

if "session_manager" not in st.session_state:
    st.session_state.session_manager = None

if "aegis_bridge" not in st.session_state:
    st.session_state.aegis_bridge = AEGISBridge()

if "active_session" not in st.session_state:
    st.session_state.active_session = None

if "sessions_history" not in st.session_state:
    st.session_state.sessions_history = []

if "coaching_log" not in st.session_state:
    st.session_state.coaching_log = []

# ============================================================
# SIDEBAR — NAVIGATION
# ============================================================

with st.sidebar:
    st.title("🎙️ SANTINEL")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📞 New Session", "📋 History", "📊 Analytics", "⚙️ Settings"]
    )
    
    st.markdown("---")
    st.subheader("Status")
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.active_session:
            st.success("✅ Session Active")
        else:
            st.info("⏸️ No Session")
    with col2:
        if st.session_state.aegis_bridge.available:
            st.success("✅ AEGIS Ready")
        else:
            st.warning("⚠️ AEGIS Mock")

# ============================================================
# PAGE: HOME
# ============================================================

if page == "🏠 Home":
    st.title("SANTINEL — AI Coaching Assistant")
    st.markdown("Real-time negotiation coaching powered by AI + Intelligence")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sessions", len(st.session_state.sessions_history), "total")
    
    with col2:
        successful = sum(1 for s in st.session_state.sessions_history if s.get("outcome") == "success")
        st.metric("Success Rate", f"{successful}/{len(st.session_state.sessions_history)}" if st.session_state.sessions_history else "N/A")
    
    with col3:
        st.metric("Coaching Tips", len(st.session_state.coaching_log))
    
    with col4:
        st.metric("AEGIS Status", "✅ Connected" if st.session_state.aegis_bridge.available else "⚠️ Mock")
    
    st.markdown("---")
    
    st.subheader("Quick Start")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Start New Session", key="home_start"):
            st.session_state.page = "📞 New Session"
            st.rerun()
    
    with col2:
        if st.button("📋 View History", key="home_history"):
            st.session_state.page = "📋 History"
            st.rerun()
    
    st.markdown("---")
    st.subheader("Recent Coaching Tips")
    
    if st.session_state.coaching_log:
        for tip in st.session_state.coaching_log[-3:]:
            with st.container():
                st.markdown(f"**{tip['timestamp']}** — {tip['provider']}")
                st.write(tip['suggestion'][:200] + "...")
    else:
        st.info("No coaching tips yet. Start a session to get coaching!")

# ============================================================
# PAGE: NEW SESSION
# ============================================================

elif page == "📞 New Session":
    st.title("Start New Coaching Session")
    
    col1, col2 = st.columns(2)
    
    with col1:
        contact_name = st.text_input("Contact Name", placeholder="e.g., Ion Popescu")
    
    with col2:
        company_name = st.text_input("Company Name", placeholder="e.g., ABC SRL")
    
    st.markdown("---")
    
    if contact_name and company_name:
        st.subheader("📊 Pre-Call Intelligence")
        
        # Get AEGIS context
        injector = ContextInjector(st.session_state.aegis_bridge)
        context = injector.prepare_coaching_context(contact_name, company_name)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Contact Info")
            st.write(f"**Name:** {context['contact'].get('name', 'N/A')}")
            st.write(f"**Company:** {context['company'].get('name', 'N/A')}")
            st.write(f"**Role:** {context['contact'].get('role', 'N/A')}")
            st.write(f"**Experience:** {context['contact'].get('experience', 'N/A')}")
        
        with col2:
            st.subheader("Risk Profile")
            risk = context['risk_profile']
            if risk == "high":
                st.error(f"⚠️ HIGH RISK")
            elif risk == "medium":
                st.warning(f"⚠️ MEDIUM RISK")
            else:
                st.success(f"✅ LOW RISK")
            
            st.write(f"**Financial Status:** {context['company'].get('financial_status', 'N/A')}")
            st.write(f"**Previous Deals:** {len(context['history'])}")
        
        st.markdown("---")
        
        st.subheader("💡 Coaching Recommendations")
        for i, rec in enumerate(context['recommendations'], 1):
            st.write(f"{i}. {rec}")
        
        st.markdown("---")
        
        if st.button("▶️ Start Session", key="start_session"):
            # Initialize session
            session_mgr = SessionManager(user_id="user_001")
            session_mgr.start_session(contact_name, company_name)
            
            st.session_state.active_session = {
                "session_id": session_mgr.session_id,
                "manager": session_mgr,
                "contact_name": contact_name,
                "company_name": company_name,
                "context": context,
                "started_at": datetime.now(timezone.utc).isoformat()
            }
            
            st.success(f"✅ Session started: {session_mgr.session_id}")
            st.rerun()
    else:
        st.info("Enter contact and company name to view intelligence")

# ============================================================
# PAGE: ACTIVE SESSION (During Call)
# ============================================================

if st.session_state.active_session:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎙️ Active Session")
    st.sidebar.write(f"Contact: {st.session_state.active_session['contact_name']}")
    st.sidebar.write(f"Company: {st.session_state.active_session['company_name']}")
    
    if st.sidebar.button("⏹️ End Session", key="end_session"):
        session_mgr = st.session_state.active_session["manager"]
        result = session_mgr.end_session()
        
        st.session_state.sessions_history.append({
            "session_id": result['session_id'],
            "contact": st.session_state.active_session['contact_name'],
            "company": st.session_state.active_session['company_name'],
            "duration": result['summary']['duration'],
            "outcome": "success",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        st.session_state.active_session = None
        st.success("✅ Session ended and saved")
        st.rerun()
    
    # Real-time coaching input
    if page == "📞 New Session":
        st.markdown("---")
        st.subheader("💬 Real-Time Coaching")
        
        situation = st.text_area(
            "Describe current situation:",
            placeholder="e.g., Contact says they can only offer 10% discount, I need 20%",
            height=100
        )
        
        if st.button("💡 Get Coaching", key="get_coaching"):
            session_mgr = st.session_state.active_session["manager"]
            coaching = session_mgr.get_real_time_coaching(situation)
            
            if coaching['status'] == 'success':
                st.success("✅ Coaching suggestion:")
                st.write(coaching['coaching'])
                
                st.session_state.coaching_log.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "provider": coaching.get('provider', 'unknown'),
                    "suggestion": coaching['coaching']
                })
            else:
                st.error(f"Error: {coaching.get('message', 'Unknown error')}")

# ============================================================
# PAGE: HISTORY
# ============================================================

elif page == "📋 History":
    st.title("Session History")
    
    if st.session_state.sessions_history:
        df = pd.DataFrame(st.session_state.sessions_history)
        st.dataframe(df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("Session Details")
        
        selected_session = st.selectbox(
            "Select session:",
            [f"{s['contact']} @ {s['company']} ({s['timestamp'][:10]})" for s in st.session_state.sessions_history]
        )
        
        if selected_session:
            idx = [f"{s['contact']} @ {s['company']} ({s['timestamp'][:10]})" for s in st.session_state.sessions_history].index(selected_session)
            session = st.session_state.sessions_history[idx]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Duration", f"{session['duration']}s")
            with col2:
                st.metric("Outcome", session['outcome'])
            with col3:
                st.metric("Date", session['timestamp'][:10])
    else:
        st.info("No sessions yet. Start a new session to see history.")

# ============================================================
# PAGE: ANALYTICS
# ============================================================

elif page == "📊 Analytics":
    st.title("Analytics Dashboard")
    
    if st.session_state.sessions_history:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = len(st.session_state.sessions_history)
            st.metric("Total Sessions", total)
        
        with col2:
            successful = sum(1 for s in st.session_state.sessions_history if s.get("outcome") == "success")
            rate = (successful / total * 100) if total > 0 else 0
            st.metric("Success Rate", f"{rate:.0f}%")
        
        with col3:
            total_time = sum(s.get("duration", 0) for s in st.session_state.sessions_history)
            st.metric("Total Time", f"{total_time}s")
        
        with col4:
            st.metric("Coaching Tips", len(st.session_state.coaching_log))
        
        st.markdown("---")
        
        st.subheader("Sessions by Company")
        companies = pd.DataFrame(st.session_state.sessions_history)['company'].value_counts()
        st.bar_chart(companies)
        
        st.markdown("---")
        
        st.subheader("Coaching Log")
        for log in st.session_state.coaching_log[-10:]:
            st.write(f"**{log['timestamp']}** ({log['provider']}): {log['suggestion'][:150]}...")
    else:
        st.info("No analytics yet. Start sessions to see metrics.")

# ============================================================
# PAGE: SETTINGS
# ============================================================

elif page == "⚙️ Settings":
    st.title("Settings")
    
    st.subheader("AEGIS Connection")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"Status: {'✅ Connected' if st.session_state.aegis_bridge.available else '⚠️ Mock Mode'}")
    
    with col2:
        if st.button("🔄 Reconnect AEGIS"):
            st.session_state.aegis_bridge = AEGISBridge()
            st.rerun()
    
    st.markdown("---")
    
    st.subheader("Export Data")
    if st.button("📥 Export Sessions as JSON"):
        data = {
            "sessions": st.session_state.sessions_history,
            "coaching_log": st.session_state.coaching_log
        }
        json_str = json.dumps(data, indent=2)
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name="santinel_export.json",
            mime="application/json"
        )
    
    st.markdown("---")
    
    st.subheader("System Info")
    st.write(f"**Version:** SANTINEL Week 2")
    st.write(f"**Build:** UI_STREAMLIT.PY")
    st.write(f"**Timestamp:** {datetime.now(timezone.utc).isoformat()}")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown("""
<center>
🎙️ SANTINEL — AI Coaching Assistant for Negotiations<br>
Powered by Groq + AEGIS Veritas Intelligence<br>
© 2026 SANTINEL Project
</center>
""", unsafe_allow_html=True)