# Skill Quality Validation - Production Code Examples

This file contains advanced production-grade Python code examples extracted from the main SKILL.md file for reference purposes.

---

## 1. Automated Quality Checker (Pattern 1)

**Automated Validation Script** (Python):

```python
# ✅ CORRECT - Automated quality checker
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class ValidationResult:
    category: str
    passed: int
    total: int
    failures: List[str]
    
    @property
    def score(self) -> float:
        return (self.passed / self.total) * 100 if self.total > 0 else 0
    
    @property
    def is_passing(self) -> bool:
        return self.score >= 80.0

class SkillValidator:
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.content = skill_path.read_text(encoding='utf-8')
        self.lines = self.content.split('\n')
        
    def validate_structure(self) -> ValidationResult:
        """Validate 10 structure items"""
        failures = []
        passed = 0
        
        # 1.1: Single file check
        if len(list(self.skill_path.parent.glob('*.md'))) == 1:
            passed += 1
        else:
            failures.append("1.1: Multiple .md files found")
        
        # 1.2: YAML frontmatter
        if self.content.startswith('---'):
            frontmatter = self._extract_frontmatter()
            if all(k in frontmatter for k in ['name', 'description', 'invocable']):
                passed += 1
            else:
                failures.append("1.2: Missing required frontmatter fields")
        else:
            failures.append("1.2: No YAML frontmatter found")
        
        # 1.7: Pattern count
        pattern_count = len(re.findall(r'^## Pattern \d+:', self.content, re.MULTILINE))
        if 7 <= pattern_count <= 10:
            passed += 1
        else:
            failures.append(f"1.7: Found {pattern_count} patterns (need 7-10)")
        
        # ... continue for all 10 checks
        
        return ValidationResult("Structure", passed, 10, failures)
    
    def validate_all(self) -> Dict[str, ValidationResult]:
        """Run all validation categories"""
        return {
            'structure': self.validate_structure(),
            'content': self.validate_content(),
            'code_quality': self.validate_code_quality(),
            'language': self.validate_language()
        }
    
    def generate_report(self) -> str:
        """Generate detailed quality report"""
        results = self.validate_all()
        total_passed = sum(r.passed for r in results.values())
        total_items = sum(r.total for r in results.values())
        overall_score = (total_passed / total_items) * 100
        
        report = f"# Quality Validation Report\n\n"
        report += f"**Overall Score**: {total_passed}/{total_items} ({overall_score:.1f}%)\n"
        report += f"**Status**: {'✅ PASS' if overall_score >= 85 else '❌ FAIL'}\n\n"
        
        for category, result in results.values():
            status = '✅' if result.is_passing else '❌'
            report += f"## {result.category} ({result.passed}/{result.total} = {result.score:.1f}%) {status}\n\n"
            
            if result.failures:
                report += "**Failures:**\n"
                for failure in result.failures:
                    report += f"- {failure}\n"
                report += "\n"
        
        return report

# Usage
validator = SkillValidator(Path("~/.copilot/skills/my-skill/SKILL.md"))
report = validator.generate_report()
print(report)
```

---

## 2. Structure Validator with Detailed Reporting (Pattern 2)

**Automated Structure Validator with Detailed Reporting**:

```python
# ✅ CORRECT - Structure validator with error context
class StructureValidator:
    REQUIRED_SECTIONS = [
        "When to Use This Skill",
        "Core Principles",
        "Common Pitfalls",
        "Anti-Patterns"
    ]
    
    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')
        self.sections = self._extract_sections()
    
    def _extract_sections(self) -> List[Dict[str, any]]:
        """Extract H2 sections with line numbers"""
        sections = []
        for i, line in enumerate(self.lines, 1):
            if line.startswith('## '):
                sections.append({
                    'title': line[3:].strip(),
                    'line_number': i,
                    'level': 2
                })
        return sections
    
    def validate_section_order(self) -> tuple[bool, str]:
        """Validate 'When to Use' is first H2 section"""
        if not self.sections:
            return False, "No H2 sections found"
        
        first_section = self.sections[0]['title']
        if first_section != "When to Use This Skill":
            return False, (
                f"First H2 section is '{first_section}' (line {self.sections[0]['line_number']}), "
                f"expected 'When to Use This Skill'"
            )
        
        return True, "Section order is correct"
    
    def validate_required_sections(self) -> tuple[bool, List[str]]:
        """Check all required sections exist"""
        found_sections = {s['title'] for s in self.sections}
        missing = set(self.REQUIRED_SECTIONS) - found_sections
        
        if missing:
            return False, [f"Missing section: {s}" for s in missing]
        
        return True, []
    
    def validate_pattern_count(self) -> tuple[bool, str]:
        """Validate 7-10 pattern sections exist"""
        patterns = [s for s in self.sections if re.match(r'Pattern \d+:', s['title'])]
        count = len(patterns)
        
        if count < 7:
            return False, f"Only {count} pattern sections (need 7-10). Add {7-count} more patterns."
        elif count > 10:
            return False, f"Too many patterns ({count}). Consider splitting into separate skills."
        
        return True, f"Pattern count is optimal ({count})"
```

---

## 3. Comprehensive Code Quality Analyzer (Pattern 4)

