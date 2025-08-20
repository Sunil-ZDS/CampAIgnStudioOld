# app.py - Streamlit UI

import streamlit as st
import asyncio
import nest_asyncio
import threading
import queue
import os
import sys

# Apply nest_asyncio for Streamlit compatibility with asyncio
nest_asyncio.apply()

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import modules
from core.pipeline import run_pipeline_from_ui
from agents.orchestrator_agent import OrchestratorAgent
from services.openai_config import create_azure_openai_model
from core.pipeline import detect_sections_to_update

# Cleanup function
async def cleanup_openai_client():
    """Safely close the Azure OpenAI async client"""
    global AZURE_CLIENT
    if AZURE_CLIENT:
        await AZURE_CLIENT.aclose()
        print("✅ Azure OpenAI client closed safely.")

if "azure_model" not in st.session_state:
    st.session_state.azure_model = asyncio.run(create_azure_openai_model())

# Set page config
st.set_page_config(layout="wide", page_title="CampAIgn Studio", page_icon="🚀")

# Load custom CSS
def load_css():
    css_file = os.path.join(project_root, "styles.css")
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom CSS file not found.")

# Run at start
load_css()

# --- LOGO ---
LOCAL_LOGO_PATH = os.path.join(project_root, "images", "ZDSLogo.jpg")
if os.path.exists(LOCAL_LOGO_PATH):
    st.image(LOCAL_LOGO_PATH, width=60)

