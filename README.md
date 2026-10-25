# Claude Agent Engineering

A hands-on engineering showcase demonstrating how to design and build reliable AI workflows, agents, multi-agent systems, and agent runtimes using Claude.

The repository focuses on the engineering patterns behind production-oriented AI systems. Core mechanisms are demonstrated directly before introducing higher-level SDKs and frameworks.

## Current Implementation

### Workflow Engineering

Currently demonstrated:

- Prompt chaining
- Reusable Claude API client
- Externalized prompt management
- Per-stage inference configuration
- Claude response content-block handling
- Output token-limit detection
- Explicit workflow state transitions
- Bounded intermediate outputs

### Decision Research Workflow

The current implementation demonstrates an evidence-oriented decision workflow:

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

A natural-language decision request is progressively transformed into structured requirements, evaluation criteria, and an evidence-oriented research plan.

Actual research, tool execution, and autonomous decision-making will be introduced through subsequent engineering demonstrations.

## Repository Structure

```text
claude-agent-engineering/
├── projects/
│   └── workflow-engineering/
│       ├── src/
│       │   └── workflow_engineering/
│       │       ├── prompt_chain.py
│       │       ├── prompt_loader.py
│       │       └── prompts/
│       └── tests/
│
├── shared/
│   └── src/
│       └── claude_engineering/
│           ├── claude_client.py
│           ├── config.py
│           └── constants.py
│
├── .env.example
├── pyproject.toml
└── uv.lock
```

`shared` contains reusable Claude infrastructure and configuration.

`projects` contains focused implementations demonstrating individual AI engineering patterns and architectural responsibilities.

## Engineering Principles

The repository follows several design principles:

1. **Demonstrate the underlying mechanism before introducing abstraction.**  
   Agent loops, routing, context management, tool execution, and runtime behavior are implemented explicitly before framework abstractions are introduced.

2. **Separate orchestration from model instructions.**  
   Application code controls execution flow while external prompt resources define model behavior.

3. **Treat intermediate outputs as contracts.**  
   A successful model invocation does not automatically imply a valid workflow result.

4. **Bound model behavior deliberately.**  
   Token budgets, reasoning configuration, validation, and stopping conditions are part of application architecture.

5. **Make failure modes observable.**  
   Truncation and invalid responses should fail visibly instead of silently propagating through downstream stages.

6. **Introduce abstractions based on demonstrated requirements.**  
   Architectural components are added when the system has a concrete engineering reason for them.

## Setup

### Requirements

- Python 3.12+
- `uv`
- Anthropic API credentials

Create the local environment file:

```bash
cp .env.example .env
```

Configure the Anthropic API key in `.env`.

Never commit `.env` or API credentials.

Synchronize dependencies:

```bash
uv sync
```

## Running Workflow Engineering

From the repository root:

```bash
uv run --project projects/workflow-engineering \
  python projects/workflow-engineering/src/workflow_engineering/prompt_chain.py
```

## Engineering Demonstration Roadmap

The repository will progressively demonstrate:

### Workflow Engineering

- Prompt chaining
- Routing
- Parallelization and aggregation
- Evaluator-optimizer
- Orchestrator-worker

### Agent Engineering

- Agent execution loops
- Reasoning/action cycles
- Tool use
- State transitions
- Stop policies
- Autonomy boundaries

### Context & Memory Engineering

- Context construction
- Context pruning and compaction
- Working memory
- Durable memory
- Retrieval and memory boundaries

### Multi-Agent Engineering

- Manager-worker architectures
- Supervisor patterns
- Specialized subagents
- Delegation
- Fan-out/fan-in execution

### Tool & MCP Engineering

- Tool schemas
- Tool selection and execution
- Validation
- Error handling
- Model Context Protocol (MCP)

### Harness Engineering

- Runtime architecture
- Execution lifecycle
- State management
- Checkpointing
- Recovery
- Execution budgets

### Production Engineering

- Environment isolation and sandboxes
- Guardrails
- Agent security
- Reliability
- Observability
- Evaluation and regression testing

### Framework Engineering

Implementations will ultimately be compared with higher-level approaches including:

- Claude Agent SDK
- Custom agent runtimes
- LangGraph
- Strands
- PydanticAI

The focus is not merely on framework APIs, but on understanding the architectural responsibilities each abstraction provides.

## Engineering Objective

Calling an LLM API is straightforward.

Engineering a system that can reliably determine what to do, construct the correct context, invoke tools safely, recover from failures, coordinate specialized agents, control cost and latency, and produce evidence-backed results is a substantially different problem.

**Claude Agent Engineering** is a practical showcase of that engineering layer.