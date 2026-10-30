/**
 * Personalized Learning Roadmap & Daily Task Tracker
 */

let currentRoadmap = null;

async function loadRoadmapModule() {
    try {
        const res = await API.get("/api/planner/current");
        if (res && res.has_plan) {
            currentRoadmap = res;
            renderRoadmapUI(res);
        } else {
            renderEmptyRoadmapState();
        }
    } catch (err) {
        console.error("Failed to load roadmap:", err);
        renderEmptyRoadmapState();
    }
}

function renderEmptyRoadmapState() {
    const container = document.getElementById("roadmap-container");
    if (!container) return;

    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">🗺️</div>
            <h3 class="empty-state-title">No Active Roadmap Generated</h3>
            <p class="empty-state-description">
                Generate a personalized 14-week curriculum tailored to your target role, resume skills, and assessment performance.
            </p>
            <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                <button type="button" class="btn btn-primary" onclick="generateRoadmapFromCurrentProfile()">
                    ⚡ Generate 14-Week Roadmap
                </button>
                <button type="button" class="btn btn-secondary" onclick="switchTab('resume')">
                    📄 Upload Resume First
                </button>
            </div>
        </div>
    `;
}

async function generateRoadmapFromCurrentProfile() {
    const user = API.getUser();
    const targetRole = user ? user.target_role : "Full Stack Developer";

    showToast("Generating personalized 14-week roadmap...", "info");

    try {
        const res = await API.post("/api/planner/generate", {
            target_role: targetRole,
            hours_per_week: 8
        });

        currentRoadmap = res;
        showToast("14-Week Roadmap ready!", "success");
        renderRoadmapUI(res);

        if (typeof loadDashboardData === "function") {
            loadDashboardData();
        }
    } catch (err) {
        showToast(err.message || "Failed to generate roadmap.", "error");
    }
}

function renderRoadmapUI(plan) {
    const container = document.getElementById("roadmap-container");
    if (!container) return;

    const weeks = plan.weeks || [];
    const totalTasks = plan.total_tasks || 0;
    const completedTasks = plan.completed_tasks || 0;
    const pct = plan.completion_percentage || 0;

    container.innerHTML = `
        <!-- Roadmap Summary Card -->
        <div class="roadmap-header-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem;">
                <div>
                    <span class="badge" style="background: rgba(255,255,255,0.15); color: #fff; margin-bottom: 0.5rem;">
                        ${escapeHtml(plan.target_role || "Target Career")} &bull; 14-Week Path
                    </span>
                    <h2>Personalized 14-Week Roadmap</h2>
                    <p>Comprehensive 14-week curriculum designed around your schedule (${plan.hours_per_week || 8} hrs/week). Mark daily tasks complete to track mastery.</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 2rem; font-weight: 800;">${pct}%</div>
                    <div style="font-size: 0.85rem; color: #cbd5e1;">${completedTasks} of ${totalTasks} tasks completed</div>
                </div>
            </div>

            <div class="progress-bar-container" style="margin-top: 1.25rem; height: 10px; background: rgba(255,255,255,0.2);">
                <div class="progress-bar-fill progress-bar-success" style="width: ${pct}%;"></div>
            </div>
        </div>

        <!-- Week-by-Week Accordion/Cards -->
        <div class="roadmap-weeks-list">
            ${weeks.map(w => renderWeekCard(w, plan.plan_id)).join("")}
        </div>
    `;
}

function renderWeekCard(week, planId) {
    const isCompleted = week.is_completed || false;
    const tasks = week.daily_tasks || [];
    const resources = week.resources || [];
    const exercises = week.practical_exercises || [];
    const project = week.weekly_project || {};
    const test = week.weekly_test || {};
    const phaseBadge = week.phase ? `<span class="badge badge-secondary" style="font-size: 0.72rem; margin-left: 0.5rem;">${escapeHtml(week.phase)}</span>` : '';

    return `
        <div class="week-card" id="week-card-${week.week}">
            <div class="week-card-header">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.25rem; flex-wrap: wrap;">
                        <h3 style="font-size: 1.15rem;">Week ${week.week}: ${escapeHtml(week.focus_skill.toUpperCase())}</h3>
                        ${phaseBadge}
                    </div>
                        <span class="badge ${week.focus_tier === 'remedial' ? 'badge-warning' : (week.focus_tier === 'advanced' ? 'badge-violet' : 'badge-primary')}">
                            ${escapeHtml(week.category || "Skill Module")}
                        </span>
                        ${isCompleted ? '<span class="badge badge-success">✓ Week Completed</span>' : ''}
                    </div>
                    <p style="font-size: 0.875rem; color: var(--text-secondary);">${escapeHtml(week.goal)}</p>
                    ${week.adaptive_note ? `<div style="font-size: 0.8rem; color: var(--warning-text); background: var(--warning-light); padding: 0.35rem 0.65rem; border-radius: 6px; margin-top: 0.35rem; display: inline-block;">⚡ ${escapeHtml(week.adaptive_note)}</div>` : ''}
                </div>
                <div style="text-align: right; font-size: 0.85rem; color: var(--text-muted); font-weight: 600;">
                    ${week.hours_allocated} hrs allocated
                </div>
            </div>

            <!-- Daily Task Checklist -->
            <div style="margin-top: 1rem;">
                <h4 style="font-size: 0.9rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.5rem;">
                    Daily Learning Tasks
                </h4>
                <div class="task-list">
                    ${tasks.map(t => `
                        <div class="task-item ${t.completed ? 'completed' : ''}" id="task-container-${t.id}">
                            <input 
                                type="checkbox" 
                                class="task-checkbox" 
                                id="task-chk-${t.id}" 
                                ${t.completed ? 'checked' : ''} 
                                onchange="handleTaskToggle('${planId}', '${t.id}', this.checked)"
                            >
                            <label class="task-info" for="task-chk-${t.id}">
                                <div class="task-title">${escapeHtml(t.title)}</div>
                                <div class="task-desc">${escapeHtml(t.description)} &bull; ${t.time_est_hours}h estimated</div>
                            </label>
                        </div>
                    `).join("")}
                </div>
            </div>

            <!-- Practical Deliverable & Weekly Assessment Row -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 1.25rem;">
                <!-- Mini Capstone -->
                <div style="background-color: var(--bg-surface-alt); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border);">
                    <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.25rem;">
                        🛠️ ${escapeHtml(project.title || "Weekly Practical Deliverable")}
                    </div>
                    <p style="font-size: 0.8rem; color: var(--text-secondary);">${escapeHtml(project.description || "")}</p>
                </div>

                <!-- Weekly Quiz Milestone -->
                <div style="background-color: var(--bg-surface-alt); padding: 1rem; border-radius: var(--radius-md); border: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-primary);">
                            📝 Week ${week.week} Assessment
                        </div>
                        <div style="font-size: 0.8rem; color: var(--text-muted);">
                            ${test.status === 'submitted' ? `Passed (${test.score_percent}% score)` : 'Test retention & trigger adaptive updates'}
                        </div>
                    </div>
                    <button 
                        type="button" 
                        class="btn ${test.status === 'submitted' ? 'btn-secondary' : 'btn-violet'} btn-sm"
                        onclick="launchWeeklyQuiz('${week.focus_skill}', ${week.week})"
                    >
                        ${test.status === 'submitted' ? 'Retake Quiz' : 'Take Quiz →'}
                    </button>
                </div>
            </div>

            <!-- Curated Educational Resources -->
            <div style="margin-top: 1.25rem;">
                <h4 style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em;">
                    Curated Learning Resources
                </h4>
                <div class="resource-cards-grid">
                    ${resources.map(r => `
                        <a href="${escapeHtml(r.url)}" target="_blank" rel="noopener noreferrer" class="resource-link-card">
                            <span>${r.type === 'Video' ? '🎬' : (r.type === 'Interactive' ? '💻' : '📖')}</span>
                            <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(r.title)}</span>
                            <span style="margin-left: auto; color: var(--text-muted); font-size: 0.75rem;">↗</span>
                        </a>
                    `).join("")}
                </div>
            </div>
        </div>
    `;
}

async function handleTaskToggle(planId, taskId, isChecked) {
    const taskContainer = document.getElementById(`task-container-${taskId}`);
    if (taskContainer) {
        taskContainer.classList.toggle("completed", isChecked);
    }

    try {
        const res = await API.post("/api/planner/task/toggle", {
            plan_id: planId,
            task_id: taskId,
            completed: isChecked
        });

        // Update progress counter in dashboard
        if (typeof loadDashboardData === "function") {
            loadDashboardData();
        }

    } catch (err) {
        showToast(err.message || "Failed to update task status.", "error");
        // Revert checkbox state
        const chk = document.getElementById(`task-chk-${taskId}`);
        if (chk) chk.checked = !isChecked;
        if (taskContainer) taskContainer.classList.toggle("completed", !isChecked);
    }
}

