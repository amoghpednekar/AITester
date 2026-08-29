# Test Cases — AI-Powered PRD Reviewer (pmprompt.com)

> **Source:** PRD Example - AI PRD Reviewer.pdf (dated 1/6/2025)
> **Rule Base:** Antihallucination.rules.md
> **Unresolved PRD details resolved by Product/Test Owner:**
> - Grading scale: **0–100**; default component weighting: **10**
> - Feedback report export format: **PDF**
> - Cloud provider: **AWS**
> - Error message behavior: generic in nature (no specific codes defined)
> - Language: **English only**
> - 100-concurrent-user load profile: out of scope for this round

---

## 1. Verified Facts (traceable to PRD)

1. Users upload **or** paste a PRD; tool analyzes and grades the content.
2. File upload supports **.docx, .pdf, .txt**. Text paste is supported.
3. Parsing handles headings, bullet points, and other structural elements.
4. Grades are shown as a summarized report across categories including **Clarity, Completeness, Coherence**.
5. Structural Analysis checks for goals, scope, requirements, success metrics.
6. Completeness Score is based on presence of user personas, success metrics, risk assessments.
7. Grading rubric is customizable by admins or advanced users (weighting).
8. Section-level feedback/suggestions are provided (e.g., "Add user personas", "Clarify success metrics").
9. Best Practices Library allows browsing relevant examples for flagged issues.
10. Versioning: document history tracked; side-by-side comparisons supported.
11. Collaboration: share annotated PRD feedback; share a link; export the feedback report.
12. Third-party integrations (Confluence, Jira, Notion) are **Future scope**, not in MVP.
13. Response time under 10 seconds for documents < 10 pages; target 99.9% uptime.
14. Security: HTTPS, encrypted storage, GDPR/CCPA compliance; content fully deletable on request.
15. Privacy: option to remove content after analysis OR keep it anonymized for model improvement **with explicit user consent**.
16. Documents require some structure (headers, bullet points) for **optimal** analysis.
17. Initial language support: **English only**. Multi-language is future scope.
18. User flow: Login/Access → Upload or Paste → Review & Analysis → Feedback → Edit & Iterate → Export/Share.
19. Acceptance criteria: at least **three (3) actionable suggestions** per PRD upload.
20. Timeline: MVP (M1–2) = upload/paste + core grading + feedback summary; Beta (M3–4) = section feedback, multiple formats, collaboration; Full Release (M5–6) = versioning, advanced analytics, GDPR/CCPA.

## 2. Missing / Unknown Information (resolved or out of scope)

- Grading scale resolved to **0–100**; default weighting **10** (Product/TM).
- Export format resolved to **PDF** (Product/TM).
- Provider resolved to **AWS** (Engineering).
- Error messages are generic; no specific codes — no fixed XML/format asserted.
- Login/auth specifics and file size limits remain **Insufficient information to determine** (no constraints set).
- 100-concurrent-user load profile: **skipped for this round**; concurrency acceptance retained from PRD §12.3 only.
- Section-level insight wording kept generic (not exhaustively enumerated).

---

## 3. Test Case Matrix

