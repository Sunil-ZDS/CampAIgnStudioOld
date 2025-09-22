# # main.py
# from database.db_manager import DatabaseManager
# # from agents.analyst_agent import AnalystAgent
# # from agents.strategy_agent import StrategyAgent
# # from agents.creative_agent import CreativeAgent
# # from agents.orchestrator_agent import OrchestratorAgent
# from services.openai_config import create_azure_openai_model
# # from models.response_models import CampaignBrief

# import sys
# import os
# import asyncio
# import nest_asyncio
# from dotenv import load_dotenv
# # from typing import Callable, Optional
# from core.pipeline import EnhancedMarketingCampaignPipeline

# # Get the directory where main.py resides (which is your project root)
# project_root = os.path.dirname(os.path.abspath(__file__))
# # Add this directory to the Python path
# sys.path.insert(0, project_root)

# # Load environment variables from .env file
# load_dotenv()


# # Standalone execution functions (To run directly from CLI)
# # async def main():
# #     """Standalone execution function for testing"""
# #     print("🚀 Enhanced Marketing Campaign Pipeline Starting...\n")

# #     try:
# #         # Create model
# #         azure_model = create_azure_openai_model()
# #         if not azure_model:
# #             print("❌ Model creation failed. Exiting.")
# #             return

# #         # Initialize database
# #         print("🗄️ Initializing PostgreSQL database...")
# #         db_config = {
# #             "host": os.getenv("DB_HOST"),
# #             "database": os.getenv("DB_NAME", "marketing_campaigns"),
# #             "user": os.getenv("DB_USER"),
# #             "password": os.getenv("DB_PASSWORD")
# #         }
        
# #         # Validate configuration
# #         missing_config = [k for k, v in db_config.items() if not v]
# #         if missing_config:
# #             print(f"❌ Missing database configuration: {missing_config}")
# #             print("Make sure all required environment variables are set in .env file.")
# #             return
            
# #         db_manager = DatabaseManager(db_config)

# #         await db_manager.initialize_database()
# #         await db_manager.populate_sample_data()

# #         print(f"\n🎉 System Ready! Starting enhanced campaign generation...\n")

# #         # Get user input
# #         campaign_objective = input("Enter the campaign objective: \n> ")
# #         target_industry = input("Enter the target industry (or leave blank): \n> ")

# #         if not target_industry.strip():
# #             target_industry = None
# #         print("-" * 50)

# #         # Create and run pipeline
# #         pipeline = EnhancedMarketingCampaignPipeline(azure_model, db_manager)
# #         final_campaign = await pipeline.run_enhanced_campaign(campaign_objective, target_industry)

# #         # Display Results
# #         print("\n" + "="*70)
# #         print("📋 DATA-DRIVEN CAMPAIGN BRIEF")
# #         print("="*70)
# #         print(f"\n📊 EXECUTIVE SUMMARY:")
# #         print(final_campaign.executive_summary)
# #         print(f"\n🎯 STRATEGY OVERVIEW:")
# #         print(final_campaign.strategy_overview)
# #         print(f"\n🎨 CREATIVE DIRECTION:")
# #         print(final_campaign.creative_direction)
# #         print(f"\n🚀 IMPLEMENTATION PLAN:")
# #         print(final_campaign.implementation_plan)
# #         print(f"\n📈 SUCCESS METRICS:")
# #         print(final_campaign.success_metrics)
# #         print(f"\n📊 ANALYST INSIGHTS:")
# #         print(final_campaign.analyst_insights)
# #         print(f"\n⏭️ NEXT STEPS:")
# #         if isinstance(final_campaign.next_steps, list):
# #             for i, step in enumerate(final_campaign.next_steps, 1):
# #                 print(f"   {i}. {step}")
# #         else:
# #             print(final_campaign.next_steps)
# #         print("\n" + "="*70)
# #         print("\n🎉 Enhanced Marketing Campaign Pipeline Completed Successfully!")

# #     except Exception as e:
# #         print(f"❌ Pipeline execution failed: {e}")
# #         import traceback
# #         traceback.print_exc()
# #     finally:
# #         # Clean up database connections
# #         if 'db_manager' in locals():
# #             await db_manager.close()


# # def run_enhanced_campaign_sync():
# #     """Helper function to run the async main in different environments."""
# #     try:
# #         asyncio.run(main())
# #     except RuntimeError as e:
# #         if "asyncio.run() cannot be called from a running event loop" in str(e):
# #             print("Detected existing event loop, applying nest_asyncio...")
# #             nest_asyncio.apply()
# #             asyncio.run(main())
# #         else:
# #             raise e


# # if __name__ == "__main__":
# #     run_enhanced_campaign_sync()


from database.db_manager import DatabaseManager
from services.openai_config import create_azure_openai_model
import sys
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from core.pipeline import EnhancedMarketingCampaignPipeline

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
load_dotenv()

async def main():
    print("🚀 Enhanced Marketing Campaign Pipeline Starting...\n")
    try:
        azure_model = create_azure_openai_model()
        if not azure_model:
            print("❌ Model creation failed. Exiting.")
            return

        # Use Excel-based DatabaseManager
        excel_path = os.path.join(project_root, "campaigns.xlsx")
        db_manager = DatabaseManager(excel_path)

        print(f"\n🎉 System Ready! Starting enhanced campaign generation...\n")

        campaign_objective = input("Enter the campaign objective: \n> ")
        target_industry = input("Enter the target industry (or leave blank): \n> ")
        if not target_industry.strip():
            target_industry = None
        print("-" * 50)

        pipeline = EnhancedMarketingCampaignPipeline(azure_model, db_manager)
        final_campaign = await pipeline.run_enhanced_campaign(campaign_objective, target_industry)

        print("\n" + "="*70)
        print("📋 DATA-DRIVEN CAMPAIGN BRIEF")
        print("="*70)
        print(f"\n📊 EXECUTIVE SUMMARY:")
        print(final_campaign.executive_summary)
        print(f"\n🎯 STRATEGY OVERVIEW:")
        print(final_campaign.strategy_overview)
        print(f"\n🎨 CREATIVE DIRECTION:")
        print(final_campaign.creative_direction)
        print(f"\n🚀 IMPLEMENTATION PLAN:")
        print(final_campaign.implementation_plan)
        print(f"\n📈 SUCCESS METRICS:")
        print(final_campaign.success_metrics)
        print(f"\n📊 ANALYST INSIGHTS:")
        print(final_campaign.analyst_insights)
        print(f"\n⏭️ NEXT STEPS:")
        if isinstance(final_campaign.next_steps, list):
            for i, step in enumerate(final_campaign.next_steps, 1):
                print(f"   {i}. {step}")
        else:
            print(final_campaign.next_steps)
        print("\n" + "="*70)
        print("\n🎉 Enhanced Marketing Campaign Pipeline Completed Successfully!")

    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'db_manager' in locals():
            await db_manager.close()

def run_enhanced_campaign_sync():
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            print("Detected existing event loop, applying nest_asyncio...")
            nest_asyncio.apply()
            asyncio.run(main())
        else:
            raise e

if __name__ == "__main__":
    run_enhanced_campaign_sync()