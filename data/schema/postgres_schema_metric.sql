CREATE TABLE IF NOT EXISTS churn_studies.metric (
    account_id character(32) COLLATE pg_catalog."default",
    metric_time timestamp(6) without time zone NOT NULL,
    metric_name_id integer NOT NULL,
    metric_value real
) WITH (OIDS = FALSE) TABLESPACE pg_default;

ALTER TABLE
    churn_studies.metric OWNER TO postgres;

CREATE INDEX IF NOT EXISTS idx_metric_account_id ON churn_studies.metric USING btree (account_id) TABLESPACE pg_default;

CREATE UNIQUE INDEX IF NOT EXISTS idx_metric_account_time ON churn_studies.metric USING btree (account_id, metric_name_id, metric_time) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_metric_time ON churn_studies.metric USING btree (metric_time, metric_name_id) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_metric_type ON churn_studies.metric USING btree (metric_name_id) TABLESPACE pg_default;