| TC ID | Module | Title | Priority | Traceability |
|-------|--------|-------|----------|--------------|
| TC-001 | Upload & Parsing | Valid .docx upload | P1 | §4.1, §6.2 |
| TC-002 | Upload & Parsing | Valid .pdf upload | P1 | §4.1, §6.2 |
| TC-003 | Upload & Parsing | Valid .txt upload | P1 | §4.1, §6.2 |
| TC-004 | Upload & Parsing | Unsupported file format | P2 | §4.1 |
| TC-005 | Upload & Parsing | Paste PRD text | P1 | §4.1, §6.2 |
| TC-006 | Upload & Parsing | Parsing of headings and bullets | P1 | §4.1 |
| TC-007 | Upload & Parsing | Unstructured document handling | P2 | §8 |
| TC-008 | Analysis & Grading | Grade report categories shown | P1 | §4.3 |
| TC-009 | Analysis & Grading | Structural analysis sections | P1 | §4.2 |
| TC-010 | Analysis & Grading | Completeness score basis | P1 | §4.2 |
| TC-011 | Analysis & Grading | Default rubric weight = 10 | P1 | §4.2 + TM |
| TC-012 | Analysis & Grading | Score range 0–100 | P1 | §4.2 + TM |
| TC-013 | Analysis & Grading | Customizable rubric weighting | P2 | §4.2 |
| TC-014 | Feedback | Minimum 3 actionable suggestions | P1 | §12.1 |
| TC-015 | Feedback | Section-level suggestions | P1 | §4.3 |
| TC-016 | Feedback | Export report as PDF | P1 | §6.6 + TM |
| TC-017 | Collaboration | Share annotated feedback with team | P2 | §4.5, §6.6 |
| TC-018 | Collaboration | Share link with collaborators | P2 | §6.6 |
| TC-019 | Versioning | Document history tracked | P3 | §4.4, §10 |
| TC-020 | Versioning | Side-by-side comparison | P3 | §4.4, §10 |
| TC-021 | Performance | Response < 10s for < 10 pages | P1 | §5.2, §12.3 |
| TC-022 | Security | HTTPS data transmission | P1 | §5.3, §12.4 |
| TC-023 | Security | Encrypted storage (AWS) | P1 | §5.3 + Eng |
| TC-024 | Privacy | Delete user content on request | P1 | §5.3, §12.4 |
| TC-025 | Privacy | Consent for anonymized model use | P1 | §5.3 |
| TC-026 | Language | English language support | P1 | §8 |
| TC-027 | Language | Non-English content behavior | P2 | §8 |
| TC-028 | Roadmap | Feature gating by milestone | P2 | §10 |

---

## 4. Detailed Test Cases

### TC-001 — Valid .docx upload
- **Priority:** P1 | **Module:** Upload & Parsing
- **Description:** Verify a user can upload a valid PRD in .docx format and receive analysis.
- **Preconditions:** User is logged into pmprompt.com and has the AI-based PRD Reviewer open (§6.1–6.2).
- **Test Steps:**
  1. Select the upload option.
  2. Choose a well-structured .docx PRD.
  3. Confirm the upload completes.
  4. Trigger/confirm analysis.
- **Expected Results:**
  1. Upload is accepted (.docx supported, §4.1).
  2. A grade and feedback report are received (§12.1).
- **Notes:** Document under 10 pages to fall within response-time scope (see TC-021).

### TC-002 — Valid .pdf upload
- **Priority:** P1 | **Module:** Upload & Parsing
- **Description:** Verify a user can upload a valid PRD in .pdf format.
- **Preconditions:** User is logged in; tool is open.
- **Test Steps:**
  1. Select the upload option.
  2. Choose a well-structured .pdf PRD.
  3. Confirm upload and analysis.
- **Expected Results:**
  1. Upload accepted (.pdf supported, §4.1).
  2. Analysis runs and feedback is returned (§6.3–6.4).

### TC-003 — Valid .txt upload
- **Priority:** P1 | **Module:** Upload & Parsing
- **Description:** Verify a user can upload a valid PRD in .txt format.
- **Preconditions:** User is logged in; tool is open.
- **Test Steps:**
  1. Select the upload option.
  2. Choose a well-structured .txt PRD.
  3. Confirm upload and analysis.
- **Expected Results:**
  1. Upload accepted (.txt supported, §4.1).
  2. Analysis runs and feedback is returned (§6.3–6.4).

### TC-004 — Unsupported file format
- **Priority:** P2 | **Module:** Upload & Parsing
- **Description:** Verify behavior for a format not listed as supported.
- **Preconditions:** Tool is open; a non-.docx/.pdf/.txt file available.
- **Test Steps:**
  1. Attempt to upload a format not in §4.1 (e.g., .xls).
- **Expected Results:**
  1. **Insufficient information to determine** — §4.1 lists only .docx/.pdf/.txt; no rejection behavior is defined. Verify only that no undocumented support is claimed. Error messaging is generic (TM) — do not assert specific wording.

