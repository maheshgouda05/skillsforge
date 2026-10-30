/**
 * SkillForge - Placement & Hiring Hub Controller
 * Manages verified company listings, multi-filter search,
 * personalized company preparation plans, bookmarks, and application tracking.
 */

let allOpportunities = [];
let currentFilter = {
    search: "",
    job_type: "all",
    status: "all",
    location: "all",
    saved_only: false
};
let activeTab = "all"; // 'all', 'saved', 'tracker'

document.addEventListener("DOMContentLoaded", () => {
    initPlacementsHub();
});

async function initPlacementsHub() {
    loadStudentProfile();
    setupEventHandlers();
    await loadPlacementStats();
    await loadOpportunities();
}

function loadStudentProfile() {
    const user = API.getUser() || {};
    const userName = user.full_name || "Student";
    const userRole = user.target_role || "Full Stack Developer";

    const sidebarName = document.getElementById("sidebar-user-name");
    if (sidebarName) sidebarName.innerText = userName;

    const sidebarRole = document.getElementById("sidebar-user-role");
    if (sidebarRole) sidebarRole.innerText = userRole;

    const topbarRole = document.getElementById("topbar-role-badge");
    if (topbarRole) topbarRole.innerText = userRole;
}

function setupEventHandlers() {
    // Search input with debounce
    const searchInput = document.getElementById("placements-search-input");
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener("input", (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                currentFilter.search = e.target.value.trim();
                renderFilteredOpportunities();
            }, 250);
        });
    }

    // Dropdowns
    const typeSelect = document.getElementById("filter-job-type");
    if (typeSelect) {
        typeSelect.addEventListener("change", (e) => {
            currentFilter.job_type = e.target.value;
            renderFilteredOpportunities();
        });
    }

    const statusSelect = document.getElementById("filter-status");
    if (statusSelect) {
        statusSelect.addEventListener("change", (e) => {
            currentFilter.status = e.target.value;
            renderFilteredOpportunities();
        });
    }

    const locationSelect = document.getElementById("filter-location");
    if (locationSelect) {
        locationSelect.addEventListener("change", (e) => {
            currentFilter.location = e.target.value;
            renderFilteredOpportunities();
        });
    }

    // Clear filters button
    const clearBtn = document.getElementById("btn-clear-filters");
    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            currentFilter = {
                search: "",
                job_type: "all",
                status: "all",
                location: "all",
                saved_only: activeTab === "saved"
            };
            if (searchInput) searchInput.value = "";
            if (typeSelect) typeSelect.value = "all";
            if (statusSelect) statusSelect.value = "all";
            if (locationSelect) locationSelect.value = "all";
            renderFilteredOpportunities();
        });
    }

    // Modal Close buttons
    document.querySelectorAll(".modal-close-btn, .btn-modal-dismiss").forEach(btn => {
        btn.addEventListener("click", () => {
            closeAllModals();
        });
    });

    // Close on backdrop click
    document.querySelectorAll(".placement-modal-backdrop").forEach(backdrop => {
        backdrop.addEventListener("click", (e) => {
            if (e.target === backdrop) {
                closeAllModals();
            }
        });
    });

    // Close on ESC
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") closeAllModals();
    });
}

function closeAllModals() {
    document.querySelectorAll(".placement-modal-backdrop").forEach(el => el.classList.remove("open"));
}

/* -------------------- STATS -------------------- */

async function loadPlacementStats() {
    try {
        const stats = await API.get("/api/placements/stats");
        if (stats) {
            const elUpcoming = document.getElementById("stat-upcoming-drives");
            if (elUpcoming) elUpcoming.innerText = stats.upcoming_drives ?? 0;

            const elOpen = document.getElementById("stat-open-apps");
            if (elOpen) elOpen.innerText = stats.open_applications ?? 0;

            const elIntern = document.getElementById("stat-internships");
            if (elIntern) elIntern.innerText = stats.internship_opportunities ?? 0;

            const elDeadlines = document.getElementById("stat-deadlines");
            if (elDeadlines) elDeadlines.innerText = stats.application_deadlines ?? 0;

            const badgeAll = document.getElementById("tab-badge-all");
            if (badgeAll) badgeAll.innerText = stats.total_opportunities ?? 0;

            const badgeSaved = document.getElementById("tab-badge-saved");
            if (badgeSaved) badgeSaved.innerText = stats.user_saved_count ?? 0;

            const badgeTracker = document.getElementById("tab-badge-tracker");
            if (badgeTracker) badgeTracker.innerText = stats.user_applied_count ?? 0;
        }
    } catch (e) {
        console.warn("Could not load placement statistics:", e);
    }
}

