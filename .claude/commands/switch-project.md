# Switch Active Project

Switch the active project context. Usage: `/switch-project [ies|framework|therapy]`

**Available projects:**
| Project | Focus | SiYuan Notebook |
|---------|-------|-----------------|
| ies | Framework development (backend, plugin) | Intelligent Exploration System |
| framework | Implementation/testing for chris | Framework Project |
| therapy | Content exploration (therapeutic worldview) | Therapy Framework |

---

## Process

1. **Check for unsaved work** in current project
   - If significant work was done, consider spawning scribe agent first

2. **Update `.active-project`** with the new project name

3. **Load new context:**
   - Read `{project}/CLAUDE.md`
   - Read `{project}/progress.md`
   - Activate Serena project if available

4. **Report context summary:**
   - Current state
   - Next steps from progress.md
   - Hanging questions (therapy only)

If no argument provided, show current active project and list options.

## Agent Alternative

For full context handoff, spawn the project-switcher agent:
```
Task(subagent_type: "project-switcher", prompt: "Switch to {project}")
```
