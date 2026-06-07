-- This runs automatically when the Postgres container starts for the first time.
-- The database and user are already created via env vars in docker-compose.
-- This file is a good place to add seed data for practice.

-- Seed some sample todos
INSERT INTO todos (task, done) VALUES
  ('Learn Docker basics', true),
  ('Understand Docker Compose networking', false),
  ('Practice volume mounts', false),
  ('Try multi-stage builds', false)
ON CONFLICT DO NOTHING;
