---
name: dotnet-ocr-matching-workflow
description: Use when: you need to orchestrate an end-to-end OCR-to-database matching WPF workflow by composing existing skills (secure-config, Oracle, Dify OCR, matching, and comparison UI).
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, wpf, csharp, ddd, ocr, matching, workflow, orchestration]
  invocable: false
---

# Build a Complete OCR Matching System End-to-End

Workflow orchestrator that composes individual skills into a full OCR matching pipeline: DDD project setup, secure configuration, Oracle DB integration, Dify API OCR extraction, weighted field matching, WPF comparison UI, and export — all wired together with dependency injection.

## When to Use This Skill

Use this skill when:
- Composing secure-config, Oracle, Dify OCR, and WPF UI skills into one pipeline
- Bootstrapping a greenfield DDD solution (Domain/Application/Infrastructure/WPF)
- Integrating PDF preview, OCR parameter input, and comparison tabs in one shell
- Wiring dependency injection so layers depend only downward and stay testable
- Adding a user verification gate before exporting matched data (CSV/RPA)
- Onboarding engineers to the dependency order and integration seams

Prerequisites: .NET 8+ SDK, Oracle access, Dify API endpoint, and basic DDD knowledge.

---

## Related Skills

- **`dotnet-wpf-secure-config`** — DPAPI encryption foundation (Step 2)
- **`dotnet-oracle-wpf-integration`** — Oracle DB connection + repository (Step 2)
- **`dotnet-wpf-dify-api-integration`** — Dify API client + SSE streaming (Step 2)
- **`dotnet-wpf-employee-input`** — Employee ID input and storage (Step 3)
- **`dotnet-wpf-pdf-preview`** — PDF upload and WebView2 preview (Step 4)
- **`dotnet-wpf-ocr-parameter-input`** — OCR parameter input tab (Step 5)
- **`dotnet-generic-matching`** — Weighted field matching in Domain layer (Step 6)
- **`dotnet-wpf-comparison-view`** — Side-by-side results comparison UI (Step 7)
- **`tdd-standard-practice`** — Test generated code with Red-Green-Refactor
- **`git-commit-practices`** — Commit each step as an atomic change

---
## Core Principles
1. **Orchestrate, Don't Duplicate** — This skill references other skills; it never re-implements their content (ニュートラル)
2. **Dependency Order** — Apply skills in strict dependency order: foundation → infrastructure → presentation (基礎と型)
3. **Layer Isolation** — Each DDD layer has exactly one allowed dependency direction (基礎と型)
4. **Test Before Integration** — Verify each skill's output independently before wiring layers together (継続は力)
5. **Composition via DI** — All cross-layer wiring goes through the DI container, never direct instantiation (成長の複利)

---
## Quick Execution Checklist
- Create the four-layer solution and verify dependency directions.
- Apply `dotnet-wpf-secure-config` before any skill that stores credentials.
- Apply Oracle and Dify integration skills and run their connection tests.
- Add the PDF preview + OCR input tabs and confirm the PDF renders.
- Implement matching + comparison and confirm users can verify rows.
- Run the end-to-end checklist and only then add export.
- Use the Step 11 checklist to isolate failures before debugging the full pipeline.

Why: This order isolates failures to one layer at a time and reduces debugging cost.

---

## Workflow: Build OCR Matching System

### Step 1 — Set Up DDD Project Structure

Use when creating a new solution or verifying that an existing one follows the four-layer DDD structure.

Create the solution and four projects. Organize the Domain layer by **use-case**, not by technical concern.

```
YourApp/
├── YourApp.Domain/           # Domain Layer (no dependencies)
│   └── YourUseCase/          # Use-case based organization
│       ├── Services/
│       ├── ValueObjects/
│       ├── Specifications/
│       └── Interfaces (IRepository, IExtractor)
├── YourApp.Application/      # Application Layer (depends on Domain)
│   └── UseCases/YourUseCase/
├── YourApp.Infrastructure/   # Infrastructure Layer (implements Domain)
│   ├── Configuration/
│   ├── ExternalApis/         # Dify API etc.
│   ├── Databases/            # Oracle etc.
│   └── FileSystem/
└── YourApp.Presentation.Wpf/ # Presentation Layer (depends on Application)
    ├── ViewModels/
    ├── Views/
    ├── Converters/
    └── Services/
```

