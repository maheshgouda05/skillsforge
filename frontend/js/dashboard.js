/**
 * Main Student Dashboard Controller
 */

let skillsChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    setupNavigation();
    initResumeModule();
    await loadUserProfile();
    await loadDashboardData();
    await loadRoadmapModule();

    // Check URL hash for direct tab linking
    const hash = window.location.hash.replace("#", "") || "overview";
    switchTab(hash);
}

function setupNavigation() {
    const navItems = document.querySelectorAll(".nav-item[data-tab]");
    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const targetTab = item.getAttribute("data-tab");
            switchTab(targetTab);
        });
    });

    window.addEventListener("hashchange", () => {
        const targetTab = window.location.hash.replace("#", "") || "overview";
        switchTab(targetTab);
    });
}

function switchTab(tabId) {
    // Validate target pane exists
    const targetPane = document.getElementById(`pane-${tabId}`);
    if (!targetPane) tabId = "overview";

    // Update nav items
    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.toggle("active", item.getAttribute("data-tab") === tabId);
    });

    // Update panes
    document.querySelectorAll(".tab-pane").forEach(pane => {
        pane.classList.remove("active");
    });

    const activePane = document.getElementById(`pane-${tabId}`);
    if (activePane) {
        activePane.classList.add("active");
    }

    // Update title in topbar
    const titles = {
        "overview": "Student Dashboard",
        "resume": "Resume & Skill Extraction",
        "job-match": "Target Role & Skill Gap Analysis",
        "assessment": "20-MCQ Technical Assessment",
        "roadmap": "Personalized 8-Week Roadmap",
        "weekly-test": "Weekly Assessment & Adaptation",
        "projects": "Recommended Capstone Projects"
    };
    const titleEl = document.getElementById("current-tab-title");
    if (titleEl) {
        titleEl.innerText = titles[tabId] || "Skills-to-Job Planner";
    }

    window.location.hash = `#${tabId}`;
    window.scrollTo({ top: 0, behavior: "smooth" });
}

async function loadUserProfile() {
    try {
        const res = await API.get("/api/auth/me");
        if (res.authenticated && res.user) {
            API.setUser(res.user);
            updateUserDisplay(res.user);
        } else {
            // Check local fallback or guest
            const localUser = API.getUser();
            if (localUser) {
                updateUserDisplay(localUser);
            }
        }
    } catch (err) {
        console.warn("User profile fetch:", err);
    }
}

function updateUserDisplay(user) {
    if (!user) return;
    const nameEl = document.getElementById("sidebar-user-name");
    const roleEl = document.getElementById("sidebar-user-role");
    const headerName = document.getElementById("dashboard-welcome-name");

    if (nameEl) nameEl.innerText = user.full_name || "Student";
    if (roleEl) roleEl.innerText = user.target_role || "Full Stack Developer";
    if (headerName) headerName.innerText = user.full_name || "Student";

    const topRoleSelect = document.getElementById("target-role-select");
    if (topRoleSelect && user.target_role) {
        topRoleSelect.value = user.target_role;
    }
}

async function loadDashboardData() {
    try {
        const data = await API.get("/api/dashboard");
        renderDashboardMetrics(data);
        renderSkillsChart(data);
        renderRecentActivity(data.recent_activity || []);
        renderRecommendedProjects(data.recommended_projects || []);
    } catch (err) {
        console.error("Dashboard data load error:", err);
    }
}

function renderDashboardMetrics(data) {
    // 1. Skill Match Score
    const matchEl = document.getElementById("stat-match-percentage");
    if (matchEl) {
        if (data.has_resume && data.match_percentage !== null) {
            matchEl.innerText = `${data.match_percentage}%`;
        } else {
            matchEl.innerText = "--%";
        }
    }

    // 2. Strong Skills Count
    const strongEl = document.getElementById("stat-strong-skills");
    if (strongEl) {
        strongEl.innerText = (data.strong_skills || []).length;
    }

    // 3. Weak / Missing Skills Count
    const gapsEl = document.getElementById("stat-skill-gaps");
    if (gapsEl) {
        const gapCount = (data.weak_skills || []).length + (data.missing_skills || []).length;
        gapsEl.innerText = gapCount;
    }

    // 4. Roadmap Task Completion
    const roadmapEl = document.getElementById("stat-roadmap-completion");
    if (roadmapEl) {
        if (data.has_roadmap && data.roadmap_completion !== null) {
            roadmapEl.innerText = `${data.roadmap_completion}%`;
        } else {
            roadmapEl.innerText = "0%";
        }
    }

    // Empty state banners vs active states
    const resumeNotice = document.getElementById("dashboard-empty-resume-banner");
    if (resumeNotice) {
        resumeNotice.style.display = data.has_resume ? "none" : "block";
    }

    const assessmentNotice = document.getElementById("dashboard-empty-assessment-banner");
    if (assessmentNotice) {
        assessmentNotice.style.display = data.has_assessment ? "none" : "block";
    }

    // Categorized Skill Pill Cloud on Overview
    renderOverviewSkillPills(data);
}

