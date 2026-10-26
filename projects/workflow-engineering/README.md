# Workflow Engineering with Claude

A hands-on engineering demonstration of controlled AI workflow patterns using Claude.

The project focuses on how application code can coordinate model reasoning through predefined execution structures before moving into autonomous agent systems.

## Workflow Patterns

| Pattern | Status |
|---|---|
| Prompt Chaining | ✅ Implemented |
| Routing | ✅ Implemented |
| Parallelization + Aggregation | ⬜ Next |
| Evaluator–Optimizer | ⬜ Planned |
| Orchestrator–Worker | ⬜ Planned |

---

# 01 — Prompt Chaining

Prompt Chaining decomposes a complex request into a predefined sequence of focused model interactions.

## Use Case

The workflow converts an open-ended decision request into a structured research plan.

Example:

```text
I need a laptop under $1,500 for Java development,
AI experimentation, and occasional video editing.
Battery life is important and I want to keep it
for at least five years.
```

## Architecture

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

Each stage performs one focused responsibility.

The output of one stage becomes context for the next stage.

## Engineering Characteristics

The implementation demonstrates:

- task decomposition
- focused prompts
- explicit state propagation
- per-stage model configuration
- bounded outputs
- response validation
- truncation detection
- externalized prompt templates

The execution path is predefined by application code.

Claude reasons within each stage but does not determine which stage executes next.

Therefore, this is a **workflow**, not an autonomous agent.

---

# 02 — Routing

Routing introduces conditional execution.

Instead of sending every request through the same downstream processing path, Claude classifies the semantic intent of the decision and the application dispatches execution to a predefined specialized path.

## Goal

The routing workflow demonstrates:

```text
Same Entry Point
      ↓
Semantic Classification
      ↓
Validated Route
      ↓
Application-Controlled Dispatch
      ↓
Route-Specific Processing
      ↓
Route-Specific Decision Plan
```

## Supported Routes

The application currently defines four routes:

```text
PURCHASE
CAREER
TRAVEL
GENERAL
```

These routes are application-defined.

Claude cannot dynamically create additional execution paths.

## Complete Architecture

```text
Natural-Language Decision Request
               ↓
        Understand Decision
               ↓
        Extract Constraints
               ↓
   Define Evaluation Criteria
               ↓
          Claude Router
               ↓
       DecisionRoute Validation
               ↓
    ┌──────────┼──────────┬──────────┐
    ↓          ↓          ↓          ↓
PURCHASE     CAREER     TRAVEL     GENERAL
    ↓          ↓          ↓          ↓
Purchase    Career      Travel     General
 Plan        Plan        Plan        Plan
    └──────────┴──────────┴──────────┘
               ↓
      Route-Specific Result
```

## Semantic Router

Claude is used as a bounded semantic classifier.

Conceptually:

```text
Input:
"The user needs to choose a laptop..."

Output:
PURCHASE
```

The router prompt explicitly restricts output to:

```text
PURCHASE
CAREER
TRAVEL
GENERAL
```

The returned model output is converted into the application's typed route:

```python
DecisionRoute(model_output.strip())
```

This creates an explicit model/application boundary:

```text
Model Output
     ↓
Untrusted String
     ↓
DecisionRoute Validation
     ↓
Validated Application Value
```

Unsupported values fail validation instead of silently entering the execution flow.

## Application-Controlled Dispatch

After Claude selects a valid route, Python controls what actually executes.

Conceptually:

```text
DecisionRoute.PURCHASE
        ↓
create_purchase_plan()

DecisionRoute.CAREER
        ↓
create_career_plan()

DecisionRoute.TRAVEL
        ↓
create_travel_plan()

DecisionRoute.GENERAL
        ↓
create_general_plan()
```

This separation is fundamental:

> Claude selects among allowed routes. The application defines and controls the capabilities behind those routes.

## Route-Specific Behavior

The four routes produce meaningfully different downstream plans.

### PURCHASE

Focuses on areas such as:

- product or service requirements
- measurable characteristics
- price
- total ownership considerations
- compatibility
- reliability
- long-term suitability

### CAREER

Focuses on areas such as:

- skill relevance
- professional growth
- time investment
- financial cost
- credential or market recognition
- long-term career value
- alternatives

### TRAVEL

Focuses on areas such as:

- destination suitability
- timing
- weather
- transportation
- accommodation
- total trip cost
- traveler preferences
- practical constraints

### GENERAL

Provides a fallback decision-analysis path for requests that do not belong to one of the specialized domains.

It focuses on:

- relevant decision factors
- missing information
- constraints
- trade-offs
- actionable next steps

## Example Routing Behavior

The same application entry point was validated with multiple decision types:

```text
Laptop decision
      ↓
PURCHASE
      ↓
Purchase-specific plan


AI certification decision
      ↓
CAREER
      ↓
Career-specific plan


Vacation decision
      ↓
TRAVEL
      ↓
Travel-specific plan


Personal schedule decision
      ↓
GENERAL
      ↓
General decision plan
```

