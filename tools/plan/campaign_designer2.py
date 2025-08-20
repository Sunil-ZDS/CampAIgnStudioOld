# tools/plan/campaign_designer.py

import streamlit as st
import asyncio
import threading
import queue
import time

from core.pipeline import run_pipeline_from_ui, detect_sections_to_update
from agents.orchestrator_agent import OrchestratorAgent
from services.openai_config import create_azure_openai_model


def show_campaign_designer():
    st.markdown("## 🎯 Campaign Designer – Generate Your Brief")

    # Initialize session state defaults
    default_values = {
        'pipeline_thread': None,
        'pipeline_running': False,
        'pipeline_result': None,
        'pipeline_error': None,
        'status_queue': queue.Queue(),
        'analysis_result': None,
        'strategy_result': None,
        'creative_result': None,
        'campaign_objective': None,
        'target_industry': None,
        'campaign_details': None,
        'chat_history': [],
        'azure_model': None,
        'current_status': None,
        'revision_in_progress': False
    }

    for key, default in default_values.items():
        if key not in st.session_state:
            if key == 'azure_model':
                try:
                    st.session_state[key] = create_azure_openai_model()
                except Exception as e:
                    st.error(f"Failed to initialize Azure OpenAI model: {str(e)}")
                    st.session_state[key] = None
            else:
                st.session_state[key] = default

    # Main form
    with st.form("campaign_form"):
        st.markdown('<div class="section">', unsafe_allow_html=True)

        campaign_objective = st.text_area(
            "🎯 Campaign Objective",
            placeholder="e.g., Create a digital campaign for Huggies targeting new parents",
            help="Clearly define what you want the campaign to achieve.",
            key="campaign_objective_input"
        )

        media_objective = st.text_input(
            "🎯 Media Objective",
            placeholder="e.g., Maximize reach among new parents",
            help="What is the main goal for media?",
            key="media_objective_input"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            target_industry = st.text_input(
                "🏭 Target Industry",
                placeholder="e.g., baby care",
                help="Specify the industry for more focused insights. Leave blank for general.",
                key="industry_input"
            )

        with col2:
            campaign_budget = st.text_input(
                "💰 Campaign Budget (USD)",
                placeholder="e.g., 50000",
                help="Enter the total budget for the campaign.",
                key="campaign_budget_input"
            )

        with col3:
            campaign_timing = st.text_input(
                "📅 Campaign Timing",
                placeholder="e.g., Q3 2024 or 2024-07-01 to 2024-09-30",
                help="Specify the campaign duration or timing.",
                key="campaign_timing_input"
            )

        col4, col5 = st.columns(2)

        with col4:
            campaign_destination_url = st.text_input(
                "🔗 Campaign Destination URL",
                placeholder="e.g., https://yourlandingpage.com", 
                help="Where should the campaign traffic be directed?",
                key="campaign_url_input"
            )

        with col5:
            media_target = st.text_input(
                "👥 Media (Audience) Target",
                placeholder="e.g., Parents aged 25-35 in urban areas",
                help="Describe the audience you want to target.",
                key="media_target_input"
            )

        submitted = st.form_submit_button("Generate Campaign Brief",
                                          disabled=st.session_state.pipeline_running or st.session_state.revision_in_progress)

        if submitted and not st.session_state.pipeline_running and not st.session_state.revision_in_progress:
            if not campaign_objective:
                st.error("Please enter a Campaign Objective.")
            else:
                # Reset session state
                st.session_state.pipeline_running = True
                st.session_state.pipeline_result = None
                st.session_state.pipeline_error = None
                st.session_state.current_status = None
                st.session_state.chat_history = []

                while not st.session_state.status_queue.empty():
                    try:
                        st.session_state.status_queue.get_nowait()
                    except queue.Empty:
                        break

                campaign_details = {
                    "campaign_objective": campaign_objective,
                    "media_objective": media_objective,
                    "target_industry": target_industry.strip() if target_industry else None,
                    "campaign_budget": campaign_budget,
                    "campaign_timing": campaign_timing,
                    "campaign_destination_url": campaign_destination_url.strip() if campaign_destination_url else None,
                    "media_target": media_target.strip() if media_target else None
                }

                st.session_state.campaign_objective = campaign_objective
                st.session_state.target_industry = target_industry.strip() if target_industry else None
                st.session_state.campaign_details = campaign_details

                st.session_state.pipeline_thread = threading.Thread(
                    target=run_pipeline_in_thread,
                    args=(campaign_details, st.session_state.status_queue)
                )
                st.session_state.pipeline_thread.start()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Status updates and polling
    if st.session_state.pipeline_running:
        status_placeholder = st.empty()
        messages_processed = 0
        while not st.session_state.status_queue.empty() and messages_processed < 10:
            try:
                message = st.session_state.status_queue.get_nowait()
                messages_processed += 1
                if isinstance(message, dict):
                    if "status" in message:
                        st.session_state.current_status = message["status"]
                    elif "result" in message:
                        st.session_state.pipeline_result = message["result"]
                        st.session_state.pipeline_running = False
                        break
                    elif "error" in message:
                        st.session_state.pipeline_error = message["error"]
                        st.session_state.pipeline_running = False
                        break
                    elif "done" in message:
                        st.session_state.pipeline_running = False
                        break
            except queue.Empty:
                break

        if st.session_state.current_status:
            status_placeholder.info(st.session_state.current_status)
        else:
            status_placeholder.info("Initializing pipeline...")

        if st.session_state.pipeline_running:
            time.sleep(1)
            st.rerun()

    # Display results
    if st.session_state.pipeline_result:
        campaign_brief = st.session_state.pipeline_result
        st.success("✅ Campaign brief generated successfully!")

        st.markdown('<h2 class="section-title">📋 Data-Driven Campaign Brief</h2>', unsafe_allow_html=True)

        def display_section(header: str, content: str):
            st.markdown(f'<div class="section-header">{header}</div>', unsafe_allow_html=True)
            if isinstance(content, str):
                lines = [line.strip() for line in content.split('.') if line.strip()]
                for line in lines:
                    st.markdown(f"- {line}")
            elif isinstance(content, list):
                for item in content:
                    st.markdown(f"- {item}")

        # Executive Summary
        if hasattr(campaign_brief, 'executive_summary'):
            display_section("📊 Executive Summary", campaign_brief.executive_summary)

        # Strategy Overview
        if hasattr(campaign_brief, 'strategy_overview'):
            display_section("🎯 Strategy Overview", campaign_brief.strategy_overview)

        # Creative Direction
        if hasattr(campaign_brief, 'creative_direction'):
            display_section("🎨 Creative Direction", campaign_brief.creative_direction)

        # Implementation Plan
        if hasattr(campaign_brief, 'implementation_plan'):
            display_section("🚀 Implementation Plan", campaign_brief.implementation_plan)

        # Success Metrics
        if hasattr(campaign_brief, 'success_metrics'):
            st.markdown('<div class="section-header">📈 Success Metrics</div>', unsafe_allow_html=True)
            metrics = campaign_brief.success_metrics
            if isinstance(metrics, list):
                for metric in metrics:
                    st.markdown(f"- {metric}")
            else:
                for line in metrics.split("."):
                    st.markdown(f"- {line.strip()}")

        # Analyst Insights
        if hasattr(campaign_brief, 'analyst_insights'):
            st.markdown('<div class="section-header">📊 Analyst Insights</div>', unsafe_allow_html=True)
            for line in campaign_brief.analyst_insights.split("."):
                st.markdown(f"- {line.strip()}")

        # Next Steps
        if hasattr(campaign_brief, 'next_steps'):
            st.markdown('<div class="section-header">⏭ Next Steps</div>', unsafe_allow_html=True)
            next_steps = campaign_brief.next_steps
            if isinstance(next_steps, list):
                for step in next_steps:
                    st.markdown(f"- {step}")
            else:
                for step in next_steps.split("."):
                    st.markdown(f"- {step.strip()}")

    # Interactive feedback section
    st.markdown('<h3 class="section-subtitle">💬 Request a Change or Revision</h3>', unsafe_allow_html=True)

    if st.session_state.chat_history:
        for entry in st.session_state.chat_history:
            if entry["role"] == "user":
                st.markdown(f'<div class="user-msg"><b>You:</b> {entry["content"]}</div>')
            elif entry["role"] == "assistant":
                st.markdown(f'<div class="ai-msg"><b>CampAIgn:</b> {entry["content"]}</div>')

    if st.session_state.revision_in_progress:
        st.info("🔄 Processing your revision request... Please wait.")

    with st.form("feedback_form", clear_on_submit=True):
        user_feedback = st.text_input(
            "Type your feedback or revision request:",
            placeholder="e.g., 'Change the creative assets and brand voice'",
            key="feedback_input",
            disabled=st.session_state.revision_in_progress
        )
        submit_feedback = st.form_submit_button("Submit Revision Request",
                                                disabled=st.session_state.revision_in_progress)

        if submit_feedback and user_feedback:
            st.session_state.revision_in_progress = True
            st.session_state.feedback_text = user_feedback
            st.rerun()

        if st.session_state.revision_in_progress and user_feedback:
            try:
                campaign_brief = st.session_state.pipeline_result
                sections = detect_sections_to_update(user_feedback, campaign_brief)
                if not any(sections.values()):
                    st.error("Couldn't detect specific sections to update. Please clarify your request.")
                    st.session_state.revision_in_progress = False
                    st.rerun()

                model = st.session_state.azure_model
                if not model:
                    raise Exception("Azure OpenAI model not initialized")
                orchestrator = OrchestratorAgent(model)
                updated_brief = asyncio.run(
                    orchestrator.handle_revision(
                        current_brief=campaign_brief,
                        feedback=user_feedback,
                        sections_to_update=sections
                    )
                )

                st.session_state.pipeline_result = updated_brief
                st.session_state.chat_history.append({
                    "user": user_feedback,
                    "ai": f"Successfully updated the following sections: {', '.join([k for k, v in sections.items() if v])}"
                })

            except Exception as e:
                st.error(f"Revision failed: {str(e)}")
                print(f"Revision error: {str(e)}")
            finally:
                st.session_state.revision_in_progress = False
                st.rerun()

    # Display errors
    if st.session_state.pipeline_error:
        st.error(f"Error: {st.session_state.pipeline_error}")

    # Back button
    if st.button("⬅ Back to Tools"):
        st.session_state.current_tool = None
        st.session_state.current_section = "Plan"
        st.rerun()


# --- Pipeline Execution Function ---
def run_pipeline_in_thread(campaign_details: dict, q: queue.Queue):
    def thread_status_callback(message: str):
        q.put({"status": message})

    try:
        result = asyncio.run(run_pipeline_from_ui(campaign_details, status_callback=thread_status_callback))
        if isinstance(result, dict) and "analysis_result" in result:
            st.session_state.analysis_result = result.get("analysis_result")
            st.session_state.strategy_result = result.get("strategy_result")
            st.session_state.creative_result = result.get("creative_result")
            final_result = result.get("final_campaign")
        else:
            final_result = result
        q.put({"result": final_result})
    except Exception as e:
        q.put({"error": str(e)})
    finally:
        q.put({"done": True})