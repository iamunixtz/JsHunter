"use client"

import { useEffect, useState } from "react"
import { Bug, Shield, AlertTriangle, FileText, Activity } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, BarChart, Pie, PieChart, Cell, XAxis, YAxis } from "recharts"
import { supabase } from "@/lib/supabase"
import Link from "next/link"

interface DashboardStats {
  totalProjects: number
  totalScans: number
  totalSecrets: number
  criticalSecrets: number
  recentScans: any[]
  secretsByType: any[]
  scansByDay: any[]
  severityDistribution: any[]
}

const COLORS = ["#ef4444", "#f97316", "#eab308", "#22c55e"]

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      // Fetch basic counts
      const [projectsResult, scansResult, secretsResult] = await Promise.all([
        supabase.from("projects").select("*", { count: "exact" }),
        supabase.from("scans").select("*", { count: "exact" }),
        supabase.from("secrets").select("*", { count: "exact" }),
      ])

      // Fetch critical secrets count
      const { count: criticalCount } = await supabase
        .from("secrets")
        .select("*", { count: "exact" })
        .eq("severity", "critical")

      // Fetch recent scans
      const { data: recentScans } = await supabase
        .from("scans")
        .select(`
          *,
          projects(name)
        `)
        .order("created_at", { ascending: false })
        .limit(5)

      // Fetch secrets by type
      const { data: secretsByType } = await supabase
        .from("secrets")
        .select("secret_type")
        .then((result) => {
          const counts: Record<string, number> = {}
          result.data?.forEach((secret) => {
            counts[secret.secret_type] = (counts[secret.secret_type] || 0) + 1
          })
          return Object.entries(counts)
            .map(([type, count]) => ({ type, count }))
            .sort((a, b) => b.count - a.count)
            .slice(0, 10)
        })

      // Fetch severity distribution
      const { data: severityData } = await supabase
        .from("secrets")
        .select("severity")
        .then((result) => {
          const counts: Record<string, number> = { critical: 0, high: 0, medium: 0, low: 0 }
          result.data?.forEach((secret) => {
            counts[secret.severity] = (counts[secret.severity] || 0) + 1
          })
          return Object.entries(counts).map(([severity, count]) => ({ severity, count }))
        })

      // Fetch scans by day (last 7 days)
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)

      const { data: scansByDay } = await supabase
        .from("scans")
        .select("created_at")
        .gte("created_at", sevenDaysAgo.toISOString())
        .then((result) => {
          const counts: Record<string, number> = {}
          result.data?.forEach((scan) => {
            const date = new Date(scan.created_at).toLocaleDateString()
            counts[date] = (counts[date] || 0) + 1
          })
          return Object.entries(counts).map(([date, count]) => ({ date, count }))
        })

      setStats({
        totalProjects: projectsResult.count || 0,
        totalScans: scansResult.count || 0,
        totalSecrets: secretsResult.count || 0,
        criticalSecrets: criticalCount || 0,
        recentScans: recentScans || [],
        secretsByType: secretsByType || [],
        scansByDay: scansByDay || [],
        severityDistribution: severityData || [],
      })
    } catch (error) {
      console.error("Error fetching dashboard stats:", error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="container mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-slate-700 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-slate-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Link href="/" className="flex items-center gap-2">
                <div className="flex items-center justify-center w-10 h-10 bg-red-600 rounded-lg">
                  <Bug className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Rezon</h1>
                  <p className="text-sm text-slate-400">Dashboard</p>
                </div>
              </Link>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/projects">
                <Button variant="ghost" className="text-white hover:bg-slate-800">
                  Projects
                </Button>
              </Link>
              <Link href="/scan">
                <Button className="bg-red-600 hover:bg-red-700">New Scan</Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Total Projects</CardTitle>
              <Shield className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats?.totalProjects}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Total Scans</CardTitle>
              <Activity className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats?.totalScans}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Secrets Found</CardTitle>
              <FileText className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{stats?.totalSecrets}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Critical Issues</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-400">{stats?.criticalSecrets}</div>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Secrets by Type */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Top Secret Types</CardTitle>
              <CardDescription className="text-slate-400">Most commonly found secret types</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  count: {
                    label: "Count",
                    color: "hsl(var(--chart-1))",
                  },
                }}
                className="h-[300px]"
              >
                <BarChart data={stats?.secretsByType}>
                  <XAxis dataKey="type" tick={{ fontSize: 12 }} angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="count" fill="#ef4444" />
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>

          {/* Severity Distribution */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Severity Distribution</CardTitle>
              <CardDescription className="text-slate-400">Breakdown of secrets by severity level</CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer
                config={{
                  count: {
                    label: "Count",
                    color: "hsl(var(--chart-1))",
                  },
                }}
                className="h-[300px]"
              >
                <PieChart>
                  <Pie
                    data={stats?.severityDistribution}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="count"
                    nameKey="severity"
                  >
                    {stats?.severityDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <ChartTooltip content={<ChartTooltipContent />} />
                </PieChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </div>

        {/* Recent Scans */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Recent Scans</CardTitle>
            <CardDescription className="text-slate-400">Latest scanning activity</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {stats?.recentScans.map((scan) => (
                <div key={scan.id} className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <div>
                      <p className="text-white font-medium">{scan.projects?.name || "Unknown Project"}</p>
                      <p className="text-sm text-slate-400">{scan.url || scan.filename || "Code scan"}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={scan.status === "completed" ? "default" : "secondary"}>{scan.status}</Badge>
                    <Badge variant="outline" className="text-yellow-400 border-yellow-400">
                      {scan.total_secrets} secrets
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
