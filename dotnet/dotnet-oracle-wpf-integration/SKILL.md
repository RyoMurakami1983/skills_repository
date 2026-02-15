---
name: dotnet-oracle-wpf-integration
description: Add Oracle DB connection to WPF apps with repository pattern and CRUD operations.
author: RyoMurakami1983
tags: [dotnet, wpf, oracle, csharp, mvvm, repository-pattern]
invocable: false
version: 1.0.0
---

# Add Oracle Database Connection to WPF Applications

End-to-end workflow for adding Oracle Database connection to existing .NET WPF applications: OracleConfigModel with DPAPI encryption, MVVM settings dialog with connection test, repository pattern for data access, and SQL execution with ORA-* error handling.

## When to Use This Skill

Use this skill when:
- Adding Oracle Database connection to an existing WPF application
- Creating MVVM settings dialog for Oracle connection with connection test
- Implementing repository pattern (ISofRepository + SofDatabaseOracle) for Oracle
- Executing validated Oracle SQL from `dotnet-access-to-oracle-migration`
- Building data access layer with parameterized queries and connection pooling

**Prerequisites**:
- `dotnet-wpf-secure-config` must be applied first (DPAPI encryption foundation)
- Oracle SQL should be prepared using `dotnet-access-to-oracle-migration` (Access → Oracle conversion)

---

## Related Skills

- **`dotnet-wpf-secure-config`** — Required: DPAPI encryption foundation (apply first)
- **`dotnet-access-to-oracle-migration`** — Convert Access SQL to Oracle SQL for use in Step 5
- **`dotnet-wpf-dify-api-integration`** — Shares SecureConfigService when used in the same app
- **`tdd-standard-practice`** — Test generated code with Red-Green-Refactor
- **`git-commit-practices`** — Commit each step as an atomic change

---

## Core Principles

1. **Layered Architecture** — Separate Domain (ISofRepository), Infrastructure (SofDatabaseOracle), and Presentation (ViewModel) (基礎と型)
2. **Security by Default** — Passwords encrypted via DPAPI; connection strings built at runtime, never stored (ニュートラル)
3. **Progressive Integration** — Config → UI → Repository → SQL, one layer at a time (継続は力)
4. **MVVM Discipline** — ViewModel drives all UI logic; minimal code-behind (基礎と型)
5. **Reusable Components** — Repository and config patterns work across WPF projects (成長の複利)

---

## Workflow: Integrate Oracle DB into WPF

### Step 1 — Set Up Project Structure

Use when initializing the folder structure and NuGet dependencies for Oracle integration.

Add Oracle-specific folders to the existing project structure from `dotnet-wpf-secure-config`:
- `Infrastructure/Configuration/OracleConfigModel.cs` — Oracle config model
- `Infrastructure/Repositories/ISofRepository.cs` + `SofDatabaseOracle.cs` — Data access
- `Presentation/ViewModels/OracleConfigViewModel.cs` — Settings ViewModel
- `Presentation/Views/OracleConfigDialog.xaml` — Settings dialog

```powershell
# Oracle data access provider
Install-Package Oracle.ManagedDataAccess.Core
# MVVM framework (skip if already installed from dotnet-wpf-secure-config)
Install-Package CommunityToolkit.Mvvm
```

> **Values**: 基礎と型 / 成長の複利

### Step 2 — Add Oracle Config Model

Use when defining the Oracle connection configuration with DPAPI-encrypted password.

Create `OracleConfigModel` and integrate it into the existing `AppConfigModel` from `dotnet-wpf-secure-config`.

**OracleConfigModel.cs**:

```csharp
namespace YourApp.Infrastructure.Configuration
{
    public class OracleConfigModel
    {
        public string UserId { get; set; } = string.Empty;
        public string PasswordEncrypted { get; set; } = string.Empty;
        // EZ Connect format required: "host:port/service". Run tnsping to resolve TNS names.
        public string DataSource { get; set; } = string.Empty;

        public string GetDecryptedPassword()
            => DpapiEncryptor.Decrypt(PasswordEncrypted);
        public void SetPassword(string plainPassword)
            => PasswordEncrypted = DpapiEncryptor.Encrypt(plainPassword);
        public bool IsValid()
            => !string.IsNullOrWhiteSpace(UserId)
            && !string.IsNullOrWhiteSpace(PasswordEncrypted)
            && !string.IsNullOrWhiteSpace(DataSource);
    }
}
```

