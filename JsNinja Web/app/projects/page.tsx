"use client"

import { useEffect, useState } from "react"
import { Bug, Plus, FolderOpen, Calendar, Target, Trash2, Edit } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { supabase, type Project } from "@/lib/supabase"
import Link from "next/link"

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [newProject, setNewProject] = useState({ name: "", description: "" })

  useEffect(() => {
    fetchProjects()
  }, [])

  const fetchProjects = async () => {
    try {
      const { data, error } = await supabase
        .from("projects")
        .select(`
          *,
          scans(count)
        `)
        .order("created_at", { ascending: false })

      if (error) throw error
      setProjects(data || [])
    } catch (error) {
      console.error("Error fetching projects:", error)
    } finally {
      setLoading(false)
    }
  }

  const createProject = async () => {
    if (!newProject.name.trim()) return

    try {
      const { data, error } = await supabase
        .from("projects")
        .insert([
          {
            name: newProject.name,
            description: newProject.description,
          },
        ])
        .select()
        .single()

      if (error) throw error

      setProjects([data, ...projects])
      setNewProject({ name: "", description: "" })
      setShowCreateDialog(false)
    } catch (error) {
      console.error("Error creating project:", error)
    }
  }

  const deleteProject = async (projectId: string) => {
    if (!confirm("Are you sure you want to delete this project? This will also delete all associated scans.")) {
      return
    }

    try {
      const { error } = await supabase.from("projects").delete().eq("id", projectId)

      if (error) throw error

      setProjects(projects.filter((p) => p.id !== projectId))
    } catch (error) {
      console.error("Error deleting project:", error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
        <div className="container mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-slate-700 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="h-48 bg-slate-700 rounded"></div>
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
                  <p className="text-sm text-slate-400">Projects</p>
                </div>
              </Link>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/dashboard">
                <Button variant="ghost" className="text-white hover:bg-slate-800">
                  Dashboard
                </Button>
              </Link>
              <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                <DialogTrigger asChild>
                  <Button className="bg-red-600 hover:bg-red-700">
                    <Plus className="w-4 h-4 mr-2" />
                    New Project
                  </Button>
                </DialogTrigger>
                <DialogContent className="bg-slate-800 border-slate-700">
                  <DialogHeader>
                    <DialogTitle className="text-white">Create New Project</DialogTitle>
                    <DialogDescription className="text-slate-400">
                      Create a new project to organize your scans
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-4">
                    <div>
                      <Input
                        placeholder="Project name"
                        value={newProject.name}
                        onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>
                    <div>
                      <Textarea
                        placeholder="Project description (optional)"
                        value={newProject.description}
                        onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                        className="bg-slate-700 border-slate-600 text-white"
                      />
                    </div>
                  </div>
                  <DialogFooter>
                    <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                      Cancel
                    </Button>
                    <Button onClick={createProject} className="bg-red-600 hover:bg-red-700">
                      Create Project
                    </Button>
                  </DialogFooter>
                </DialogContent>
              </Dialog>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-white mb-2">Your Projects</h2>
          <p className="text-slate-400">Organize and manage your security scans</p>
        </div>

        {projects.length === 0 ? (
          <Card className="bg-slate-800/50 border-slate-700 text-center py-12">
            <CardContent>
              <FolderOpen className="w-16 h-16 text-slate-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No Projects Yet</h3>
              <p className="text-slate-400 mb-6">Create your first project to start organizing your scans</p>
              <Button onClick={() => setShowCreateDialog(true)} className="bg-red-600 hover:bg-red-700">
                <Plus className="w-4 h-4 mr-2" />
                Create First Project
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Card
                key={project.id}
                className="bg-slate-800/50 border-slate-700 hover:bg-slate-800/70 transition-colors"
              >
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className="w-10 h-10 bg-red-600/20 rounded-lg flex items-center justify-center">
                        <Target className="w-5 h-5 text-red-400" />
                      </div>
                      <div>
                        <CardTitle className="text-white">{project.name}</CardTitle>
                        <CardDescription className="text-slate-400">
                          {project.description || "No description"}
                        </CardDescription>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteProject(project.id)}
                      className="text-slate-400 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2 text-sm text-slate-400">
                      <Calendar className="w-4 h-4" />
                      {new Date(project.created_at).toLocaleDateString()}
                    </div>
                    <Badge variant="outline" className="text-slate-300">
                      0 scans
                    </Badge>
                  </div>
                  <div className="flex gap-2">
                    <Link href={`/scan?project=${project.id}`} className="flex-1">
                      <Button className="w-full bg-red-600 hover:bg-red-700">New Scan</Button>
                    </Link>
                    <Link href={`/projects/${project.id}`}>
                      <Button variant="outline" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
