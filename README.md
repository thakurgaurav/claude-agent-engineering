# Claude Agent Engineering

An engineering showcase for building AI workflows and agentic systems with Claude.

This repository demonstrates the engineering patterns behind AI applications through working implementations. It begins with controlled LLM workflows and progressively extends toward agents, tools, context and memory management, multi-agent systems, MCP, agent runtimes, reliability, security, and evaluation.

## Engineering Approach

The repository is organized around one principle:

> Understand and demonstrate the underlying engineering mechanism before introducing higher-level abstractions.

Each project focuses on a specific system responsibility and contains its own implementation, prompts, tests, architecture, and documentation.

## Projects

### 01 — Workflow Engineering

**Status:** In Progress

Demonstrates patterns for coordinating multiple model operations while application code remains responsible for execution flow.

Currently implemented:

- ✅ Prompt Chaining
- ⬜ Routing
- ⬜ Parallelization & Aggregation
- ⬜ Evaluator–Optimizer
- ⬜ Orchestrator–Worker

The current Prompt Chaining implementation transforms a natural-language decision request through four specialized Claude stages:

```text
Decision Request
      ↓
Understand Decision
      ↓
Extract Constraints
      ↓
Define Evaluation Criteria
      ↓
Create Research Plan
```

See [`projects/workflow-engineering`](projects/workflow-engineering/) for architecture, implementation details, and execution instructions.

## Repository Structure

```text
claude-agent-engineering/
├── README.md
│
├── projects/
│   └── workflow-engineering/
│       ├── README.md
│       ├── pyproject.toml
│       ├── src/
│       └── tests/
│
├── shared/
│   └── src/
│       └── claude_engineering/
│
├── .env.example
├── pyproject.toml
└── uv.lock
```

`projects/` contains focused engineering implementations.

`shared/` contains reusable Claude infrastructure used across projects.

## Current Engineering Demonstrations

The repository currently demonstrates:

- Claude API integration
- Multi-stage prompt chaining
- Explicit workflow orchestration
- Externalized prompt management
- Reusable model invocation
- Per-stage inference configuration
- Intermediate state propagation
- Claude content-block handling
- Output truncation detection
- Bounded intermediate outputs

Detailed implementation documentation lives with the project that demonstrates each capability.

## What's Next

The repository will expand incrementally as additional capabilities are implemented.

The progression will move from:

```text
Workflows
    ↓
Agents
    ↓
Tools & MCP
    ↓
Context & Memory
    ↓
Multi-Agent Systems
    ↓
Agent Runtimes
    ↓
Reliability, Security & Evaluation
```

Only implemented capabilities receive detailed documentation.

## Engineering Objective

Calling a model is only one part of an AI system.

The broader engineering challenge is controlling how reasoning is decomposed, how context moves through the system, how outputs are validated, how tools are invoked, how state is maintained, and how increasingly autonomous behavior remains observable and controlled.

**Claude Agent Engineering** demonstrates those responsibilities through working implementations.