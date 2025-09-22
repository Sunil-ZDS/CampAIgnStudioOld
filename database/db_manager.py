# # database/db_manager.py
# # import asyncio
# import asyncpg
# import random
# from typing import Dict, Any, List
# from dataclasses import dataclass
# from datetime import datetime, timedelta

# @dataclass
# class CampaignRecord:
#     campaign_id: str
#     campaign_name: str
#     industry: str
#     target_audience: str
#     channels: List[str]
#     budget: float
#     duration_days: int
#     ctr: float  # Click-through rate
#     conversion_rate: float
#     roas: float  # Return on ad spend
#     engagement_rate: float
#     brand_lift: float
#     success_score: float
#     creative_type: str
#     messaging_tone: str
#     launch_date: datetime
#     created_at: datetime

# class DatabaseManager:
#     def __init__(self, db_config: Dict[str, Any]):
#         self.db_config = db_config
#         self.connection_pool = None

#     async def initialize_database(self):
#         """Initialize database connection pool and create tables"""
#         try:
#             # Create connection pool
#             self.connection_pool = await asyncpg.create_pool(
#                 **self.db_config,
#                 min_size=1,
#                 max_size=10
#             )
#             # Create tables
#             await self.create_tables()
#             print("✅ Database initialized successfully!")
#         except Exception as e:
#             print(f"❌ Database initialization failed: {e}")
#             raise

#     async def create_tables(self):
#         """Create campaign tables"""
#         create_table_sql = """
#         CREATE TABLE IF NOT EXISTS campaigns (
#             campaign_id VARCHAR(50) PRIMARY KEY,
#             campaign_name VARCHAR(200) NOT NULL,
#             industry VARCHAR(100) NOT NULL,
#             target_audience TEXT NOT NULL,
#             channels TEXT[] NOT NULL,
#             budget DECIMAL(12,2) NOT NULL,
#             duration_days INTEGER NOT NULL,
#             ctr DECIMAL(5,4) NOT NULL,
#             conversion_rate DECIMAL(5,4) NOT NULL,
#             roas DECIMAL(8,2) NOT NULL,
#             engagement_rate DECIMAL(5,4) NOT NULL,
#             brand_lift DECIMAL(5,4) NOT NULL,
#             success_score DECIMAL(5,2) NOT NULL,
#             creative_type VARCHAR(100) NOT NULL,
#             messaging_tone VARCHAR(100) NOT NULL,
#             launch_date TIMESTAMP NOT NULL,
#             created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#         );

#         CREATE INDEX IF NOT EXISTS idx_campaigns_industry ON campaigns(industry);
#         CREATE INDEX IF NOT EXISTS idx_campaigns_success_score ON campaigns(success_score);
#         CREATE INDEX IF NOT EXISTS idx_campaigns_channels ON campaigns USING GIN(channels);
#         CREATE INDEX IF NOT EXISTS idx_campaigns_launch_date ON campaigns(launch_date);
#         """
#         async with self.connection_pool.acquire() as conn:
#             await conn.execute(create_table_sql)

#     def generate_sample_campaigns(self) -> List[CampaignRecord]:
#         """Generate diverse sample campaign data"""
#         industries = ["Technology", "Healthcare", "Finance", "Retail", "Food & Beverage",
#                       "Automotive", "Entertainment", "Education", "Fashion", "Travel"]

#         channels = ["Social Media", "Google Ads", "Email Marketing", "Content Marketing",
#                     "Influencer Marketing", "TV", "Radio", "Print", "Outdoor", "Programmatic"]

#         creative_types = ["Video", "Static Image", "Carousel", "Interactive", "Story",
#                           "Podcast", "Blog Post", "Infographic", "Animation", "User Generated"]

#         tones = ["Humorous", "Emotional", "Informative", "Urgent", "Inspirational",
#                  "Professional", "Casual", "Bold", "Caring", "Innovative"]

#         audiences = [
#             "Young professionals (25-35)", "Parents with children", "Senior citizens (55+)",
#             "College students", "Small business owners", "Health-conscious consumers",
#             "Tech enthusiasts", "Budget-conscious families", "Luxury consumers", "Millennials"
#         ]

