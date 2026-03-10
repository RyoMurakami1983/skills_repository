# Git Ops Folder Init — Deep Knowledge

## Manufacturing Domain Gitignore Patterns

For steel/metalworking environments, extend the base .gitignore:

```gitignore
# Manufacturing-specific binary formats
*.dwg *.dxf          # CAD drawings
*.sldprt *.sldasm    # SolidWorks parts/assemblies
*.x_t *.x_b          # Parasolid formats
*.pdf                 # Reports (keep source .md, ignore PDF exports)
*.xlsx *.xls *.csv    # Raw measurement data
*.db *.sqlite         # Local databases
```

## Tracked vs Ignored — Decision Matrix

| File type | Track | Ignore | Why |
|-----------|-------|--------|-----|
| .github/ workflows | ✅ | | CI configuration is knowledge |
| .claude/ settings | ✅ | | AI tool config is knowledge |
| *.md documents | ✅ | | Human-readable knowledge artifacts |
| *.py *.sh scripts | ✅ | | Automation code is knowledge |
| *.xlsx *.csv | | ✅ | Raw data → belongs in data systems |
| *.pdf | | ✅ | Derived artifact → regenerate from .md |
| *.docx *.pptx | | ✅ | Binary format → no useful diff |

## Why Not Track Business Files?

Core principle: **git tracks intent and knowledge, not data** (基礎と型)
- Business files (PDFs, spreadsheets) change frequently with no semantic diff
- Binary diffs generate noise, not signal
- Sensitive business data should stay in proper data management systems

## Maintenance Cadence

- **After each ops change**: commit .github/ workflow updates
- **Quarterly**: review .gitignore for new file types introduced
- **Annually**: prune old branches, archive completed project folders
