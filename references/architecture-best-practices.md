# Architecture Best Practices

Synthesized from the two local PDFs and the 42 Coffee Cups article: https://www.42coffeecups.com/blog/software-architecture-best-practices

## Practical Heuristics

- Start with separation of concerns; enforce it with imports, package boundaries, or tests.
- Prefer modular monoliths until distribution has a measurable payoff; design boundaries so the system can move toward deployable units or services later.
- Use DDD/bounded contexts to find boundaries, not to justify premature services.
- Make APIs explicit before crossing process or repo boundaries.
- Keep business policy independent from UI, database, framework, and transport details.
- Design for observability when work crosses async, service, or deployment boundaries.
- Treat scalability as a workload question: scale the pressured path, not the whole system.
- Choose cloud-native features when they simplify operations, not because they are fashionable.
- Treat public APIs, event contracts, environment variables, database schemas, and shared packages as architecture surfaces.
- Enforce chosen architecture with compilers, module systems, dependency checks, generated diagrams, and CI. Human discipline alone is fragile.
- Use partial boundaries when the future pressure is plausible but a full boundary is premature.
- Keep startup/composition code dirty and low-level so policy code stays clean.

## Review Questions

- What changes together?
- What must fail independently?
- What must scale independently?
- What owns the data and invariants?
- What can be tested without details?
- Which imports point the wrong way?
- Where are hidden contracts: events, env vars, schemas, payload tags, shared constants?
- What would break if this module became a separately deployed process?
- Which boundary mode is actually needed: source, package, deployable component, local process, or service?
- Are layers doing useful work, or are they mostly pass-through?
- Is a service boundary architecturally significant, or only an expensive function call?
- Are framework/database/web objects crossing into use cases or entities?
- Are modules using language visibility to hide internals, or is everything effectively public?

## Red Flags

- controllers contain policy
- domain imports infrastructure
- services share database tables without ownership
- event payloads are undocumented
- one helper module imports everything
- many modules depend on framework globals
- tests require full production wiring for simple business rules
- diagrams exist but regeneration commands do not
- layered architecture has no stated open/closed layer policy
- event processors require atomic transactions across multiple handlers
- microservices require routine orchestration from the UI/API layer
- plugin modules import each other or core internals
- ports-and-adapters infrastructure can call other infrastructure without going through the domain
- ORM rows, web requests, SDK objects, or queue payloads appear in policy code

## Source-Derived Corrections

- Layered architecture is not just "UI/business/data." Its value depends on isolation and explicit request-flow rules; otherwise it becomes a sinkhole.
- Event-driven architecture is not just "async." Mediator and broker topologies solve different workflow-shape problems.
- Microkernel architecture depends on a stable minimal core, registry/discovery, contracts, and versioning.
- Microservices should reduce accidental complexity compared with heavyweight SOA; if service orchestration dominates, the granularity is likely wrong.
- Space-based architecture is an extreme-load pattern centered on processing units, in-memory data grids, and virtualized middleware, not a generic cloud pattern.
- Clean architecture is a dependency and boundary discipline. It does not require every app to implement every ring, and it explicitly allows partial boundaries where full boundaries cost too much.