**Update AppConfigModel** (add Oracle property):

```csharp
public class AppConfigModel
{
    public OracleConfigModel OracleDb { get; set; } = new();  // 🆕 Add this
    // public DifyConfigModel DifyApi { get; set; } = new();  // Added by Dify skill
    public string Version { get; set; } = "1.0";
}
```

**Update ISecureConfigService and SecureConfigService** (add Oracle methods):

```csharp
// ISecureConfigService — add:
Task<OracleConfigModel> LoadOracleConfigAsync();
Task SaveOracleConfigAsync(OracleConfigModel config);

// SecureConfigService — implement:
public async Task<OracleConfigModel> LoadOracleConfigAsync()
{
    var appConfig = await LoadAppConfigAsync();
    return appConfig.OracleDb;
}
public async Task SaveOracleConfigAsync(OracleConfigModel config)
{
    var appConfig = await LoadAppConfigAsync();
    appConfig.OracleDb = config;
    await SaveAppConfigAsync(appConfig);
}
```

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Create Settings UI

Use when building the Oracle connection settings dialog with connection test.

Create ViewModel and XAML dialog following MVVM pattern.

**OracleConfigViewModel.cs**:

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace YourApp.Presentation.ViewModels
{
    public partial class OracleConfigViewModel : ObservableObject
    {
        private readonly ISecureConfigService _configService;

        [ObservableProperty] private string userId = string.Empty;
        [ObservableProperty] private string password = string.Empty;
        [ObservableProperty] private string dataSource = string.Empty;
        [ObservableProperty] private string statusMessage = string.Empty;
        [ObservableProperty] private bool isSaving;

        public OracleConfigViewModel(ISecureConfigService configService)
            => _configService = configService;

        public async Task LoadConfigAsync()
        {
            try
            {
                var config = await _configService.LoadOracleConfigAsync();
                UserId = config.UserId;
                DataSource = config.DataSource;
                Password = config.GetDecryptedPassword();
            }
            catch (InvalidOperationException)
            {
                // DPAPI decryption fails if user profile or machine changed
                Password = string.Empty;
                StatusMessage = "Failed to decrypt stored password. Please re-enter.";
            }
        }

        private bool ValidateFields()
        {
            if (string.IsNullOrWhiteSpace(UserId)
                || string.IsNullOrWhiteSpace(Password)
                || string.IsNullOrWhiteSpace(DataSource))
            { StatusMessage = "All fields are required."; return false; }
            return true;
        }

        [RelayCommand]
        private async Task SaveAsync()
        {
            if (!ValidateFields()) return;
            IsSaving = true;
            try
            {
                var config = new OracleConfigModel
                    { UserId = UserId, DataSource = DataSource };
                config.SetPassword(Password);
                await _configService.SaveOracleConfigAsync(config);
                StatusMessage = "Saved.";
            }
            catch (Exception ex) { StatusMessage = $"Save failed: {ex.Message}"; }
            finally { IsSaving = false; }
        }

        [RelayCommand]
        private async Task TestConnectionAsync()
        {
            if (!ValidateFields()) return;
            StatusMessage = "Testing connection...";
            try
            {
                string connStr = $"User Id={UserId};Password={Password};"
                    + $"Data Source={DataSource};Connection Timeout=10;";
                await Task.Run(() =>
                {
                    using var conn = new Oracle.ManagedDataAccess.Client
                        .OracleConnection(connStr);
                    conn.Open();
                    using var cmd = conn.CreateCommand();
                    cmd.CommandText = "SELECT SYSDATE FROM DUAL";
                    cmd.ExecuteScalar();
                });
                StatusMessage = "✅ Connection successful!";
            }
            catch (Exception ex)
            { StatusMessage = $"❌ Connection failed: {ex.Message}"; }
        }
    }
}
```

**OracleConfigDialog.xaml.cs** — Minimal code-behind (PasswordBox bridging only):

```csharp
public partial class OracleConfigDialog : Window
{
    public OracleConfigDialog(OracleConfigViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
        Loaded += async (_, _) => await viewModel.LoadConfigAsync();
        // PasswordBox does not support two-way binding natively
        viewModel.PropertyChanged += (_, e) =>
        { if (e.PropertyName == nameof(viewModel.Password)) PasswordBox.Password = viewModel.Password; };
        PasswordBox.PasswordChanged += (_, _) => viewModel.Password = PasswordBox.Password;
    }
    private void Close_Click(object sender, RoutedEventArgs e) => Close();
}
```

> **Values**: 基礎と型 / 成長の複利

### Step 4 — Build Data Access Layer

Use when implementing the repository pattern for Oracle data access.

Create `ISofRepository` interface in the Domain layer and `SofDatabaseOracle` implementation in Infrastructure.

**ISofRepository.cs** — Domain interface (no Oracle dependency):

```csharp
namespace YourApp.Infrastructure.Repositories
{
    public interface ISofRepository
    {
        // Returns rows as List<Dictionary<column_name, value>>
        Task<List<Dictionary<string, object?>>> QueryAsync(
            string sql, Dictionary<string, object>? parameters = null);
        // Returns affected row count
        Task<int> ExecuteAsync(
            string sql, Dictionary<string, object>? parameters = null);
    }
}
```

**SofDatabaseOracle.cs** — Infrastructure implementation:

```csharp
using Oracle.ManagedDataAccess.Client;

