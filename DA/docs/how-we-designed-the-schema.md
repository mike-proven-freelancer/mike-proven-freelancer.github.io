# How we designed the schema (and how you can do it when the ask is vague)

A step-by-step explanation of where the tables and columns came from, and how to plan a schema when the job description isn’t crystal clear.

---

## The problem you’re naming

The job said things like “combine multiple sources,” “structure into research-grade datasets,” and “evaluate predictive models” — but it didn’t spell out “build these 5 tables with these 20 columns.” So it feels like:

- You’re supposed to “clean and organize chaos” (general).
- You also want to “overdeliver” with something useful and actionable.
- That seems to start with schema design — but you’re not sure how to decide what’s meaningful when you don’t know exactly what they’ll ask for.

Below is how we actually decided what to build, so you can reuse this way of thinking on other projects.

---

## Step 1: You don’t need to predict every question — just the *kind* of use

You don’t have to know every report or model upfront. You only need to know:

- **Who/what are the main “nouns”?** (accounts, channels, creators, content, campaigns)
- **What “verbs” or events happen over time?** (posts get engagement, campaigns spend money, revenue is earned)
- **What does the job imply they’ll do with the data?** (compare model outputs to historical outcomes → need time-series and clear “when”)

So “meaningful” here means: *needed to describe those nouns and events in a way that supports typical analyses and backtests.* We didn’t guess one specific question; we guessed the **categories** of questions (reporting, trends, prediction, allocation) and designed so those are possible.

---

## Step 2: Use the job description to infer “nouns” and “verbs”

We re-read the job and pulled out clues:

| Job wording | What we inferred |
|-------------|-------------------|
| “Multiple public sources” | Data will come from several places (platform, ads, affiliate, newsletter, etc.) — so we need **one place** to put it that can link those sources. |
| “Structuring into research-grade datasets” | We need **consistent IDs and definitions** so the same “post” or “campaign” is recognizable across files. |
| “Reconstructing historical information snapshots” | We need **dates** and a clear **grain** (e.g. one row per day per post) so we can say “what did we know as of date X?” |
| “Evaluating predictive decision models” / “backtests” | We need **outcomes we can compare to** (e.g. actual engagement or revenue) and **time order** (train on past, test on future). |
| “Identifying patterns across structured datasets” | We need **dimensions** (channel, theme, creator, campaign) so we can group and compare. |

So even though the job didn’t say “build fact_post_performance_daily,” we inferred: they’ll want **time-series metrics** (daily is a common grain) and **entities** to slice by. That’s enough to start a schema.

---

## Step 3: List the entities (“nouns”) that show up in the raw world

We imagined what a content publisher actually has, based on the job and the industry:

- **Account** — the brand (BrightWave Media).
- **Channel** — where we publish (blog, newsletter, social platform X).
- **Creator** — who writes or presents the content.
- **Content** — each piece (post, article, video).
- **Campaign** — each paid push (ads, promotions).

Those become **dimension tables**: one row per entity, with stable IDs and attributes (name, type, dates). We didn’t invent these from nowhere — they’re the things that appear in real-world exports (post IDs, campaign IDs, channel names, etc.). So “how did you know?” → We looked at what the job and the business domain imply exists, and made one table per major entity.

---

## Step 4: List what happens over time (“verbs” / events)

Then we asked: what **happens** that we’d want to measure or predict?

- **Engagement** — each day, each piece of content gets impressions, likes, shares, clicks, comments.
- **Spend** — each day, each campaign spends money and gets impressions/clicks.
- **Revenue** — individual events: affiliate sale, sponsorship payment, subscription signup.

Those become **fact tables**: one row per “event” or per “day summary,” with a **date** and **IDs** linking to the dimension tables. So we get:

- `fact_post_performance_daily` — one row per (content, date) with engagement metrics.
- `fact_campaign_spend_daily` — one row per (campaign, date) with spend and delivery.
- `fact_revenue_events` — one row per revenue event, with optional links to content or campaign.

