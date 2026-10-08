# Testing strategy

Tests are how we know the service does what the spec says. They are also what
makes it safe to let anyone, human or AI, change the code: a change that keeps
every test passing has, by definition, kept every specified behaviour.

## Kinds of test

| Folder | Checks | Goes through | Speed |
|---|---|---|---|
| `tests/unit/` | One rule or one object | Python calls, in-memory adapters | Milliseconds |
| `tests/acceptance/` | One acceptance criterion, end to end | HTTP, in-memory adapters | Fast |
| `tests/contract/` | The API matches `contracts/openapi.json` | HTTP | Seconds |
| `tests/characterization/` | The new service matches recorded legacy behaviour | HTTP | Fast |
| `tests/integration/` (add when needed) | A real adapter against the real thing | A real database or service | Slower |

`make test` runs all of them.

### Unit tests

Most tests are unit tests of domain objects. They need no setup beyond
constructing the object, so they are the cheapest place to cover every branch
of a rule. Use cases are tested with in-memory adapters, not mocks: the test
then checks what was stored, not which methods were called.

### Property-based tests

For any rule of the form "this must hold whatever happens", add a
property-based test with Hypothesis alongside the examples. The test generates
hundreds of input sequences and checks the invariant after each step. Rules
about totals, limits, ordering and idempotency are the usual candidates. See
`tests/unit/test_payment_properties.py`.

On a developer machine each run uses new random inputs. In CI, Hypothesis
detects the environment and uses a fixed set, so a pull request does not fail
because of an unrelated random discovery. When a run fails, Hypothesis prints
the smallest failing input; add it as an ordinary example test so it stays
covered.

### Acceptance tests

One file per spec, named `test_NNNN_<spec name>.py`, with at least one test per
acceptance criterion. They use the service the way a client does, over HTTP,
and assert on the response and on what was stored. Read side by side with the
spec, they should look like the same document in two languages.

### Contract tests

Three things protect the API contract:

1. **Snapshot.** `test_openapi_snapshot.py` fails if the code serves a
   different contract than the committed `contracts/openapi.json`. A contract
   change is therefore always a visible diff in review.
2. **Conformance.** `test_api_conformance.py` uses Schemathesis to send
   generated requests, valid and invalid, and checks that every response has a
   documented status, content type and body shape, and that nothing returns a
   server error.
3. **Compatibility.** CI compares the contract with the target branch using
   oasdiff and fails on a breaking change.

When this service starts calling other services, or other teams depend on it,
consider consumer-driven contract tests (Pact) between the pairs. They are not
needed for a single service.

### Characterization tests

Used when rewriting an existing system: recorded legacy requests and responses
are replayed against the new service. See [docs/legacy/](../legacy/README.md).
Delete the folder if nothing is being rewritten.

### Integration tests

The template has none because it has no real adapters. Add
`tests/integration/` with the first database adapter, and run the adapter
against a real database started for the test. Run the same repository tests
against the in-memory and the real adapter, so the in-memory one stays an
honest stand-in.

## Conventions

- **Name tests as sentences** about behaviour:
  `test_refund_larger_than_the_refundable_amount_is_rejected`.
- **Arrange, act, assert**, separated by blank lines. One behaviour per test.
- **Assert on outcomes**, not on calls. Avoid mocks of our own code.
- **Assert that rejections change nothing.** A test for a refused request
  also checks that no data was written.
- **No real data.** Fixtures are invented. Never copy production records
  into the repository.
- **Fixed time and identifiers.** Inject the clock and id generator.
- **Link tests to criteria** with `@pytest.mark.covers("NNNN:AC-n")`.

## Coverage

The gate is 90% with branch coverage. It is a floor that catches untested
code, not a target: a criterion without a test is a failure at any percentage,
which is what `make trace` checks.

## A test fails after your change

Assume the test is right. Either the change broke specified behaviour, or the
spec needs to change first. Editing a test so that it passes is only correct
when a person has agreed that the old behaviour was wrong.
