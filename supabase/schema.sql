-- Crowdfunding Campaign OS: private, per-user campaign storage
-- Run this entire file in Supabase SQL Editor.
create extension if not exists pgcrypto;

create table if not exists public.campaigns (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  campaign_data jsonb not null default '{}'::jsonb,
  metrics jsonb not null default '{}'::jsonb,
  action_tasks jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, name)
);

create index if not exists campaigns_user_updated_idx
  on public.campaigns (user_id, updated_at desc);

alter table public.campaigns enable row level security;

drop policy if exists "Users can read their own campaigns" on public.campaigns;
create policy "Users can read their own campaigns"
  on public.campaigns for select
  using (auth.uid() = user_id);

drop policy if exists "Users can create their own campaigns" on public.campaigns;
create policy "Users can create their own campaigns"
  on public.campaigns for insert
  with check (auth.uid() = user_id);

drop policy if exists "Users can update their own campaigns" on public.campaigns;
create policy "Users can update their own campaigns"
  on public.campaigns for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

drop policy if exists "Users can delete their own campaigns" on public.campaigns;
create policy "Users can delete their own campaigns"
  on public.campaigns for delete
  using (auth.uid() = user_id);

grant select, insert, update, delete on public.campaigns to authenticated;
