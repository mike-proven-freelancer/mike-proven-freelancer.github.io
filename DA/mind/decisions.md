# Decisions log

Concise record of why we chose certain options (for AI/future context).

| Decision | Choice | Reason |
|----------|--------|--------|
| Company context | Brand/content publisher (BrightWave Media) | User selected; aligns with “social media / content success” and multi-source data. |
| Web-friendly outputs | CSV, MD, HTML reports, notebooks, SQLite + schema + extracts | User selected all; plus optional messy raw formats to emulate real-world difficulties. |
| Database | SQLite | Single file, portable, static-site friendly; schema + CSV exports for browsing. |
| Languages | Python + R | Job post mentions Python; user requested same tasks in R for learning and portfolio. |
| Data | Fully synthetic, 100+ records per core entity | No real people; de-identification impossible; realistic patterns only. |
| Phases | 1=Design, 2=Build data, 3=Insights + action plan | Matches user’s three-phase description in first-proj.txt. |
| Mind folder | Used for phase state, tasks, glossary, decisions | User requested; for AI continuity and project organization; user does not need to read it. |
| Chats folder | `chats/` stores exported chat transcripts | User requested; future AIs should read `mind/context.md` then `chats/` for continuity. |
