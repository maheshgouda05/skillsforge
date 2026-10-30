-- ====================================================================
-- SKILLS-TO-JOB PLANNER - PLACEMENT & HIRING HUB MIGRATION
-- Database schema for company recruitment drives, student saved bookmarks,
-- and individual application tracking pipelines.
-- ====================================================================

-- 1. Company Placement Opportunities Table
CREATE TABLE IF NOT EXISTS public.placement_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_name TEXT NOT NULL,
    company_logo TEXT,
    role_title TEXT NOT NULL,
    job_type TEXT NOT NULL DEFAULT 'Full-time', -- 'Full-time', 'Internship', 'Campus Drive', 'Off-campus', 'Fresher', 'Graduate Engineer Trainee (GET)', 'Walk-in'
    location TEXT NOT NULL DEFAULT 'Pan India',
    package_ctc TEXT NOT NULL DEFAULT 'Not specified',
    eligibility_criteria TEXT NOT NULL,
    required_skills JSONB NOT NULL DEFAULT '[]'::jsonb,
    selection_rounds JSONB NOT NULL DEFAULT '[]'::jsonb,
    opening_date TEXT DEFAULT 'Open now',
    deadline_date TEXT DEFAULT 'Not specified',
    recruitment_date TEXT DEFAULT 'Not specified',
    status TEXT NOT NULL DEFAULT 'Currently Open' CHECK (status IN ('Currently Open', 'Upcoming', 'Closing Soon', 'Closed', 'Completed', 'Unverified')),
    apply_url TEXT NOT NULL,
    source_url TEXT NOT NULL,
    is_verified BOOLEAN DEFAULT TRUE,
    last_verified_at TEXT NOT NULL DEFAULT CURRENT_DATE::text,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Student Saved / Bookmarked Opportunities Table
CREATE TABLE IF NOT EXISTS public.saved_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    opportunity_id UUID REFERENCES public.placement_opportunities(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, opportunity_id)
);

-- 3. Student Application Tracker Table
CREATE TABLE IF NOT EXISTS public.student_applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    opportunity_id UUID REFERENCES public.placement_opportunities(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'Interested' CHECK (status IN ('Interested', 'Preparing', 'Applied', 'Assessment Completed', 'Interview Scheduled', 'Selected', 'Rejected')),
    applied_date TEXT,
    interview_date TEXT,
    notes TEXT DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, opportunity_id)
);

-- 4. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_placement_opps_status ON public.placement_opportunities(status);
CREATE INDEX IF NOT EXISTS idx_placement_opps_type ON public.placement_opportunities(job_type);
CREATE INDEX IF NOT EXISTS idx_placement_opps_company ON public.placement_opportunities(company_name);
CREATE INDEX IF NOT EXISTS idx_saved_opps_user ON public.saved_opportunities(user_id);
CREATE INDEX IF NOT EXISTS idx_student_apps_user ON public.student_applications(user_id);
CREATE INDEX IF NOT EXISTS idx_student_apps_status ON public.student_applications(status);

-- 5. Row Level Security (RLS) Policies
ALTER TABLE public.placement_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.student_applications ENABLE ROW LEVEL SECURITY;

-- Opportunities: readable by all authenticated users
CREATE POLICY "Placement opportunities are viewable by all authenticated users"
    ON public.placement_opportunities FOR SELECT
    TO authenticated
    USING (true);

-- Saved Opportunities: users can view and modify only their own saved items
CREATE POLICY "Users can manage their own saved opportunities"
    ON public.saved_opportunities FOR ALL
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Applications: users can view and manage only their own applications
CREATE POLICY "Users can manage their own applications"
    ON public.student_applications FOR ALL
    TO authenticated
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
