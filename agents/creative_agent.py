# agents/creative_agent.py
from pydantic_ai import Agent
from models.response_models import AnalysisOutput, StrategyOutput, CreativeOutput

class CreativeAgent:
    def __init__(self, model):
        self.agent = Agent(
            model=model,
            output_type=CreativeOutput,
            system_prompt="""You are a Creative Director known for breakthrough creative campaigns
             that emotionally connect with audiences. You specialize in developing memorable taglines,
             compelling ad copy, and cohesive visual directions that drive engagement.

                        You now have access to historical campaign performance data and creative trends analysis.
             Use this data to inform your creative decisions and develop concepts that have proven to work.

                        Focus on creativity that converts, resonates with the target market, and follows successful patterns."""

        )

    async def develop_creative(
        self,
        campaign_objective: str,
        target_industry: str,
        strategy_result: StrategyOutput,
        analysis_result: AnalysisOutput,
        campaign_budget: str = None,
        campaign_timing: str = None,
        campaign_destination_url: str = None,
        media_objective: str = None,
        media_target: str = None
    ) -> CreativeOutput:
        """Create compelling creative concepts using performance data and successful creative trends."""
        prompt = f"""Create compelling creative concepts using performance data and successful creative trends:

        CAMPAIGN OBJECTIVE: {campaign_objective}
        TARGET INDUSTRY: {target_industry or "General"}
        CAMPAIGN BUDGET: {campaign_budget or "Not specified"}
        CAMPAIGN TIMING: {campaign_timing or "Not specified"}
        CAMPAIGN DESTINATION URL: {campaign_destination_url or "Not specified"}
        MEDIA OBJECTIVE: {media_objective or "Not specified"}
        MEDIA (AUDIENCE) TARGET: {media_target or "Not specified"}

        STRATEGY CONTEXT:
        - Overall Strategy: {strategy_result.overall_strategy}
        -Target Audience Deepdive: {strategy_result.target_audience_deep_dive}
        - Key Messaging Pillars: {', '.join(strategy_result.key_messaging_pillars)}
        - Recommended Channel & Tactics: {', '.join(strategy_result.recommended_channels_and_tactics)}
        - Budget Allocation & Guidance: {', '.join(strategy_result.budget_allocation_guidance)}
        - Measurement KPIs: {', '.join(strategy_result.measurement_kpis)}

        
        CREATIVE PERFORMANCE INSIGHTS:
        CREATIVE TRENDS: {', '.join(analysis_result.creative_trends)}
        SUCCESS PATTERNS: {', '.join(analysis_result.successful_patterns)}
        CHANNEL PERFORMANCE: Focus on top-performing channels like {', '.join(list(analysis_result.channel_performance.keys())[:3]) if analysis_result.channel_performance else "various channels"}

        Develop creative concepts that incorporate:
        - Campaign tagline inspired by successful patterns
        - Ad copy samples optimized for top-performing channels
        - Visual direction based on proven creative trends
        - Content themes aligned with successful campaigns
        - Brand voice and tone informed by performance data
        - Creative insights explaining why these approaches work

        """

        prompt += """ 
        Please return your response strictly in the following JSON format:
            {
            "creative_concept": "A campaign centered around empowering users through simplicity and clarity.",
            "visual_direction": "Minimalist aesthetic with soft gradients, clean typography, and lifestyle imagery showing real people using the product effortlessly.",
            "messaging_themes": [
                "Empowerment through simplicity",
                "Trusted solutions for everyday life",
                "Designed with you in mind"
            ],
            "call_to_action_examples": [
                "Start Your Free Trial Today",
                "See How It Works",
                "Join Thousands of Happy Users"
            ],
            "ad_format_recommendations": {
                "social_media": ["video", "carousel", "static_image"],
                "email": ["banner", "animated_gif"],
                "search": ["text_ad"]
            },
            "tone_of_voice": "Friendly, approachable, and confident"
            }

            """

        result = await self.agent.run(prompt)
        return result.output