# agents/strategy_agent.py
from pydantic_ai import Agent
from models.response_models import AnalysisOutput, StrategyOutput

class StrategyAgent:
    def __init__(self, model):
        self.agent = Agent(
            model=model,
            result_type=StrategyOutput,
            system_prompt="""You are a Senior Marketing Strategist with expertise in digital marketing,
             audience analysis, and campaign optimization. You excel at identifying target audiences,
             crafting compelling messaging, and selecting the most effective marketing channels.

                        You now have access to historical campaign performance data and analyst insights.
             Use this data to inform your strategic recommendations and improve campaign effectiveness.

                        Focus on data-driven strategies, proven patterns, and measurable outcomes.""",
            max_retries = 3
        )

    async def develop_strategy(
        self, campaign_objective: str, target_industry: str, analysis_result: AnalysisOutput,
        campaign_budget: str = None, campaign_timing: str = None, campaign_destination_url: str = None,
        media_objective: str = None, media_target: str = None
    ) -> StrategyOutput:
        """Develop a comprehensive marketing strategy using historical performance insights."""
        prompt = f"""Develop a comprehensive marketing strategy using historical performance insights:

        CAMPAIGN OBJECTIVE: {campaign_objective}
        TARGET INDUSTRY: {target_industry or "General"}
        CAMPAIGN BUDGET: {campaign_budget or "Not specified"}
        CAMPAIGN TIMING: {campaign_timing or "Not specified"}
        CAMPAIGN DESTINATION URL: {campaign_destination_url or "Not specified"}
        MEDIA OBJECTIVE: {media_objective or "Not specified"}
        MEDIA (AUDIENCE) TARGET: {media_target or "Not specified"}

        ANALYST INSIGHTS:

        EXECUTIVE SUMMARY: {', '.join(analysis_result.executive_summary)}
        SUCCESS PATTERNS: {', '.join(analysis_result.successful_patterns)}
        CHANNEL PERFORMANCE: {analysis_result.channel_performance}
        AUDIENCE INSIGHTS: {', '.join(analysis_result.audience_insights)}
        BUDGET RECOMMENDATIONS: {analysis_result.budget_recommendations}
        CREATIVE TRENDS: {', '.join(analysis_result.creative_trends)}
        KEY SUCCESS FACTORS: {', '.join(analysis_result.key_success_factors)}
        RECOMMENDATIONS: {', '.join(analysis_result.recommendations)}
        
        

        Develop strategy considering:
        - Target audience demographics and psychographics informed by successful patterns
        - Key messaging pillars based on proven approaches
        - Marketing channels prioritized by historical performance
        - Success metrics and KPIs aligned with industry benchmarks
        - Budget allocation based on data-driven recommendations
        - Implementation timeline optimized for success
        - Success factors from high-performing campaigns

        Make sure all keys are present and values are of the correct type.
        """

        prompt += """

            Please return your response strictly in the following JSON format:
            {
            "overall_strategy": "...",
            "target_audience_deep_dive": "...",
            "key_messaging_pillars": ["...", "..."],
            "recommended_channels_and_tactics": {
                "channel_name": ["tactic1", "tactic2"]
            },
            "budget_allocation_guidance": {
                "channel1": "percentage or amount",
                ...
            },
            "measurement_kpis": ["...", "..."]
            }

            Make sure all keys are present and values are of the correct type.
            """

        result = await self.agent.run(prompt)
        return result.output
    