### TC-005 — Paste PRD text
- **Priority:** P1 | **Module:** Upload & Parsing
- **Description:** Verify a user can paste PRD text and run analysis.
- **Preconditions:** User is logged in; tool is open.
- **Test Steps:**
  1. Use the paste/text-editor option (§4.1).
  2. Paste PRD content.
  3. Trigger analysis.
- **Expected Results:**
  1. Pasting is supported (§4.1, §6.2).
  2. Analysis runs and feedback is returned (§6.3–6.4).

### TC-006 — Parsing of headings and bullets
- **Priority:** P1 | **Module:** Upload & Parsing
- **Description:** Verify the tool handles headings and bullet points structurally.
- **Preconditions:** A structured PRD with headings and bullets is available.
- **Test Steps:**
  1. Upload or paste a structured PRD.
  2. Run analysis.
- **Expected Results:**
  1. Structural elements are parsed (§4.1).

### TC-007 — Unstructured document handling
- **Priority:** P2 | **Module:** Upload & Parsing
- **Description:** Verify behavior for documents lacking structure.
- **Preconditions:** A document without headers/bullets is available.
- **Test Steps:**
  1. Upload a minimally structured document.
  2. Run analysis.
- **Expected Results:**
  1. Optimal analysis is not guaranteed without structure (§8) — treat as **Inference (low confidence)** beyond this statement; no exact failure behavior is defined.

### TC-008 — Grade report categories shown
- **Priority:** P1 | **Module:** Analysis & Grading
- **Description:** Verify the report shows scores across categories including Clarity, Completeness, Coherence.
- **Preconditions:** A completed analysis exists.
- **Test Steps:**
  1. Complete an analysis.
  2. Inspect the summarized report.
- **Expected Results:**
  1. Summarized report shows scores across categories, including Clarity, Completeness, Coherence (§4.3).

### TC-009 — Structural analysis sections
- **Priority:** P1 | **Module:** Analysis & Grading
- **Description:** Verify structural analysis checks for essential PRD sections.
- **Preconditions:** A PRD is submitted.
- **Test Steps:**
  1. Run analysis.
  2. Inspect structural-analysis results.
- **Expected Results:**
  1. Tool checks for essential sections; examples: Goals, Scope, Requirements, Success Metrics (§4.2).

### TC-010 — Completeness score basis
- **Priority:** P1 | **Module:** Analysis & Grading
- **Description:** Verify the completeness score reflects presence of standard components.
- **Preconditions:** A PRD is submitted.
- **Test Steps:**
  1. Run analysis.
  2. Inspect the completeness score.
- **Expected Results:**
  1. Completeness score considers presence of user personas, success metrics, risk assessments (§4.2).

### TC-011 — Default rubric weight = 10
- **Priority:** P1 | **Module:** Analysis & Grading
- **Description:** Verify the default grading weight used by the system is 10.
- **Preconditions:** No custom rubric has been configured.
- **Test Steps:**
  1. Run analysis with default settings.
  2. Inspect the rubric/score derivation.
- **Expected Results:**
  1. Default component weighting is **10** (resolved by TM; §4.2 default behavior).

### TC-012 — Score range 0–100
- **Priority:** P1 | **Module:** Analysis & Grading
- **Description:** Verify all reported scores fall within 0–100.
- **Preconditions:** A completed analysis exists.
- **Test Steps:**
  1. Complete an analysis.
  2. Check each category score and the overall grade.
- **Expected Results:**
  1. Scores are on a **0–100** scale (resolved by TM; §4.2 grading).

### TC-013 — Customizable rubric weighting
- **Priority:** P2 | **Module:** Analysis & Grading
- **Description:** Verify admins/advanced users can adjust component weightings.
- **Preconditions:** User has admin/advanced-user access (§4.2 scopes this to those roles).
- **Test Steps:**
  1. Open grading rubric settings.
  2. Adjust weighting for a PRD component.
  3. Observe scoring impact.