namespace YourApp.Infrastructure.Repositories
{
    public class SofDatabaseOracle : ISofRepository
    {
        private readonly ISecureConfigService _configService;
        public SofDatabaseOracle(ISecureConfigService configService)
            => _configService = configService;

        public async Task<List<Dictionary<string, object?>>> QueryAsync(
            string sql, Dictionary<string, object>? parameters = null)
        {
            var results = new List<Dictionary<string, object?>>();
            await using var conn = await CreateConnectionAsync();
            await using var cmd = conn.CreateCommand();
            cmd.CommandText = sql;
            BindParameters(cmd, parameters);
            await using var reader = await cmd.ExecuteReaderAsync();
            while (await reader.ReadAsync())
            {
                var row = new Dictionary<string, object?>();
                for (int i = 0; i < reader.FieldCount; i++)
                    row[reader.GetName(i)] = reader.IsDBNull(i) ? null : reader.GetValue(i);
                results.Add(row);
            }
            return results;
        }

        public async Task<int> ExecuteAsync(
            string sql, Dictionary<string, object>? parameters = null)
        {
            await using var conn = await CreateConnectionAsync();
            await using var cmd = conn.CreateCommand();
            cmd.CommandText = sql;
            BindParameters(cmd, parameters);
            return await cmd.ExecuteNonQueryAsync();
        }

        private async Task<OracleConnection> CreateConnectionAsync()
        {
            var config = await _configService.LoadOracleConfigAsync();
            if (!config.IsValid())
                throw new InvalidOperationException(
                    "Oracle connection is not configured. Open Settings to enter credentials.");
            string password = config.GetDecryptedPassword();
            var conn = new OracleConnection(
                $"User Id={config.UserId};Password={password};Data Source={config.DataSource};");
            await conn.OpenAsync();
            return conn;
        }

        private static void BindParameters(
            OracleCommand cmd, Dictionary<string, object>? parameters)
        {
            if (parameters == null) return;
            // ✅ Always use parameterized queries — prevents SQL injection
            foreach (var (key, value) in parameters)
                cmd.Parameters.Add(new OracleParameter(key, value ?? DBNull.Value));
        }
    }
}
```

**Why repository pattern**: The domain layer depends on `ISofRepository` (an interface), not on `OracleConnection` (infrastructure). This allows testing with mock repositories and switching databases without changing business logic.

> **Values**: 基礎と型 / 成長の複利

### Step 5 — Implement SQL Execution

Use when executing validated Oracle SQL for CRUD operations.

Use `ISofRepository` methods with SQL from `dotnet-access-to-oracle-migration`.

**SELECT query** (read data):

```csharp
// SQL validated by dotnet-access-to-oracle-migration
string sql = @"
SELECT s.""ship_date"", s.""prod_number"", s.""quantity""
FROM SCHEMA_A.""production_info"" s
WHERE s.""ship_date"" >= :shipDate";

var results = await _repository.QueryAsync(sql,
    new Dictionary<string, object> { { ":shipDate", "202601" } });

