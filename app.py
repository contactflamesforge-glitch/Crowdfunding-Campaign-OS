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
.block-container {padding-top: 2rem; max-width: 1250px;}
.hero {padding: 1.5rem 1.7rem; border-radius: 16px; background: linear-gradient(120deg,#14213d,#244b75); color: white; margin-bottom: 1rem;}
.hero h1 {color:white; margin:0;}
.hero p {color:#e5edf7; margin:.4rem 0 0 0;}
.small-note {color: #777; font-size: .88rem;}
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
    "Backer Communications", "Settings"
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
            (["settings"], "Settings")
        ]
        for phrases, page_name in routes:
            if any(phrase in spoken for phrase in phrases):
                target = page_name
                break
        if target is None:
            st.session_state["jarvis_reply"] = "I heard you. Try saying open Campaign Analyzer, open Marketing Studio, or open Launch Manager."
            return
    elif event.get("type") == "gesture":
        gestures = {
            "Open_Palm": "Overview",
            "Victory": "Marketing Studio",
            "Pointing_Up": "Launch Manager",
            "Thumb_Up": "Campaign Analyzer"
        }
        target = gestures.get(event.get("gesture"))
        if event.get("gesture") == "Closed_Fist":
            st.session_state["jarvis_reply"] = "Okay. I have stopped speaking."
            return
    if target:
        st.session_state["workspace_page"] = target
        st.session_state["jarvis_reply"] = f"Opening {target}."

C = st.session_state.campaign
st.sidebar.title("🚀 Campaign OS")
st.sidebar.subheader("J.A.R.V.I.S. Voice & Gesture Control")
jarvis_event = jarvis_controls(reply=st.session_state.get("jarvis_reply", ""), key="jarvis_control", default=None)
if jarvis_event and jarvis_event.get("at") != st.session_state.get("jarvis_last_event_at"):
    st.session_state["jarvis_last_event_at"] = jarvis_event.get("at")
    handle_jarvis_event(jarvis_event)
page = st.sidebar.radio("Workspace", PAGES, key="workspace_page")
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

def ask_ai(task, extra="", temperature=0.65):
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
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    try:
        response = requests.post(
            url + "?key=" + key,
            headers={"Content-Type": "application/json"},
            json={"contents":[{"parts":[{"text":prompt}]}],
                  "generationConfig":{"temperature":temperature, "maxOutputTokens":6000}},
            timeout=90
        )
        if response.status_code != 200:
            st.error(f"Gemini returned an error ({response.status_code}). Check the API key, model access, and quota.")
            with st.expander("Technical details"):
                st.code(response.text[:2500])
            return
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        st.markdown(text)
        st.download_button("Download this result", text, file_name="campaign-os-output.txt")
    except requests.exceptions.Timeout:
        st.error("The request timed out. Try again with a shorter task.")
    except Exception as e:
        st.error(f"Could not generate a response: {e}")

def page_header(title, subtitle):
    st.title(title)
    st.caption(subtitle)

if page == "Overview":
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
    st.info("This version does not browse the live web. It will not pretend to have verified competitors or market statistics. Paste research, links' contents, or interview notes for evidence-based analysis.")
    research = st.text_area("Paste research, competitor notes, customer interviews, survey results, or source excerpts", height=180)
    if st.button("Analyze market and audience", type="primary"):
        ask_ai("Analyze the supplied research. Identify backer segments, motivations, objections, alternatives, competitor positioning where evidence exists, unanswered questions, and a practical validation plan. Distinguish evidence from hypotheses.", research)

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

elif page == "Settings":
    page_header("Settings", "Connect the AI engine and review how this workspace handles information.")
    st.write("This app uses the Google Gemini API to generate drafts and analysis.")
    st.text_input("Gemini API key", type="password", key="gemini_key", help="Paste your key here. It stays in this app session. For a permanent deployment setup, add GEMINI_API_KEY to your hosting secrets.")
    st.caption("Never paste API keys into campaign notes, GitHub files, or messages to other people.")
    st.subheader("Model")
    st.code("gemini-2.5-flash")
    st.subheader("Data and reliability")
    st.markdown("- Campaign brief fields are stored in the current app session.\n- AI requests send the campaign brief and task to Google Gemini.\n- This first version does not independently verify market research or platform rules.\n- Review all outputs, prices, claims, legal requirements, and fulfilment plans before publishing.")
    if st.button("Test Gemini connection"):
        with st.spinner("Checking Gemini..."):
            ask_ai("Reply with exactly: Connection successful. The campaign workspace is ready.", "Connection test only.")
