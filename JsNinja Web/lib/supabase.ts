import { createClient } from "@supabase/supabase-js"

// Check if Supabase environment variables are available
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

// Create a mock client for development when Supabase is not configured
const createMockClient = () => ({
  from: (table: string) => ({
    select: (columns?: string) => ({
      eq: (column: string, value: any) => ({ data: [], error: null, count: 0 }),
      order: (column: string, options?: any) => ({ data: [], error: null, count: 0 }),
      limit: (count: number) => ({ data: [], error: null, count: 0 }),
      single: () => ({ data: null, error: { message: "Supabase not configured" } }),
      then: (callback: any) => callback({ data: [], error: null, count: 0 }),
    }),
    insert: (data: any) => ({
      select: () => ({
        single: () => ({ data: null, error: { message: "Supabase not configured" } }),
      }),
    }),
    update: (data: any) => ({
      eq: (column: string, value: any) => ({ data: null, error: { message: "Supabase not configured" } }),
    }),
    delete: () => ({
      eq: (column: string, value: any) => ({ data: null, error: { message: "Supabase not configured" } }),
    }),
  }),
})

export const supabase =
  supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : (createMockClient() as any)

export const isSupabaseConfigured = !!(supabaseUrl && supabaseKey)

export type Project = {
  id: string
  name: string
  description?: string
  created_at: string
  updated_at: string
}

export type Scan = {
  id: string
  project_id: string
  url?: string
  filename?: string
  file_size?: number
  scan_type: "url" | "file"
  status: "pending" | "completed" | "failed"
  total_secrets: number
  created_at: string
  completed_at?: string
}

export type Secret = {
  id: string
  scan_id: string
  secret_type: string
  secret_value: string
  line_number?: number
  context?: string
  severity: "low" | "medium" | "high" | "critical"
  created_at: string
}
