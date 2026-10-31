# Claude Agent Engineering

An engineering showcase for building AI workflows and agentic systems with Claude. The repository progresses from application-controlled workflows toward agents, tools, context, memory, multi-agent systems, runtimes, reliability, security, and evaluation.

## Engineering approach

> Understand and demonstrate the underlying engineering mechanism before introducing higher-level abstractions.

Each project separates implementation, runnable demonstrations, prompts, tools, provider integrations, and tests.

## Projects

### 01 — Workflow Engineering

**Status:** In progress

Implemented:

- [x] Prompt Chaining
- [x] Routing
- [x] Parallelization + Aggregation
- [x] Evaluator–Optimizer
- [ ] Orchestrator–Worker

The project progresses from deterministic application-controlled execution to model-directed decisions within explicit boundaries:

```text
Prompt Chaining → Routing → Parallelization + Aggregation
                 → Evaluator–Optimizer → Orchestrator–Worker
```

It demonstrates semantic routing and validation, Claude Tool Use, concurrent tool execution, fan-out/fan-in orchestration, real provider integrations, semantic aggregation and evaluation, feedback-driven optimization, structured-output validation and bounded repair, failure isolation, Pydantic contracts, MongoDB hard filtering, and separation of Claude-facing capabilities from provider infrastructure.

The current implementation remains workflow-oriented: Claude reasons, selects routes/tools, aggregates evidence, evaluates results, and proposes refinements; the application owns execution boundaries, concurrency, retries, validation, lifecycle, iteration limits, failure handling, and termination. Optimization is bounded and does not guarantee convergence.

See [the workflow-engineering README](projects/workflow-engineering/README.md) for architecture, setup, demonstrations, and validation details.

## License

This project is licensed under the [Apache License 2.0](LICENSE).
