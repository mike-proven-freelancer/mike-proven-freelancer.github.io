## **Project phases (what you will actually do)**

### **We will forecast stock inventory purchases by “Brick N’ Mortar Merchant”**

### **Phase 1 — Frame the question**

- **Decision the forecast supports** (e.g. “rough staffing for the next 4 weeks,” not “predict the universe”).
- **Horizon:** next 7 days, 4 weeks, or 3 months—**short** horizons are easier to defend honestly.
- **Metric:** exactly what is being predicted (e.g. “total weekly sales in dollars”).

Use this, or something better and more specific and professional: How much inventory should be ordered for the next two months?

### **Phase 2 — Understand the history**

- Plot the full series; note **trend**, **seasonality** (day-of-week, month, holidays), and **odd spikes** (promotions, outages, COVID-era breaks).
- Write 2–3 bullets: **what would surprise a naive reader** (e.g. “December is always high”).

Use this, or something better and more specific and professional: Measure current existing inventory stock, compare to last year’s sales data, compare next month and the month after’s sales data of previous years. Compare the annual trends and % change per year, apply this % to this year based on current monthly % change average. Create and use 36 months of Inventory and sales data over 3 products (‘a-brand’, ‘b-brand’, ‘c-brand’ products)

### **Phase 3 — Build simple baselines (on purpose)**

Start dumb on purpose; it makes the story teachable.

- **Naive baseline:** last value repeated, or same week last year (if yearly seasonality exists).

Use this, or something better and more specific and professional: Last year = baseline

- **Moving average** over a sensible window.

Use this, or something better and more specific and professional: Applied % change from above to future projected inventory orders 

- Optional: one slightly smarter method you can explain (e.g. **seasonal naive** or a **small** off-the-shelf model **only if** you can explain it in plain language).

**Train/test split:** Hold out the **last N periods** and score forecasts against them (simple error summaries in plain language: “typically off by about X”).

### **Phase 4 — “With humility” (this is the differentiator)**

- **Point forecast + interval or band:** e.g. “best guess” plus “could reasonably fall between A and B” using simple methods (residual spread, bootstrap, or pre-built prediction intervals—pick one you can explain).

Use this, or something better and more specific and professional: “Best guess” is based on this year’s (15 month) sales trend compared to last year’s (months 16 to 30) sales trend. 

- **Scenarios:** e.g. “if the next month is **10% below** the recent average, what does that imply for the sum?” (arithmetic scenario, not a second model.)

Use this, or something better and more specific and professional: Apply the scenario of consumer tightening and reduced inventory based on future energy concerns, conflicts, and costs.

- **Assumptions list:** “No major policy change,” “same store set,” “no new competitor,” etc.—whatever fits the data story.

Use this, or something better and more specific and professional: If nothing happens, and marketing strategies only maintain consumer interest.

### **Phase 5 — Deliverables (good enough for GitHub + a blog snippet)**

- **README** — question, data source, how to run, limitations.
- **Notebook or script** — clean, commented for a hiring manager skimming.
- **Charts** — history + holdout forecast + scenario band.
- **Short narrative** — 5–10 sentences a non-technical owner could follow.

