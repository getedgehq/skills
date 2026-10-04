# Evidence and source handling

Every externally factual claim needs a source. Every displayed output needs an origin label in the project manifest. Use `original_demo`, `creator_showcase`, `actual_run`, `workflow_visualization`, `reference_only` or `missing`.

A rendered chat is not an actual screenshot. Do not simulate loading timers, rankings, scan verdicts or success checks as observed facts. Label a visualized workflow prominently enough to read at feed size. Keep an explicit tool or skill name in the prompt when it was in the real recording.

For an actual-run cut, retain exact prompt, model/client where known, skill ID/version, tool history, outputs, human interventions, source and destination. A developer's pasted claims ledger is a locator, not independent inspection of the footage.

Do not splice separate runs into one causally continuous run. Creator demos may be attributed showcases but cannot be the result of an invented new run. An open-source skill's license does not automatically cover a separately hosted creator video, artwork, voice, portrait or music.

A creator's own post can establish that they released something. An unrelated community discussion does not prove where it was discovered or that your product ingested that thread. Avoid source-to-ingestion animations without ingestion evidence. Use "published expertise" rather than implying a particular ingestion event.

The current starter has an original procedural 3D motion study and a labeled workflow visualization. It does not establish an agent run, a tool invocation, automatic discovery, or comparative improvement. Replace these sections with same-run evidence for a recording-based launch.

Do not send private prompts to search/ranking services or install MCP servers as part of packaging. Request permission before external config/account changes or nontrivial paid services.

For an explicitly approved creator/concept showcase, set claim_mode to showcase and publication_approval to non_evidence_showcase in brief.json. Only do this after the user approves that scope. Retain accurate labels and rights. Never use this switch to evade evidence requirements for a recorded-run claim. The default is recorded_run.
