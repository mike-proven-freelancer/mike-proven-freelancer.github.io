-- BrightWave Media benchmark schema (SQLite)
-- See docs/data-spec.md for full specification.

-- Dimensions
CREATE TABLE IF NOT EXISTS dim_account (
  account_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TEXT,
  region TEXT
);

CREATE TABLE IF NOT EXISTS dim_channel (
  channel_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  name TEXT NOT NULL,
  platform TEXT,
  created_at TEXT,
  FOREIGN KEY (account_id) REFERENCES dim_account(account_id)
);

CREATE TABLE IF NOT EXISTS dim_creator (
  creator_id TEXT PRIMARY KEY,
  account_id TEXT NOT NULL,
  display_name TEXT NOT NULL,
  role TEXT,
  joined_at TEXT,
  FOREIGN KEY (account_id) REFERENCES dim_account(account_id)
);

CREATE TABLE IF NOT EXISTS dim_content (
  content_id TEXT PRIMARY KEY,
  channel_id TEXT NOT NULL,
  creator_id TEXT NOT NULL,
  title TEXT,
  theme TEXT,
  content_type TEXT,
  published_at TEXT,
  FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id),
  FOREIGN KEY (creator_id) REFERENCES dim_creator(creator_id)
);

CREATE TABLE IF NOT EXISTS dim_campaign (
  campaign_id TEXT PRIMARY KEY,
  channel_id TEXT NOT NULL,
  name TEXT NOT NULL,
  start_date TEXT,
  end_date TEXT,
  objective TEXT,
  FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id)
);

-- Bridge: content promoted by campaign (many-to-many)
CREATE TABLE IF NOT EXISTS bridge_post_campaign (
  content_id TEXT NOT NULL,
  campaign_id TEXT NOT NULL,
  PRIMARY KEY (content_id, campaign_id),
  FOREIGN KEY (content_id) REFERENCES dim_content(content_id),
  FOREIGN KEY (campaign_id) REFERENCES dim_campaign(campaign_id)
);

-- Facts
CREATE TABLE IF NOT EXISTS fact_post_performance_daily (
  content_id TEXT NOT NULL,
  date TEXT NOT NULL,
  impressions INTEGER,
  likes INTEGER,
  shares INTEGER,
  clicks INTEGER,
  comments INTEGER,
  PRIMARY KEY (content_id, date),
  FOREIGN KEY (content_id) REFERENCES dim_content(content_id)
);

CREATE TABLE IF NOT EXISTS fact_campaign_spend_daily (
  campaign_id TEXT NOT NULL,
  date TEXT NOT NULL,
  spend REAL,
  impressions INTEGER,
  clicks INTEGER,
  PRIMARY KEY (campaign_id, date),
  FOREIGN KEY (campaign_id) REFERENCES dim_campaign(campaign_id)
);

CREATE TABLE IF NOT EXISTS fact_revenue_events (
  event_id TEXT PRIMARY KEY,
  content_id TEXT,
  campaign_id TEXT,
  date TEXT NOT NULL,
  amount REAL NOT NULL,
  type TEXT NOT NULL,
  FOREIGN KEY (content_id) REFERENCES dim_content(content_id),
  FOREIGN KEY (campaign_id) REFERENCES dim_campaign(campaign_id)
);

-- Newsletter send summary (one row per send date; from vendor TSV export)
CREATE TABLE IF NOT EXISTS fact_newsletter_daily (
  date TEXT PRIMARY KEY,
  recipients INTEGER,
  sends INTEGER,
  opens INTEGER,
  clicks INTEGER,
  unsubscribes INTEGER,
  bounces INTEGER
);

-- Indexes for common joins and filters
CREATE INDEX IF NOT EXISTS idx_perf_content ON fact_post_performance_daily(content_id);
CREATE INDEX IF NOT EXISTS idx_perf_date ON fact_post_performance_daily(date);
CREATE INDEX IF NOT EXISTS idx_spend_campaign ON fact_campaign_spend_daily(campaign_id);
CREATE INDEX IF NOT EXISTS idx_spend_date ON fact_campaign_spend_daily(date);
CREATE INDEX IF NOT EXISTS idx_revenue_date ON fact_revenue_events(date);
CREATE INDEX IF NOT EXISTS idx_revenue_type ON fact_revenue_events(type);
CREATE INDEX IF NOT EXISTS idx_newsletter_date ON fact_newsletter_daily(date);
