---
name: dotnet-access-to-oracle-migration
description: >
  Migrate Access SQL to Oracle, generate .NET C# code.
  Use when converting Access queries to Oracle.
license: MIT
metadata:
  author: RyoMurakami1983
  tags: [dotnet, oracle, access, csharp, database-migration]
  invocable: false
---

# Migrate Access SQL to Oracle

End-to-end workflow for migrating Access database queries to Oracle and generating .NET (C#) IOracle implementation classes. Covers TNS resolution, VIEW/SYNONYM detection, SQL conversion, and record count validation.

## When to Use This Skill

Use this skill when:
- Migrating Access database queries to Oracle for .NET applications
- Converting Access SQL syntax to Oracle-compatible SQL with proper quoting
- Generating C# IOracle implementation classes from validated Oracle queries
- Detecting VIEW/SYNONYM structures that Access links don't reveal
- Validating Oracle connections with tnsping and EZ Connect format
- Ensuring data consistency between Access and Oracle with Near Equal validation

## Related Skills

- **`skill`** — Validate or improve this skill before publishing
- **`skill-writing-guide`** — Learn skill writing best practices

---

## Core Principles

1. **Error-Driven Approach** — Learn from ORA-* errors to correct DSN, authentication, and schema issues (基礎と型)
2. **Structural Awareness** — Detect VIEW/SYNONYM instead of assuming TABLE (ニュートラル)
3. **Access Naming Translation** — Reverse `.` → `_` conversion for Oracle format (基礎と型)
4. **Progressive Validation** — Connect → Detect → Validate → Convert → Generate (継続は力)
5. **Near Equal Tolerance** — Accept ±5 record difference due to timing/data refresh (成長の複利)

---

## Dependencies

- **.NET 6.0+** with Oracle.ManagedDataAccess.Core (NuGet)
- **Oracle Instant Client** for `tnsping` command
- **Access Database** with linked Oracle tables

---

## Workflow: Migrate Access SQL to Oracle

### Step 1 — Collect Information

Gather all required information upfront before attempting Oracle connection.

Collect from user:
1. **Access SQL**: Complete query (Access syntax)
2. **Record count**: Number of records from Access
3. **TNS/DSN name**: Example: PROD_DSN
4. **Oracle credentials**: Username and password

**Why**: Without upfront information, you risk multiple round-trips (wrong TNS → re-ask, missing credentials → re-ask). Collecting everything first enables a single-pass migration.

> **Values**: 基礎と型 / 継続は力

### Step 2 — Resolve TNS Name with tnsping

Run `tnsping` to convert TNS/DSN names to EZ Connect format that Oracle.ManagedDataAccess.Core requires.

```powershell
# ✅ CORRECT — Resolve TNS name to EZ Connect format
# Oracle.ManagedDataAccess.Core cannot use ODBC DSN or TNS names directly
tnsping PROD_DSN
```

**Extract** from output:
- HOST: `192.0.2.10`, PORT: `1521`, SERVICE_NAME: `prod_service`
- **EZ Connect**: `192.0.2.10:1521/prod_service`

**Why**: Oracle.ManagedDataAccess.Core requires EZ Connect format. Guessing the format leads to ORA-50201 errors that waste debugging time.

> **Values**: 基礎と型 / ニュートラル

### Step 3 — Test Connection and Handle Errors

Use ORA-* error codes as learning signals to fix DSN, authentication, or network issues.

```powershell
# ✅ CORRECT — Test connection with error handling
Add-Type -Path "Oracle.ManagedDataAccess.dll"
$conn = New-Object Oracle.ManagedDataAccess.Client.OracleConnection
$conn.ConnectionString = "User Id=SCHEMA_A;Password=your_password;Data Source=192.0.2.10:1521/prod_service"

try {
    $conn.Open()
    Write-Host "✓ Connection successful"
    $conn.Close()  # Important: release connection to pool immediately
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    # ORA-* error codes reveal root cause — use decision table below
}
```

| Error Code | Cause | Solution |
|------------|-------|----------|
| ORA-50201 | DSN format invalid | Use EZ Connect with `tnsping` |
| ORA-01017 | Wrong credentials | Re-check username/password |
| ORA-12154/12545 | TNS/network issue | Use EZ Connect or check firewall |

> **Values**: 基礎と型 / 成長の複利

### Step 4 — Convert Access Table Names

Reverse Access's `.` → `_` conversion: `SCHEMA_A_production_info` → `SCHEMA_A."production_info"`.

```csharp
// ✅ CORRECT — Split at FIRST underscore only
// Access converts OWNER.TABLE → OWNER_TABLE (cannot use '.' in table names)
var parts = "SCHEMA_A_production_info".Split('_', 2);
string oracleFormat = $"{parts[0]}.\"{parts[1]}\"";  // SCHEMA_A."production_info"
```

**Why**: Access silently replaces `.` with `_` in linked table names. Without reversing this, all Oracle queries fail with "table not found".

> **Values**: 基礎と型

### Step 5 — Detect VIEW/SYNONYM Structure

Check object types before assuming TABLE. Access shows all linked objects as "tables", hiding Oracle's real structure.

```sql
-- ✅ CORRECT — Check object type before assuming TABLE
SELECT owner, object_name, object_type
FROM all_objects
WHERE object_name IN ('production_info', 'detasheet_info', 'sales_order_info')
  AND owner IN ('SCHEMA_A', 'SCHEMA_B', 'SCHEMA_C', 'PUBLIC')
ORDER BY owner, object_name;
```

**Typical result**: Objects appear as SYNONYM in `SCHEMA_A`, with real TABLE in `SCHEMA_B`.

**Why**: Skipping this step causes cascading errors in column queries and SQL conversion.

> **Values**: ニュートラル / 基礎と型

> 📚 **Advanced**: SYNONYM referent resolution and multi-owner scenarios → See [references/advanced-examples-part2.md](references/advanced-examples-part2.md#pattern-5-advanced---synonym-resolution)

### Step 6 — Validate Column Existence

Query `all_tab_columns` with the **actual table owner** (not synonym owner) to get exact column names.

```sql
-- ✅ CORRECT — Query columns from actual table owner
SELECT column_id, column_name, data_type, data_length
FROM all_tab_columns
WHERE table_name = 'production_info'
  AND owner = 'SCHEMA_B'  -- Use actual table owner, not synonym owner
ORDER BY column_id;
```

| Column Name | Exists? | Notes |
|-------------|---------|-------|
| `destination` / `destination_code` | ✅ Both | Different columns! |
| `DESTINATION` (uppercase) | ❌ | Case-sensitive! |

**Why**: Column names in Oracle are case-sensitive. A missing or misspelled column causes silent data loss or query errors.

> **Values**: 基礎と型 / 継続は力

> 📚 **Advanced**: Batch column verification → See [references/advanced-examples-part2.md](references/advanced-examples-part2.md#pattern-6-advanced---batch-column-verification)

### Step 7 — Convert SQL Syntax (3 Rules)

Transform Access SQL to Oracle SQL using 3 rules consistently.

**Rule 1**: Table names — `SCHEMA_A_production_info` → `SCHEMA_A."production_info"`
**Rule 2**: Column names — `ship_date` → `"ship_date"`
**Rule 3**: String literals — `"202601"` → `'202601'`

```sql
-- ❌ WRONG — Access SQL
SELECT SCHEMA_A_production_info.ship_date
FROM SCHEMA_A_production_info
WHERE SCHEMA_A_production_info.ship_date >= "202601"

-- ✅ CORRECT — Oracle SQL with proper quoting
SELECT s."ship_date"
FROM SCHEMA_A."production_info" s
WHERE s."ship_date" >= '202601'
```

**Why**: Access and Oracle use opposite quoting conventions. Applying all 3 rules consistently prevents the most common SQL conversion failures.

> **Values**: 基礎と型 / ニュートラル

> 📚 **Advanced**: Multi-table JOIN conversion → See [references/advanced-examples.md](references/advanced-examples.md)

### Step 8 — Validate with Near Equal

Execute converted SQL in Oracle and compare record count to Access count. Accept ±5 difference.

```powershell
# ✅ CORRECT — Count Oracle records and compare
$cmd = $conn.CreateCommand()
$cmd.CommandText = 'SELECT COUNT(*) FROM SCHEMA_A."production_info" s WHERE s."ship_date" >= ''202601'''
$oracleCount = [int]$cmd.ExecuteScalar()
$accessCount = 178  # From user

# ±5 tolerance: data refresh timing, concurrent transactions, cached views
$diff = [Math]::Abs($oracleCount - $accessCount)
if ($diff -le 5) {
    Write-Host "✓ Near Equal: Access=$accessCount, Oracle=$oracleCount (diff=$diff)"
} else {
    Write-Host "⚠ Difference too large: Access=$accessCount, Oracle=$oracleCount (diff=$diff)"
}
```

| Scenario | Action | Why |
|----------|--------|-----|
| Diff ≤ 5 | ✅ Proceed | Acceptable timing/refresh difference |
| Diff > 20 | ❌ Stop | Likely SQL conversion error |

**Why**: Exact count matches are rare because Access and Oracle query at different times. Near Equal validates correctness without requiring identical snapshots.

> **Values**: 成長の複利 / 継続は力

### Step 9 — Generate C# IOracle Implementation

Create C# class implementing IOracle interface with validated Oracle SQL.

```csharp
// ✅ CORRECT — IOracle implementation template
using System;

namespace OracleApp
{
    internal class SampleDataExtractor : IOracle
    {
        // Environment variables allow runtime configuration without recompiling
        string IOracle.User => Environment.GetEnvironmentVariable("ORA_USER") ?? "SCHEMA_A";
        string IOracle.Password => Environment.GetEnvironmentVariable("ORA_PW") ?? "your_password";

        // DSN must use EZ Connect format for Oracle.ManagedDataAccess.Core
        string IOracle.Dsn => Environment.GetEnvironmentVariable("ORA_DSN") ?? "192.0.2.10:1521/prod_service";

        // C# verbatim strings (@"") require doubling internal quotes
        // Oracle: s."ship_date" → C#: s.""ship_date""
        public string Sql => @"
SELECT
   s.""ship_date"",
   s.""prod_number""
FROM SCHEMA_A.""production_info"" s
WHERE s.""ship_date"" >= '202601'";
    }
}
```

**C# String Escaping Rule**: Oracle `"ship_date"` → C# `@""ship_date""` (double the quotes!)

**Why**: Code generation is the final step. Generating code before SQL validation leads to runtime errors harder to debug than SQL-level failures.

> **Values**: 継続は力 / 成長の複利

> 📚 **Advanced**: Full 3-table JOIN with resource disposal → See [references/advanced-examples.md](references/advanced-examples.md#pattern-9-advanced---production-grade-c-ioracle-with-full-3-table-join)

---

## Good Practices

### 1. Always Use tnsping for Connection Resolution

**What**: Run `tnsping` to resolve TNS/DSN names to EZ Connect format before connecting.

**Why**: Eliminates ORA-50201 errors; provides authoritative HOST/PORT/SERVICE_NAME.

**Values**: 基礎と型（再現可能な型）

### 2. Detect Object Type Before Querying

**What**: Check `all_objects` and `all_synonyms` before querying columns or data.

**Why**: Access hides Oracle's VIEW/SYNONYM structure; assuming TABLE causes cascading errors.

**Values**: ニュートラル（偏らない検証）/ 基礎と型

### 3. Validate Columns Before SQL Conversion

**What**: Confirm all Access columns exist in Oracle with exact spelling before converting SQL.

**Why**: Case-sensitive column names cause silent data loss; early validation prevents late failures.

**Values**: 継続は力（段階的検証）

---

## Common Pitfalls

### 1. Using ODBC DSN Directly

**Problem**: Passing `Data Source=PROD_DSN` to Oracle.ManagedDataAccess.Core.

```csharp
// ❌ WRONG — ODBC DSN name causes ORA-50201
var connStr = "User Id=SCHEMA_A;Password=your_password;Data Source=PROD_DSN";
```

**Solution**: Use `tnsping` to get EZ Connect format.

```csharp
// ✅ CORRECT — EZ Connect format
var connStr = "User Id=SCHEMA_A;Password=your_password;Data Source=192.0.2.10:1521/prod_service";
```

### 2. Assuming Tables Instead of Detecting Type

**Problem**: Querying `all_tab_columns` with `owner = 'SCHEMA_A'` when real tables are in `SCHEMA_B`.

**Solution**: Check `all_objects` first, then `all_synonyms` to get actual table owner.

### 3. Forgetting to Escape Double Quotes in C#

**Problem**: Copy-paste Oracle SQL into C# without doubling quotes.

**Solution**: Double every `"` inside C# `@""` strings: `s."ship_date"` → `s.""ship_date""`.

---

## Anti-Patterns

### Skipping tnsping and Guessing EZ Connect

**What**: Assuming `Data Source=PROD_DSN` means `Data Source=someserver:1521/PROD_DSN`.

**Why It's Wrong**: TNS names don't follow predictable patterns; hostnames can be IPs, DNS names, or aliases; service names may differ from TNS names.

**Better Approach**: Always run `tnsping` to get authoritative HOST/PORT/SERVICE_NAME.

---

## Quick Reference

### Migration Checklist

- [ ] Collect: Access SQL, record count, TNS name, credentials
- [ ] Resolve TNS → `tnsping` → EZ Connect format
- [ ] Test connection → Handle ORA-* errors
- [ ] Convert Access table names → `SCHEMA."table_name"` format
- [ ] Detect structure → `all_objects` (VIEW/SYNONYM/TABLE)
- [ ] Validate columns → `all_tab_columns` with actual owner
- [ ] Convert SQL → 3 rules (table/column/literal quoting)
- [ ] Validate → COUNT(*) ≈ Access count (±5)
- [ ] Generate C# → IOracle implementation with `""` escaping

### Conversion Cheat Sheet

| Access | Oracle | C# @"" String |
|--------|--------|---------------|
| `SCHEMA_A_production_info` | `SCHEMA_A."production_info"` | `SCHEMA_A.""production_info""` |
| `ship_date` | `"ship_date"` | `""ship_date""` |
| `"202601"` | `'202601'` | `'202601'` |

---

## Resources

- [references/advanced-examples.md](references/advanced-examples.md) — Production-grade examples
- [references/advanced-examples-part2.md](references/advanced-examples-part2.md) — Additional examples
- [references/SKILL.ja.md](references/SKILL.ja.md) — 日本語版

---

## Changelog

### Version 2.0.0 (2026-02-15)
- **Breaking**: Converted from Pattern format to single Workflow format
- Add Values integration to Core Principles and all Steps
- Add Good Practices, Common Pitfalls, Anti-Patterns sections
- Add Dependencies section and Migration Checklist

### Version 1.0.0 (2026-02-12)
- Initial release (Pattern format)
- 9 patterns covering full migration workflow
