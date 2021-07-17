CREATE TABLE churn_studies.metric_name (
    metric_name_id integer NOT NULL,
    metric_name text COLLATE pg_catalog."default"
) WITH (OIDS = FALSE) TABLESPACE pg_default;

ALTER TABLE
    churn_studies.metric_name OWNER TO postgres;

CREATE UNIQUE INDEX idx_metric_name_id ON churn_studies.metric_name USING btree (metric_name_id) TABLESPACE pg_default;

CREATE UNIQUE INDEX idx_metric_name_name ON churn_studies.metric_name USING btree (metric_name COLLATE pg_catalog."default") TABLESPACE pg_default;