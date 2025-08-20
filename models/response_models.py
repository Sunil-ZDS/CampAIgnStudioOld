# models/response_models.py
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

#To feed into channel_performance in AnalysisOutput
# Source: AnalystAgent - OutputModel: ChannelMetrics - Used by: AnalysisOutput
class ChannelMetrics(BaseModel):
    avg_success_score: float = Field(description="Average success score of campaigns using this channel")
    avg_roas: float = Field(description="Average Return on Ad Spend")
    avg_ctr: Optional[float] = Field(default=None, description="Average Click Through Rate")
    avg_conversion_rate: Optional[float] = Field(default=None, description="Average conversion rate")
    campaign_count: Optional[int] = Field(default=None, description="Number of campaigns analyzed")

#Used by AnalystAgent - Structured Analyst Output
# Source: AnalystAgent - OutputModel: AnalysisOutput - Used by: StrategyAgent, OrchestratorAgent
class AnalysisOutput(BaseModel):
    executive_summary: str = Field(description="Summary of findings and recommendations", example="")
    successful_patterns: List[str] = Field(description="Patterns from high-performing campaigns")
    channel_performance: Dict[str, ChannelMetrics] = Field(description="Performance metrics by channel")
    audience_insights: List[str] = Field(description="Insights about target audiences")
    budget_recommendations: Dict[str, str] = Field(description="Data-driven budget advice")
    creative_trends: List[str] = Field(description="Emerging creative trends")
    key_success_factors: List[str] = Field(description="Factors that drive success")
    recommendations: List[str] = Field(description="Actionable next steps")

#Used by StrategyAgent - Structured Strategy Output
# Source: StrategyAgent - OutputModel: StrategyOutput - Used by: CreativeAgent, OrchestratorAgent
class StrategyOutput(BaseModel):
    overall_strategy: str = Field(description="The overarching strategy for the campaign.")
    target_audience_deep_dive: str = Field(description="Detailed insights and segmentation for the target audience.") #create nessted model - AudienceProfile
    key_messaging_pillars: List[str] = Field(description="Core messages to be communicated.")
    recommended_channels_and_tactics: Dict[str, List[str]] = Field(description="Recommended channels and specific tactics for each.")
    budget_allocation_guidance: Dict[str, str] = Field(description="Guidance on how to allocate budget.") #create nessted model - BudgetBreakdown
    measurement_kpis: List[str] = Field(description="Key Performance Indicators (KPIs) to measure success.")

#Used by CreativeAgent - Structured Creative Output
# Source: CreativeAgent - OutputModel: CreativeOutput - Used by: OrchestratorAgent
class CreativeOutput(BaseModel):
    creative_concept: str = Field(description="The main creative concept or big idea for the campaign.")
    visual_direction: str = Field(description="Guidance on imagery, colors, and overall aesthetic.")
    messaging_themes: List[str] = Field(description="Specific themes or angles for ad copy.")
    call_to_action_examples: List[str] = Field(description="Examples of effective calls to action.")
    ad_format_recommendations: Dict[str, List[str]] = Field(description="Recommended ad formats for various channels (e.g., social media: [video, carousel, static image]).")
    tone_of_voice: str = Field(description="The overall tone to be used in communications (e.g., empathetic, energetic, authoritative).")

#Used by OrchestratorAgent - Structured Campaign Brief Output
# Source: OrchestratorAgent - OutputModel: CampaignBrief - Used by: app.py (UI)
class CampaignBrief(BaseModel):
    executive_summary: str = Field(description="A high-level summary of the entire campaign brief.")
    campaign_objective: str = Field(description="The primary objective of the campaign.")
    target_audience: str = Field(description="A detailed description of the target audience.")
    strategy_overview: str = Field(description="An overview of the campaign strategy, combining insights and tactical recommendations.")
    creative_direction: str = Field(description="The core creative concept and visual/messaging guidelines.")
    implementation_plan: str = Field(description="Key steps and phases for campaign execution.")
    success_metrics: List[str] = Field(description="The KPIs to track and measure campaign success.") #Should be typed object instead - name, goal, measurement_method, expected_result - List[SuccessMetric]]
    analyst_insights: str = Field(description="Direct insights from the data analysis phase.")
    next_steps: List[str] = Field(description="Actionable next steps for the campaign team.")