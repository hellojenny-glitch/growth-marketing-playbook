-- =============================================================================
-- Cohort Retention Analysis
-- =============================================================================
-- Business question: of users who signed up in a given month, what
-- percentage are still active in each subsequent month? This is the classic
-- "leaky bucket" view, used to spot whether retention is improving release
-- over release, and where the steepest drop-off happens (usually month 1).
--
-- Assumes two tables:
--   users(user_id, signup_date)
--   events(user_id, event_date, event_name)
-- Adjust table/column names to match your warehouse schema.
-- =============================================================================

WITH cohorts AS (
    -- Assign every user to a signup cohort month
    SELECT
        user_id,
        DATE_TRUNC('month', signup_date) AS cohort_month
    FROM users
),

activity AS (
    -- Pull every month in which a user was active (any event counts;
    -- swap event_name filter below if you want a stricter "active" definition,
    -- e.g. only 'session_start' or a specific product action)
    SELECT
        user_id,
        DATE_TRUNC('month', event_date) AS activity_month
    FROM events
    -- WHERE event_name = 'session_start'   -- uncomment to narrow the definition of "active"
    GROUP BY user_id, DATE_TRUNC('month', event_date)
),

cohort_activity AS (
    SELECT
        c.cohort_month,
        c.user_id,
        a.activity_month,
        DATEDIFF('month', c.cohort_month, a.activity_month) AS months_since_signup
    FROM cohorts c
    JOIN activity a
        ON c.user_id = a.user_id
        AND a.activity_month >= c.cohort_month   -- ignore activity before signup, shouldn't exist but defensive
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT user_id) AS total_users
    FROM cohorts
    GROUP BY cohort_month
)

SELECT
    ca.cohort_month,
    cs.total_users AS cohort_size,
    ca.months_since_signup,
    COUNT(DISTINCT ca.user_id) AS active_users,
    ROUND(
        COUNT(DISTINCT ca.user_id) / cs.total_users * 100,
        1
    ) AS retention_pct
FROM cohort_activity ca
JOIN cohort_size cs
    ON ca.cohort_month = cs.cohort_month
GROUP BY ca.cohort_month, cs.total_users, ca.months_since_signup
ORDER BY ca.cohort_month, ca.months_since_signup;

-- Output shape (pivot this in your BI tool or a follow-up query):
-- cohort_month | cohort_size | months_since_signup | active_users | retention_pct
-- 2026-01-01   | 1200        | 0                    | 1200         | 100.0
-- 2026-01-01   | 1200        | 1                    | 540          | 45.0
-- 2026-01-01   | 1200        | 2                    | 410          | 34.2
-- ...
