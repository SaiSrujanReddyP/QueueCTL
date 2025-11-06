"""
Web Dashboard for QueueCTL monitoring
"""

import json
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

from .job_queue import JobQueue
from .config import Config


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the dashboard"""
    
    def __init__(self, job_queue: JobQueue, config: Config, *args, **kwargs):
        self.job_queue = job_queue
        self.config = config
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self._serve_dashboard()
        elif path == '/api/status':
            self._serve_api_status()
        elif path == '/api/jobs':
            self._serve_api_jobs(parsed_path.query)
        elif path == '/api/metrics':
            self._serve_api_metrics(parsed_path.query)
        elif path.startswith('/static/'):
            self._serve_static(path)
        else:
            self._send_404()
    
    def _serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = self._get_dashboard_html()
        self._send_response(200, html, 'text/html')
    
    def _serve_api_status(self):
        """Serve system status API"""
        try:
            status = self.job_queue.get_status()
            metrics = self.job_queue.get_system_metrics(24)
            
            response = {
                'status': status,
                'metrics': metrics,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            self._send_json_response(response)
        except Exception as e:
            self._send_error_response(str(e))
    
    def _serve_api_jobs(self, query_string: str):
        """Serve jobs API with filtering"""
        try:
            params = parse_qs(query_string)
            state = params.get('state', [None])[0]
            limit = int(params.get('limit', [100])[0])
            
            jobs = self.job_queue.list_jobs(state)[:limit]
            
            # Add metrics for each job
            for job in jobs:
                job['metrics'] = self.job_queue.get_job_metrics(job['id'])
            
            self._send_json_response({'jobs': jobs})
        except Exception as e:
            self._send_error_response(str(e))
    
    def _serve_api_metrics(self, query_string: str):
        """Serve metrics API"""
        try:
            params = parse_qs(query_string)
            hours = int(params.get('hours', [24])[0])
            
            metrics = self.job_queue.get_system_metrics(hours)
            self._send_json_response(metrics)
        except Exception as e:
            self._send_error_response(str(e))
    
    def _serve_static(self, path: str):
        """Serve static files (CSS, JS)"""
        if path == '/static/style.css':
            css = self._get_dashboard_css()
            self._send_response(200, css, 'text/css')
        elif path == '/static/script.js':
            js = self._get_dashboard_js()
            self._send_response(200, js, 'application/javascript')
        else:
            self._send_404()
    
    def _send_response(self, status_code: int, content: str, content_type: str):
        """Send HTTP response"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))
    
    def _send_json_response(self, data: Dict[str, Any]):
        """Send JSON response"""
        json_data = json.dumps(data, indent=2)
        self._send_response(200, json_data, 'application/json')
    
    def _send_error_response(self, error: str):
        """Send error response"""
        response = {'error': error}
        self._send_json_response(response)
    
    def _send_404(self):
        """Send 404 response"""
        self._send_response(404, 'Not Found', 'text/plain')
    
    def log_message(self, format, *args):
        """Override to suppress request logging"""
        pass
    
    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QueueCTL Dashboard</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <header>
        <h1>QueueCTL Dashboard</h1>
        <div class="version">v1.0.0</div>
    </header>
    
    <main>
        <section class="metrics-grid">
            <div class="metric-card">
                <h3>System Status</h3>
                <div id="system-status">Loading...</div>
            </div>
            
            <div class="metric-card">
                <h3>Job Counts</h3>
                <div id="job-counts">Loading...</div>
            </div>
            
            <div class="metric-card">
                <h3>Performance</h3>
                <div id="performance-metrics">Loading...</div>
            </div>
            
            <div class="metric-card">
                <h3>Success Rate</h3>
                <div id="success-rate">Loading...</div>
            </div>
        </section>
        
        <section class="jobs-section">
            <div class="section-header">
                <h2>Recent Jobs</h2>
                <div class="filters">
                    <select id="state-filter">
                        <option value="">All States</option>
                        <option value="pending">Pending</option>
                        <option value="processing">Processing</option>
                        <option value="completed">Completed</option>
                        <option value="failed">Failed</option>
                        <option value="dead">Dead (DLQ)</option>
                        <option value="scheduled">Scheduled</option>
                    </select>
                    <button id="refresh-btn">Refresh</button>
                </div>
            </div>
            
            <div class="jobs-container">
                <table id="jobs-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Command</th>
                            <th>State</th>
                            <th>Priority</th>
                            <th>Attempts</th>
                            <th>Created</th>
                            <th>Duration</th>
                        </tr>
                    </thead>
                    <tbody id="jobs-tbody">
                        <tr><td colspan="7">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </section>
    </main>
    
    <script src="/static/script.js"></script>
