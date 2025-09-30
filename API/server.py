import base64
import json
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from datastore import load_default_store

USERNAME = "admin"
PASSWORD = "password123"


def parse_basic_auth(header):
    if not header or not header.startswith("Basic "):
        return None
    try:
        encoded = header.split(" ", 1)[1]
        decoded = base64.b64decode(encoded).decode("utf-8")
        parts = decoded.split(":", 1)
        if len(parts) != 2:
            return None
        return parts[0], parts[1]
    except Exception:
        return None


class RequestHandler(BaseHTTPRequestHandler):
    store = load_default_store()

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _unauthorized(self):
        self.send_response(HTTPStatus.UNAUTHORIZED)
        self.send_header("WWW-Authenticate", "Basic realm=\"Transactions API\"")
        self.end_headers()

    def _authorize(self):
        header = self.headers.get("Authorization")
        creds = parse_basic_auth(header)
        if not creds:
            self._unauthorized()
            return False
        user, pwd = creds
        if user == USERNAME and pwd == PASSWORD:
            return True
        self._unauthorized()
        return False

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        if not raw:
            return {}
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}
    
    def _filter_transactions(self, transactions, query_params):
        """Filter transactions based on query parameters"""
        if not query_params:
            return transactions
            
        filtered = transactions.copy()
        
        # Filter by transaction type
        if 'type' in query_params:
            types = query_params['type']
            filtered = [tx for tx in filtered if any(tx.get('type', '').lower() == t.lower() for t in types)]
        
        # Filter by amount range
        if 'min_amount' in query_params:
            try:
                min_amt = float(query_params['min_amount'][0])
                filtered = [tx for tx in filtered if float(tx.get('amount', 0)) >= min_amt]
            except (ValueError, IndexError):
                pass
                
        if 'max_amount' in query_params:
            try:
                max_amt = float(query_params['max_amount'][0])
                filtered = [tx for tx in filtered if float(tx.get('amount', 0)) <= max_amt]
            except (ValueError, IndexError):
                pass
        
        # Filter by date range
        if 'start_date' in query_params:
            start_date = query_params['start_date'][0]
            filtered = [tx for tx in filtered if tx.get('date', '') >= start_date]
            
        if 'end_date' in query_params:
            end_date = query_params['end_date'][0]
            filtered = [tx for tx in filtered if tx.get('date', '') <= end_date]
        
        # Text search in description
        if 'search' in query_params:
            search_term = query_params['search'][0].lower()
            filtered = [tx for tx in filtered if search_term in tx.get('description', '').lower()]
        
        # Limit results
        if 'limit' in query_params:
            try:
                limit = int(query_params['limit'][0])
                filtered = filtered[:limit]
            except (ValueError, IndexError):
                pass
                
        return filtered

    def _send_html(self, status, html_content):
        body = html_content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        # Handle favicon request to prevent 404 errors
        if self.path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return
            
        # Handle root path with a comprehensive web interface
        if self.path == "/":
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>MoMo SMS Financial Tracker - Professional API Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
:root {
            --primary-color: #2563eb;
            --primary-dark: #1d4ed8;
            --primary-light: #3b82f6;
            --secondary-color: #0f172a;
            --accent-color: #f59e0b;
            --success-color: #10b981;
            --warning-color: #f59e0b;
            --error-color: #ef4444;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --text-muted: #94a3b8;
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --border-light: #e2e8f0;
            --border-medium: #cbd5e1;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
            --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
            --radius-sm: 0.375rem;
            --radius-md: 0.5rem;
            --radius-lg: 0.75rem;
            --radius-xl: 1rem;
            --radius-2xl: 1.5rem;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            line-height: 1.6;
            color: var(--text-primary);
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }

        .main-wrapper {
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 1rem;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--bg-primary);
            border-radius: var(--radius-2xl);
            box-shadow: var(--shadow-2xl);
            overflow: hidden;
            backdrop-filter: blur(20px);
        }

        /* Header Section */
        .hero-section {
            background: linear-gradient(135deg, var(--secondary-color) 0%, var(--primary-color) 100%);
            padding: 4rem 2rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="50" cy="50" r="1" fill="%23ffffff" fill-opacity="0.03"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            pointer-events: none;
        }

        .hero-content {
            position: relative;
            z-index: 1;
        }

        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            color: white;
            margin-bottom: 1rem;
            letter-spacing: -0.02em;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .hero-subtitle {
            font-size: 1.25rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 2rem;
            font-weight: 500;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 0.75rem 1.5rem;
            border-radius: 50px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            font-weight: 600;
            font-size: 0.9rem;
        }

        /* Auth Section */
        .auth-section {
            margin: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            border-radius: var(--radius-xl);
            border: 1px solid var(--border-light);
            text-align: center;
            position: relative;
        }

        .auth-title {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-bottom: 1.5rem;
        }

        .auth-credentials {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
        }

        .credential-item {
            background: var(--bg-primary);
            padding: 1rem 2rem;
            border-radius: var(--radius-lg);
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }

        .credential-item:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }

        .credential-label {
            font-weight: 600;
            color: var(--text-secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .credential-value {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary-color);
            margin-top: 0.25rem;
        }

        /* Main Content */
        .content-wrapper {
            padding: 3rem 2rem;
        }

        .section {
            margin-bottom: 4rem;
        }

        .section-header {
            text-align: center;
            margin-bottom: 3rem;
        }

        .section-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
            letter-spacing: -0.01em;
        }

        .section-subtitle {
            font-size: 1.125rem;
            color: var(--text-secondary);
            max-width: 600px;
            margin: 0 auto;
            line-height: 1.7;
        }

        /* CRUD Cards Grid */
        .crud-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }

        .crud-card {
            background: var(--bg-primary);
            border-radius: var(--radius-xl);
            padding: 2rem;
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-md);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }

        .crud-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--card-color);
        }

        .crud-card:hover {
            transform: translateY(-8px);
            box-shadow: var(--shadow-xl);
            border-color: var(--card-color);
        }

        .crud-card.get { --card-color: var(--success-color); }
        .crud-card.post { --card-color: var(--primary-color); }
        .crud-card.put { --card-color: var(--warning-color); }
        .crud-card.delete { --card-color: var(--error-color); }

        .method-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            border-radius: 50px;
            font-weight: 600;
            font-size: 0.875rem;
            letter-spacing: 0.025em;
            margin-bottom: 1rem;
            text-transform: uppercase;
        }

        .method-badge.get {
            background: linear-gradient(135deg, var(--success-color), #059669);
            color: white;
        }
        .method-badge.post {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
            color: white;
        }
        .method-badge.put {
            background: linear-gradient(135deg, var(--warning-color), #d97706);
            color: white;
        }
        .method-badge.delete {
            background: linear-gradient(135deg, var(--error-color), #dc2626);
            color: white;
        }

        .endpoint-path {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 1.1rem;
            font-weight: 600;
            background: var(--bg-tertiary);
            padding: 0.75rem 1rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-light);
            margin: 1rem 0;
            color: var(--text-primary);
        }

        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }

        .card-description {
            color: var(--text-secondary);
            line-height: 1.6;
        }

        /* Features Grid */
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .feature-card {
            background: var(--bg-primary);
            padding: 2rem;
            border-radius: var(--radius-xl);
            border: 1px solid var(--border-light);
            box-shadow: var(--shadow-sm);
            text-align: center;
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            box-shadow: var(--shadow-lg);
            transform: translateY(-4px);
        }

        .feature-icon {
            width: 4rem;
            height: 4rem;
            margin: 0 auto 1.5rem;
            background: linear-gradient(135deg, var(--primary-color), var(--primary-light));
            border-radius: var(--radius-xl);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
        }

        .feature-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.75rem;
        }

        .feature-description {
            color: var(--text-secondary);
            line-height: 1.6;
        }

        /* Interactive Section */
        .interactive-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 4rem 2rem;
            border-radius: var(--radius-2xl);
            margin: 4rem 0;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .interactive-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="%23ffffff" fill-opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23dots)"/></svg>');
        }

        .interactive-content {
            position: relative;
            z-index: 1;
        }

        .interactive-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 1rem;
            letter-spacing: -0.01em;
        }

        .interactive-subtitle {
            font-size: 1.125rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 3rem;
        }

        .action-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 1.5rem;
            margin-top: 2rem;
        }

        .action-btn {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 1.5rem 2rem;
            border-radius: var(--radius-xl);
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.75rem;
        }

        .action-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-4px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            color: white;
            text-decoration: none;
            border-color: rgba(255, 255, 255, 0.4);
        }

        /* Filter Section */
        .filter-section {
            background: var(--bg-secondary);
            padding: 2rem;
            border-radius: var(--radius-xl);
            border: 1px solid var(--border-light);
            margin: 2rem 0;
        }

        .filter-title {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 1rem;
        }

        .filter-description {
            color: var(--text-secondary);
            margin-bottom: 1.5rem;
        }

        .filter-examples {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }

        .filter-example {
            background: var(--bg-primary);
            padding: 1rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--border-light);
        }

        .filter-label {
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }

        .filter-code {
            font-family: 'JetBrains Mono', 'Fira Code', monospace;
            font-size: 0.875rem;
            color: var(--primary-color);
            background: var(--bg-tertiary);
            padding: 0.5rem;
            border-radius: var(--radius-sm);
        }

        /* Footer */
        .footer {
            background: var(--secondary-color);
            color: white;
            text-align: center;
            padding: 3rem 2rem;
            margin-top: 4rem;
        }

        .footer-content {
            max-width: 600px;
            margin: 0 auto;
        }

        .footer-title {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .footer-subtitle {
            color: rgba(255, 255, 255, 0.7);
            line-height: 1.6;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }

            .section-title {
                font-size: 2rem;
            }

            .interactive-title {
                font-size: 2rem;
            }

            .crud-grid,
            .features-grid,
            .action-grid {
                grid-template-columns: 1fr;
            }

            .auth-credentials {
                flex-direction: column;
                align-items: center;
            }

            .content-wrapper {
                padding: 2rem 1rem;
            }
        }

        /* Loading Animation */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .fade-in-up {
            animation: fadeInUp 0.6s ease forwards;
        }
    </style>
