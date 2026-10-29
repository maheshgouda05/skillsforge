/**
 * 20-MCQ Technical Assessment Engine
 */

let activeAssessment = null;
let currentQuestionIndex = 0;
let userAnswers = {};
let flaggedQuestions = {};
let timerInterval = null;
let timeRemainingSeconds = 0;

async function startAssessment() {
    const roleSelect = document.getElementById("assessment-role-select");
    const targetRole = roleSelect ? roleSelect.value : "Full Stack Developer";

    const btn = document.getElementById("btn-start-assessment");
    if (btn) {
        btn.disabled = true;
        btn.innerText = "Generating 20-Question Exam...";
    }

    try {
        const res = await API.post("/api/assessment/generate", {
            target_role: targetRole,
            count: 20
        });

        activeAssessment = res;
        userAnswers = {};
        flaggedQuestions = {};
        currentQuestionIndex = 0;
        timeRemainingSeconds = (res.timer_minutes || 25) * 60;

        // Hide intro, show exam view
        document.getElementById("assessment-intro").style.display = "none";
        document.getElementById("assessment-results").style.display = "none";
        document.getElementById("assessment-active").style.display = "block";

        renderQuestionPalette();
        renderActiveQuestion();
        startTimer();

        showToast("Assessment started! 25-minute timer running.", "info");

    } catch (err) {
        showToast(err.message || "Failed to generate assessment.", "error");
        if (btn) {
            btn.disabled = false;
            btn.innerText = "Start 20-Question Assessment";
        }
    }
}

function startTimer() {
    clearInterval(timerInterval);
    const timerDisplay = document.getElementById("timer-display");
    const timerPill = document.getElementById("timer-pill");

    function update() {
        if (timeRemainingSeconds <= 0) {
            clearInterval(timerInterval);
            timerDisplay.innerText = "00:00";
            showToast("Time's up! Automatically submitting your assessment...", "warning");
            submitAssessment(true);
            return;
        }

        const mins = Math.floor(timeRemainingSeconds / 60);
        const secs = timeRemainingSeconds % 60;
        timerDisplay.innerText = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;

        if (timeRemainingSeconds < 300) {
            timerPill.classList.add("urgent");
        } else {
            timerPill.classList.remove("urgent");
        }

        timeRemainingSeconds--;
    }

    update();
    timerInterval = setInterval(update, 1000);
}

function renderActiveQuestion() {
    if (!activeAssessment || !activeAssessment.questions) return;

    const q = activeAssessment.questions[currentQuestionIndex];
    const total = activeAssessment.questions.length;

    document.getElementById("q-counter").innerText = `Question ${currentQuestionIndex + 1} of ${total}`;
    document.getElementById("q-skill-badge").innerText = q.skill || "Technical";
    document.getElementById("q-difficulty-badge").innerText = q.difficulty || "medium";
    document.getElementById("q-text").innerText = q.question;

    // Render options
    const optionsContainer = document.getElementById("q-options-container");
    const letters = ["A", "B", "C", "D"];
    const currentSelected = userAnswers[String(q.id)];

    optionsContainer.innerHTML = q.options.map((opt, idx) => {
        const isSelected = currentSelected === idx;
        return `
            <div class="option-card ${isSelected ? 'selected' : ''}" onclick="selectOption(${idx})">
                <span class="option-letter">${letters[idx]}</span>
                <span class="option-label" style="font-weight: 500;">${escapeHtml(opt)}</span>
            </div>
        `;
    }).join("");

    // Nav button states
    document.getElementById("btn-prev-q").disabled = currentQuestionIndex === 0;
    const nextBtn = document.getElementById("btn-next-q");
    if (currentQuestionIndex === total - 1) {
        nextBtn.innerText = "Review & Submit";
        nextBtn.onclick = () => confirmSubmitModal();
    } else {
        nextBtn.innerText = "Next Question →";
        nextBtn.onclick = () => nextQuestion();
    }

    // Flag button state
    const flagBtn = document.getElementById("btn-flag-q");
    const isFlagged = Boolean(flaggedQuestions[String(q.id)]);
    flagBtn.innerText = isFlagged ? "🚩 Flagged" : "⚑ Flag for Review";
    flagBtn.classList.toggle("btn-warning", isFlagged);
    flagBtn.classList.toggle("btn-secondary", !isFlagged);

    updatePaletteState();
}

function selectOption(index) {
    if (!activeAssessment) return;
    const q = activeAssessment.questions[currentQuestionIndex];
    userAnswers[String(q.id)] = index;
    renderActiveQuestion();
}

function toggleFlagQuestion() {
    if (!activeAssessment) return;
    const q = activeAssessment.questions[currentQuestionIndex];
    const qId = String(q.id);
    flaggedQuestions[qId] = !flaggedQuestions[qId];
    renderActiveQuestion();
}

function nextQuestion() {
    if (currentQuestionIndex < activeAssessment.questions.length - 1) {
        currentQuestionIndex++;
        renderActiveQuestion();
    }
}

function prevQuestion() {
    if (currentQuestionIndex > 0) {
        currentQuestionIndex--;
        renderActiveQuestion();
    }
}

function jumpToQuestion(index) {
    if (index >= 0 && index < activeAssessment.questions.length) {
        currentQuestionIndex = index;
        renderActiveQuestion();
    }
}

