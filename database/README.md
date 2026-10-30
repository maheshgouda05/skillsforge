# SkillForge – Database Architecture & Supabase Schema

SkillForge utilizes **Supabase PostgreSQL** as its primary cloud data store. All tables are safeguarded with **Row Level Security (RLS)** policies ensuring multi-tenant isolation where each student can only access and modify their own records.

---

## 🗄️ Database Entity-Relationship Diagram (ERD)

```mermaid
erDiagram
    auth_users ||--|| profiles : "references id"
    profiles ||--o{ analyses : "profile_id"
    profiles ||--o{ assessments : "profile_id"
    profiles ||--o{ learning_plans : "profile_id"
    profiles ||--o{ weekly_tests : "profile_id"
    analyses ||--o{ learning_plans : "analysis_id"

    profiles {
        uuid id PK
        text full_name
        text email
        text target_role
        timestamptz created_at
        timestamptz updated_at
    }

    analyses {
        uuid id PK
        uuid profile_id FK
        text target_role
        text job_description
        numeric alignment_score
        jsonb result
        timestamptz created_at
    }

    assessments {
        uuid id PK
        uuid profile_id FK
        jsonb questions
        jsonb answers
        jsonb results
        text status
        timestamptz created_at
        timestamptz submitted_at
    }

    learning_plans {
        uuid id PK
        uuid profile_id FK
        uuid analysis_id FK
        text plan_type
        integer hours_per_week
        jsonb plan_data
        timestamptz created_at
        timestamptz updated_at
    }

    weekly_tests {
        uuid id PK
        uuid profile_id FK
        text skill
        integer week
        jsonb questions
        jsonb answers
        numeric score_percent
        text status
        timestamptz created_at
        timestamptz submitted_at
    }
```

---

## 📋 Schema Definition

The full DDL and migration script is stored in [`database/supabase_schema.sql`](file:///Users/maheshbasarkod/Documents/hackthon3/database/supabase_schema.sql).

### Key Tables
1. **`public.profiles`**: Extends `auth.users` with student career preferences, full name, and chosen target job role. Cascades on account deletion.
2. **`public.analyses`**: Stores resume text extraction metadata, extracted skills list, and Gemini AI coaching feedback.
3. **`public.assessments`**: Stores generated 20-MCQ technical exam sets, student submissions, and granular performance scores.
4. **`public.learning_plans`**: Holds the complete 14-week curriculum (70 daily tasks, milestones, and checkbox completion states).
5. **`public.weekly_tests`**: Tracks weekly quiz submissions and inputs to the adaptive curriculum engine.

---

## 🛡️ Row Level Security (RLS) & Security Policies

* Every table has RLS explicitly enabled (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`).
* Queries executed via the frontend client or authenticated API calls require `auth.uid() = profile_id`.
* The backend API interacts securely via isolated GoTrue clients and service role authentication for administrative maintenance tasks.

---

## ⚡ Performance Indexes

Composite indexes are configured for high-frequency queries:
```sql
CREATE INDEX idx_analyses_profile ON public.analyses(profile_id, created_at DESC);
CREATE INDEX idx_assessments_profile ON public.assessments(profile_id, created_at DESC);
CREATE INDEX idx_plans_profile ON public.learning_plans(profile_id, created_at DESC);
CREATE INDEX idx_weekly_tests_profile ON public.weekly_tests(profile_id, week, created_at DESC);
```
