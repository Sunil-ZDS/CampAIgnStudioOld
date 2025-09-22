# agents/analyst_agent.py
from typing import Dict, List
from pydantic_ai import Agent
# import json

from database.db_manager import DatabaseManager
from models.response_models import AnalysisOutput

class AnalystAgent:
    def __init__(self, model, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.agent = Agent(
            model=model,
            output_type=AnalysisOutput,
            system_prompt="""You are a Senior Marketing Data Analyst with expertise in campaign performance analysis,
             pattern recognition, and data-driven marketing insights. You excel at identifying success patterns from
             historical campaign data and translating them into actionable recommendations.

             **Crucially, your output MUST strictly adhere to the provided JSON schema. Ensure 'channel_performance'
            and 'budget_recommendations' are objects (dictionaries), not lists or prose.**

            Focus on:
            - Identifying patterns in successful campaigns
            - Channel performance analysis
            - Audience behavior insights
            - Budget optimization recommendations
            - Creative performance trends
            - ROI and conversion optimization

            Provide data-driven, actionable insights that can directly improve campaign performance."""
        )

    async def analyze_campaign_patterns(self, campaign_objective: str, target_industry: str = None) -> AnalysisOutput:
        """Analyze historical campaign data to identify success patterns"""

        # Gather data from database
        print("DEBUG: Loading successful campaigns...")
        successful_campaigns = await self.db_manager.get_successful_campaigns(20)
        print("DEBUG: Loaded successful campaigns.")
        channel_performance = await self.db_manager.get_channel_performance()
        print("DEBUG: Loaded channel performance.")
        industry_insights = await self.db_manager.get_industry_insights(target_industry)
        print("DEBUG: Loaded industry insights.")

        # Prepare analysis prompt
        analysis_prompt = f"""
        Develop a comprehensive marketing strategy using historical performance insights:

        CAMPAIGN OBJECTIVE: {campaign_objective}
        TARGET INDUSTRY: {target_industry or "General"}

        HISTORICAL SUCCESS DATA:

        TOP PERFORMING CAMPAIGNS:
        {self._format_campaign_data(successful_campaigns)}

        CHANNEL PERFORMANCE ANALYSIS:
        {self._format_channel_data(channel_performance)}

        INDUSTRY INSIGHTS:
        {self._format_industry_data(industry_insights)}

        Based on this data, provide insights adhering strictly to the AnalysisOutput schema:
        1.  `successful_patterns`: List of key success patterns.
        2.  `channel_performance`: A JSON object (dictionary) where keys are channel names (e.g., "Social Media") and values are their average performance metrics (e.g., {{"avg_success_score": 8.5, "avg_roas": 7.2}}). Do NOT provide a list of descriptive strings.
        3.  `audience_insights`: List of audience-related insights.
        4.  `budget_recommendations`: A JSON object (dictionary) where keys are budget categories (e.g., "Low Budget", "High Budget") or specific channel names, and values are budget recommendations for them (e.g., {{"Social Media": "Invest more in video ads", "Content Marketing": "Allocate 20% of budget"}}). Do NOT provide a list of descriptive strings.
        5.  `creative_trends`: List of effective creative trends.
        6.  `key_success_factors`: List of critical factors.
        7.  `recommendations`: List of actionable recommendations.

        Focus on actionable insights that can be directly applied to strategy and creative development.
        """

        print("DEBUG: Sending prompt to Azure OpenAI...")
        result = await self.agent.run(analysis_prompt)

        print("DEBUG: Received response from Azure OpenAI.")
        return result.output

    def _format_campaign_data(self, campaigns: List[Dict]) -> str:
        """Format campaign data for analysis"""
        if not campaigns:
            return "No successful campaigns found"
        formatted = []
        for camp in campaigns[:10]:  # Top 10 for brevity
            formatted.append(
                f"• {camp['campaign_name']} | Industry: {camp['industry']} | "
                f"Success Score: {camp['success_score']} | ROAS: {camp['roas']} | "
                f"Channels: {', '.join(camp['channels'])} | "
                f"Creative: {camp['creative_type']} | Tone: {camp['messaging_tone']}"
            )
        return "\n".join(formatted)

    def _format_channel_data(self, channels: Dict) -> str:
        """Format channel performance data"""
        if not channels:
            return "No channel data available"
        formatted = []
        for channel, data in channels.items():
            formatted.append(
                f"• {channel}: Success Score {data['avg_success_score']:.2f} | "
                f"ROAS {data['avg_roas']:.2f} | CTR {data['avg_ctr']:.4f} | "
                f"Campaigns: {data['campaign_count']}"
            )
        return "\n".join(formatted)

    def _format_industry_data(self, industries: List[Dict]) -> str:
        """Format industry insights data"""
        if not industries:
            return "No industry data available"
        formatted = []
        for industry in industries[:5]:  # Top 5 industries
            formatted.append(
                f"• {industry['industry']}: Avg Success {industry['avg_success_score']:.2f} | "
                f"Avg Budget ${industry['avg_budget']:,.0f} | "
                f"Campaigns: {industry.get('campaign_count', 'N/A')}"
            )
        return "\n".join(formatted)
    
    def _format_channel_data_for_prompt(self, channels: Dict) -> str:
        """Format channel performance data specifically for the prompt as key-value pairs."""
        if not channels:
            return "No channel data available."
        formatted = []
        for channel, data in channels.items():
            formatted.append(
                f'"{channel}": {{"avg_success_score": {data["avg_success_score"]:.2f}, '
                f'"avg_roas": {data["avg_roas"]:.2f}, '
                f'"avg_ctr": {data["avg_ctr"]:.4f}, '
                f'"avg_conversion_rate": {data["avg_conversion_rate"]:.4f}, '
                f'"campaign_count": {data["campaign_count"]}}}'
            )
        # Wrap it in curly braces to suggest it's part of a JSON object
        return "{\n" + ",\n".join(formatted) + "\n}"