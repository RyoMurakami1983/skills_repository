# Response Index Template

> **Instructions**: Copy this file to your project's `.github/skills/<your-domain>/references/response-index.md` and fill in each section. Replace all `[placeholder]` text with your actual information. Add entries to the Response History table as you complete each inquiry response.

---

## §1 Inquiry Classification Taxonomy

Define the types of inquiries your domain receives. Each type should represent a recurring pattern (3+ occurrences to justify a type).

| Type ID | Name (EN) | Name (JA) | Description | Typical Source | Complexity |
|---------|-----------|-----------|-------------|----------------|------------|
| [TYPE-1] | [External Audit] | [外部監査] | [Formal audit by certification body or customer] | [Certification body] | High |
| [TYPE-2] | [Compliance Survey] | [コンプライアンス調査] | [Questionnaire about regulatory compliance] | [Customer quality dept] | Medium |
| [TYPE-3] | [Confirmation Request] | [確認要求] | [Simple confirmation of status or capability] | [Various] | Low |

> Add types as new patterns emerge. Remove types that haven't been used in 2+ years.

---

## §2 Response History

Record every inquiry response chronologically. This is the core asset of the evidence-response system.

### [Current Year]

| Year-Month | Sender | Type | Folder/Location | Main File | Question Summary |
|-----------|--------|------|-----------------|-----------|-----------------|
| [YYYY-MM] | [Organization name] | [TYPE-ID] | [Folder path] | [Filename] | [Brief summary of questions] |

### [Previous Year]

| Year-Month | Sender | Type | Folder/Location | Main File | Question Summary |
|-----------|--------|------|-----------------|-----------|-----------------|
| | | | | | |

> **Recording rule**: Add a new row immediately after completing each response. Include enough detail in "Question Summary" to find this entry when searching for similar questions.

---

## §3 Statistics Summary

Update these statistics during annual freshness reviews.

| Metric | Value |
|--------|-------|
| Total responses recorded | [N] |
| Unique senders | [N] |
| Most frequent type | [TYPE-ID] ([N] responses) |
| Most frequent sender | [Organization] ([N] responses) |
| Oldest response | [YYYY-MM] |
| Newest response | [YYYY-MM] |
| Coverage period | [N] years |

---

## §4 Repeat Sender Map

Track organizations that send inquiries multiple times. Consistency across responses to the same sender is critical.

| Sender | Response count | Years active | Types received | Consistency notes |
|--------|---------------|-------------|----------------|-------------------|
| [Organization A] | [N] | [YYYY–YYYY] | [TYPE-1, TYPE-2] | [Any consistency concerns] |
| [Organization B] | [N] | [YYYY–YYYY] | [TYPE-2] | |

> **Why track repeat senders**: If the same organization asks similar questions across years, your answers must be consistent. Use this map to find and cross-reference past responses.

---

## §5 How to Add a New Response

Follow these steps after completing each inquiry response:

1. **Add a row** to §2 Response History under the current year
2. **Fill in all columns** — sender, type, location, filename, question summary
3. **Update §3 Statistics** if this is a new sender or a milestone entry
4. **Update §4 Repeat Sender Map** if this sender has responded before
5. **Commit the change** to git with a message like: `docs: add [sender] [type] response [YYYY-MM]`

### How to Expand the Taxonomy

If a new inquiry doesn't fit any existing type:

1. Check if this is truly a new pattern (has it occurred 3+ times?)
2. If yes, add a new row to §1 Taxonomy with a descriptive Type ID
3. Update the classification decision flow in the main SKILL.md
4. Reclassify any past responses that fit the new type

---

## §6 Maintenance Log

| Date | Reviewer | Changes made |
|------|----------|-------------|
| [YYYY-MM-DD] | [Name/Role] | Initial creation |
| | | |
