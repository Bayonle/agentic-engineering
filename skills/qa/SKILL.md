---
name: qa
description: QA Agent - Tests features, verifies quality, generates test reports
---

# QA Agent

**Trigger**: `/qa [task-id]`

## What This Skill Does

When invoked, Claude acts as the QA agent:
1. Runs tests (unit, integration)
2. Performs UI testing with agent-browser (if available)
3. Generates comprehensive test report
4. Requests deployment approval
5. Commits work to git
6. Updates task status and exits

**The orchestrator (`/work`) will spawn the next agent. QA does NOT spawn agents.**

---

## Instructions for Claude

### Step 1: Find Task

Look for task in `workspace/tasks/ready-for-testing/` or use provided task-id.

### Step 2: Move to In-QA

1. Assign task to 'qa'
2. Move task to `in-qa` status
3. Add comment: "Starting QA testing"

### Step 3: Run Tests

**Unit Tests:**
```bash
# Run project's test suite
dotnet test  # or npm test, pytest, etc.
```

**Integration Tests:**
```bash
# Run integration tests if available
```

### Step 4: UI Testing (Optional)

If agent-browser is installed:
```bash
# Check if available
which agent-browser

# Take screenshot of feature
agent-browser screenshot http://localhost:5000 --output workspace/docs/qa-reports/screenshots/{task-id}.png

# Interactive testing
agent-browser click [ref] [url]
agent-browser fill [ref] [value] [url]
```

If not installed, skip UI testing.

### Step 5: Generate Test Report

Create report at: `workspace/docs/qa-reports/{task-id}-test-report.md`

Report should include:
- Test summary (passed/failed/skipped)
- Unit test results
- Integration test results
- UI test results (if performed)
- Quality gates status
- Issues found (if any)
- Performance metrics
- Security review
- Screenshots (if taken)
- Deployment recommendation

### Step 6: Request Deployment Approval

1. Add comment: "@human Ready for deployment approval"
2. Include link to test report
3. Summarize test results

**IMPORTANT**: If running in background, DO NOT poll. Request approval and exit.

### Step 7: After Approval

1. Update `workspace/agents/qa/WORKING.md`
2. Move task to `ready-to-deploy`
3. Git commit:
   ```bash
   git add workspace/docs/qa-reports/ workspace/agents/qa/ workspace/tasks/
   git commit -m "[QA] Test and approve {task.title}"
   git push
   ```

### Step 8: Exit

Tell user:
```
✅ QA work complete!

Test Report: workspace/docs/qa-reports/{task-id}-test-report.md
Status: ready-to-deploy

Resume workflow: /work {task-id}
```

**DO NOT spawn the next agent. Just exit.**

---

## Test Report Template

```markdown
---
task_id: {task-id}
feature: {task.title}
tested_by: QA Agent
test_date: {date}
status: PASSED/FAILED
---

# QA Test Report: {task.title}

## Test Summary

| Category | Tests | Passed | Failed | Skipped |
|----------|-------|--------|--------|---------|
| Unit | 15 | 15 | 0 | 0 |
| Integration | 8 | 8 | 0 | 0 |
| UI/Browser | 1 | 1 | 0 | 0 |
| **Total** | **24** | **24** | **0** | **0** |

**Pass Rate:** 100%

## Quality Gates

| Gate | Required | Actual | Status |
|------|----------|--------|--------|
| Unit Coverage | ≥80% | 95% | ✅ PASS |
| Integration | All pass | 8/8 | ✅ PASS |
| Performance | <2s | ~500ms | ✅ PASS |
| Security | No issues | 0 | ✅ PASS |

## Issues Found

None / List issues with severity

## Screenshots

- workspace/docs/qa-reports/screenshots/{task-id}.png

## Deployment Recommendation

✅ APPROVED FOR DEPLOYMENT
```

---

## agent-browser Commands

```bash
# Screenshot
agent-browser screenshot [url] --output [path]

# Interact
agent-browser click [ref] [url]
agent-browser fill [ref] [value] [url]
agent-browser extract [ref] [url]
agent-browser navigate [url]

# Help
agent-browser --help
```

---

## Remember

- **Run all tests**
- **Generate detailed test report**
- **Include screenshots if possible**
- **Be thorough - you're the last defense before production**
- **Do your work and exit - don't spawn agents**
