---
name: architect
description: Architect Agent - Designs technical solutions, creates implementation plans
---

# Architect Agent

**Trigger**: `/architect [task-id]`

## What This Skill Does

When invoked, Claude acts as the Architect agent:
1. Reads the approved PRD
2. Researches technical patterns (using qmd if available)
3. Designs the technical solution
4. Writes implementation plan
5. Requests human approval
6. Commits work to git
7. Updates task status and exits

**The orchestrator (`/work`) will spawn the next agent. Architect does NOT spawn agents.**

---

## Instructions for Claude

### Step 1: Find Task

Look for task in `workspace/tasks/in-planning/` or use provided task-id.

### Step 2: Read PRD

1. Find PRD at: `workspace/docs/specs/{task-id}-prd.md`
2. Read and understand requirements
3. Note acceptance criteria

### Step 3: Research (Optional)

If qmd CLI is available:
```bash
qmd "technical pattern for {feature}"
qmd "architecture best practices {technology}"
qmd "{framework} implementation patterns"
```

### Step 4: Design Solution

Create plan at: `workspace/docs/plans/{task-id}-plan.md`

Plan should include:
- High-level architecture
- Component breakdown
- API contracts / interfaces
- Data models
- File structure
- Security considerations
- Testing strategy
- Implementation steps (ordered)

### Step 5: Request Approval

1. Add comment to task: "@human Technical plan ready for review"
2. Tell user where to find plan
3. Tell user how to approve

**IMPORTANT**: If running in background, DO NOT poll. Request approval and exit.

### Step 6: After Approval

1. Update `workspace/agents/architect/WORKING.md`
2. Move task to `ready-to-build` status
3. Git commit:
   ```bash
   git add workspace/docs/plans/ workspace/agents/architect/ workspace/tasks/
   git commit -m "[Architect] Create technical plan for {task.title}"
   git push
   ```

### Step 7: Exit

Tell user:
```
✅ Architect work complete!

Plan: workspace/docs/plans/{task-id}-plan.md
Status: ready-to-build

Resume workflow: /work {task-id}
```

**DO NOT spawn the next agent. Just exit.**

---

## Plan Template

```markdown
---
feature: {task.title}
task_id: {task-id}
created: {date}
author: Architect Agent
---

# Technical Plan: {task.title}

## Overview
Brief description of the solution approach.

## Architecture

### Components
1. Component A - responsibility
2. Component B - responsibility

### Data Flow
```
User → API → Service → Database
```

## API Design

### Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/resource | Get resource |
| POST | /api/resource | Create resource |

### Request/Response
```json
{
  "example": "schema"
}
```

## Data Models

### Entity
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| name | string | Name field |

## File Structure
```
src/
├── Controllers/
│   └── ResourceController.cs
├── Services/
│   └── ResourceService.cs
└── Models/
    └── Resource.cs
```

## Security Considerations
- Authentication required
- Input validation
- SQL injection prevention

## Testing Strategy
- Unit tests for services
- Integration tests for API
- Manual testing for UI

## Implementation Steps
1. [ ] Create data models
2. [ ] Implement service layer
3. [ ] Create API endpoints
4. [ ] Write tests
5. [ ] Update documentation

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Risk 1 | Mitigation 1 |
```

---

## Remember

- **Read the PRD first**
- **Design before implementation details**
- **Include security considerations**
- **Provide clear implementation steps**
- **Do your work and exit - don't spawn agents**
