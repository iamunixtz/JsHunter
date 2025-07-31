"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { Bug, Upload, Globe, FileText, Zap, AlertTriangle, CheckCircle, XCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { JSScanner, type ScanResult } from "@/lib/scanner"
import { supabase, type Project, isSupabaseConfigured } from "@/lib/supabase"
import Link from "next/link"

export default function ScanPage() {
  const searchParams = useSearchParams()
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedProject, setSelectedProject] = useState<string>("")
  const [url, setUrl] = useState(searchParams.get("url") || "")
  const [jsCode, setJsCode] = useState(searchParams.get("code") || "")
  const [file, setFile] = useState<File | null>(null)
  const [scanning, setScanning] = useState(false)
  const [scanResults, setScanResults] = useState<ScanResult[]>([])
  const [scanProgress, setScanProgress] = useState(0)
  const [beautifiedCode, setBeautifiedCode] = useState("")
  const [decodedCode, setDecodedCode] = useState("")

  useEffect(() => {
    fetchProjects()
    const projectId = searchParams.get("project")
    if (projectId) {
      setSelectedProject(projectId)
    }
  }, [searchParams])

  const fetchProjects = async () => {
    try {
      const { data, error } = await supabase.from("projects").select("*").order("name")

      if (error) throw error
      setProjects(data || [])
    } catch (error) {
      console.error("Error fetching projects:", error)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      const reader = new FileReader()
      reader.onload = (e) => {
        const content = e.target?.result as string
        setJsCode(content)
      }
      reader.readAsText(selectedFile)
    }
  }

  const beautifyCode = () => {
    if (jsCode) {
      const beautified = JSScanner.beautifyJS(jsCode)
      setBeautifiedCode(beautified)
    }
  }

  const decodeCode = () => {
    if (jsCode) {
      const decoded = JSScanner.decodeJS(jsCode)
      setDecodedCode(decoded)
    }
  }

  const performScan = async () => {
    setScanning(true)
    setScanProgress(0)
    setScanResults([])

    try {
      let codeToScan = jsCode
      let scanType: "url" | "file" = "file"
      let filename = file?.name
      let fileSize = file?.size

      // If URL is provided, fetch the code
      if (url && !jsCode) {
        setScanProgress(20)
        codeToScan = await JSScanner.fetchJSFromURL(url)
        scanType = "url"
        filename = undefined
        fileSize = undefined
      }

      if (!codeToScan) {
        throw new Error("No code to scan")
      }

      setScanProgress(40)

      let scanData = null

      // Only create scan record if Supabase is configured and project is selected
      if (isSupabaseConfigured && selectedProject) {
        const { data, error: scanError } = await supabase
          .from("scans")
          .insert([
            {
              project_id: selectedProject,
              url: url || undefined,
              filename,
              file_size: fileSize,
              scan_type: scanType,
              status: "pending",
            },
          ])
          .select()
          .single()

        if (scanError) {
          console.warn("Failed to create scan record:", scanError)
        } else {
          scanData = data
        }
      }

      setScanProgress(60)

      // Perform the actual scan
      const results = await JSScanner.scanCode(codeToScan)
      setScanResults(results)

      setScanProgress(80)

      // Save results to database if possible
      if (scanData) {
        await JSScanner.saveScanResults(scanData.id, results)
      }

      setScanProgress(100)
    } catch (error) {
      console.error("Scan error:", error)
      alert(`Scan failed: ${error}`)
    } finally {
      setScanning(false)
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

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <XCircle className="w-4 h-4" />
      case "high":
        return <AlertTriangle className="w-4 h-4" />
      case "medium":
        return <AlertTriangle className="w-4 h-4" />
      case "low":
        return <CheckCircle className="w-4 h-4" />
      default:
        return <AlertTriangle className="w-4 h-4" />
    }
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
                  <p className="text-sm text-slate-400">Secret Scanner</p>
                </div>
              </Link>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/dashboard">
                <Button variant="ghost" className="text-white hover:bg-slate-800">
                  Dashboard
                </Button>
              </Link>
              <Link href="/projects">
                <Button variant="ghost" className="text-white hover:bg-slate-800">
                  Projects
                </Button>
              </Link>
            </nav>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">JavaScript Secret Scanner</h2>
            <p className="text-slate-400">Scan JavaScript files for API keys, tokens, and sensitive data</p>
          </div>

          {/* Project Selection */}
          {!isSupabaseConfigured && (
            <Card className="bg-yellow-900/20 border-yellow-600/50 mb-6">
              <CardHeader>
                <CardTitle className="text-yellow-400 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Database Not Configured
                </CardTitle>
                <CardDescription className="text-yellow-300">
                  Supabase is not configured. Scans will work but results won't be saved. Add NEXT_PUBLIC_SUPABASE_URL
                  and NEXT_PUBLIC_SUPABASE_ANON_KEY environment variables to enable data persistence.
                </CardDescription>
              </CardHeader>
            </Card>
          )}

          {/* Project Selection - only show if Supabase is configured */}
          {isSupabaseConfigured && (
            <Card className="bg-slate-800/50 border-slate-700 mb-6">
              <CardHeader>
                <CardTitle className="text-white">Select Project</CardTitle>
                <CardDescription className="text-slate-400">
                  Choose a project to organize your scan results
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Select value={selectedProject} onValueChange={setSelectedProject}>
                  <SelectTrigger className="bg-slate-700 border-slate-600 text-white">
                    <SelectValue placeholder="Select a project" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-700 border-slate-600">
                    {projects.map((project) => (
                      <SelectItem key={project.id} value={project.id} className="text-white">
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          )}

          {/* Scan Interface */}
          <Card className="bg-slate-800/50 border-slate-700 mb-6">
            <CardHeader>
              <CardTitle className="text-white">Scan Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="url" className="w-full">
                <TabsList className="grid w-full grid-cols-3 bg-slate-700">
                  <TabsTrigger value="url" className="data-[state=active]:bg-slate-600">
                    <Globe className="w-4 h-4 mr-2" />
                    URL Scan
                  </TabsTrigger>
                  <TabsTrigger value="file" className="data-[state=active]:bg-slate-600">
                    <Upload className="w-4 h-4 mr-2" />
                    File Upload
                  </TabsTrigger>
                  <TabsTrigger value="code" className="data-[state=active]:bg-slate-600">
                    <FileText className="w-4 h-4 mr-2" />
                    Code Input
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="url" className="space-y-4">
                  <Input
                    placeholder="https://example.com/script.js"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400"
                  />
                </TabsContent>

                <TabsContent value="file" className="space-y-4">
                  <div className="border-2 border-dashed border-slate-600 rounded-lg p-8 text-center">
                    <Upload className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                    <input
                      type="file"
                      accept=".js,.jsx,.ts,.tsx"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload" className="cursor-pointer">
                      <Button variant="outline" className="mb-2 bg-transparent">
                        Choose JavaScript File
                      </Button>
                    </label>
                    <p className="text-sm text-slate-400">{file ? file.name : "Select a JavaScript file to scan"}</p>
                  </div>
                </TabsContent>

                <TabsContent value="code" className="space-y-4">
                  <Textarea
                    placeholder="Paste your JavaScript code here..."
                    value={jsCode}
                    onChange={(e) => setJsCode(e.target.value)}
                    className="min-h-[300px] bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 font-mono"
                  />
                  <div className="flex gap-2">
                    <Button onClick={beautifyCode} variant="outline">
                      Beautify Code
                    </Button>
                    <Button onClick={decodeCode} variant="outline">
                      Decode Code
                    </Button>
                  </div>
                </TabsContent>
              </Tabs>

              {scanning && (
                <div className="mt-6">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-4 h-4 text-yellow-400 animate-pulse" />
                    <span className="text-white">Scanning in progress...</span>
                  </div>
                  <Progress value={scanProgress} className="w-full" />
                </div>
              )}

              <Button
                onClick={performScan}
                disabled={scanning || (isSupabaseConfigured && !selectedProject) || (!url && !jsCode)}
                className="bg-red-600 hover:bg-red-700 disabled:opacity-50"
              >
                <Zap className="w-4 h-4 mr-2" />
                {scanning ? "Scanning..." : "Start Scan"}
              </Button>
            </CardContent>
          </Card>

          {/* Beautified/Decoded Code Display */}
          {(beautifiedCode || decodedCode) && (
            <Card className="bg-slate-800/50 border-slate-700 mb-6">
              <CardHeader>
                <CardTitle className="text-white">Processed Code</CardTitle>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue={beautifiedCode ? "beautified" : "decoded"}>
                  <TabsList className="bg-slate-700">
                    {beautifiedCode && (
                      <TabsTrigger value="beautified" className="data-[state=active]:bg-slate-600">
                        Beautified
                      </TabsTrigger>
                    )}
                    {decodedCode && (
                      <TabsTrigger value="decoded" className="data-[state=active]:bg-slate-600">
                        Decoded
                      </TabsTrigger>
                    )}
                  </TabsList>
                  {beautifiedCode && (
                    <TabsContent value="beautified">
                      <Textarea
                        value={beautifiedCode}
                        readOnly
                        className="min-h-[300px] bg-slate-700 border-slate-600 text-white font-mono text-sm"
                      />
                    </TabsContent>
                  )}
                  {decodedCode && (
                    <TabsContent value="decoded">
                      <Textarea
                        value={decodedCode}
                        readOnly
                        className="min-h-[300px] bg-slate-700 border-slate-600 text-white font-mono text-sm"
                      />
                    </TabsContent>
                  )}
                </Tabs>
              </CardContent>
            </Card>
          )}

          {/* Scan Results */}
          {scanResults.length > 0 && (
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                  Scan Results ({scanResults.length} secrets found)
                </CardTitle>
                <CardDescription className="text-slate-400">Detected secrets and sensitive information</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {scanResults.map((result, index) => (
                    <div key={index} className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {getSeverityIcon(result.severity)}
                          <h4 className="font-semibold text-white">{result.secretType}</h4>
                        </div>
                        <Badge className={`${getSeverityColor(result.severity)} text-white`}>
                          {result.severity.toUpperCase()}
                        </Badge>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <p className="text-sm text-slate-400 mb-1">Secret Value:</p>
                          <code className="text-sm bg-slate-800 px-2 py-1 rounded text-red-300 break-all">
                            {result.secretValue}
                          </code>
                        </div>

                        <div>
                          <p className="text-sm text-slate-400 mb-1">Line {result.lineNumber}:</p>
                          <pre className="text-sm bg-slate-800 p-2 rounded text-slate-300 overflow-x-auto">
                            {result.context}
                          </pre>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {scanResults.length === 0 && !scanning && (url || jsCode) && (
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="text-center py-12">
                <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">No Secrets Found</h3>
                <p className="text-slate-400">The scan completed successfully with no sensitive data detected.</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
