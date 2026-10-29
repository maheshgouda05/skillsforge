/**
 * Resume Parsing & Skill Alignment Module
 */

let currentExtractedSkills = [];

function initResumeModule() {
    const dropzone = document.getElementById("resume-dropzone");
    const fileInput = document.getElementById("resume-file-input");

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener("click", () => fileInput.click());

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleResumeFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", (e) => {
        if (e.target.files && e.target.files[0]) {
            handleResumeFile(e.target.files[0]);
        }
    });

    const hoursRange = document.getElementById("study-hours-input");
    const hoursLabel = document.getElementById("study-hours-display");
    if (hoursRange && hoursLabel) {
        hoursRange.addEventListener("input", (e) => {
            hoursLabel.innerText = `${e.target.value} hrs/week`;
        });
    }
}

async function handleResumeFile(file) {
    if (!file) return;

    const validExtensions = ["pdf", "docx", "doc", "txt"];
    const ext = file.name.split(".").pop().toLowerCase();
    if (!validExtensions.includes(ext)) {
        showToast("Please upload a PDF, DOCX, or TXT file.", "error");
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        showToast("File size exceeds 5MB limit.", "error");
        return;
    }

    const dropzone = document.getElementById("resume-dropzone");
    dropzone.innerHTML = `
        <div class="upload-icon">⏳</div>
        <h4>Extracting skills from ${escapeHtml(file.name)}...</h4>
        <p class="form-hint">Analyzing document text via PyMuPDF</p>
    `;

    const formData = new FormData();
    formData.append("resume", file);

    try {
        const res = await API.upload("/api/resume/parse", formData);
        showToast("Resume parsed successfully!", "success");

        dropzone.innerHTML = `
            <div class="upload-icon" style="color: var(--success);">✓</div>
            <h4>${escapeHtml(file.name)}</h4>
            <p class="form-hint">${(file.size / 1024).toFixed(1)} KB &bull; Extracted ${res.detected_skills.length} skills</p>
            <button type="button" class="btn btn-secondary btn-sm" style="margin-top: 0.5rem;" onclick="document.getElementById('resume-file-input').click()">Replace File</button>
        `;

        currentExtractedSkills = [...res.detected_skills];
        renderSkillTags();

        // Reveal the candidate skills editor and target job selection
        document.getElementById("resume-analysis-controls").style.display = "block";

    } catch (err) {
        showToast(err.message || "Failed to extract text from resume.", "error");
        dropzone.innerHTML = `
            <div class="upload-icon">📄</div>
            <h4>Upload your resume (PDF, DOCX, or TXT)</h4>
            <p class="form-hint">Drag & drop or click to browse (Max 5MB)</p>
        `;
    }
}

function renderSkillTags() {
    const container = document.getElementById("extracted-skills-tags");
    if (!container) return;

    if (currentExtractedSkills.length === 0) {
        container.innerHTML = `<span style="font-size: 0.85rem; color: var(--text-muted);">No skills added yet. Type below or upload a resume.</span>`;
        return;
    }

    container.innerHTML = currentExtractedSkills.map((skill, idx) => `
        <span class="skill-tag">
            ${escapeHtml(skill)}
            <span class="skill-tag-remove" onclick="removeSkillTag(${idx})" title="Remove skill">&times;</span>
        </span>
    `).join("");
}

function removeSkillTag(index) {
    currentExtractedSkills.splice(index, 1);
    renderSkillTags();
}

function addCustomSkill() {
    const input = document.getElementById("custom-skill-input");
    const val = input.value.trim().toLowerCase();
    if (!val) return;

    if (!currentExtractedSkills.includes(val)) {
        currentExtractedSkills.push(val);
        renderSkillTags();
    }
    input.value = "";
}

async function runCompleteAnalysis() {
    const btn = document.getElementById("btn-run-analysis");
    btn.disabled = true;
    btn.innerHTML = `<span>⏳ Analyzing with Gemini AI...</span>`;

    const targetRole = document.getElementById("target-role-select").value;
    const jobDescription = document.getElementById("job-desc-input").value;
    const hours = parseInt(document.getElementById("study-hours-input").value, 10) || 8;

    const formData = new FormData();
    formData.append("target_role", targetRole);
    formData.append("job_description", jobDescription);
    formData.append("candidate_skills", JSON.stringify(currentExtractedSkills));
    formData.append("hours_per_week", hours);

    const fileInput = document.getElementById("resume-file-input");
    if (fileInput && fileInput.files && fileInput.files[0]) {
        formData.append("resume", fileInput.files[0]);
    }

    try {
        const analysis = await API.upload("/api/analyze", formData);
        showToast("Analysis complete!", "success");
        renderAnalysisResults(analysis);

        // Update dashboard cache
        if (typeof loadDashboardData === "function") {
            loadDashboardData();
        }
    } catch (err) {
        showToast(err.message || "Failed to analyze skills.", "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>🚀 Run Complete Skill Gap Analysis</span>`;
    }
}

function renderAnalysisResults(analysis) {
    const resultContainer = document.getElementById("analysis-result-container");
    if (!resultContainer) return;

    resultContainer.style.display = "block";

    document.getElementById("result-match-score").innerText = `${analysis.match_percentage}%`;
    document.getElementById("result-target-role").innerText = analysis.target_role;

    // AI Coaching advice
    const adviceEl = document.getElementById("result-ai-advice");
    if (adviceEl && analysis.ai_insights) {
        adviceEl.innerText = analysis.ai_insights.coaching_advice || "";
    }

    // Strong skills
    const strongList = document.getElementById("result-strong-skills");
    if (strongList) {
        strongList.innerHTML = (analysis.strong_skills || []).length > 0
            ? analysis.strong_skills.map(s => `<span class="badge badge-success">${escapeHtml(s.skill || s)}</span>`).join(" ")
            : `<span style="font-size: 0.85rem; color: var(--text-muted);">None identified yet</span>`;
    }

    // Missing skills
    const missingList = document.getElementById("result-missing-skills");
    if (missingList) {
        missingList.innerHTML = (analysis.missing_skills || []).length > 0
            ? analysis.missing_skills.map(s => `<span class="badge badge-slate">${escapeHtml(s.skill || s)}</span>`).join(" ")
            : `<span style="font-size: 0.85rem; color: var(--text-muted);">All core skills present</span>`;
    }

    resultContainer.scrollIntoView({ behavior: "smooth" });
}
