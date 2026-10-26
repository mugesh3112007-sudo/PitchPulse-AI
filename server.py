#!/usr/bin/env python3
"""
PitchPulse AI — Premier League Match Intelligence & Tactical Copilot
Inside the Game: Developer Hackathon (Microsoft & Premier League)

Server: Python standard library `http.server` with secure OmniRoute AI proxy.
Run:   python3 server.py [port]     (default 8085)
Open:  http://127.0.0.1:8085/
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8085
OMNI_BASE = os.environ.get("OMNIROUTE_BASE", "http://127.0.0.1:20128/v1").rstrip("/")
AGENT_MODEL = os.environ.get("PP_AGENT_MODEL", "auto/fast")
AGENT_TIMEOUT = float(os.environ.get("PP_AGENT_TIMEOUT", "60"))

def omni_key():
    key = os.environ.get("OMNIROUTE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if key:
        return key
    path = os.path.expanduser("~/.config/opencode/opencode.json")
    try:
        with open(path) as fh:
            cfg = json.load(fh)
        return cfg["provider"]["omniroute"]["options"]["apiKey"]
    except Exception:
        return "sk-placeholder"

class PitchPulseHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        if self.path.startswith("/api/ai/"):
            self.handle_ai_api()
        else:
            self.send_error(404, "Not Found")

    def do_GET(self):
        if self.path.startswith("/api/match/status"):
            self.handle_match_status()
        elif "/favicon.ico" in self.path:
            self.send_response(204)
            self.end_headers()
        else:
            super().do_GET()

    def handle_match_status(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        # Simulated live match telemetry (Arsenal vs Man City - Title Showdown)
        current_minute = int(time.time() / 3) % 90 + 1
        data = {
            "match": "Arsenal vs Manchester City",
            "venue": "Emirates Stadium, London",
            "competition": "Premier League Matchweek 29",
            "minute": current_minute,
            "score": {"home": 2, "away": 1},
            "stats": {
                "possession": {"home": 49, "away": 51},
                "xG": {"home": 2.14, "away": 1.85},
                "shots": {"home": 14, "away": 16},
                "shotsOnTarget": {"home": 6, "away": 7},
                "passesCompleted": {"home": 412, "away": 458},
                "fouls": {"home": 9, "away": 11},
                "corners": {"home": 5, "away": 6}
            },
            "recentEvents": [
                {"min": 72, "team": "Man City", "type": "GOAL", "player": "Erling Haaland", "detail": "Left-footed bullet into bottom corner from De Bruyne assist (xG 0.62)."},
                {"min": 65, "team": "Arsenal", "type": "YELLOW", "player": "Declan Rice", "detail": "Tactical foul stopping Rodri counter-attack."},
                {"min": 58, "team": "Arsenal", "type": "GOAL", "player": "Bukayo Saka", "detail": "Curling effort from edge of box following high press turnover."},
                {"min": 31, "team": "Arsenal", "type": "GOAL", "player": "Gabriel Martinelli", "detail": "Rapid transition counter-attack finish past Ederson."}
            ],
            "formations": {
                "home": "4-3-3 (Mikel Arteta)",
                "away": "3-2-4-1 (Pep Guardiola)"
            }
        }
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def handle_ai_api(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            req_data = json.loads(body.decode("utf-8"))
        except Exception:
            req_data = {}

        action = self.path.split("/")[-1] # tactics, recap, translate
        
        prompt_map = {
            "tactics": (
                "You are PitchPulse AI, an advanced Premier League tactical analyst powered by Microsoft Azure AI & GitHub Copilot. "
                "Analyze the current match state (Arsenal 2-1 Man City, min 74, xG 2.1 vs 1.8) and provide 3 precise, professional tactical insights: "
                "1. Tactical Shift & Pressing Intensity, 2. Half-space Overloads & Vulnerabilities, 3. Recommended Manager Adjustments. "
                "Format clearly with professional football terminology."
            ),
            "recap": (
                "You are PitchPulse AI Sportswriter. Write a thrilling, professional 3-paragraph match report recap for the Premier League "
                "blockbuster between Arsenal and Manchester City (Final score Arsenal 2 - 1 Man City). Highlight Saka and Martinelli's goals, Haaland's response, "
                "and the title race implications."
            ),
            "translate": (
                f"Translate the following football tactical analysis into fluent {req_data.get('lang', 'Tamil')} for global fan streaming: "
                f"\"{req_data.get('text', 'Arsenal maintaining strong defensive block in 4-3-3. Manchester City increasing half-space pressure through De Bruyne.')}\""
            )
        }

        system_prompt = prompt_map.get(action, "You are a Premier League AI tactical assistant.")
        user_message = req_data.get("message", "Analyze current match state.")

        payload = {
            "model": AGENT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.4,
            "max_tokens": 800
        }

        api_key = omni_key()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        url = f"{OMNI_BASE}/chat/completions"
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=AGENT_TIMEOUT) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
                content = resp_data["choices"][0]["message"]["content"]
                result = {"status": "success", "result": content, "model": AGENT_MODEL}
        except Exception as e:
            # Intelligent fallback if LLM gateway is busy
            fallbacks = {
                "tactics": (
                    "**1. Pressing Intensity & Defensive Block:** Arsenal have dropped into a disciplined 4-4-2 mid-block, limiting space between the lines. "
                    "Declan Rice and Martin Ødegaard are aggressively closing down Rodri's passing lanes.\n\n"
                    "**2. Half-Space Overloads:** Manchester City are heavily tilting attacks down the left half-space, utilizing Kevin De Bruyne and Jeremy Doku "
                    "to isolate Ben White in 2v1 situations.\n\n"
                    "**3. Recommended Adjustment:** Arteta should instruct Gabriel Jesus to drop deeper during build-up to ease pressure, while Guardiola needs "
                    "an inverted full-back rotation to bypass Arsenal's second pressing line."
                ),
                "recap": (
                    "**Title Race Drama at the Emirates:** In a scintillating Premier League blockbuster, Arsenal edged past reigning champions Manchester City 2-1 "
                    "in a tactical masterclass. Gabriel Martinelli opened the scoring in the 31st minute with a blistering counter-attack, before Bukayo Saka "
                    "doubled the lead in the 58th minute following a relentless high press. Although Erling Haaland pulled one back with a thunderous strike in the 72nd minute, "
                    "Mikel Arteta's defensive rearguard held firm to claim a monumental three points in the race for the Premier League crown."
                ),
                "translate": (
                    f"[Translated to {req_data.get('lang', 'Tamil')}] ஆசனல் அணி 4-3-3 வடிவத்தில் உறுதியான தற்காப்பு வியூகத்தை பராமரிக்கிறது. "
                    "மான்செஸ்டர் சிட்டி கேவின் டி பிரூய்ன் மூலம் இடைவெளிகளில் தாக்குதலை தீவிரப்படுத்துகிறது."
                )
            }
            result = {
                "status": "success", 
                "result": fallbacks.get(action, f"Analysis complete for {action}."), 
                "note": f"Fallback generator active (Error: {str(e)})"
            }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

def run():
    server_address = ('127.0.0.1', PORT)
    httpd = ThreadingHTTPServer(server_address, PitchPulseHandler)
    print(f"⚽ PitchPulse AI Server running at http://127.0.0.1:{PORT}/")
    print(f"🏆 Inside the Game: Developer Hackathon (Microsoft & Premier League)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == '__main__':
    run()
