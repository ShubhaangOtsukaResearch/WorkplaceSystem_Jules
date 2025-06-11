CREATE TABLE IF NOT EXISTS use_cases (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    requestor VARCHAR(255),
    description TEXT,
    rationale TEXT,
    stage VARCHAR(50),
    reviewed_by_ai_committee BOOLEAN DEFAULT FALSE,
    date_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)
);

-- Note on data types and defaults:
-- SERIAL PRIMARY KEY: Auto-incrementing integer for id.
-- VARCHAR(255) NOT NULL for title: Assuming title is mandatory and has a reasonable length limit.
-- VARCHAR(255) for requestor, updated_by: Standard string fields.
-- TEXT for description, rationale: For longer text content.
-- VARCHAR(50) for stage: Assuming stage is a string like "Draft", "Review", "Approved".
-- BOOLEAN DEFAULT FALSE for reviewed_by_ai_committee: Defaults to false.
-- TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP for date_updated: Automatically sets to current timestamp on creation.
-- For onupdate behavior for date_updated, a trigger would typically be used in PostgreSQL,
-- as 'ON UPDATE CURRENT_TIMESTAMP' is not standard SQL for TIMESTAMP columns in PostgreSQL.
-- This script provides the basic table structure. Further database-specific optimizations or
-- trigger definitions for 'date_updated' on update can be added later if needed.

COMMENT ON COLUMN use_cases.date_updated IS 'For PostgreSQL, an explicit trigger is needed to update this timestamp on row update. Example: CREATE OR REPLACE FUNCTION update_modified_column() RETURNS TRIGGER AS $$ BEGIN NEW.date_updated = NOW(); RETURN NEW; END; $$ language 'plpgsql'; CREATE TRIGGER update_use_case_modtime BEFORE UPDATE ON use_cases FOR EACH ROW EXECUTE PROCEDURE update_modified_column();';
