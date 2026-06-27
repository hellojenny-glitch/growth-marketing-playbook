# Cohort Retention & Funnel Conversion Queries (Snowflake)

Two SQL queries that answer the two questions growth teams ask most often:
"are we keeping the users we acquire?" and "where exactly do people fall out
of the signup/activation funnel?"

Written for Snowflake syntax (`DATE_TRUNC`, `DATEDIFF`, `MEDIAN`, window
functions), but the logic ports to BigQuery or Postgres with minor function
name changes.

## 01_cohort_retention.sql

Groups users by signup month, then measures what percentage of each cohort
is still active in month 0, 1, 2, 3... This is the standard "cohort table"
view you'd see in a board deck, the one where every row is a signup month and
every column is months-since-signup, and the numbers decay as you move right.

**What makes this version correct rather than just plausible-looking:** it
joins activity to cohort with `activity_month >= cohort_month`, so a user's
pre-signup activity (imported historical events, testing, etc.) can't
inflate month-0 retention. It's a common bug to skip.

**To adapt it:** swap the `events` table reference and tighten the
`WHERE event_name = ...` filter to match whatever "active" means for your
product. Page views are a weak definition of active; a core action (sent a
message, made a purchase, completed a workout) is a strong one.

## 02_funnel_conversion.sql

Measures conversion through an ordered sequence of steps (e.g. viewed
pricing -> started signup -> completed signup -> activated), plus the median
time it took users to move between each step.

**What makes this version correct rather than just plausible-looking:** most
funnel queries people write count "did the user ever do X" independently
per step, which silently breaks the moment a user does step 3 before step 2
(imported data, replay traffic, multi-session weirdness). This query
self-joins each step to the prior step with a timestamp constraint, so step N
only counts if step N-1 genuinely happened first for that user.

**To adapt it:** edit the `step_definitions` CTE with your actual event
names and order. The query handles any number of steps without further
changes.

## Why these are written this way

Both queries are deliberately over-commented relative to how I'd write them
in a real PR. That's intentional here: the goal is to show the reasoning
behind each design choice (why the join condition is what it is, what bug it
prevents), not just the working code. In production I'd trim the comments to
the non-obvious parts and let the column names carry the rest.
