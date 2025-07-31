"use client"

import { useState } from "react"
import { Bug, Shield, Zap, Target, FileText, Globe, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

export default function HomePage() {
  const [url, setUrl] = useState("")
  const [jsCode, setJsCode] = useState("")

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-10 h-10 bg-red-600 rounded-lg">
                <Bug className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">Rezon</h1>
                <p className="text-sm text-slate-400">JavaScript Secret Scanner</p>
              </div>
            </div>
            <nav className="flex items-center gap-4">
              <Link href="/dashboard">
                <Button variant="ghost" className="text-white hover:bg-slate-800">
                  <BarChart3 className="w-4 h-4 mr-2" />
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

      {/* Hero Section */}
      <section className="py-20">
        <div className="container mx-auto px-4 text-center">
          <div className="flex justify-center mb-6">
            <div className="flex items-center justify-center w-20 h-20 bg-red-600/20 rounded-full border border-red-600/30">
              <Shield className="w-10 h-10 text-red-400" />
            </div>
          </div>
          <h2 className="text-5xl font-bold text-white mb-6">Hunt Secrets in JavaScript</h2>
          <p className="text-xl text-slate-300 mb-8 max-w-2xl mx-auto">
            Advanced JavaScript secret scanner for bug hunters. Detect API keys, tokens, and sensitive data in JS files
            with precision.
          </p>

          {/* Quick Scan Interface */}
          <Card className="max-w-4xl mx-auto bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-red-400" />
                Quick Scan
              </CardTitle>
              <CardDescription className="text-slate-400">
                Scan JavaScript files for secrets and API keys
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="url" className="w-full">
                <TabsList className="grid w-full grid-cols-2 bg-slate-700">
                  <TabsTrigger value="url" className="data-[state=active]:bg-slate-600">
                    <Globe className="w-4 h-4 mr-2" />
                    URL Scan
                  </TabsTrigger>
                  <TabsTrigger value="code" className="data-[state=active]:bg-slate-600">
                    <FileText className="w-4 h-4 mr-2" />
                    Code Scan
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="url" className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      placeholder="https://example.com/script.js"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400"
                    />
                    <Link href={`/scan?url=${encodeURIComponent(url)}`}>
                      <Button className="bg-red-600 hover:bg-red-700">
                        <Zap className="w-4 h-4 mr-2" />
                        Scan URL
                      </Button>
                    </Link>
                  </div>
                </TabsContent>

                <TabsContent value="code" className="space-y-4">
                  <Textarea
                    placeholder="Paste your JavaScript code here..."
                    value={jsCode}
                    onChange={(e) => setJsCode(e.target.value)}
                    className="min-h-[200px] bg-slate-700 border-slate-600 text-white placeholder:text-slate-400 font-mono"
                  />
                  <Link href={`/scan?code=${encodeURIComponent(jsCode)}`}>
                    <Button className="bg-red-600 hover:bg-red-700">
                      <Zap className="w-4 h-4 mr-2" />
                      Scan Code
                    </Button>
                  </Link>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 bg-slate-800/30">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-white text-center mb-12">Advanced Bug Hunting Features</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <div className="w-12 h-12 bg-red-600/20 rounded-lg flex items-center justify-center mb-4">
                  <Bug className="w-6 h-6 text-red-400" />
                </div>
                <CardTitle className="text-white">Secret Detection</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">
                  Detect 200+ types of secrets including AWS keys, GitHub tokens, API keys, and more with advanced regex
                  patterns.
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  <Badge variant="secondary">AWS</Badge>
                  <Badge variant="secondary">GitHub</Badge>
                  <Badge variant="secondary">Google</Badge>
                  <Badge variant="secondary">Stripe</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-600/20 rounded-lg flex items-center justify-center mb-4">
                  <FileText className="w-6 h-6 text-blue-400" />
                </div>
                <CardTitle className="text-white">JS Processing</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">
                  Beautify, decode, and analyze obfuscated JavaScript code. Support for URL encoding, base64, and more.
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  <Badge variant="secondary">Beautify</Badge>
                  <Badge variant="secondary">Decode</Badge>
                  <Badge variant="secondary">Deobfuscate</Badge>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <div className="w-12 h-12 bg-green-600/20 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-green-400" />
                </div>
                <CardTitle className="text-white">Analytics & Reports</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-slate-400">
                  Track findings across projects, generate reports, and maintain historical data for comprehensive
                  analysis.
                </p>
                <div className="flex flex-wrap gap-2 mt-4">
                  <Badge variant="secondary">Projects</Badge>
                  <Badge variant="secondary">History</Badge>
                  <Badge variant="secondary">Reports</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-slate-800">
        <div className="container mx-auto px-4 text-center">
          <p className="text-slate-400">Built for bug hunters and security researchers</p>
        </div>
      </footer>
    </div>
  )
}
