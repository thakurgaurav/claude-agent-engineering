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
- [x] Evaluator–Optimizer
- [ ] Orchestrator–Worker

Current workflow progression:

```text
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

The project demonstrates a progression from deterministic application-controlled workflows toward increasingly model-directed execution.

```text
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

Evaluator–Optimizer
      ↓
Claude generates an initial result
      +
Claude evaluates the result against semantic quality criteria
      +
Evaluator feedback drives bounded optimization
      +
Application controls iteration limits and termination
```

### Capabilities Demonstrated

Current implementations demonstrate:

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
- semantic evaluation
- evaluator-generated actionable feedback
- iterative result optimization
- bounded evaluator–optimizer loops
- explicit workflow termination conditions
- structured-output validation
- bounded structured-output repair
- controlled failure after repeated invalid model output
- Pydantic-based model contracts
- MongoDB-backed deterministic filtering
- separation of hard constraints from semantic preferences
- shared dependency management
- separation between Claude-facing capabilities and provider infrastructure

### Evaluator–Optimizer

The Evaluator–Optimizer implementation demonstrates a production-oriented quality-improvement loop using a rental recommendation workflow.

```text
User Request
      ↓
Requirement Interpreter
      ↓
MongoDB Hard Filtering
      ↓
Candidate Properties
      ↓
Generator
      ↓
Recommendation
      ↓
Evaluator
      │
      ├── PASS ──────────────────────► Finish
      │
      └── NEEDS_REVISION
                ↓
         Actionable Feedback
                ↓
            Optimizer
                ↓
      Revised Recommendation
                ↓
            Evaluator
                ↓
          PASS / Continue
                ↓
       Bounded Iteration Limit
```

The implementation separates deterministic and semantic responsibilities:

- MongoDB applies deterministic hard constraints.
- Claude interprets semantic preferences.
- The generator selects and explains a recommendation.
- The evaluator acts as a semantic quality gate.
- The optimizer uses evaluator feedback to revise the result.
- The application owns the optimization loop and maximum iteration count.
- Pydantic validates structured model output before it enters the workflow.
- Invalid structured output receives one bounded repair attempt before failing explicitly.

The workflow also demonstrates an important reliability principle:

> Optimization does not guarantee convergence.

If the evaluator continues to reject a result, the application stops after the configured optimization limit rather than allowing an unbounded model loop.

A successful initial recommendation bypasses optimization entirely:

```text
Generator
    ↓
Evaluator
    ↓
PASS
    ↓
Finish

Optimization iterations: 0
```

A recommendation requiring improvement follows the optimization path:

```text
Generator
    ↓
Evaluator
    ↓
NEEDS_REVISION
    ↓
Optimizer
    ↓
Evaluator
    ↓
PASS or bounded continuation
```

The current implementation remains **workflow-oriented rather than autonomous**. Claude makes semantic decisions inside explicitly defined stages, while the application owns execution boundaries, concurrency, retries, validation, workflow lifecycle, optimization limits, and termination.

**Current focus:** Orchestrator–Worker.