function renderOverviewSkillPills(data) {
    const container = document.getElementById("overview-skills-cloud");
    if (!container) return;

    if (!data.has_resume && !data.has_assessment) {
        container.innerHTML = `
            <div class="empty-state" style="padding: 1.5rem; border: none; background: transparent;">
                <p style="font-size: 0.85rem; color: var(--text-muted);">
                    Upload your resume or take the 20-MCQ assessment to populate your skills breakdown.
                </p>
                <button type="button" class="btn btn-primary btn-sm" style="margin-top: 0.5rem;" onclick="switchTab('resume')">
                    Analyze Resume
                </button>
            </div>
        `;
        return;
    }

    let pills = [];
    (data.strong_skills || []).forEach(s => {
        pills.push(`<span class="badge badge-success">✓ ${escapeHtml(s.skill || s)}</span>`);
    });
    (data.intermediate_skills || []).forEach(s => {
        pills.push(`<span class="badge badge-primary">◈ ${escapeHtml(s.skill || s)}</span>`);
    });
    (data.weak_skills || []).forEach(s => {
        pills.push(`<span class="badge badge-warning">⚠ ${escapeHtml(s.skill || s)}</span>`);
    });
    (data.missing_skills || []).forEach(s => {
        pills.push(`<span class="badge badge-slate">+ ${escapeHtml(s.skill || s)}</span>`);
    });

    container.innerHTML = pills.length > 0
        ? pills.join(" ")
        : `<span style="font-size: 0.85rem; color: var(--text-muted);">No categorized skills recorded.</span>`;
}

function renderSkillsChart(data) {
    const canvas = document.getElementById("skills-radar-chart");
    if (!canvas || typeof Chart === "undefined") return;

    const ctx = canvas.getContext("2d");
    if (skillsChartInstance) {
        skillsChartInstance.destroy();
    }

    // Build chart data from assessment or analyzed skills
    let labels = [];
    let scores = [];

    if (data.assessment_skills && Object.keys(data.assessment_skills).length > 0) {
        Object.entries(data.assessment_skills).forEach(([skill, info]) => {
            labels.push(skill.toUpperCase());
            scores.push(info.score_percent || 0);
        });
    } else if (data.strong_skills || data.intermediate_skills || data.weak_skills) {
        (data.strong_skills || []).slice(0, 4).forEach(s => { labels.push((s.skill || s).toUpperCase()); scores.push(85); });
        (data.intermediate_skills || []).slice(0, 4).forEach(s => { labels.push((s.skill || s).toUpperCase()); scores.push(65); });
        (data.weak_skills || []).slice(0, 4).forEach(s => { labels.push((s.skill || s).toUpperCase()); scores.push(35); });
    }

    if (labels.length === 0) {
        labels = ["PYTHON", "SQL", "GIT", "APIS", "SYSTEMS"];
        scores = [0, 0, 0, 0, 0];
    }

    skillsChartInstance = new Chart(ctx, {
        type: "radar",
        data: {
            labels: labels,
            datasets: [{
                label: "Competency Level (%)",
                data: scores,
                backgroundColor: "rgba(37, 99, 235, 0.2)",
                borderColor: "#2563eb",
                pointBackgroundColor: "#6366f1",
                pointBorderColor: "#fff",
                pointHoverBackgroundColor: "#fff",
                pointHoverBorderColor: "#2563eb",
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    angleLines: { color: "#e2e8f0" },
                    grid: { color: "#f1f5f9" },
                    pointLabels: {
                        font: { size: 11, weight: "bold" },
                        color: "#334155"
                    },
                    suggestedMin: 0,
                    suggestedMax: 100,
                    ticks: { stepSize: 25, display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function renderRecentActivity(activities) {
    const list = document.getElementById("recent-activity-list");
    if (!list) return;

    if (!activities || activities.length === 0) {
        list.innerHTML = `
            <div style="padding: 1.5rem; text-align: center; color: var(--text-muted); font-size: 0.85rem;">
                No recent activity recorded yet. Start by parsing a resume or taking a test.
            </div>
        `;
        return;
    }

    list.innerHTML = activities.map(act => `
        <div style="display: flex; align-items: flex-start; gap: 0.75rem; padding: 0.85rem 0; border-bottom: 1px solid var(--border);">
            <div style="width: 8px; height: 8px; border-radius: 50%; background-color: var(--primary); margin-top: 6px;"></div>
            <div style="flex: 1;">
                <div style="font-size: 0.875rem; font-weight: 600; color: var(--text-primary);">${escapeHtml(act.title)}</div>
                <div style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(act.detail)}</div>
            </div>
            <span style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(act.time || "")}</span>
        </div>
    `).join("");
}

function renderRecommendedProjects(projects) {
    const container = document.getElementById("recommended-projects-list");
    if (!container) return;

    if (!projects || projects.length === 0) {
        container.innerHTML = `<p style="font-size: 0.85rem; color: var(--text-muted);">No project recommendations available.</p>`;
        return;
    }

    container.innerHTML = projects.map(p => `
        <div class="card" style="margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                <h4 style="font-size: 1rem; color: var(--text-primary);">${escapeHtml(p.title)}</h4>
                <span class="badge ${p.difficulty === 'Advanced' ? 'badge-violet' : 'badge-primary'}">${escapeHtml(p.difficulty || 'Intermediate')}</span>
            </div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.5;">${escapeHtml(p.description)}</p>
        </div>
    `).join("");
}

function logoutUser() {
    API.clearSession();
    showToast("Signed out successfully.", "info");
    setTimeout(() => {
        window.location.href = "auth.html";
    }, 600);
}
