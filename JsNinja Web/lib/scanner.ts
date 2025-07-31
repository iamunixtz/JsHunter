import { SECRET_PATTERNS, SEVERITY_MAP } from "./secret-patterns"
import { supabase, isSupabaseConfigured } from "./supabase"
import * as js_beautify from "js-beautify"

export interface ScanResult {
  secretType: string
  secretValue: string
  lineNumber: number
  context: string
  severity: "low" | "medium" | "high" | "critical"
}

export class JSScanner {
  static beautifyJS(code: string): string {
    try {
      return js_beautify.js(code, {
        indent_size: 2,
        space_in_empty_paren: true,
        preserve_newlines: true,
        max_preserve_newlines: 2,
        jslint_happy: false,
        space_after_anon_function: true,
        brace_style: "collapse",
        keep_array_indentation: false,
        keep_function_indentation: false,
        space_before_conditional: true,
        break_chained_methods: false,
        eval_code: false,
        unescape_strings: false,
        wrap_line_length: 0,
        wrap_attributes: "auto",
        wrap_attributes_indent_size: 4,
        end_with_newline: false,
      })
    } catch (error) {
      console.error("Error beautifying JS:", error)
      return code
    }
  }

  static decodeJS(code: string): string {
    try {
      // Decode URL encoded strings
      let decoded = decodeURIComponent(code)

      // Decode HTML entities
      decoded = decoded
        .replace(/&quot;/g, '"')
        .replace(/&#x27;/g, "'")
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">")
        .replace(/&amp;/g, "&")

      // Decode base64 strings (basic detection)
      const base64Regex = /['"]([A-Za-z0-9+/]{4,}={0,2})['"]?/g
      decoded = decoded.replace(base64Regex, (match, base64) => {
        try {
          if (base64.length % 4 === 0 && /^[A-Za-z0-9+/]*={0,2}$/.test(base64)) {
            const decodedBase64 = atob(base64)
            if (decodedBase64.length > 0 && /^[\x20-\x7E]*$/.test(decodedBase64)) {
              return `"${decodedBase64}" /* base64 decoded */`
            }
          }
        } catch (e) {
          // Not valid base64, return original
        }
        return match
      })

      return decoded
    } catch (error) {
      console.error("Error decoding JS:", error)
      return code
    }
  }

  static async scanCode(code: string): Promise<ScanResult[]> {
    const results: ScanResult[] = []
    const lines = code.split("\n")

    for (const [patternName, pattern] of Object.entries(SECRET_PATTERNS)) {
      // Reset regex lastIndex to avoid issues with global flag
      pattern.lastIndex = 0

      let match
      while ((match = pattern.exec(code)) !== null) {
        const secretValue = match[1]
        if (!secretValue || secretValue.length < 8) continue

        // Find line number
        const beforeMatch = code.substring(0, match.index)
        const lineNumber = beforeMatch.split("\n").length

        // Get context (surrounding lines)
        const contextStart = Math.max(0, lineNumber - 2)
        const contextEnd = Math.min(lines.length, lineNumber + 1)
        const context = lines.slice(contextStart, contextEnd).join("\n")

        results.push({
          secretType: patternName,
          secretValue,
          lineNumber,
          context,
          severity: SEVERITY_MAP[patternName] || "medium",
        })
      }
    }

    return results
  }

  static async fetchJSFromURL(url: string): Promise<string> {
    try {
      const response = await fetch(url)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const contentType = response.headers.get("content-type")
      if (!contentType?.includes("javascript") && !contentType?.includes("text")) {
        console.warn("URL may not contain JavaScript content")
      }
      return await response.text()
    } catch (error) {
      throw new Error(`Failed to fetch JS from URL: ${error}`)
    }
  }

  static async saveScanResults(scanId: string, results: ScanResult[]): Promise<void> {
    if (!isSupabaseConfigured) {
      console.warn("Supabase not configured - scan results will not be saved")
      return
    }

    try {
      const secretsData = results.map((result) => ({
        scan_id: scanId,
        secret_type: result.secretType,
        secret_value: result.secretValue,
        line_number: result.lineNumber,
        context: result.context,
        severity: result.severity,
      }))

      if (secretsData.length > 0) {
        const { error } = await supabase.from("secrets").insert(secretsData)

        if (error) {
          throw new Error(`Failed to save scan results: ${error.message}`)
        }
      }

      // Update scan with total secrets count
      const { error: updateError } = await supabase
        .from("scans")
        .update({
          total_secrets: results.length,
          status: "completed",
          completed_at: new Date().toISOString(),
        })
        .eq("id", scanId)

      if (updateError) {
        throw new Error(`Failed to update scan: ${updateError.message}`)
      }
    } catch (error) {
      console.error("Error saving scan results:", error)
      // Don't throw error - allow scan to complete even if saving fails
    }
  }
}
