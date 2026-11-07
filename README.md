# Crowdfunding Campaign OS

AI-powered workspace for crowdfunding campaign strategy, creation, marketing, launch planning, performance analysis, and backer communication.

## Features

- Campaign brief shared across the workspace
- Campaign readiness analysis and risk review
- Market and audience analysis from research you provide
- Campaign headline, story, FAQ, and video-script drafts
- Reward-tier strategy with cost and fulfilment cautions
- Pre-launch audience-building plan
- Email, social, outreach, and promotional content
- Launch runbook and campaign performance analysis
- Transparent backer updates and responses
- **J.A.R.V.I.S. voice and hand-gesture controls:** browser speech recognition, spoken responses, and camera-based gesture shortcuts for workspace navigation

## J.A.R.V.I.S. controls

Open the app in a modern browser (Chrome is recommended). In the left sidebar:

1. Tap **Voice control**, allow microphone access, and speak a command such as "open Campaign Analyzer" or "open Marketing Studio".
2. Tap **Hand gestures**, allow camera access, and show one hand clearly.
3. Gesture shortcuts: open palm = Overview; victory sign = Marketing Studio; pointing up = Launch Manager; thumbs up = Campaign Analyzer; closed fist = stop spoken audio.
4. Tap **Stop** to stop microphone recognition, camera capture, and speech output.

Voice recognition and camera gesture support depend on browser/device support and permissions. On some mobile browsers, speech recognition or camera processing may be unavailable or slower. The camera is processed in the browser; the app sends recognized gesture labels, not a video recording, to the Streamlit app.

## Run locally

1. Install Python 3.10 or newer.
2. Download or clone this repository.
3. Install dependencies:

   `pip install -r requirements.txt`

4. Start the app:

   `streamlit run app.py`

5. Open the local address shown in your terminal and add your Gemini API key in **Settings**.

## Deploy on Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud and choose **Create app**.
2. Select this repository, the `main` branch, and `app.py`.
3. Deploy the app.
4. In the app's deployment settings, add a secret named `GEMINI_API_KEY` containing your Google Gemini API key.
5. Save the secret and reboot the app.

Never commit API keys or other secrets to this repository.

## Important limitations

- This is a J.A.R.V.I.S.-inspired interface, not the fictional Iron Man AI.
- The first version does not browse the live web or independently verify market research.
- Market and competitor analysis is based on evidence and source material supplied by the user.
- Campaign brief information is held in the current app session; this initial version does not provide a permanent campaign database or user accounts.
- AI-generated claims, costs, reward prices, legal requirements, platform rules, and delivery estimates must be checked before publication.
- No AI system can guarantee that a crowdfunding campaign will reach its funding goal.

## Technology

- Python
- Streamlit
- Google Gemini API
- Browser Web Speech API
- MediaPipe Gesture Recognizer
