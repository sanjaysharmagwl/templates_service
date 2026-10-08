"""Service template: a spec-driven FastAPI backend service.

Layers, from the inside out (see docs/architecture/overview.md):

    domain       business rules; plain Python, no framework imports
    application  use cases and the ports they need
    adapters     implementations of ports (databases, clocks, other services)
    api          HTTP: routes, request/response schemas, error mapping
    main         composition root that wires the layers together
"""
