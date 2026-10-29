-- ====================================================================
-- SKILLS-TO-JOB PLANNER - SUPABASE POSTGRESQL SCHEMA
-- Production database schema, tables, foreign keys, indexes, and RLS
-- ====================================================================

-- 1. Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. User Profiles Table (Linked to Supabase Auth)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    target_role TEXT DEFAULT 'Full Stack Developer',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Resume Analyses Table
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    target_role TEXT NOT NULL,
    job_description TEXT,
    alignment_score NUMERIC(5, 2) DEFAULT 0.00,
    result JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Technical Assessments Table (Initial & Skill Assessments)
CREATE TABLE IF NOT EXISTS public.assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    questions JSONB NOT NULL DEFAULT '[]'::jsonb,
    answers JSONB NOT NULL DEFAULT '{}'::jsonb,
    results JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'submitted')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ
);

-- 5. Personalized Learning Plans & Roadmaps Table
CREATE TABLE IF NOT EXISTS public.learning_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE SET NULL,
    plan_type TEXT NOT NULL DEFAULT 'personalized',
    hours_per_week INTEGER NOT NULL DEFAULT 8 CHECK (hours_per_week BETWEEN 1 AND 60),
    plan_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Weekly Tests & Adaptive Assessment Results Table
CREATE TABLE IF NOT EXISTS public.weekly_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE,
    skill TEXT NOT NULL,
    week INTEGER NOT NULL CHECK (week BETWEEN 1 AND 52),
    questions JSONB NOT NULL DEFAULT '[]'::jsonb,
    answers JSONB NOT NULL DEFAULT '{}'::jsonb,
    score_percent NUMERIC(5, 2),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'submitted')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    submitted_at TIMESTAMPTZ
);

-- --------------------------------------------------------------------
-- INDEXES FOR HIGH-PERFORMANCE QUERYING
-- --------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_analyses_profile ON public.analyses(profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assessments_profile ON public.assessments(profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_plans_profile ON public.learning_plans(profile_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_weekly_tests_profile ON public.weekly_tests(profile_id, week, created_at DESC);

-- --------------------------------------------------------------------
-- ROW LEVEL SECURITY (RLS) POLICIES
-- --------------------------------------------------------------------

-- Enable RLS on all tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weekly_tests ENABLE ROW LEVEL SECURITY;

-- Profiles Policies
CREATE POLICY "Users can read own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

-- Analyses Policies
CREATE POLICY "Users can read own analyses"
    ON public.analyses FOR SELECT
    USING (auth.uid() = profile_id OR profile_id IS NULL);

CREATE POLICY "Users can insert own analyses"
    ON public.analyses FOR INSERT
    WITH CHECK (auth.uid() = profile_id OR profile_id IS NULL);

-- Assessments Policies
CREATE POLICY "Users can read own assessments"
    ON public.assessments FOR SELECT
    USING (auth.uid() = profile_id OR profile_id IS NULL);

CREATE POLICY "Users can insert own assessments"
    ON public.assessments FOR INSERT
    WITH CHECK (auth.uid() = profile_id OR profile_id IS NULL);

CREATE POLICY "Users can update own assessments"
    ON public.assessments FOR UPDATE
    USING (auth.uid() = profile_id OR profile_id IS NULL);

-- Learning Plans Policies
CREATE POLICY "Users can read own learning plans"
    ON public.learning_plans FOR SELECT
    USING (auth.uid() = profile_id OR profile_id IS NULL);

CREATE POLICY "Users can insert own learning plans"
    ON public.learning_plans FOR INSERT
    WITH CHECK (auth.uid() = profile_id OR profile_id IS NULL);

CREATE POLICY "Users can update own learning plans"
    ON public.learning_plans FOR UPDATE
    USING (auth.uid() = profile_id OR profile_id IS NULL);

-- Weekly Tests Policies
CREATE POLICY "Users can read own weekly tests"
    ON public.weekly_tests FOR SELECT
    USING (auth.uid() = profile_id OR profile_id IS NULL);

CREATE POLICY "Users can insert own weekly tests"
    ON public.weekly_tests FOR INSERT
    WITH CHECK (auth.uid() = profile_id OR profile_id IS NULL);

CREATE POLICY "Users can update own weekly tests"
    ON public.weekly_tests FOR UPDATE
    USING (auth.uid() = profile_id OR profile_id IS NULL);

-- --------------------------------------------------------------------
-- AUTOMATIC PROFILE CREATION TRIGGER (Optional on auth.users signup)
-- --------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
    INSERT INTO public.profiles (id, full_name, email, target_role)
    VALUES (
        new.id,
        COALESCE(new.raw_user_meta_data->>'full_name', 'Student'),
        new.email,
        COALESCE(new.raw_user_meta_data->>'target_role', 'Full Stack Developer')
    )
    ON CONFLICT (id) DO NOTHING;
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

