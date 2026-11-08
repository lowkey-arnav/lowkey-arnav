import os, json, urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

USER = os.environ.get("GH_USER", "lowkey-arnav")
TZ = ZoneInfo("Asia/Kolkata")
STEAM_HOURS = 24  # coffee steams if last push was within this many hours

def last_push():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/events/public?per_page=100",
        headers={"Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN','')}",
                 "Accept": "application/vnd.github+json"})
    try:
        events = json.load(urllib.request.urlopen(req, timeout=20))
    except Exception:
        return None
    for e in events:
        if e["type"] == "PushEvent" and e["actor"]["login"].lower() == USER.lower():
            return datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
    return None

now = datetime.now(timezone.utc)
lp = last_push()
if lp:
    hrs = (now - lp).total_seconds() / 3600
    steaming = hrs <= STEAM_HOURS
    if hrs < 1: ago = f"{int(hrs*60)}m ago"
    elif hrs < 48: ago = f"{int(hrs)}h ago"
    else: ago = f"{int(hrs//24)}d ago"
    status = f"last push {ago}"
else:
    steaming, status = False, "no recent pushes"

local = now.astimezone(TZ)
clock = local.strftime("%I:%M %p").lstrip("0")
date = local.strftime("%a, %d %b %Y")
state = "coding" if steaming else "idle"
dot = "#27c93f" if steaming else "#8b949e"
steam = """
<g class="steam" fill="none" stroke="#8b949e" stroke-width="3" stroke-linecap="round">
  <path class="s1" d="M468 150 q-8 -14 0 -28 q8 -14 0 -28"/>
  <path class="s2" d="M490 150 q-8 -14 0 -28 q8 -14 0 -28"/>
  <path class="s3" d="M512 150 q-8 -14 0 -28 q8 -14 0 -28"/>
</g>""" if steaming else ""

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="220" viewBox="0 0 600 220">
<style>
text {{ font-family: 'Courier New', monospace; fill: #c9d1d9; }}
.big {{ font-size: 44px; font-weight: bold; fill: #58a6ff; }}
.sm {{ font-size: 15px; }}
.dim {{ fill: #8b949e; }}
.steam path {{ opacity: 0; animation: rise 2.6s ease-in infinite; }}
.s2 {{ animation-delay: .8s !important; }} .s3 {{ animation-delay: 1.6s !important; }}
@keyframes rise {{ 0% {{ opacity: 0; transform: translateY(14px); }}
  30% {{ opacity: .8; }} 100% {{ opacity: 0; transform: translateY(-14px); }} }}
</style>
<rect width="600" height="220" rx="10" fill="#0d1117"/>
<circle cx="24" cy="22" r="6" fill="#ff5f56"/><circle cx="44" cy="22" r="6" fill="#ffbd2e"/><circle cx="64" cy="22" r="6" fill="#27c93f"/>
<text x="40" y="95" class="big">{clock}</text>
<text x="40" y="125" class="sm dim">{date} · IST</text>
<circle cx="46" cy="163" r="6" fill="{dot}"/>
<text x="62" y="168" class="sm">{state} · {status}</text>
<text x="40" y="198" class="sm dim">updated {local.strftime("%H:%M")} IST</text>
{steam}
<path d="M455 160 h70 v28 a24 24 0 0 1 -24 24 h-22 a24 24 0 0 1 -24 -24 z" fill="#30363d"/>
<path d="M525 168 h8 a10 10 0 0 1 0 20 h-8" fill="none" stroke="#30363d" stroke-width="6"/>
</svg>'''
open("live_desk.svg", "w", encoding="utf-8").write(svg)
print("wrote live_desk.svg:", state, status)