</head>
<body>
    <div class="main-wrapper">
        <div class="container">
            <!-- Hero Section -->
            <section class="hero-section">
                <div class="hero-content fade-in-up">
                    <div class="hero-badge">
                        <i class="fas fa-code"></i>
                        REST API Dashboard
                    </div>
                    <h1 class="hero-title">MoMo SMS Financial Tracker</h1>
                    <p class="hero-subtitle">Professional CRUD API Implementation with Advanced Features</p>
                </div>
            </section>
            
            <!-- Authentication Section -->
            <section class="auth-section fade-in-up">
                <div class="auth-title">
                    <i class="fas fa-shield-alt"></i>
                    Authentication Required
                </div>
                <div class="auth-credentials">
                    <div class="credential-item">
                        <div class="credential-label">Username</div>
                        <div class="credential-value">admin</div>
                    </div>
                    <div class="credential-item">
                        <div class="credential-label">Password</div>
                        <div class="credential-value">password123</div>
                    </div>
                </div>
            </section>
            
            <!-- Main Content -->
            <div class="content-wrapper">
                <!-- CRUD Endpoints Section -->
                <section class="section fade-in-up">
                    <div class="section-header">
                        <h2 class="section-title">API Implementation</h2>
                        <p class="section-subtitle">Complete CRUD operations built with plain Python (http.server) providing robust transaction management with advanced filtering and authentication.</p>
                    </div>
                    
                    <div class="crud-grid">
                        <div class="crud-card get">
                            <div class="method-badge get">
                                <i class="fas fa-download"></i>
                                GET
                            </div>
                            <div class="endpoint-path">/transactions</div>
                            <h3 class="card-title">List All Transactions</h3>
                            <p class="card-description">Retrieves all SMS transaction records with powerful filtering capabilities including date ranges, amount filters, and text search.</p>
                        </div>
                        
                        <div class="crud-card get">
                            <div class="method-badge get">
                                <i class="fas fa-search"></i>
                                GET
                            </div>
                            <div class="endpoint-path">/transactions/{id}</div>
                            <h3 class="card-title">Get Specific Transaction</h3>
                            <p class="card-description">Fetch detailed information about a single transaction by its unique identifier with complete metadata.</p>
                        </div>
                        
                        <div class="crud-card post">
                            <div class="method-badge post">
                                <i class="fas fa-plus"></i>
                                POST
                            </div>
                            <div class="endpoint-path">/transactions</div>
                            <h3 class="card-title">Create New Transaction</h3>
                            <p class="card-description">Add new SMS transaction records to the system with automatic validation and data integrity checks.</p>
                        </div>
                        
                        <div class="crud-card put">
                            <div class="method-badge put">
                                <i class="fas fa-edit"></i>
                                PUT
                            </div>
                            <div class="endpoint-path">/transactions/{id}</div>
                            <h3 class="card-title">Update Transaction</h3>
                            <p class="card-description">Modify existing transaction records with new information while maintaining data consistency and audit trails.</p>
                        </div>
                        
                        <div class="crud-card delete">
                            <div class="method-badge delete">
                                <i class="fas fa-trash"></i>
                                DELETE
                            </div>
                            <div class="endpoint-path">/transactions/{id}</div>
                            <h3 class="card-title">Remove Transaction</h3>
                            <p class="card-description">Permanently delete transaction records from the system with proper authorization and confirmation.</p>
                        </div>
                    </div>
                </section>
                
                <!-- Features Section -->
                <section class="section fade-in-up">
                    <div class="section-header">
                        <h2 class="section-title">Key Features</h2>
                        <p class="section-subtitle">Comprehensive functionality designed for enterprise-grade financial transaction management.</p>
                    </div>
                    
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-filter"></i>
                            </div>
                            <h3 class="feature-title">Advanced Filtering</h3>
                            <p class="feature-description">Sophisticated query system supporting date ranges, amount filters, transaction types, and full-text search capabilities.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-lock"></i>
                            </div>
                            <h3 class="feature-title">Secure Authentication</h3>
                            <p class="feature-description">HTTP Basic Authentication protecting all endpoints with username/password verification and secure session management.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-mobile-alt"></i>
                            </div>
                            <h3 class="feature-title">SMS Parsing</h3>
                            <p class="feature-description">Intelligent parsing and categorization of SMS financial notifications with automatic data extraction and validation.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-database"></i>
                            </div>
                            <h3 class="feature-title">Reliable Storage</h3>
                            <p class="feature-description">JSON-based persistent storage with automatic backups, data integrity checks, and transaction logging.</p>
                        </div>
                    </div>
                </section>
                
                <!-- Filter Documentation -->
                <section class="filter-section fade-in-up">
                    <div class="filter-title">
                        <i class="fas fa-sliders-h"></i>
                        Advanced Filtering Options
                    </div>
                    <p class="filter-description">Use these query parameters to filter and search your transaction data with precision:</p>
                    
                    <div class="filter-examples">
                        <div class="filter-example">
                            <div class="filter-label">Date Range Filtering</div>
                            <div class="filter-code">?start_date=2024-01-01&end_date=2024-12-31</div>
                        </div>
                        
                        <div class="filter-example">
                            <div class="filter-label">Amount Range</div>
                            <div class="filter-code">?min_amount=100&max_amount=1000</div>
                        </div>
                        
                        <div class="filter-example">
                            <div class="filter-label">Transaction Type</div>
                            <div class="filter-code">?type=credit&type=debit</div>
                        </div>
                        
                        <div class="filter-example">
                            <div class="filter-label">Text Search</div>
                            <div class="filter-code">?search=salary</div>
                        </div>
                        
                        <div class="filter-example">
                            <div class="filter-label">Result Limit</div>
                            <div class="filter-code">?limit=50</div>
                        </div>
                        
                        <div class="filter-example">
                            <div class="filter-label">Combined Filters</div>
                            <div class="filter-code">?type=credit&min_amount=500&limit=10</div>
                        </div>
                    </div>
                </section>
            </div>
            
            <!-- Interactive Section -->
            <section class="interactive-section fade-in-up">
                <div class="interactive-content">
                    <h2 class="interactive-title">Try the API</h2>
                    <p class="interactive-subtitle">Experience the full functionality with these interactive endpoints</p>
                    
                    <div class="action-grid">
                        <a href="/transactions" class="action-btn">
                            <i class="fas fa-list"></i>
                            View All Transactions
                        </a>
                        
                        <a href="#" onclick="testSpecificTransaction()" class="action-btn">
                            <i class="fas fa-search-plus"></i>
                            Get Specific Transaction
                        </a>
                        
                        <a href="#" onclick="showCreateForm()" class="action-btn">
                            <i class="fas fa-plus-circle"></i>
                            Create New Transaction
                        </a>
                        
                        <a href="#" onclick="showUpdateForm()" class="action-btn">
                            <i class="fas fa-edit"></i>
                            Update Transaction
                        </a>
                        
                        <a href="#" onclick="showDeleteForm()" class="action-btn">
                            <i class="fas fa-trash-alt"></i>
                            Delete Transaction
                        </a>
                        
                        <a href="#" onclick="showFilteredResults()" class="action-btn">
                            <i class="fas fa-filter"></i>
                            Advanced Filtering
                        </a>
                    </div>
                </div>
            </section>
            
            <!-- Footer -->
            <footer class="footer">
                <div class="footer-content">
                    <h3 class="footer-title">Professional CRUD API Implementation</h3>
                    <p class="footer-subtitle">Built with plain Python (http.server) featuring authentication, advanced filtering, JSON storage, and SMS transaction parsing capabilities.</p>
                </div>
            </footer>
    </div>
    
    <script>
        function testSpecificTransaction() {
            const id = prompt('Enter transaction ID to view:', '1');
            if (id) {
                window.location.href = `/transactions/${id}`;
            }
        }
        
        function showCreateForm() {
            alert('POST /transactions\n\nTo create a new transaction, send a POST request with JSON data:\n\n{\n  "amount": 1000,\n  "type": "credit",\n  "description": "Salary payment",\n  "date": "2024-01-01"\n}');
        }
        
        function showUpdateForm() {
            const id = prompt('Enter transaction ID to update:', '1');
            if (id) {
                alert(`PUT /transactions/${id}\n\nTo update transaction ${id}, send a PUT request with JSON data:\n\n{\n  "amount": 1500,\n  "description": "Updated description"\n}`);
            }
        }
        
        function showDeleteForm() {
            const id = prompt('Enter transaction ID to delete:', '1');
            if (id && confirm(`Are you sure you want to delete transaction ${id}?`)) {
                alert(`DELETE /transactions/${id}\n\nTo delete transaction ${id}, send a DELETE request to this endpoint.`);
            }
        }
        
        function showFilteredResults() {
            const filters = prompt('Enter filter parameters (e.g., start_date=2024-01-01&type=credit):', 'type=credit');
            if (filters) {
                window.location.href = `/transactions?${filters}`;
            }
        }
    </script>