The important behavior is not simply that Claude returns different labels.

The selected label causes the application to execute a **different predefined downstream path**.

## Workflow, Not Agent

Routing introduces model-directed branching, but the system is still a workflow.

Claude can decide:

```text
Which supported route best matches this request?
```

Claude cannot decide:

```text
What arbitrary capability should I execute next?
```

The application still owns:

- available routes
- route validation
- route handlers
- execution boundaries
- workflow termination

This distinction becomes important when later projects introduce agent loops where the model has greater control over what happens next.

---

# Project Organization

Implementation and runnable demonstrations are intentionally separated.

```text
src/workflow_engineering/
├── demos/
│   ├── __init__.py
│   ├── prompt_chaining_demo.py
│   └── routing_demo.py
│
├── prompts/
│   ├── __init__.py
│   ├── understand_decision.txt
│   ├── extract_constraints.txt
│   ├── define_evaluation_criteria.txt
│   ├── create_research_plan.txt
│   ├── route_decision.txt
│   ├── create_purchase_plan.txt
│   ├── create_career_plan.txt
│   ├── create_travel_plan.txt
│   └── create_general_plan.txt
│
├── model.py
├── prompt_chain.py
├── prompt_loader.py
└── routing.py
```

The responsibilities are:

```text
model.py
    ↓
Common model invocation policy

prompt_chain.py
    ↓
Prompt Chaining implementation

routing.py
    ↓
Routing implementation

prompts/
    ↓
Model behavior contracts

demos/
    ↓
Independently runnable demonstrations

tests/
    ↓
Automated verification
```

This keeps demonstration inputs and console output out of the reusable workflow implementation.

---

# Model Invocation

Common model invocation behavior lives in:

```text
model.py
```

This layer handles concerns such as:

- Claude model selection
- maximum output tokens
- thinking configuration
- Anthropic response content blocks
- text extraction
- truncation detection

Individual workflow patterns use this common capability instead of implementing their own Claude invocation logic.

---

# Prompt Management

Prompts are stored as packaged text resources rather than embedded directly inside Python functions.

For example:

```text
prompts/
├── route_decision.txt
├── create_purchase_plan.txt
├── create_career_plan.txt
├── create_travel_plan.txt
└── create_general_plan.txt
```

This keeps:

```text
Workflow orchestration
```

separate from:

```text
Model instructions
```

and allows individual prompts to evolve without mixing prompt content into application control logic.

---

# Response Handling

Anthropic responses may contain different content-block types.

The implementation does not assume:

```python
response.content[0].text
```

Instead, text content is explicitly selected from text blocks.

Conceptually:

```text
Claude Response
      ↓
Multiple Content Blocks
      ↓
Select Text Blocks
      ↓
Join Text Content
      ↓
Application Result
```

The implementation also checks the response stop reason.

If generation stops because the configured output-token limit is reached, the response is treated as incomplete rather than silently continuing with truncated data.

---

# Running the Demonstrations

## Prompt Chaining

```bash
uv run --project projects/workflow-engineering \
  python -m workflow_engineering.demos.prompt_chaining_demo
```

## Routing

```bash
uv run --project projects/workflow-engineering \
  python -m workflow_engineering.demos.routing_demo
```

The `DECISION_REQUEST` in the routing demonstration can be changed to observe different semantic routes and downstream execution paths.

Examples include:

```text
Laptop decision        → PURCHASE
AI certification       → CAREER
Vacation decision      → TRAVEL
Personal scheduling    → GENERAL
```

---

# Engineering Validation

The project uses automated tests, linting, and static type checking.

Run:

```bash
uv run pytest
```

```bash
uv run ruff check .
```

```bash
uv run pyright
```

Routing tests validate:

- supported route values
- rejection of unsupported routes
- dispatcher behavior
- route-specific handler selection

Live model behavior has also been exercised through the runnable demonstrations for:

```text
PURCHASE
CAREER
TRAVEL
GENERAL
```

---

# Current Engineering Boundary

The current implementation intentionally does not introduce:

- autonomous agent loops
- tool execution
- memory
- dynamic route creation
- multi-agent coordination

The objective is to make each workflow mechanism explicit before adding greater autonomy.

At the current stage:

```text
Application
    ↓
owns execution structure

Claude
    ↓
performs bounded reasoning within that structure
```

---

# Next — Parallelization + Aggregation

The next workflow pattern explores operations that do not need to execute sequentially.

Instead of:

```text
A → B → C
```

we will examine:

```text
          ┌→ Worker A ─┐
Request ──┼→ Worker B ─┼→ Aggregator → Result
          └→ Worker C ─┘
```

This introduces the next engineering question:

> Which model operations actually depend on each other, and which can safely execute concurrently?

That becomes **Workflow Pattern 03 — Parallelization + Aggregation**.