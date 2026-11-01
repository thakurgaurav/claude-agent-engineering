# Claude Agent Engineering

An engineering showcase for building AI workflows and agentic systems with Claude. The repository progresses from application-controlled workflows toward agents, tools, context, memory, multi-agent systems, runtimes, reliability, security, and evaluation.

## Learning & Demonstration Scope

This repository is a **hands-on AI engineering learning project** designed to demonstrate workflow and agentic patterns through clear, isolated implementations.

The examples intentionally make architectural boundaries visible—such as prompt chaining, routing, parallel execution, evaluation loops, and orchestration. In some labs, this means using multiple model calls or explicitly separating responsibilities that could potentially be handled with fewer calls in a production implementation.

These examples should therefore be treated as **pattern demonstrations, not prescriptive production architectures**.

For a real system, the appropriate design depends on the problem, model capability, reliability requirements, latency, cost, observability, and the level of deterministic control required.

**The goal is not to maximize model calls, workflow stages, or agentic behavior. Use the simplest architecture that reliably solves the problem, and introduce additional structure only when it provides a clear engineering benefit.**

## Architecture & Anthropic SDK Distinction

This repository intentionally separates **agentic architecture patterns** from **Anthropic SDK abstractions**.

The workflow-engineering labs implement patterns such as Prompt Chaining, Routing, Parallelization, Evaluator–Optimizer, and Orchestrator–Worker explicitly in application code. Where model calls are required, they use Anthropic’s standard API client; the orchestration itself remains explicit. This makes model responsibilities, validation, concurrency, failure handling, and stopping behavior visible rather than hiding those mechanics behind a higher-level framework.

The repository structure—including `shared/` and `projects/`—is a production-oriented organization used by this learning project. It should not be interpreted as a directory structure prescribed by Anthropic.

The **Claude Agent SDK** is introduced separately during the Agents phase, where the focus shifts from predefined application-controlled workflows toward model-directed agent loops, tool use, context and state management, permissions, hooks, sub-agents, and other agent-runtime capabilities.

Throughout the repository, we distinguish between:

- **Architecture patterns** — general techniques for designing workflows and agents.
- **Application architecture** — how this repository organizes and implements those techniques.
- **Anthropic APIs and SDKs** — capabilities provided by Anthropic that may implement or abstract parts of the runtime.
- **Claude Code conventions** — development-time mechanisms such as `CLAUDE.md` and `.claude/`, which are separate from the runtime architecture of the applications being built.

The goal is to understand the underlying engineering mechanics first, and then understand what higher-level SDKs and frameworks provide or abstract.

## Engineering approach

> Understand and demonstrate the underlying engineering mechanism before introducing higher-level abstractions.

Each project separates implementation, runnable demonstrations, prompts, tools, provider integrations, and tests.

## Projects

### 01 — Workflow Engineering

**Status:** Complete

Implemented:

- [x] Prompt Chaining
- [x] Routing
- [x] Parallelization + Aggregation
- [x] Evaluator–Optimizer
- [x] Orchestrator–Worker

The project progresses from deterministic application-controlled execution to model-directed decisions within explicit boundaries:

```text
Prompt Chaining → Routing → Parallelization + Aggregation
                 → Evaluator–Optimizer → Orchestrator–Worker
```

It demonstrates semantic routing and validation, Claude Tool Use, concurrent tool execution, fan-out/fan-in orchestration, real provider integrations, semantic aggregation and evaluation, feedback-driven optimization, dynamic task decomposition, structured-output validation and bounded repair, failure isolation, Pydantic contracts, MongoDB hard filtering, and separation of Claude-facing capabilities from provider infrastructure.

The completed workflow progression is:

- Prompt Chaining — application controls a predefined sequence.
- Routing — Claude selects among application-defined routes.
- Parallelization — the application defines the independent parallel work.
- Evaluator–Optimizer — the application owns an iterative generation, evaluation, and improvement loop.
- Orchestrator–Worker — Claude dynamically determines the substantial work needed for a specific request; the application executes the generated work.