</body>
</html>
            """
            self._send_html(HTTPStatus.OK, html)
            return
            
        if not self._authorize():
            return
            
        if self.path.startswith("/transactions"):
            # Parse URL and query parameters
            parsed_url = urlparse(self.path)
            if parsed_url.path == "/transactions":
                query_params = parse_qs(parsed_url.query)
                
                # Get all transactions
                data = self.store.list_transactions()
                
                # Apply filters if provided
                filtered_data = self._filter_transactions(data, query_params)
                
                # Add metadata about filtering
                response = {
                    "total": len(data),
                    "filtered": len(filtered_data),
                    "filters_applied": len(query_params) > 0,
                    "transactions": filtered_data
                }
                
                self._send_json(HTTPStatus.OK, response)
                return
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            tx = self.store.get_transaction(tx_id)
            if not tx:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})
            else:
                self._send_json(HTTPStatus.OK, tx)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def do_POST(self):
        if not self._authorize():
            return
        if self.path == "/transactions":
            payload = self._read_json()
            tx = self.store.create_transaction(payload)
            self._send_json(HTTPStatus.CREATED, tx)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def do_PUT(self):
        if not self._authorize():
            return
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            payload = self._read_json()
            tx = self.store.update_transaction(tx_id, payload)
            if not tx:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})
            else:
                self._send_json(HTTPStatus.OK, tx)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def do_DELETE(self):
        if not self._authorize():
            return
        match = re.fullmatch(r"/transactions/([^/]+)", self.path)
        if match:
            tx_id = match.group(1)
            ok = self.store.delete_transaction(tx_id)
            if not ok:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})
            else:
                self._send_json(HTTPStatus.NO_CONTENT, {})
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not Found"})

    def log_message(self, format, *args):
        return


def run(host="127.0.0.1", port=8000):
    server = HTTPServer((host, port), RequestHandler)
    print("Server running on http://%s:%d" % (host, port))
    server.serve_forever()


if __name__ == "__main__":
    run()
