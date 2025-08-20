-- database/setup_db.sql
-- PostgreSQL Database Setup Script for Marketing Campaign Pipeline
-- Run this script to set up your database manually if needed

-- Create database (run this as superuser)
CREATE DATABASE marketing_campaigns;

-- Connect to the marketing_campaigns database, then run the following:
-- Create the campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id VARCHAR(50) PRIMARY KEY,
    campaign_name VARCHAR(200) NOT NULL,
    industry VARCHAR(100) NOT NULL,
    target_audience TEXT NOT NULL,
    channels TEXT[] NOT NULL,
    budget DECIMAL(12,2) NOT NULL,
    duration_days INTEGER NOT NULL,
    ctr DECIMAL(5,4) NOT NULL,
    conversion_rate DECIMAL(5,4) NOT NULL,
    roas DECIMAL(8,2) NOT NULL,
    engagement_rate DECIMAL(5,4) NOT NULL,
    brand_lift DECIMAL(5,4) NOT NULL,
    success_score DECIMAL(5,2) NOT NULL,
    creative_type VARCHAR(100) NOT NULL,
    messaging_tone VARCHAR(100) NOT NULL,
    launch_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_campaigns_industry ON campaigns(industry);
CREATE INDEX IF NOT EXISTS idx_campaigns_success_score ON campaigns(success_score);
CREATE INDEX IF NOT EXISTS idx_campaigns_channels ON campaigns USING GIN(channels);
CREATE INDEX IF NOT EXISTS idx_campaigns_launch_date ON campaigns(launch_date);

-- Sample data insertion (optional - the Python script will handle this)
-- This is just for reference or manual setup
-- Sample successful campaigns
INSERT INTO campaigns (
    campaign_id, campaign_name, industry, target_audience, channels, budget,
    duration_days, ctr, conversion_rate, roas, engagement_rate, brand_lift,
    success_score, creative_type, messaging_tone, launch_date) VALUES
    ('CAMP_001', 'Digital Baby Care Awareness', 'Healthcare', 'New parents (25-35)',
     ARRAY['Social Media', 'Google Ads', 'Content Marketing'], 50000.00, 30,
     0.0450, 0.1250, 8.50, 0.1200, 0.2800, 8.90, 'Video', 'Caring', '2024-01-15'),

    ('CAMP_002', 'Premium Diaper Launch', 'Baby Care', 'Affluent parents with infants',
     ARRAY['Influencer Marketing', 'Social Media', 'Email Marketing'], 75000.00, 45,
     0.0380, 0.1180, 9.20, 0.1450, 0.3100, 9.25, 'Carousel', 'Premium', '2024-02-01'),

    ('CAMP_003', 'Back-to-School Campaign', 'Education', 'Parents with school-age children',
     ARRAY['TV', 'Social Media', 'Print'], 120000.00, 60,
     0.0320, 0.0980, 7.80, 0.0890, 0.2200, 8.45, 'Video', 'Inspirational', '2024-07-15'),

    ('CAMP_004', 'Organic Baby Food Launch', 'Food & Beverage', 'Health-conscious new parents',
     ARRAY['Content Marketing', 'Social Media', 'Influencer Marketing'], 40000.00, 30,
     0.0520, 0.1420, 10.50, 0.1680, 0.3500, 9.80, 'User Generated', 'Caring', '2024-03-10'),

    ('CAMP_005', 'Night-time Comfort Campaign', 'Baby Care', 'Parents of toddlers (1-3 years)',
     ARRAY['Social Media', 'Google Ads', 'Programmatic'], 65000.00, 35,
     0.0410, 0.1290, 8.90, 0.1350, 0.2900, 8.75, 'Animation', 'Emotional', '2024-04-05'),

    ('CAMP_006', 'Tech-Savvy Parent App', 'Technology', 'Millennial parents',
     ARRAY['Social Media', 'Google Ads', 'Content Marketing'], 85000.00, 40,
     0.0350, 0.1050, 7.60, 0.1100, 0.2600, 8.20, 'Interactive', 'Innovative', '2024-05-20'),

    ('CAMP_007', 'Sensitive Skin Care', 'Healthcare', 'Parents of babies with sensitive skin',
     ARRAY['Content Marketing', 'Email Marketing', 'Social Media'], 35000.00, 25,
     0.0480, 0.1380, 9.80, 0.1520, 0.3200, 9.45, 'Static Image', 'Professional', '2024-06-01'),

    ('CAMP_008', 'Budget-Friendly Essentials', 'Retail', 'Budget-conscious families',
     ARRAY['Social Media', 'Google Ads', 'Email Marketing'], 30000.00, 20,
     0.0560, 0.1650, 11.20, 0.1890, 0.3800, 10.15, 'Carousel', 'Urgent', '2024-07-01'),

    ('CAMP_009', 'Eco-Friendly Baby Products', 'Sustainability', 'Environmentally conscious parents',
     ARRAY['Content Marketing', 'Influencer Marketing', 'Social Media'], 55000.00, 35,
     0.0420, 0.1320, 9.40, 0.1420, 0.3100, 9.10, 'Video', 'Inspirational', '2024-08-15'),

    ('CAMP_010', 'First-Time Parent Support', 'Education', 'First-time parents',
     ARRAY['Email Marketing', 'Content Marketing', 'Social Media'], 45000.00, 50,
     0.0390, 0.1190, 8.20, 0.1280, 0.2700, 8.60, 'Blog Post', 'Caring', '2024-09-01');

-- Query examples to test the setup
-- Get top performing campaigns
SELECT campaign_name, industry, success_score, roas, channels FROM campaigns WHERE success_score >= 8.0 ORDER BY success_score DESC;

-- Channel performance analysis
SELECT
    channel,
    AVG(success_score) as avg_success_score,
    AVG(roas) as avg_roas,
    AVG(ctr) as avg_ctr,
    COUNT(*) as campaign_count
FROM (
    SELECT unnest(channels) as channel, success_score, roas, ctr
    FROM campaigns
) channel_data
GROUP BY channel
ORDER BY avg_success_score DESC;

-- Industry performance
SELECT
    industry,
    AVG(success_score) as avg_success_score,
    AVG(budget) as avg_budget,
    COUNT(*) as campaign_count
FROM campaigns GROUP BY industryORDER BY avg_success_score DESC;

-- Budget vs Performance correlation
SELECT
    CASE
        WHEN budget < 40000 THEN 'Low Budget'
        WHEN budget < 70000 THEN 'Medium Budget'
        ELSE 'High Budget'
    END as budget_category,
    AVG(success_score) as avg_success_score,
    AVG(roas) as avg_roas,
    COUNT(*) as campaign_count
FROM campaigns
GROUP BY budget_category
ORDER BY avg_success_score DESC;