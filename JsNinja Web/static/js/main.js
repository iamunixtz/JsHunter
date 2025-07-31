// Main JavaScript file for JSNinja

// Import Bootstrap
const bootstrap = window.bootstrap

// Initialize tooltips
document.addEventListener("DOMContentLoaded", () => {
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
})

// Utility functions
function showAlert(message, type = "info") {
  const alertDiv = document.createElement("div")
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  const container = document.querySelector(".container")
  container.insertBefore(alertDiv, container.firstChild)

  // Auto dismiss after 5 seconds
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove()
    }
  }, 5000)
}

// Copy to clipboard function
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(
    () => {
      showAlert("Copied to clipboard!", "success")
    },
    (err) => {
      showAlert("Failed to copy to clipboard", "danger")
    },
  )
}

// Format file size
function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes"
  const k = 1024
  const sizes = ["Bytes", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString() + " " + date.toLocaleTimeString()
}

// Severity color mapping
const severityColors = {
  critical: "danger",
  high: "warning",
  medium: "info",
  low: "success",
}

// Get severity badge HTML
function getSeverityBadge(severity) {
  const color = severityColors[severity] || "secondary"
  return `<span class="badge bg-${color}">${severity.toUpperCase()}</span>`
}

// Debounce function
function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

// Loading spinner
function showLoading(element) {
  element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...'
  element.disabled = true
}

function hideLoading(element, originalText) {
  element.innerHTML = originalText
  element.disabled = false
}

// Export functions for global use
window.JSNinja = {
  showAlert,
  copyToClipboard,
  formatFileSize,
  formatDate,
  getSeverityBadge,
  debounce,
  showLoading,
  hideLoading,
}
