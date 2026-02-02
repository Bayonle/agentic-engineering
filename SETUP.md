# Setup Guide - Agentic Workflow Plugin

Complete guide to setting up and publishing the plugin.

---

## Current Status

✅ Plugin structure created
✅ All 6 skills implemented (pm, architect, engineer, qa, deploy, work)
✅ Library files copied
✅ Workspace templates ready
✅ Documentation complete
✅ Verification passed

---

## Next Steps

### 1. Test Locally (5 minutes)

```bash
cd ~/Desktop/agentic-workflow-plugin

# Install plugin locally
claude plugin install .

# Test in a new project
mkdir -p ~/test-agentic-project
cd ~/test-agentic-project

# Create a test task
echo "Add hello world endpoint" > /tmp/test-task.md

# Test PM agent (will auto-create workspace)
/pm /tmp/test-task
```

**Expected output:**
- "📦 First time setup: Creating agentic workspace..."
- Workspace created with agents/, tasks/, docs/
- PM agent starts working

### 2. Initialize Git Repository (2 minutes)

```bash
cd ~/Desktop/agentic-workflow-plugin

# Initialize git
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial release: Agentic Workflow v1.0.0

- PM, Architect, Engineer, QA, DevOps agents
- Full SDLC automation
- Git commits integration
- qmd documentation search
- Auto-workspace initialization
- Plugin-based distribution

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### 3. Create GitHub Repository (5 minutes)

```bash
# On GitHub.com, create new repository:
# Name: agentic-workflow
# Description: Autonomous multi-agent SDLC workflow for Claude Code
# Public: Yes
# README: No (we have one)
# License: No (we have one)

# Add remote
git remote add origin https://github.com/bayonleamzat/agentic-workflow.git

# Push
git branch -M main
git push -u origin main
```

### 4. Test Installation from GitHub (5 minutes)

```bash
# Uninstall local version
claude plugin uninstall agentic-workflow

# Install from GitHub
claude plugin install https://github.com/bayonleamzat/agentic-workflow

# Test again
cd ~/another-test-project
/work test-001
```

### 5. Create Release (Optional)

On GitHub:
1. Go to Releases → Create new release
2. Tag: `v1.0.0`
3. Title: `Agentic Workflow v1.0.0 - Initial Release`
4. Description: Copy from CHANGELOG.md
5. Publish release

---

## Installation Instructions for Users

Once published, users install with:

```bash
# From GitHub
claude plugin install https://github.com/bayonleamzat/agentic-workflow

# Verify
claude plugin list

# Use in any project
cd ~/any-project
/work task-001
```

---

## Plugin Directory Structure

```
agentic-workflow-plugin/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── skills/
│   ├── pm/
│   │   ├── SKILL.md             # PM agent
│   │   └── assets/
│   │       └── SOUL.md          # PM personality template
│   ├── architect/
│   │   ├── SKILL.md
│   │   └── assets/SOUL.md
│   ├── engineer/
│   │   ├── SKILL.md
│   │   └── assets/SOUL.md
│   ├── qa/
│   │   └── SKILL.md
│   ├── deploy/
│   │   └── SKILL.md
│   └── work/
│       └── SKILL.md             # Orchestrator
├── lib/
│   ├── task_manager.py          # Task management
│   ├── activity.py              # Activity logging
│   ├── notifications.py         # Notifications
│   ├── daily_standup.py         # Standup reports
│   └── templates/
│       └── workspace/           # Workspace template
│           ├── agents/
│           ├── tasks/
│           └── docs/
├── README.md                    # Main documentation
├── LICENSE                      # MIT License
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # Contribution guide
├── SETUP.md                     # This file
├── .gitignore                   # Git ignore rules
└── verify-plugin.sh             # Verification script
```

---

## How It Works

### First Use in a Project

```bash
cd ~/my-project
/pm task-001
```

**Plugin does:**
1. Finds plugin directory via `__file__`
2. Checks if `workspace/` exists in current dir
3. If not, copies template from `lib/templates/workspace/`
4. Initializes agents with SOUL templates
5. Starts PM agent workflow

### Subsequent Uses

```bash
/pm task-002
```

**Plugin does:**
1. Finds existing workspace
2. Loads task manager
3. Runs PM agent logic
4. No reinitialization needed

---

## Updating the Plugin

### For Development

```bash
cd ~/Desktop/agentic-workflow-plugin

# Make changes to skills or lib
vim skills/pm/SKILL.md

# Reinstall locally
claude plugin install .

# Test changes
cd ~/test-project
/pm test-task
```

### For Users

```bash
# Update to latest version
claude plugin update agentic-workflow

# Or reinstall
claude plugin uninstall agentic-workflow
claude plugin install https://github.com/bayonleamzat/agentic-workflow
```

---

## Troubleshooting

### Plugin not found after install

```bash
# Check plugin list
claude plugin list

# Verify installation
ls ~/.claude/plugins/
```

### Workspace not creating

```bash
# Check plugin can find itself
cd ~/test-project
/pm --help

# Should see PM agent help or workspace creation
```

### Skills not working

```bash
# Check plugin.json
cat ~/.claude/plugins/agentic-workflow/.claude-plugin/plugin.json

# Verify skills directory
ls ~/.claude/plugins/agentic-workflow/skills/
```

---

## Distribution Options

### Option 1: GitHub Only (Current)
- Users install via URL
- Simple distribution
- Manual updates

```bash
claude plugin install https://github.com/bayonleamzat/agentic-workflow
```

### Option 2: Claude Plugin Marketplace (Future)
- Submit to official marketplace
- Automatic updates
- Better discovery
- Version management

### Option 3: NPM Package (Alternative)
- Publish to npm
- Users install via npm
- Familiar workflow for Node developers

---

## Maintenance

### Releasing Updates

1. Make changes
2. Update version in `plugin.json`
3. Update CHANGELOG.md
4. Commit and push
5. Create GitHub release
6. Users update with `claude plugin update`

### Handling Issues

1. Monitor GitHub issues
2. Reproduce locally
3. Fix in new branch
4. Test thoroughly
5. Merge and release

---

## Marketing

### Announcement Ideas

**Twitter/X:**
```
🚀 Launching Agentic Workflow v1.0!

Autonomous SDLC for @ClaudeAI Code:
✅ PM writes PRDs
✅ Architect designs
✅ Engineer codes
✅ QA tests
✅ DevOps deploys

All automatic. Just /work task-001

Install: github.com/bayonleamzat/agentic-workflow
```

**Blog Post:**
- "Building Software with AI Agents"
- "How I Automated My Entire SDLC"
- "From Idea to Deployment in One Command"

**Dev.to / Hacker News:**
- Share setup guide
- Demo video
- Case study

---

## Success Metrics

Track:
- GitHub stars
- Installation count
- Issues / PR activity
- User feedback
- Real-world usage examples

---

## Future Enhancements

See CHANGELOG.md "Unreleased" section for planned features:
- Slack/Discord notifications
- CI/CD integrations
- Custom agent roles
- Team collaboration
- Analytics dashboard
- Multi-language support

---

**Ready to ship! 🚀**

Follow the steps above to publish your plugin and start helping developers automate their SDLC.
