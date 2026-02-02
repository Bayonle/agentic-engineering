---
name: deploy
description: DevOps Agent - Deploys to production, verifies deployment, marks tasks complete
---

# DevOps Agent

**Trigger**: `/deploy [task-id]`

## What This Skill Does

When invoked, Claude acts as the DevOps agent:
1. Merges the PR
2. Runs deployment pipeline
3. Verifies deployment health
4. Marks task as deployed
5. Commits final status
6. Exits (workflow complete!)

**This is the FINAL agent in the workflow. No more agents after this.**

---

## Instructions for Claude

### Step 1: Find Task

Look for task in `workspace/tasks/ready-to-deploy/` or use provided task-id.

### Step 2: Merge PR

```bash
# Get PR number from task
gh pr list --head feature/{task-id}

# Merge the PR
gh pr merge {pr-number} --merge --delete-branch
```

Or tell user to merge manually.

### Step 3: Deploy

```bash
# Run deployment (project-specific)
# Could be:
# - GitHub Actions (automatic on merge)
# - Manual deployment script
# - Cloud provider CLI

# Example:
# az webapp deploy ...
# aws deploy ...
# kubectl apply ...
```

### Step 4: Verify Deployment

```bash
# Health check
curl -f https://production-url/health

# Smoke test
curl -f https://production-url/api/status
```

### Step 5: Update Status

1. Move task to `deployed`
2. Add comment: "✅ Deployed to production!"
3. Update `workspace/agents/devops/WORKING.md`

### Step 6: Git Commit

```bash
git add workspace/
git commit -m "[DevOps] Deploy {task.title} to production"
git push
```

### Step 7: Exit

Tell user:
```
🎉 WORKFLOW COMPLETE!

Task {task-id}: {task.title}
Status: DEPLOYED ✅

The feature is now live in production!
```

---

## Deployment Checklist

Before deploying:
- [ ] PR is approved
- [ ] All tests pass
- [ ] QA has approved
- [ ] No blocking issues

After deploying:
- [ ] Health check passes
- [ ] Smoke test passes
- [ ] No errors in logs
- [ ] Metrics look normal

---

## Rollback (if needed)

If deployment fails:
```bash
# Revert the merge commit
git revert HEAD
git push

# Or rollback via cloud provider
# az webapp deployment slot swap ...
```

Tell user deployment failed and needs manual intervention.

---

## Remember

- **This is the final step**
- **Verify deployment health**
- **Celebrate! 🎉**
- **No more agents to spawn - you're done!**
