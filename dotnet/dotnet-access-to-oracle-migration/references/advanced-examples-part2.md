# Advanced Examples - Additional Patterns

## Pattern 5: Advanced - SYNONYM Resolution

**Use Case**: Discovering actual table owners when objects are accessed via synonyms

```sql
-- ✅ CORRECT - Get SYNONYM referent (actual TABLE)
SELECT owner, synonym_name, table_owner, table_name
FROM all_synonyms
WHERE synonym_name IN ('production_info', 'detasheet_info', 'sales_order_info')
  AND owner IN ('SCHEMA_A', 'PUBLIC');
```

**Result**:
```
OWNER     SYNONYM_NAME       TABLE_OWNER  TABLE_NAME
SCHEMA_A  production_info    SCHEMA_B     production_info
SCHEMA_A  detasheet_info    SCHEMA_B     detasheet_info
SCHEMA_A  sales_order_info   SCHEMA_B     sales_order_info
```

**Key Insight**: Real tables are in `SCHEMA_B` schema, accessed via `SCHEMA_A` synonyms. Always query `all_synonyms` to get `table_owner` before querying `all_tab_columns`.

---

## Pattern 6: Advanced - Batch Column Verification

**Use Case**: Automated validation that all Access columns exist in Oracle

```powershell
# ✅ CORRECT - Verify all required columns exist
$tables = @('production_info', 'detasheet_info', 'sales_order_info')
$accessColumns = @{
    'production_info' = @('ship_date', 'prod_number', 'heat_number', 'sales_order_key', 'ext_prod_number', 'furnace_number', 'prod_number_key')
    'detasheet_info' = @('heat_number', 'ext_prod_number', 'ms_issue_date', 'steel_grade')
    'sales_order_info' = @('sales_order_key', 'customer_code', 'destination', 'delivery_code')
}

$missingColumns = @()

foreach ($table in $tables) {
    # Get Oracle columns (use actual table owner from SYNONYM query)
    $sql = "SELECT column_name FROM all_tab_columns WHERE table_name = '$table' AND owner = 'SCHEMA_B'"
    $oracleColumns = Invoke-OracleQuery -Sql $sql | Select-Object -ExpandProperty column_name
    
    # Compare with Access columns
    foreach ($col in $accessColumns[$table]) {
        if ($col -notin $oracleColumns) {
            $missingColumns += "$table.$col"
            Write-Host "⚠ Missing: $table.$col" -ForegroundColor Red
        }
    }
}

if ($missingColumns.Count -eq 0) {
    Write-Host "✓ All Access columns exist in Oracle" -ForegroundColor Green
} else {
    Write-Host "❌ $($missingColumns.Count) columns missing" -ForegroundColor Red
}
```

---

## Migration Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. COLLECT INFORMATION                                          │
│    ├─ Access SQL (query text)                                   │
│    ├─ Record count (178 records)                                │
│    ├─ TNS/DSN name (PROD_DSN)                                   │
│    └─ Credentials (SCHEMA_A / your_password)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. RESOLVE TNS NAME                                             │
│    → tnsping PROD_DSN                                           │
│    → Extract: HOST=192.0.2.10, PORT=1521, SERVICE=prod_service │
│    → Build EZ Connect: 192.0.2.10:1521/prod_service            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. TEST CONNECTION                                              │
│    → Oracle.ManagedDataAccess.Client.OracleConnection          │
│    → Handle errors: ORA-50201, ORA-01017, ORA-12154            │
│    → ✓ Connection successful                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 4. DETECT OBJECT STRUCTURE                                      │
│    → all_objects: object_type = SYNONYM                         │
│    → all_synonyms: table_owner = SCHEMA_B, table_name = production_info│
│    → ✓ Confirmed: SCHEMA_A.xxx are SYNONYMs → SCHEMA_B.xxx (TABLEs)│
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. VALIDATE COLUMNS                                             │
│    → all_tab_columns WHERE owner='SCHEMA_B' AND table_name='...'│
│    → Compare with Access column list                            │
│    → ✓ All required columns exist                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 6. CONVERT SQL                                                  │
│    Rule 1: SCHEMA_A_production_info → SCHEMA_A."production_info"│
│    Rule 2: ship_date → "ship_date"                              │
│    Rule 3: "202601" → '202601'                                  │
│    → ✓ Oracle SQL generated                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. TEST & VALIDATE                                              │
│    → SELECT COUNT(*) FROM converted_sql                         │
│    → Oracle: 178 records, Access: 178 records                   │
│    → Diff: 0 (≤5 acceptable)                                    │
│    → ✓ Near Equal validation passed                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 8. GENERATE C# CODE                                             │
│    → class DetasheetExtractor : IOracle                         │
│    → User/Password/Dsn properties                               │
│    → public string Sql => @"..." (with "" escaping)             │
│    → ✓ IOracle implementation ready                            │
└─────────────────────────────────────────────────────────────────┘
```

---

**See Also**:
- [SKILL.md](../SKILL.md) - Main skill documentation (Quick Reference section)
