# Advanced Examples - dotnet-access-to-oracle-migration

Production-grade and advanced implementation examples extracted from the main SKILL.md for progressive disclosure.

---

## Pattern 2: Advanced - Multiple DSN Resolution

**Use Case**: Handling multiple DSN names (e.g., testing across different environments)

```powershell
# ✅ CORRECT - Handle multiple DSN names
$dsnNames = @('DEV_DSN', 'PROD_DSN')

foreach ($dsn in $dsnNames) {
    Write-Host "=== Resolving $dsn ==="
    tnsping $dsn
    
    # Parse HOST, PORT, SERVICE_NAME from output
    $tnspingOutput = tnsping $dsn 2>&1
    
    if ($tnspingOutput -match 'HOST = ([^)]+)') {
        $host = $Matches[1]
    }
    if ($tnspingOutput -match 'PORT = ([^)]+)') {
        $port = $Matches[1]
    }
    if ($tnspingOutput -match 'SERVICE_NAME = ([^)]+)') {
        $serviceName = $Matches[1]
    }
    
    # Build EZ Connect string
    $ezConnect = "$host`:$port/$serviceName"
    Write-Host "EZ Connect: $ezConnect" -ForegroundColor Green
}
```

**Output Example**:
```
=== Resolving DEV_DSN ===
EZ Connect: 192.0.2.10:1521/prod_service

=== Resolving PROD_DSN ===
EZ Connect: 192.0.2.10:1521/prod_service
```

---

## Pattern 4: Advanced - Batch Table Name Conversion

**Use Case**: Converting multiple Access table names to Oracle format in a single operation

```csharp
// ✅ CORRECT - Handle multiple tables from Access SQL
using System;
using System.Linq;

var accessTables = new[] { 
    "SCHEMA_A_production_info", 
    "SCHEMA_A_detasheet_info", 
    "SCHEMA_A_sales_order_info" 
};

var oracleTables = accessTables.Select(t => {
    var parts = t.Split('_', 2);  // Split at FIRST underscore only
    return $"{parts[0]}.\"{parts[1]}\"";
}).ToList();

// Result: [
//   "SCHEMA_A.\"production_info\"", 
//   "SCHEMA_A.\"detasheet_info\"", 
//   "SCHEMA_A.\"sales_order_info\""
// ]

// Use in SQL generation
var fromClause = string.Join(", ", oracleTables.Select((t, i) => $"{t} t{i}"));
Console.WriteLine($"FROM {fromClause}");
// Output: FROM SCHEMA_A."production_info" t0, SCHEMA_A."detasheet_info" t1, SCHEMA_A."sales_order_info" t2
```

---

## Pattern 9: Advanced - Production-Grade C# IOracle with Full 3-Table JOIN

**Use Case**: Complex multi-table JOIN with double-quote escaping for identifiers

```csharp
// ✅ CORRECT - Production C# implementation with 3-table JOIN
using System;

namespace OracleApp
{
    /// <summary>
    /// Detasheet data extraction from Oracle
    /// Joins: production_info ← detasheet_info ← sales_order_info
    /// </summary>
    internal class DetasheetExtractor : IOracle
    {
        string IOracle.User => Environment.GetEnvironmentVariable("ORA_USER") ?? "SCHEMA_A";
        
        string IOracle.Password => Environment.GetEnvironmentVariable("ORA_PW") ?? "your_password";
        
        string IOracle.Dsn => Environment.GetEnvironmentVariable("ORA_DSN") ?? "192.0.2.10:1521/prod_service";
        