</body>
</html>'''
    
    def _get_dashboard_css(self) -> str:
        """Generate dashboard CSS"""
        return '''
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #1a1a1a;
    color: #ffffff;
    line-height: 1.6;
}

header {
    background: #2d2d2d;
    padding: 1rem 2rem;
    border-bottom: 3px solid #bbfa01;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

header h1 {
    color: #bbfa01;
    font-size: 2rem;
}

.version {
    background: #bbfa01;
    color: #1a1a1a;
    padding: 0.25rem 0.75rem;
    border-radius: 15px;
    font-weight: bold;
    font-size: 0.9rem;
}

main {
    padding: 2rem;
    max-width: 1400px;
    margin: 0 auto;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: #2d2d2d;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #444;
    transition: transform 0.2s;
}

.metric-card:hover {
    transform: translateY(-2px);
    border-color: #bbfa01;
}

.metric-card h3 {
    color: #bbfa01;
    margin-bottom: 1rem;
    font-size: 1.1rem;
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 0.5rem;
}

.metric-label {
    color: #aaa;
    font-size: 0.9rem;
}

.jobs-section {
    background: #2d2d2d;
    border-radius: 8px;
    padding: 1.5rem;
    border: 1px solid #444;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.section-header h2 {
    color: #bbfa01;
}

.filters {
    display: flex;
    gap: 1rem;
    align-items: center;
}

select, button {
    background: #1a1a1a;
    color: #ffffff;
    border: 1px solid #555;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    font-size: 0.9rem;
}

button {
    background: #bbfa01;
    color: #1a1a1a;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.2s;
}

button:hover {
    background: #a8e600;
}

.jobs-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    text-align: left;
    padding: 0.75rem;
    border-bottom: 1px solid #444;
}

th {
    background: #1a1a1a;
    color: #bbfa01;
    font-weight: bold;
    position: sticky;
    top: 0;
}

tr:hover {
    background: #333;
}

.state-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: bold;
    text-transform: uppercase;
}

