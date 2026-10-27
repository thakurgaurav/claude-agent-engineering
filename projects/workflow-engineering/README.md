# Workflow Engineering with Claude

A hands-on engineering demonstration of controlled AI workflow patterns using Claude.

The project focuses on how application code can coordinate model reasoning through predefined execution structures before moving into autonomous agent systems.

## Workflow Patterns

| Pattern | Status |
|---|---|
| Prompt Chaining | ✅ Implemented |
| Routing | ✅ Implemented |
| Parallelization + Aggregation | ✅ Implemented |
| Evaluator–Optimizer | ⬜ Next |
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

---

# 03 — Parallelization + Aggregation

Parallelization executes independent operations concurrently instead of waiting for each operation to finish sequentially.

This lab also introduces Claude Tool Use and demonstrates the distinction between:

- Claude selecting tools
- the Anthropic tool-use protocol
- application-managed tool execution
- semantic aggregation of independent results

## Use Case — Travel Safety Intelligence

The workflow answers a travel-safety question using three independent real-world signals.

Example:

```text
I'm planning to spend the day outdoors in Los Angeles
on October 30, 2026.

Check the weather forecast, air quality, and recent nearby
fire activity.

Use all three sources and tell me whether conditions look
suitable for outdoor activities.
```

The workflow gathers:

1. Weather — Open-Meteo
2. Air Quality — Open-Meteo Air Quality
3. Recent satellite thermal activity — NASA FIRMS

These operations are independent and can therefore execute concurrently.

## Architecture

```text
Travel Request
      │
      ▼
    Claude
      │
      │ identifies required capabilities
      ▼
Multiple tool_use requests
      │
      ├────────────────┬──────────────────┐
      ▼                ▼                  ▼
   Weather         Air Quality       Fire Activity
      │                │                  │
 Open-Meteo       Open-Meteo AQ        NASA FIRMS
      │                │                  │
      └────────────────┼──────────────────┘
                       ▼
                tool_result[]
                       │
                       ▼
                     Claude
                       │
                       ▼
             Semantic Aggregation
                       │
                       ▼
             Travel Safety Assessment
```

## Claude-Facing Tools

Claude is exposed to capability-oriented tools:

```python
get_destination_weather(destination, travel_date)

get_destination_air_quality(destination, travel_date)

get_nearby_fire_activity(destination)
```

The tool contracts describe capabilities rather than infrastructure.

Claude does not need to know:

- provider API URLs
- API authentication details
- geographic coordinate lookup implementation
- raw provider response formats
- caching implementation
- HTTP client details

Those responsibilities remain inside the application.

## Claude Tool Selection

Claude receives the user request together with the available tool definitions.

For a request requiring weather, air quality, and fire activity, Claude can return multiple `tool_use` blocks in the same response.

Conceptually:

```text
Claude Response
      │
      ├── tool_use: get_destination_weather
      │
      ├── tool_use: get_destination_air_quality
      │
      └── tool_use: get_nearby_fire_activity
```

This is an important distinction:

> Claude can request multiple tools in parallel, but the application determines how those tools are actually executed.

Tool selection and tool execution are separate responsibilities.

## Application-Managed Parallel Execution

Because the three tools are independent, the application executes them concurrently.

Conceptually:

```text
Claude
  │
  ├── Weather tool request
  ├── Air Quality tool request
  └── Fire Activity tool request
             │
             ▼
      asyncio.gather(...)
             │
     ┌───────┼────────┐
     ▼       ▼        ▼
 Weather     AQ      FIRMS
     │       │        │
     └───────┼────────┘
             ▼
       Tool Results
```

The provider integrations currently use synchronous HTTP calls.

They are therefore executed through:

```python
asyncio.to_thread(...)
```

The resulting tasks are coordinated using:

```python
await asyncio.gather(...)
```

This allows independent blocking provider calls to overlap without requiring the provider modules themselves to become asynchronous.

## Fan-Out / Fan-In

The workflow demonstrates a classic fan-out / fan-in pattern.

```text
                    ┌── Weather ───────┐
                    │                  │
Request ──► Claude ─┼── Air Quality ───┼──► Claude ──► Result
                    │                  │
                    └── Fire Activity ─┘
```

### Fan-Out

Claude identifies multiple independent capabilities.

