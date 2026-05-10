# state.md — bpmn-onto

Current project state. Update at the end of each work session.

---

## Status

**Phase:** Phase 2 — BPMN Parsing

**What's done:**
- Spike & decide complete: repo skeleton, uv toolchain, library decisions logged, 6 example BPMN files, ISA-95 reference doc, design doc

**What's next:**
- Build the BPMN parser: lxml → BpmnProcess Pydantic model
- Start with manufacturing-work-order.bpmn
- Then stress test against tier1 structural examples

**Blockers / open questions:**
- None

---

## Session log

### 2026-05-10

**Time spent:** ~2 hours
**What I did:**
- Set up repo skeleton, uv toolchain, pushed to GitHub
- Locked library decisions in DECISIONS.md
- Added 6 example BPMN files across 3 tiers
- Wrote design doc and ISA-95 reference

**What I learned / surprised me:**
- uv not on PATH after install — needed to add ~/.local/bin manually
- pip not available inside venv without uv — expected but worth noting

**What's next:**
- Phase 2: BpmnProcess Pydantic model and lxml parser

**Notes for the README / blog post:**
- PATH issue with uv install is a common gotcha worth mentioning