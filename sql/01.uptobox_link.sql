SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;
SET default_tablespace = '';

CREATE EXTENSION IF NOT EXISTS pg_trgm;

DROP TABLE IF EXISTS uptobox_link;
CREATE TABLE uptobox_link (
  id integer PRIMARY KEY DEFAULT nextval('seq_general'),
  enabled boolean NOT NULL DEFAULT TRUE,
  created timestamp without time zone NOT NULL DEFAULT now(),
  version timestamp without time zone NOT NULL DEFAULT now(),

  date timestamp without time zone NOT NULL,
  token varchar(12) NOT NULL,
  title varchar(255) NOT NULL,
  size integer NOT NULL,

  expiration_date timestamp with time zone NOT NULL,
  vector tsvector NOT NULL
);
ALTER TABLE uptobox_link ADD CONSTRAINT uptobox_link_token_uniq UNIQUE(token);
CREATE INDEX uptobox_link_token_index ON uptobox_link USING btree(token) WHERE enabled = true;
CREATE INDEX uptobox_link_title_trigram_index ON uptobox_link USING GIN(title gin_trgm_ops) WHERE enabled = true;
CREATE INDEX uptobox_link_title_vector_index ON uptobox_link USING GIN(vector) WHERE enabled = true;
CREATE INDEX uptobox_link_expiration_date_index ON uptobox_link USING BTREE(expiration_date) WHERE enabled = true;