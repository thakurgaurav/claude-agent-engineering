# Claude Agent Engineering

An engineering showcase for building AI workflows and agentic systems with Claude.

This repository demonstrates AI engineering patterns through working implementations, beginning with controlled workflows and progressively moving toward agents, tools, context, memory, multi-agent systems, runtimes, reliability, security, and evaluation.

## Engineering Approach

The repository follows one principle:

> Understand and demonstrate the underlying engineering mechanism before introducing higher-level abstractions.

Each project focuses on a specific engineering capability and keeps implementation, runnable demonstrations, prompts, tools, provider integrations, and tests clearly separated.

## Projects

### 01 — Workflow Engineering

**Status:** In Progress

Implemented workflow patterns:

- [x] Prompt Chaining
- [x] Routing
- [x] Parallelization + Aggregation
- [ ] Evaluator–Optimizer
- [ ] Orchestrator–Worker

Current workflow progression:

```text id="u5kdxk"
Prompt Chaining
      ↓
Routing
      ↓
Parallelization + Aggregation
      ↓
Evaluator–Optimizer
      ↓
Orchestrator–Worker
```

The project currently demonstrates the progression from deterministic application-controlled workflows toward increasingly model-directed execution:

```text id="rhm7w4"
Prompt Chaining
      ↓
Application controls a predefined sequence

Routing
      ↓
Claude selects among predefined execution paths

Parallelization + Aggregation
      ↓
Claude selects independent capabilities
      +
Application executes them concurrently
      +
Claude semantically aggregates the results
```

Current capabilities demonstrated include:

- multi-stage Claude workflows
- semantic routing
- typed route validation
- application-controlled dispatch
- Claude Tool Use
- multiple tool requests in a single Claude turn
- application-managed concurrent tool execution
- fan-out / fan-in orchestration
- real external tool integrations
- semantic aggregation
- failure isolation and graceful degradation
- shared dependency caching
- separation between Claude-facing capabilities and provider infrastructure

The current implementation remains **workflow-oriented rather than autonomous**. The application still owns execution boundaries, concurrency, failure handling, workflow lifecycle, and termination.

**Current focus:** Evaluator–Optimizer.