/* -------------------- OPPORTUNITIES -------------------- */

async function loadOpportunities() {
    const grid = document.getElementById("opportunities-grid");
    if (grid) {
        grid.innerHTML = `
            <div style="grid-column: 1 / -1; text-align: center; padding: 3rem; color: var(--text-muted);">
                <div class="spinner" style="margin: 0 auto 1rem auto; width: 32px; height: 32px; border: 3px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                <p>Loading verified company recruitment drives...</p>
            </div>
        `;
    }

    try {
        const res = await API.get("/api/placements/opportunities");
        if (res && res.opportunities) {
            allOpportunities = res.opportunities;
            populateFilterDropdowns(allOpportunities);
            renderFilteredOpportunities();
        }
    } catch (e) {
        if (grid) {
            grid.innerHTML = `
                <div class="empty-placements-state" style="grid-column: 1 / -1;">
                    <div class="empty-placements-icon">⚠️</div>
                    <h3>Unable to load opportunities</h3>
                    <p>${escapeHtml(e.message || "Failed to reach backend server.")}</p>
                    <button class="btn btn-primary btn-sm" onclick="loadOpportunities()">Retry</button>
                </div>
            `;
        }
    }
}

function populateFilterDropdowns(opps) {
    const locationSelect = document.getElementById("filter-location");
    if (locationSelect && locationSelect.children.length <= 1) {
        const locations = new Set();
        opps.forEach(o => {
            if (o.location) {
                if (o.location.includes("Pan India")) locations.add("Pan India");
                if (o.location.includes("Bengaluru")) locations.add("Bengaluru");
                if (o.location.includes("Hyderabad")) locations.add("Hyderabad");
                if (o.location.includes("Pune")) locations.add("Pune");
                if (o.location.includes("Chennai")) locations.add("Chennai");
                if (o.location.includes("Noida") || o.location.includes("NCR")) locations.add("Delhi NCR");
                if (o.location.includes("Mumbai")) locations.add("Mumbai");
            }
        });
        locations.forEach(loc => {
            const opt = document.createElement("option");
            opt.value = loc;
            opt.textContent = loc;
            locationSelect.appendChild(opt);
        });
    }
}

function renderFilteredOpportunities() {
    const grid = document.getElementById("opportunities-grid");
    if (!grid) return;

    let items = allOpportunities.slice();

    // Tab filter
    if (activeTab === "saved") {
        items = items.filter(x => x.is_saved);
    }

    // Search
    if (currentFilter.search) {
        const q = currentFilter.search.toLowerCase();
        items = items.filter(x =>
            (x.company_name && x.company_name.toLowerCase().includes(q)) ||
            (x.role_title && x.role_title.toLowerCase().includes(q)) ||
            (x.location && x.location.toLowerCase().includes(q)) ||
            (Array.isArray(x.required_skills) && x.required_skills.some(s => s.toLowerCase().includes(q)))
        );
    }

    // Job type
    if (currentFilter.job_type && currentFilter.job_type !== "all") {
        const t = currentFilter.job_type.toLowerCase();
        items = items.filter(x => x.job_type && x.job_type.toLowerCase().includes(t));
    }

    // Status
    if (currentFilter.status && currentFilter.status !== "all") {
        const s = currentFilter.status.toLowerCase();
        items = items.filter(x => x.status && x.status.toLowerCase() === s);
    }

    // Location
    if (currentFilter.location && currentFilter.location !== "all") {
        const l = currentFilter.location.toLowerCase();
        items = items.filter(x => x.location && x.location.toLowerCase().includes(l));
    }

    if (items.length === 0) {
        grid.innerHTML = `
            <div class="empty-placements-state" style="grid-column: 1 / -1;">
                <div class="empty-placements-icon">🔍</div>
                <h3>No opportunities found</h3>
                <p>No verified recruitment drives match your current search or filter criteria.</p>
                <button class="btn btn-secondary btn-sm" onclick="document.getElementById('btn-clear-filters').click()">
                    Reset All Filters
                </button>
            </div>
        `;
        return;
    }

    grid.innerHTML = items.map(opp => renderOpportunityCardHtml(opp)).join("");
}

