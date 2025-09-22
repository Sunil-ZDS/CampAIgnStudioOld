# agents/orchestrator_agent.py
from pydantic_ai import Agent
from models.response_models import AnalysisOutput, StrategyOutput, CreativeOutput, CampaignBrief
import json
# from copy import deepcopy
from datetime import datetime

class OrchestratorAgent:
    def __init__(self, model):
        self.agent = Agent(
            model=model,
            output_type=CampaignBrief,
            system_prompt=

            """You are a Marketing Campaign Orchestrator AI. Synthesize insights and handle revisions with:
            - Data-driven decision making
            - Cross-functional integration
            - Version control awareness
            - Contextual understanding of revision requests"""



        )
        self.revision_history = []


    async def finalize_campaign_brief(
        self,
        campaign_objective: str,
        target_industry: str,
        analysis_result: AnalysisOutput,
        strategy_result: StrategyOutput,
        creative_result: CreativeOutput,
        campaign_budget: str = None,
        campaign_timing: str = None,
        campaign_destination_url: str = None,
        media_objective: str = None,
        media_target: str = None
    ) -> CampaignBrief:
        """Create a comprehensive, data-driven campaign brief integrating strategy, creative, and analyst insights."""
        prompt = f"""Create a comprehensive, data-driven campaign brief integrating strategy, creative, and analyst insights:

        CAMPAIGN OBJECTIVE: {campaign_objective}
        TARGET INDUSTRY: {target_industry or "General"}
        CAMPAIGN BUDGET: {campaign_budget or "Not specified"}
        CAMPAIGN TIMING: {campaign_timing or "Not specified"}
        CAMPAIGN DESTINATION URL: {campaign_destination_url or "Not specified"}
        MEDIA OBJECTIVE: {media_objective or "Not specified"}
        MEDIA (AUDIENCE) TARGET: {media_target or "Not specified"}

        ANALYST INSIGHTS SUMMARY:
        - Success Patterns: {', '.join(analysis_result.successful_patterns[:3])}
        - Top Channels: {', '.join(list(analysis_result.channel_performance.keys())[:3]) if analysis_result.channel_performance else "N/A"}
        - Key Recommendations: {', '.join(analysis_result.recommendations[:3])}

        STRATEGY DETAILS:
        - Overall Strategy: {strategy_result.overall_strategy}
        -Target Audience Deepdive: {strategy_result.target_audience_deep_dive}
        - Key Messaging Pillars: {', '.join(strategy_result.key_messaging_pillars)}
        - Recommended Channel & Tactics: {', '.join(strategy_result.recommended_channels_and_tactics)}
        - Budget Allocation & Guidance: {', '.join(strategy_result.budget_allocation_guidance)}
        - Measurement KPIs: {', '.join(strategy_result.measurement_kpis)}

        CREATIVE DETAILS:
        - Creative Concept: {creative_result.creative_concept}
        - Visual Direction: {creative_result.visual_direction}
        - Messaging Themes: {creative_result.messaging_themes}
        - Call to Action Examples: {creative_result.call_to_action_examples}
        - Ad format Recommendations: {creative_result.ad_format_recommendations}
        - Tone of Voice: {creative_result.tone_of_voice}

        Synthesize everything into a polished, data-driven campaign brief with:
        - Executive summary highlighting data-driven approach
        - Implementation roadmap based on successful patterns
        - Clear next steps incorporating analyst recommendations
        - Analyst insights section explaining the data foundation

        Ensure each field in the CampaignBrief is populated logically and comprehensively.
        
        """

        prompt += """
                {
                "executive_summary": "This campaign aims to drive awareness and conversions for a new line of eco-friendly home products by leveraging data-driven creative strategies across high-performing digital channels.",
                "campaign_objective": "Increase brand awareness and generate 10,000 new product trial sign-ups within 8 weeks.",
                "target_audience": "Environmentally-conscious millennials and Gen Z adults aged 24–38, primarily urban dwellers with a household income of $50k–$90k. They value sustainability, wellness, and ethical consumerism.",
                "strategy_overview": "The strategy combines audience segmentation, behavioral targeting, and creative personalization. It leverages top-performing platforms like Instagram Reels, TikTok, and YouTube Shorts, supported by retargeting via Google Display Network and email nurturing.",
                "creative_direction": "A vibrant, nature-inspired visual aesthetic with warm earth tones and dynamic storytelling. Messaging is upbeat, empowering, and solution-focused, using humor and relatable situations to highlight everyday benefits of sustainable living.",
                "implementation_plan": "Phase 1: Creative development & platform setup (Weeks 1–2)\nPhase 2: Launch of awareness phase with video-first content (Weeks 3–5)\nPhase 3: Retargeting + conversion push (Weeks 6–7)\nPhase 4: Optimization & performance analysis (Ongoing)",
                "success_metrics": [
                    {
                    "name": "Brand Awareness",
                    "goal": "Reach 2 million impressions",
                    "measurement_method": "Social media analytics and display ad reporting",
                    "expected_result": "5% increase in branded search volume"
                    },
                    {
                    "name": "Engagement Rate",
                    "goal": "3.5%",
                    "measurement_method": "Click-through rate on social and display ads",
                    "expected_result": "Above industry benchmark"
                    },
                    {
                    "name": "Conversion Rate",
                    "goal": "4%",
                    "measurement_method": "Landing page form submissions",
                    "expected_result": "At least 10,000 qualified leads"
                    }
                ],
                "analyst_insights": "Previous campaigns showed that video content under 15 seconds performs best on TikTok and Instagram Reels. Audiences respond positively to UGC-style testimonials and behind-the-scenes clips showing product impact. Email nurture sequences with personalized subject lines increased CTR by 22% in past A/B tests.",
                "next_steps": [
                    "Finalize creative assets and begin pre-launch testing",
                    "Set up tracking pixels and conversion events across all platforms",
                    "Schedule influencer partnerships for week 3",
                    "Begin building email segments for post-click nurture"
                ]
                }

                """
        result = await self.agent.run(prompt)
        return result.output
    
    async def handle_revision(
        self,
        current_brief: CampaignBrief,
        feedback: str,
        sections_to_update: dict
    ) -> CampaignBrief:
        """Handle campaign revisions with version control and context awareness"""
        revision_prompt = f"""**Campaign Revision Request**
        
        Current Campaign State:
        {json.dumps(current_brief.dict(), indent=2)}

        User Feedback: {feedback}
        
        Required Updates: {sections_to_update}

        Revision Rules:
        1. Maintain consistent brand voice and strategy
        2. Preserve unchanged sections unless explicitly modified
        3. Track changes in 'revision_history'
        4. Validate against original business objectives

        Generate updated campaign brief with these changes:
        """

        updated_brief = await self.agent.run(revision_prompt)
        new_brief = updated_brief.output
        
        # Track changes
        self._track_changes(current_brief, new_brief)
        return new_brief

    def _track_changes(self, old: CampaignBrief, new: CampaignBrief):
        changes = {}
        for section in ['strategy', 'creative', 'analyst', 'campaign']:
            old_dict = old.dict().get(section, {})
            new_dict = new.dict().get(section, {})
            section_changes = {
                field: {"old": old_dict.get(field), "new": new_dict.get(field)}
                for field in new_dict
                if old_dict.get(field) != new_dict.get(field)
            }
            if section_changes:
                changes[section] = section_changes
        
        if changes:
            self.revision_history.append({
                "timestamp": datetime.now().isoformat(),
                "changes": changes
            })