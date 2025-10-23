import os
import logging
import datetime
import sqlite3
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import aiofiles

# --- Setup Logger ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("MORA_AI")

# --- Load environment variables ---
load_dotenv()
PORT = int(os.getenv("PORT", 8000))

# --- FastAPI App ---
app = FastAPI(title="MORA AI", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Simple SQLite for demo data ---
DB_PATH = "mora.db"
DB = sqlite3.connect(DB_PATH, check_same_thread=False)
DB.execute(
    """CREATE TABLE IF NOT EXISTS guest_sessions (
        id TEXT PRIMARY KEY,
        expires_at REAL
    )"""
)
DB.commit()

# --- Routes ---
@app.post("/guest/start")
async def start_guest_session():
    guest_id = str(uuid.uuid4())
    ttl_seconds = 1800  # 30 minutes
    expires_at = datetime.datetime.utcnow().timestamp() + ttl_seconds
    DB.execute("INSERT INTO guest_sessions (id, expires_at) VALUES (?, ?)", (guest_id, expires_at))
    DB.commit()

    logger.info(f"Guest session started: {guest_id}")
    return {
        "guest_token": guest_id,
        "ttl_seconds": ttl_seconds,
        "expires_at": expires_at,
    }

@app.get("/health")
def health():
    try:
        DB.execute("SELECT 1")
        return {"ok": True, "db": True, "time": datetime.datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error("Health check failed: %s", e)
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# --- Homepage ---
HOMEPAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MORA AI</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: linear-gradient(to bottom right, #000428, #004e92);
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }
    h1 {
      font-size: 4rem;
      margin-bottom: 1rem;
      color: #00bfff;
    }
    a.button {
      background: white;
      color: #004e92;
      padding: 12px 24px;
      border-radius: 8px;
      text-decoration: none;
      font-weight: bold;
      transition: background 0.3s;
    }
    a.button:hover {
      background: #00bfff;
      color: white;
    }
    #popupBackdrop {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.8);
      align-items: center;
      justify-content: center;
    }
    #popup {
      background: white;
      color: #004e92;
      padding: 20px 30px;
      border-radius: 12px;
      text-align: center;
      width: 300px;
    }
    #popup button {
      margin-top: 10px;
      padding: 8px 16px;
      background: #004e92;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <h1>MORA AI</h1>
  <a class="button" href="/docs">Open Docs</a>

  <div id="popupBackdrop">
    <div id="popup">
      <p>Your guest session has ended.</p>
      <button id="signInBtn">Sign in</button>
      <button id="cancelBtn">Cancel</button>
    </div>
  </div>

  <script>
    const GUEST_COOKIE = "guest";
    const GUEST_EXPIRES = "guest_expires";

    function setCookie(name, value, secs) {
      const d = new Date(Date.now() + secs * 1000);
      document.cookie = `${name}=${value}; path=/; expires=${d.toUTCString()}; SameSite=Lax`;
    }

    function getCookie(name) {
      const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
      return v ? v.pop() : null;
    }

    async function startGuestIfNeeded() {
      const token = getCookie(GUEST_COOKIE);
      if (!token) {
        try {
          const res = await fetch("/guest/start", { method: "POST" });
          if (res.ok) {
            const j = await res.json();
            setCookie(GUEST_COOKIE, j.guest_token, j.ttl_seconds);
            setCookie(GUEST_EXPIRES, j.expires_at, j.ttl_seconds);
            scheduleExpiryPopup(j.expires_at);
          }
        } catch (e) {
          console.error("Guest start failed", e);
        }
      } else {
        const expires = getCookie(GUEST_EXPIRES);
        if (expires) scheduleExpiryPopup(expires);
      }
    }

    function scheduleExpiryPopup(expireTs) {
      const now = Date.now() / 1000;
      const remain = expireTs - now;
      if (remain <= 0) {
        showPopup();
      } else {
        setTimeout(showPopup, remain * 1000);
      }
    }

    function showPopup() {
      document.getElementById("popupBackdrop").style.display = "flex";
    }

    document.getElementById("cancelBtn").addEventListener("click", () => {
      document.getElementById("popupBackdrop").style.display = "none";
    });

    document.getElementById("signInBtn").addEventListener("click", () => {
      alert("Sign-in feature coming soon!");
    });

    window.addEventListener("load", startGuestIfNeeded);
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def homepage():
    return HTMLResponse(content=HOMEPAGE_HTML, status_code=200)

# --- Run the server ---
if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Starting MORA AI on port {PORT}")
    uvicorn.run("server:app", host="0.0.0.0", port=PORT, reload=True)