Set project references enforcing dependency rules:

```xml
<!-- YourApp.Application.csproj -->
<ProjectReference Include="..\YourApp.Domain\YourApp.Domain.csproj" />

<!-- YourApp.Infrastructure.csproj -->
<ProjectReference Include="..\YourApp.Domain\YourApp.Domain.csproj" />

<!-- YourApp.Presentation.Wpf.csproj -->
<ProjectReference Include="..\YourApp.Application\YourApp.Application.csproj" />
<ProjectReference Include="..\YourApp.Infrastructure\YourApp.Infrastructure.csproj" />
```

**Dependency rules**:
- **Domain** → nothing (pure business logic)
- **Application** → Domain only (use-case orchestration)
- **Infrastructure** → Domain only (implements interfaces)
- **Presentation** → Application + Infrastructure (DI registration only)

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Apply Foundation Skills

Use when setting up the three infrastructure pillars that all later steps depend on.

Apply these existing skills **in this exact order** — each builds on the previous:

| Order | Skill | What It Provides | Layer |
|-------|-------|-----------------|-------|
| 1st | **`dotnet-wpf-secure-config`** | `DpapiEncryptor`, `SecureConfigService`, `AppConfigModel` | Infrastructure |
| 2nd | **`dotnet-oracle-wpf-integration`** | Oracle connection, repository implementation, connection test dialog | Infrastructure |
| 3rd | **`dotnet-wpf-dify-api-integration`** | `DifyApiService`, SSE streaming, API test dialog | Infrastructure |

🆕 **Why this order matters**: Oracle and Dify skills both store credentials via `SecureConfigService`, so secure-config must come first. Oracle and Dify are independent of each other but both depend on the config foundation.

After applying all three, verify with the test dialogs each skill provides:
- ✅ Oracle connection test passes
- ✅ Dify API ping returns a response
- ✅ Config file created at `%LOCALAPPDATA%`

> **Values**: 基礎と型 / 継続は力

### Step 3 — Add Employee ID Configuration

Use when the system needs to identify which user is processing documents.

Apply: **`dotnet-wpf-employee-input`**

Wire into the existing infrastructure:
- Add `EmployeeId` and `EmployeeName` to `AppConfigModel` (from Step 2)
- Store them encrypted via `SecureConfigService` (from Step 2)
- Expose a Settings dialog/menu to edit them (employee-input skill)

Why: Keeping this in secure-config avoids leaking IDs into plain-text settings.

> **Values**: ニュートラル / 継続は力

### Step 4 — Add PDF Upload and Preview

Use when adding the document input interface — the left side of the main window.

Apply: **`dotnet-wpf-pdf-preview`**

Layout integration:
- Left column: PDF upload + WebView2 preview (`dotnet-wpf-pdf-preview`)
- Right column: `TabControl` hosting OCR input (Step 5) and results (Step 7)

The PDF preview skill provides `PdfPreviewService` for the left column. The right column TabControl hosts tabs from Steps 5 and 7.

> **Values**: 基礎と型 / ニュートラル

### Step 5 — Build OCR Parameter Input Tab

Use when creating the first tab in the right column — where users specify OCR parameters and trigger extraction.

Apply: **`dotnet-wpf-ocr-parameter-input`**

🆕 **Ask the user** what classification and selection fields they need. Common examples:

| Field Type | Example | Bound To |
|-----------|---------|----------|
| Category dropdown | "Product Type", "Department" | Database lookup query |
| Free-text input | "Remarks", "Special Instructions" | Dify API prompt parameter |
| Date picker | "Order Date", "Delivery Date" | Filter criteria |

Wire to existing services:
- Connect "Execute OCR" button to `DifyApiService` (from Step 2)
- Pass selected PDF path from `PdfPreviewService` (from Step 4)
- Display progress via `IProgress<(int, string)>` pattern

```csharp
// PSEUDOCODE: wire Execute OCR → Application use case (Step 8)
[RelayCommand]
private Task ExecuteOcrAsync() =>
    _processDocumentUseCase.ExecuteAsync(
        PdfPath,
        SelectedCategory,
        Remarks,
        progress: BuildProgressReporter());
```

> **Values**: 成長の複利 / ニュートラル

### Step 6 — Implement Domain Matching Logic