function renderOpportunityCardHtml(opp) {
    const isSaved = Boolean(opp.is_saved);
    const status = opp.status || "Currently Open";
    let statusClass = "badge-open";
    if (status === "Closing Soon") statusClass = "badge-closing";
    if (status === "Upcoming") statusClass = "badge-upcoming";
    if (status === "Closed") statusClass = "badge-closed";

    const skills = Array.isArray(opp.required_skills) ? opp.required_skills.slice(0, 5) : [];
    const skillsHtml = skills.map(s => `<span class="skill-tag-pill">${escapeHtml(s)}</span>`).join("");
    const moreSkillsCount = (opp.required_skills?.length || 0) - skills.length;
    const moreSkillsTag = moreSkillsCount > 0 ? `<span class="skill-tag-pill">+${moreSkillsCount} more</span>` : "";

    const initials = (opp.company_name || "CO").split(" ").map(w => w[0]).join("").substring(0, 2).toUpperCase();
    const logoSrc = opp.company_logo || "";

    const logoHtml = logoSrc
        ? `<img src="${escapeHtml(logoSrc)}" alt="${escapeHtml(opp.company_name)} logo" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
           <span style="display:none; font-weight:800; color:var(--primary); font-size:1.1rem;">${escapeHtml(initials)}</span>`
        : `<span style="font-weight:800; color:var(--primary); font-size:1.1rem;">${escapeHtml(initials)}</span>`;

    const myAppStatus = opp.my_application_status;
    const appTrackBadge = myAppStatus
        ? `<span class="badge badge-primary" style="font-size:0.75rem; padding:0.25rem 0.5rem;">Stage: ${escapeHtml(myAppStatus)}</span>`
        : "";

    return `
        <div class="opportunity-card" id="card-${escapeHtml(opp.id)}">
            <div>
                <div class="card-top-bar">
                    <div class="company-brand-meta">
                        <div class="company-logo-box">
                            ${logoHtml}
                        </div>
                        <div class="company-name-wrap">
                            <h3>
                                ${escapeHtml(opp.company_name)}
                                <span class="verified-icon" title="Verified Official Opportunity">
                                    <svg width="16" height="16" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                                    </svg>
                                </span>
                            </h3>
                            <span class="company-track-type">${escapeHtml(opp.job_type || "Full-time")}</span>
                        </div>
                    </div>
                    <div class="card-actions-top">
                        <button type="button" class="btn-bookmark ${isSaved ? 'bookmarked' : ''}" 
                                onclick="toggleSaveOpportunity('${escapeHtml(opp.id)}', event)" 
                                title="${isSaved ? 'Remove Bookmark' : 'Save Opportunity'}">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="${isSaved ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                                <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </button>
                    </div>
                </div>

                <h4 class="card-role-title">${escapeHtml(opp.role_title)}</h4>

                <div class="status-badge-row">
                    <span class="badge ${statusClass}">${escapeHtml(status)}</span>
                    <span class="badge-job-type">📍 ${escapeHtml(opp.location ? opp.location.split('(')[0].trim() : 'Pan India')}</span>
                    ${appTrackBadge}
                </div>

                <div class="opp-key-details">
                    <div class="opp-detail-item">
                        <span style="font-size:1.1rem;">💰</span>
                        <div>
                            <span class="detail-label">Package / CTC</span>
                            <span class="detail-val">${escapeHtml(opp.package_ctc || 'Not specified')}</span>
                        </div>
                    </div>
                    <div class="opp-detail-item">
                        <span style="font-size:1.1rem;">⏳</span>
                        <div>
                            <span class="detail-label">Deadline</span>
                            <span class="detail-val">${escapeHtml(opp.deadline_date || 'Rolling / Open')}</span>
                        </div>
                    </div>
                </div>

                <div class="eligibility-box" title="Eligibility Criteria">
                    <strong>Eligibility:</strong> ${escapeHtml(opp.eligibility_criteria ? opp.eligibility_criteria.substring(0, 115) + '...' : 'Not specified')}
                </div>

                <div class="card-skills-row">
                    <div class="skills-tags-list">
                        ${skillsHtml}
                        ${moreSkillsTag}
                    </div>
                </div>
            </div>

            <div>
                <div class="card-footer-meta">
                    <span>
                        Verified: <strong>${escapeHtml(opp.last_verified_at || 'Recent')}</strong>
                    </span>
                    <a href="${escapeHtml(opp.source_url || opp.apply_url)}" target="_blank" rel="noopener noreferrer" class="verified-source-link">
                        Official Notification ↗
                    </a>
                </div>

                <div class="card-action-buttons">
                    <button type="button" class="btn-prepare-action" onclick="openPrepareModal('${escapeHtml(opp.id)}')">
                        <span>⚡ Prepare for Company</span>
                    </button>
                    <a href="${escapeHtml(opp.apply_url)}" target="_blank" rel="noopener noreferrer" class="btn-apply-action">
                        Apply Official Portal ↗
                    </a>
                </div>

                <div style="display:flex; gap:0.5rem; margin-top:0.65rem;">
                    <button type="button" class="btn-details-action" style="flex:1;" onclick="openDetailsModal('${escapeHtml(opp.id)}')">
                        📋 Selection Rounds
                    </button>
                    <button type="button" class="btn-track-action" style="flex:1;" onclick="openTrackModal('${escapeHtml(opp.id)}')">
                        ${myAppStatus ? '📝 Update Track' : '+ Track App'}
                    </button>
                </div>
            </div>
        </div>
    `;
}

