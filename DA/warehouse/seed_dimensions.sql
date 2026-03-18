-- Minimal dimension rows so we can load engagement fact data (CONT-001..CONT-005).
-- Run after schema.sql. Safe to run multiple times (INSERT OR IGNORE / REPLACE as needed).

INSERT OR IGNORE INTO dim_account (account_id, name, created_at, region) VALUES
  ('BW001', 'BrightWave Media', '2022-01-01', 'US');

INSERT OR IGNORE INTO dim_channel (channel_id, account_id, name, platform, created_at) VALUES
  ('CH-blog', 'BW001', 'BrightWave Blog', 'blog', '2022-01-15');

INSERT OR IGNORE INTO dim_creator (creator_id, account_id, display_name, role, joined_at) VALUES
  ('CR-Alex', 'BW001', 'Alex Chen', 'Writer', '2022-02-01'),
  ('CR-Jordan', 'BW001', 'Jordan Lee', 'Writer', '2022-02-01');

INSERT OR IGNORE INTO dim_content (content_id, channel_id, creator_id, title, theme, content_type, published_at) VALUES
  ('CONT-001', 'CH-blog', 'CR-Alex', 'How to Build a Budget That Works', 'Budgeting & Saving', 'article', '2024-01-10'),
  ('CONT-002', 'CH-blog', 'CR-Jordan', 'Investing Basics for Beginners', 'Investing Basics', 'article', '2024-01-12'),
  ('CONT-003', 'CH-blog', 'CR-Alex', 'Retirement Planning in Your 30s', 'Retirement Planning', 'article', '2024-01-14'),
  ('CONT-004', 'CH-blog', 'CR-Jordan', 'FinTech Apps Worth Trying', 'FinTech & Digital Banking', 'article', '2024-01-16'),
  ('CONT-005', 'CH-blog', 'CR-Alex', 'Side Hustles That Actually Pay', 'Small Business & Side Hustles', 'article', '2024-01-18');