The application executes those operations concurrently.

### Fan-In

The application collects all resulting `tool_result` blocks and returns them to Claude together.

Claude then reasons across the combined evidence.

## Anthropic Tool Protocol

Each Claude tool request contains a tool-use identifier.

Conceptually:

```text
tool_use
    │
    ├── id
    ├── tool name
    └── input
```

After executing the tool, the application returns:

```text
tool_result
    │
    ├── tool_use_id
    └── content
```

The `tool_use_id` associates each result with the tool request that produced it.

Multiple results are returned together before Claude performs final aggregation.

## Semantic Aggregation

The final step is not simple concatenation.

Claude receives evidence from multiple sources:

```text
Weather
   +
Air Quality
   +
Fire Activity
       ↓
     Claude
       ↓
Cross-signal reasoning
       ↓
Travel Safety Assessment
```

Claude can reason about relationships between signals.

For example:

```text
Mild weather
     +
Moderate air quality
     +
Nearby recent thermal detections
     ↓
Generally suitable conditions,
but with environmental caution
```

This is **semantic aggregation**.

The model interprets the combined meaning of the results rather than merely joining strings.

## NASA FIRMS Data Semantics

NASA FIRMS provides satellite thermal/fire hotspot detections.

A detection does not necessarily represent a unique wildfire.

Multiple detections may correspond to:

- the same fire event
- industrial heat sources
- agricultural burning
- volcanic activity
- other thermal anomalies

For this reason, the workflow reports FIRMS data as:

```text
satellite thermal detections
```

rather than interpreting every detection as a separate wildfire.

The Claude-facing tool provides a compact signal including:

- number of nearby detections
- search radius
- search period
- closest detection distance
- most recent detection date

Claude then incorporates that signal into the overall assessment.

## Failure Isolation

Parallel workflows introduce an important reliability concern.

If three independent branches execute concurrently, failure of one branch should not necessarily destroy successful results from the others.

The workflow therefore uses:

```python
await asyncio.gather(
    *tool_tasks,
    return_exceptions=True,
)
```

Conceptually:

```text
Weather ───────────── SUCCESS ───┐
                                 │
Air Quality ──────── TIMEOUT ────┼──► Aggregate available evidence
                                 │
Fire Activity ─────── SUCCESS ───┘
```

A failed tool execution is converted into a tool result with an error indication.

Conceptually:

```text
tool_result
    │
    ├── tool_use_id
    ├── is_error = true
    └── concise failure information
```

Claude can then produce a degraded result using the information that remains available.

This demonstrates **graceful degradation** rather than all-or-nothing execution.

## Shared Location Resolution

All three travel intelligence tools need geographic coordinates.

For example:

```text
"Los Angeles"
      ↓
latitude
longitude
```

Location resolution is therefore implemented as a shared provider capability.

```text
Weather ───────┐
               │
Air Quality ───┼──► resolve_location()
               │
Fire Activity ─┘
```

## Process-Local Location Cache

Repeatedly resolving the same destination would create unnecessary geocoding requests.

Location resolution therefore uses a process-local in-memory cache.

```text
Destination
     │
     ▼
Location Cache
     │
     ├── HIT ─────────────► Location
     │
     └── MISS
           │
           ▼
      Geocoding API
           │
           ▼
       Cache Result
           │
           ▼
        Location
```

The cache is intentionally simple.

It is:

- process-local
- memory-based
- keyed by normalized destination
- shared by the travel tools
- protected during writes

## Minimal Lock Duration

The cache lock is not held during external network operations.

The pattern is:

```text
Cache lookup
     │
     ├── HIT → return
     │
     ▼
    MISS
     │
     ▼
Geocoding HTTP call       ← no lock
     │
     ▼
Parse response            ← no lock
     │
     ▼
Acquire lock
     │
Check cache again
     │
Write if necessary
     │
Release lock
```

This prevents a slow network operation from unnecessarily holding a shared lock.

## Cold-Cache Behavior

During the first concurrent request, multiple branches can observe the cache before any branch has populated it.

For example:

```text
Weather             Air Quality             Fire
   │                     │                    │
cache lookup          cache lookup         cache lookup
   │                     │                    │
 MISS                  MISS                 MISS
   │                     │                    │
geocoding API         geocoding API        geocoding API
```