- **Expected Results:**
  1. Weighting can be tweaked by admins or advanced users (§4.2).

### TC-014 — Minimum 3 actionable suggestions
- **Priority:** P1 | **Module:** Feedback
- **Description:** Verify every PRD upload produces at least three actionable suggestions.
- **Preconditions:** A PRD has been analyzed.
- **Test Steps:**
  1. Complete analysis.
  2. Count actionable suggestions returned.
- **Expected Results:**
  1. At least three actionable suggestions are returned per upload (§12.1).

### TC-015 — Section-level suggestions
- **Priority:** P1 | **Module:** Feedback
- **Description:** Verify specific section-level improvement suggestions are provided.
- **Preconditions:** A PRD has been analyzed.
- **Test Steps:**
  1. Complete analysis.
  2. Inspect section-level insights.
- **Expected Results:**
  1. Specific per-section suggestions are offered, e.g., "Add user personas", "Clarify success metrics" (§4.3). Keep assertions section-level; wording is not exhaustively enumerated.

### TC-016 — Export report as PDF
- **Priority:** P1 | **Module:** Feedback
- **Description:** Verify the user can export the feedback report as PDF.
- **Preconditions:** A completed report exists.
- **Test Steps:**
  1. Complete analysis.
  2. Use the export option (§6.6).
- **Expected Results:**
  1. Report exports as **PDF** (resolved by TM; §6.6).
  2. A share link option is also available (§6.6).

### TC-017 — Share annotated feedback with team
- **Priority:** P2 | **Module:** Collaboration
- **Description:** Verify annotated PRD feedback can be shared with team members.
- **Preconditions:** A completed annotated analysis exists.
- **Test Steps:**
  1. Complete analysis with annotations.
  2. Use the collaboration/share option.
- **Expected Results:**
  1. Option to share annotated feedback is available (§4.5).
- **Notes:** Full collaboration tooling (permissions, shareable links) scoped to Enhanced Beta (§10 M3–4).

### TC-018 — Share link with collaborators
- **Priority:** P2 | **Module:** Collaboration
- **Description:** Verify a user may share a link with collaborators.
- **Preconditions:** A completed report exists.
- **Test Steps:**
  1. Complete analysis.
  2. Use the share-link option (§6.6).
- **Expected Results:**
  1. User may share a link with collaborators (§6.6).

### TC-019 — Document history tracked
- **Priority:** P3 | **Module:** Versioning & Comparison
- **Description:** Verify versions of uploaded documents are tracked to show progress over time.
- **Preconditions:** Feature available (scoped to Full Release §10).
- **Test Steps:**
  1. Analyze a PRD.
  2. Modify and re-analyze.
  3. Inspect document history.
- **Expected Results:**
  1. Document history tracks versions (§4.4). Available at Full Release (M5–6) per §10.

### TC-020 — Side-by-side comparison
- **Priority:** P3 | **Module:** Versioning & Comparison
- **Description:** Verify older and newer PRD versions can be compared side by side.
- **Preconditions:** At least two versions of a document exist.
- **Test Steps:**
  1. Open an older version alongside a newer one.
- **Expected Results:**
  1. Side-by-side comparison is supported to see improvements (§4.4).

### TC-021 — Response time under 10 seconds
- **Priority:** P1 | **Module:** Performance
- **Description:** Verify response time is under 10 seconds for documents under 10 pages.
- **Preconditions:** A < 10 page PRD is available.
- **Test Steps:**
  1. Submit a < 10 page PRD.
  2. Measure time from submission to feedback display.
- **Expected Results:**
  1. Response time is under 10 seconds (§5.2, §12.3).
- **Notes:** Larger documents must scale gracefully (§5.2); further threshold behavior not defined.

### TC-022 — HTTPS data transmission
- **Priority:** P1 | **Module:** Security
- **Description:** Verify all data transmission occurs over HTTPS.
- **Preconditions:** Deployed environment available.
- **Test Steps:**
  1. Initiate upload/paste and analysis.
  2. Inspect network traffic for transport encryption.