Lab 01 — Prompt Chaining demonstrates a predefined sequence of focused Claude calls:

```text
Decision request → Understand → Extract constraints
                 → Define criteria → Create research plan
```

The application owns stage order and state propagation. Each stage uses a focused prompt, bounded output, response/truncation validation, and packaged prompt templates. Claude reasons within the sequence; it does not create new stages or execution paths.

Lab 02 — Routing adds model-directed branching within application-defined capabilities:

```text
Request → Understand → Extract constraints → Define criteria
       → Claude router → validated route → predefined handler
```

Claude returns a constrained route such as `PURCHASE`, `CAREER`, `TRAVEL`, or `GENERAL`. Application validation and Python dispatch select the corresponding handler, so the model chooses among allowed paths but cannot create arbitrary routes.

Lab 03 — Parallelization + Aggregation answers travel-safety questions using independent signals:

```text
Request → Claude selects tools → weather / air quality / fire activity
        → concurrent tool results → Claude semantic aggregation → assessment
```

The application executes synchronous provider calls concurrently with `asyncio.to_thread()` and `asyncio.gather()`, matches results to tool-use IDs, and uses available evidence when an individual provider fails. Claude-facing tools isolate provider URLs, authentication, response formats, caching, geocoding, and network details. The application defines which independent work exists before execution.

Lab 04 — Evaluator–Optimizer recommends a rental from a MongoDB-backed dataset:

```text
Request → requirement interpreter → hard-filtered candidates
        → generator → evaluator ── PASS → final recommendation
                              └── NEEDS_REVISION → optimizer → evaluator
```

MongoDB applies deterministic eligibility constraints; Claude generates and evaluates recommendations only from eligible properties. The application validates selected IDs, owns the bounded feedback loop and termination, and stops after the configured iteration limit. Optimization can improve a result but does not guarantee convergence.

Lab 05 — Orchestrator–Worker demonstrates an Educational Legal Case Preparation Assistant using synthetic scenarios:

```text
Natural-language case
    ↓
Claude Orchestrator
    ↓
Dynamic ExecutionPlan
    ↓
N generic workers executing generated tasks concurrently
    ↓
Worker results / isolated failures
    ↓
Claude Synthesizer
    ↓
Structured CasePreparationSummary
```

The key distinction from Lab 03 is that Parallelization begins with independent work already defined by the application. In Orchestrator–Worker, Claude dynamically determines which substantial tasks are required for the specific request; the application then executes those generated tasks. `CaseTask` and `ExecutionPlan` provide structured decomposition contracts, one reusable generic worker handles every task instead of hard-coded worker types, and each worker returns a structured `WorkerResult`. Independent tasks run concurrently, while the application owns execution policy, concurrency, failure isolation, stopping, and synthesis coordination.

The workflow preserves successful worker executions when another worker fails. Failed analysis remains explicitly visible as incomplete rather than being silently reconstructed by the synthesizer. The final structured `CasePreparationSummary` consolidates the available findings, uncertainties, verification items, and incomplete areas. The model-call pattern is one orchestrator call, `N` concurrent worker calls, and one synthesizer call: `N + 2` Claude calls. This is a workflow with application-owned boundaries, not an autonomous or multi-agent system.

The implementation uses structured Pydantic contracts at component boundaries and tests synthesizer failure visibility, worker-failure isolation, continuation to synthesis, preservation of successful executions, and complete execution-state handoff. See [the workflow-engineering README](projects/workflow-engineering/README.md) for the component architecture, runnable demo, prompts, validation, and implementation details.

Lab 05 is educational only: its legal scenarios are synthetic, it is not legal advice, and it does not integrate authoritative or current legal sources. Production use would require verified authoritative sources plus appropriate safety, security, privacy, and evaluation controls.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
