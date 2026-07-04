# Software Architecture Patterns

Derived from the local `Software Architecture Patterns.pdf`. This is an original compact rubric, not a copy of the book.

## Layered Architecture

Best fit:
- conventional business apps
- clear presentation, application, domain, and persistence concerns
- teams that need simple onboarding and predictable flow
- request/response systems where adjacent-layer communication is easy to explain and enforce

Use deliberately:
- Decide which layers are closed and which are open. Closed layers preserve isolation by forcing requests through the layer below. Open layers are explicit bypass points for cases where a layer would add no value.
- Treat layers as an isolation mechanism, not as folder names. The point is to keep changes in UI, business rules, services, or persistence from cascading through the system.
- If most requests simply pass through layer after layer, the architecture is paying ceremony without gaining isolation.

Watch for:
- domain logic leaking into controllers or views
- persistence models becoming the domain model
- layers bypassed for convenience
- too many layers for a small app
- the architecture sinkhole anti-pattern: pass-through layers with little transformation, policy, validation, or orchestration
- relaxed layering where controllers reach repositories directly without an explicit rule allowing it

## Event-Driven Architecture

Best fit:
- asynchronous workflows
- independent producers and consumers
- integration-heavy systems
- audit trails, notifications, pipelines, ingestion, or reactive operations

Watch for:
- unclear event ownership
- hidden coupling through event payloads
- weak idempotency and replay strategy
- no observability for event flow

Mediator topology:
- Use when one initiating event has multiple steps and needs workflow knowledge.
- The mediator should know the process steps, not own the business logic for each step.
- Event processors should remain single-purpose and should not rely on other processors to finish their own task.

Broker topology:
- Use when the flow can be a decentralized chain of event processors publishing follow-on events.
- Prefer it for simpler event flows where no central orchestration is needed.
- Expect event chains to evolve; some events may have no current consumer.

Hard checks:
- Define event contracts, formats, and versioning before consumers proliferate.
- Avoid this pattern when one business transaction must be atomic across multiple processors.
- Engineer broker/mediator failure handling, reconnection, poison events, replay, and tracing as part of the architecture, not as operations cleanup later.

## Microkernel Architecture

Best fit:
- stable core with variable plugins
- product platforms with optional extensions
- systems where custom behavior should not modify the core
- internally versioned business applications that behave like products with optional or customer-specific features

Watch for:
- plugin API instability
- plugins importing core internals
- versioning and compatibility drift
- plugin-to-plugin coupling that turns extensions into a second core

Design rules:
- Keep the core minimal: only what is needed to run the product and coordinate extensions.
- Maintain a plugin registry or equivalent discovery mechanism with names, contracts, formats, and connection details.
- Prefer adapters when third-party plugins cannot conform to the standard contract.
- Create the plugin contract versioning strategy at the start; retrofitting it later is expensive.

## Microservices Architecture

Best fit only when at least one pressure is real:
- independent scaling
- independent failure isolation
- independent release cadence
- separate ownership
- security/data isolation
- multiple products consuming a stable API

Avoid when:
- boundaries are not yet known
- team is small
- transactions span services frequently
- observability, deployment, testing, and contract discipline are weak
- services require UI/API-level orchestration to complete ordinary use cases
- service components are so fine-grained that the system becomes heavyweight SOA under a smaller name

Design rules:
- Service components should be coarse enough to own a meaningful business capability.
- Avoid direct service-to-service orchestration where possible; repeated orchestration is evidence that the boundary or granularity is wrong.
- Shared functionality should be duplicated only when it is genuinely small and stable; otherwise extract a consciously governed shared component.
- A shared database can reduce service chatter, but it weakens data ownership and must be justified by the system context.
- Distributed service calls bring contract governance, latency, deployment, test, and failure-mode costs. Count those costs before recommending the pattern.

Default: choose modular monolith, package-by-component, or multiple deployable processes first unless distribution is forced by evidence.

## Space-Based Architecture

Best fit:
- extreme scale or bursty load
- state can be partitioned or held in distributed memory/grid structures
- avoiding central database bottlenecks is the primary design driver
- high-volume systems with unpredictable concurrent load where ordinary web/app/database scaling just moves the bottleneck downward

Avoid when:
- ordinary web scale is enough
- operational maturity is limited
- consistency requirements are strict and simple persistence would work
- the data set is large, relational, and mostly operational rather than active/volatile

Design rules:
- Processing units package application logic with an in-memory data grid and optional async persistence.
- Virtualized middleware is not decoration; it usually includes request routing, data replication, distributed processing coordination, and deployment management.
- Partition active volatile data away from inactive data to keep the memory footprint realistic.
- A backing store is often still present for initial loading and asynchronous persistence; the point is to remove it from the synchronous request bottleneck.

## Pattern Selection Rules

- Choose the simplest pattern that preserves changeability. Distribution is a cost, not a virtue.
- Prefer explicit source/package boundaries before process or network boundaries.
- If a pattern’s primary benefit is not tied to a real force in the repo, reject it for now and document the condition that would change the decision.