.state-pending { background: #ffa500; color: #000; }
.state-processing { background: #00bfff; color: #000; }
.state-completed { background: #32cd32; color: #000; }
.state-failed { background: #ff6b6b; color: #fff; }
.state-dead { background: #dc143c; color: #fff; }
.state-scheduled { background: #9370db; color: #fff; }

.priority-high { color: #ff6b6b; font-weight: bold; }
.priority-normal { color: #bbfa01; }
.priority-low { color: #aaa; }

@media (max-width: 768px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }
    
    .section-header {
        flex-direction: column;
        gap: 1rem;
        align-items: stretch;
    }
    
    .filters {
        justify-content: center;
    }
}
'''
    
    def _get_dashboard_js(self) -> str:
        """Generate dashboard JavaScript"""
        return '''
class QueueCTLDashboard {
    constructor() {
        this.init();
        this.startAutoRefresh();
    }
    
    init() {
        this.loadData();
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadData();
        });
        
        document.getElementById('state-filter').addEventListener('change', () => {
            this.loadJobs();
        });
    }
    
    startAutoRefresh() {
        setInterval(() => {
            this.loadData();
        }, 5000); // Refresh every 5 seconds
    }
    
    async loadData() {
        await Promise.all([
            this.loadStatus(),
            this.loadJobs()
        ]);
    }
    
    async loadStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            this.updateSystemStatus(data);
            this.updateJobCounts(data.status);
            this.updatePerformanceMetrics(data.metrics);
            this.updateSuccessRate(data.metrics);
        } catch (error) {
            console.error('Error loading status:', error);
        }
    }
    
    async loadJobs() {
        try {
            const stateFilter = document.getElementById('state-filter').value;
            const url = stateFilter ? `/api/jobs?state=${stateFilter}&limit=50` : '/api/jobs?limit=50';
            
            const response = await fetch(url);
            const data = await response.json();
            
            this.updateJobsTable(data.jobs);
        } catch (error) {
            console.error('Error loading jobs:', error);
        }
    }
    
    updateSystemStatus(data) {
        const statusEl = document.getElementById('system-status');
        const timestamp = new Date(data.timestamp).toLocaleString();
        
        statusEl.innerHTML = `
            <div class="metric-value">Online</div>
            <div class="metric-label">Last updated: ${timestamp}</div>
        `;
    }
    
    updateJobCounts(status) {
        const countsEl = document.getElementById('job-counts');
        
        const total = Object.values(status).reduce((sum, count) => sum + count, 0);
        
        countsEl.innerHTML = `
            <div class="metric-value">${total}</div>
            <div class="metric-label">Total Jobs</div>
            <div style="margin-top: 1rem; font-size: 0.9rem;">
                <div>Pending: ${status.pending || 0}</div>
                <div>Processing: ${status.processing || 0}</div>
                <div>Completed: ${status.completed || 0}</div>
                <div>Failed: ${status.failed || 0}</div>
                <div>Dead: ${status.dead || 0}</div>
            </div>
        `;
    }
    
    updatePerformanceMetrics(metrics) {
        const perfEl = document.getElementById('performance-metrics');
        
        const avgTime = Math.round(metrics.avg_execution_time_ms || 0);
        const jobsPerHour = Math.round(metrics.jobs_per_hour || 0);
        
        perfEl.innerHTML = `
            <div class="metric-value">${avgTime}ms</div>
            <div class="metric-label">Avg Execution Time</div>
            <div style="margin-top: 1rem; font-size: 0.9rem;">
                <div>Jobs/Hour: ${jobsPerHour}</div>
            </div>
        `;
    }
    
    updateSuccessRate(metrics) {
        const rateEl = document.getElementById('success-rate');
        
        const successRate = Math.round(metrics.success_rate_percent || 0);
        const color = successRate >= 90 ? '#32cd32' : successRate >= 70 ? '#ffa500' : '#ff6b6b';
        
        rateEl.innerHTML = `
            <div class="metric-value" style="color: ${color}">${successRate}%</div>
            <div class="metric-label">Success Rate (24h)</div>
        `;
    }
    
    updateJobsTable(jobs) {
        const tbody = document.getElementById('jobs-tbody');
        
        if (!jobs || jobs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7">No jobs found</td></tr>';
            return;
        }
        
        tbody.innerHTML = jobs.map(job => {
            const createdAt = new Date(job.created_at).toLocaleString();
            const duration = job.execution_time_ms ? `${job.execution_time_ms}ms` : '-';
            const command = job.command.length > 40 ? job.command.substring(0, 40) + '...' : job.command;
            
            let priorityClass = 'priority-normal';
            if (job.priority > 0) priorityClass = 'priority-high';
            else if (job.priority < 0) priorityClass = 'priority-low';
            
            return `
                <tr>
                    <td><code>${job.id}</code></td>
                    <td><code>${command}</code></td>
                    <td><span class="state-badge state-${job.state}">${job.state}</span></td>
                    <td class="${priorityClass}">${job.priority}</td>
                    <td>${job.attempts}/${job.max_retries}</td>
                    <td>${createdAt}</td>
                    <td>${duration}</td>
                </tr>
            `;
        }).join('');
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new QueueCTLDashboard();
});
'''


class WebDashboard:
    """Web dashboard server for QueueCTL"""
    
    def __init__(self, job_queue: JobQueue, config: Config, host: str = 'localhost', port: int = 8080):
        self.job_queue = job_queue
        self.config = config
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
    
    def start(self):
        """Start the web dashboard server"""
        def handler(*args, **kwargs):
            return DashboardHandler(self.job_queue, self.config, *args, **kwargs)
        
        self.server = HTTPServer((self.host, self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        
        print(f"Web dashboard started at http://{self.host}:{self.port}")
    
    def stop(self):
        """Stop the web dashboard server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=5)
        print("Web dashboard stopped")


def start_dashboard(job_queue: JobQueue, config: Config, host: str = 'localhost', port: int = 8080):
    """Start the web dashboard"""
    dashboard = WebDashboard(job_queue, config, host, port)
    dashboard.start()
    return dashboard