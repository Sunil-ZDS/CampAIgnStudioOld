#pipeline.py
from services.openai_config import create_azure_openai_model
from database.db_manager import DatabaseManager
from agents.analyst_agent import AnalystAgent
from agents.strategy_agent import StrategyAgent
from agents.creative_agent import CreativeAgent
from agents.orchestrator_agent import OrchestratorAgent
from models.response_models import CampaignBrief
import json
import streamlit as st
import asyncio
import os
from typing import Callable, Optional


class EnhancedMarketingCampaignPipeline:
    def __init__(self, model, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.analyst_agent = AnalystAgent(model, db_manager)
        self.strategy_agent = StrategyAgent(model)
        self.creative_agent = CreativeAgent(model)
        self.orchestrator_agent = OrchestratorAgent(model)

    async def run_enhanced_campaign(
        self, 
        campaign_objective: str, 
        target_industry: str = None, 
        status_callback: Optional[Callable[[str], None]] = None,
        campaign_budget: str = None, 
        campaign_timing: str = None, 
        campaign_destination_url: str = None,
        media_objective: str = None, 
        media_target: str = None
    ) -> CampaignBrief:

        # Helper to send status and also print to console for debugging
        def update_status(message: str):
            if status_callback:
                status_callback(message)
            print(message)

        try:
            update_status("📊 Step 1: AnalystAgent - Analyzing Historical Campaign Data...")    
            analysis_result = await self.analyst_agent.analyze_campaign_patterns(
                campaign_objective, target_industry
            )
            update_status("✅ AnalystAgent: Analysis completed!")

            update_status("🎯 Step 2: StrategyAgent - Developing Data-Driven Strategy...")
            strategy_result = await self.strategy_agent.develop_strategy(
                campaign_objective, target_industry, analysis_result,
                campaign_budget=campaign_budget,
                campaign_timing=campaign_timing,
                campaign_destination_url=campaign_destination_url,
                media_objective=media_objective,
                media_target=media_target
            )
            update_status("✅ StrategyAgent: Data-driven strategy completed!")

            update_status("🎨 Step 3: CreativeAgent - Creating Performance-Optimized Creative...")
            creative_result = await self.creative_agent.develop_creative(
                campaign_objective, target_industry, strategy_result, analysis_result,
                campaign_budget=campaign_budget,
                campaign_timing=campaign_timing,
                campaign_destination_url=campaign_destination_url,
                media_objective=media_objective,
                media_target=media_target
            )
            update_status("✅ CreativeAgent: Performance-optimized creative completed!")

            update_status("🎬 Step 4: OrchestratorAgent - Finalizing Data-Enhanced Campaign Brief...")
            final_result = await self.orchestrator_agent.finalize_campaign_brief(
                campaign_objective, target_industry, analysis_result, strategy_result, creative_result,
                campaign_budget=campaign_budget,
                campaign_timing=campaign_timing,
                campaign_destination_url=campaign_destination_url,
                media_objective=media_objective,
                media_target=media_target
            )
            update_status("✅ OrchestratorAgent: Data-enhanced campaign brief completed!")
            
            return final_result
            
        except Exception as e:
            error_msg = f"Error in pipeline step: {str(e)}"
            update_status(f"❌ {error_msg}")
            raise Exception(error_msg)

async def run_pipeline_from_ui(
    campaign_details: dict, 
    status_callback: Optional[Callable[[str], None]] = None
) -> CampaignBrief:
    """
    Main pipeline function called from the UI.
    Returns the final campaign brief or raises an exception.
    """
    # Helper to send status and also print to console for debugging
    def update_status(message: str):
        if status_callback:
            status_callback(message)
        print(message)

    db_manager = None
    
    try:
        # Set up database connection and model inside this function for self-containment
        update_status("🚀 Initializing AI model and database connection...")
        
        azure_model = create_azure_openai_model()
        if not azure_model:
            raise Exception("Azure OpenAI model creation failed. Check your configuration.")
        update_status("✅ AI model initialized successfully!")

        # Database configuration
        db_config = {
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "database": os.getenv("DB_NAME", "marketing_campaigns")
        }
        
        # Validate database configuration
        missing_config = [k for k, v in db_config.items() if not v]
        if missing_config:
            raise Exception(f"Missing database configuration: {missing_config}")
        
        db_manager = DatabaseManager(db_config)

        # Extract campaign details
        campaign_objective = campaign_details.get("campaign_objective")
        if not campaign_objective:
            raise Exception("Campaign objective is required")
            
        campaign_budget = campaign_details.get("campaign_budget")
        campaign_timing = campaign_details.get("campaign_timing")
        campaign_destination_url = campaign_details.get("campaign_destination_url")
        media_objective = campaign_details.get("media_objective")
        media_target = campaign_details.get("media_target")
        target_industry = campaign_details.get("target_industry")

        # Initialize database
        update_status("🗄️ Initializing database connection...")
        await db_manager.initialize_database()
        
        # Only populate sample data if needed (check if data exists first)
        update_status("📊 Checking and populating sample data...")
        await db_manager.populate_sample_data()

        update_status("🎉 Starting enhanced campaign generation...")
        pipeline = EnhancedMarketingCampaignPipeline(azure_model, db_manager)
        
        final_campaign = await pipeline.run_enhanced_campaign(
            campaign_objective, 
            target_industry, 
            status_callback=status_callback,
            campaign_budget=campaign_budget,
            campaign_timing=campaign_timing,
            campaign_destination_url=campaign_destination_url,
            media_objective=media_objective,
            media_target=media_target
        )
        
        update_status("✅ Campaign pipeline execution complete!")
        return final_campaign
        
    except Exception as e:
        error_msg = f"Pipeline execution failed: {str(e)}"
        update_status(f"❌ {error_msg}")
        raise Exception(error_msg)
        
    finally:
        # Always clean up database connection
        if db_manager:
            try:
                update_status("⏳ Closing database connection...")
                await db_manager.close()
                update_status("✅ Database connection closed.")
            except Exception as e:
                print(f"Warning: Error closing database connection: {e}")

# --- Helper: Use Azure OpenAI to detect which sections to update ---
async def detect_sections_to_update_async(feedback, campaign_brief):
    try:
        azure_model = create_azure_openai_model()
        from pydantic_ai import Agent
        system_prompt = (
            "You are an assistant that helps identify which sections of a marketing campaign brief need updates. "
            "Sections and their triggers:\n"
            "- 'analyst': market data, research, competitor analysis, insights\n"
            "- 'strategy': targeting, positioning, channels, budget allocation\n"
            "- 'creative': taglines, visuals, ad copy, brand voice, slogans\n"
            "- 'campaign': timelines, objectives, URLs, media planning\n"
            "Respond ONLY with JSON: {\"analyst\": bool, \"strategy\": bool, \"creative\": bool, \"campaign\": bool}"
        )
        user_prompt = (
            f"User feedback: \"{feedback}\"\n"
            f"Current campaign brief summary: {str(campaign_brief)[:500]}...\n"
            "Analyze the feedback and return which sections need updates as a JSON object."
        )
        agent = Agent(
            model=azure_model,
            result_type=str,
            system_prompt=system_prompt
        )
        result = await agent.run(user_prompt)
        try:
            parsed_result = json.loads(result.output)
        except (json.JSONDecodeError, AttributeError):
            import re
            json_match = re.search(r'\{[^}]+\}', str(result.output))
            if json_match:
                parsed_result = json.loads(json_match.group())
            else:
                raise ValueError("Could not parse JSON from response")
        section_flags = {
            'analyst': bool(parsed_result.get('analyst', False)),
            'strategy': bool(parsed_result.get('strategy', False)),
            'creative': bool(parsed_result.get('creative', False)),
            'campaign': bool(parsed_result.get('campaign', False))
        }
        return section_flags
    except Exception as e:
        st.error(f"Error in section detection: {str(e)}")
        feedback_lower = feedback.lower()
        return {
            'analyst': any(word in feedback_lower for word in ['data', 'analysis', 'insight', 'research', 'competitor']),
            'strategy': any(word in feedback_lower for word in ['strategy', 'target', 'position', 'channel', 'budget']),
            'creative': any(word in feedback_lower for word in ['creative', 'tagline', 'visual', 'copy', 'slogan', 'brand', 'message']),
            'campaign': any(word in feedback_lower for word in ['timeline', 'schedule', 'url', 'landing page', 'media plan'])
        }
    


def detect_sections_to_update(feedback, campaign_brief):
    try:
        return asyncio.run(detect_sections_to_update_async(feedback, campaign_brief))
    except Exception as e:
        st.error(f"Error in section detection wrapper: {str(e)}")
        feedback_lower = feedback.lower()
        return {
            'analyst': any(word in feedback_lower for word in ['data', 'analysis', 'insight', 'research', 'competitor']),
            'strategy': any(word in feedback_lower for word in ['strategy', 'target', 'position', 'approach']),
            'creative': any(word in feedback_lower for word in ['creative', 'message', 'brand', 'voice', 'visual', 'content', 'copy']),
            'campaign': any(word in feedback_lower for word in ['budget', 'timing', 'objective', 'goal'])
        }