        /// <summary>
        /// SQL with 3-table JOIN and extraction conditions
        /// Note: All identifiers quoted with ""
        /// </summary>
        public string Sql => @"
SELECT 
   s.""ship_date"",
   s.""prod_number"",
   m.""ext_prod_number"",
   m.""ms_issue_date"",
   m.""steel_grade"",
   s.""furnace_number"",
   e.""destination"",
   s.""heat_number""
FROM 
   SCHEMA_A.""production_info"" s
   LEFT JOIN SCHEMA_A.""detasheet_info"" m
      ON s.""heat_number"" = m.""heat_number""
      AND s.""ext_prod_number"" = m.""ext_prod_number""
   INNER JOIN SCHEMA_A.""sales_order_info"" e
      ON s.""sales_order_key"" = e.""sales_order_key""
WHERE 
   (s.""ship_date"" >= '202601' OR s.""ship_date"" IS NULL)
   AND m.""ms_issue_date"" >= '20250000'
   AND e.""customer_code"" = '590400'
   AND e.""delivery_code"" = '693800'
ORDER BY 
   s.""prod_number_key""";
    }
}
```

**Key Points**:
1. **Double-quote escaping**: Oracle `"ship_date"` → C# `@""ship_date""`
2. **Environment variables**: Credentials from `ORA_USER`, `ORA_PW`, `ORA_DSN` with fallbacks
3. **JOIN strategy**: LEFT JOIN for optional Detasheet, INNER JOIN for required sales order
4. **WHERE conditions**: Hardcoded values (no parameterization for this use case)
5. **NULL handling**: `OR s.""ship_date"" IS NULL` for incomplete records

**Expected Result**: 178 records (validated against Access query)

---

## Pattern 9: Advanced - Resource Disposal with using Statements

**Use Case**: Proper IDisposable management for Oracle connections

```csharp
// ✅ CORRECT - Production-grade with resource disposal
using System;
using System.Data;
using Oracle.ManagedDataAccess.Client;

public class OracleDataExtractor
{
    private readonly string _connectionString;
    
    public OracleDataExtractor(string user, string password, string dsn)
    {
        // Oracle.ManagedDataAccess.Core requires EZ Connect format
        _connectionString = $"User Id={user};Password={password};Data Source={dsn}";
    }
    
    public DataTable Execute(string sql)
    {
        // using statement ensures connection/command disposal even on exception
        using var connection = new OracleConnection(_connectionString);
        using var command = connection.CreateCommand();
        
        command.CommandText = sql;
        command.CommandTimeout = 300; // 5 minutes for large datasets
        
        try
        {
            connection.Open();
            
            using var adapter = new OracleDataAdapter(command);
            var dataTable = new DataTable();
            adapter.Fill(dataTable);
            
            return dataTable;
        }
        catch (OracleException ex)
        {
            // Log ORA-* error code for debugging
            Console.WriteLine($"Oracle Error {ex.Number}: {ex.Message}");
            throw;
        }
    }
}

// Usage
var extractor = new OracleDataExtractor("SCHEMA_A", "your_password", "192.0.2.10:1521/prod_service");
var sql = @"SELECT s.""prod_number"" FROM SCHEMA_A.""production_info"" s WHERE s.""ship_date"" >= '202601'";
var results = extractor.Execute(sql);
Console.WriteLine($"Retrieved {results.Rows.Count} records");
```

**Why This Matters**:
- **Memory leaks prevented**: `using` ensures Dispose() called even if exception thrown
- **Connection pooling**: Proper disposal returns connections to pool
- **Timeout configuration**: Large datasets need extended CommandTimeout
- **Error context**: ORA-* error codes aid debugging (ORA-50201, ORA-01017, etc.)

---

## References

**See Also**:
- [SKILL.md](../SKILL.md) - Main skill documentation
- [anti-patterns.md](anti-patterns.md) - Common mistakes to avoid
- [SKILL.ja.md](SKILL.ja.md) - 日本語版

**Related Files**:
- [OracleApp/SampleDataExtractor.cs](../../../OracleApp/SampleDataExtractor.cs) - Production implementation
- [OracleApp/BaseExtractor.cs](../../../OracleApp/BaseExtractor.cs) - Reference implementation
