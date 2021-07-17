WITH date_vals AS (
	SELECT
		i :: timestamp AS metric_date
	FROM
		generate_series(
			'%from_yyyy-mm-dd',
			'%to_yyyy-mm-dd',
			'7 day' :: INTERVAL
		) i
)
INSERT INTO
	metric (
		account_id,
		metric_time,
		metric_name_id,
		metric_value
	)
SELECT
	account_id,
	metric_date,
	'%new_metric_id',
	count(*) AS metric_value
FROM
	event e
	INNER JOIN date_vals d ON e.event_time < metric_date
	AND e.event_time >= metric_date - INTERVAL '90 day'
WHERE
	event_type = '%event2measure'
GROUP BY
	account_id,
	metric_date ON CONFLICT DO NOTHING;