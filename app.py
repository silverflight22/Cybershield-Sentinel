import os
import json
import time
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from google import genai
from google.genai import types

app = FastAPI(title="Cybershield Sentinel")

def analyze_phishing_content(text: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "risk_level": "High",
            "score": 95,
            "threats": ["API Key Missing"],
            "analysis": "GEMINI_API_KEY environment variable is not set. Run 'set GEMINI_API_KEY=your_key' in your terminal before running."
        }

    # Sequence of models to try in order of performance and availability
    fallback_models = [
        ("gemini-2.0-flash-lite", "v1"),
        ("gemini-2.0-flash", "v1"),
         ("gemini-3.5-flash", "v1"),
           ("gemini-3.6-flash", "v1"),
        
    ]

    prompt = f"""
You are a cybersecurity expert analyzing a potential phishing attempt.
Analyze the following text/email content for phishing indicators, urgency tactics, brand impersonation, and malicious intent.

Text to analyze:
---
{text}
---

Return ONLY a valid JSON object matching this exact structure:
{{
  "risk_level": "High" | "Medium" | "Low",
  "score": <integer from 0 to 100>,
  "threats": ["list", "of", "detected", "threats"],
  "analysis": "A concise breakdown of why this content was flagged or marked safe."
}}
"""

    last_error = None

    for model_name, api_version in fallback_models:
        try:
            print(f"[*] Attempting analysis with model: {model_name} ({api_version})...")
            
            # Initialize client with the specific API version appropriate for the model
            client = genai.Client(http_options={"api_version": api_version})
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            result = json.loads(response.text)
            print(f"[✓] Analysis successful using: {model_name}")
            return result

        except Exception as e:
            error_msg = str(e)
            print(f"[!] Model {model_name} failed: {error_msg}")
            last_error = error_msg
            time.sleep(0.5)

    return {
        "risk_level": "High",
        "score": 90,
        "threats": ["All Fallback Models Exhausted"],
        "analysis": f"All fallback attempts failed. Last recorded error: {last_error}"
    }

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cybershield Sentinel - Phishing Detector</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen font-sans">
    <div class="max-w-4xl mx-auto px-4 py-8">
        <header class="mb-8 border-b border-slate-800 pb-6">
            <h1 class="text-3xl font-extrabold text-cyan-400 tracking-tight flex items-center gap-3">
                <span>🛡️</span> Cybershield Sentinel
            </h1>
            <p class="text-slate-400 mt-2">AI-Powered Threat Analysis & Phishing Detection Engine</p>
        </header>

        <main class="space-y-6">
            <div class="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                <label for="emailContent" class="block text-sm font-semibold text-slate-300 mb-2">
                    Paste Email, SMS, or Message Content to Scan:
                </label>
                <textarea 
                    id="emailContent" 
                    rows="8" 
                    class="w-full bg-slate-900 border border-slate-700 rounded-lg p-4 text-slate-200 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition placeholder-slate-500"
                    placeholder="Paste email text, header, or link here..."
                ></textarea>
                
                <button 
                    onclick="analyzeText()" 
                    id="scanBtn"
                    class="mt-4 w-full bg-cyan-600 hover:bg-cyan-500 text-white font-bold py-3 rounded-lg transition duration-200 shadow-lg shadow-cyan-950 flex items-center justify-center gap-2"
                >
                    <span>🔍</span> Analyze Content
                </button>
            </div>

            <div id="loader" class="hidden text-center py-8">
                <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-cyan-400"></div>
                <p class="text-slate-400 mt-2 text-sm">Evaluating threat telemetry...</p>
            </div>

            <div id="resultsCard" class="hidden bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
                <div class="flex items-center justify-between border-b border-slate-700 pb-4 mb-4">
                    <div>
                        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Threat Status</span>
                        <div id="riskLabel" class="text-sm font-bold mt-1">--</div>
                    </div>
                    <div class="text-right">
                        <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Risk Score</span>
                        <div id="riskScore" class="text-2xl font-black text-cyan-400 mt-1">0/100</div>
                    </div>
                </div>

                <div class="mb-4">
                    <h3 class="text-sm font-semibold text-slate-300 mb-2">Detected Indicators & Threat Tactics:</h3>
                    <ul id="threatsList" class="list-disc list-inside text-sm text-slate-400 space-y-1 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                    </ul>
                </div>

                <div>
                    <h3 class="text-sm font-semibold text-slate-300 mb-1">Detailed Analysis:</h3>
                    <p id="analysisText" class="text-sm text-slate-300 leading-relaxed bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                    </p>
                </div>
            </div>
        </main>
    </div>

    <script>
        async function analyzeText() {
            const text = document.getElementById('emailContent').value.trim();
            if (!text) {
                alert('Please paste some text to analyze.');
                return;
            }

            const loader = document.getElementById('loader');
            const resultsCard = document.getElementById('resultsCard');
            const scanBtn = document.getElementById('scanBtn');

            loader.classList.remove('hidden');
            resultsCard.classList.add('hidden');
            scanBtn.disabled = true;

            try {
                const formData = new FormData();
                formData.append('content', text);

                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                document.getElementById('riskLabel').innerText = data.risk_level + ' Risk';
                document.getElementById('riskLabel').className = 'text-sm font-bold ' + 
                    (data.risk_level === 'High' ? 'text-red-400' : data.risk_level === 'Medium' ? 'text-amber-400' : 'text-emerald-400');

                document.getElementById('riskScore').innerText = data.score + '/100';

                const list = document.getElementById('threatsList');
                list.innerHTML = '';
                if (data.threats && data.threats.length > 0) {
                    data.threats.forEach(t => {
                        const li = document.createElement('li');
                        li.innerText = t;
                        list.appendChild(li);
                    });
                } else {
                    list.innerHTML = '<li>No major threat indicators detected.</li>';
                }

                document.getElementById('analysisText').innerText = data.analysis;
                resultsCard.classList.remove('hidden');

            } catch (err) {
                alert('Network error analyzing request.');
            } finally {
                loader.classList.add('hidden');
                scanBtn.disabled = false;
            }
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@app.post("/analyze", response_class=JSONResponse)
async def analyze_endpoint(content: str = Form(...)):
    result = analyze_phishing_content(content)
    return JSONResponse(content=result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