Once one result has been stored, subsequent requests in the same running process use the cached value.

This is an intentional trade-off for this demonstration.

Preventing duplicate cold-cache work would require additional coordination such as:

- per-key synchronization
- single-flight/request coalescing
- distributed locking for multi-instance systems

Those mechanisms are not required to demonstrate the workflow pattern.

The same general cold-cache problem can also occur with distributed caches such as Redis unless additional coordination or cache warming is used.

## Tool Runner Comparison

The Anthropic SDK provides a Tool Runner that can manage much of the Claude ↔ tool execution lifecycle.

This lab retains a Tool Runner implementation for comparison.

However, the explicit application-managed implementation is used to make concurrency behavior visible.

This lets the project demonstrate the distinction between:

```text
Claude capability
      ↓
Generate multiple tool requests

Anthropic protocol
      ↓
tool_use / tool_result

Application responsibility
      ↓
Execute independent tools concurrently
```

The important engineering conclusion is:

> Claude produces parallel tool calls; the application determines their execution semantics.

## Observed Execution

A successful three-tool run produced approximately:

```text
Claude tool selection:     2.26s
Parallel tool execution:   3.45s
Claude aggregation:        4.26s
Total:                     9.97s
```

The parallel execution phase approaches the latency of the slowest independent branch rather than requiring the application to wait for the sum of all branch latencies.

Conceptually:

```text
Sequential

Weather  ─── 2.5s
AQ             ─── 3.0s
FIRMS                 ─── 2.0s

≈ 7.5s


Parallel

Weather  ───────── 2.5s
AQ       ───────────── 3.0s
FIRMS    ─────── 2.0s

≈ 3.0s
```

Parallelization reduces workflow wall-clock latency when operations are independent.

It does not make the individual external services faster.

## Engineering Lessons

This lab demonstrates:

- Parallelization as a workflow pattern
- Claude Tool Use
- multiple `tool_use` blocks in one Claude response
- Anthropic `tool_use` / `tool_result` protocol
- application-managed concurrency
- fan-out / fan-in orchestration
- `asyncio.gather()`
- `asyncio.to_thread()`
- semantic aggregation
- failure isolation
- graceful degradation
- capability-oriented tool design
- separation of Claude-facing tools from provider implementations
- real external API integration
- shared dependency caching
- minimal lock duration
- cold-cache behavior
- distinction between cache safety and duplicate-work suppression
- distinction between tool selection and tool execution

## Workflow, Not Agent

Despite using Claude Tool Use, this implementation remains a workflow.

Claude has authority to determine which exposed information capabilities are needed.

The application still owns:

```text
tool availability
execution mechanics
concurrency
failure handling
result collection
aggregation lifecycle
workflow termination
```

Conceptually:

```text
Claude
   ↓
"What capabilities do I need?"

Application
   ↓
"How are those capabilities executed?"

Claude
   ↓
"What does the combined evidence mean?"
```

There is no autonomous agent loop in which Claude repeatedly decides arbitrary next actions until a goal is complete.

That distinction becomes important in later Agent Engineering labs.

---

# Project Organization

Implementation, provider integrations, prompts, tests, and runnable demonstrations are intentionally separated.

```text
src/workflow_engineering/
├── demos/
│   ├── __init__.py
│   ├── prompt_chaining_demo.py
│   ├── routing_demo.py
│   └── parallel_travel_demo.py
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
├── tools/
│   ├── __init__.py
│   ├── location.py
│   ├── weather.py
│   ├── air_quality.py
│   ├── fire_activity.py
│   └── travel_tools.py
│
├── config.py
├── model.py
├── parallelization.py
├── prompt_chain.py
├── prompt_loader.py
└── routing.py
```

The responsibilities are:

```text
model.py
    ↓
Common text-oriented Claude invocation policy


prompt_chain.py
    ↓
Prompt Chaining implementation


routing.py
    ↓
Routing implementation


parallelization.py
    ↓
Parallel Tool Use + aggregation orchestration


tools/
    ↓
Claude-facing capabilities and external provider integrations


config.py
    ↓
External service configuration


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

This keeps demonstration inputs and console output out of reusable workflow implementation.

It also separates Claude-facing capability contracts from external provider infrastructure.

---

# Model Invocation

Common text-oriented model invocation behavior lives in:

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

Prompt Chaining and Routing use this common capability.

Parallelization uses the shared Anthropic client directly because the workflow needs access to Claude's structured Tool Use protocol and iterative tool execution lifecycle.

---

# Prompt Management

Prompts are stored as packaged text resources rather than embedded directly inside Python functions where appropriate.

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

# Configuration

Infrastructure and environment-specific values are externalized from implementation modules.

Examples include:

```text
ANTHROPIC_API_KEY

OPEN_METEO_GEOCODING_URL
OPEN_METEO_FORECAST_URL
OPEN_METEO_AIR_QUALITY_URL

NASA_FIRMS_MAP_KEY
NASA_FIRMS_AREA_API_URL
NASA_FIRMS_SOURCE

EXTERNAL_API_TIMEOUT_SECONDS
```

Real credentials belong in the local `.env` file.

`.env.example` documents required configuration without containing secrets.

Application code accesses these values through the configuration layer rather than hard-coding provider infrastructure.

---

# Response Handling

Anthropic responses may contain different content-block types.

The implementation does not assume:

```python
response.content[0].text
```

Instead, relevant content blocks are explicitly selected.

For normal text-oriented model calls:

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

Tool-based workflows additionally process structured:

```text
tool_use
tool_result
```

content blocks.

The implementation also checks response completion behavior so incomplete model output is not silently treated as a successful complete result.

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

The routing demonstration can be changed to observe different semantic routes and downstream execution paths.

Examples:

```text
Laptop decision        → PURCHASE
AI certification       → CAREER
Vacation decision      → TRAVEL
Personal scheduling    → GENERAL
```

## Parallelization + Aggregation

```bash
uv run --project projects/workflow-engineering \
  python -m workflow_engineering.demos.parallel_travel_demo
```

The demonstration performs real external API calls and requires the corresponding environment configuration.

It demonstrates:

```text
Claude tool selection
        ↓
Concurrent provider execution
        ↓
Tool result collection
        ↓
Claude semantic aggregation
```

---

# Engineering Validation

The project uses automated tests, linting, and static type checking.

Run tests:

```bash
uv run pytest -q
```

Run Ruff:

```bash
uv run ruff check projects/workflow-engineering
```

Run Pyright:

```bash
uv run pyright projects/workflow-engineering
```

The current implementation passes:

```text
pytest
ruff
pyright
```

Validation covers workflow behavior as well as static correctness.

Live model behavior has also been exercised through runnable demonstrations for:

```text
Prompt Chaining
Routing
Parallelization + Aggregation
```

---

# Current Engineering Boundary

The project now demonstrates three increasingly dynamic workflow patterns:

```text
Prompt Chaining
      ↓
Predefined sequential execution


Routing
      ↓
Model-selected predefined branch


Parallelization
      ↓
Model-selected capabilities
+
application-managed concurrent execution
+
model-based semantic aggregation
```

The current implementation intentionally does not yet introduce:

- autonomous agent loops
- persistent memory
- multi-agent coordination
- arbitrary model-directed execution
- custom agent harnesses

Tool execution is now present, but it remains inside a controlled workflow.

At the current stage:

```text
Application
    ↓
owns execution lifecycle,
concurrency, boundaries,
failure handling and termination


Claude
    ↓
performs reasoning,
route selection,
tool selection and aggregation
within those boundaries
```

The objective is to understand these control boundaries clearly before increasing model autonomy.

---

# Next — Evaluator–Optimizer

The next workflow pattern introduces iterative improvement.

Instead of accepting the first generated result:

```text
Input
  ↓
Generator
  ↓
Result
```

the workflow introduces an evaluation and refinement cycle:

```text
Input
  ↓
Generator
  ↓
Candidate
  ↓
Evaluator
  ↓
Quality acceptable?
  │
  ├── Yes ─────────► Final Result
  │
  └── No
       ↓
    Feedback
       ↓
    Optimizer
       ↓
    Improved Candidate
       └──────────────► Evaluator
```

This introduces the next engineering question:

> How can model-generated output be evaluated against explicit criteria and improved without creating an uncontrolled agent loop?

That becomes **Workflow Pattern 04 — Evaluator–Optimizer**.