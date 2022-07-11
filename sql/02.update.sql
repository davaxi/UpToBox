SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;
SET default_tablespace = '';

DROP INDEX IF EXISTS uptobox_link_expiration_date_index ;
ALTER TABLE uptobox_link ADD COLUMN exported BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE uptobox_link DROP COLUMN IF EXISTS expiration_date;
ALTER TABLE uptobox_link ADD COLUMN like_count INTEGER NOT NULL DEFAULT 0;