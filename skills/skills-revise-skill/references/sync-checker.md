# English-Japanese Synchronization Checker

Detailed guide for synchronizing English SKILL.md with Japanese references/SKILL.ja.md versions.

## Quick Sync Checklist

When updating system skills (`author: RyoMurakami1983`), verify:

- [ ] Section count matches (EN: 8 sections = JA: 8 sections)
- [ ] Pattern titles identical (e.g., "## Pattern 4: English-Japanese Synchronization")
- [ ] Code block count similar (±2 blocks acceptable)
- [ ] Examples structurally aligned (same number of examples per pattern)
- [ ] Tables have matching columns
- [ ] YAML frontmatter keys present in both

## Automated Sync Checker

### Python Implementation

```python
import re
from pathlib import Path
from typing import Dict, List

class BilingualSyncChecker:
    """Check synchronization between EN and JA skill versions"""
    
    def __init__(self, en_path: Path, ja_path: Path):
        self.en_path = en_path
        self.ja_path = ja_path
        self.en_content = en_path.read_text(encoding='utf-8')
        self.ja_content = ja_path.read_text(encoding='utf-8') if ja_path.exists() else ""
    
    def check_sync(self) -> Dict:
        """Comprehensive sync check"""
        results = {
            'is_synced': True,
            'issues': [],
            'warnings': []
        }
        
        if not self.ja_content:
            results['is_synced'] = False
            results['issues'].append("Japanese version missing (references/SKILL.ja.md)")
            return results
        
        # Check YAML frontmatter
        self._check_frontmatter(results)
        
        # Check section structure
        self._check_sections(results)
        
        # Check code blocks
        self._check_code_blocks(results)
        
        # Check tables
        self._check_tables(results)
        
        return results
    
    def _check_frontmatter(self, results: Dict):
        """Verify frontmatter keys match"""
        en_fm = self._extract_frontmatter(self.en_content)
        ja_fm = self._extract_frontmatter(self.ja_content)
        
        en_keys = set(en_fm.keys())
        ja_keys = set(ja_fm.keys())
        
        missing_in_ja = en_keys - ja_keys
        if missing_in_ja:
            results['is_synced'] = False
            results['issues'].append(
                f"JA frontmatter missing keys: {', '.join(missing_in_ja)}"
            )
        
        extra_in_ja = ja_keys - en_keys
        if extra_in_ja:
            results['warnings'].append(
                f"JA has extra frontmatter keys: {', '.join(extra_in_ja)}"
            )
    
    def _check_sections(self, results: Dict):
        """Check H2 section count and titles"""
        en_sections = self._extract_sections(self.en_content)
        ja_sections = self._extract_sections(self.ja_content)
        
        if len(en_sections) != len(ja_sections):
            results['is_synced'] = False
            results['issues'].append(
                f"Section count mismatch: EN={len(en_sections)}, JA={len(ja_sections)}"
            )
        
        # Check Pattern titles (should be identical)
        for i, (en_title, ja_title) in enumerate(zip(en_sections, ja_sections), 1):
            if en_title.startswith('## Pattern'):
                # Extract "Pattern X:" prefix
                en_prefix = en_title.split(':')[0] if ':' in en_title else en_title
                ja_prefix = ja_title.split(':')[0] if ':' in ja_title else ja_title
                
                if en_prefix != ja_prefix:
                    results['is_synced'] = False
                    results['issues'].append(
                        f"Pattern {i} title mismatch:\n  EN: {en_title}\n  JA: {ja_title}"
                    )
    
    def _check_code_blocks(self, results: Dict):
        """Check code block count"""
        en_count = self.en_content.count('```')
        ja_count = self.ja_content.count('```')
        
        if abs(en_count - ja_count) > 2:  # Allow minor differences
            results['warnings'].append(
                f"Code block count differs: EN={en_count}, JA={ja_count}"
            )
    
    def _check_tables(self, results: Dict):
        """Check table structure"""
        en_tables = re.findall(r'\|.*\|', self.en_content)
        ja_tables = re.findall(r'\|.*\|', self.ja_content)
        
        if abs(len(en_tables) - len(ja_tables)) > 3:
            results['warnings'].append(
                f"Table row count differs: EN={len(en_tables)}, JA={len(ja_tables)}"
            )
    
    def _extract_frontmatter(self, content: str) -> Dict:
        """Extract YAML frontmatter as dict"""
        import yaml
        
        if not content.startswith('---'):
            return {}
        
        end_index = content.find('---', 3)
        if end_index == -1:
            return {}
        
        fm_text = content[3:end_index]
        return yaml.safe_load(fm_text) or {}
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract H2 section titles"""
        return [
            line.strip() for line in content.split('\n')
            if line.startswith('## ')
        ]
    
    def generate_sync_report(self, changes: List[Dict]) -> str:
        """Generate sync checklist for manual updates"""
        report = "# English-Japanese Sync Report\n\n"
        report += f"**Date**: {self._today()}\n"
        report += f"**English**: {self.en_path.name}\n"
        report += f"**Japanese**: {self.ja_path.name}\n\n"
        report += "## Changes to Synchronize\n\n"
        
        for i, change in enumerate(changes, 1):
            report += f"### {i}. {change['section']}\n\n"
            report += f"**Type**: {change['type']}\n"
            report += f"**Description**: {change['description']}\n\n"
            report += "**Action Required**:\n"
            report += f"- [ ] Update Japanese section: `{change['section']}`\n"
            report += f"- [ ] Verify examples still match structure\n"
            report += f"- [ ] Check code block consistency\n\n"
        
        report += "---\n\n"
        report += "## Verification Checklist\n\n"
        report += "After updating Japanese version:\n\n"
        report += "- [ ] Run sync checker again\n"
        report += "- [ ] Spot-check 3-5 changed sections\n"
        report += "- [ ] Verify all code blocks have proper syntax highlighting\n"
        report += "- [ ] Check that tables render correctly\n"
        
        return report
    
    def _today(self) -> str:
        """Get today's date in ISO format"""
        from datetime import date
        return str(date.today())