function renderQuestionPalette() {
    const palette = document.getElementById("palette-grid");
    if (!palette || !activeAssessment) return;

    palette.innerHTML = activeAssessment.questions.map((q, idx) => `
        <button type="button" class="palette-btn" id="palette-btn-${idx}" onclick="jumpToQuestion(${idx})">
            ${idx + 1}
        </button>
    `).join("");
}

function updatePaletteState() {
    if (!activeAssessment) return;

    activeAssessment.questions.forEach((q, idx) => {
        const btn = document.getElementById(`palette-btn-${idx}`);
        if (!btn) return;

        btn.className = "palette-btn";
        const qId = String(q.id);

        if (userAnswers[qId] !== undefined) {
            btn.classList.add("answered");
        }
        if (flaggedQuestions[qId]) {
            btn.classList.add("flagged");
        }
        if (idx === currentQuestionIndex) {
            btn.classList.add("active");
        }
    });
}

function confirmSubmitModal() {
    const total = activeAssessment.questions.length;
    const answeredCount = Object.keys(userAnswers).length;
    const unAnswered = total - answeredCount;

    const confirmed = confirm(
        `Are you ready to submit your assessment?\n\n` +
        `• Answered: ${answeredCount} / ${total}\n` +
        `• Unanswered: ${unAnswered}\n\n` +
        `Click OK to finalize and grade your score.`
    );

    if (confirmed) {
        submitAssessment(false);
    }
}

async function submitAssessment(isAuto = false) {
    clearInterval(timerInterval);

    try {
        const res = await API.post("/api/assessment/submit", {
            assessment_id: activeAssessment.assessment_id,
            answers: userAnswers
        });

        showToast("Assessment evaluated successfully!", "success");
        renderAssessmentResults(res);

        // Update dashboard cache
        if (typeof loadDashboardData === "function") {
            loadDashboardData();
        }

    } catch (err) {
        showToast(err.message || "Failed to submit assessment.", "error");
    }
}

function renderAssessmentResults(res) {
    document.getElementById("assessment-active").style.display = "none";
    const resultsContainer = document.getElementById("assessment-results");
    resultsContainer.style.display = "block";

    document.getElementById("final-score-percent").innerText = `${res.overall_score_percent}%`;
    document.getElementById("final-score-fraction").innerText = `${res.total_correct} of ${res.total_questions} questions correct`;

    // Grade badge
    const badge = document.getElementById("score-grade-badge");
    if (res.overall_score_percent >= 80) {
        badge.className = "badge badge-success";
        badge.innerText = "Advanced Proficiency";
    } else if (res.overall_score_percent >= 50) {
        badge.className = "badge badge-primary";
        badge.innerText = "Intermediate Competence";
    } else {
        badge.className = "badge badge-warning";
        badge.innerText = "Foundational / Needs Reinforcement";
    }

    // Topic breakdown
    const topicContainer = document.getElementById("skill-breakdown-bars");
    if (topicContainer && res.skill_results) {
        topicContainer.innerHTML = Object.entries(res.skill_results).map(([skill, data]) => `
            <div style="margin-bottom: 0.875rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.875rem; font-weight: 600; margin-bottom: 0.35rem;">
                    <span style="text-transform: capitalize;">${escapeHtml(skill)}</span>
                    <span>${data.score_percent}% (${data.correct}/${data.total})</span>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar-fill" style="width: ${data.score_percent}%;"></div>
                </div>
            </div>
        `).join("");
    }

    // Full Answer Key & Explanation Review
    const reviewContainer = document.getElementById("answer-review-list");
    if (reviewContainer && res.review) {
        reviewContainer.innerHTML = res.review.map((item, idx) => {
            const letters = ["A", "B", "C", "D"];
            const isCorrect = item.is_correct;
            return `
                <div class="card" style="margin-bottom: 1rem; border-left: 4px solid ${isCorrect ? 'var(--success)' : 'var(--danger)'};">
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span style="font-weight: 700; font-size: 0.9rem;">Question ${idx + 1} (${escapeHtml(item.skill)})</span>
                        <span class="badge ${isCorrect ? 'badge-success' : 'badge-danger'}">
                            ${isCorrect ? '✓ Correct' : '✕ Incorrect'}
                        </span>
                    </div>
                    <p style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.75rem;">${escapeHtml(item.question)}</p>
                    <div style="font-size: 0.85rem; margin-bottom: 0.5rem;">
                        <div><strong>Your Answer:</strong> ${item.user_answer !== null && item.user_answer !== undefined ? escapeHtml(item.options[item.user_answer]) : '<span style="color: var(--text-muted);">(Unanswered)</span>'}</div>
                        <div style="color: var(--success-text); margin-top: 0.25rem;"><strong>Correct Answer:</strong> ${escapeHtml(item.options[item.correct_answer])}</div>
                    </div>
                    <div style="background-color: var(--bg-surface-alt); padding: 0.5rem 0.75rem; border-radius: var(--radius-sm); font-size: 0.8125rem; color: var(--text-muted);">
                        💡 <strong>Explanation:</strong> ${escapeHtml(item.explanation)}
                    </div>
                </div>
            `;
        }).join("");
    }

    resultsContainer.scrollIntoView({ behavior: "smooth" });
}

function retakeAssessment() {
    document.getElementById("assessment-results").style.display = "none";
    document.getElementById("assessment-intro").style.display = "block";
    const btn = document.getElementById("btn-start-assessment");
    if (btn) {
        btn.disabled = false;
        btn.innerText = "Start 20-Question Assessment";
    }
}

