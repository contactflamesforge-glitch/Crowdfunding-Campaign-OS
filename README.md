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

- The first version does not browse the live web or independently verify market research.
- Market and competitor analysis is based on evidence and source material supplied by the user.
- Campaign brief information is held in the current app session; this initial version does not provide a permanent campaign database or user accounts.
- AI-generated claims, costs, reward prices, legal requirements, platform rules, and delivery estimates must be checked before publication.
- No AI system can guarantee that a crowdfunding campaign will reach its funding goal.

## Technology

- Python
- Streamlit
- Google Gemini API
