# Lasting reviews: Supabase + Render

Reviews are stored in a **persistent store** so they survive restarts and redeploys. You can use **Supabase** as the store when deploying the backend to **Render** (or any host with an ephemeral filesystem).

## 1. Supabase setup

1. **Create a project** at [supabase.com](https://supabase.com) (free tier is enough).

2. **Create the `reviews` table** in the SQL Editor:

   ```sql
   create table if not exists public.reviews (
     id uuid primary key default gen_random_uuid(),
     business_id text not null,
     user_name text not null,
     rating smallint not null check (rating >= 1 and rating <= 5),
     comment text not null,
     verified boolean default true,
     created_at timestamptz default now()
   );

   -- Optional: allow anonymous read/write for the backend (uses anon key)
   alter table public.reviews enable row level security;

   create policy "Allow all for anon"
     on public.reviews for all
     to anon
     using (true)
     with check (true);
   ```

   If you prefer to use the **service role** key (no RLS), you can skip the policy and leave RLS disabled.

3. **Get your keys** from Project Settings → API:
   - **Project URL** → use as `SUPABASE_URL`
   - **anon public** key → use as `SUPABASE_KEY` or `SUPABASE_ANON_KEY`
   - Or **service_role** key → use as `SUPABASE_KEY` (bypasses RLS; keep this secret)

## 2. Render setup

1. **New Web Service** from your repo; use the same build/start commands you use locally (e.g. `pip install -r requirements.txt` and `gunicorn` or `python app.py` / `flask run`). See your `start.sh` or Render’s suggested Python commands.

2. **Environment variables** in the Render dashboard:
   - `SUPABASE_URL` = your Supabase project URL  
   - `SUPABASE_KEY` = your anon key (or service_role key if you’re not using RLS)  
   - Optionally `SUPABASE_ANON_KEY` instead of `SUPABASE_KEY` (both are read by the app)  
   - Set `SECRET_KEY` for Flask sessions (e.g. a long random string)  
   - Any other vars your app needs (e.g. `FOURSQUARE_API_KEY`)

3. Deploy. The app will use Supabase for reviews when `SUPABASE_URL` and `SUPABASE_KEY` (or `SUPABASE_ANON_KEY`) are set.

## 3. Behavior

- **With Supabase configured** (e.g. on Render): all reviews are read and written in Supabase. The directory and business detail pages use this store; the shared-reviews API does too. Data persists across deploys and restarts.
- **Without Supabase** (e.g. local): the main app uses `business_data.json` for reviews; the shared-reviews API uses `shared_reviews.json`. No code changes required for local dev.

## 4. GitHub Pages (static site) backend URL

If you use the static site in `docs/` with the shared-reviews API, set its backend URL to your Render service (e.g. `https://your-app.onrender.com`) so it can POST/GET reviews from the same Supabase-backed API.
