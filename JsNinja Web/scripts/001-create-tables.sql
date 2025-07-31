-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create scans table
CREATE TABLE IF NOT EXISTS scans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    url TEXT,
    filename VARCHAR(255),
    file_size INTEGER,
    scan_type VARCHAR(50) NOT NULL, -- 'url' or 'file'
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'completed', 'failed'
    total_secrets INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Create secrets table
CREATE TABLE IF NOT EXISTS secrets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    secret_type VARCHAR(255) NOT NULL,
    secret_value TEXT NOT NULL,
    line_number INTEGER,
    context TEXT,
    severity VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_scans_project_id ON scans(project_id);
CREATE INDEX IF NOT EXISTS idx_secrets_scan_id ON secrets(scan_id);
CREATE INDEX IF NOT EXISTS idx_secrets_type ON secrets(secret_type);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at);
