# Claude Agent Engineering

An engineering showcase for building AI workflows and agentic systems with Claude.

The repository demonstrates the engineering patterns behind AI applications—from structured LLM workflows to tool-using agents, context and memory management, multi-agent coordination, and agent runtimes.

The implementation evolves incrementally, with each capability added as a working engineering demonstration.

---

## Current Implementation

### Workflow Engineering — Prompt Chaining

The current implementation demonstrates **prompt chaining** through a Personal Research & Decision workflow.

Instead of asking the model to process the entire decision in one large prompt, the task is decomposed into specialized stages with explicit responsibilities.

```text
Decision Request
      │
      ▼
Understand Decision
      │
      ▼
Extract Constraints
      │
      ▼
Define Evaluation Criteria
      │
      ▼
Create Research Plan
```

Each stage receives a defined input, performs one responsibility, and passes its output to the appropriate downstream stage.

The execution sequence is controlled by application code rather than by the model.

---

## Example Decision

The current workflow can process a request such as:

```text
I need a laptop under $1,500 for Java development,
AI experimentation, and occasional video editing.

Battery life is important and I want to keep it
for at least five years.
```

Rather than immediately recommending a laptop, the workflow progressively determines:

1. What decision is being made?
2. What constraints and preferences matter?
3. How should candidate options eventually be evaluated?
4. What evidence needs to be collected before making the decision?

The final result is an evidence-oriented **research plan**.

External research, tool execution, and final recommendations are intentionally outside the current implementation.

---

## Stage 1 — Understand the Decision

The first stage converts the original natural-language request into a clearer description of the decision.

It identifies:

- the decision being made
- the user's primary goal
- options already mentioned
- explicitly provided context

The stage is instructed not to recommend an option and not to invent missing information.

```text
Raw User Request
       │
       ▼
Understand Decision
       │
       ▼
Normalized Decision Description
```

This creates a cleaner input for subsequent stages.

---

## Stage 2 — Extract Constraints

The normalized decision is passed to the constraint-extraction stage.

The stage separates information into:

### Hard Constraints

Requirements that candidate options must satisfy.

Examples:

```text
Budget < $1,500
Supports Java development
Supports AI experimentation
```

### Soft Preferences

Important requirements that may be negotiable.

Example:

```text
Good battery life
```

### Unknowns

Missing information that could materially affect the decision.

Examples could include:

```text
Required RAM
Operating system preference
Local GPU requirements
Portability expectations
```

This stage converts an open-ended decision into a more explicit decision contract.

---

## Stage 3 — Define Evaluation Criteria

Constraints are transformed into criteria that can later be used to compare candidate options.

For each criterion, the workflow identifies:

- criterion
- source: hard constraint or soft preference
- evidence needed

For example:

```text
Constraint
    │
    ▼
Budget < $1,500
    │
    ▼
Evaluation Criterion
    │
    ▼
Total Purchase Price
    │
    ▼
Evidence Needed
    │
    ▼
Actual configuration price
```

Another example:

```text
AI experimentation
       │
       ▼
Hardware / Software Capability
       │
       ├── GPU capability
       ├── memory capacity
       └── framework compatibility
```

The stage therefore separates **what matters** from the evidence that will eventually be required to evaluate it.

---

## Stage 4 — Create the Research Plan

The final stage determines what information should be collected before candidate options are compared.

For each research item, it identifies:

- research item
- evidence needed
- preferred source type
- evaluation criteria supported

Example:

```text
Research Item
    │
    ▼
Local AI Capability
    │
    ├── Evidence
    │     GPU / accelerator
    │     VRAM or unified memory
    │     AI benchmark results
    │
    ├── Sources
    │     Manufacturer specifications
    │     Independent benchmarks
    │
    └── Supports
          AI experimentation requirement
```

The workflow therefore ends with a structured plan describing **what needs to be researched and why**.

It does not yet perform that research.

---

## Prompt Chaining Architecture

The workflow is explicitly orchestrated by application code.

```text
Application
     │
     ▼
Load Prompt Template
     │
     ▼
Configure Model Invocation
     │
     ▼
Claude API
     │
     ▼
Validate Response
     │
     ▼
Store Intermediate Result
     │
     ▼
Next Workflow Stage
```

The current chain is conceptually:

```text
decision_request
      │
      ▼
understand_decision()
      │
      │ decision_understanding
      ▼
extract_constraints()
      │
      │ constraints
      ▼
define_evaluation_criteria()
      │
      │ evaluation_criteria
      ▼
create_research_plan()
      │
      ▼
research_plan
```

Claude performs the model reasoning within each stage.

The application controls:

- which stage executes
- execution order
- what context each stage receives
- inference configuration
- output limits
- response validation
- propagation of intermediate results

This distinction is important because the current implementation is a **workflow**, not an autonomous agent.

---

## Prompt Management

Model instructions are stored separately from workflow code.

```text
workflow_engineering/
├── prompt_chain.py
├── prompt_loader.py
└── prompts/
    ├── understand_decision.txt
    ├── extract_constraints.txt
    ├── define_evaluation_criteria.txt
    └── create_research_plan.txt
```

This separates:

```text
Python
  → execution behavior

Prompt files
  → model instructions

Prompt loader
  → prompt-resource access
```

