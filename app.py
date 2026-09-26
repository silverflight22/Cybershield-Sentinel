import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai

app = FastAPI(title="Cybershield Sentinel")

# Initialize Google Gemini Client
# Reads GEMINI_API_KEY directly from Render environment variables
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None

class AnalysisRequest(BaseModel):
    content: str | None = None
    text: str | None = None
    message: str | None = None

# Single-page Upgraded Dashboard UI
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cybershield Sentinel — Phishing & Threat Analysis</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;700&family=Inter:wght@300;400;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0b0f19; color: #e2e8f0; }
        .code-font { font-family: 'Fira Code', monospace; }
        .glow-cyan { box-shadow: 0 0 20px rgba(6, 182, 212, 0.25); }
        .glow-danger { box-shadow: 0 0 25px rgba(239, 68, 68, 0.35); }
        .glow-success { box-shadow: 0 0 25px rgba(34, 197, 94, 0.35); }
        .bg-grid {
            background-size: 30px 30px;
            background-image: 
                linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
        }
    </style>
</head>
<body class="min-h-screen bg-grid flex flex-col justify-between">

    <!-- Header / Navbar -->
    <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 text-xl font-bold">
                    <i class="fa-solid fa-shield-halved"></i>
                </div>
                <div>
                    <h1 class="font-bold text-lg tracking-wide text-slate-100 flex items-center gap-2">
                        CYBERSHIELD <span class="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">SENTINEL v1.0</span>
                    </h1>
                    <p class="text-xs text-slate-400">AI-Powered Phishing & Threat Intelligence Platform</p>
                </div>
            </div>
            <div class="flex items-center space-x-4">
                <div class="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-full border border-slate-700 text-xs">
                    <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span class="text-slate-300 font-medium">System Online</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-5xl mx-auto px-4 py-10 w-full flex-grow">

        <div class="mb-8 text-center">
            <h2 class="text-3xl font-extrabold text-white tracking-tight sm:text-4xl mb-2">
                Analyze Suspicious Content & URLs
            </h2>
            <p class="text-slate-400 text-sm max-w-2xl mx-auto">
                Paste suspicious email headers, website URLs, or raw message text. Cybershield utilizes Google Gemini AI to detect phishing indicators and malicious vector risks in real time.
            </p>
        </div>

        <!-- Main Input Card -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-2xl mb-8 glow-cyan">
            <form id="analyzeForm" onsubmit="submitAnalysis(event)">
                <div class="mb-4">
                    <label for="inputText" class="block text-sm font-semibold text-slate-300 mb-2 flex items-center justify-between">
                        <span><i class="fa-solid fa-terminal text-cyan-400 mr-2"></i>Suspicious Payload / Email / URL Text</span>
                        <span class="text-xs text-slate-500 font-normal">Supports raw text, URLs, headers, or email bodies</span>
                    </label>
                    <textarea 
                        id="inputText" 
                        rows="6" 
                        required 
                        placeholder="Paste suspicious URL (e.g. http://secure-update-paypal-verify.com) or full email body text here..."
                        class="w-full bg-slate-950 border border-slate-800 rounded-xl p-4 text-slate-200 code-font text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition shadow-inner placeholder-slate-600"
                    ></textarea>
                </div>

                <div class="flex items-center justify-between">
                    <button 
                        type="button" 
                        onclick="loadSample()" 
                        class="text-xs text-cyan-400 hover:text-cyan-300 hover:underline flex items-center gap-1"
                    >
                        <i class="fa-solid fa-lightbulb"></i> Load Phishing Sample
                    </button>
                    <button 
                        type="submit" 
                        id="submitBtn"
                        class="px-6 py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold text-sm rounded-xl transition shadow-lg flex items-center gap-2 cursor-pointer"
                    >
                        <i class="fa-solid fa-magnifying-glass font-bold"></i> Analyze Threat
                    </button>
                </div>
            </form>
        </div>

        <!-- Loading State -->
        <div id="loadingState" class="hidden text-center py-12">
            <div class="inline-block p-4 rounded-full bg-cyan-500/10 border border-cyan-500/20 mb-4 animate-bounce">
                <i class="fa-solid fa-shield-cat text-4xl text-cyan-400 animate-pulse"></i>
            </div>
            <h3 class="text-lg font-semibold text-slate-200 mb-1">Scanning Threat Vectors...</h3>
            <p class="text-sm text-slate-400">Communicating with Cybershield AI Engine</p>
        </div>

        <!-- Error State -->
        <div id="errorState" class="hidden bg-red-950/40 border border-red-800/80 rounded-xl p-4 mb-8 text-red-300 text-sm flex items-start gap-3">
            <i class="fa-solid fa-triangle-exclamation text-xl text-red-400 mt-0.5"></i>
            <div>
                <p class="font-semibold text-red-200" id="errorTitle">Analysis Request Failed</p>
                <p id="errorMessage" class="text-xs text-red-300/80 mt-1"></p>
            </div>
        </div>

        <!-- Results Display Container -->
        <div id="resultContainer" class="hidden space-y-6">
            <div id="resultHeaderCard" class="bg-slate-900/90 border rounded-2xl p-6 shadow-2xl relative overflow-hidden transition-all">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div class="flex items-center gap-4">
                        <div id="verdictIconContainer" class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold">
                            <i id="verdictIcon" class="fa-solid fa-shield"></i>
                        </div>
                        <div>
                            <span id="verdictBadge" class="px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider">
                                UNKNOWN
                            </span>
                            <h3 id="verdictTitle" class="text-xl font-bold text-slate-100 mt-1">
                                Analysis Complete
                            </h3>
                        </div>
                    </div>
                    
                    <div class="bg-slate-950 px-5 py-3 rounded-xl border border-slate-800 flex items-center gap-4">
                        <div>
                            <div class="text-xs text-slate-400 uppercase tracking-wider font-semibold">Risk Level</div>
                            <div id="riskLevelText" class="text-lg font-extrabold text-slate-200">MEDIUM</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <h4 class="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-list-check text-cyan-400"></i> AI Assessment & Findings
                    </h4>
                    <div id="summaryText" class="text-sm text-slate-300 leading-relaxed space-y-2"></div>
                </div>

                <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <h4 class="text-sm font-semibold text-slate-200 mb-3 flex items-center gap-2">
                        <i class="fa-solid fa-code text-cyan-400"></i> Raw API Response
                    </h4>
                    <pre id="rawOutput" class="bg-slate-950 p-4 rounded-xl text-xs code-font text-emerald-400 overflow-x-auto max-h-60 border border-slate-800"></pre>
                </div>
            </div>
        </div>

    </main>

    <footer class="border-t border-slate-800 bg-slate-900/50 py-6 text-center text-xs text-slate-500">
        <p>Cybershield Sentinel Threat Intelligence Platform • Powered by FastAPI & Google Gemini AI</p>
    </footer>

    <script>
        function loadSample() {
            document.getElementById('inputText').value = 
`URGENT ACCOUNT NOTICE: Dear Customer, 

We noticed suspicious sign-in attempts on your account from an unrecognized device. For your protection, your access has been temporarily restricted.

Please verify your identity immediately to restore full account access:
http://security-update-paypal-login-alert.com/verify-identity

If you do not complete verification within 24 hours, your account will be permanently suspended.`;
        }

        async function submitAnalysis(e) {
            e.preventDefault();

            const text = document.getElementById('inputText').value.trim();
            if (!text) return;

            const loadingState = document.getElementById('loadingState');
            const resultContainer = document.getElementById('resultContainer');
            const errorState = document.getElementById('errorState');
            const submitBtn = document.getElementById('submitBtn');

            loadingState.classList.remove('hidden');
            resultContainer.classList.add('hidden');
            errorState.classList.add('hidden');
            submitBtn.disabled = true;
            submitBtn.classList.add('opacity-50');

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ content: text })
                });

                if (!response.ok) {
                    const errData = await response.json().catch(() => ({}));
                    throw new Error(errData.detail || `Server returned status ${response.status}`);
                }

                const data = await response.json();
                displayResults(data);

            } catch (err) {
                document.getElementById('errorTitle').innerText = 'Analysis Failed';
                document.getElementById('errorMessage').innerText = err.message;
                errorState.classList.remove('hidden');
            } finally {
                loadingState.classList.add('hidden');
                submitBtn.disabled = false;
                submitBtn.classList.remove('opacity-50');
            }
        }

        function displayResults(data) {
            const resultContainer = document.getElementById('resultContainer');
            const rawOutput = document.getElementById('rawOutput');
            const summaryText = document.getElementById('summaryText');
            
            const verdictHeader = document.getElementById('resultHeaderCard');
            const verdictIconContainer = document.getElementById('verdictIconContainer');
            const verdictIcon = document.getElementById('verdictIcon');
            const verdictBadge = document.getElementById('verdictBadge');
            const verdictTitle = document.getElementById('verdictTitle');
            const riskLevelText = document.getElementById('riskLevelText');

            rawOutput.innerText = JSON.stringify(data, null, 2);

            const isPhishing = data.is_phishing || data.phishing || data.verdict === 'phishing' || false;
            const riskLevel = (data.risk_level || data.risk || (isPhishing ? 'HIGH' : 'LOW')).toUpperCase();
            const analysis = data.analysis || data.details || data.reason || data.message || JSON.stringify(data);

            summaryText.innerHTML = `<p>${analysis.replace(/\n/g, '<br>')}</p>`;
            riskLevelText.innerText = riskLevel;

            if (isPhishing || riskLevel === 'HIGH' || riskLevel === 'CRITICAL') {
                verdictHeader.className = "bg-slate-900/90 border border-red-800/80 rounded-2xl p-6 shadow-2xl glow-danger";
                verdictIconContainer.className = "w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold bg-red-500/20 text-red-400 border border-red-500/30";
                verdictIcon.className = "fa-solid fa-triangle-exclamation";
                verdictBadge.className = "px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider bg-red-500/20 text-red-400 border border-red-500/30";
                verdictBadge.innerText = "PHISHING THREAT DETECTED";
                verdictTitle.innerText = "High-Risk Threat Identified";
                riskLevelText.className = "text-lg font-extrabold text-red-400";
            } else {
                verdictHeader.className = "bg-slate-900/90 border border-emerald-800/80 rounded-2xl p-6 shadow-2xl glow-success";
                verdictIconContainer.className = "w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
                verdictIcon.className = "fa-solid fa-shield-check";
                verdictBadge.className = "px-2.5 py-1 rounded-md text-xs font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
                verdictBadge.innerText = "SAFE / LOW RISK";
                verdictTitle.innerText = "No Phishing Indicators Found";
                riskLevelText.className = "text-lg font-extrabold text-emerald-400";
            }

            resultContainer.classList.remove('hidden');
            resultContainer.scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return HTML_CONTENT

@app.post("/analyze")
def analyze_threat(payload: AnalysisRequest):
    content = payload.content or payload.text or payload.message
    if not content:
        raise HTTPException(status_code=400, detail="No content provided for analysis.")

    if not client:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable is not configured on Render.")

    prompt = f"""
    You are an expert cybersecurity threat analyst.
    Analyze the following input text for phishing attempts, spoofing indicators, suspicious links, urgency manipulation, or malware risk.

    Input content:
    "{content}"

    Provide a response in JSON format matching this exact schema:
    {{
        "is_phishing": boolean,
        "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
        "analysis": "Detailed breakdown explaining why this is or isn't a threat."
    }}
    Return raw JSON only.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        raw_text = response.text.strip()

        # Clean JSON fences if model returns markdown formatting
        if raw_text.startswith("```json"):
            raw_text = raw_text.removeprefix("```json").removesuffix("```").strip()
        elif raw_text.startswith("```"):
            raw_text = raw_text.removeprefix("```").removesuffix("```").strip()

        import json
        parsed = json.loads(raw_text)
        return parsed

    except Exception as e:
        # Fallback structured response if JSON parsing fails
        return {
            "is_phishing": True,
            "risk_level": "HIGH",
            "analysis": f"Threat analysis complete. Raw model feedback:\n{response.text if 'response' in locals() else str(e)}"
        }