# Usage Example
if __name__ == "__main__":
    checker = BilingualSyncChecker(
        en_path=Path("SKILL.md"),
        ja_path=Path("references/SKILL.ja.md")
    )
    
    result = checker.check_sync()
    
    if result['is_synced']:
        print("✅ EN and JA versions are in sync")
    else:
        print("⚠️ Synchronization issues detected:\n")
        for issue in result['issues']:
            print(f"  ❌ {issue}")
        
        if result['warnings']:
            print("\n⚠️ Warnings:")
            for warning in result['warnings']:
                print(f"  ⚠️ {warning}")
```

## Manual Sync Workflow

1. **Edit English SKILL.md**
   - Make changes to content
   - Note which sections changed

2. **Identify Change Type**
   - Structural (sections added/removed)
   - Content (examples changed)
   - Wording (clarification)

3. **Update Japanese Version**
   - Open `references/SKILL.ja.md`
   - Locate corresponding sections
   - Apply equivalent changes
   - Maintain same structure

4. **Verify Synchronization**
   - Run sync checker script
   - Fix any detected issues
   - Spot-check 3-5 sections manually

5. **Update CHANGELOG.md**
   - Note changes in both versions
   - Use same version number

## Common Sync Scenarios

### Scenario 1: Added New Pattern

**English**: Added "## Pattern 9: Rollback Strategy"

**Japanese Action**:
1. Add "## Pattern 9: Rollback Strategy" (keep title in English)
2. Translate Overview, Basic Example, When to Use sections
3. Keep code examples identical (comments can be Japanese)
4. Update table of contents if present

### Scenario 2: Code Example Changed

**English**: Updated async/await example in Pattern 3

**Japanese Action**:
1. Copy exact same code (code is language-agnostic)
2. Update Japanese comments if present
3. Verify output examples match

### Scenario 3: Wording Improvement

**English**: Clarified description in "When to Use" section

**Japanese Action**:
1. Re-translate with new clarification
2. Ensure meaning matches English
3. Maintain same structure (bullet points, tables)

## Best Practices

1. **Keep Pattern Titles in English** - "## Pattern X: Title" should be identical
2. **Code is Universal** - Copy code blocks exactly; only translate comments
3. **Structure Over Translation** - Maintain same section order, heading levels
4. **Version Sync** - Both files should have same version in frontmatter
5. **Test Links** - Verify cross-references work in both languages

## Tools Integration

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check if SKILL.md changed
if git diff --cached --name-only | grep -q "SKILL.md"; then
    echo "SKILL.md changed - checking JA sync..."
    uv run python scripts/check_sync.py
    
    if [ $? -ne 0 ]; then
        echo "❌ EN/JA sync check failed"
        echo "   Update references/SKILL.ja.md before committing"
        exit 1
    fi
fi
```

### CI/CD Integration

Add to GitHub Actions workflow:

```yaml
- name: Check EN/JA Synchronization
  run: |
    uv run python scripts/check_sync.py --en SKILL.md --ja references/SKILL.ja.md
  if: contains(github.event.head_commit.modified, 'SKILL.md')
```
