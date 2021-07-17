CREATE TABLE IF NOT EXISTS churn_studies.event (
    account_id varchar NOT NULL,
    event_time timestamp(6) without time zone NOT NULL,
    event_type varchar NOT NULL,
    product_id integer NOT NULL,
    additional_data varchar
) WITH (OIDS = FALSE) TABLESPACE pg_default;

ALTER TABLE
    churn_studies.event OWNER TO postgres;

CREATE INDEX IF NOT EXISTS idx_event_account_id ON churn_studies.event USING btree (account_id) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_event_account_time ON churn_studies.event USING btree (account_id, event_time) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_event_time ON churn_studies.event USING btree (event_time) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_event_type ON churn_studies.event USING btree (event_type) TABLESPACE pg_default;

CREATE INDEX IF NOT EXISTS idx_product_id ON churn_studies.event USING btree (product_id) TABLESPACE pg_default;