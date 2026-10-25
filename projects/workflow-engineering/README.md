# Workflow Engineering with Claude

A hands-on engineering demonstration of workflow patterns for coordinating multiple Claude model operations while application code controls the execution path.

This project will demonstrate five workflow patterns:

- ✅ Prompt Chaining
- ⬜ Routing
- ⬜ Parallelization & Aggregation
- ⬜ Evaluator–Optimizer
- ⬜ Orchestrator–Worker

The first pattern, **Prompt Chaining**, is implemented and documented below.

---

# 01 — Prompt Chaining

Prompt chaining decomposes a larger task into a sequence of focused model operations.

Instead of asking Claude to perform the entire task in one invocation, each stage has a specific responsibility and passes relevant output to downstream stages.

## Demonstration Use Case

The implementation uses a **Personal Research & Decision** workflow.

Example request:

```text
I need a laptop under $1,500 for Java development,
AI experimentation, and occasional video editing.

Battery life is important and I want to keep it
for at least five years.
```

The workflow does not immediately recommend a laptop.

Instead, it progressively transforms the request into an evidence-oriented research plan.

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

The application controls this sequence. Claude performs the model reasoning within each stage.

For that reason, this implementation is a **workflow rather than an autonomous agent**.

---

## Stage 1 — Understand the Decision

The first stage normalizes the original request.

It identifies:

- the decision being made
- the user's primary goal
- options already mentioned
- explicitly provided context

It is explicitly instructed not to recommend an option or invent missing information.

```text
Raw Decision Request
        │
        ▼
 understand_decision()
        │
        ▼
Normalized Decision
```

---

## Stage 2 — Extract Constraints

The normalized decision becomes the input to the second stage.

This stage separates information into:

### Hard Constraints

Requirements that candidate options must satisfy.

### Soft Preferences

Important requirements that may be negotiable.

### Unknowns

Missing information that could materially affect the decision.

```text
Normalized Decision
        │
        ▼
extract_constraints()
        │
        ├── Hard Constraints
        ├── Soft Preferences
        └── Unknowns
```

This provides a clearer contract for downstream processing.

---

## Stage 3 — Define Evaluation Criteria

The extracted constraints are transformed into criteria that could later be used to evaluate candidate options.

Each criterion identifies:

- the criterion
- whether it originated from a hard constraint or soft preference
- evidence needed to evaluate it

For example:

```text
Budget < $1,500
       │
       ▼
Total Purchase Price
       │
       ▼
Evidence Required
       │
       ▼
Actual configuration price
```

This separates **what matters to the decision** from **the evidence needed to evaluate it**.

---

## Stage 4 — Create the Research Plan

The final stage determines what information should be collected before candidate options are compared.

Each research item identifies:

- research item
- evidence needed
- preferred source type
- evaluation criteria supported

Conceptually:

```text
Evaluation Criteria
        │
        ▼
Evidence Requirements
        │
        ▼
Research Items
        │
        ▼
Research Plan
```

The current workflow stops here.

It determines **what should be researched**, but does not yet perform external research, invoke tools, or recommend a candidate.

Those capabilities will be introduced separately as the repository expands.

---

# Architecture

The workflow is explicitly orchestrated by application code.

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

Claude does not independently choose which stage executes next.

The application determines:

- execution order
- context passed between stages
- prompt selection
- model configuration
- output-token budgets
- response validation

Claude performs the reasoning required by each individual stage.

---

# Prompt Management

Model instructions are maintained separately from workflow orchestration.

```text
src/workflow_engineering/
├── prompt_chain.py
├── prompt_loader.py
└── prompts/
    ├── understand_decision.txt
    ├── extract_constraints.txt
    ├── define_evaluation_criteria.txt
    └── create_research_plan.txt
```

Responsibilities are separated as:

```text
prompt_chain.py
      │
      └── Workflow orchestration

prompt_loader.py
      │
      └── Prompt resource loading

prompts/*.txt
      │
      └── Model instructions
```

Prompt resources are loaded through Python package resources rather than relying on a particular working directory.

---

# Model Invocation

Common Claude invocation behavior is centralized rather than duplicated across workflow stages.

Each stage can still specify inference settings appropriate to its responsibility.

For example:

```text
Understand Decision
      │
      └── max_tokens = 400

Extract Constraints
      │
      └── max_tokens = 800

Define Evaluation Criteria
      │
      └── max_tokens = 1000

Create Research Plan
      │
      └── max_tokens = 1200
```

This demonstrates an important workflow design principle:

**Different stages do not necessarily have identical inference requirements.**

---

# Response Validation

A successful API request does not necessarily mean a workflow stage completed successfully.

During implementation, some responses reached their configured output-token limit:

```text
stop_reason = max_tokens
```

The response still contained valid-looking text, but it was incomplete.

Passing that response downstream could cause subsequent stages to reason over partial information.

The model invocation therefore detects truncation and fails visibly rather than silently propagating incomplete output.

```text
Claude Response
      │
      ▼
Validate Completion
      │
      ├── Complete ──────► Continue
      │
      └── Truncated
              │
              ▼
          Raise Error
```

The solution was not simply to keep increasing token limits.

Prompts were also refined to produce bounded outputs, including limits on the number of generated criteria and research items.

---

# Intermediate Output Boundaries

Prompt chaining creates an important engineering boundary:

```text
Model Call A
     │
     │ intermediate output
     ▼
Model Call B
```

Anything unnecessary, incorrect, incomplete, or ambiguous in that intermediate output becomes context for the next stage.

The implementation therefore demonstrates:

- bounded intermediate outputs
- stage-specific responsibilities
- explicit context propagation
- truncation detection
- prompt refinement
- per-stage token budgets

One observed behavior was **semantic drift** between stages: information categorized one way upstream could be interpreted differently by a downstream model call.

That behavior is intentionally documented rather than hidden. Later workflow patterns and evaluation mechanisms can address this class of problem more systematically.

---

# Current Engineering Features

The Prompt Chaining implementation currently demonstrates:

- Multi-stage Claude workflows
- Explicit application-controlled execution
- Specialized model responsibilities
- External prompt templates
- Package-resource prompt loading
- Reusable Claude client
- Centralized model invocation
- Per-stage output-token budgets
- Configurable reasoning behavior
- Claude content-block handling
- Empty-response validation
- Output truncation detection
- Bounded intermediate outputs
- Explicit state propagation
- Separation of prompts, configuration, and orchestration

---

# Project Structure

```text
workflow-engineering/
├── README.md
├── pyproject.toml
├── src/
│   └── workflow_engineering/
│       ├── __init__.py
│       ├── prompt_chain.py
│       ├── prompt_loader.py
│       └── prompts/
│           ├── __init__.py
│           ├── understand_decision.txt
│           ├── extract_constraints.txt
│           ├── define_evaluation_criteria.txt
│           └── create_research_plan.txt
└── tests/
    └── test_claude_connection.py
```

Reusable Claude configuration and client infrastructure live in the repository-level `shared` package.

---

# Running the Demonstration

From the repository root:

```bash
uv run --project projects/workflow-engineering \
  python projects/workflow-engineering/src/workflow_engineering/prompt_chain.py
```

The workflow executes all four stages and returns the generated research plan.

---

# Next Pattern — Routing

Prompt chaining follows a predefined sequence:

```text
A → B → C → D
```

The next implementation will introduce **Routing**.

Instead of every request following the same sequence, the workflow will classify the request and select an appropriate predefined execution path.

```text
                  ┌── Path A
Request → Router ─┼── Path B
                  └── Path C
```

The application will still control the available paths, keeping this within workflow engineering rather than autonomous agent execution.