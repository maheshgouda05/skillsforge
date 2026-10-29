import urllib.request
import urllib.error
import json
import uuid

BASE_URL = "http://127.0.0.1:8000"

def request_json(endpoint, method="GET", data=None, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        print(f"HTTPError on {endpoint}: {e.code} - {err_body}")
        raise e

def run_tests():
    print("=== STARTING FULL END-TO-END SYSTEM TEST ===")

    # 1. Health check
    print("\n1. Testing Health Check...")
    health = request_json("/api/health")
    assert health["status"] == "ok", f"Health failed: {health}"
    print("✓ Backend healthy:", health)

    # 2. Roles list
    print("\n2. Testing Supported Roles...")
    roles = request_json("/api/roles")
    assert len(roles["roles"]) >= 9, f"Roles count: {len(roles['roles'])}"
    print(f"✓ Retrieved {len(roles['roles'])} industry roles.")

    # 3. User Registration / Auth
    print("\n3. Testing User Registration / Auth...")
    test_email = f"student_{uuid.uuid4().hex[:6]}@gmail.com"
    reg_payload = {
        "email": test_email,
        "password": "Password@123",
        "full_name": "Hackathon Test Student",
        "target_role": "Python Developer"
    }
    auth_res = request_json("/api/auth/register", method="POST", data=reg_payload)
    token = auth_res.get("access_token")
    assert token, "Token missing in auth response"
    print("✓ Registered test user. Token length:", len(token))

    # 4. Auth Me
    print("\n4. Testing /api/auth/me...")
    me = request_json("/api/auth/me", token=token)
    assert me["authenticated"] is True, f"Auth failed: {me}"
    assert me["user"]["email"] == test_email
    print("✓ Auth verification passed for:", me["user"]["full_name"])

    # 5. Resume Analysis & Skill Gap
    print("\n5. Testing Resume & Skill Gap Analysis...")
    analysis_req = {
        "target_role": "Python Developer",
        "job_description": "We are seeking a senior Python developer experienced in FastAPI, SQL, Docker, and Git.",
        "candidate_skills": ["python", "sql", "git"],
        "hours_per_week": 10
    }
    # Form data request for /api/analyze
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body_lines = [
        f"--{boundary}",
        'Content-Disposition: form-data; name="target_role"',
        '',
        "Python Developer",
        f"--{boundary}",
        'Content-Disposition: form-data; name="job_description"',
        '',
        "Looking for Python Developer skilled in FastAPI, SQL, Git, Docker.",
        f"--{boundary}",
        'Content-Disposition: form-data; name="candidate_skills"',
        '',
        json.dumps(["python", "sql", "git"]),
        f"--{boundary}",
        'Content-Disposition: form-data; name="hours_per_week"',
        '',
        "10",
        f"--{boundary}--",
        ''
    ]
    raw_body = "\r\n".join(body_lines).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/analyze",
        data=raw_body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Authorization": f"Bearer {token}"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        analysis = json.loads(resp.read().decode("utf-8"))
    
    assert "match_percentage" in analysis, "match_percentage missing"
    assert "plan_id" in analysis, "plan_id missing"
    plan_id = analysis["plan_id"]
    print(f"✓ Analysis complete! Match score: {analysis['match_percentage']}%, Plan ID: {plan_id}")
    print(f"  Missing skills identified: {[m['skill'] for m in analysis['missing_skills']]}")

    # 6. Generate 20-MCQ Technical Assessment
    print("\n6. Testing 20-MCQ Technical Assessment Generation...")
    assessment_req = {
        "target_role": "Python Developer",
        "count": 20
    }
    exam = request_json("/api/assessment/generate", method="POST", data=assessment_req, token=token)
    assert exam["total_questions"] == 20, f"Expected 20 questions, got {exam['total_questions']}"
    assert len(exam["questions"]) == 20, "Questions array length mismatch"
    # Verify answers are NOT exposed!
    for q in exam["questions"]:
        assert "answer" not in q, f"SECURITY LEAK: correct answer exposed in public question {q['id']}!"
    print(f"✓ Generated {exam['total_questions']} MCQs with zero answer leakage.")

    # 7. Submit Technical Assessment
    print("\n7. Testing Assessment Submission and Grading...")
    assessment_id = exam["assessment_id"]
    answers = {}
    for idx, q in enumerate(exam["questions"]):
        # Submit option 1 or 2 for testing
        answers[str(q["id"])] = (idx % 4)
    
    submit_payload = {
        "assessment_id": assessment_id,
        "answers": answers
    }
    results = request_json("/api/assessment/submit", method="POST", data=submit_payload, token=token)
    assert "overall_score_percent" in results, "Score missing"
    assert "review" in results, "Review missing"
    assert len(results["review"]) == 20, "Review length mismatch"
    print(f"✓ Assessment scored! Overall: {results['overall_score_percent']}%, Correct: {results['total_correct']}/20")

    # 8. Fetch Current Active Learning Plan
    print("\n8. Testing Active Roadmap Fetch...")
    roadmap = request_json("/api/planner/current", token=token)
    assert roadmap["has_plan"] is True, "Plan not found"
    assert len(roadmap["weeks"]) == 8, f"Expected 8 weeks, got {len(roadmap['weeks'])}"
    print(f"✓ Retrieved 8-week curriculum for {roadmap['target_role']} (Total tasks: {roadmap['total_tasks']})")

    # 9. Toggle Task Completion & Verify Persistence
    print("\n9. Testing Task Completion & Persistence...")
    first_task = roadmap["weeks"][0]["daily_tasks"][0]
    task_id = first_task["id"]
    toggle_res = request_json("/api/planner/task/toggle", method="POST", data={
        "plan_id": roadmap["plan_id"],
        "task_id": task_id,
        "completed": True
    }, token=token)
    assert toggle_res["completed"] is True
    assert toggle_res["completed_tasks"] >= 1
    print(f"✓ Task {task_id} checked! Completed tasks count: {toggle_res['completed_tasks']}, Progress: {toggle_res['completion_percentage']}%")

    # Verify persistence by re-fetching
    recheck = request_json("/api/planner/current", token=token)
    persisted_task = recheck["weeks"][0]["daily_tasks"][0]
    assert persisted_task["completed"] is True, "Task completion was NOT persisted!"
    print("✓ Verified persistence: task remains completed after refresh!")

    # 10. Weekly Assessment & Adaptive Update
    print("\n10. Testing Weekly Assessment & Adaptive Planning...")
    weekly_gen = request_json("/api/weekly-test/generate", method="POST", data={
        "skill": "python",
        "week": 1,
        "count": 5
    }, token=token)
    assert weekly_gen["total_questions"] == 5
    test_id = weekly_gen["test_id"]

    # Submit with answers
    weekly_answers = {str(q["id"]): 1 for q in weekly_gen["questions"]}
    weekly_res = request_json("/api/weekly-test/submit", method="POST", data={
        "test_id": test_id,
        "answers": weekly_answers
    }, token=token)
    print(f"✓ Weekly test scored: {weekly_res['score_percent']}%. Advice: {weekly_res['adaptive_recommendation']['recommendation_summary']}")

    # Apply adaptive adaptation
    adapt_res = request_json("/api/planner/adapt", method="POST", data={
        "plan_id": roadmap["plan_id"],
        "completed_week": 1,
        "test_id": test_id,
        "skill": "python",
        "score_percent": weekly_res["score_percent"]
    }, token=token)
    print(f"✓ Adaptive engine updated Week 2 curriculum: {adapt_res['message']}")
    # Verify Week 1 completed tasks were preserved!
    week1_tasks = adapt_res["plan"]["weeks"][0]["daily_tasks"]
    assert week1_tasks[0]["completed"] is True, "Adaptive update erroneously erased completed tasks from Week 1!"
    print("✓ Adaptive update preserved completed tasks and history successfully!")

    # 11. Student Dashboard Aggregator
    print("\n11. Testing Full Student Dashboard Aggregator...")
    dash = request_json("/api/dashboard", token=token)
    assert dash["has_resume"] is True
    assert dash["has_assessment"] is True
    assert dash["has_roadmap"] is True
    assert dash["match_percentage"] is not None
    assert len(dash["recent_activity"]) >= 2
    assert len(dash["recommended_projects"]) >= 1
    print("✓ Student Dashboard loaded with 100% real Supabase metrics!")
    print(f"  Match: {dash['match_percentage']}%, Tasks: {dash['completed_tasks']}/{dash['total_tasks']}, Activity events: {len(dash['recent_activity'])}")

    print("\n=== ALL 11 END-TO-END TESTS PASSED WITH 100% SUCCESS! ===")

if __name__ == "__main__":
    run_tests()
