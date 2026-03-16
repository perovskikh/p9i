-- AI Prompt System Database Schema
-- Version: 1.0
-- Applied: 2026-03-16

-- ============================================================================
-- PROMPTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS prompts (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0.0',
    type TEXT,
    layer TEXT,
    tags TEXT[] DEFAULT '{}',
    variables JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for prompts
CREATE INDEX idx_prompts_name ON prompts(name);
CREATE INDEX idx_prompts_type_layer ON prompts(type, layer);
CREATE INDEX idx_prompts_fts ON prompts USING GIN(to_tsvector('english', content));

-- ============================================================================
-- PROMPT VERSIONS TABLE (History)
-- ============================================================================

CREATE TABLE IF NOT EXISTS prompt_versions (
    id SERIAL PRIMARY KEY,
    prompt_id INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    content TEXT NOT NULL,
    changelog TEXT,
    eval_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_prompt_versions_prompt_id ON prompt_versions(prompt_id);
CREATE INDEX idx_prompt_versions_created ON prompt_versions(created_at DESC);

-- ============================================================================
-- API KEYS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    project_id TEXT NOT NULL,
    permissions TEXT[] DEFAULT '{}',
    rate_limit INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX idx_api_keys_project ON api_keys(project_id);
CREATE INDEX idx_api_keys_key ON api_keys(key);

-- ============================================================================
-- PROJECTS TABLE (Multi-tenant)
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_projects_slug ON projects(slug);

-- ============================================================================
-- PROJECT MEMORY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS project_memory (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(project_id, key)
);

CREATE INDEX idx_project_memory_project ON project_memory(project_id);

-- ============================================================================
-- AUDIT LOG TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    api_key_id INTEGER REFERENCES api_keys(id),
    action TEXT NOT NULL,
    resource_type TEXT,
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_log_created ON audit_log(created_at DESC);
CREATE INDEX idx_audit_log_api_key ON audit_log(api_key_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);

-- ============================================================================
-- INSERT DEFAULT DATA
-- ============================================================================

-- Insert system API key (will be replaced by env in production)
INSERT INTO api_keys (key, project_id, permissions, rate_limit, is_active)
VALUES ('sk-system-dev', 'system', ARRAY['*'], 1000, true)
ON CONFLICT (key) DO NOTHING;

-- Insert default project
INSERT INTO projects (name, slug)
VALUES ('System', 'system')
ON CONFLICT (slug) DO NOTHING;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for prompts
CREATE TRIGGER update_prompts_updated_at
    BEFORE UPDATE ON prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for projects
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for project_memory
CREATE TRIGGER update_project_memory_updated_at
    BEFORE UPDATE ON project_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VERIFY
-- ============================================================================

SELECT 'Schema applied successfully' AS status;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';