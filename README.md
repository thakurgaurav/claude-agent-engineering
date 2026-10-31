# Claude Agent Engineering

An engineering showcase for building AI workflows and agentic systems with Claude. The repository progresses from application-controlled workflows toward agents, tools, context, memory, multi-agent systems, runtimes, reliability, security, and evaluation.

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

Lab 05 demonstrates an Educational Legal Case Preparation Assistant using synthetic scenarios. A Claude orchestrator creates a structured `ExecutionPlan` of `CaseTask` objects; one reusable generic worker executes each generated task concurrently, returning structured `WorkerResult` contracts; and a Claude synthesizer produces a structured `CasePreparationSummary`. Individual worker failures are isolated and remain visible as incomplete analysis rather than being silently reconstructed. The pattern remains a workflow: the application owns execution policy, concurrency, stopping, failure handling, and synthesis coordination. It is not an autonomous or multi-agent system.

Lab 05 is educational only: its legal scenarios are synthetic, it is not legal advice, and it does not integrate authoritative or current legal sources. Production use would require verified authoritative sources plus appropriate safety, security, privacy, and evaluation controls.

See [the workflow-engineering README](projects/workflow-engineering/README.md) for architecture, setup, demonstrations, and validation details.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