**Comprehensive Code Quality Analyzer**:

```python
# ✅ CORRECT - Full code quality analysis
class CodeQualityAnalyzer:
    def __init__(self, content: str):
        self.content = content
        self.code_blocks = self._extract_code_blocks()
    
    def _extract_code_blocks(self) -> List[Dict]:
        """Extract code blocks with metadata"""
        blocks = []
        pattern = r'```(\w+)\n(.*?)```'
        for match in re.finditer(pattern, self.content, re.DOTALL):
            lang = match.group(1)
            code = match.group(2)
            marker_match = re.search(r'//\s*([✅❌])\s*(CORRECT|WRONG)', code)
            
            blocks.append({
                'language': lang,
                'code': code,
                'marker': marker_match.group(1) if marker_match else None,
                'marker_type': marker_match.group(2) if marker_match else None,
                'start_pos': match.start(),
                'line_count': code.count('\n')
            })
        return blocks
    
    def analyze_progression(self) -> Tuple[bool, str]:
        """Analyze if examples progress from simple to advanced"""
        # Group blocks by pattern section
        patterns = {}
        current_pattern = None
        
        for line in self.content.split('\n'):
            if re.match(r'^## Pattern \d+:', line):
                current_pattern = line
                patterns[current_pattern] = []
            elif current_pattern and '```' in line:
                # Track code blocks per pattern
                pass
        
        # Check for progression indicators
        progression_keywords = ['basic', 'simple', 'configuration', 'advanced', 'production']
        
        failures = []
        for pattern_name, blocks in patterns.items():
            if len(blocks) < 3:
                failures.append(f"{pattern_name}: Only {len(blocks)} code examples (need 3+)")
        
        if failures:
            return False, "; ".join(failures)
        
        return True, "Code progression is appropriate"
    
    def validate_completeness(self) -> ValidationResult:
        """Check for DI, error handling, async patterns"""
        failures = []
        passed = 0
        
        # 3.4.1: DI configuration
        if re.search(r'builder\.Services\.|services\.(Add|Configure)', self.content):
            passed += 1
        else:
            failures.append("3.4.1: No DI configuration examples found")
        
        # 3.4.3: Error handling
        if re.search(r'\btry\s*\{|\bcatch\s*\(', self.content):
            passed += 1
        else:
            failures.append("3.4.3: No error handling examples (try/catch)")
        
        # 3.4.4: Async patterns
        async_count = len(re.findall(r'\basync\s+Task', self.content))
        cancellation_count = len(re.findall(r'CancellationToken', self.content))
        
        if async_count > 0:
            passed += 1
            if cancellation_count >= async_count * 0.5:  # At least 50% have CancellationToken
                passed += 0.5  # Bonus for good async practices
        else:
            failures.append("3.4.4: No async/await examples")
        
        # 3.4.5: Resource management
        if re.search(r'\busing\s+\(|\busing\s+var\b', self.content):
            passed += 1
        else:
            failures.append("3.4.5: No using statements for resource disposal")
        
        return ValidationResult("Code Completeness", int(passed), 5, failures)
```

---

## 4. Detailed HTML Report Generator (Pattern 6)

**Detailed HTML Report Generator**:

```python
# ✅ CORRECT - HTML report with charts and recommendations
from jinja2 import Template

class ReportGenerator:
    HTML_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
    <head><title>Skill Quality Report</title></head>
    <body>
        <h1>Quality Validation Report: {{ skill_name }}</h1>
        <h2>Overall Score: {{ overall_score }}% {{ status }}</h2>
        
        <table>
            <tr><th>Category</th><th>Score</th><th>Status</th></tr>
            {% for cat in categories %}
            <tr>
                <td>{{ cat.name }}</td>
                <td>{{ cat.passed }}/{{ cat.total }} ({{ cat.score }}%)</td>
                <td>{{ cat.status }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>Critical Failures</h2>
        <ul>
        {% for failure in critical_failures %}
            <li>{{ failure }}</li>
        {% endfor %}
        </ul>
        
        <h2>Improvement Recommendations</h2>
        <ol>
        {% for rec in recommendations %}
            <li><strong>{{ rec.priority }}</strong>: {{ rec.action }}</li>
        {% endfor %}
        </ol>
    </body>
    </html>
    '''
    
    def generate(self, validation_results: Dict[str, ValidationResult]) -> str:
        template = Template(self.HTML_TEMPLATE)
        
        # Calculate scores
        total_passed = sum(r.passed for r in validation_results.values())
        total_items = sum(r.total for r in validation_results.values())
        overall = (total_passed / total_items) * 100
        
        # Generate recommendations
        recommendations = self._generate_recommendations(validation_results)
        
        return template.render(
            skill_name="my-skill",
            overall_score=f"{overall:.1f}",
            status="✅ PASS" if overall >= 85 else "❌ FAIL",
            categories=[
                {'name': k, 'passed': v.passed, 'total': v.total, 
                 'score': v.score, 'status': '✅' if v.is_passing else '❌'}
                for k, v in validation_results.items()
            ],
            critical_failures=self._extract_critical_failures(validation_results),
            recommendations=recommendations
        )
```
