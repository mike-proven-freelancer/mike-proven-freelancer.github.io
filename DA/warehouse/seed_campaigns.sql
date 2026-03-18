-- Campaign dimension rows for campaign spend fact data (CAMP-Q1-PUSH, CAMP-Q1-SUB).
-- Run after schema.sql and seed_dimensions.sql. Safe to run multiple times.

INSERT OR IGNORE INTO dim_campaign (campaign_id, channel_id, name, start_date, end_date, objective) VALUES
  ('CAMP-Q1-PUSH', 'CH-blog', 'Q1 Content Push', '2024-01-15', '2024-03-31', 'engagement'),
  ('CAMP-Q1-SUB', 'CH-blog', 'Q1 Subscription Drive', '2024-01-17', '2024-03-31', 'subscriptions');