Use when building the core business logic that compares OCR-extracted data against database records.

Apply: **`dotnet-generic-matching`**

🆕 **Ask the user** what fields to match and their relative importance:

| Question | Example Answer | Maps To |
|----------|---------------|---------|
| What fields identify a record? | "Product name, customer code" | Weight 2.5–3.0 |
| What fields confirm a match? | "Unit price, quantity" | Weight 1.5–2.5 |
| What fields are supplementary? | "Dimensions, remarks" | Weight 0.5–1.5 |

The `dotnet-generic-matching` skill creates these Domain layer components:

```
YourApp.Domain/
└── YourUseCase/
    ├── ValueObjects/
    │   ├── FieldComparison.cs
    │   └── MatchingScore.cs
    ├── Services/
    │   ├── SimilarityCalculator.cs
    │   └── FieldMatchingService<TSource, TCandidate>.cs
    └── Specifications/
        └── HighQualityMatchingSpecification.cs
```

Configure field definitions with user-specified weights (examples):
- `ProductName` → string similarity, weight 3.0
- `UnitPrice` → decimal similarity, weight 2.0 (use `decimal`, not `double`)

```csharp
// PSEUDOCODE: configure fields + weights
var fields = BuildFieldDefinitionsFromUserInput();
var matcher = new FieldMatchingService<ExtractedItem, ReferenceRecord>(fields, successThreshold: 70.0);
```

> **Values**: 基礎と型 / 成長の複利

### Step 7 — Build Results Comparison View

Use when creating the second tab that displays matching results side-by-side.

Apply: **`dotnet-wpf-comparison-view`**

The comparison view receives `MatchingResult<TSource, TCandidate>` from Step 6 and renders:

```
┌─────────────────────────────────────────────────────┐
│  Results Tab                                         │
│  ┌────────┬──────────────┬──────────┬───────┬─────┐ │
│  │ ☐      │ DB Record    │ OCR Data │ Score │ Edit│ │
│  ├────────┼──────────────┼──────────┼───────┼─────┤ │
│  │ ☑      │ Widget A     │ Widget A │ 95.2% │  ✎  │ │
│  │ ☐      │ Gadget B     │ Gadget C │ 67.1% │  ✎  │ │
│  │ ☑      │ Part X       │ Part X   │ 100%  │  ✎  │ │
│  └────────┴──────────────┴──────────┴───────┴─────┘ │
│                                                      │
│  [Export CSV]                                        │
└─────────────────────────────────────────────────────┘
```

Key features provided by the comparison-view skill:
- ✅ Side-by-side comparison of database records vs. OCR-extracted data
- ✅ Editable fields with **score recalculation** on edit
- ✅ Checkbox verification column for user approval
- ✅ Color-coded scores (green ≥ 80%, yellow ≥ 60%, red < 60%)

> **Values**: ニュートラル / 継続は力

### Step 8 — Create Application Use Cases

Use when wiring the full processing pipeline in the Application layer — the glue between Domain and Infrastructure.

Create the use case that orchestrates the entire flow: load reference data → OCR extract → match.

```csharp
// PSEUDOCODE: Application layer orchestrates Infrastructure + Domain
public Task<IReadOnlyList<MatchingResult<ExtractedItem, ReferenceRecord>>> ExecuteAsync(
    string pdfPath,
    string category,
    string remarks,
    IProgress<(int percent, string message)>? progress = null);
```

Why: Putting orchestration in a use case keeps ViewModels UI-only and testable.

🆕 **This use case depends on interfaces, not implementations** — the DI container (Step 9) provides the concrete services.

> **Values**: 基礎と型 / 成長の複利

### Step 9 — Wire DI Container

Use when registering all services from previous steps into the dependency injection container.

Register services in `App.xaml.cs` following the layer order:

```csharp
// PSEUDOCODE: register in the same order as the dependency flow
services.AddSingleton<ISecureConfigService, SecureConfigService>();
services.AddSingleton<IDataRepository, OracleDatabaseRepository>();
services.AddSingleton<IDocumentExtractor, DifyApiService>();
services.AddSingleton(provider => BuildMatchingServiceFromUserFields(provider));
services.AddTransient<ProcessDocumentUseCase>();
services.AddTransient<MainWindowViewModel>();
```

