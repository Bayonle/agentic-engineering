# Agentic Workflow - Autonomous SDLC System

**Autonomous multi-agent workflow system for Claude Code**

PM writes PRDs → Architect designs → Engineer implements → QA tests → DevOps deploys

Full software development lifecycle automation with git commits, documentation search, and complete task management.

---

## Features

✅ **5 Autonomous Agents** - PM, Architect, Engineer, QA, DevOps
✅ **Auto-Handoff** - Agents spawn next agent automatically
✅ **Git Commits** - Each phase commits work automatically
✅ **Documentation Search** - Integrated qmd CLI for research
✅ **Task Management** - File-based task tracking
✅ **Zero Setup** - Auto-initializes workspace on first use
✅ **Works Anywhere** - No per-project configuration needed

---

## Installation

### Install Plugin

```bash
# Clone from GitHub
git clone https://github.com/Bayonle/agentic-engineering.git
cd agentic-engineering

# Install locally
claude plugin install .
```

**Note:** Claude Code currently requires local installation. The plugin will be submitted to the official marketplace for direct URL installation in the future.

### Verify Installation

```bash
# Check plugin is installed
claude plugin list

# Test in any directory
cd ~/my-project
/pm --help
```

---

## Quick Start

### 1. Create a Task

```bash
cd ~/my-project

# First use will auto-create workspace/
echo "Add user authentication" > workspace/tasks/inbox/task-001.md
```

### 2. Run Full Workflow

```bash
/work task-001
```

That's it! The workflow will:
- PM researches and writes PRD (you approve)
- Architect designs solution (you approve)
- Engineer implements code
- QA tests feature
- DevOps deploys (you approve)

### 3. Or Run Individual Agents

```bash
/pm task-001        # PM only
/architect task-001 # Architect only
/engineer task-001  # Engineer only
/qa task-001        # QA only
/deploy task-001    # Deploy only
```

---

## Available Commands

| Command | Agent | Purpose |
|---------|-------|---------|
| `/work task-id` | All | Full workflow PM→Architect→Engineer→QA→DevOps |
| `/pm task-id` | PM | Research requirements, write PRD |
| `/architect task-id` | Architect | Design solution, create technical plan |
| `/engineer task-id` | Engineer | Implement code, create PR |
| `/qa task-id` | QA | Test feature, verify quality |
| `/deploy task-id` | DevOps | Deploy to production |

---

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│  /work task-001                                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────┐
│  PM Agent                                               │
│  - Researches requirements with qmd                     │
│  - Writes comprehensive PRD                             │
│  - Requests human approval                              │
│  - Git commits PRD                                      │
└─────────────────────────────────────────────────────────┘
                          │ (auto-handoff)
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Architect Agent                                        │
│  - Reads PRD                                            │
│  - Researches patterns with qmd                         │
│  - Designs technical solution                           │
│  - Creates implementation plan                          │
│  - Requests human approval                              │
│  - Git commits plan                                     │
└─────────────────────────────────────────────────────────┘
                          │ (auto-handoff)
                          ↓
┌─────────────────────────────────────────────────────────┐
│  Engineer Agent                                         │
│  - Reads plan                                           │
│  - Researches APIs with qmd                             │
│  - Implements feature                                   │
│  - Writes tests                                         │
│  - Creates PR                                           │
│  - Git commits code                                     │
└─────────────────────────────────────────────────────────┘
                          │ (auto-handoff)
                          ↓
┌─────────────────────────────────────────────────────────┐
│  QA Agent                                               │
│  - Runs tests                                           │
│  - Verifies quality                                     │
│  - Requests deployment approval                         │
│  - Git commits test reports                             │
└─────────────────────────────────────────────────────────┘
                          │ (auto-handoff)
                          ↓
┌─────────────────────────────────────────────────────────┐
│  DevOps Agent                                           │
│  - Deploys to production                                │
│  - Verifies health checks                               │
│  - Marks task complete                                  │
│  - Git commits deployment                               │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
                    ✅ Feature Live!
```

---

## Workspace Structure

On first use, the plugin auto-creates this structure:

```
your-project/
└── workspace/
    ├── agents/              # Agent memory
    │   ├── pm/
    │   │   ├── SOUL.md      # PM personality & knowledge
    │   │   └── WORKING.md   # Current state
    │   ├── architect/
    │   ├── engineer/
    │   ├── qa/
    │   └── devops/
    ├── tasks/               # Task management
    │   ├── inbox/           # New tasks
    │   ├── in-planning/     # Being planned
    │   ├── ready-to-build/  # Ready to code
    │   ├── ready-for-testing/ # Ready to test
    │   ├── ready-to-deploy/ # Ready to ship
    │   └── deployed/        # Complete
    ├── docs/
    │   ├── specs/           # PRDs
    │   ├── plans/           # Technical plans
    │   ├── qa-reports/      # Test reports
    │   └── deployment-reports/ # Deployment logs
    └── activity.log         # Agent activity
```

---

## Git Commits

Each agent automatically commits their work:

```bash
# After workflow completes:
$ git log --oneline --author="Claude"