# App title with logo
st.markdown("""
<style>
.title-container {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 8px;
}
.logo-title {
    font-size: 2em;
    font-weight: bold;
    background: linear-gradient(90deg, #7b1fa2, #3f51b5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="title-container">
    <span style="font-size: 2em;">🚀</span>
    <div class="logo-title">CampAIgn Studio</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<p class='tagline'>Where Campaigns Are Crafted by Intelligence</p>",
            unsafe_allow_html=True)
st.markdown("<p class='tagline'>Your Unified Marketing Command Center to Plan smarter, Create faster, Launch confidently, Optimize continuously, Report transparently</p>",
            unsafe_allow_html=True)

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'current_phase' not in st.session_state:
    st.session_state['current_phase'] = "Plan"
if 'current_tool' not in st.session_state:
    st.session_state['current_tool'] = None

# --- LOGIN PAGE ---
if not st.session_state['logged_in']:
    st.subheader("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username == "admin" and password == "ZDS@2021":
            st.session_state['logged_in'] = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

else:
    # Tool Sections Navigation
    st.markdown("### 🛠️ Navigate Your Campaign Lifecycle")
    phase_options = ["Plan", "Create", "Launch", "Optimize", "Report", "Ask CampAIgn"]
    cols = st.columns(len(phase_options))

    for i, phase in enumerate(phase_options):
        if cols[i].button(phase, use_container_width=True):
            st.session_state.current_phase = phase
            st.session_state.current_tool = None
            st.rerun()

    current_phase = st.session_state.get('current_phase', 'Plan')

    def navigate_to(tool_name):
        st.session_state.current_tool = tool_name
        st.session_state.current_phase = None
        st.rerun()

    # TOOL LOADER
    current_tool = st.session_state.get('current_tool', None)

    if current_tool == "campaign_designer":
        from tools.plan.campaign_designer import show_campaign_designer
        show_campaign_designer()
    elif current_tool == "audience_research_and_persona_builder":
        st.info("👥 Audience Research & Persona Builder – Coming soon...")
    elif current_tool == "competitive_intelligence_tool":
        st.info("📊 Competitive Intelligence Tool – Coming soon...")
    elif current_tool == "media_planner_and_budget_allocator":
        st.info("💰 Media Planner & Budget Allocator – Coming soon...")
    elif current_tool == "performance_forecasting_engine":
        st.info("📈 Performance Forecasting Engine – Coming soon...")
    elif current_tool == "creative_asset_generator":
        st.info("📝 Creative Asset Generator – Coming soon...")
    elif current_tool == "influencer_matching_and_briefing_tool":
        st.info("🤝 Influencer Matching & Briefing Tool – Coming soon...")
    elif current_tool == "landing_page_analyzer":
        st.info("🔗 Landing Page Analyzer – Coming soon...")
    elif current_tool == "brand_voice_checker":
        st.info("🗣️ Brand Voice & Messaging Consistency Checker – Coming soon...")
    elif current_tool == "ad_copy_compliance":
        st.info("📄 Ad Copy Compliance Checker – Coming soon...")
    elif current_tool == "legal_assistant":
        st.info("⚖️ Legal & Compliance Assistant – Coming soon...")
    elif current_tool == "crisis_response":
        st.info("📢 Crisis Response Generator – Coming soon...")
    elif current_tool == "campaign_optimizer":
        st.info("⚙️ Campaign Optimizer – Coming soon...")
    elif current_tool == "ab_testing":
        st.info("🧪 A/B Testing Assistant – Coming soon...")
    elif current_tool == "reporting_dashboard":
        st.info("📈 Multi-Channel Reporting Dashboard – Coming soon...")
    elif current_tool == "pitch_deck_generator":
        st.info("📁 Client Pitch Deck Generator – Coming soon...")
    elif current_tool == "ask_campaigntool":
        # st.info("💬 Ask CampAIgn – Coming soon...")
        from services.openai_config import create_azure_openai_model, get_azure_openai_model
        from tools.q_and_a.campaigntool_qa import show_ask_campaign_chat
        # Only create if not already created
        if get_azure_openai_model() is None:
            st.session_state.azure_model = asyncio.run(create_azure_openai_model())

        asyncio.run(show_ask_campaign_chat())

    else:
        # Show tools based on selected phase
        if current_phase == "Plan":
            st.markdown("### 📋 Plan Phase – Strategy & Research Tools")
            if st.button("🎯 Campaign Designer - Generate full AI-powered campaign briefs based on objectives, audience, budget.", use_container_width=True):
                navigate_to("campaign_designer")
            if st.button("👥 Audience Research & Persona Builder - Build detailed customer personas and audience segments.", use_container_width=True):
                navigate_to("audience_research_and_persona_builder")
            if st.button("🔍 Competitive Intelligence Tool - Analyze competitors' campaigns and strategies.", use_container_width=True):
                navigate_to("competitive_intelligence_tool")
            if st.button("📊 Media Planner & Budget Allocator - Recommend optimal media mix and budget allocation.", use_container_width=True):
                navigate_to("media_planner_and_budget_allocator")
            if st.button("📈 Performance Forecasting Engine - Predict KPIs like CTR, conversion rate, ROAS before launch.", use_container_width=True):
                navigate_to("performance_forecasting_engine")

        elif current_phase == "Create":
            st.markdown("### 🎨 Create Phase – Creative Ideation Tools")
            if st.button("📝 Creative Asset Generator - Generate ad copy, headlines, CTAs, and visual ideas.", use_container_width=True):
                navigate_to("creative_asset_generator")
            if st.button("🤝 Influencer Matching & Briefing Tool - Find influencers and auto-generate briefing templates.", use_container_width=True):
                navigate_to("influencer_matching_and_briefing_tool")
            if st.button("🔗 Landing Page Analyzer - Evaluate and optimize landing pages for conversions.", use_container_width=True):
                navigate_to("landing_page_analyzer")
            if st.button("🗣️ Brand Voice & Messaging Consistency Checker - Ensure messaging aligns with brand tone and guidelines.", use_container_width=True):
                navigate_to("brand_voice_checker")

        elif current_phase == "Launch":
            st.markdown("### 🚀 Launch Phase – Execution & Readiness Tools")
            if st.button("📄 Ad Copy Compliance Checker - Ensure ad copy follows platform policies (Google, Meta, TikTok).", use_container_width=True):
                navigate_to("ad_copy_compliance")
            if st.button("⚖️ Legal & Compliance Assistant - Flag legal risks in campaign content.", use_container_width=True):
                navigate_to("legal_assistant")
            if st.button("📢 Crisis Response Generator - Draft PR responses or crisis comms during negative sentiment spikes.", use_container_width=True):
                navigate_to("crisis_response")

        elif current_phase == "Optimize":
            st.markdown("### 🔍 Optimize Phase – Performance Improvement Tools")
            if st.button("⚙️ Campaign Optimizer - Campaign Optimizer", use_container_width=True):
                navigate_to("campaign_optimizer")
            if st.button("🧪 A/B Testing Assistant - Help create and analyze A/B tests for creatives, landing pages, CTAs.", use_container_width=True):
                navigate_to("ab_testing")

        elif current_phase == "Report":
            st.markdown("### 📊 Report Phase – Analysis & Communication Tools")
            if st.button("📈 Multi-Channel Reporting Dashboard - Track performance across platforms in one centralized view.", use_container_width=True):
                navigate_to("reporting_dashboard")
            if st.button("📁 Client Pitch Deck Generator - Automatically generate client-facing pitch decks from campaign data.", use_container_width=True):
                navigate_to("pitch_deck_generator")

        elif current_phase == "Ask CampAIgn":
            st.markdown("### 💬 Ask CampAIgn – Ask Anything About Your Campaign")
            if st.button("🧠 Ask CampAIgn", use_container_width=True):
                navigate_to("ask_campaigntool")

                

# Footer
st.markdown("---")
st.markdown("<p class='footer'>Powered by <b>Zen Data Shastra</b></p>",
            unsafe_allow_html=True)