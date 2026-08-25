from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


# =============================================================================
# 👉 INTEGRATION POINT
# -----------------------------------------------------------------------------
# Replace the body of this function with a call into your actual program.
# Whatever string it returns gets shown on the page.
#
# Examples:
#   from my_module import analyze
#   return analyze(user_input)
#
#   import subprocess
#   proc = subprocess.run(["python3", "my_script.py", user_input],
#                          capture_output=True, text=True)
#   return proc.stdout
# =============================================================================


#!/usr/bin/env python3
import sys
import datetime
from jinja2 import Template

SERVICE_EXPLANATIONS = {
    21: {
        "severity": "CRITICAL", 
        "impact": "Backdoor Access", 
        "desc": "vsftpd 2.3.4 contains a famous backdoor. Typing a smiley face ':)' in the password grants instant root shell access."
    },
    22: {
        "severity": "MEDIUM", 
        "impact": "Remote Shell", 
        "desc": "SSH is open for remote login. Secure, but vulnerable to password brute-force attacks if weak credentials are used."
    },
    23: {
        "severity": "HIGH", 
        "impact": "Cleartext Traffic", 
        "desc": "Telnet sends all usernames and passwords across the network in plain text without encryption."
    },
    25: {
        "severity": "INFO", 
        "impact": "Mail Server", 
        "desc": "SMTP email service is running. Can be abused for email spoofing if misconfigured."
    },
    80: {
        "severity": "LOW", 
        "impact": "Unencrypted Web", 
        "desc": "Standard web server running over HTTP (no SSL/HTTPS). Traffic can be intercepted on local Wi-Fi."
    },
    139: {
        "severity": "MEDIUM", 
        "impact": "File Sharing", 
        "desc": "NetBIOS/SMB legacy file sharing enabled. Exposes host details to network enumeration."
    },
    445: {
        "severity": "HIGH", 
        "impact": "SMB Exploit Risk", 
        "desc": "Windows/Samba file sharing open. Highly targeted protocol used by worms like WannaCry and EternalBlue."
    },
    513: {
        "severity": "CRITICAL", 
        "impact": "No-Password Login", 
        "desc": "Legacy rlogin daemon allows remote users to log in directly without requiring a password."
    },
    3306: {
        "severity": "LOW", 
        "impact": "Exposed Database", 
        "desc": "MySQL database server is directly accessible from the network instead of local-only."
    },
    5900: {
        "severity": "MEDIUM", 
        "impact": "Remote Desktop", 
        "desc": "VNC graphical desktop sharing active. Allows remote screen control if weak passwords are set."
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Network Vulnerability Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 30px; }
        .container { max-width: 1050px; margin: 0 auto; background: #1e293b; padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; margin-top: 0; }
        .meta-info { margin-bottom: 20px; color: #94a3b8; font-size: 0.95em; }
        
        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 20px; }
        .metric-card { background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; text-align: center; }
        .metric-value { font-size: 1.8em; font-weight: bold; margin-top: 5px; }
        .color-hosts { color: #38bdf8; }
        .color-critical { color: #ef4444; }
        .color-high { color: #f97316; }
        .color-medium { color: #eab308; }

        .controls { display: flex; gap: 12px; margin-bottom: 25px; background: #0f172a; padding: 15px; border-radius: 8px; border: 1px solid #334155; align-items: center; flex-wrap: wrap; }
        .controls input, .controls select { background: #1e293b; color: #f8fafc; border: 1px solid #475569; padding: 8px 12px; border-radius: 6px; font-size: 0.95em; outline: none; }
        .controls input { flex-grow: 1; min-width: 200px; }
        .controls input:focus, .controls select:focus { border-color: #38bdf8; }

        .host-card { background: #0f172a; border-radius: 8px; padding: 15px; margin-bottom: 20px; border: 1px solid #334155; }
        .host-header { font-size: 1.2em; font-weight: bold; color: #f1f5f9; margin-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px 10px; text-align: left; border-bottom: 1px solid #334155; vertical-align: middle; }
        th { background-color: #334155; color: #f8fafc; font-size: 0.9em; }
        
        .badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; display: inline-block; }
        .badge-CRITICAL { background-color: #ef4444; color: #ffffff; }
        .badge-HIGH { background-color: #f97316; color: #ffffff; }
        .badge-MEDIUM { background-color: #eab308; color: #000000; }
        .badge-LOW { background-color: #3b82f6; color: #ffffff; }
        .badge-INFO { background-color: #64748b; color: #ffffff; }

        .impact-tag { background: #334155; color: #38bdf8; padding: 3px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; margin-bottom: 4px; display: inline-block; }

        @media print {
            .controls, .btn-export { display: none !important; }
            body { background-color: #ffffff !important; color: #000000 !important; padding: 0 !important; }
            .container, .host-card, .metric-card { background: #ffffff !important; color: #000000 !important; border: 1px solid #ccc !important; box-shadow: none !important; }
            h1, .host-header { color: #000000 !important; }
            th { background-color: #f1f5f9 !important; color: #000000 !important; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Network Vulnerability Assessment</h1>
        <div class="meta-info">
            <p><strong>Target Range:</strong> {{ target }} | <strong>Scan Date:</strong> {{ scan_time }}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div style="color: #94a3b8; font-size: 0.85em;">TOTAL HOSTS</div>
                <div class="metric-value color-hosts">{{ stats.total_hosts }}</div>
            </div>
            <div class="metric-card">
                <div style="color: #94a3b8; font-size: 0.85em;">CRITICAL RISKS</div>
                <div class="metric-value color-critical">{{ stats.critical }}</div>
            </div>
            <div class="metric-card">
                <div style="color: #94a3b8; font-size: 0.85em;">HIGH RISKS</div>
                <div class="metric-value color-high">{{ stats.high }}</div>
            </div>
            <div class="metric-card">
                <div style="color: #94a3b8; font-size: 0.85em;">MEDIUM / LOW</div>
                <div class="metric-value color-medium">{{ stats.medium_low }}</div>
            </div>
        </div>

        <div class="controls">
            <input type="text" id="searchInput" onkeyup="filterResults()" placeholder="Search by port, service, or impact...">
            <select id="severitySelect" onchange="filterResults()" style="width: 150px;">
                <option value="ALL">All Severities</option>
                <option value="CRITICAL">Critical</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
                <option value="INFO">Info</option>
            </select>
            <button class="btn-export" onclick="window.print()" style="background: #38bdf8; color: #0f172a; font-weight: bold; border: none; padding: 9px 16px; border-radius: 6px; cursor: pointer; white-space: nowrap;">
                Export PDF
            </button>
        </div>

        {% for host in hosts %}
        <div class="host-card">
            <div class="host-header">Host IP: {{ host.ip }} ({{ host.hostname or 'Target System' }}) - Status: {{ host.status }}</div>
            {% if host.ports %}
            <table class="scanTable">
                <thead>
                    <tr>
                        <th style="width: 12%;">Port</th>
                        <th style="width: 10%;">State</th>
                        <th style="width: 15%;">Service</th>
                        <th style="width: 20%;">Detected Version</th>
                        <th style="width: 33%;">Security Risk / Student Insight</th>
                        <th style="width: 10%;">Severity</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in host.ports %}
                    <tr class="data-row" data-severity="{{ p.severity }}">
                        <td><strong>{{ p.port }}/{{ p.proto }}</strong></td>
                        <td><span style="color: #4ade80;">{{ p.state }}</span></td>
                        <td>{{ p.service }}</td>
                        <td>{{ p.product }} {{ p.version }}</td>
                        <td>
                            <div class="impact-tag">{{ p.impact }}</div>
                            <div style="font-size: 0.88em; color: #cbd5e1; margin-top: 2px;">{{ p.desc }}</div>
                        </td>
                        <td><span class="badge badge-{{ p.severity }}">{{ p.severity }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% else %}
            <p style="color: #94a3b8;">No open ports detected on this host.</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <script>
        function filterResults() {
            const searchInput = document.getElementById('searchInput').value.toLowerCase();
            const selectedSeverity = document.getElementById('severitySelect').value;
            const rows = document.querySelectorAll('.data-row');

            rows.forEach(row => {
                const textContent = row.textContent.toLowerCase();
                const rowSeverity = row.getAttribute('data-severity');

                const matchesSearch = textContent.includes(searchInput);
                const matchesSeverity = (selectedSeverity === 'ALL') || (rowSeverity === selectedSeverity);

                if (matchesSearch && matchesSeverity) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }
    </script>
</body>
</html>
"""

def run_assessment(target_range):
    try:
        import nmap
    except ImportError:
        return run_socket_fallback(target_range)

    print(f"[*] Scanning {target_range} (Fast scan mode)...")

    try:
        scanner = nmap.PortScanner()
        scanner.scan(hosts=target_range, arguments='-sV -F')
    except (nmap.PortScannerError, FileNotFoundError, OSError):
        return run_socket_fallback(target_range)
    
    parsed_hosts = []
    
    for host in scanner.all_hosts():
        host_data = {
            "ip": host,
            "hostname": scanner[host].hostname(),
            "status": scanner[host].state(),
            "ports": []
        }
        
        for proto in scanner[host].all_protocols():
            ports = scanner[host][proto].keys()
            for port in sorted(ports):
                port_info = scanner[host][proto][port]
                port_num = int(port)
                
                info = SERVICE_EXPLANATIONS.get(port_num, {
                    "severity": "INFO",
                    "impact": "Standard Port",
                    "desc": f"Port {port_num} is open running {port_info['name']}."
                })
                
                host_data["ports"].append({
                    "port": port_num,
                    "proto": proto,
                    "state": port_info["state"],
                    "service": port_info["name"],
                    "product": port_info.get("product", ""),
                    "version": port_info.get("version", ""),
                    "severity": info["severity"],
                    "impact": info["impact"],
                    "desc": info["desc"]
                })
                
        parsed_hosts.append(host_data)
        
    return parsed_hosts


def run_socket_fallback(target):
    """Run a small TCP check when the host does not provide the nmap binary."""
    import socket

    common_ports = [21, 22, 23, 25, 80, 139, 443, 445, 513, 3306, 5900, 8080]
    host = target.split('/', 1)[0]
    open_ports = []

    for port in common_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(0.35)
            try:
                if connection.connect_ex((host, port)) == 0:
                    info = SERVICE_EXPLANATIONS.get(port, {
                        "severity": "INFO",
                        "impact": "Standard Port",
                        "desc": f"Port {port} is open."
                    })
                    try:
                        service = socket.getservbyport(port, "tcp")
                    except OSError:
                        service = "unknown"
                    open_ports.append({
                        "port": port,
                        "proto": "tcp",
                        "state": "open",
                        "service": service,
                        "product": "",
                        "version": "",
                        **info,
                    })
            except socket.gaierror as error:
                raise ValueError(f"Invalid target '{target}': {error}") from error

    return [{
        "ip": host,
        "hostname": "",
        "status": "up",
        "ports": open_ports,
    }]

def generate_report(target_range, results):
    stats = {
        "total_hosts": len(results),
        "critical": 0,
        "high": 0,
        "medium_low": 0
    }
    
    for host in results:
        for p in host.get("ports", []):
            sev = p.get("severity")
            if sev == "CRITICAL":
                stats["critical"] += 1
            elif sev == "HIGH":
                stats["high"] += 1
            elif sev in ["MEDIUM", "LOW"]:
                stats["medium_low"] += 1

    template = Template(HTML_TEMPLATE)
    rendered_html = template.render(
        target=target_range,
        scan_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        hosts=results,
        stats=stats
    )
    
    return rendered_html

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        target = sys.argv[1]
        scan_results = run_assessment(target)
        generate_report(target, scan_results)

# -------------------------------------


def run_my_program(user_input: str) -> str:
    return f"Python processed your input: '{user_input.upper()}'"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/run-script', methods=['POST'])
def run_script():
    target = request.form.get('user_data', '').strip()
    try:
        scan_results = run_assessment(target)
        return generate_report(target, scan_results)
    except (OSError, ValueError, ImportError) as error:
        return render_template(
            'index.html',
            output=f'Unable to scan {target}: {error}',
            previous_input=target,
        ), 400


@app.route('/report')
def report():
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
