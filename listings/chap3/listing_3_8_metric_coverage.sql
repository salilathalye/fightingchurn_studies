WITH date_range AS (
	SELECT
		'%from_yyyy-mm-dd' :: timestamp AS start_date,
		'%to_yyyy-mm-dd' :: timestamp AS end_date
),
account_count AS (
	SELECT
		count(DISTINCT account_id) AS n_account
	FROM
		event e
		INNER JOIN date_range d ON e.event_time BETWEEN start_date
		AND end_date
)
SELECT
	metric_name,
	count(DISTINCT m.account_id) AS count_with_metric,
	n_account AS n_account,
	(count(DISTINCT m.account_id)) :: float / n_account :: float AS pcnt_with_metric,
	avg(metric_value) AS avg_value,
	min(metric_value) AS min_value,
	max(metric_value) AS max_value,
	min(metric_time) AS earliest_metric,
	max(metric_time) AS last_metric
FROM
	metric m
	CROSS JOIN account_count
	INNER JOIN date_range ON metric_time >= start_date
	AND metric_time <= end_date
	INNER JOIN metric_name n ON m.metric_name_id = n.metric_name_id
GROUP BY
	metric_name,
	n_account
ORDER BY
	metric_name;