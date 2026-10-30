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
    body = json.dumps(data).encode("utf-8") if data is not None else None
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
    print("\n6. Testing 20-MCQ Technical Assessment Generation (Automatic Domain Detection)...")
    # Omit target_role to verify automatic determination from student profile & resume skills
    exam = request_json("/api/assessment/generate", method="POST", data={}, token=token)
    assert exam["total_questions"] == 20, f"Expected 20 questions, got {exam['total_questions']}"
    assert exam["target_role"] == "Python Developer", f"Expected auto-detected Python Developer, got {exam['target_role']}"
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
    assert len(roadmap["weeks"]) == 14, f"Expected 14 weeks, got {len(roadmap['weeks'])}"
    print(f"✓ Retrieved 14-week curriculum for {roadmap['target_role']} (Total tasks: {roadmap['total_tasks']})")

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

    # 12. Forgot & Reset Password Flow
    print("\n12. Testing Forgot & Reset Password Flow in Supabase...")
    new_test_password = "UpdatedPassword@456"
    forgot_res = request_json("/api/auth/forgot-password", method="POST", data={"email": test_email})
    assert forgot_res.get("otp"), "OTP not returned in recovery request"
    recovery_otp = forgot_res["otp"]
    print(f"✓ Recovery OTP code generated for {test_email}: {recovery_otp}")

    reset_res = request_json("/api/auth/reset-password", method="POST", data={
        "email": test_email,
        "token_or_otp": recovery_otp,
        "new_password": new_test_password
    })
    assert "updated" in reset_res.get("message", "").lower()
    print("✓ Password reset verified with Supabase Auth Admin.")

    # Verify old password fails
    try:
        request_json("/api/auth/login", method="POST", data={
            "email": test_email,
            "password": "Password@123"
        })
        raise AssertionError("Old password was not invalidated after reset!")
    except urllib.error.HTTPError as err:
        assert err.code == 401
        print("✓ Old password successfully rejected (401).")

    # Verify new password succeeds
    login_new = request_json("/api/auth/login", method="POST", data={
        "email": test_email,
        "password": new_test_password
    })
    token = login_new.get("access_token")
    assert token, "Login with new password failed"
    print("✓ Successfully logged in with new password!")

    # 13. Testing Placement & Hiring Hub
    print("\n13. Testing Placement & Hiring Hub (Stats, Listings, Prepare, Bookmarks, Tracker)...")
    stats = request_json("/api/placements/stats", token=token)
    assert stats["upcoming_drives"] >= 10, f"Upcoming drives count: {stats['upcoming_drives']}"
    assert stats["open_applications"] >= 10, f"Open applications count: {stats['open_applications']}"
    assert stats["internship_opportunities"] >= 3, f"Internships count: {stats['internship_opportunities']}"
    assert stats["application_deadlines"] >= 10, f"Deadlines count: {stats['application_deadlines']}"
    print(f"✓ Placement statistics verified: {stats}")

    # Test opportunities listing
    opps = request_json("/api/placements/opportunities", token=token)
    assert opps["total"] >= 15, f"Opportunities count: {opps['total']}"
    first_opp = opps["opportunities"][0]
    opp_id = first_opp["id"]
    print(f"✓ Retrieved {opps['total']} verified opportunities. Sample: {first_opp['company_name']} - {first_opp['role_title']}")

    # Test filtering by job_type
    internships = request_json("/api/placements/opportunities?job_type=Internship", token=token)
    assert len(internships["opportunities"]) >= 3, f"Internships count: {len(internships['opportunities'])}"
    print(f"✓ Filtered {len(internships['opportunities'])} internship opportunities.")

    # Test search query
    tcs_search = request_json("/api/placements/opportunities?search=TCS", token=token)
    assert len(tcs_search["opportunities"]) >= 1, "TCS search returned 0 items"
    tcs_opp = tcs_search["opportunities"][0]
    tcs_id = tcs_opp["id"]
    print(f"✓ Search filter verified: found {tcs_opp['company_name']}")

    # Test Prepare for Company
    prep_res = request_json(f"/api/placements/prepare/{tcs_id}", method="POST", data={
        "student_skills": ["python", "sql", "git"]
    }, token=token)
    assert prep_res["match_score"] is not None
    assert len(prep_res["round_strategies"]) >= 3
    assert len(prep_res["recommended_projects"]) >= 1
    assert "tata" in prep_res["company_name"].lower() or "tcs" in prep_res.get("company_name", "").lower()
    print(f"✓ Generated personalized preparation plan for {prep_res['company_name']}: Match {prep_res['match_score']}%, Rounds: {len(prep_res['round_strategies'])}")

    # Test Bookmark / Save
    save_toggle = request_json(f"/api/placements/saved/{tcs_id}", method="POST", token=token)
    assert save_toggle["is_saved"] is True, "Save toggle failed"
    saved_list = request_json("/api/placements/saved", token=token)
    assert saved_list["count"] >= 1, "Saved opportunities count is 0"
    print("✓ Successfully bookmarked opportunity and verified in saved list.")

    # Test Application Tracker
    track_res = request_json("/api/placements/applications", method="POST", data={
        "opportunity_id": tcs_id,
        "status": "Preparing",
        "applied_date": "2026-10-30",
        "notes": "Revising TCS NQT cognitive ability and coding practice questions"
    }, token=token)
    assert track_res["status"] == "Preparing"

    apps_list = request_json("/api/placements/applications", token=token)
    assert apps_list["count"] >= 1
    assert apps_list["applications"][0]["opportunity"]["company_name"] == tcs_opp["company_name"]
    print(f"✓ Successfully tracked application for {tcs_opp['company_name']}: Stage = {track_res['status']}")

    # Update Application Stage to Applied
    update_track = request_json("/api/placements/applications", method="POST", data={
        "opportunity_id": tcs_id,
        "status": "Applied"
    }, token=token)
    assert update_track["status"] == "Applied"
    print("✓ Successfully transitioned application stage to 'Applied'.")

    # Delete application tracking
    del_track = request_json(f"/api/placements/applications/{tcs_id}", method="DELETE", token=token)
    assert del_track["deleted"] is True
    print("✓ Successfully cleaned up tracked application.")

    print("\n=== ALL 13 END-TO-END TESTS PASSED WITH 100% SUCCESS! ===")

if __name__ == "__main__":
    run_tests()