We didn’t need the client to say “we need a fact_post_performance_daily table.” We needed them to say “we have multiple sources and want to evaluate models” — that implies we need **time-series facts** and **links to dimensions**. Standard pattern: **dimensions = who/what**, **facts = what happened when**.

---

## Step 5: Choose a grain (one row = what?)

“Grain” means: what does **one row** represent?

- **Dimensions**: one row per account, per channel, per creator, per content piece, per campaign. That’s the natural grain for “entities.”
- **Facts**: we chose **daily** for performance and spend (one row per content per day, one row per campaign per day) because:
  - The job mentioned “historical snapshots” and “backtests” — daily is fine for training and testing.
  - It’s a common grain in analytics and keeps the dataset size manageable.
- **Revenue**: one row per **event** (each sale or payment), because revenue is often reported per transaction.

So “how did you know what columns?” For **dimensions**, we added what you’d need to describe and filter: IDs, names, types, created/published dates. For **facts**, we added what the job and domain imply: **date**, **IDs** to join to dimensions, and **metrics** (impressions, clicks, spend, amount). We didn’t list every possible metric — we listed the ones that support the kinds of questions we inferred (revenue per post, cost per subscriber, engagement trends, next-week prediction, budget allocation).

---

## Step 6: Schema first, then cleaning — and why

Yes: we **designed the target schema before cleaning**. Here’s the order:

1. **Look at (or imagine) the raw sources** — what entities and events do they describe? What IDs and dates do they have?
2. **Design the “clean” target** — one schema (tables, columns, keys, grain) that can answer the kinds of questions you inferred.
3. **Cleaning = mapping raw → target** — parsing dates, deduplicating, filling missing values, joining sources so that the result fits the schema.

So the schema is the **destination**. You’re not “cleaning for the sake of it” — you’re cleaning **toward** that structure. If the client later asks for something you didn’t plan for, you might add a column or a table; that’s normal. The first pass is “what’s the minimum useful structure that supports backtests and pattern-finding?”

---

## Step 7: How to do this when *you* don’t know what they want

When the ask is “general clean and organize this chaos”:

1. **List the nouns in the raw data** (or in the client’s description). Those are candidate dimensions.
2. **List the events or metrics that change over time.** Those are candidate fact tables.
3. **Ask yourself: “If they wanted to compare last month to this month, or run a backtest, what would they need?”** Usually: dates, IDs that link sources, and numeric outcomes. Add those.
4. **Use a simple pattern**: dimensions (who/what) + facts (what happened when, at what grain). That pattern works for most “we have messy data and want to analyze it” jobs.
5. **Start with one grain** (e.g. daily for performance). You can always add more detailed or more aggregated tables later.

You’re not trying to read their mind. You’re making a **reasonable, flexible** design from the clues they gave (multiple sources, historical snapshots, predictive models, patterns). Overdelivering then means: build that schema, clean the data into it, and show one or two concrete uses (e.g. a backtest, a KPI report) so they see it’s actionable.

---

## Summary

| Question | Short answer |
|----------|--------------|
| How did you know what tables to have? | We inferred **entities** (account, channel, creator, content, campaign) and **events** (daily engagement, daily spend, revenue events) from the job and the domain. |
| How did you know what columns? | Dimensions: IDs + names + types + dates. Facts: date + IDs to dimensions + numeric metrics that support reporting and backtests. |
| Do you design schema before cleaning? | Yes. Schema is the target; cleaning is the process of getting raw data into that shape. |
| What if the job isn’t clear? | Design for the *kind* of use (time-series, backtests, slicing by channel/theme/campaign). You don’t need every future question — just a structure that can support them. |
| What’s “meaningful” data? | Data that describes the entities and events at the grain you chose, so that the analyses you inferred (and similar ones) are possible. |

Next, we’ll generate the messy raw files and then show how each one maps into this schema — so you see how “chaos” turns into the clean tables we designed.