/* -------------------- TAB SWITCHING -------------------- */

function switchPlacementTab(tab) {
    activeTab = tab;
    document.querySelectorAll(".placement-tab-btn").forEach(btn => {
        btn.classList.toggle("active", btn.getAttribute("data-tab") === tab);
    });

    const oppGrid = document.getElementById("opportunities-grid");
    const trackerContainer = document.getElementById("tracker-container");
    const filterToolbar = document.getElementById("filter-toolbar");

    if (tab === "tracker") {
        if (oppGrid) oppGrid.style.display = "none";
        if (filterToolbar) filterToolbar.style.display = "none";
        if (trackerContainer) {
            trackerContainer.style.display = "block";
            loadApplicationTracker();
        }
    } else {
        if (oppGrid) oppGrid.style.display = "grid";
        if (filterToolbar) filterToolbar.style.display = "flex";
        if (trackerContainer) trackerContainer.style.display = "none";
        currentFilter.saved_only = (tab === "saved");
        renderFilteredOpportunities();
    }
}

/* -------------------- BOOKMARK / SAVE -------------------- */

async function toggleSaveOpportunity(oppId, event) {
    if (event) {
        event.stopPropagation();
        event.preventDefault();
    }

    if (!API.getToken()) {
        showToast("Please log in to save opportunities to your dashboard.", "warning");
        return;
    }

    try {
        const res = await API.post(`/api/placements/saved/${oppId}`);
        const opp = allOpportunities.find(x => x.id === oppId);
        if (opp && res) {
            opp.is_saved = res.is_saved;
            showToast(res.is_saved ? `Saved ${opp.company_name} to your bookmarks.` : `Removed ${opp.company_name} from bookmarks.`, "info");
        }
        await loadPlacementStats();
        renderFilteredOpportunities();
    } catch (e) {
        showToast("Could not update bookmark: " + (e.message || "Error"), "danger");
    }
}

/* -------------------- DETAILS & SELECTION ROUNDS MODAL -------------------- */