foreach (var row in results)
{
    string shipDate = row["ship_date"]?.ToString() ?? "";
    string prodNumber = row["prod_number"]?.ToString() ?? "";
}
```

**INSERT/UPDATE/DELETE** (write data with transaction):

```csharp
await using var conn = new OracleConnection(connectionString);
await conn.OpenAsync();
await using var transaction = conn.BeginTransaction();
try
{
    await using var cmd = conn.CreateCommand();
    cmd.Transaction = transaction;
    cmd.CommandText = @"UPDATE SCHEMA_A.""production_info""
        SET ""status"" = :status WHERE ""prod_number"" = :prodNo";
    cmd.Parameters.Add(new OracleParameter(":status", "SHIPPED"));
    cmd.Parameters.Add(new OracleParameter(":prodNo", "P-001"));
    await cmd.ExecuteNonQueryAsync();
    await transaction.CommitAsync();
}
catch { await transaction.RollbackAsync(); throw; }
```

**Oracle quoting rules** (from `dotnet-access-to-oracle-migration`):
- Table names: `SCHEMA_A."production_info"` (schema + double-quoted lowercase)
- Column names: `"ship_date"` (double-quoted lowercase)
- String literals: `'202601'` (single quotes, not double)
- C# verbatim strings: `@"s.""ship_date"""` (double the double-quotes)

> **Values**: 基礎と型 / 継続は力

### Step 6 — Error Handling

Use when handling Oracle-specific errors from connection or query execution.

Map ORA-* error codes to actionable solutions. See **Quick Reference** for the full error code table.

```csharp
catch (OracleException ex)
{
    string message = ex.Number switch
    {
        1017 => "Authentication failed. Check User ID and Password.",
        12154 => "TNS name not found. Use EZ Connect format (host:port/service).",
        12545 => "Network error. Check host, port, and firewall.",
        50201 => "Invalid Data Source format. Run tnsping to get EZ Connect string.",
        12170 => "Connection timeout. Check network or increase timeout.",
        _ => $"Oracle error ORA-{ex.Number:D5}: {ex.Message}"
    };
    throw new InvalidOperationException(message, ex);
}
```

**TNS vs EZ Connect**: `Oracle.ManagedDataAccess.Core` NuGet package cannot resolve ODBC DSN or TNS names. Run `tnsping DSN_NAME` to extract EZ Connect format (`host:port/service_name`).

> **Values**: 温故知新 / 基礎と型

### Step 7 — Register DI and Test End-to-End

Use when wiring Oracle services into DI and verifying the complete integration.

Add Oracle services to the existing DI setup from `dotnet-wpf-secure-config`.

```csharp
// App.xaml.cs — Add to existing OnStartup
protected override void OnStartup(StartupEventArgs e)
{
    base.OnStartup(e);
    var services = new ServiceCollection();
    // ✅ From dotnet-wpf-secure-config (already registered)
    services.AddSingleton<ISecureConfigService, SecureConfigService>();
    // 🆕 Oracle integration (Transient: fresh connection per operation)
    services.AddTransient<ISofRepository, SofDatabaseOracle>();
    services.AddTransient<OracleConfigViewModel>();
    _serviceProvider = services.BuildServiceProvider();
}
```

```csharp
// Launch settings dialog
var vm = _serviceProvider.GetRequiredService<OracleConfigViewModel>();
new OracleConfigDialog(vm).ShowDialog();

// Smoke test: connection + parameterized query
var repo = _serviceProvider.GetRequiredService<ISofRepository>();
var sysdate = await repo.QueryAsync("SELECT SYSDATE FROM DUAL");
Debug.Assert(sysdate.Count == 1, "SYSDATE query should return 1 row");
```

**Test sequence**: Settings dialog (save/reload/decrypt) → Connection test (`SELECT SYSDATE FROM DUAL`) → Query with SQL from `dotnet-access-to-oracle-migration` → Error handling (wrong credentials → ORA-01017).

> **Values**: 成長の複利 / 継続は力

---

## Common Pitfalls

### 1. Using TNS Names with Oracle.ManagedDataAccess.Core

**Problem**: `Data Source=PROD_DSN` fails with ORA-50201 because the NuGet package cannot resolve ODBC DSN or TNS names.
**Solution**: Run `tnsping PROD_DSN` to get EZ Connect format, then use `Data Source=192.0.2.10:1521/prod_service`.

### 2. Connection Pool Leaks

**Problem**: Forgetting `using` / `Dispose()` on `OracleConnection` exhausts the connection pool.
**Solution**: Always use `await using var conn = ...` to ensure connections return to the pool.

```csharp
// ❌ WRONG — Connection leaks if exception occurs
var conn = new OracleConnection(connStr);
conn.Open();