**DI registration order matters for readability**, not runtime — register in the same order as dependency flow:

```
SecureConfigService → OracleRepository → DifyApiService → MatchingService → UseCase → ViewModels
```

> **Values**: 成長の複利 / 基礎と型

### Step 10 — Add Export Functionality (Optional)

Use when adding CSV or RPA export after the user has verified matching results.

Export requires all quality gates to pass before generating output:

```csharp
// PSEUDOCODE: export only after verification + threshold gates
if (!results.All(r => r.IsVerified)) throw new InvalidOperationException("Verify all rows first");
if (!results.All(r => r.Score.OverallPercentage >= 70.0m)) throw new InvalidOperationException("Below threshold");
WriteCsv(results, outputPath); // RFC 4180 escaping
```

✅ Quality checks before export:
- All matching scores ≥ threshold (e.g., 70%)
- All user checkboxes verified
- RFC 4180 CSV field escaping (commas, quotes, newlines)

> **Values**: 継続は力 / ニュートラル

### Step 11 — Test End-to-End

Use when verifying that all skills are correctly integrated and the full pipeline works.

Run through this test checklist in order:

| # | Test | How to Verify | Depends On |
|---|------|--------------|------------|
| 1 | Oracle connection | Settings → Test Connection button | Step 2 |
| 2 | Dify API connection | Settings → Test API button | Step 2 |
| 3 | Employee ID persistence | Enter ID, restart app, verify restored | Step 3 |
| 4 | PDF upload + preview | Select PDF, verify WebView2 renders | Step 4 |
| 5 | OCR parameter input | Fill fields, click Execute | Step 5 |
| 6 | OCR progress display | Watch progress bar and status text | Steps 5, 8 |
| 7 | Matching results display | Verify side-by-side comparison table | Steps 6, 7 |
| 8 | Editable field recalculation | Edit a field, verify score updates | Step 7 |
| 9 | Checkbox verification | Check all rows, verify Export enables | Step 7 |
| 10 | CSV export | Export and open in Excel | Step 10 |

🆕 **If any test fails**, debug by isolating the layer:
- Infrastructure issue → Check connection strings and API keys in config
- Domain issue → Unit test the matching service with known inputs
- Presentation issue → Verify ViewModel bindings in XAML

> **Values**: 継続は力 / 基礎と型

### Step 12 — Customize for Production

Use when adapting the system for a specific business domain.

| Customization | Where to Change | Skill Reference |
|---------------|----------------|-----------------|
| Add/remove OCR parameters | `OcrProcessTabViewModel` | `dotnet-wpf-ocr-parameter-input` |
| Change matching fields/weights | `FieldDefinition` list in DI | `dotnet-generic-matching` |
| Adjust quality threshold | `FieldMatchingService` constructor | `dotnet-generic-matching` |
| Add new database columns | Repository + Domain model | `dotnet-oracle-wpf-integration` |
| Change Dify workflow ID | `AppConfigModel` + Settings UI | `dotnet-wpf-dify-api-integration` |
| Modify export format | `ExportService` | Step 10 of this skill |
| Add new comparison columns | `ResultTabViewModel` + XAML | `dotnet-wpf-comparison-view` |

🆕 **Production hardening checklist**:
- [ ] Error handling in each use case (try-catch with user-friendly messages)
- [ ] Logging with structured log events
- [ ] Config backup/restore mechanism
- [ ] Timeout settings for Oracle and Dify API calls

> **Values**: 成長の複利 / 継続は力

---

## Good Practices

### 1. Apply Skills in Dependency Order

✅ Always apply foundation skills first, then infrastructure, then presentation. The dependency chain is strict:

```
secure-config → oracle + dify → employee-input → pdf-preview → ocr-input → matching → comparison
```

Skipping ahead causes missing interfaces and compile errors.

### 2. Test Each Layer Independently Before Integration

✅ Each skill provides its own test mechanism (connection test dialogs, unit test patterns). Verify each skill works in isolation before moving to the next step.

```
Step 2: Test Oracle connection → Pass ✅
Step 2: Test Dify API → Pass ✅
Step 4: Test PDF preview → Pass ✅
Step 8: Wire together → Confidence ✅
```

### 3. Use DI for All Cross-Layer Dependencies