#         campaigns = []
#         base_date = datetime.now() - timedelta(days=365)

#         for i in range(100):  # Generate 100 sample campaigns
#             # Create realistic performance correlations
#             budget = random.uniform(5000, 500000)
#             duration = random.randint(7, 90)

#             # Higher budgets and longer durations tend to perform better
#             base_performance = min(0.8, (budget / 100000) * 0.3 + (duration / 90) * 0.2 + random.uniform(0.2, 0.6))

#             ctr = max(0.005, base_performance * random.uniform(0.8, 1.2) * 0.05)
#             conversion_rate = max(0.01, base_performance * random.uniform(0.7, 1.3) * 0.08)
#             roas = max(1.2, base_performance * random.uniform(0.8, 1.5) * 8)
#             engagement_rate = max(0.02, base_performance * random.uniform(0.9, 1.1) * 0.15)
#             brand_lift = max(0.05, base_performance * random.uniform(0.7, 1.2) * 0.25)

#             # Calculate success score
#             success_score = (ctr * 20 + conversion_rate * 12.5 + (roas - 1) * 2 +
#                             engagement_rate * 6.67 + brand_lift * 4) / 5

#             campaign = CampaignRecord(
#                 campaign_id=f"CAMP_{i+1:03d}",
#                 campaign_name=f"Campaign {i+1}: {random.choice(['Launch', 'Boost', 'Drive', 'Maximize', 'Transform'])} {random.choice(['Sales', 'Awareness', 'Engagement', 'Growth', 'Impact'])}",
#                 industry=random.choice(industries),
#                 target_audience=random.choice(audiences),
#                 channels=random.sample(channels, random.randint(2, 5)),
#                 budget=round(budget, 2),
#                 duration_days=duration,
#                 ctr=round(ctr, 4),
#                 conversion_rate=round(conversion_rate, 4),
#                 roas=round(roas, 2),
#                 engagement_rate=round(engagement_rate, 4),
#                 brand_lift=round(brand_lift, 4),
#                 success_score=round(success_score, 2),
#                 creative_type=random.choice(creative_types),
#                 messaging_tone=random.choice(tones),
#                 launch_date=base_date + timedelta(days=random.randint(0, 365)),
#                 created_at=datetime.now()
#             )
#             campaigns.append(campaign)
#         return campaigns

#     async def populate_sample_data(self):
#         """Populate database with sample campaign data"""
#         sample_campaigns = self.generate_sample_campaigns()
#         insert_sql = """
#         INSERT INTO campaigns (
#             campaign_id, campaign_name, industry, target_audience, channels, budget,
#             duration_days, ctr, conversion_rate, roas, engagement_rate, brand_lift,
#             success_score, creative_type, messaging_tone, launch_date
#         ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
#         ON CONFLICT (campaign_id) DO NOTHING
#         """
#         async with self.connection_pool.acquire() as conn:
#             for campaign in sample_campaigns:
#                 await conn.execute(
#                     insert_sql,
#                     campaign.campaign_id, campaign.campaign_name, campaign.industry,
#                     campaign.target_audience, campaign.channels, campaign.budget,
#                     campaign.duration_days, campaign.ctr, campaign.conversion_rate,
#                     campaign.roas, campaign.engagement_rate, campaign.brand_lift,
#                     campaign.success_score, campaign.creative_type, campaign.messaging_tone,
#                     campaign.launch_date
#                 )
#             print(f"✅ Populated {len(sample_campaigns)} sample campaigns!")

#     async def get_successful_campaigns(self, limit: int = 20) -> List[Dict]:
#         """Get top performing campaigns"""
#         query = """
#         SELECT * FROM campaigns
#         WHERE success_score >= 7.0
#         ORDER BY success_score DESC, roas DESC
#         LIMIT $1
#         """
#         async with self.connection_pool.acquire() as conn:
#             rows = await conn.fetch(query, limit)
#             return [dict(row) for row in rows]