// ✅ CORRECT — Connection always returned to pool
await using var conn = new OracleConnection(connStr);
await conn.OpenAsync();
```

### 3. Oracle Double-Quote Escaping in C#

**Problem**: C# verbatim strings require doubling `"`, making Oracle quoted identifiers hard to read.
**Solution**: Use `@""` syntax consistently and comment the intended Oracle SQL.

```csharp
// Oracle SQL: SELECT s."ship_date" FROM SCHEMA_A."production_info" s
string sql = @"SELECT s.""ship_date"" FROM SCHEMA_A.""production_info"" s";
```

### 4. Hardcoding Connection Strings

**Problem**: Embedding `User Id=SCOTT;Password=tiger` directly in C# code.
**Solution**: Always read from `ISecureConfigService` and build connection strings at runtime.

---

## Anti-Patterns

### SQL in ViewModel

**What**: Writing Oracle queries directly in the ViewModel or code-behind.
**Why It's Wrong**: Mixes presentation concerns with data access; untestable without a database.
**Better Approach**: All SQL goes through `ISofRepository` in the Infrastructure layer.

### Ignoring Parameterized Queries

**What**: String-concatenating user input into SQL queries.
**Why It's Wrong**: SQL injection vulnerability.
**Better Approach**: Always use `OracleParameter` for dynamic values.

```csharp
// ❌ WRONG — SQL injection risk
cmd.CommandText = $"SELECT * FROM users WHERE name = '{userInput}'";
// ✅ CORRECT — Parameterized query
cmd.CommandText = "SELECT * FROM users WHERE name = :name";
cmd.Parameters.Add(new OracleParameter(":name", userInput));
```

### Skipping DPAPI for Oracle Passwords

**What**: Storing Oracle passwords in plaintext config files or environment variables.
**Why It's Wrong**: Anyone with file system access can read the password.
**Better Approach**: Use `OracleConfigModel.SetPassword()` which encrypts via `DpapiEncryptor`.

---

## Quick Reference

### ORA-* Error Code Quick Reference

| Code | Message | Fix |
|------|---------|-----|
| ORA-01017 | Invalid username/password | Re-enter in Settings dialog |
| ORA-12154 | TNS could not be resolved | Use EZ Connect format |
| ORA-12545 | Connect failed | Check host/port/firewall |
| ORA-50201 | Invalid DSN | Run `tnsping` for EZ Connect |
| ORA-00942 | Table or view does not exist | Check schema + double-quoting |
| ORA-00904 | Invalid identifier | Verify column name case |
| ORA-12170 | Connection timed out | Increase timeout / check network |

### TNS vs EZ Connect Decision

| Scenario | Format | Example |
|----------|--------|---------|
| Have TNS name only | Run `tnsping` first | `tnsping PROD_DSN` |
| Have host/port/service | Use EZ Connect directly | `192.0.2.10:1521/prod_service` |
| Oracle Instant Client installed | TNS may work | `Data Source=PROD_DSN` |
| NuGet package only | EZ Connect required | `Data Source=host:port/service` |

### Implementation Checklist

- [ ] Install NuGet: `Oracle.ManagedDataAccess.Core`, `CommunityToolkit.Mvvm`
- [ ] Create `OracleConfigModel.cs` and update `AppConfigModel` (Step 2)
- [ ] Add Oracle methods to `ISecureConfigService` and `SecureConfigService` (Step 2)
- [ ] Create `OracleConfigViewModel.cs` with connection test (Step 3)
- [ ] Create `OracleConfigDialog.xaml` + `.xaml.cs` (Step 3)
- [ ] Create `ISofRepository` + `SofDatabaseOracle` (Step 4)
- [ ] Add ORA-* error handling (Step 6)
- [ ] Register services and test end-to-end (Step 7)
- [ ] Replace all `YourApp` namespace placeholders

---

## Resources

- `dotnet-access-to-oracle-migration` — SQL conversion workflow for preparing Oracle queries
- [Oracle.ManagedDataAccess.Core NuGet](https://www.nuget.org/packages/Oracle.ManagedDataAccess.Core)