✅ Never instantiate infrastructure services directly in ViewModels or use cases. Always inject via constructor and register in the DI container (Step 9).

✅ Prefer constructor injection (Application depends on interfaces)

❌ Avoid `new DifyApiService(...)` inside ViewModels/use cases (tight coupling)


---

## Common Pitfalls & Anti-Patterns

See [references/detailed-patterns.md](references/detailed-patterns.md) for full descriptions and examples.

**Key rules**:
- Apply skills in strict dependency order — `secure-config` before Oracle/Dify
- Never bypass the Application layer from Presentation
- Keep Domain layer free of infrastructure types
- Reference skills — don't duplicate their content

---

## Quick Reference

### Implementation Checklist

- [ ] Create 4-layer DDD solution structure (Step 1)
- [ ] Apply `dotnet-wpf-secure-config` — DPAPI foundation (Step 2)
- [ ] Apply `dotnet-oracle-wpf-integration` — Oracle repository (Step 2)
- [ ] Apply `dotnet-wpf-dify-api-integration` — Dify API client (Step 2)
- [ ] Apply `dotnet-wpf-employee-input` — Employee ID (Step 3)
- [ ] Apply `dotnet-wpf-pdf-preview` — PDF upload + WebView2 (Step 4)
- [ ] Apply `dotnet-wpf-ocr-parameter-input` — OCR parameters tab (Step 5)
- [ ] Apply `dotnet-generic-matching` — Domain matching logic (Step 6)
- [ ] Apply `dotnet-wpf-comparison-view` — Results comparison tab (Step 7)
- [ ] Create `ProcessDocumentUseCase` in Application layer (Step 8)
- [ ] Wire DI container in `App.xaml.cs` (Step 9)
- [ ] Add export functionality (Step 10, optional)
- [ ] Run end-to-end test checklist (Step 11)
- [ ] Customize fields, weights, thresholds for production (Step 12)

### Skill Dependency Graph

- `dotnet-wpf-secure-config` → required by Oracle/Dify/employee-input
- `dotnet-wpf-pdf-preview` → UI-only (feeds selected PDF path)
- `dotnet-wpf-ocr-parameter-input` → depends on Dify + PDF preview
- `dotnet-generic-matching` → Domain-only (no infrastructure)
- `dotnet-wpf-comparison-view` → consumes matching results

### Layer Responsibility Table

| Layer | Contains | Depends On | Example Classes |
|-------|----------|-----------|-----------------|
| 🆕 Domain | Business logic, interfaces, value objects | Nothing | `FieldMatchingService`, `IDataRepository` |
| ✅ Application | Use cases, orchestration | Domain | `ProcessDocumentUseCase` |
| ✅ Infrastructure | DB access, API clients, config | Domain | `OracleDatabaseRepository`, `DifyApiService` |
| ❌ Presentation | ViewModels, Views, XAML | Application | `MainWindowViewModel`, `ResultTabView` |

### Integration Wiring Summary

| From (Producer) | To (Consumer) | Via | Registered In |
|-----------------|--------------|-----|---------------|
| `SecureConfigService` | Oracle, Dify, Employee | `ISecureConfigService` | DI (Step 9) |
| `OracleDatabaseRepository` | `ProcessDocumentUseCase` | `IDataRepository` | DI (Step 9) |
| `DifyApiService` | `ProcessDocumentUseCase` | `IDocumentExtractor` | DI (Step 9) |
| `FieldMatchingService` | `ProcessDocumentUseCase` | Direct (Domain) | DI (Step 9) |
| `ProcessDocumentUseCase` | `OcrProcessTabViewModel` | Constructor injection | DI (Step 9) |

---

## Resources

- `dotnet-wpf-secure-config` — DPAPI encryption and config management
- `dotnet-oracle-wpf-integration` — Oracle database integration
- `dotnet-wpf-dify-api-integration` — Dify API OCR extraction
- `dotnet-generic-matching` — Generic weighted field matching
- `dotnet-wpf-comparison-view` — Side-by-side results UI
- [Microsoft DI Documentation](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection)
- [Domain-Driven Design Reference (Eric Evans)](https://www.domainlanguage.com/ddd/reference/)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-07-13 | 🆕 Initial release — 12-step orchestrator for OCR matching system |

<!-- Japanese version available at references/SKILL.ja.md -->