Prompts are loaded using Python package resources rather than relying on the process's current working directory.

This allows workflow code to remain focused on orchestration rather than containing large embedded prompt strings.

---

## Claude Invocation

Model invocation is centralized so individual workflow stages do not need to duplicate Claude API interaction logic.

Conceptually:

```text
Workflow Stage
      │
      ▼
_call_model()
      │
      ├── Claude client
      ├── model configuration
      ├── token budget
      ├── reasoning configuration
      └── response handling
              │
              ▼
           Claude API
```

Each workflow stage can still specify configuration appropriate to its responsibility.

For example:

```text
Understand Decision
      ↓
smaller output budget

Extract Constraints
      ↓
larger output budget

Evaluation Criteria
      ↓
bounded structured response

Research Plan
      ↓
larger but explicitly bounded response
```

This avoids treating every model invocation as having identical inference requirements.

---

## Response Handling

Claude responses are treated as structured content rather than assuming that the first response block always contains text.

The implementation handles text content blocks explicitly.

This becomes increasingly important as the repository introduces capabilities such as reasoning and tool use, where responses may contain different content-block types.

---

## Truncation Detection

A model invocation returning text does not necessarily mean the response is complete.

The workflow checks Claude's stop reason.

If generation stops because the configured output-token limit was reached:

```text
stop_reason = max_tokens
```

the workflow raises an error rather than passing incomplete output into the next stage.

```text
Claude Response
      │
      ▼
Was generation complete?
      │
      ├── Yes → continue
      │
      └── No
           │
           ▼
       Fail visibly
```

This prevents an incomplete upstream response from silently affecting every downstream stage.

During implementation, this validation exposed stages whose prompts allowed unnecessarily verbose output.

Instead of continually increasing token limits, the output contracts were tightened to produce more concise downstream context.

---

## Bounded Intermediate Outputs

The workflow deliberately limits the amount of information produced by individual stages.

For example, evaluation and research stages constrain the number of generated items and request concise fields.

This helps control:

- unnecessary output
- latency
- token usage
- downstream context size
- duplicated information
- truncation risk

The intermediate output of one model invocation becomes input context for later invocations, so unnecessary output can compound across a multi-stage workflow.

---

## Current Engineering Features

The repository currently demonstrates:

- Multi-stage prompt chaining
- Explicit workflow orchestration
- Specialized stage responsibilities
- Intermediate state propagation
- Externalized prompt templates
- Package-based prompt loading
- Reusable Claude client
- Centralized Claude invocation
- Per-stage output-token budgets
- Configurable reasoning behavior
- Claude content-block handling
- Empty-response validation
- Output truncation detection
- Bounded model responses
- Prompt refinement based on observed behavior
- Separation of configuration, prompts, and workflow logic

---

## Repository Structure

```text
claude-agent-engineering/
├── projects/
│   └── workflow-engineering/
│       ├── pyproject.toml
│       ├── src/
│       │   └── workflow_engineering/
│       │       ├── __init__.py
│       │       ├── prompt_chain.py
│       │       ├── prompt_loader.py
│       │       └── prompts/
│       │           ├── __init__.py
│       │           ├── understand_decision.txt
│       │           ├── extract_constraints.txt
│       │           ├── define_evaluation_criteria.txt
│       │           └── create_research_plan.txt
│       │
│       └── tests/
│           └── test_claude_connection.py
│
├── shared/
│   ├── pyproject.toml
│   └── src/
│       └── claude_engineering/
│           ├── __init__.py
│           ├── claude_client.py
│           ├── config.py
│           └── constants.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

The repository separates reusable Claude infrastructure from individual engineering demonstrations.

```text
shared/
   ↓
Reusable Claude infrastructure

projects/
   ↓
Focused engineering implementations
```

---

## Setup

### Requirements

- Python 3.12+
- `uv`
- Anthropic API credentials

Clone the repository and synchronize dependencies.

Create the environment configuration:

```bash
cp .env.example .env
```

Configure the Anthropic API key:

```text
ANTHROPIC_API_KEY=
```

The `.env` file is excluded from Git and should never be committed.

Synchronize dependencies:

```bash
uv sync
```

---

## Run the Current Workflow

From the repository root:

```bash
uv run --project projects/workflow-engineering \
  python projects/workflow-engineering/src/workflow_engineering/prompt_chain.py
```

The workflow executes the complete prompt chain and returns the generated research plan.

---

## What's Next

The repository will be extended incrementally as additional capabilities are implemented.

Upcoming demonstrations will introduce concepts such as:

- workflow routing
- parallel execution and aggregation
- evaluator-optimizer loops
- orchestrator-worker workflows
- tool use
- agent execution loops
- context and memory management
- multi-agent coordination
- MCP integration
- agent runtime and harness design
- reliability, security, observability, and evaluation

Detailed documentation will be added as each capability is actually implemented.

---

## Engineering Objective

Calling an LLM API is only one component of an AI system.

The broader engineering challenge is controlling:

```text
Reasoning decomposition
        ↓
Context construction
        ↓
Model execution
        ↓
Output validation
        ↓
Tool interaction
        ↓
State management
        ↓
Failure handling
        ↓
Reliable system behavior
```

**Claude Agent Engineering** demonstrates these capabilities incrementally through working implementations.