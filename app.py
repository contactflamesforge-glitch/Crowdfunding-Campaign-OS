import os
import json
import requests
import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(page_title="Crowdfunding Campaign OS", page_icon="🚀", layout="wide")

jarvis_controls = components.declare_component("jarvis_controls", path=str(Path(__file__).parent / "jarvis_component"))


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800&family=Rajdhani:wght@400;500;600;700&display=swap');
:root{--neon:#35e8ff;--violet:#9b72ff;--mint:#54ffd0;--ink:#07111f}
.stApp{background:radial-gradient(ellipse at 12% 4%,rgba(23,91,143,.28),transparent 36%),radial-gradient(ellipse at 88% 18%,rgba(101,44,168,.2),transparent 34%),linear-gradient(145deg,#050b16 0%,#0a1425 52%,#080d1a 100%);color:#eaf6ff;font-family:'Rajdhani',sans-serif}
.block-container{padding-top:1.7rem;max-width:1450px}
h1,h2,h3{font-family:'Orbitron',sans-serif!important;letter-spacing:.04em;color:#eafaff!important}
p,label,.stMarkdown,.stCaption{color:#c7d9ee}
.hero{position:relative;overflow:hidden;padding:2rem;border:1px solid rgba(53,232,255,.42);border-radius:22px;background:linear-gradient(115deg,rgba(9,35,61,.96),rgba(34,22,73,.86));box-shadow:0 0 28px rgba(53,232,255,.13),inset 0 0 30px rgba(94,126,255,.08);margin-bottom:1.3rem;animation:rise .8s ease both}
.hero:after{content:'';position:absolute;inset:-80% -30%;background:linear-gradient(110deg,transparent 45%,rgba(53,232,255,.08) 50%,transparent 55%);animation:sweep 7s linear infinite}
.hero h1{font-size:clamp(1.5rem,4vw,2.4rem);text-shadow:0 0 18px rgba(53,232,255,.45);margin:0}
.hero p{color:#c5eaff;margin:.5rem 0 0}
@keyframes sweep{to{transform:translateX(45%)}}
@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes pulse{50%{box-shadow:0 0 22px rgba(53,232,255,.28)}}
section[data-testid="stSidebar"]{background:linear-gradient(180deg,#081629,#10112b 70%,#090f1c);border-right:1px solid rgba(53,232,255,.25)}
section[data-testid="stSidebar"] h1,section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3{font-family:'Orbitron',sans-serif!important}
.stButton>button,.stDownloadButton>button{border:1px solid rgba(53,232,255,.7);border-radius:12px;background:linear-gradient(110deg,#075b79,#47318c);color:#fff;font-weight:700;box-shadow:0 0 14px rgba(53,232,255,.12);transition:all .2s ease}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:#a4f8ff;transform:translateY(-2px);box-shadow:0 0 22px rgba(53,232,255,.3)}
.stTextInput input,.stTextArea textarea,.stSelectbox div[data-baseweb="select"]>div,.stDateInput input{background:#0d1b2e!important;color:#eaf6ff!important;border-color:#28516c!important;border-radius:10px!important}
div[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(12,36,59,.9),rgba(32,24,62,.8));padding:14px;border:1px solid rgba(53,232,255,.25);border-radius:14px;box-shadow:inset 0 0 20px rgba(53,232,255,.04)}
div[data-testid="stAlert"]{border-radius:13px}
.stRadio label{color:#d8f5ff!important}
hr{border-color:rgba(53,232,255,.18)}
.small-note{color:#9bb5cc;font-size:.9rem}
</style>
""", unsafe_allow_html=True)

if "campaign" not in st.session_state:
    st.session_state.campaign = {
        "name": "", "platform": "Kickstarter", "category": "Product / invention",
        "stage": "Idea stage", "goal": "", "currency": "USD", "location": "",
        "product": "", "problem": "", "audience": "", "benefit": "",
        "proof": "", "risks": "", "notes": ""
    }

PAGES = [
    "Overview", "Campaign Brief", "Campaign Analyzer", "Market & Audience",
    "Campaign Story", "Reward Strategy", "Pre-Launch Planner",
    "Marketing Studio", "Launch Manager", "Performance Analyst",
    "Backer Communications", "Campaign Library", "Command Centre", "Autopilot", "Backer Discovery", "Creative Studio", "Shopify Prospecting", "Holographic Command Deck", "Cloud Account", "Settings"
]


HOLO_PANELS = [
    ("Campaign Analyzer", "Assess campaign readiness and risks"),
    ("Market & Audience", "Explore audience and market fit"),
    ("Campaign Story", "Build the campaign narrative"),
    ("Reward Strategy", "Design practical reward tiers"),
    ("Marketing Studio", "Create campaign marketing assets"),
    ("Launch Manager", "Organize launch execution"),
    ("Performance Analyst", "Review campaign performance"),
    ("Backer Discovery", "Research potential backers"),
    ("Creative Studio", "Prepare creative concepts"),
    ("Shopify Prospecting", "Find Shopify stores and identify evidence-backed growth opportunities"),
    ("Command Centre", "View campaign operations")
]

def handle_jarvis_event(event):
    if not isinstance(event, dict):
        return
    target = None
    if event.get("type") == "voice":
        spoken = str(event.get("text", "")).strip().lower()
        routes = [
            (["overview", "home", "dashboard"], "Overview"),
            (["campaign brief", "project brief"], "Campaign Brief"),
            (["analyze my campaign", "campaign analyzer", "check my campaign"], "Campaign Analyzer"),
            (["market research", "audience research", "market and audience"], "Market & Audience"),
            (["campaign story", "write my story"], "Campaign Story"),
            (["reward strategy", "reward tiers"], "Reward Strategy"),
            (["pre-launch", "prelaunch"], "Pre-Launch Planner"),
            (["marketing studio", "create marketing", "marketing content"], "Marketing Studio"),
            (["launch manager", "launch plan", "launch schedule"], "Launch Manager"),
            (["performance analyst", "campaign performance", "analyze performance"], "Performance Analyst"),
            (["backer communication", "backer update"], "Backer Communications"),
            (["campaign library", "switch campaign", "save campaign"], "Campaign Library"),
            (["command centre", "command center", "metrics dashboard"], "Command Centre"),
            (["autopilot", "mission planner"], "Autopilot"),
            (["backer discovery", "find backers"], "Backer Discovery"),
            (["creative studio", "create visuals"], "Creative Studio"),
            (["shopify", "find stores", "store prospecting", "store leads"], "Shopify Prospecting"),
            (["holographic", "hologram", "command deck", "talk to jarvis", "jarvis chat"], "Holographic Command Deck"),
            (["settings"], "Settings")
        ]
        for phrases, page_name in routes:
            if any(phrase in spoken for phrase in phrases):
                target = page_name
                break
        if target is None:
            st.session_state["jarvis_chat_pending"] = str(event.get("text", "")).strip()
            st.session_state["workspace_page"] = "Holographic Command Deck"
            st.session_state["jarvis_reply"] = "Of course. Let us talk."
            return
    elif event.get("type") == "gesture":
        gesture = event.get("gesture")
        if st.session_state.get("workspace_page") == "Holographic Command Deck":
            if "holo_panel_index" not in st.session_state:
                st.session_state["holo_panel_index"] = 0
            idx = st.session_state["holo_panel_index"] % len(HOLO_PANELS)
            if gesture in ("Thumb_Up", "Pointing_Up"):
                idx = (idx - 1) % len(HOLO_PANELS)
                st.session_state["holo_panel_index"] = idx
                st.session_state["jarvis_reply"] = "Highlighted " + HOLO_PANELS[idx][0] + ". Make a victory sign to open it."
                return
            if gesture in ("Thumb_Down", "Pointing_Down"):
                idx = (idx + 1) % len(HOLO_PANELS)
                st.session_state["holo_panel_index"] = idx
                st.session_state["jarvis_reply"] = "Highlighted " + HOLO_PANELS[idx][0] + ". Make a victory sign to open it."
                return
            if gesture == "Victory":
                target = HOLO_PANELS[idx][0]
                st.session_state["jarvis_return_page"] = "Holographic Command Deck"
                st.session_state["workspace_page"] = target
                st.session_state["jarvis_reply"] = "Opening " + target + ". Make a fist or use Back to return."
                return
            if gesture == "Closed_Fist":
                st.session_state.pop("jarvis_return_page", None)
                st.session_state["workspace_page"] = "Overview"
                st.session_state["jarvis_reply"] = "Returning to Overview."
                return
        if gesture == "Closed_Fist":
            return_page = st.session_state.pop("jarvis_return_page", None)
            if return_page == "Holographic Command Deck":
                st.session_state["workspace_page"] = return_page
                st.session_state["jarvis_reply"] = "Returning to the Holographic Command Deck."
            else:
                st.session_state["jarvis_reply"] = "Back. Returning to Overview."
                st.session_state["jarvis_nav_action"] = "back"
            return
        if gesture == "ILoveYou":
            st.session_state.pop("jarvis_return_page", None)
            st.session_state["jarvis_reply"] = "JARVIS exiting gesture mode. Returning to Overview."
            st.session_state["jarvis_nav_action"] = "exit"
            st.session_state["workspace_page"] = "Overview"
            return
        if gesture == "Victory":
            st.session_state["jarvis_reply"] = "Selected. Opening the highlighted workspace."
            st.session_state["jarvis_nav_action"] = "select"
            return
        if gesture in ("Thumb_Up", "Pointing_Up"):
            st.session_state["jarvis_nav_action"] = "up"
            return
        if gesture in ("Thumb_Down", "Pointing_Down"):
            st.session_state["jarvis_nav_action"] = "down"
            return
    if target:
        if target in [panel[0] for panel in HOLO_PANELS]:
            if st.session_state.get("workspace_page") == "Holographic Command Deck":
                st.session_state["jarvis_return_page"] = "Holographic Command Deck"
        else:
            st.session_state.pop("jarvis_return_page", None)
        st.session_state["workspace_page"] = target
        st.session_state["jarvis_reply"] = f"Opening {target}."

C = st.session_state.campaign
st.sidebar.title("🚀 Campaign OS")
# J.A.R.V.I.S. sits in the main workspace so the camera preview can use the full screen width.
st.subheader("J.A.R.V.I.S.  //  Voice & Gesture Command Deck")
jarvis_event = jarvis_controls(reply=st.session_state.get("jarvis_reply", ""), key="jarvis_control", default=None)
if jarvis_event and jarvis_event.get("at") != st.session_state.get("jarvis_last_event_at"):
    st.session_state["jarvis_last_event_at"] = jarvis_event.get("at")
    handle_jarvis_event(jarvis_event)
if "workspace_page" not in st.session_state:
    st.session_state["workspace_page"] = "Overview"
if "jarvis_page_index" not in st.session_state:
    st.session_state["jarvis_page_index"] = PAGES.index(st.session_state["workspace_page"])
nav_action = st.session_state.pop("jarvis_nav_action", None)
if nav_action == "up":
    st.session_state["jarvis_page_index"] = (st.session_state["jarvis_page_index"] - 1) % len(PAGES)
elif nav_action == "down":
    st.session_state["jarvis_page_index"] = (st.session_state["jarvis_page_index"] + 1) % len(PAGES)
elif nav_action == "select":
    st.session_state["workspace_page"] = PAGES[st.session_state["jarvis_page_index"]]
elif nav_action == "back":
    st.session_state["jarvis_page_index"] = PAGES.index("Overview")
    st.session_state["workspace_page"] = "Overview"
if nav_action in ("up", "down"):
    st.session_state["workspace_page"] = PAGES[st.session_state["jarvis_page_index"]]
if st.session_state.get("workspace_page") in PAGES and not nav_action:
    st.session_state["jarvis_page_index"] = PAGES.index(st.session_state["workspace_page"])
pending_page = st.session_state.pop("pending_workspace_page", None)
if pending_page in PAGES:
    st.session_state["workspace_page"] = pending_page
    st.session_state["jarvis_page_index"] = PAGES.index(pending_page)

page = st.sidebar.radio("Workspace", PAGES, key="workspace_page", index=st.session_state["jarvis_page_index"])
st.session_state["jarvis_page_index"] = PAGES.index(page)
if page != "Holographic Command Deck" and st.session_state.get("jarvis_return_page") == "Holographic Command Deck":
    back_col, _ = st.columns([2, 5])
    if back_col.button("← Back to J.A.R.V.I.S. Command Deck", key="jarvis_back_to_deck", use_container_width=True):
        st.session_state.pop("jarvis_return_page", None)
        st.session_state["pending_workspace_page"] = "Holographic Command Deck"
        st.session_state["jarvis_reply"] = "Returning to the command deck."
        st.rerun()
st.sidebar.caption("Plan carefully. Create honestly. Launch with evidence.")

def api_key():
    try:
        saved = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        saved = ""
    return saved or os.getenv("GEMINI_API_KEY", "") or st.session_state.get("gemini_key", "")

def brief_text():
    labels = {
        "name":"Campaign name", "platform":"Platform", "category":"Category",
        "stage":"Stage", "goal":"Funding goal", "currency":"Currency",
        "location":"Creator location", "product":"What is being offered",
        "problem":"Problem", "audience":"Intended audience",
        "benefit":"Main benefit", "proof":"Evidence / proof available",
        "risks":"Known risks or constraints", "notes":"Additional context"
    }
    return "\n".join(f"{labels[k]}: {v}" for k,v in C.items() if v)

def ask_ai(task, extra="", temperature=0.65, web_search=False):
    key = api_key()
    if not key:
        st.error("Add your Gemini API key in Settings before generating.")
        return
    prompt = f"""You are Crowdfunding Campaign OS, a rigorous crowdfunding strategist and campaign operator.
Your job is to help plan, create, launch, and improve legitimate crowdfunding campaigns.

NON-NEGOTIABLE RULES:
- Never invent market research, statistics, competitor findings, testimonials, customer quotes, traction, product capabilities, costs, shipping dates, or proof.
- Separate supplied facts, reasonable hypotheses, and items that need validation.
- If information is missing, state the gap and ask for the most important missing input rather than pretending.
- Avoid generic marketing clichés, exaggerated promises, fake urgency, and guaranteed funding claims.
- Tailor recommendations to the campaign, platform, audience, stage, goal, and constraints.
- Explain why each important recommendation matters.
- Be candid about weaknesses, risks, and feasibility.
- Use clear, practical language and actionable steps.
- Respect platform rules and applicable consumer, privacy, and advertising laws.

CAMPAIGN BRIEF:
{brief_text()}

TASK:
{task}

ADDITIONAL INSTRUCTIONS / MATERIAL:
{extra}

Return a well-structured, specific, practical answer. Mark unverified claims clearly."""
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"
    try:
        response = requests.post(
            url + "?key=" + key,
            headers={"Content-Type": "application/json"},
            json={"contents":[{"parts":[{"text":prompt}]}],
                  "tools":[{"google_search":{}}] if web_search else [],
                  "generationConfig":{"temperature":temperature, "maxOutputTokens":6000}},
            timeout=90
        )
        if response.status_code != 200:
            st.error(f"Gemini returned an error ({response.status_code}). Check the API key, model access, and quota.")
            with st.expander("Technical details"):
                st.code(response.text[:2500])
            return
        data = response.json()
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(part.get("text", "") for part in parts if "text" in part)
        st.markdown(text)
        grounding = data["candidates"][0].get("groundingMetadata", {})
        sources = grounding.get("groundingChunks", [])
        if sources:
            st.subheader("Web sources used")
            for source in sources:
                web = source.get("web", {})
                uri = web.get("uri", "")
                title = web.get("title", uri)
                if uri:
                    st.markdown(f"- [{title}]({uri})")
        st.download_button("Download this result", text, file_name="campaign-os-output.txt")
    except requests.exceptions.Timeout:
        st.error("The request timed out. Try again with a shorter task.")
    except Exception as e:
        st.error(f"Could not generate a response: {e}")


def supabase_config():
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_PUBLISHABLE_KEY", "")
    except Exception:
        url, key = "", ""
    return (url or os.getenv("SUPABASE_URL", "")).rstrip("/"), key or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")

def supabase_request(method, path, token=None, params=None, payload=None, prefer=None):
    base, public_key = supabase_config()
    if not base or not public_key:
        raise RuntimeError("Supabase is not configured. Add SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY to Streamlit Secrets.")
    headers = {"apikey": public_key, "Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    else:
        headers["Authorization"] = "Bearer " + public_key
    if prefer:
        headers["Prefer"] = prefer
    response = requests.request(method, base + path, headers=headers, params=params, json=payload, timeout=30)
    if not response.ok:
        try:
            detail = response.json().get("message") or response.json().get("msg") or response.text
        except Exception:
            detail = response.text
        raise RuntimeError(f"Supabase error ({response.status_code}): {detail}")
    if response.status_code == 204 or not response.text:
        return None
    return response.json()

def cloud_user():
    return st.session_state.get("supabase_user")

def cloud_token():
    return st.session_state.get("supabase_access_token")

def cloud_save_campaign(name):
    user = cloud_user()
    token = cloud_token()
    if not user or not token:
        raise RuntimeError("Sign in to your cloud account first.")
    payload = {"user_id": user["id"], "name": name, "campaign_data": dict(st.session_state.campaign),
               "metrics": dict(st.session_state.campaign_metrics), "action_tasks": list(st.session_state.action_tasks)}
    return supabase_request("POST", "/rest/v1/campaigns", token=token,
        params={"on_conflict":"user_id,name"}, payload=payload,
        prefer="resolution=merge-duplicates,return=representation")

def cloud_list_campaigns():
    user = cloud_user()
    return supabase_request("GET", "/rest/v1/campaigns", token=cloud_token(),
        params={"select":"id,name,updated_at,campaign_data,metrics,action_tasks",
                "user_id":f"eq.{user['id']}", "order":"updated_at.desc"})

def cloud_open_campaign(record):
    st.session_state.campaign = record.get("campaign_data") or {}
    st.session_state.campaign_metrics = record.get("metrics") or {"raised":0.0,"backers":0,"visits":0,"email_signups":0}
    st.session_state.action_tasks = record.get("action_tasks") or []
    st.rerun()


def jarvis_chat_response(user_text):
    """Return a conversational Gemini response grounded in the current campaign brief."""
    key = api_key()
    if not key:
        return "I can chat once the Gemini API key is configured. Open Settings and add your key; please never share it in chat."
    history = st.session_state.setdefault("jarvis_chat_history", [])
    recent = history[:-1][-12:]
    conversation = []
    for item in recent:
        role = "user" if item.get("role") == "user" else "model"
        conversation.append({"role": role, "parts": [{"text": item.get("content", "")}]})
    system_context = (
        "You are J.A.R.V.I.S., a warm, intelligent, calm conversational AI assistant inside a "
        "Crowdfunding Campaign OS. Speak naturally like a helpful person, not like a rigid command parser. "
        "Answer general questions as well as crowdfunding, marketing, business, and campaign questions. "
        "Use the supplied campaign facts when relevant, but do not pretend to know facts that are not supplied. "
        "Never invent metrics, research, testimonials, campaign progress, or actions. "
        "You may explain how to do something, but do not claim to have changed app data or performed external actions "
        "unless the app explicitly confirms that action. Ask one concise clarifying question when necessary. "
        "Keep ordinary conversation friendly and concise; provide more detail when asked.\n\n"
        "CURRENT CAMPAIGN BRIEF:\n" + brief_text()
    )
    contents = [{"role": "user", "parts": [{"text": system_context + "\n\nUser says: " + user_text}]}]
    contents = conversation + contents
    # Try the faster Flash-Lite model first for snappier chat; use Flash as backup.
    models = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
    try:
        last_status = None
        last_detail = ""
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            response = requests.post(
                url + "?key=" + key,
                headers={"Content-Type": "application/json"},
                json={"contents": contents, "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1800}},
                timeout=60
            )
            if response.status_code == 200:
                data = response.json()
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                answer = "".join(part.get("text", "") for part in parts if "text" in part).strip()
                if answer:
                    return answer
                last_status, last_detail = response.status_code, "The model returned an empty response."
                continue
            last_status = response.status_code
            try:
                error_data = response.json().get("error", {})
                last_detail = error_data.get("message", response.text[:400])
            except Exception:
                last_detail = response.text[:400]
            # Try the lightweight backup model for temporary service errors or model access issues.
            if response.status_code not in (404, 429, 500, 502, 503, 504):
                break
        return f"J.A.R.V.I.S. could not get a response from Gemini (HTTP {last_status}). {last_detail[:350]}"
    except requests.exceptions.Timeout:
        return "Gemini took too long to respond. Please try again shortly."
    except Exception as exc:
        return f"J.A.R.V.I.S. hit a connection error: {str(exc)[:250]}"


def page_header(title, subtitle):
    st.title(title)
    st.caption(subtitle)


# Expanded campaign operations workspaces
if "campaigns" not in st.session_state:
    st.session_state.campaigns = {}
if "campaign_metrics" not in st.session_state:
    st.session_state.campaign_metrics = {"raised": 0.0, "backers": 0, "visits": 0, "email_signups": 0}
if "action_tasks" not in st.session_state:
    st.session_state.action_tasks = []

if page == "Campaign Library":
    page_header("Campaign Library", "Manage separate campaign workspaces and transfer backups between devices.")
    if cloud_user() and cloud_token():
        st.success("Cloud storage connected · " + cloud_user().get("email", "signed in"))
        cloud_name = st.text_input("Cloud campaign name", C.get("name") or "Untitled campaign", key="cloud_save_name")
        c1, c2 = st.columns(2)
        if c1.button("Save current campaign to cloud", type="primary"):
            try:
                cloud_save_campaign(cloud_name.strip() or "Untitled campaign")
                st.success("Campaign saved to your private cloud database.")
            except Exception as exc:
                st.error(str(exc))
        if c2.button("Refresh cloud campaigns"):
            try:
                st.session_state.cloud_campaign_records = cloud_list_campaigns()
            except Exception as exc:
                st.error(str(exc))
        if "cloud_campaign_records" not in st.session_state:
            try:
                st.session_state.cloud_campaign_records = cloud_list_campaigns()
            except Exception as exc:
                st.session_state.cloud_campaign_records = []
                st.error(str(exc))
        records = st.session_state.get("cloud_campaign_records", [])
        if records:
            labels = {f"{r.get('name','Untitled')} · {str(r.get('updated_at',''))[:10]}":r for r in records}
            selected_label = st.selectbox("Your cloud campaigns", list(labels))
            a1, a2 = st.columns(2)
            if a1.button("Open selected cloud campaign"):
                cloud_open_campaign(labels[selected_label])
            if a2.button("Delete selected cloud campaign"):
                try:
                    rec = labels[selected_label]
                    supabase_request("DELETE", "/rest/v1/campaigns", token=cloud_token(),
                        params={"id":f"eq.{rec['id']}", "user_id":f"eq.{cloud_user()['id']}"})
                    st.session_state.cloud_campaign_records = [r for r in records if r.get("id") != rec.get("id")]
                    st.success("Cloud campaign deleted.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        else:
            st.info("No campaigns saved in the cloud yet.")
    else:
        st.warning("Cloud storage is not connected. Open Cloud Account, add the two Supabase settings, then create an account or sign in.")
    left, right = st.columns(2)
    with left:
        st.subheader("Save current campaign")
        save_name = st.text_input("Library name", C.get("name") or "Untitled campaign")
        if st.button("Save campaign"):
            if save_name.strip():
                snap = dict(C)
                snap["name"] = save_name.strip()
                st.session_state.campaigns[save_name.strip()] = snap
                st.success("Campaign saved in this session.")
    with right:
        st.subheader("Open a campaign")
        names = list(st.session_state.campaigns)
        if names:
            selected = st.selectbox("Saved campaigns", names)
            if st.button("Open campaign"):
                st.session_state.campaign = dict(st.session_state.campaigns[selected])
                st.rerun()
            if st.button("Delete campaign"):
                del st.session_state.campaigns[selected]
                st.rerun()
        else:
            st.info("No campaigns saved yet.")
    backup = json.dumps({"campaigns":st.session_state.campaigns,"current_campaign":C}, indent=2)
    st.download_button("Export campaign backup", backup, "campaign-os-backup.json", "application/json")
    upload = st.file_uploader("Import campaign backup", type=["json"])
    if upload and st.button("Import backup"):
        try:
            data = json.loads(upload.getvalue().decode("utf-8"))
            if "campaigns" in data:
                st.session_state.campaigns.update(data.get("campaigns", {}))
                if isinstance(data.get("current_campaign"), dict):
                    st.session_state.campaign = data["current_campaign"]
            else:
                st.session_state.campaign = data
            st.success("Import complete.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not import backup: {exc}")

elif page == "Command Centre":
    page_header("Campaign Command Centre", "Track funding, traffic, backers and conversion using your actual numbers.")
    m = st.session_state.campaign_metrics
    a,b,c,d = st.columns(4)
    m["raised"] = a.number_input("Amount raised", min_value=0.0, value=float(m["raised"]), step=10.0)
    m["backers"] = b.number_input("Backers", min_value=0, value=int(m["backers"]))
    m["visits"] = c.number_input("Page visits", min_value=0, value=int(m["visits"]))
    m["email_signups"] = d.number_input("Email signups", min_value=0, value=int(m["email_signups"]))
    try:
        goal = float(str(C.get("goal","0")).replace(",","").replace("$",""))
    except Exception:
        goal = 0.0
    progress = m["raised"] / goal * 100 if goal > 0 else 0
    conversion = m["backers"] / m["visits"] * 100 if m["visits"] else 0
    signup_rate = m["email_signups"] / m["visits"] * 100 if m["visits"] else 0
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Funding progress", f"{progress:.1f}%" if goal else "Set numeric goal")
    k2.metric("Raised", f"{m['raised']:,.2f} {C.get('currency','USD')}")
    k3.metric("Backer conversion", f"{conversion:.2f}%")
    k4.metric("Email signup rate", f"{signup_rate:.2f}%")
    if goal:
        st.progress(min(max(progress/100,0.0),1.0))
    st.caption("These are current snapshots, not historical trends. Keep dated records separately for trend analysis.")
    if st.button("Ask J.A.R.V.I.S. to diagnose metrics"):
        ask_ai("Diagnose the funnel using only supplied numbers. Calculate rates, identify bottlenecks, explain uncertainty, and propose three measurable tests.", json.dumps({"goal":goal,**m}))

elif page == "Autopilot":
    page_header("Autopilot Mission Planner", "Convert a campaign objective into sequenced tasks with owners and completion criteria.")
    objective = st.text_area("Mission objective", height=90)
    horizon = st.selectbox("Planning horizon", ["7 days","14 days","30 days","45 days","60 days","90 days"])
    capacity = st.text_area("Team, available time, budget, assets and constraints", height=100)
    if st.button("Generate mission plan", type="primary"):
        ask_ai(f"Create a {horizon} execution plan for this objective: {objective}. Include priorities, dependencies, owner roles, milestones, measurable done criteria, risks, weekly reviews and first 48-hour actions. Never claim actions were completed.", capacity)
    st.divider()
    st.subheader("Action tracker")
    with st.form("add_action"):
        title = st.text_input("Action item")
        owner = st.text_input("Owner")
        due = st.date_input("Due date")
        add = st.form_submit_button("Add action")
    if add and title.strip():
        st.session_state.action_tasks.append({"task":title.strip(),"owner":owner,"due":str(due),"done":False})
        st.rerun()
    for i, task in enumerate(st.session_state.action_tasks):
        x,y = st.columns([5,1])
        x.write(f"{'Done' if task['done'] else 'To do'} — {task['task']} · {task['owner']} · {task['due']}")
        if y.button("Toggle", key=f"toggle_{i}"):
            task["done"] = not task["done"]
            st.rerun()
    if st.session_state.action_tasks:
        st.download_button("Export actions", json.dumps(st.session_state.action_tasks,indent=2), "campaign-actions.json")

elif page == "Backer Discovery":
    page_header("Backer Discovery Engine", "Identify relevant communities, creators, partners and media without inventing contacts.")
    geography = st.text_input("Target geography")
    audience = st.text_area("Ideal backer profile", C.get("audience",""), height=90)
    value = st.text_area("Why would a community or partner care?", C.get("benefit",""), height=80)
    if st.button("Build discovery plan", type="primary"):
        ask_ai("Build a backer discovery plan: community types, creator categories, partner types, search phrases, qualification criteria, personalization fields, a 2-week ethical outreach process, and lead tracker columns. Do not invent real names, emails, audience sizes or partnerships.", f"Geography: {geography}\nAudience: {audience}\nPartner value: {value}", web_search=True)

elif page == "Creative Studio":
    page_header("Creative Studio", "Create production briefs and image/video concepts from verified campaign facts.")
    asset = st.selectbox("Asset type", ["Hero campaign image","Social media graphics","Paid ad concepts","Campaign video storyboard","Product explainer","Launch banner"])
    channel = st.selectbox("Channel", ["Kickstarter / Indiegogo","Instagram","Facebook","TikTok","YouTube","Email / press"])
    notes = st.text_area("Brand style, colors, available images, exact text and visual restrictions", height=120)
    if st.button("Generate creative brief", type="primary"):
        ask_ai(f"Create a production-ready creative brief for {asset} on {channel}. Include composition, copy hierarchy, visual direction, accessibility, variants to test and image-generation prompts. Do not show unverified product features, endorsements or results.", notes)

elif page == "Holographic Command Deck":
    page_header("J.A.R.V.I.S. // HOLOGRAPHIC COMMAND DECK", "Conversational AI and a hologram-inspired interactive command environment.")
    st.markdown("""
    <style>
    .holo-stage{position:relative;overflow:hidden;border:1px solid rgba(65,229,255,.55);border-radius:22px;padding:22px 18px;background:radial-gradient(circle at 50% 45%,rgba(19,179,222,.18),transparent 31%),linear-gradient(145deg,#06172a,#10112b 72%,#061522);box-shadow:0 0 30px rgba(48,218,255,.13),inset 0 0 35px rgba(91,103,255,.10);min-height:210px;text-align:center}
    .holo-core{width:112px;height:112px;border:2px solid #62efff;border-radius:50%;margin:4px auto 13px;display:grid;place-items:center;position:relative;color:#bffaff;font:700 13px Orbitron,Arial;letter-spacing:2px;text-shadow:0 0 12px #36eaff;box-shadow:0 0 22px rgba(53,232,255,.45),inset 0 0 20px rgba(53,232,255,.2);animation:holoPulse 3s ease-in-out infinite}
    .holo-core:before,.holo-core:after{content:"";position:absolute;inset:-12px;border:1px solid rgba(75,229,255,.55);border-radius:50%;transform:rotateX(68deg);animation:holoSpin 8s linear infinite}
    .holo-core:after{inset:-22px;transform:rotateX(68deg) rotateZ(60deg);animation-direction:reverse}
    .holo-label{color:#8eeeff;font:11px Orbitron,Arial;letter-spacing:2px}
    .holo-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:14px}
    .holo-tile{border:1px solid rgba(63,217,255,.35);border-radius:12px;padding:11px 5px;background:linear-gradient(130deg,rgba(8,67,91,.65),rgba(43,31,91,.55));color:#d8faff;font:10px Orbitron,Arial;letter-spacing:1px}
    @keyframes holoPulse{50%{box-shadow:0 0 38px rgba(53,232,255,.6),inset 0 0 26px rgba(53,232,255,.3);transform:scale(1.025)}}
    @keyframes holoSpin{to{transform:rotateX(68deg) rotateZ(360deg)}}
    @media(max-width:600px){.holo-grid{grid-template-columns:repeat(3,1fr)}.holo-stage{padding:17px 10px}}
    </style>
    <div class="holo-stage">
      <div class="holo-core">J.A.R.V.I.S.</div>
      <div class="holo-label">HOLOGRAPHIC SYSTEM // ONLINE</div>
      <div class="holo-grid">
        <div class="holo-tile">◉ CONVERSATION</div><div class="holo-tile">⌖ CAMPAIGN DATA</div><div class="holo-tile">✧ GESTURE LINK</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("The hologram is a screen-based visual interface. Hand tracking uses your camera when you activate it in the J.A.R.V.I.S. control panel above.")

    st.subheader("Interactive holographic panels")
    if "holo_panel_index" not in st.session_state:
        st.session_state["holo_panel_index"] = 0
    selected_index = st.session_state["holo_panel_index"] % len(HOLO_PANELS)
    st.caption("Browse with Previous/Next, select any panel below, then open it. Camera gestures are optional; every action has a touch or click alternative.")
    nav_a, nav_b, nav_c = st.columns([1, 2, 1])
    if nav_a.button("← Previous", use_container_width=True, help="Focus the previous holographic panel"):
        st.session_state["holo_panel_index"] = (selected_index - 1) % len(HOLO_PANELS)
        st.rerun()
    with nav_b:
        panel_name, panel_description = HOLO_PANELS[selected_index]
        st.markdown(
            f'<div role="status" aria-live="polite" style="text-align:center;padding:12px;border:1px solid #35e8ff;border-radius:14px;background:linear-gradient(120deg,rgba(7,75,100,.55),rgba(57,36,105,.55));box-shadow:0 0 18px rgba(53,232,255,.22)"><div style="font-size:10px;letter-spacing:2px;color:#8eeeff">FOCUSED HOLOGRAM</div><div style="font-family:Orbitron,Arial;color:#eafaff;font-size:18px;margin:7px 0">{panel_name}</div><div style="color:#b8d8ec;font-size:13px">{panel_description}</div><div style="font-size:10px;color:#8eeeff;margin-top:7px">PANEL {selected_index + 1} / {len(HOLO_PANELS)}</div></div>',
            unsafe_allow_html=True
        )
    if nav_c.button("Next →", use_container_width=True, help="Focus the next holographic panel"):
        st.session_state["holo_panel_index"] = (selected_index + 1) % len(HOLO_PANELS)
        st.rerun()

    st.markdown("#### Select a panel")
    panel_columns = st.columns(2)
    for panel_number, (panel_title, panel_desc) in enumerate(HOLO_PANELS):
        with panel_columns[panel_number % 2]:
            with st.container(border=True):
                focused = panel_number == selected_index
                if st.button(
                    ("✦ " if focused else "◈ ") + panel_title,
                    key="holo_select_" + str(panel_number),
                    type="primary" if focused else "secondary",
                    help=panel_desc,
                    use_container_width=True
                ):
                    st.session_state["holo_panel_index"] = panel_number
                    st.rerun()
                st.caption(panel_desc)
                if focused:
                    st.caption("✦ FOCUSED · READY TO OPEN")

    open_col, home_col = st.columns([2, 1])
    if open_col.button("✦ Open highlighted panel", type="primary", use_container_width=True):
        st.session_state["jarvis_return_page"] = "Holographic Command Deck"
        st.session_state["pending_workspace_page"] = panel_name
        st.session_state["jarvis_reply"] = "Opening " + panel_name + ". Make a fist or use Back to return."
        st.rerun()
    if home_col.button("↩ Return to Overview", use_container_width=True):
        st.session_state.pop("jarvis_return_page", None)
        st.session_state["pending_workspace_page"] = "Overview"
        st.session_state["jarvis_reply"] = "Returning to Overview."
        st.rerun()

    if "jarvis_chat_history" not in st.session_state:
        st.session_state.jarvis_chat_history = []
    pending = st.session_state.pop("jarvis_chat_pending", "")
    if pending:
        st.session_state.jarvis_chat_history.append({"role":"user","content":pending})
        with st.spinner("J.A.R.V.I.S. is thinking..."):
            answer = jarvis_chat_response(pending)
        st.session_state.jarvis_chat_history.append({"role":"assistant","content":answer})
        st.session_state["jarvis_reply"] = answer
    st.info("J.A.R.V.I.S. voice mode is active. Responses are spoken aloud; the text transcript is hidden.")
    prompt = st.chat_input("Talk naturally to J.A.R.V.I.S. ...")
    if prompt:
        st.session_state.jarvis_chat_history.append({"role":"user","content":prompt})
        with st.spinner("J.A.R.V.I.S. is thinking..."):
            answer = jarvis_chat_response(prompt)
        st.session_state.jarvis_chat_history.append({"role":"assistant","content":answer})
        st.session_state["jarvis_reply"] = answer[:220]
        st.rerun()
    c1, c2 = st.columns([1,3])
    if c1.button("Clear conversation"):
        st.session_state.jarvis_chat_history = []
        st.rerun()
    c2.caption("Conversation history stays in this app session and is cleared when the session resets. Voice replies use your browser's speech synthesis.")

elif page == "Overview":


    st.markdown('<div class="hero"><h1>🚀 Crowdfunding Campaign OS</h1><p>Your workspace for turning a campaign idea into a researched, prepared, and well-managed launch.</p></div>', unsafe_allow_html=True)
    st.subheader("Campaign workspace")
    a,b,c = st.columns(3)
    a.metric("Campaign", C["name"] or "Not set")
    b.metric("Platform", C["platform"])
    c.metric("Stage", C["stage"])
    st.info("Start by completing your Campaign Brief. The other workspaces use it as their context.")
    st.subheader("Your campaign workflow")
    cols = st.columns(4)
    for col, title, desc in zip(cols, ["1. Assess","2. Build","3. Prepare","4. Improve"],
        ["Analyze readiness and risks","Create story and reward tiers","Build audience and launch plan","Review results and optimize"]):
        with col:
            st.markdown(f"**{title}**")
            st.write(desc)
    st.warning("AI outputs are working drafts, not verified market research, legal advice, financial advice, or a guarantee of campaign success.")

elif page == "Campaign Brief":
    page_header("Campaign Brief", "Add the facts that every campaign tool should work from.")
    with st.form("brief_form"):
        C["name"] = st.text_input("Campaign / project name", C["name"])
        x,y = st.columns(2)
        C["platform"] = x.selectbox("Platform", ["Kickstarter","Indiegogo","GoFundMe","Crowdfunder","Other / not decided"], index=["Kickstarter","Indiegogo","GoFundMe","Crowdfunder","Other / not decided"].index(C["platform"]))
        C["category"] = y.selectbox("Campaign category", ["Product / invention","Creative project","Community / nonprofit","Personal cause","Business / startup","Other"], index=["Product / invention","Creative project","Community / nonprofit","Personal cause","Business / startup","Other"].index(C["category"]))
        x,y = st.columns(2)
        C["stage"] = x.selectbox("Current stage", ["Idea stage","Validating demand","Prototype / preparation","Pre-launch audience building","Live campaign","Post-campaign"], index=["Idea stage","Validating demand","Prototype / preparation","Pre-launch audience building","Live campaign","Post-campaign"].index(C["stage"]))
        C["goal"] = y.text_input("Funding goal (amount)", C["goal"])
        x,y = st.columns(2)
        C["currency"] = x.selectbox("Currency", ["USD","NGN","GBP","EUR","CAD","AUD","Other"], index=["USD","NGN","GBP","EUR","CAD","AUD","Other"].index(C["currency"]))
        C["location"] = y.text_input("Creator / delivery location", C["location"])
        C["product"] = st.text_area("What exactly are you offering?", C["product"], height=90)
        C["problem"] = st.text_area("What problem, need, or purpose does it address?", C["problem"], height=80)
        C["audience"] = st.text_area("Who is most likely to back it?", C["audience"], height=80)
        C["benefit"] = st.text_area("What is the main value or outcome for backers?", C["benefit"], height=80)
        C["proof"] = st.text_area("What evidence do you already have? (prototype, tests, supporters, quotes with permission, etc.)", C["proof"], height=80)
        C["risks"] = st.text_area("Known risks, limits, costs, delivery or regulatory constraints", C["risks"], height=80)
        C["notes"] = st.text_area("Other important context", C["notes"], height=80)
        submitted = st.form_submit_button("Save campaign brief", type="primary")
    if submitted:
        st.success("Campaign brief saved for this session.")

elif page == "Campaign Analyzer":
    page_header("Campaign Analyzer", "Find strengths, weaknesses, missing evidence, and readiness gaps.")
    st.write("The analyzer should challenge the campaign, not simply praise it.")
    extra = st.text_area("Add any extra information (optional)", height=100)
    if st.button("Analyze campaign", type="primary"):
        ask_ai("Evaluate campaign readiness. Provide: executive assessment; strongest elements; critical weaknesses; evidence gaps; audience and offer clarity; goal and delivery risks; platform-fit questions; a prioritized 10-step action plan; and a readiness verdict with reasons.", extra)

elif page == "Market & Audience":
    page_header("Market & Audience Intelligence", "Build a useful research plan and understand potential backers.")
    st.info("Live Google Search grounding is enabled for this workspace. Check every surfaced source for credibility, date and relevance. Paste research, links' contents, or interview notes for evidence-based analysis.")
    research = st.text_area("Paste research, competitor notes, customer interviews, survey results, or source excerpts", height=180)
    if st.button("Research market and audience", type="primary"):
        ask_ai("Research the campaign category and audience using Google Search grounding. Find relevant competitors, alternatives, audience communities, current category context and potential partners. Cite source URLs in the response. Separate verified findings from hypotheses, note dates and geography, and do not infer market size without reliable evidence.", research, web_search=True)

elif page == "Campaign Story":
    page_header("Campaign Story Builder", "Create a clear, credible story that helps the right people understand the campaign.")
    style = st.selectbox("Writing direction", ["Warm and personal","Founder-led and transparent","Practical and product-focused","Community-led","Creative and emotional"])
    extra = st.text_area("Specific story details, founder background, milestones, or tone notes", height=130)
    if st.button("Create campaign story", type="primary"):
        ask_ai(f"Create a campaign headline, short pitch, full campaign page draft, section headings, FAQ, and a concise video script. Writing direction: {style}. Do not invent personal details, product facts, or proof.", extra)

elif page == "Reward Strategy":
    page_header("Reward Strategy", "Design reward tiers that are attractive, understandable, and deliverable.")
    extra = st.text_area("Known production costs, shipping regions, estimated quantities, price limits, reward ideas, and fulfilment constraints", height=160)
    if st.button("Build reward strategy", type="primary"):
        ask_ai("Recommend a reward-tier architecture. Include tier name, proposed price, what is included, intended backer, rationale, quantity limits if justified, and fulfilment risks. Do not invent cost data. Clearly flag all prices as hypotheses until costs, fees, taxes, and shipping are validated.", extra)

elif page == "Pre-Launch Planner":
    page_header("Pre-Launch Planner", "Prepare demand, build a permission-based audience, and reduce launch-day uncertainty.")
    duration = st.selectbox("Planning horizon", ["2 weeks","30 days","45 days","60 days","90 days"])
    extra = st.text_area("Existing audience size, email list, social channels, partners, budget, team capacity, and launch date", height=140)
    if st.button("Create pre-launch plan", type="primary"):
        ask_ai(f"Create a realistic {duration} pre-launch plan with weekly milestones, daily/weekly actions, audience-building methods, validation experiments, owner roles, metrics, and launch-readiness checkpoints. Do not assume an audience or budget that was not supplied.", extra)

elif page == "Marketing Studio":
    page_header("Marketing Studio", "Create campaign-specific marketing assets without generic hype.")
    channel = st.selectbox("Asset type", ["Email sequence","Social media content","Creator / influencer outreach","Press pitch","Paid ad concepts","Launch announcement","Campaign update"])
    audience = st.text_input("Who is this particular asset for?")
    extra = st.text_area("Offer, call to action, platform limits, proof, and any source material", height=130)
    if st.button("Generate marketing assets", type="primary"):
        ask_ai(f"Create {channel} for this campaign. Target audience: {audience or 'Use the best-supported audience from the brief'}. Provide several distinct angles where appropriate, natural language, and one clear call to action. Do not fabricate proof or urgency.", extra)

elif page == "Launch Manager":
    page_header("Launch Manager", "Turn the strategy into an executable launch schedule.")
    date = st.date_input("Target launch date")
    team = st.text_area("Team members, responsibilities, available hours, and launch constraints", height=100)
    if st.button("Build launch schedule", type="primary"):
        ask_ai(f"Create a launch runbook leading up to and including {date}. Include timeline, task, owner role, dependency, completion criteria, launch-day checklist, contingency actions, and daily metrics. Make the plan realistic for the supplied team.", team)

elif page == "Performance Analyst":
    page_header("Performance Analyst", "Understand campaign performance and decide what to change.")
    metrics = st.text_area("Paste campaign metrics (goal, raised, backers, visits, conversion rate, traffic sources, email performance, dates)", height=180)
    context = st.text_area("What changed recently? Any campaign updates, promotions, or external events?", height=80)
    if st.button("Analyze performance", type="primary"):
        ask_ai("Analyze the campaign metrics supplied. Calculate only what can be calculated from the data. Identify trends, bottlenecks, plausible explanations (clearly labeled), missing metrics, and prioritized experiments. Do not claim causation from correlation.", metrics + "\n\nContext: " + context)

elif page == "Backer Communications":
    page_header("Backer Communications", "Write transparent, useful messages for supporters.")
    kind = st.selectbox("Communication type", ["Welcome / thank-you","Progress update","Milestone announcement","Delay or problem disclosure","FAQ response","Post-campaign next steps"])
    facts = st.text_area("Verified facts, what happened, what backers need to know, and next update date", height=150)
    if st.button("Draft backer message", type="primary"):
        ask_ai(f"Draft a {kind} message to backers. Be transparent, specific, respectful, and clear about what is known, unknown, and happening next. Never conceal a material delay or invent progress.", facts)



elif page == "Shopify Prospecting":
    page_header("Shopify Store Intelligence", "Find, qualify and prioritise Shopify stores using public storefront evidence.")
    st.markdown("Build a prospect list, separate likely newer stores from established stores, spot visible conversion gaps, and prepare tailored outreach.")
    st.info("Important: a storefront scan cannot prove that a store has no sales. We flag observable conversion-friction signals, not private revenue or order data. Only scan public websites you are permitted to access.")
    with st.expander("🌐 Discover candidate Shopify stores with AI search", expanded=True):
        niche = st.text_input("Store niche / product category", placeholder="e.g. skincare, fashion, home fitness")
        geography = st.text_input("Target market / country", placeholder="e.g. United States, United Kingdom")
        criteria = st.text_input("Optional qualification focus", placeholder="e.g. independent brands, visible website improvements")
        if st.button("Find candidate stores", key="shopify_discover", type="primary"):
            if not niche.strip():
                st.warning("Enter a niche or product category first.")
            else:
                ask_ai(
                    "Use Google Search grounding to find up to 12 real candidate Shopify storefronts matching the niche and geography. Return each store name, public website URL, evidence that it appears to use Shopify, product category, and source URLs. Prefer independent active storefronts. Do not invent stores, owners, emails, revenue, or sales status. Mark platform identification as probable unless verified by source evidence. These are candidates for manual scanning, not confirmed prospects.",
                    f"Niche: {niche}\\nGeography: {geography or 'Not specified'}\\nQualification focus: {criteria or 'Independent storefronts'}",
                    web_search=True
                )
    url_input = st.text_area("Store URLs (one per line)", height=110, placeholder="https://example-store.com\nhttps://another-store.com")
    uploaded = st.file_uploader("Or import a CSV with a 'url' column", type=["csv"], key="shopify_leads_csv")
    if st.button("🔎 Scan storefronts", type="primary", use_container_width=True):
        import csv
        import io
        urls = [line.strip() for line in url_input.splitlines() if line.strip()]
        if uploaded:
            try:
                rows = list(csv.DictReader(io.StringIO(uploaded.getvalue().decode("utf-8-sig"))))
                urls.extend(row.get("url", "").strip() for row in rows if row.get("url", "").strip())
            except Exception as exc:
                st.error("Could not read CSV: " + str(exc))
        urls = list(dict.fromkeys(urls))[:20]
        if not urls:
            st.warning("Add at least one store URL or upload a CSV.")
        else:
            from shopify_prospecting import scan_store
            results = []
            progress = st.progress(0)
            for i, store_url in enumerate(urls):
                try:
                    results.append(scan_store(store_url))
                except Exception as exc:
                    results.append({"url": store_url, "domain": store_url, "title": "Scan failed", "is_shopify": False,
                                    "emails": [], "store_age_hint": "Unknown", "opportunity_score": 0,
                                    "sales_status": "Not assessed", "gaps": [], "error": str(exc)})
                progress.progress((i + 1) / len(urls))
            st.session_state.shopify_store_leads = results
            st.success(f"Scanned {len(results)} storefront(s).")
    leads = st.session_state.get("shopify_store_leads", [])
    if leads:
        import csv
        import io
        st.divider()
        st.subheader("Prospect filters")
        f1, f2, f3 = st.columns(3)
        age_filter = f1.selectbox("Store maturity", ["All", "Likely new / recent signal", "Established signal", "Unclear"])
        shopify_filter = f2.selectbox("Platform", ["All", "Shopify only", "Not confirmed Shopify"])
        need_filter = f3.selectbox("Opportunity", ["All", "Higher visible friction", "Some / unclear"])
        visible = []
        for lead in leads:
            age = lead.get("store_age_hint", "")
            if age_filter == "Likely new / recent signal" and age != "Recent/current-year signal":
                continue
            if age_filter == "Established signal" and age != "Established signal":
                continue
            if age_filter == "Unclear" and age != "Store age unclear":
                continue
            if shopify_filter == "Shopify only" and not lead.get("is_shopify"):
                continue
            if shopify_filter == "Not confirmed Shopify" and lead.get("is_shopify"):
                continue
            if need_filter == "Higher visible friction" and lead.get("opportunity_score", 0) < 42:
                continue
            if need_filter == "Some / unclear" and lead.get("opportunity_score", 0) >= 42:
                continue
            visible.append(lead)
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Scanned", len(leads))
        k2.metric("Shopify confirmed", sum(bool(x.get("is_shopify")) for x in leads))
        k3.metric("Emails found", sum(bool(x.get("emails")) for x in leads))
        k4.metric("Visible friction leads", sum(x.get("opportunity_score", 0) >= 42 for x in leads))
        st.caption("Filters affect the table below. Maturity labels are weak public signals, not verified store launch dates.")
        for lead in visible:
            with st.container(border=True):
                left, right = st.columns([4, 1])
                left.markdown("**" + str(lead.get("title", lead.get("domain", "Store"))) + "**")
                left.write(lead.get("url", ""))
                left.caption(("Shopify detected" if lead.get("is_shopify") else "Shopify not confirmed") + " · " + lead.get("store_age_hint", "Unknown"))
                if lead.get("emails"):
                    left.write("Public emails: " + ", ".join(lead["emails"]))
                else:
                    left.write("No public email found on the scanned page.")
                if lead.get("gaps"):
                    left.write("Visible opportunities: " + "; ".join(lead["gaps"]))
                if lead.get("error"):
                    left.warning(lead["error"])
                right.metric("Opportunity", str(lead.get("opportunity_score", 0)) + "/100")
                right.caption(lead.get("sales_status", ""))
        if visible and st.button("🧠 Generate AI opportunity analysis + outreach drafts", type="primary"):
            evidence = json.dumps(visible[:12], ensure_ascii=False, indent=2)
            ask_ai(
                "Act as a careful Shopify growth consultant and B2B prospect researcher. For each supplied store, identify the strongest evidence-backed growth opportunity, explain what evidence supports it, list what cannot be known from a public scan, and create one concise personalised cold email offering a relevant service. Use only the supplied public evidence; do not claim the store has no sales, invent the owner's name, or fabricate metrics. Keep drafts respectful, specific, and draft-only. Return one section per store.",
                "PUBLIC STOREFRONT SCAN RESULTS:\\n" + evidence
            )
        export_buffer = io.StringIO()
        writer = csv.DictWriter(export_buffer, fieldnames=["url", "title", "is_shopify", "store_age_hint", "emails", "opportunity_score", "sales_status", "gaps"])
        writer.writeheader()
        for lead in leads:
            writer.writerow({**lead, "emails": "; ".join(lead.get("emails", [])), "gaps": "; ".join(lead.get("gaps", []))})
        st.download_button("⬇ Export all prospects as CSV", export_buffer.getvalue(), "shopify-prospects.csv", "text/csv")
        st.caption("Outreach is generated as drafts only. No email is sent and no Shopify account is accessed by this first research phase.")

elif page == "Cloud Account":
    page_header("Cloud Account", "Sign in to securely save campaigns to your private Supabase database.")
    base_url, public_key = supabase_config()
    if not base_url or not public_key:
        st.warning("Supabase connection details are not configured in Streamlit Secrets yet.")
        st.code('SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"\nSUPABASE_PUBLISHABLE_KEY = "sb_publishable_..."', language="toml")
        st.markdown("In Streamlit, open your app → **Manage app** → **Settings** → **Secrets**. Add the two values above, replacing the examples. Use your project URL and publishable key only. Never add the secret key.")
    else:
        st.success("Supabase project settings detected.")
        signed_user = cloud_user()
        if signed_user and cloud_token():
            st.success("Signed in as " + signed_user.get("email", "your account"))
            if st.button("Sign out of cloud account"):
                for k in ("supabase_user","supabase_access_token","supabase_refresh_token"):
                    st.session_state.pop(k, None)
                st.rerun()
        else:
            tab_login, tab_signup = st.tabs(["Sign in", "Create account"])
            with tab_login:
                with st.form("supabase_login_form"):
                    email = st.text_input("Email address", key="sb_login_email")
                    password = st.text_input("Password", type="password", key="sb_login_password")
                    login = st.form_submit_button("Sign in", type="primary")
                if login:
                    try:
                        result = supabase_request("POST", "/auth/v1/token", params={"grant_type":"password"},
                            payload={"email":email.strip(),"password":password})
                        if result.get("access_token") and result.get("user"):
                            st.session_state.supabase_access_token = result["access_token"]
                            st.session_state.supabase_refresh_token = result.get("refresh_token","")
                            st.session_state.supabase_user = result["user"]
                            st.success("Signed in successfully.")
                            st.rerun()
                        st.error("Sign-in did not return a session. Check your details and email verification.")
                    except Exception as exc:
                        st.error(str(exc))
            with tab_signup:
                with st.form("supabase_signup_form"):
                    new_email = st.text_input("Email address", key="sb_signup_email")
                    new_password = st.text_input("Create password (at least 8 characters)", type="password", key="sb_signup_password")
                    signup = st.form_submit_button("Create account")
                if signup:
                    if len(new_password) < 8:
                        st.error("Choose a password with at least 8 characters.")
                    else:
                        try:
                            result = supabase_request("POST", "/auth/v1/signup",
                                payload={"email":new_email.strip(),"password":new_password})
                            if result.get("access_token") and result.get("user"):
                                st.session_state.supabase_access_token = result["access_token"]
                                st.session_state.supabase_user = result["user"]
                                st.session_state.supabase_refresh_token = result.get("refresh_token","")
                                st.success("Account created and signed in.")
                                st.rerun()
                            else:
                                st.success("Account request received. Check your email to confirm the account, then return here and sign in.")
                        except Exception as exc:
                            st.error(str(exc))
    st.caption("Your password is sent directly to Supabase Auth over HTTPS. The app uses your signed-in access token and the publishable key; it does not need your Supabase secret key.")

elif page == "Settings":
    page_header("Settings", "Connect the AI engine and review how this workspace handles information.")
    st.write("This app uses the Google Gemini API to generate drafts and analysis.")
    st.text_input("Gemini API key", type="password", key="gemini_key", help="Paste your key here. It stays in this app session. For a permanent deployment setup, add GEMINI_API_KEY to your hosting secrets.")
    st.caption("Never paste API keys into campaign notes, GitHub files, or messages to other people.")
    st.subheader("Model")
    st.code("gemini-3.8-flash")
    st.subheader("Data and reliability")
    st.markdown("- Campaign brief fields are stored in the current app session.\n- AI requests send the campaign brief and task to Google Gemini.\n- This first version does not independently verify market research or platform rules.\n- Review all outputs, prices, claims, legal requirements, and fulfilment plans before publishing.")
    if st.button("Test Gemini connection"):
        with st.spinner("Checking Gemini..."):
            ask_ai("Reply with exactly: Connection successful. The campaign workspace is ready.", "Connection test only.")
