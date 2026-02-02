# Contributing to Agentic Workflow

Thank you for your interest in contributing! Here's how you can help.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/agentic-workflow
   cd agentic-workflow
   ```

3. Install locally:
   ```bash
   claude plugin install .
   ```

4. Test in a project:
   ```bash
   cd ~/test-project
   /work task-001
   ```

## Development Workflow

### Testing Changes

1. Make your changes to skills or lib
2. Test locally:
   ```bash
   cd ~/Desktop/agentic-workflow-plugin
   claude plugin install .  # Reinstall
   cd ~/test-project
   /pm test-task  # Test your changes
   ```

### Adding a New Agent

1. Create skill directory:
   ```bash
   mkdir -p skills/new-agent/assets
   ```

2. Create `skills/new-agent/SKILL.md` with:
   - YAML frontmatter (name, description)
   - Plugin initialization code
   - Agent logic
   - Auto-handoff to next agent

3. Create `skills/new-agent/assets/SOUL.md` template

4. Update README with new agent

### Modifying Existing Agents

1. Edit `skills/{agent}/SKILL.md`
2. Keep plugin initialization code intact
3. Test changes locally
4. Update documentation if behavior changes

## Code Style

### Python Code in Skills
- Use pathlib for paths
- Include plugin initialization
- Handle missing workspace gracefully
- Log activities with `log_activity()`
- Use task manager for state

### Markdown Documentation
- Clear headings
- Code examples for complex features
- Link to related docs
- Keep README concise

## Pull Request Process

1. Create feature branch:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make changes and test thoroughly

3. Commit with clear messages:
   ```bash
   git commit -m "Add: New feature description"
   ```

4. Push and create PR:
   ```bash
   git push origin feature/my-feature
   ```

5. In PR description:
   - Describe what changed
   - Why it was needed
   - How to test it
   - Any breaking changes

## Testing Checklist

Before submitting PR, verify:

- [ ] Plugin installs without errors
- [ ] Workspace auto-creates on first use
- [ ] All agents can be invoked
- [ ] Git commits work (if git available)
- [ ] qmd integration works (if qmd available)
- [ ] Task manager operations work
- [ ] Activity logging works
- [ ] No hardcoded paths
- [ ] README updated if needed
- [ ] CHANGELOG updated

## Bug Reports

Open an issue with:

1. Clear title
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment (OS, Claude Code version)
6. Error messages or logs

## Feature Requests

Open an issue with:

1. Clear description
2. Use case / why it's needed
3. Proposed solution (optional)
4. Alternatives considered (optional)

## Questions

For questions:
- Check README first
- Search existing issues
- Open new issue with "Question:" prefix

## Code of Conduct

- Be respectful
- Be helpful
- Focus on improving the project
- Welcome newcomers

## License

By contributing, you agree your contributions will be licensed under the MIT License.
