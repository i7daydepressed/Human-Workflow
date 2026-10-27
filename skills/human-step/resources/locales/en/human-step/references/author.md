# Author a readable step packet

## Recipient and scope

Establish whether a person, agent, or both will execute. For a person, provide actions in an available editor/UI; for an agent, add commands and tool limits when needed. Keep one main text understandable to both. Do not depend on the old chat, hidden REPL state, or an unpublished temporary file.

Confirm that preparing instructions was assigned. Describing “connect the device first” does not authorize connecting it, changing configuration, or starting a procedure. Establish the preparation/execution boundary.

For small tasks, use a short packet or answer rather than a mandatory file hierarchy. When the user requests an understanding exercise, do not give the complete solution instead.

## Basis

1. Establish purpose, requirement source, and needed outcome.
2. Read necessary sources from an agreed revision. Do not substitute a generic example for the actual assignment.
3. Separate requirements, chosen implementation, and the author's proposal. Resolve materially ambiguous terms before dependent actions; continue independent work.
4. Record actual paths, states, and access limits. Without a local snapshot, identify the basis for checked blocks: remote commit, earlier packet, or attached file. Do not describe assumed state as inspected.

## Header

Use shared/templates/en/human-step-packet.md as a guide, not a mandatory questionnaire. Include purpose, recipient, starting state, assignment/specification, dependencies, and scope. Mark missing fields honestly or omit irrelevant ones.

For ongoing work, link the actual specification/methodical guide and revision. Do not conflate assignment number, specification revision, app version, and source SHA. Map requirements to steps in a compact table if useful.

State what is actionable now, material exclusions, and changes that invalidate the packet. Do not include commit/push, publication, or future stages by default without authorization.

## Step

Provide one coherent action block with a checkable boundary. Name object, starting condition, and exact action. For replacement, include enough old text and the full replacement. For manual work, specify location, control, entered value, or confirmed connection.

Explain mechanism and observable outcome so the person understands what changes and why. One sentence is enough when it conveys this; do not add paragraphs for form's sake.

Include a concrete success check. If waiting is required, use a sourced time/event or an honest observation limit; never invent a delay. For mismatch, give the next safe diagnostic action within authorized scope.

Respect dependencies. Do not demand intermediate compilation when several edits intentionally complete one dependency. Identify the combined build/check point.

## Handoff

Ensure required files/materials are accessible to the recipient. Across environments, transfer necessary bytes or valid links; a cloud URL does not mean a folder is mounted locally.

Save the exact packet and revision. Use portable relative links for illustrations/local materials where supported and verify files exist. For large sources, a pinned link/version may suffice; state that bytes are not included.

Separate completed preparation from future execution: inspected sources/anchors, calculations, actual runs, recipient checks, and remaining human work. Completing one packet does not establish the entire task is ready.
