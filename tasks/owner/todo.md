---
name: Owner Task Plan
description: Active plans and task records directly owned by the repository owner.
---

# Owner Tasks

## Register Drake as Backend Developer

- Owner: ittikorn (accountable); executed by Drake
- Created at: 2026-11-18T00:00:00+07:00
- Status: In progress

- [x] Add `drake` to `.agents/team/agents.yaml` (role `backend-developer.md`, reports to ittikorn, no capabilities) and to the registry test
- [x] `python3 -m unittest discover -s .agents/skills/agent-workspace/tests` passes (27 tests)
- [ ] Owner approves and merges the registry PR; authority applies only after merge into `origin/main`
- [ ] Then prepare `.workspace/drake` and start the handoff work (`docs/handoff/2026-11-17-dev-handoff.md`)