abc1234 [DevOps] Deploy user authentication to production
def5678 [QA] Test and approve user authentication
ghi9012 [Engineer] Implement user authentication
jkl3456 [Architect] Create technical plan for user authentication
mno7890 [PM] Create PRD for user authentication
```

**Commit format:**
```
[AgentRole] Action for task

Details here

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

---

## Documentation Search

Agents use [qmd CLI](https://github.com/tobi/qmd) for fast documentation lookup:

**PM researches:**
```bash
qmd "JWT authentication best practices"
qmd "ASP.NET Core security"
```

**Architect researches:**
```bash
qmd "ASP.NET Core middleware pipeline"
qmd "PostgreSQL indexing strategies"
```

**Engineer researches:**
```bash
qmd "Entity Framework async queries"
qmd "C# record types"
```

**Install qmd (optional but recommended):**
```bash
# See: https://github.com/tobi/qmd
```

---

## Configuration

Optional `.agent-config.json` in your project:

```json
{
  "git_commits": true,
  "qmd_enabled": true,
  "auto_push": true,
  "project_name": "my-project"
}
```

---

## Examples

### Example 1: Full Workflow

```bash
cd ~/my-saas-app

# Create task
cat > workspace/tasks/inbox/task-001.md << 'EOF'
Add user profile endpoint

GET /api/users/{id}
Should return user profile with email, name, created date
EOF

# Run full workflow
/work task-001

# Agents will:
# 1. PM writes PRD (you approve)
# 2. Architect designs API (you approve)
# 3. Engineer implements endpoint
# 4. QA tests it
# 5. DevOps deploys (you approve)
```

### Example 2: Skip to Engineer

```bash
# You already have PRD and plan, just need code
/engineer task-002
```

### Example 3: Deploy Only

```bash
# Code and tests done, just deploy
/deploy task-003
```

---

## Agent Personalities

Each agent has a distinct personality and expertise:

**PM Agent**
- Strategic coordinator
- User-focused
- Decisive and pragmatic
- Writes clear, actionable PRDs

**Architect Agent**
- Thoughtful technical leader
- Pragmatic over clever
- Explains trade-offs
- Designs for maintainability

**Engineer Agent**
- Practical craftsperson
- Quality-conscious
- Pattern-aware
- Ships working code

**QA Agent**
- Quality gatekeeper
- Thorough tester
- Clear communicator
- Ensures reliability

**DevOps Agent**
- Deployment specialist
- Cautious and methodical
- Verifies health
- Ensures uptime

---

## Approval Gates

You'll be asked to approve at these points:

**After PM:**
- Review PRD: `cat workspace/docs/specs/task-001-prd.md`
- Approve: Tell Claude "I approve the PRD for task-001"

**After Architect:**
- Review plan: `cat workspace/docs/plans/task-001-plan.md`
- Approve: Tell Claude "I approve the plan for task-001"

**After QA:**
- Review tests: Check test results in comments
- Approve: Tell Claude "I approve deployment for task-001"

---

## Monitoring

Watch agent activity in real-time:

```bash
# Tail activity log
tail -f workspace/activity.log

# Check task status
cat workspace/tasks/in-progress/*.md

# View git commits
git log --oneline --author="Claude"
```

---

## Advanced Usage

### Custom SOUL Templates

Customize agent personalities:

```bash
# Edit PM personality
vim workspace/agents/pm/SOUL.md

# Changes apply to this project only
```

### Manual Task Assignment

```bash
# Skip phases manually
python3 << 'EOF'
import sys
sys.path.append('.claude/plugins/agentic-workflow/lib')
from task_manager import get_task_manager

tm = get_task_manager('workspace')
tm.move_task('task-001', 'ready-to-build')
tm.assign_task('task-001', 'engineer')
EOF

/engineer task-001
```

---

## Troubleshooting

### Workspace not created

```bash
# Manually trigger workspace creation
cd ~/my-project
/pm task-001
# Will auto-create workspace/
```

### Git commits not working

```bash
# Initialize git in your project
cd ~/my-project
git init
git remote add origin <your-repo-url>
```

### qmd not found

```bash
# Install qmd (optional)
# See: https://github.com/tobi/qmd
# Agents continue without qmd
```

---

## Requirements

- Claude Code CLI
- Python 3.7+
- Git (optional, for commits)
- qmd CLI (optional, for docs)

---

## License

MIT License - See LICENSE file

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test with real workflows
5. Submit pull request

---

## Support

- GitHub Issues: https://github.com/bayonleamzat/agentic-workflow/issues
- Documentation: See docs/ folder
- Examples: See examples/ folder

---

## Roadmap

- [ ] Support for more languages/frameworks
- [ ] Integration with CI/CD platforms
- [ ] Slack/Discord notifications
- [ ] Custom agent roles
- [ ] Team collaboration features
- [ ] Metrics and analytics

---

**Made with ❤️ for autonomous development**

Start shipping faster with AI agents that handle the full SDLC!
