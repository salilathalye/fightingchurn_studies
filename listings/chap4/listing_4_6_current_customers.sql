WITH metric_date AS (
    SELECT
        max(metric_time) AS last_metric_time
    FROM
        metric
)
SELECT
    m.account_id,
    d.last_metric_time,
    sum(
        CASE
            WHEN metric_name_id = 0 THEN metric_value
            ELSE 0
        END
    ) AS ReadingOwnedBook_90d,
    sum(
        CASE
            WHEN metric_name_id = 1 THEN metric_value
            ELSE 0
        END
    ) AS FirstLivebookAccess_90d,
    sum(
        CASE
            WHEN metric_name_id = 2 THEN metric_value
            ELSE 0
        END
    ) AS FirstManningAccess_90d,
    sum(
        CASE
            WHEN metric_name_id = 3 THEN metric_value
            ELSE 0
        END
    ) AS EBookDownloaded_90d,
    sum(
        CASE
            WHEN metric_name_id = 4 THEN metric_value
            ELSE 0
        END
    ) AS ReadingFreePreview_90d,
    sum(
        CASE
            WHEN metric_name_id = 5 THEN metric_value
            ELSE 0
        END
    ) AS HighlightCreated_90d,
    sum(
        CASE
            WHEN metric_name_id = 6 THEN metric_value
            ELSE 0
        END
    ) AS FreeContentCheckout_90d,
    sum(
        CASE
            WHEN metric_name_id = 7 THEN metric_value
            ELSE 0
        END
    ) AS ReadingOpenChapter_90d,
    sum(
        CASE
            WHEN metric_name_id = 8 THEN metric_value
            ELSE 0
        END
    ) AS TimeReadingOwnedBook_90d
FROM
    metric m
    INNER JOIN metric_date d ON m.metric_time = d.last_metric_time
GROUP BY
    m.account_id,
    d.last_metric_time
ORDER BY
    m.account_id