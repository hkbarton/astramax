DROP DATABASE IF EXISTS astramax;
CREATE DATABASE astramax;

\c astramax;

CREATE TABLE message (
  id VARCHAR(50) UNIQUE NOT NULL PRIMARY KEY,
  payload TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  processed_by VARCHAR(255) NULL
);