function openDetailsModal(oppId) {
    const opp = allOpportunities.find(x => x.id === oppId);
    if (!opp) return;

    const modal = document.getElementById("modal-opportunity-details");
    if (!modal) return;

    document.getElementById("modal-details-company").innerText = opp.company_name;
    document.getElementById("modal-details-role").innerText = opp.role_title;
    document.getElementById("modal-details-package").innerText = opp.package_ctc || "Not specified";
    document.getElementById("modal-details-location").innerText = opp.location || "Pan India";
    document.getElementById("modal-details-deadline").innerText = opp.deadline_date || "Rolling / Open";
    document.getElementById("modal-details-eligibility").innerText = opp.eligibility_criteria || "Not specified";

    const rounds = Array.isArray(opp.selection_rounds) ? opp.selection_rounds : [];
    const timelineEl = document.getElementById("modal-details-rounds-timeline");
    if (timelineEl) {
        if (rounds.length === 0) {
            timelineEl.innerHTML = `<p style="color:var(--text-muted); font-size:0.875rem;">Company selection pattern will be updated prior to the drive.</p>`;
        } else {
            timelineEl.innerHTML = rounds.map(r => `
                <div class="timeline-step">
                    <div class="timeline-bullet">${r.round_num || '•'}</div>
                    <div class="timeline-content">
                        <div class="timeline-title-row">
                            <span class="timeline-title">${escapeHtml(r.title || 'Recruitment Round')}</span>
                            ${r.duration ? `<span class="timeline-duration-badge">⏱️ ${escapeHtml(r.duration)}</span>` : ''}
                        </div>
                        <p class="timeline-pattern">${escapeHtml(r.description || '')}</p>
                        ${r.pattern ? `<p style="font-size:0.8125rem; color:var(--text-secondary); margin-bottom:0.4rem;"><strong>Format:</strong> ${escapeHtml(r.pattern)}</p>` : ''}
                        ${r.preparation_tips ? `<div class="timeline-tips">💡 <strong>Focus Tip:</strong> ${escapeHtml(r.preparation_tips)}</div>` : ''}
                    </div>
                </div>
            `).join("");
        }
    }

    const applyBtn = document.getElementById("modal-details-apply-btn");
    if (applyBtn) {
        applyBtn.href = opp.apply_url;
    }

    const prepBtn = document.getElementById("modal-details-prepare-btn");
    if (prepBtn) {
        prepBtn.onclick = () => {
            closeAllModals();
            openPrepareModal(oppId);
        };
    }

    modal.classList.add("open");
}

/* -------------------- PREPARE FOR THIS COMPANY MODAL -------------------- */

async function openPrepareModal(oppId) {
    const opp = allOpportunities.find(x => x.id === oppId);
    if (!opp) return;

    const modal = document.getElementById("modal-company-prepare");
    if (!modal) return;

    modal.classList.add("open");

    const contentBody = document.getElementById("modal-prepare-body");
    if (contentBody) {
        contentBody.innerHTML = `
            <div style="text-align:center; padding:3rem 1rem;">
                <div class="spinner" style="margin: 0 auto 1rem auto; width: 36px; height: 36px; border: 3px solid #e2e8f0; border-top-color: #4f46e5; border-radius: 50%; animation: spin 0.8s linear infinite;"></div>
                <h4 style="font-size:1.1rem; color:var(--text-primary); margin-bottom:0.35rem;">Analyzing Your Skill Match for ${escapeHtml(opp.company_name)}</h4>
                <p style="color:var(--text-muted); font-size:0.875rem;">Evaluating student profile, verified skills, and recruitment interview stages...</p>
            </div>
        `;
    }

    try {
        const plan = await API.post(`/api/placements/prepare/${oppId}`, {});
        if (!plan) throw new Error("Could not compute preparation plan.");

        renderPreparationPlanHtml(plan, opp);
    } catch (e) {
        if (contentBody) {
            contentBody.innerHTML = `
                <div class="empty-placements-state">
                    <div class="empty-placements-icon">⚠️</div>
                    <h3>Preparation Plan Generation Failed</h3>
                    <p>${escapeHtml(e.message || "An unexpected error occurred.")}</p>
                    <button class="btn btn-secondary btn-sm" onclick="openPrepareModal('${escapeHtml(oppId)}')">Retry</button>
                </div>
            `;
        }
    }
}

