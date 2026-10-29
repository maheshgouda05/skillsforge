/**
 * Weekly Assessment & Adaptive Roadmap Learning Engine
 */

let activeWeeklyTest = null;
let weeklyAnswers = {};

async function launchWeeklyQuiz(skill, week) {
    switchTab("weekly-test");

    document.getElementById("weekly-skill-input").value = skill;
    document.getElementById("weekly-week-input").value = week;

    await generateWeeklyTest();
}

async function generateWeeklyTest() {
    const skill = document.getElementById("weekly-skill-input").value.trim().toLowerCase();
    const week = parseInt(document.getElementById("weekly-week-input").value, 10) || 1;

    if (!skill) {
        showToast("Please specify a skill to test.", "warning");
        return;
    }

    const btn = document.getElementById("btn-generate-weekly");
    if (btn) {
        btn.disabled = true;
        btn.innerText = "Generating Quiz...";
    }

    try {
        const res = await API.post("/api/weekly-test/generate", {
            skill: skill,
            week: week,
            count: 5
        });

        activeWeeklyTest = res;
        weeklyAnswers = {};

        document.getElementById("weekly-test-intro").style.display = "none";
        document.getElementById("weekly-test-results").style.display = "none";
        document.getElementById("weekly-test-active").style.display = "block";

        renderWeeklyQuestions(res);
        showToast(`Week ${week} quiz for ${skill.toUpperCase()} loaded!`, "info");

    } catch (err) {
        showToast(err.message || "Failed to generate weekly quiz.", "error");
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = "Start Weekly Quiz";
        }
    }
}

function renderWeeklyQuestions(testData) {
    document.getElementById("weekly-quiz-title").innerText = `Week ${testData.week} Assessment: ${testData.skill.toUpperCase()}`;
    const container = document.getElementById("weekly-questions-container");
    const letters = ["A", "B", "C", "D"];

    container.innerHTML = testData.questions.map((q, qIdx) => `
        <div class="card" style="margin-bottom: 1.25rem;">
            <div style="font-size: 0.85rem; font-weight: 700; color: var(--text-muted); margin-bottom: 0.35rem;">
                Question ${qIdx + 1} of ${testData.questions.length}
            </div>
            <p style="font-weight: 700; font-size: 1.05rem; margin-bottom: 1rem;">${escapeHtml(q.question)}</p>
            <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                ${q.options.map((opt, optIdx) => `
                    <label class="option-card" id="weekly-opt-${q.id}-${optIdx}" onclick="selectWeeklyOption('${q.id}', ${optIdx})">
                        <span class="option-letter">${letters[optIdx]}</span>
                        <span style="font-weight: 500;">${escapeHtml(opt)}</span>
                    </label>
                `).join("")}
            </div>
        </div>
    `).join("");
}

function selectWeeklyOption(questionId, optionIndex) {
    weeklyAnswers[questionId] = optionIndex;

    // Visual selection
    const question = activeWeeklyTest.questions.find(q => String(q.id) === String(questionId));
    if (question) {
        question.options.forEach((_, idx) => {
            const card = document.getElementById(`weekly-opt-${questionId}-${idx}`);
            if (card) {
                card.classList.toggle("selected", idx === optionIndex);
            }
        });
    }
}

async function submitWeeklyTest() {
    if (!activeWeeklyTest) return;

    const total = activeWeeklyTest.questions.length;
    const answered = Object.keys(weeklyAnswers).length;

    if (answered < total) {
        const proceed = confirm(`You have answered ${answered} of ${total} questions. Submit anyway?`);
        if (!proceed) return;
    }

    const btn = document.getElementById("btn-submit-weekly");
    btn.disabled = true;
    btn.innerText = "Evaluating...";

    try {
        const res = await API.post("/api/weekly-test/submit", {
            test_id: activeWeeklyTest.test_id,
            answers: weeklyAnswers
        });

        showToast("Weekly test submitted!", "success");
        renderWeeklyResults(res);

    } catch (err) {
        showToast(err.message || "Failed to submit weekly test.", "error");
    } finally {
        btn.disabled = false;
        btn.innerText = "Submit & Evaluate";
    }
}

function renderWeeklyResults(res) {
    document.getElementById("weekly-test-active").style.display = "none";
    const container = document.getElementById("weekly-test-results");
    container.style.display = "block";

    document.getElementById("weekly-score-display").innerText = `${res.score_percent}%`;
    document.getElementById("weekly-fraction-display").innerText = `${res.correct_count} of ${res.total_questions} correct`;

    const rec = res.adaptive_recommendation || {};
    document.getElementById("adaptive-mastery-tier").innerText = rec.mastery_tier || "Evaluation Complete";
    document.getElementById("adaptive-advice-text").innerText = rec.recommendation_summary || "";

    // Save test_id and week for adaptation trigger
    document.getElementById("btn-apply-adaptation").onclick = () => applyAdaptivePlan(res.test_id, res.week, res.skill, res.score_percent);

    container.scrollIntoView({ behavior: "smooth" });
}

async function applyAdaptivePlan(testId, completedWeek, skill, scorePercent) {
    const btn = document.getElementById("btn-apply-adaptation");
    btn.disabled = true;
    btn.innerText = "Adapting Upcoming Curriculum...";

    try {
        const planRes = await API.get("/api/planner/current");
        if (!planRes || !planRes.has_plan) {
            showToast("No active learning plan found to adapt.", "warning");
            return;
        }

        const adaptRes = await API.post("/api/planner/adapt", {
            plan_id: planRes.plan_id,
            completed_week: completedWeek,
            test_id: testId,
            skill: skill,
            score_percent: scorePercent
        });

        showToast(adaptRes.message, "success");

        // Reload roadmap and switch to it
        await loadRoadmapModule();
        switchTab("roadmap");

    } catch (err) {
        showToast(err.message || "Failed to apply adaptation.", "error");
    } finally {
        btn.disabled = false;
        btn.innerText = "Apply Adaptive Changes to Roadmap →";
    }
}