#     async def get_channel_performance(self) -> Dict[str, Dict]:
#         """Analyze performance by channel"""
#         query = """
#         SELECT
#             channel,
#             AVG(success_score) as avg_success_score,
#             AVG(roas) as avg_roas,
#             AVG(ctr) as avg_ctr,
#             AVG(conversion_rate) as avg_conversion_rate,
#             COUNT(*) as campaign_count
#         FROM (
#             SELECT unnest(channels) as channel, success_score, roas, ctr, conversion_rate
#             FROM campaigns
#         ) channel_data
#         GROUP BY channel
#         ORDER BY avg_success_score DESC
#         """
#         async with self.connection_pool.acquire() as conn:
#             rows = await conn.fetch(query)
#             return {row['channel']: dict(row) for row in rows}

#     async def get_industry_insights(self, industry: str = None) -> List[Dict]:
#         """Get industry-specific insights"""
#         if industry:
#             query = """
#             SELECT
#                 industry,
#                 AVG(success_score) as avg_success_score,
#                 AVG(budget) as avg_budget,
#                 AVG(duration_days) as avg_duration,
#                 array_agg(DISTINCT creative_type) as popular_creative_types,
#                 array_agg(DISTINCT messaging_tone) as popular_tones
#             FROM campaigns
#             WHERE industry ILIKE $1
#             GROUP BY industry
#             """
#             params = [f"%{industry}%"]
#         else:
#             query = """
#             SELECT
#                 industry,
#                 AVG(success_score) as avg_success_score,
#                 AVG(budget) as avg_budget,
#                 AVG(duration_days) as avg_duration,
#                 COUNT(*) as campaign_count
#             FROM campaigns
#             GROUP BY industry
#             ORDER BY avg_success_score DESC
#             """
#             params = []
#         async with self.connection_pool.acquire() as conn:
#             if params:
#                 rows = await conn.fetch(query, *params)
#             else:
#                 rows = await conn.fetch(query)
#             return [dict(row) for row in rows]

#     async def close(self):
#         """Close database connection pool"""
#         if self.connection_pool:
#             await self.connection_pool.close()


import pandas as pd
from typing import Dict, Any, List, Optional

class DatabaseManager:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path

    async def _load_df(self):
        return pd.read_excel(self.excel_path)
    

    async def get_successful_campaigns(self, limit: int = 20) -> List[Dict]:
        df = await self._load_df()
        df = df[df['success_score'] >= 7.0]
        df = df.sort_values(['success_score', 'roas'], ascending=[False, False])
        return df.head(limit).to_dict(orient='records')

    async def get_channel_performance(self) -> Dict[str, Dict]:
        df = await self._load_df()
        # Ensure channels column is a list
        if df['channels'].dtype == object:
            df['channels'] = df['channels'].apply(lambda x: eval(x) if isinstance(x, str) and x.startswith("[") else [x] if isinstance(x, str) else x)
        # Explode channels for aggregation
        exploded = df.explode('channels')
        grouped = exploded.groupby('channels').agg(
            avg_success_score=('success_score', 'mean'),
            avg_roas=('roas', 'mean'),
            avg_ctr=('ctr', 'mean'),
            avg_conversion_rate=('conversion_rate', 'mean'),
            campaign_count=('campaign_id', 'count')
        ).reset_index()
        # Convert to dict
        channel_stats = {}
        for _, row in grouped.iterrows():
            channel_stats[row['channels']] = {
                'avg_success_score': row['avg_success_score'],
                'avg_roas': row['avg_roas'],
                'avg_ctr': row['avg_ctr'],
                'avg_conversion_rate': row['avg_conversion_rate'],
                'campaign_count': row['campaign_count']
            }
        return channel_stats
    
    async def get_industry_insights(self, industry: Optional[str] = None) -> List[Dict]:
        df = await self._load_df()
        if industry:
            df = df[df['industry'].str.contains(industry, case=False, na=False)]
        grouped = df.groupby('industry').agg(
            avg_success_score=('success_score', 'mean'),
            avg_budget=('budget', 'mean'),
            avg_duration=('duration_days', 'mean'),
            popular_creative_types=('creative_type', lambda x: list(set(x))),
            popular_tones=('messaging_tone', lambda x: list(set(x))),
            campaign_count=('campaign_id', 'count')
        ).reset_index()
        return grouped.to_dict(orient='records')
    
    async def close(self):
        # No resources to clean up for Excel
        pass