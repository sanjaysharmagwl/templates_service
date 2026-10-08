# Working with AI coding agents

AI agents can do any step in [the workflow](workflow.md). This page sets out
what that changes and what it does not.

## The principle

**The repository is the source of truth, not the tool.** Everything an agent
needs to do good work here is a plain file that a person needs too: specs,
glossary, architecture rules, standards, and one command that checks the
result. The files written only for agents are a short `AGENTS.md` and the
runbooks in `.agents/skills/`, and a person can follow those as well.

This has two consequences:

- Switching to a different AI tool or model changes nothing in the repository.
- If no AI tool is available, the team keeps working the same way.

## What does not change

- **Accountability.** The engineer who opens a pull request answers for every
  line in it. "The agent wrote it" is not an explanation.
- **The gate.** `make check` and human review apply to every change equally.
- **Decisions.** What the business wants, and whether a spec is right, is
  decided by people. Agents draft; people approve.

## Rules for using agents

1. **Give the agent a spec, not a wish.** Agents fill gaps in instructions
   with plausible guesses. Ask for a draft spec first, review it, and only
   then ask for code against the approved spec.
2. **One task at a time.** Keep each change to one task from the plan. Large
   generated changes do not get reviewed properly, by anyone.
3. **Never paste secrets or customer data into a prompt.** No credentials, no
   production records, no personal or account data. Use invented data.
4. **Agents work on branches.** They do not push to the main branch, do not
   hold production credentials, and do not run against production systems.
5. **Tests and specs are protected.** An agent must not edit a test or an
   acceptance criterion to make a check pass. Review any change to an existing
   test with extra care.
6. **Read what you merge.** If you cannot explain a piece of generated code,
   it is not ready. Ask for a simpler version or write it yourself.
7. **Treat legacy analysis as a draft.** An agent's description of what old
   code does is a starting point for a domain owner's review, not a fact.

## Signs that generated code needs another pass

- Code the spec did not ask for: extra options, endpoints, fallbacks.
- Layers of abstraction with a single use.
- Comments that narrate the code, or that address the reader of a chat.
- Errors that are caught and ignored, or defaults that hide a missing value.
- Tests that assert a mock was called instead of what happened.
- Tests that cannot fail.

The standard is in [coding-standards.md](coding-standards.md): code a new team
member can read and change without help.

## Tool setup

| File | Read by |
|---|---|
| `AGENTS.md` | Most coding agents, natively. Check your tool's documentation. |
| `CLAUDE.md` | Claude Code. One line that imports `AGENTS.md`. |
| `.agents/skills/` | Tools that support the Agent Skills format. `AGENTS.md` also lists each runbook by path for tools that do not. |

Some tools only discover skills in their own folder. `make agent-links` links
those folders to `.agents/skills/`, so there is still one copy to maintain. To
support another tool, add its folder to `scripts/link_agent_skills.py`, or add
a one-line file that points to `AGENTS.md`. Do not copy instructions into
tool-specific files: copies drift apart.

Keep `AGENTS.md` short. It is loaded into every agent session, and agents
follow a short, specific file more reliably than a long one. Detail belongs in
`docs/` and in the runbooks, which are read when needed.

## Keeping the process independent of AI

Once a quarter, build one small feature with no AI assistance, following
[workflow.md](workflow.md) as written. If a step is unclear or a document is
out of date, fix it. This is the test that the knowledge is in the repository
and not in a tool's memory or one person's prompts.