function renderPreparationPlanHtml(plan, opp) {
    const contentBody = document.getElementById("modal-prepare-body");
    if (!contentBody) return;

    const score = Math.round(plan.match_score || 0);
    let scoreColor = "#10b981"; // green
    if (score < 50) scoreColor = "#f59e0b"; // amber
    if (score < 25) scoreColor = "#ef4444"; // red

    const matchedHtml = (plan.matched_skills || []).length > 0
        ? plan.matched_skills.map(s => `<span class="matched-pill">✓ ${escapeHtml(s)}</span>`).join("")
        : `<p style="font-size:0.8rem; color:var(--text-muted);">No matched skills detected yet. Upload your resume in the Resume & Skills module to benchmark accurately.</p>`;

    const missingHtml = (plan.missing_skills || []).length > 0
        ? plan.missing_skills.map(s => `<span class="missing-pill">⚠️ ${escapeHtml(s)}</span>`).join("")
        : `<p style="font-size:0.8rem; color:#065f46;">Great job! You possess all primary prerequisite skills required for this drive.</p>`;

    const strategies = Array.isArray(plan.round_strategies) ? plan.round_strategies : [];
    const strategiesHtml = strategies.map(st => `
        <div style="background:var(--bg-page); border:1px solid var(--border); border-radius:var(--radius-md); padding:1rem 1.25rem; margin-bottom:0.75rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                <h5 style="font-size:0.9rem; font-weight:700; color:var(--text-primary); margin:0;">
                    Round ${st.round_num}: ${escapeHtml(st.title)}
                </h5>
            </div>
            <p style="font-size:0.825rem; color:var(--text-secondary); margin-bottom:0.5rem; line-height:1.45;">${escapeHtml(st.description)}</p>
            ${st.recommended_focus ? `
                <ul style="margin:0 0 0.5rem 1.25rem; padding:0; font-size:0.8rem; color:var(--text-primary);">
                    ${st.recommended_focus.map(f => `<li style="margin-bottom:0.25rem;">${escapeHtml(f)}</li>`).join("")}
                </ul>
            ` : ''}
            ${st.tips ? `<div class="timeline-tips" style="margin-top:0.4rem;">💡 <strong>Company Tip:</strong> ${escapeHtml(st.tips)}</div>` : ''}
        </div>
    `).join("");

    const actionItems = Array.isArray(plan.action_items) ? plan.action_items : [];
    const actionItemsHtml = actionItems.map(item => `
        <div style="display:flex; align-items:flex-start; gap:0.75rem; padding:0.65rem 0.85rem; background:#fff; border:1px solid var(--border); border-radius:var(--radius-sm); margin-bottom:0.5rem;">
            <span class="badge ${item.priority === 'High' ? 'badge-danger' : 'badge-primary'}" style="font-size:0.7rem; padding:0.2rem 0.45rem;">${escapeHtml(item.priority)}</span>
            <div style="flex:1;">
                <div style="font-size:0.85rem; font-weight:600; color:var(--text-primary);">${escapeHtml(item.action)}</div>
                <div style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(item.resource)}</div>
            </div>
        </div>
    `).join("");

    contentBody.innerHTML = `
        <!-- Match Score Banner -->
        <div class="match-score-banner">
            <div class="match-score-left">
                <div class="match-circle" style="border-color:${scoreColor};">
                    <span class="match-circle-val" style="color:${scoreColor};">${score}%</span>
                    <span class="match-circle-sub">MATCH</span>
                </div>
                <div>
                    <h4 style="font-size:1.15rem; font-weight:800; color:var(--text-primary); margin-bottom:0.2rem;">
                        ${escapeHtml(plan.company_name)} Alignment Score
                    </h4>
                    <p style="font-size:0.85rem; color:var(--text-muted); margin:0;">
                        Target Role: <strong>${escapeHtml(plan.role_title)}</strong>
                    </p>
                </div>
            </div>
            <div style="display:flex; gap:0.5rem;">
                <a href="dashboard.html#assessment" class="btn btn-primary btn-sm" style="display:flex; align-items:center; gap:0.35rem;">
                    ⏱️ Start 20-MCQ Exam
                </a>
                <a href="dashboard.html#roadmap" class="btn btn-secondary btn-sm" style="display:flex; align-items:center; gap:0.35rem;">
                    🗺️ 14-Week Roadmap
                </a>
            </div>
        </div>

        <!-- Skills breakdown columns -->
        <div class="match-skills-columns">
            <div class="match-skill-group">
                <h4 style="color:#065f46;">
                    <span>✓ Matched Skills (${plan.matched_skills?.length || 0})</span>
                </h4>
                <div>${matchedHtml}</div>
            </div>
            <div class="match-skill-group">
                <h4 style="color:#92400e;">
                    <span>⚠️ Skill Gaps to Bridge (${plan.missing_skills?.length || 0})</span>
                </h4>
                <div>${missingHtml}</div>
            </div>
        </div>

        <!-- Action Items -->
        <div>
            <h4 style="font-size:0.95rem; font-weight:700; color:var(--text-primary); margin-bottom:0.65rem;">
                🎯 Recommended Preparation Actions
            </h4>
            ${actionItemsHtml}
        </div>

        <!-- Round-by-Round Breakdown -->
        <div>
            <h4 style="font-size:0.95rem; font-weight:700; color:var(--text-primary); margin-bottom:0.65rem;">
                🏢 ${escapeHtml(plan.company_name)} Round-by-Round Mastery Strategy
            </h4>
            ${strategiesHtml}
        </div>

        <!-- Modal footer actions inside body -->
        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border); padding-top:1.25rem;">
            <span style="font-size:0.8rem; color:var(--text-muted);">
                Data synchronized with your SkillForge profile
            </span>
            <div style="display:flex; gap:0.75rem;">
                <button type="button" class="btn btn-secondary btn-sm" onclick="closeAllModals()">Close</button>
                <a href="${escapeHtml(opp.apply_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">
                    Apply on Official Portal ↗
                </a>
            </div>
        </div>
    `;
}

