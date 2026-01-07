-- Complete Asana Simulation Schema

-- Organizations/Workspaces
CREATE TABLE organizations (
    id TEXT PRIMARY KEY,  -- Asana GID format
    name TEXT NOT NULL,
    domain TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_personal BOOLEAN DEFAULT FALSE
);

-- Users
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT CHECK(role IN ('owner', 'admin', 'member', 'guest')) DEFAULT 'member',
    department TEXT,
    job_title TEXT,
    timezone TEXT DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Teams
CREATE TABLE teams (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    organization_id TEXT,
    department TEXT CHECK(department IN ('engineering', 'product', 'design', 'marketing', 'sales', 'operations', 'support')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (organization_id) REFERENCES organizations(id)
);

-- Team Memberships
CREATE TABLE team_memberships (
    id TEXT PRIMARY KEY,
    team_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT CHECK(role IN ('team_lead', 'member', 'viewer')) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(team_id, user_id),
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Projects
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    team_id TEXT NOT NULL,
    owner_id TEXT,  -- User ID
    color TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    project_type TEXT CHECK(project_type IN ('sprint', 'bug_tracking', 'campaign', 'okr', 'ongoing', 'adhoc')),
    status TEXT CHECK(status IN ('active', 'completed', 'archived', 'on_hold')) DEFAULT 'active',
    start_date DATE,
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- Sections (Columns in projects)
CREATE TABLE sections (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    project_id TEXT NOT NULL,
    position INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Tasks
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    project_id TEXT NOT NULL,
    section_id TEXT,
    assignee_id TEXT,  -- User ID
    parent_task_id TEXT,  -- For subtasks
    due_date DATE,
    due_time TIME,
    start_date DATE,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
    effort INTEGER CHECK(effort BETWEEN 1 AND 10),  -- Story points
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_reason TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES sections(id),
    FOREIGN KEY (assignee_id) REFERENCES users(id),
    FOREIGN KEY (parent_task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

-- Comments/Stories
CREATE TABLE comments (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_pinned BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tags
CREATE TABLE tags (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    color TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Task-Tag Associations
CREATE TABLE task_tags (
    task_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (task_id, tag_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Custom Field Definitions
CREATE TABLE custom_field_definitions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    field_type TEXT CHECK(field_type IN ('text', 'number', 'enum', 'date', 'person')),
    enum_options TEXT,  -- JSON array for enum type
    project_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Custom Field Values
CREATE TABLE custom_field_values (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    field_id TEXT NOT NULL,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, field_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (field_id) REFERENCES custom_field_definitions(id) ON DELETE CASCADE
);

-- Attachments (simplified)
CREATE TABLE attachments (
    id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_type TEXT,
    url TEXT,
    uploaded_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_comments_task_id ON comments(task_id);
CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_projects_team_id ON projects(team_id);