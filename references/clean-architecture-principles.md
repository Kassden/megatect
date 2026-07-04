# Clean Architecture Principles

Derived from the local `Clean Architecture` PDF. This is an original compact rubric, not a copy of the book.

## Goal

Architecture should preserve the ability to change software cheaply. Behavior matters, but structure protects future behavior.

Good architecture keeps options open. It should let a system start simple, then move along the spectrum from source-level modules, to independently deployable units, to services only when development, deployment, operational, or ownership forces justify it.

## Dependency Direction

Source dependencies should point inward toward stable business policy:

- entities and business rules should not depend on frameworks
- use cases should not depend on UI, DB, or web details
- interfaces/adapters translate between policy and details
- frameworks, databases, queues, and web delivery are outer details
- data crossing inward should use boundary-owned structures, not ORM rows, framework request objects, or transport payloads

## SOLID as Architectural Pressure

- SRP: split by reason to change, meaning stakeholder or actor pressure, not noun count.
- OCP: partition code and direct dependencies so high-level policy can be extended without high-impact edits.
- LSP: substitutable contracts matter at architecture scale, especially APIs and plugins.
- ISP: avoid forcing consumers to depend on unused operations or payload fields.
- DIP: high-level policy should own abstractions; details implement them. Keep unavoidable concrete dependencies gathered in low-level composition code.

## Component Principles

- Reuse/release equivalence: reusable units need coherent release boundaries.
- Common closure: group things that change together.
- Common reuse: avoid forcing consumers to depend on unused code.
- Acyclic dependencies: cycles erase independent change.
- Stable dependencies: volatile modules should depend on stable modules, not the reverse.
- Stable abstractions: the most stable parts should expose abstractions, not concrete detail piles.
- Component dependency diagrams are not functional decomposition diagrams; they are change, build, release, and volatility maps.
- Monitor dependency cycles over time. Cycles make unit testing, release isolation, and build reasoning harder.

## Boundaries

Draw boundaries around use cases, policies, volatility, deployment needs, and ownership. A boundary can be source-level, package-level, process-level, or service-level; do not jump to network boundaries unless the force is real.

Boundary modes:
- Source-level: disciplined package/module separation in one process. Fast calls, cheap deployment, but requires enforcement.
- Deployment-level: independently releasable binaries/packages in one or more processes. Adds release/version cost.
- Local process: separate address spaces using sockets, queues, or OS IPC. Adds latency and operational overhead.
- Service-level: network boundary. Slowest and most operationally expensive; use when independent deployment, scale, isolation, or ownership warrants it.

Partial boundaries:
- Full boundaries are costly. Use partial boundaries when a future separation is plausible but not yet proven.
- "Skip the last step" keeps reciprocal interfaces and data structures but deploys together.
- One-dimensional boundaries use an interface/strategy to protect one side, but can degrade through backchannels.
- Facades are the cheapest placeholder and the easiest to erode because clients can retain transitive knowledge of implementation details.
- Revisit partial boundaries as evidence changes; they either harden into real boundaries or decay.

Main component:
- Keep composition roots, dependency injection frameworks, concrete factories, and startup wiring in the lowest-level entrypoint.
- Do not let the DI framework become the application architecture. The main component should assemble details and hand control to policy.

Services:
- Services are not automatically architecture. A service boundary matters only when it separates high-level policy from low-level detail or enforces a real deployment/operational boundary.
- Services can be expensive remote function calls if their internals ignore component structure and the Dependency Rule.
- Design service internals with the same component and boundary discipline used inside a monolith.

## Details Discipline

Treat these as details until evidence says otherwise:

- database
- web framework
- UI delivery
- external service SDKs
- queues and transports
- file systems and devices

Good architecture delays irreversible detail choices and keeps policies testable without production details.

Important nuance:
- The data model can be architecturally significant; the database product and storage mechanism are details.
- Do not pass table rows, ORM entities, framework request objects, or transport DTOs inward as policy objects.
- Web delivery is an IO mechanism, not the purpose of the system.
- Frameworks are tools. Keep them at arm's length through narrow adapters and avoid framework base classes or globals in policy code.

## Testability

Testing is an architecture boundary. Use cases and policies should be testable without booting the full app, browser, database, or network when possible.

Use humble-object splits at hard-to-test boundaries: put behavior in testable presenters, interactors, gateways, mappers, or service listeners; keep the hard-to-test shell thin.

## Code Organization Enforcement

Architecture fails when implementation details erase encapsulation.

- Package by layer is simple but can invite bypasses such as controllers reaching repositories.
- Package by feature improves locality but may expose too much through feature controllers.
- Ports and adapters protects domain policy from delivery and persistence, but the "outside" can become a side road around the domain if infrastructure can call infrastructure freely.
- Package by component hides business and persistence implementation behind a small public component interface; this is often a practical monolith stepping stone toward services.
- Use compiler/module/package visibility, import rules, and static checks to enforce boundaries. Discipline and code review are not enough under delivery pressure.
