# Common Pitfalls & Anti-Patterns — dotnet-ocr-matching-workflow

> Extracted from the main [SKILL.md](../SKILL.md) for detailed reference.

---

## Common Pitfalls

### 1. Skipping Foundation Skills

**Problem**: Jumping to Oracle or Dify integration without setting up `dotnet-wpf-secure-config` first. Both skills depend on `SecureConfigService` for encrypted credential storage.

**Solution**: Always start with Step 2 in order. The secure-config skill must be applied before any service that stores credentials.

```
❌ Step 2b (Oracle) → Error: ISecureConfigService not found
✅ Step 2a (secure-config) → Step 2b (Oracle) → Works
```

### 2. Tight Coupling Between Layers

**Problem**: ViewModel directly references Oracle `DbConnection` or Dify `HttpClient` instead of going through the Application layer use case.

**Solution**: ViewModels should only depend on Application layer use cases. The use case coordinates Domain and Infrastructure services.

❌ Presentation should not reference Infrastructure types (`DifyApiService`, `OracleConnection`).

✅ Presentation should call Application use cases (`ProcessDocumentUseCase`).

### 3. Not Testing Individual Components Before Integration

**Problem**: Wiring all 7+ skills together and debugging a failure across multiple layers.

**Solution**: Follow Step 11's test checklist. If end-to-end fails, isolate which layer is broken by testing infrastructure connections first, then domain logic, then presentation bindings.

---

## Anti-Patterns

### Bypassing Application Layer

**What**: View directly calls Infrastructure services (e.g., ViewModel creates `OracleConnection` and runs queries).

**Why It's Wrong**: Violates DDD layering. Business logic becomes scattered across ViewModels, making it untestable and non-reusable.

**Better Approach**: Create a use case in the Application layer that coordinates Domain and Infrastructure services. The ViewModel only calls the use case.

### Domain Layer Depending on Infrastructure Types

**What**: Domain model imports `Oracle.ManagedDataAccess` or `System.Net.Http` namespaces.

**Why It's Wrong**: Domain layer must have zero external dependencies. Infrastructure types in Domain make it impossible to unit test without a database or API.

**Better Approach**: Define interfaces in Domain (`IDataRepository`, `IDocumentExtractor`). Implement them in Infrastructure. Register via DI.

❌ Domain must not reference Oracle/Dify namespaces.

✅ Domain should define interfaces and remain infrastructure-agnostic.

### Duplicating Skill Content in This Orchestrator

**What**: Copying full implementation code from `dotnet-generic-matching` or `dotnet-wpf-secure-config` into this workflow skill.

**Why It's Wrong**: Creates maintenance burden — changes to the source skill won't be reflected here. This orchestrator should reference, not replicate.

**Better Approach**: Each step says "Apply: **`skill-name`**" and describes only the wiring and integration points.
