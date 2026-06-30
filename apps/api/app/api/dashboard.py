DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BugBountyHunter - Automated Code Security & Repair Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #040711;
            --card-bg: rgba(8, 12, 28, 0.65);
            --border-color: rgba(0, 210, 255, 0.12);
            --accent-primary: #ffffff;
            --accent-secondary: #00d2ff;
            --accent-cyber-red: #ff2a3a;
            --text-main: #f4f4f5;
            --text-secondary: #a1a1aa;
            --text-muted: #64748b;
            --success-color: #10b981;
            --error-color: #ff2a3a;
            --warning-color: #f59e0b;
            --info-color: #3b82f6;
            --font-serif: 'Rajdhani', sans-serif;
            --font-sans: 'Space Grotesk', sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
            --font-terminal: 'Share Tech Mono', monospace;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-sans);
            background-color: var(--bg-color);
            background-image: 
                linear-gradient(rgba(4, 7, 17, 0.8), rgba(4, 7, 17, 0.8)),
                url('/static/cyber_biohazard_background.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        /* Tech grid background pattern */
        body::before {
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(255, 255, 255, 0.008) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 255, 255, 0.008) 1px, transparent 1px);
            background-size: 50px 50px;
            background-position: center;
            pointer-events: none;
            z-index: 1;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1.5rem 5rem 1.5rem;
            position: relative;
            z-index: 10;
        }

        /* Header Style */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 0;
            margin-bottom: 3rem;
            position: relative;
            z-index: 100;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            cursor: pointer;
        }

        .logo-icon {
            font-size: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .logo-text {
            font-family: var(--font-terminal);
            font-size: 1.45rem;
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }

        .server-status {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(52, 211, 153, 0.06);
            color: var(--success-color);
            padding: 0.4rem 0.9rem;
            border-radius: 50px;
            font-weight: 500;
            font-size: 0.8rem;
            border: 1px solid rgba(52, 211, 153, 0.15);
            font-family: var(--font-terminal);
            letter-spacing: 0.3px;
        }

        .server-status-dot {
            width: 6px;
            height: 6px;
            background-color: var(--success-color);
            border-radius: 50%;
            animation: pulse-dot 1.5s infinite ease-in-out;
        }

        .nav-btn-started {
            padding: 0.5rem 1.1rem;
            background: var(--text-main);
            color: var(--bg-color);
            border: none;
            border-radius: 50px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            border: 1px solid var(--text-main);
            font-family: Georgia, serif;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .nav-btn-started:hover {
            background: transparent;
            color: var(--text-main);
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.15);
        }

        /* Hero Section */
        .hero-section {
            text-align: center;
            padding: 2rem 1rem 6rem 1rem;
            position: relative;
            z-index: 5;
        }

        .hero-title {
            font-family: var(--font-serif);
            font-size: 5.8rem;
            font-weight: 700;
            line-height: 1.02;
            letter-spacing: -1px;
            color: #ffffff;
            margin-bottom: 1.8rem;
            text-transform: uppercase;
        }

        .hero-subtitle {
            font-family: var(--font-serif);
            font-style: italic;
            font-weight: 600;
            background: linear-gradient(135deg, #ffffff 30%, var(--accent-secondary) 75%, #ef4444 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            padding-right: 0.15em;
            display: inline-block;
        }

        .hero-description {
            font-size: 1.15rem;
            color: var(--text-secondary);
            max-width: 480px;
            margin: 0 auto 2.2rem auto;
            line-height: 1.6;
            font-weight: 300;
        }

        .hero-btn {
            padding: 0.85rem 2.2rem;
            background: #ffffff;
            color: var(--bg-color);
            border: none;
            border-radius: 50px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1);
            font-family: Georgia, serif;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .hero-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(255, 255, 255, 0.25);
            background: #f4f4f5;
        }



        /* Glassmorphic Panel Cards */
        .glass-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            padding: 2.5rem;
            box-shadow: 
                0 25px 50px -12px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.04);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .glass-card:hover {
            border-color: rgba(255, 255, 255, 0.09);
            box-shadow: 
                0 30px 60px -10px rgba(0, 0, 0, 0.6),
                inset 0 1px 0 rgba(255, 255, 255, 0.06);
            transform: translateY(-2px);
        }

        /* Scan Submission Card */
        .submission-card {
            max-width: 800px;
            margin: -2.5rem auto 3rem auto;
            position: relative;
            z-index: 20;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 500;
            color: #ffffff;
            margin-bottom: 1.2rem;
            letter-spacing: -0.2px;
        }

        .form-row {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            background: rgba(255, 255, 255, 0.025);
            padding: 0.4rem;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.04);
            transition: all 0.3s ease;
        }

        .form-row:focus-within {
            border-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
            background: rgba(255, 255, 255, 0.04);
        }

        .input-wrapper {
            flex: 1;
            min-width: 280px;
        }

        input[type="text"] {
            width: 100%;
            padding: 0.95rem 1.2rem;
            background: transparent;
            border: none;
            color: var(--text-main);
            font-size: 0.95rem;
            font-family: var(--font-sans);
            transition: all 0.3s ease;
            outline: none;
        }

        input[type="text"]::placeholder {
            color: var(--text-muted);
        }

        .submit-btn {
            padding: 0.85rem 2.2rem;
            background: #ff6e6e;
            border: none;
            border-radius: 50px;
            color: #040711;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
            font-family: 'Century', Georgia, serif;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            box-shadow: 0 4px 15px rgba(255, 110, 110, 0.2);
        }

        .submit-btn:hover {
            background: #ff8585;
            box-shadow: 0 10px 25px rgba(255, 110, 110, 0.4), 0 0 15px rgba(0, 210, 255, 0.3);
            transform: translateY(-2px);
        }

        .submit-btn:active {
            transform: translateY(0);
        }



        /* Scans Table */
        .scans-card {
            max-width: 1000px;
            margin: 0 auto;
            position: relative;
            z-index: 20;
        }

        .scans-table-wrapper {
            overflow-x: auto;
            margin-top: 1.5rem;
        }

        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 0.4rem;
            text-align: left;
            table-layout: fixed;
        }

        th {
            padding: 0.9rem 1.25rem;
            color: var(--text-muted);
            font-weight: 500;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }

        td {
            padding: 1.1rem 1.25rem;
            background: rgba(255, 255, 255, 0.01);
            border-top: 1px solid rgba(255, 255, 255, 0.02);
            border-bottom: 1px solid rgba(255, 255, 255, 0.02);
            font-size: 0.92rem;
            transition: all 0.2s ease;
        }

        td:first-child {
            border-left: 1px solid rgba(255, 255, 255, 0.02);
            border-radius: 12px 0 0 12px;
        }

        td:last-child {
            border-right: 1px solid rgba(255, 255, 255, 0.02);
            border-radius: 0 12px 12px 0;
        }

        tr:hover td {
            background: rgba(255, 255, 255, 0.025);
            border-color: rgba(255, 255, 255, 0.06);
        }

        .repo-name-text {
            font-weight: 600;
            color: #ffffff;
            font-size: 0.95rem;
            margin-bottom: 0.2rem;
        }

        .repo-url-text {
            font-size: 0.78rem;
            color: var(--text-muted);
            word-break: break-all;
        }

        .scan-id-text {
            font-family: var(--font-mono);
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            padding: 0.35rem 0.75rem;
            border-radius: 50px;
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: capitalize;
            border: 1px solid transparent;
        }

        .status-completed {
            background: rgba(52, 211, 153, 0.06);
            color: var(--success-color);
            border-color: rgba(52, 211, 153, 0.15);
            box-shadow: 0 0 10px rgba(52, 211, 153, 0.05);
        }

        .status-scanning, .status-running {
            background: rgba(96, 165, 250, 0.06);
            color: var(--info-color);
            border-color: rgba(96, 165, 250, 0.15);
            box-shadow: 0 0 10px rgba(96, 165, 250, 0.05);
            animation: pulse-dot 1.8s infinite ease-in-out;
        }

        .status-failed {
            background: rgba(248, 113, 113, 0.06);
            color: var(--error-color);
            border-color: rgba(248, 113, 113, 0.15);
        }

        .status-pending {
            background: rgba(251, 191, 36, 0.06);
            color: var(--warning-color);
            border-color: rgba(251, 191, 36, 0.15);
        }

        .action-link {
            color: var(--accent-secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            white-space: nowrap;
        }

        .action-link:hover {
            color: #ffffff;
            text-decoration: underline;
        }

        .action-link::after {
            content: " →";
            transition: transform 0.2s ease;
            display: inline-block;
        }

        .action-link:hover::after {
            transform: translateX(4px);
        }

        /* Detail Modal Side-panel Overlay */
        .overlay {
            position: fixed;
            top: 0;
            right: -650px;
            width: 100%;
            max-width: 650px;
            height: 100vh;
            background: rgba(9, 9, 11, 0.75);
            backdrop-filter: blur(40px);
            -webkit-backdrop-filter: blur(40px);
            border-left: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: -20px 0 50px rgba(0, 0, 0, 0.8);
            z-index: 1000;
            transition: right 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            display: flex;
            flex-direction: column;
        }

        .overlay.active {
            right: 0;
        }

        .overlay-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1.5rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }

        .close-btn {
            font-size: 1.5rem;
            cursor: pointer;
            color: var(--text-muted);
            transition: color 0.2s ease;
            background: none;
            border: none;
            padding: 0.4rem;
        }

        .close-btn:hover {
            color: #ffffff;
        }

        .overlay-content {
            flex: 1;
            overflow-y: auto;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }

        .overlay-section-title {
            font-size: 0.8rem;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 0.8px;
            margin-bottom: 0.6rem;
            font-weight: 600;
        }

        .overlay-url {
            word-break: break-all;
            color: var(--accent-secondary);
            font-weight: 500;
            font-size: 0.95rem;
        }

        /* Code & Diff Styles */
        .code-container {
            background: #040405;
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 12px;
            padding: 1.1rem;
            font-family: var(--font-mono);
            font-size: 0.82rem;
            overflow-x: auto;
            white-space: pre;
            line-height: 1.5;
            color: #e4e4e7;
        }

        .diff-added {
            color: #34d399;
            background: rgba(52, 211, 153, 0.08);
            display: inline-block;
            width: 100%;
        }

        .diff-removed {
            color: #f87171;
            background: rgba(248, 113, 113, 0.08);
            display: inline-block;
            width: 100%;
        }

        /* Tabs inside detail panel */
        .tabs-header {
            display: flex;
            gap: 0.4rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            margin-bottom: 1rem;
        }

        .tab-btn {
            background: none;
            border: none;
            color: var(--text-muted);
            padding: 0.6rem 1rem;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.85rem;
            border-bottom: 2px solid transparent;
            transition: all 0.2s ease;
            font-family: Georgia, serif;
        }

        .tab-btn.active {
            color: #ffffff;
            border-bottom-color: #ffffff;
        }

        .tab-btn:hover {
            color: #ffffff;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .finding-item {
            border: 1px solid rgba(255, 255, 255, 0.04);
            background: rgba(255, 255, 255, 0.015);
            border-radius: 12px;
            padding: 1.1rem;
            margin-bottom: 0.8rem;
        }

        .finding-title {
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 0.3rem;
            font-size: 0.92rem;
        }

        .finding-meta {
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        /* Animations */
        @keyframes float-y {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-22px) rotate(3deg); }
        }

        @keyframes float-y-offset {
            0% { transform: translateY(0) rotate(0deg); }
            100% { transform: translateY(-16px) rotate(-4deg); }
        }

        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        @keyframes twinkle {
            0%, 100% { transform: scale(0.6); opacity: 0.3; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }

        .backdrop {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(5px);
            z-index: 999;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.3s ease;
        }

        .backdrop.active {
            opacity: 1;
            pointer-events: auto;
        }
    </style>
</head>
<body>

<div class="container">
    <header>
        <div class="logo-area" onclick="location.reload()">
            <span class="logo-icon">
                <svg class="logo-svg" viewBox="0 0 100 100" width="36" height="36" style="display: inline-block; vertical-align: middle;">
                    <!-- Shield Outer -->
                    <path d="M50 5 L85 18 C85 55 50 82 50 95 C50 82 15 55 15 18 Z" fill="#090a10" stroke="#1c1e2a" stroke-width="3"/>
                    <!-- Shield Inner White Border -->
                    <path d="M50 9 L80 20 C80 51 50 74 50 86 C50 74 20 51 20 20 Z" fill="#0a0b12" stroke="#ffffff" stroke-width="2"/>
                    <!-- Grey Code Dashes -->
                    <path d="M38 27 h24 M32 33 h36 M32 72 h36 M38 78 h24" stroke="#4b5563" stroke-width="2" stroke-linecap="round" stroke-dasharray="6,4,4,4"/>
                    <!-- Left Bracket -->
                    <path d="M35 46 L27 51 L35 56" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <!-- Right Bracket -->
                    <path d="M65 46 L73 51 L65 56" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    <!-- Bug Legs -->
                    <path d="M44 47 C39 45 37 41 37 41 M43 51 C38 51 36 53 36 53 M44 55 C39 57 37 61 37 61" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
                    <path d="M56 47 C61 45 63 41 63 41 M57 51 C62 51 64 53 64 53 M56 55 C61 57 63 61 63 61" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
                    <!-- Bug Antennae -->
                    <path d="M47 37 C45 32 41 33 41 33 M53 37 C55 32 59 33 59 33" fill="none" stroke="#ef4444" stroke-width="1.8" stroke-linecap="round"/>
                    <!-- Bug Head -->
                    <circle cx="50" cy="40" r="3.5" fill="#ef4444"/>
                    <!-- Bug Body -->
                    <ellipse cx="50" cy="51" rx="6.5" ry="9" fill="#ef4444"/>
                    <!-- Bug Center Line -->
                    <line x1="50" y1="44" x2="50" y2="59" stroke="#0a0b12" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
            </span>
            <span class="logo-text">bugbountyhunter.ai</span>
        </div>
        <div class="header-right">
            <div class="server-status">
                <span class="server-status-dot"></span>
                <span>System Online</span>
            </div>
            <button class="nav-btn-started" onclick="scrollToPortal()">Get Started</button>
        </div>
    </header>

    <!-- Hero Area -->
    <section class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">The Best<br><span class="hero-subtitle">Bug Bounty Hunter</span></h1>
            <p class="hero-description">An autonomous AI agent scanning repositories, detecting vulnerabilities, and applying secure code patches instantly.</p>
            <button class="hero-btn" onclick="scrollToPortal()">Get Started</button>
        </div>
    </section>

    <!-- Scan submission -->
    <section class="glass-card submission-card" id="scan-portal">
        <h2 class="section-title">Scan & Auto-Repair New Repository</h2>
        <div class="form-row">
            <div class="input-wrapper">
                <input type="text" id="repoUrl" placeholder="Enter GitHub Repository URL (e.g., https://github.com/user/repo)" />
            </div>
            <button class="submit-btn" onclick="submitScan()">
                <span id="btnText">Initiate Bug Hunt</span>
            </button>
        </div>
    </section>

    <!-- Agent Diagnostics & Benchmark Evaluation -->
    <section class="glass-card submission-card" style="margin-top: 1rem; max-width: 800px;" id="eval-portal">
        <h2 class="section-title" style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.8rem;">
            <span>📊</span> Agent Diagnostics & Benchmark Suite
        </h2>
        <p style="font-size: 0.88rem; color: var(--text-secondary); margin-bottom: 1.2rem; line-height: 1.5;">
            Execute a local automated test runner that injects intentional coding errors (e.g. undefined names, broken return logic) to verify self-refinement accuracy and security guardrails under sandbox conditions.
        </p>
        <button class="submit-btn" style="background: linear-gradient(135deg, var(--accent-secondary) 0%, #3b82f6 100%); color: #ffffff; box-shadow: 0 4px 15px rgba(0, 210, 255, 0.2);" onclick="runEvaluator()">
            <span id="evalBtnText">Run Agent Benchmark</span>
        </button>
        <div id="evalResults" style="margin-top: 1rem; display: none;"></div>
    </section>

    <!-- Active scans table -->
    <section class="glass-card scans-card">
        <h2 class="section-title" style="margin-bottom: 0.5rem;">Recent Security Scans</h2>
        <div class="scans-table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th style="width: 45%;">Repository</th>
                        <th style="width: 25%;">Scan ID</th>
                        <th style="width: 15%;">Status</th>
                        <th style="width: 15%;">Actions</th>
                    </tr>
                </thead>
                <tbody id="scansTableBody">
                    <tr>
                        <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 2rem;">Loading scan logs...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</div>

<!-- Modal Detail Backdrop -->
<div class="backdrop" id="backdrop" onclick="closeOverlay()"></div>

<!-- Slide-in detail panel -->
<div class="overlay" id="detailOverlay">
    <div class="overlay-header">
        <h2 id="overlayTitle" class="section-title" style="margin-bottom: 0;">Scan Details</h2>
        <button class="close-btn" onclick="closeOverlay()">&times;</button>
    </div>
    <div class="overlay-content" id="overlayContent">
        <!-- Dyn details -->
    </div>
</div>

<script>
    const API_BASE = window.location.origin;

    function scrollToPortal() {
        document.getElementById("scan-portal").scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    async function loadRecentScans() {
        try {
            const res = await fetch(`${API_BASE}/api/scans`);
            const scans = await res.json();
            const tbody = document.getElementById("scansTableBody");
            
            if (scans.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 2rem;">No scans executed yet. Submit a repository URL above!</td></tr>`;
                return;
            }

            tbody.innerHTML = scans.map(scan => `
                <tr>
                    <td>
                        <div class="repo-name-text">${scan.repo_name}</div>
                        <div class="repo-url-text">${scan.github_url}</div>
                    </td>
                    <td class="scan-id-text" title="${scan.id}">${scan.id.substring(0, 8)}...</td>
                    <td>
                        <span class="status-badge status-${scan.status}">
                            ${scan.status === 'completed' ? '✅' : scan.status === 'failed' ? '❌' : '⏳'} ${scan.status}
                        </span>
                    </td>
                    <td>
                        <span class="action-link" onclick="viewScanDetails('${scan.id}')">View Analysis</span>
                    </td>
                </tr>
            `).join("");
        } catch (err) {
            console.error("Failed to load scans", err);
        }
    }

    async function submitScan() {
        const urlInput = document.getElementById("repoUrl");
        const btnText = document.getElementById("btnText");
        const url = urlInput.value.trim();

        if (!url) {
            alert("Please enter a valid GitHub URL!");
            return;
        }

        try {
            btnText.textContent = "Hunting Bugs...";
            const res = await fetch(`${API_BASE}/api/scan`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ github_url: url })
            });
            const data = await res.json();
            
            urlInput.value = "";
            btnText.textContent = "Initiate Bug Hunt";
            
            // Reload scan table
            await loadRecentScans();
            
            alert("BugBountyHunter scan submitted successfully! Processing in background...");
        } catch (err) {
            alert("Error submitting scan repository.");
            btnText.textContent = "Initiate Bug Hunt";
        }
    }

    async function viewScanDetails(scanId) {
        const overlay = document.getElementById("detailOverlay");
        const backdrop = document.getElementById("backdrop");
        const content = document.getElementById("overlayContent");
        
        content.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 3rem;">Loading scan details...</div>`;
        overlay.classList.add("active");
        backdrop.classList.add("active");

        try {
            const res = await fetch(`${API_BASE}/api/scans/${scanId}`);
            const data = await res.json();
            
            document.getElementById("overlayTitle").textContent = `${data.repository.repo_name} Analysis`;
            
            // Build findings layout
            let findingsHtml = "";
            const tools = Object.keys(data.scan.findings || {});
            
            if (tools.length === 0) {
                findingsHtml = `<div style="color: var(--text-muted);">No issues or outputs recorded by scanners.</div>`;
            } else {
                // Render tabs for tools
                const tabHeaders = tools.map((tool, idx) => `
                    <button class="tab-btn ${idx === 0 ? 'active' : ''}" onclick="switchTab(event, '${tool}')">${tool.toUpperCase()}</button>
                `).join("");
                
                const tabBodies = tools.map((tool, idx) => {
                    const result = data.scan.findings[tool];
                    const stdout = result.stdout || "";
                    const stderr = result.stderr || "";
                    
                    return `
                        <div id="tab-${tool}" class="tab-content ${idx === 0 ? 'active' : ''}">
                            ${stdout ? `
                                <div class="overlay-section-title">Scanner Output:</div>
                                <div class="code-container">${escapeHtml(stdout)}</div>
                            ` : ""}
                            ${stderr ? `
                                <div class="overlay-section-title" style="margin-top: 1rem; color: var(--error-color);">Scanner Errors:</div>
                                <div class="code-container" style="border-color: rgba(248, 113, 113, 0.15);">${escapeHtml(stderr)}</div>
                            ` : ""}
                            ${(!stdout && !stderr) ? '<div style="color: var(--text-muted);">Scanner exited with no output.</div>' : ''}
                        </div>
                    `;
                }).join("");
                
                findingsHtml = `
                    <div>
                        <div class="tabs-header">${tabHeaders}</div>
                        <div>${tabBodies}</div>
                    </div>
                `;
            }

            // Build fixes/patches applied layout
            let fixesHtml = "";
            if (data.fixes.length === 0) {
                fixesHtml = `<div style="color: var(--text-muted); font-size: 0.95rem;">No permanent patches applied. The code has no repairable violations or validation tests were rejected.</div>`;
            } else {
                fixesHtml = data.fixes.map(fix => `
                    <div class="finding-item">
                        <div class="finding-title">🔧 Applied Fix: ${fix.file_path}</div>
                        <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.75rem;">Status: <span style="color: var(--success-color); font-weight: bold;">${fix.status}</span></div>
                        <div class="code-container" style="border-color: rgba(52, 211, 153, 0.15);">${formatDiff(fix.patch)}</div>
                    </div>
                `).join("");
            }

            // Build candidate attempts layout
            let attemptsHtml = "";
            if (data.attempts.length === 0) {
                attemptsHtml = `<div style="color: var(--text-muted); font-size: 0.95rem;">No patch candidate attempts generated.</div>`;
            } else {
                attemptsHtml = data.attempts.map(att => {
                    let valHtml = "";
                    if (att.validation_result) {
                        try {
                            const val = JSON.parse(att.validation_result);
                            const errLog = (val.stderr || "") + (val.stdout || "");
                            if (errLog.trim()) {
                                valHtml = `
                                    <details style="margin-top: 0.5rem;">
                                        <summary style="cursor: pointer; color: var(--error-color); font-size: 0.8rem; font-weight: 500; outline: none;">Show Validation Errors</summary>
                                        <div class="code-container" style="border-color: rgba(248, 113, 113, 0.15); font-size: 0.78rem; margin-top: 0.4rem; max-height: 150px; overflow-y: auto;">${escapeHtml(errLog)}</div>
                                    </details>
                                `;
                            }
                        } catch (e) {
                            console.error(e);
                        }
                    }

                    // Style item color and icon depending on status
                    let isMemory = false;
                    let cleanStatus = att.status;
                    if (att.status.endsWith("_memory")) {
                        isMemory = true;
                        cleanStatus = att.status.replace("_memory", "");
                    }
                    
                    let memoryBadge = isMemory ? `<span style="background: rgba(0, 210, 255, 0.12); color: var(--accent-secondary); padding: 0.15rem 0.45rem; border-radius: 4px; font-size: 0.72rem; font-weight: bold; margin-left: 0.5rem; border: 1px solid rgba(0, 210, 255, 0.25);">🧠 MEMORY HIT</span>` : "";

                    let itemBorder = "rgba(255,255,255,0.02)";
                    let statusLabel = cleanStatus;
                    let icon = "⏳";
                    if (cleanStatus.includes("passed")) {
                        itemBorder = "rgba(52, 211, 153, 0.15)";
                        icon = "✅";
                    } else if (cleanStatus.includes("failed")) {
                        itemBorder = "rgba(248, 113, 113, 0.15)";
                        icon = "❌";
                    } else if (cleanStatus.includes("rejected")) {
                        itemBorder = "rgba(239, 68, 68, 0.25)";
                        icon = "🛡️";
                    }

                    // Format human readable statuses
                    if (cleanStatus.startsWith("refined_attempt_")) {
                        const cycle = cleanStatus.split("_")[2];
                        const outcome = cleanStatus.split("_")[3];
                        statusLabel = `Self-Refinement Cycle #${cycle} (${outcome})`;
                    } else if (cleanStatus === "rejected_security_guardrail") {
                        statusLabel = "Security Guardrail Violation (Blocked)";
                    }

                    return `
                        <div class="finding-item" style="border-color: ${itemBorder};">
                            <div class="finding-title" style="color: #ffffff; display: flex; align-items: center; gap: 0.4rem;">
                                <span>${icon}</span>
                                <span>File: ${att.file_path} (Line ${att.line_number})</span>
                                ${memoryBadge}
                            </div>
                            <div class="finding-meta" style="margin-top: 0.2rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
                                <span>Status: <b style="color: #ffffff;">${statusLabel}</b></span>
                                <span>Score: <b style="color: ${att.score >= 1.0 ? 'var(--success-color)' : 'var(--warning-color)'}">${att.score}</b></span>
                            </div>
                            <details style="outline: none;">
                                <summary style="cursor: pointer; color: var(--accent-secondary); font-size: 0.85rem; font-weight: 500; outline: none; margin-bottom: 0.5rem;">Show Patch Candidate Diff</summary>
                                <div class="code-container" style="font-size: 0.8rem;">${formatDiff(att.patch)}</div>
                            </details>
                            ${valHtml}
                        </div>
                    `;
                }).join("");
            }

            let traceHtml = "";
            if (data.scan.reasoning_trace) {
                traceHtml = `
                    <div class="code-container" style="font-size: 0.78rem; font-family: var(--font-mono); max-height: 250px; overflow-y: auto; white-space: pre-wrap; border-color: rgba(0, 210, 255, 0.2); line-height: 1.4; color: #a1a1aa;">${escapeHtml(data.scan.reasoning_trace)}</div>
                `;
            } else {
                traceHtml = `<div style="color: var(--text-muted); font-size: 0.9rem;">No reasoning traces logged for this scan.</div>`;
            }

            content.innerHTML = `
                <div>
                    <div class="overlay-section-title">GitHub URL</div>
                    <div class="overlay-url">${data.repository.github_url}</div>
                </div>

                <div style="background: rgba(0, 210, 255, 0.03); border: 1px solid rgba(0, 210, 255, 0.1); border-radius: 12px; padding: 1rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; letter-spacing: 0.5px;">LLM Token Usage</div>
                        <div style="font-size: 1.3rem; font-weight: 700; color: #ffffff; font-family: var(--font-mono); margin-top: 0.2rem;">${data.scan.token_usage || 0} <span style="font-size: 0.75rem; font-weight: 500; color: var(--text-muted);">tokens</span></div>
                    </div>
                    <div style="width: 1px; height: 30px; background: rgba(255,255,255,0.08);"></div>
                    <div>
                        <div style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-muted); font-weight: 600; letter-spacing: 0.5px;">Agent Execution Time</div>
                        <div style="font-size: 1.3rem; font-weight: 700; color: #ffffff; font-family: var(--font-mono); margin-top: 0.2rem;">${data.scan.execution_time ? data.scan.execution_time.toFixed(1) : "0.0"} <span style="font-size: 0.75rem; font-weight: 500; color: var(--text-muted);">seconds</span></div>
                    </div>
                </div>

                <div>
                    <div class="overlay-section-title">Agent Inner Monologue & Trace</div>
                    ${traceHtml}
                </div>

                <div>
                    <div class="overlay-section-title">Tool Findings</div>
                    ${findingsHtml}
                </div>

                <div>
                    <div class="overlay-section-title">Successful Repairs</div>
                    ${fixesHtml}
                </div>

                <div>
                    <div class="overlay-section-title">Candidate Repair Attempts Log</div>
                    ${attemptsHtml}
                </div>
            `;
        } catch (err) {
            content.innerHTML = `<div style="color: var(--error-color); text-align: center; padding: 3rem;">Error retrieving scan information.</div>`;
        }
    }

    function switchTab(evt, tool) {
        const tabBtns = document.getElementsByClassName("tab-btn");
        const tabContents = document.getElementsByClassName("tab-content");
        
        for (let btn of tabBtns) {
            btn.classList.remove("active");
        }
        for (let content of tabContents) {
            content.classList.remove("active");
        }
        
        evt.currentTarget.classList.add("active");
        document.getElementById(`tab-${tool}`).classList.add("active");
    }

    function closeOverlay() {
        document.getElementById("detailOverlay").classList.remove("active");
        document.getElementById("backdrop").classList.remove("active");
    }

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function formatDiff(patch) {
        if (!patch) return '<span style="color: var(--text-muted);">No changes.</span>';
        
        return patch.split('\\n').map(line => {
            const escaped = escapeHtml(line);
            if (line.startsWith('+') && !line.startsWith('+++')) {
                return `<span class="diff-added">${escaped}</span>`;
            } else if (line.startsWith('-') && !line.startsWith('---')) {
                return `<span class="diff-removed">${escaped}</span>`;
            }
            return escaped;
        }).join('\\n');
    }

    async function runEvaluator() {
        const btnText = document.getElementById("evalBtnText");
        const resultsDiv = document.getElementById("evalResults");
        
        try {
            btnText.textContent = "Benchmarking Agent...";
            resultsDiv.style.display = "none";
            
            const res = await fetch(`${API_BASE}/api/evaluate`, {
                method: "POST"
            });
            const data = await res.json();
            
            btnText.textContent = "Run Agent Benchmark";
            
            if (data.error) {
                resultsDiv.innerHTML = `<div style="color: var(--error-color); font-size: 0.9rem; padding: 1rem; border: 1px solid rgba(255,42,58,0.2); border-radius: 8px; background: rgba(255,42,58,0.02)">Error running benchmark: ${data.error}</div>`;
                resultsDiv.style.display = "block";
                return;
            }
            
            resultsDiv.innerHTML = `
                <div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 1.2rem; margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 0.6rem;">
                        <span style="font-weight: 600; color: #ffffff; font-size: 0.95rem;">Benchmark Run Completed</span>
                        <span class="status-badge status-completed" style="text-transform: uppercase;">
                            ${data.status === 'passed' ? '✅ PASS' : '❌ FAIL'}
                        </span>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem;">
                        <div>
                            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 600;">SUCCESS RATE</div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: var(--success-color); font-family: var(--font-mono); margin-top: 0.2rem;">${data.success_rate_percentage}%</div>
                        </div>
                        <div>
                            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 600;">BUGS FIXED</div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: #ffffff; font-family: var(--font-mono); margin-top: 0.2rem;">${data.bugs_successfully_fixed} / ${data.total_bugs_preset}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 600;">REFINEMENT CYCLES</div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: #ffffff; font-family: var(--font-mono); margin-top: 0.2rem;">${data.self_refinement_cycles_executed}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.72rem; color: var(--text-muted); font-weight: 600;">RUN-TIME ELAPSED</div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: #ffffff; font-family: var(--font-mono); margin-top: 0.2rem;">${data.execution_time_seconds}s</div>
                        </div>
                    </div>
                </div>
            `;
            resultsDiv.style.display = "block";
            
            await loadRecentScans();
        } catch (err) {
            btnText.textContent = "Run Agent Benchmark";
            resultsDiv.innerHTML = `<div style="color: var(--error-color); font-size: 0.9rem; padding: 1rem;">Fetch communication error: check if server is running.</div>`;
            resultsDiv.style.display = "block";
        }
    }

    loadRecentScans();
    setInterval(loadRecentScans, 6000);
</script>

</body>
</html>
"""
