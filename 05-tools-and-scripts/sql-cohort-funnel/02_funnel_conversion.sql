-- =============================================================================
-- Funnel Conversion Analysis (with time-to-convert)
-- =============================================================================
-- Business question: for a defined sequence of steps (e.g. viewed pricing ->
-- started signup -> completed signup -> activated), what's the conversion
-- rate at each step, and how long does it typically take users to move
-- through the funnel? This version enforces ORDER (step 2 must happen after
-- step 1 for the same user) rather than just counting "did this event ever
-- happen," which is the most common funnel-query mistake.
--
-- Assumes: events(user_id, event_date, event_name)
-- Edit the step_definitions CTE to match your actual event names and order.
-- =============================================================================

WITH step_definitions AS (
    -- Define your funnel steps here, in order. step_number must be sequential.
    SELECT 1 AS step_number, 'viewed_pricing_page' AS event_name
    UNION ALL SELECT 2, 'started_signup'
    UNION ALL SELECT 3, 'completed_signup'
    UNION ALL SELECT 4, 'activated_account'
),

user_step_events AS (
    -- For each user, find the FIRST time they completed each step
    SELECT
        e.user_id,
        sd.step_number,
        sd.event_name,
        MIN(e.event_date) AS step_completed_at
    FROM events e
    JOIN step_definitions sd
        ON e.event_name = sd.event_name
    GROUP BY e.user_id, sd.step_number, sd.event_name
),

ordered_funnel AS (
    -- Self-join each step to the previous step, requiring it to have
    -- happened earlier in time. This is what enforces "order" instead of
    -- just "did the event happen at all."
    SELECT
        curr.user_id,
        curr.step_number,
        curr.event_name,
        curr.step_completed_at,
        prev.step_completed_at AS previous_step_completed_at
    FROM user_step_events curr
    LEFT JOIN user_step_events prev
        ON curr.user_id = prev.user_id
        AND prev.step_number = curr.step_number - 1
        AND prev.step_completed_at <= curr.step_completed_at
    WHERE curr.step_number = 1
       OR prev.step_completed_at IS NOT NULL  -- step N only counts if step N-1 happened first
)

SELECT
    step_number,
    event_name,
    COUNT(DISTINCT user_id) AS users_reaching_step,
    ROUND(
        COUNT(DISTINCT user_id) * 100.0 /
        FIRST_VALUE(COUNT(DISTINCT user_id)) OVER (ORDER BY step_number),
        1
    ) AS pct_of_funnel_start,
    -- Step-over-step conversion (this step vs. the immediately preceding one)
    ROUND(
        COUNT(DISTINCT user_id) * 100.0 /
        LAG(COUNT(DISTINCT user_id)) OVER (ORDER BY step_number),
        1
    ) AS pct_of_previous_step,
    -- Median time to convert from the previous step, in hours
    MEDIAN(
        DATEDIFF('hour', previous_step_completed_at, step_completed_at)
    ) AS median_hours_since_previous_step
FROM ordered_funnel
GROUP BY step_number, event_name
ORDER BY step_number;

-- Output shape:
-- step_number | event_name           | users_reaching_step | pct_of_funnel_start | pct_of_previous_step | median_hours_since_previous_step
-- 1           | viewed_pricing_page  | 10000                | 100.0                | NULL                  | NULL
-- 2           | started_signup       | 3200                 | 32.0                 | 32.0                  | 0.4
-- 3           | completed_signup     | 2100                 | 21.0                 | 65.6                  | 2.1
-- 4           | activated_account    | 1400                 | 14.0                 | 66.7                  | 18.5
--
-- Read: step 4's median_hours tells you most activated users took ~18.5
-- hours between completing signup and activating, which is a strong signal
-- for where to time an onboarding nudge email.
