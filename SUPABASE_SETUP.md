# Supabase setup for Crowdfunding Campaign OS

This project uses Supabase as an optional cloud database target. The SQL schema is in `supabase/schema.sql`.

## Important status

The database schema has been added to the repository. Cloud sync is **not connected to the running app yet**. A Supabase project and its credentials are required before that can be safely completed and tested.

## Create a Supabase project

1. Open https://supabase.com/ and create a free account.
2. Create a new project. Choose a strong database password and keep it private.
3. Wait for the project to finish provisioning.
4. In the project dashboard, open **SQL Editor**.
5. Open `supabase/schema.sql` from this repository, copy its full contents, paste into SQL Editor, and run it.
6. In **Project Settings → API** (or **Data API**, depending on dashboard layout), copy the Project URL and the publishable/anon key. Never use or expose the service_role/secret key in the Streamlit app.

## Configure the app after integration

The app will need the Project URL and publishable/anon key as Streamlit secrets, plus a user sign-in flow. Do not put credentials in GitHub source code or campaign briefs. Do not send keys in ChatGPT messages.

## Security model

- The table uses Supabase Auth user IDs.
- Row Level Security (RLS) is enabled.
- Each signed-in user can read, create, update and delete only rows whose `user_id` matches their authenticated user ID.
- The app must use a signed-in user's access token for database requests. A publishable/anon key alone is not sufficient to access private campaign rows.
- Never put the Supabase service_role/secret key in browser code, GitHub, or Streamlit user-facing inputs.

## Free-tier note

Supabase offers a free tier, but quotas, project pausing/availability, storage, and feature limits can change. Check the current plan details before relying on it for business-critical records. Keep periodic JSON exports as backups.
