# DECISIONS.md — bpmn-onto

A running log of architecture and technical decisions. Append-only. New decisions go at the bottom.

Each entry follows this format:

---

### [Date] — [Short title]

**Context:** What was being decided and why.

**Decision:** What was chosen.

**Alternatives considered:** What else was on the table and why it lost.

**Consequences:** What this commits us to, and any trade-offs we accept.

---

## Decisions

### 2026-05-09 — Python 3.11+ as the implementation language

**Context:** Need to pick a language. The project does XML parsing, calls LLM APIs, emits RDF, and ships a CLI. Tiago is fluent in Python and the LLM SDK ecosystem is Python-first.

**Decision:** Python 3.11+.

**Alternatives considered:**
- Python 3.10: rejected because 3.11 gives noticeably better error messages (`ExceptionGroup`, fine-grained tracebacks) and we want match statements without contortion.
- TypeScript/Node: rejected because the RDF and ontology ecosystem is weaker on Node, and Tiago's productivity in Python is higher.
- Rust: rejected as overkill for an LLM-call-heavy tool whose hot path is HTTP latency, not CPU.

**Consequences:** All examples and CI assume `python>=3.11`. Drops support for users still on 3.10. Acceptable — this is a developer tool, not a library targeting embedded environments.

---

### 2026-05-09 — `uv` as the package manager and dev toolchain

**Context:** Need a package manager for the project. The standard is `pip` but `uv` is faster, handles venvs cleanly, and is the modern standard for Python projects.

**Decision:** `uv`.

**Alternatives considered:**
- `pip` + `venv`: rejected because `uv` is a strict superset in daily use and significantly faster. No downside for a greenfield project.
- `poetry`: rejected because `pyproject.toml` + `uv` is cleaner and poetry's lockfile format is non-standard.
- `pipenv`: rejected, effectively superseded.

**Consequences:** Contributors need `uv` installed. Setup is one `curl` command. `uv venv` + `uv pip install -e ".[dev]"` is the canonical dev setup. Document this in README.

---

### 2026-05-09 — `lxml` for BPMN XML parsing, no dedicated BPMN library

**Context:** BPMN 2.0 is a heavily namespaced XML format. We need to parse it into Python objects we can reason about. There are dedicated BPMN libraries on PyPI but they're either abandoned, bloated with execution-engine code we don't need, or both.

**Decision:** Use `lxml` directly with a thin custom parser layer in `bpmn_onto.parser`. The custom layer extracts only the structural elements we care about (processes, tasks, events, gateways, flows, lanes, pools).

**Alternatives considered:**
- `xml.etree.ElementTree` (stdlib): rejected because BPMN's namespace handling is painful in `ElementTree` and `lxml`'s XPath support is materially better.
- `bpmn-python` and similar: rejected because they bundle execution semantics, are sparsely maintained, and would constrain our data model to theirs.
- Writing our own XML parser: obviously rejected.

**Consequences:** We own the BPMN-to-Python mapping. Pro: full control over the data model, no dependency on a stale library, easy to extend. Con: we have to handle BPMN edge cases ourselves (subprocesses, message flows, boundary events). Acceptable given v1 scope is "structural extraction for ontology purposes," not full BPMN execution semantics.

---

### 2026-05-09 — Turtle/RDF as primary output, Cypher as optional secondary

**Context:** The tool's job is to emit a validated ontology. Two reasonable target representations: RDF (Turtle serialization) and labeled property graphs (Cypher for Neo4j).

**Decision:** Turtle/RDF is the primary, fully-supported output. Cypher is a stretch goal — implemented if time allows in phase 5, deferred otherwise.

**Alternatives considered:**
- Cypher-first: rejected because RDF is the canonical ontology format and SHACL/OWL tooling assumes it. ISA-95 reference work is RDF-shaped.
- JSON-LD: rejected as primary because Turtle is more readable and is the lingua franca of the semantic-web tooling we'd validate against. JSON-LD remains an easy addition later via `rdflib` since it's a serialization concern.

**Consequences:** v1 ships with `--target isa95 --output factory.ttl` working end-to-end. Cypher emission is gated behind explicit flag and may be marked experimental. README sells the project as RDF-first.

---

### 2026-05-09 — `rdflib` for RDF graph construction and serialization

**Context:** We need to build an RDF graph in memory and serialize it to Turtle. Optionally validate it against SHACL shapes.

**Decision:** `rdflib` (>=7.0).

**Alternatives considered:**
- Hand-written Turtle string emission: rejected because escaping, prefix handling, and namespace management are non-trivial and a solved problem.
- `pyoxigraph`: rejected as overkill — it's a SPARQL/triplestore engine, we just need graph construction.

**Consequences:** Adds a real dependency, but `rdflib` is the standard. Gives us serialization to Turtle, JSON-LD, N-Triples, and N3 essentially for free, plus a SPARQL query interface if we ever want it.

---

### 2026-05-09 — SHACL validation deferred to phase 5; `pyshacl` is the likely choice

**Context:** "Validated ontology" is in the project description. The verifier-agent layer (phase 4) catches LLM extraction errors. Schema-level validation against ISA-95 SHACL shapes (phase 5) catches structural errors in the emitted graph.

**Decision:** Don't commit to a SHACL library yet. Defer the choice to phase 5 with `pyshacl` as the leading candidate. The verifier-agent layer in phase 4 is the priority — that's the project's architectural story.

**Alternatives considered:**
- Commit to `pyshacl` now: rejected because we don't yet know whether ISA-95 has usable public SHACL shapes or whether we'll have to write our own. Don't add the dependency until we need it.
- Use OWL reasoning instead of SHACL: rejected as too heavy and slow. SHACL is the modern approach.

**Consequences:** v1 may ship without schema-level SHACL validation if phase 5 runs out of time. The verifier-agent layer is the non-negotiable validation layer. SHACL becomes a v1.1 item if needed.

---

### 2026-05-09 — Thin LLM provider abstraction with multiple implementations

**Context:** This tool calls an LLM. We don't want to hard-code one provider, and the verifier pattern is more interesting if extractor and verifier can run on different models or providers.

**Decision:** Define a minimal `Provider` protocol in `bpmn_onto.llm.base` with one method, roughly `complete(messages, schema=None) -> dict | str`. Ship implementations for Anthropic and OpenAI as optional extras (`pip install bpmn-onto[anthropic]` etc). Allow the user to mix providers per role (extractor model X, verifier model Y) via config.

**Alternatives considered:**
- LangChain / LlamaIndex: rejected. Too much surface area for what we need, and they obscure the prompt engineering that is the point of the project.
- Litellm: considered seriously. Rejected for v1 because writing our own thin abstraction is a few dozen lines, surfaces structured-output handling explicitly, and is more honest portfolio work. May revisit in v2.
- Hard-code Anthropic only: rejected because cross-provider verifier configurations are part of the project's story.

**Consequences:** We own the provider interface. We have to implement structured-output handling per provider (Anthropic tool use vs. OpenAI structured outputs vs. Ollama JSON mode). Trade-off accepted — this is the engineering, and it's exactly the kind of thing the README will discuss.