- **Expected Results:**
  1. All data transmission over HTTPS (§5.3, §12.4).

### TC-023 — Encrypted storage (AWS)
- **Priority:** P1 | **Module:** Security
- **Description:** Verify uploaded documents are stored encrypted.
- **Preconditions:** A document has been analyzed and retained; cloud provider is AWS (Engineering).
- **Test Steps:**
  1. Upload and analyze a document.
  2. Inspect storage encryption.
- **Expected Results:**
  1. Storage is encrypted for uploaded documents (§5.3), hosted on **AWS** (Engineering).

### TC-024 — Delete user content on request
- **Priority:** P1 | **Module:** Privacy
- **Description:** Verify user content can be fully deleted upon request.
- **Preconditions:** A document has been submitted.
- **Test Steps:**
  1. Submit a document.
  2. Request deletion.
  3. Attempt to retrieve the content.
- **Expected Results:**
  1. User content fully deletable upon request (§5.3, §12.4).

### TC-025 — Consent for anonymized model use
- **Priority:** P1 | **Module:** Privacy
- **Description:** Verify content is only kept anonymized for model improvement with explicit consent.
- **Preconditions:** A document has been submitted.
- **Test Steps:**
  1. Submit a document.
  2. Observe the retention/consent flow.
- **Expected Results:**
  1. Content may only be kept anonymized with **explicit user consent** (§5.3).
  2. Removal option must be available (§5.3; §8 mitigation "options to delete submissions").

### TC-026 — English language support
- **Priority:** P1 | **Module:** Language
- **Description:** Verify the tool supports English as the primary language.
- **Preconditions:** Tool is open.
- **Test Steps:**
  1. Submit a PRD in English.
- **Expected Results:**
  1. English is supported as the primary language (§8).

### TC-027 — Non-English content behavior
- **Priority:** P2 | **Module:** Language
- **Description:** Verify behavior for non-English PRD content.
- **Preconditions:** A non-English PRD is available.
- **Test Steps:**
  1. Submit a non-English PRD.
- **Expected Results:**
  1. **Insufficient information to determine** — §8 names English only; additional languages *may* be added in future. Behaviour for unsupported languages is not defined.

### TC-028 — Feature gating by milestone
- **Priority:** P2 | **Module:** Roadmap
- **Description:** Verify features are gated according to the release roadmap.
- **Preconditions:** Application build has a known milestone/version.
- **Test Steps:**
  1. Confirm MVP: basic upload/paste, core grading (structure/completeness), feedback summary (§10 M1–2).
  2. For Beta: section-level feedback, multiple formats, collaboration/permissions (§10 M3–4).
  3. For Full Release: versioning/comparison, advanced analytics, GDPR/CCPA (§10 M5–6).
- **Expected Results:**
  1. Features appear only in their scoped milestone (§10).
  2. Confluence/Jira/Notion integrations and multi-language support are **not** expected in MVP — Future scope (§10, §4.5).

---

## 5. Self-Validation Check

1. **Traceability:** Every expected result cites a PRD section (§4.x, §5.x, §6.x, §8, §10, §12.x) or a recorded Product/Engineering resolution. No assertion invents features, error codes, or messages.
2. **Unknowns flagged:** Upload rejection wording (TC-004), non-English behavior (TC-027), granular load profile, and file-size limits remain **Insufficient information to determine** and are not assumed. Section-level insight wording stays generic (TC-015).
3. **Contradiction check:**
   - Third-party integrations kept in Future scope only (TC-028), consistent with §4.5 and §10.
   - Versioning/comparison and collaboration tied to roadmap milestones (TC-017, TC-019), consistent with §10.
   - English-only support respected (TC-026, TC-027), consistent with §8.
   - Performance/acceptance figures (10 s, 100 users, 99.9% uptime, ≥3 suggestions) match §5.2 and §12 exactly. 100-user load profile acknowledged as skipped per Product.
4. **Determinism:** Repeatable steps with attributed expected outputs; no reliance on unverifiable "typical" behavior.