/* -------------------- APPLICATION TRACKER -------------------- */

async function loadApplicationTracker() {
    const tableBody = document.getElementById("tracker-table-body");
    if (!tableBody) return;

    tableBody.innerHTML = `
        <tr>
            <td colspan="6" style="text-align:center; padding:2rem; color:var(--text-muted);">
                Loading your tracked applications...
            </td>
        </tr>
    `;

    try {
        const res = await API.get("/api/placements/applications");
        const apps = res && res.applications ? res.applications : [];

        if (apps.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align:center; padding:3rem 1rem;">
                        <div style="font-size:2rem; margin-bottom:0.5rem;">📁</div>
                        <h4 style="font-size:1.05rem; font-weight:700; color:var(--text-primary); margin-bottom:0.25rem;">No Applications Tracked Yet</h4>
                        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:1rem;">
                            Track your recruitment journey by clicking "+ Track App" on any company card.
                        </p>
                        <button class="btn btn-primary btn-sm" onclick="switchPlacementTab('all')">
                            Explore Upcoming Drives
                        </button>
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = apps.map(app => {
            const opp = app.opportunity || {};
            const stages = ["Interested", "Preparing", "Applied", "Assessment Completed", "Interview Scheduled", "Selected", "Rejected"];
            const optionsHtml = stages.map(st => `<option value="${st}" ${app.status === st ? 'selected' : ''}>${st}</option>`).join("");

            return `
                <tr id="tracker-row-${escapeHtml(app.id)}">
                    <td>
                        <div style="font-weight:700; color:var(--text-primary);">${escapeHtml(opp.company_name || 'Company')}</div>
                        <div style="font-size:0.75rem; color:var(--text-muted);">${escapeHtml(opp.role_title || 'Role')}</div>
                    </td>
                    <td>
                        <span class="badge badge-primary" style="font-size:0.75rem;">${escapeHtml(opp.job_type || 'Full-time')}</span>
                    </td>
                    <td>
                        <select class="tracker-stage-select" onchange="updateApplicationStage('${escapeHtml(app.opportunity_id)}', this.value)">
                            ${optionsHtml}
                        </select>
                    </td>
                    <td>
                        <input type="date" value="${escapeHtml(app.applied_date || '')}" 
                               style="padding:0.3rem 0.5rem; font-size:0.8rem; border:1px solid var(--border); border-radius:var(--radius-sm);"
                               onchange="updateApplicationDate('${escapeHtml(app.opportunity_id)}', this.value)" />
                    </td>
                    <td>
                        <input type="text" placeholder="Add interview notes..." value="${escapeHtml(app.notes || '')}"
                               style="width:100%; max-width:200px; padding:0.3rem 0.5rem; font-size:0.8rem; border:1px solid var(--border); border-radius:var(--radius-sm);"
                               onblur="updateApplicationNotes('${escapeHtml(app.opportunity_id)}', this.value)" />
                    </td>
                    <td>
                        <div style="display:flex; align-items:center; gap:0.5rem;">
                            <a href="${escapeHtml(opp.apply_url || '#')}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-xs" style="padding:0.25rem 0.5rem; font-size:0.75rem;">
                                Portal ↗
                            </a>
                            <button type="button" class="btn btn-secondary btn-xs" style="padding:0.25rem 0.5rem; font-size:0.75rem; color:var(--danger-text);"
                                    onclick="deleteTrackedApplication('${escapeHtml(app.opportunity_id)}')">
                                ✕
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join("");

    } catch (e) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align:center; padding:2rem; color:var(--danger-text);">
                    Failed to load applications: ${escapeHtml(e.message || "Error")}
                </td>
            </tr>
        `;
    }
}

async function openTrackModal(oppId) {
    const opp = allOpportunities.find(x => x.id === oppId);
    if (!opp) return;

    if (!API.getToken()) {
        showToast("Please log in to track your applications.", "warning");
        return;
    }

    const currentStatus = opp.my_application_status || "Interested";
    const modal = document.getElementById("modal-track-app");
    if (!modal) return;

    document.getElementById("track-modal-company").innerText = opp.company_name;
    document.getElementById("track-modal-role").innerText = opp.role_title;
    document.getElementById("track-modal-opp-id").value = oppId;
    document.getElementById("track-modal-status").value = currentStatus;

    modal.classList.add("open");
}

async function saveTrackModalSubmission() {
    const oppId = document.getElementById("track-modal-opp-id").value;
    const statusVal = document.getElementById("track-modal-status").value;
    const appliedDate = document.getElementById("track-modal-date").value;
    const notesVal = document.getElementById("track-modal-notes").value;

    try {
        await API.post("/api/placements/applications", {
            opportunity_id: oppId,
            status: statusVal,
            applied_date: appliedDate || undefined,
            notes: notesVal
        });

        const opp = allOpportunities.find(x => x.id === oppId);
        if (opp) opp.my_application_status = statusVal;

        showToast("Application tracking updated successfully!", "success");
        closeAllModals();
        await loadPlacementStats();
        renderFilteredOpportunities();
    } catch (e) {
        showToast("Failed to update application tracker: " + (e.message || "Error"), "danger");
    }
}

async function updateApplicationStage(oppId, newStatus) {
    try {
        await API.post("/api/placements/applications", {
            opportunity_id: oppId,
            status: newStatus
        });
        const opp = allOpportunities.find(x => x.id === oppId);
        if (opp) opp.my_application_status = newStatus;

        showToast(`Updated status to: ${newStatus}`, "info");
        await loadPlacementStats();
    } catch (e) {
        showToast("Failed to update status: " + (e.message || "Error"), "danger");
    }
}

async function updateApplicationDate(oppId, newDate) {
    try {
        await API.post("/api/placements/applications", {
            opportunity_id: oppId,
            applied_date: newDate
        });
        showToast("Updated application date.", "info");
    } catch (e) {
        showToast("Failed to update date.", "danger");
    }
}

async function updateApplicationNotes(oppId, newNotes) {
    try {
        await API.post("/api/placements/applications", {
            opportunity_id: oppId,
            notes: newNotes
        });
    } catch (e) {
        console.warn("Failed to sync notes:", e);
    }
}

async function deleteTrackedApplication(oppId) {
    if (!confirm("Are you sure you want to remove this opportunity from your tracker?")) return;
    try {
        await API.delete(`/api/placements/applications/${oppId}`);
        const opp = allOpportunities.find(x => x.id === oppId);
        if (opp) opp.my_application_status = null;

        showToast("Removed from application tracker.", "info");
        await loadPlacementStats();
        loadApplicationTracker();
        renderFilteredOpportunities();
    } catch (e) {
        showToast("Failed to remove application.", "danger");
    }
}

/* -------------------- UTILITIES -------------------- */

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
