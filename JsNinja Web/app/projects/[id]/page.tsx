"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Bug, Calendar, Globe, FileText, AlertTriangle, TrendingUp, Activity } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { Bar, BarChart, XAxis, YAxis } from "recharts"
import { supabase, type Project, type Scan, type Secret } from "@/lib/supabase"
import Link from "next/link"

interface ProjectDetails extends Project {
  scans: (Scan & { secrets: Secret[] })[]
}

export default function ProjectDetailPage() {
  const params = useParams()
  const projectId = params.id as string
  const [project, setProject] = useState<ProjectDetails | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (projectId) {
      fetchProjectDetails()
    }
  }, [projectId])

  const fetchProjectDetails = async () => {
    try {
      const { data: projectData, error: projectError } = await supabase
        .from("projects")
        .select("*")
        .eq("id", projectId)
        .single()

      if (projectError) throw projectError

      const { data: scansData, error: scansError } = await supabase
        .from("scans")
        .select(`
          *,
          secrets(*)
        `)
        .eq("project_id", projectId)
        .order("created_at", { ascending: false })

      if (scansError) throw scansError

      setProject({
        ...projectData,
        scans: scansData || [],
      })
    } catch (error) {
      console.error("Error fetching project details:", error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-600"
      case "high":
        return "bg-orange-600"
      case "medium":
        return "bg-yellow-600"
      case "low":
        return "bg-green-600"
      default:
        return "bg-gray-600"
    }
  }

  const getSecretTypeStats = () => {
    const stats: Record<string, number> = {}
    project?.scans.forEach((scan) => {
      scan.secrets.forEach((secret) => {
        stats[secret.secret_type] = (stats[secret.secret_type] || 0) + 1
      })
    })
    return Object.entries(stats)
      .map(([type, count]) => ({ type, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="container mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-slate-700 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-32 bg-slate-700 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!project) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="text-center py-12">
            <h3 className="text-xl font-semibold text-white mb-2">Project Not Found</h3>
            <p className="text-slate-400 mb-6">The requested project could not be found.</p>
            <Link href="/projects">
              <Button className="bg-red-600 hover:bg-red-700">Back to Projects</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const totalSecrets = project.scans.reduce((sum, scan) => sum + scan.secrets.length, 0)
  const criticalSecrets = project.scans.reduce(
    (sum, scan) => sum + scan.secrets.filter((s) => s.severity === "critical").length,
    0,
  )

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
                  <p className="text-sm text-slate-400">{project.name}</p>
                </div>
              </Link>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/projects">
                <Button variant="ghost" className="text-white hover:bg-slate-800">
                  All Projects
                </Button>
              </Link>
              <Link href={`/scan?project=${project.id}`}>
                <Button className="bg-red-600 hover:bg-red-700">New Scan</Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Project Info */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">{project.name}</h2>
          <p className="text-slate-400 mb-4">{project.description || "No description provided"}</p>
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <div className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              Created {new Date(project.created_at).toLocaleDateString()}
            </div>
            <Badge variant="outline" className="text-slate-300">
              {project.scans.length} scans
            </Badge>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Total Scans</CardTitle>
              <Activity className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{project.scans.length}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Secrets Found</CardTitle>
              <FileText className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">{totalSecrets}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Critical Issues</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-400">{criticalSecrets}</div>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-400">Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">
                {project.scans.length > 0
                  ? Math.round(
                      (project.scans.filter((s) => s.status === "completed").length / project.scans.length) * 100,
                    )
                  : 0}
                %
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Secret Types Chart */}
        {totalSecrets > 0 && (
          <Card className="bg-slate-800/50 border-slate-700 mb-8">
            <CardHeader>
              <CardTitle className="text-white">Secret Types Distribution</CardTitle>
              <CardDescription className="text-slate-400">
                Most commonly found secret types in this project
              </CardDescription>
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
                <BarChart data={getSecretTypeStats()}>
                  <XAxis dataKey="type" tick={{ fontSize: 12 }} angle={-45} textAnchor="end" height={100} />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="count" fill="#ef4444" />
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>
        )}

        {/* Recent Scans */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white">Scan History</CardTitle>
            <CardDescription className="text-slate-400">All scans performed in this project</CardDescription>
          </CardHeader>
          <CardContent>
            {project.scans.length === 0 ? (
              <div className="text-center py-12">
                <Activity className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No Scans Yet</h3>
                <p className="text-slate-400 mb-6">Start your first scan to see results here</p>
                <Link href={`/scan?project=${project.id}`}>
                  <Button className="bg-red-600 hover:bg-red-700">Start First Scan</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {project.scans.map((scan) => (
                  <div key={scan.id} className="flex items-center justify-between p-4 bg-slate-700/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          scan.status === "completed"
                            ? "bg-green-400"
                            : scan.status === "failed"
                              ? "bg-red-400"
                              : "bg-yellow-400"
                        }`}
                      ></div>
                      <div>
                        <div className="flex items-center gap-2">
                          {scan.scan_type === "url" ? (
                            <Globe className="w-4 h-4 text-slate-400" />
                          ) : (
                            <FileText className="w-4 h-4 text-slate-400" />
                          )}
                          <p className="text-white font-medium">{scan.url || scan.filename || "Code scan"}</p>
                        </div>
                        <p className="text-sm text-slate-400">{new Date(scan.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={scan.status === "completed" ? "default" : "secondary"}>{scan.status}</Badge>
                      <Badge variant="outline" className="text-yellow-400 border-yellow-400">
                        {scan.secrets.length} secrets
                      </Badge>
                      {scan.secrets.filter((s) => s.severity === "critical").length > 0 && (
                        <Badge className="bg-red-600 text-white">
                          {scan.secrets.filter((s) => s.severity === "critical").length} critical
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
