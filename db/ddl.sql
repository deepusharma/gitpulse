create database dev;

create schema gitpulse;



-- Create a database for your projects
CREATE TABLE IF NOT EXISTS gitpulse.projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    github_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create a table to store git activity (useful for gitpulse later)
CREATE TABLE IF NOT EXISTS  gitpulse.git_activity (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES  gitpulse.projects(id),
    commit_hash VARCHAR(40),
    commit_message TEXT,
    author VARCHAR(100),
    committed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
