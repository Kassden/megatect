# Pattern Fit Rubric

Use this after inventory and graph evidence.

## Modular Monolith

Choose when:
- one product or tight product family
- one team or tightly coordinated teams
- direct calls are adequate
- boundaries are still being discovered
- the system may later need deployable units or services, but current evidence does not justify distribution

Require:
- public module entrypoints
- dependency rules
- acyclic system graph
- tests around use cases
- compiler/import/static enforcement where the language and tooling allow it

Prefer package-by-component when:
- a feature/business capability can expose one narrow entrypoint
- internal persistence and business logic should be hidden from other components
- the monolith is a possible stepping stone to future services

## Layered

Choose when:
- workflow is mostly request/response
- presentation, application, domain, persistence split is natural
- simplicity matters more than plugin/event flexibility

Require:
- explicit closed/open layer policy
- a rule for whether controllers may reach repositories
- a sinkhole check: how many requests pass through layers without useful work

Reject when layers become pass-through ceremony, bypasses are accidental, or domain logic leaks outward.

## Clean Architecture / Ports and Adapters

Choose when:
- business rules must outlive delivery mechanisms
- testability without framework/database is important
- external integrations vary

Require:
- inward source dependencies
- boundary-owned request/response models
- composition root kept in main/startup code
- adapters for database, web, queues, SDKs, and framework details

Reject when the app is tiny and adapters would only add ceremony. Use partial boundaries instead when a full boundary is plausible but not yet worth its cost.

## Event-Driven

Choose when:
- async decoupling is core
- fan-out workflows exist
- consumers should evolve independently

Require:
- idempotency
- replay/error strategy
- event ownership
- observability
- event contract format and versioning
- mediator versus broker topology decision

Prefer mediator when workflow orchestration is real. Prefer broker when the chain can be decentralized and no central coordinator is needed.

Reject when a single business transaction must be atomic across processors or when tracing/recovery cannot be made reliable.

## Microkernel

Choose when:
- stable core plus plugins/extensions is the product shape
- third-party or user-defined extensions matter

Require:
- minimal core
- plugin registry/discovery
- stable plugin APIs
- compatibility and contract versioning policy
- low plugin-to-plugin coupling

## Microservices

Choose only with evidence:
- independent scaling
- independent failure isolation
- data/security isolation
- separate ownership/release cadence
- stable API boundaries

Require:
- coarse business-capability boundaries
- contract tests and versioning
- deployment automation
- production observability
- resilience design for network failures
- data ownership story

Reject by default for small teams, unclear boundaries, shared transactions, weak ops, or frequent service orchestration from UI/API layers.

## Space-Based

Choose only for extreme concurrency or throughput where central persistence is the bottleneck and operational maturity exists.

Require:
- active data can fit and replicate in memory
- processing-unit partitioning makes sense
- request routing, data-grid replication, optional processing-grid coordination, and deployment management are available
- asynchronous persistence is acceptable for the workload

Reject when a conventional database-backed architecture can meet the load, when consistency must be simple and strict, or when most data is large inactive operational history.

## Boundary Escalation Ladder

When choosing a pattern, escalate boundary strength only as evidence requires:

1. Naming/folders and tests.
2. Package/module visibility and import rules.
3. Source-level ports and adapters.
4. Independently releasable/deployable components.
5. Local processes.
6. Network services.

At each step, state the force that justifies the added cost.
