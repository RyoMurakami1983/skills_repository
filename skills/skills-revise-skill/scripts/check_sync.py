#!/usr/bin/env python3
"""
EN/JA SKILL.md Synchronization Checker

Checks synchronization between English SKILL.md and Japanese references/SKILL.ja.md
and reports differences with actionable recommendations.

Usage:
    python scripts/check_sync.py path/to/skill-directory/
    python scripts/check_sync.py path/to/skill-directory/ --strict
    python scripts/check_sync.py path/to/skill-directory/ --json
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class SkillDocument:
    """Represents a parsed SKILL.md document"""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = ""
        self.frontmatter = {}
        self.sections = []
        self.pattern_count = 0
        self.good_examples = 0
        self.bad_examples = 0
        self.tables = []
        
        if filepath.exists():
            self._parse()
    
    def _parse(self):
        """Parse the SKILL.md file"""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        self._parse_frontmatter()
        self._parse_sections()
        self._count_patterns()
        self._count_examples()
        self._parse_tables()
    
    def _parse_frontmatter(self):
        """Extract YAML frontmatter"""
        frontmatter_match = re.search(r'^---\n(.*?)\n---', self.content, re.DOTALL)
        if frontmatter_match:
            yaml_content = frontmatter_match.group(1)
            
            # Parse basic fields
            name_match = re.search(r'^name:\s*(.+)$', yaml_content, re.MULTILINE)
            if name_match:
                self.frontmatter['name'] = name_match.group(1).strip()
            
            desc_match = re.search(r'^description:\s*(.+)$', yaml_content, re.MULTILINE)
            if desc_match:
                self.frontmatter['description'] = desc_match.group(1).strip()
            
            author_match = re.search(r'^author:\s*(.+)$', yaml_content, re.MULTILINE)
            if author_match:
                self.frontmatter['author'] = author_match.group(1).strip()
            
            # Parse tags array
            tags_match = re.search(r'^tags:\s*\[(.*?)\]', yaml_content, re.MULTILINE)
            if tags_match:
                tags_str = tags_match.group(1)
                self.frontmatter['tags'] = [
                    tag.strip().strip('"').strip("'") 
                    for tag in tags_str.split(',') 
                    if tag.strip()
                ]
    
    def _parse_sections(self):
        """Extract H2 section headers"""
        # Remove frontmatter first
        content_without_fm = re.sub(r'^---\n.*?\n---\n', '', self.content, flags=re.DOTALL)
        
        # Find all H2 headers
        section_matches = re.finditer(r'^##\s+(.+)$', content_without_fm, re.MULTILINE)
        self.sections = [match.group(1).strip() for match in section_matches]
    
    def _count_patterns(self):
        """Count Pattern 1, Pattern 2, etc."""
        pattern_matches = re.findall(r'###\s+Pattern\s+\d+', self.content, re.IGNORECASE)
        self.pattern_count = len(pattern_matches)
    
    def _count_examples(self):
        """Count ✅ and ❌ markers"""
        self.good_examples = len(re.findall(r'✅', self.content))
        self.bad_examples = len(re.findall(r'❌', self.content))
    
    def _parse_tables(self):
        """Extract table structures"""
        # Find markdown tables (lines with |)
        lines = self.content.split('\n')
        in_table = False
        current_table = []
        
        for line in lines:
            stripped = line.strip()
            if '|' in stripped and stripped.startswith('|'):
                if not in_table:
                    in_table = True
                    current_table = []
                current_table.append(line)
            else:
                if in_table and current_table:
                    self.tables.append(current_table)
                    current_table = []
                in_table = False
        
        if current_table:
            self.tables.append(current_table)
    
    def exists(self) -> bool:
        """Check if the file exists"""
        return self.filepath.exists()


class SyncChecker:
    """Checks synchronization between EN and JA versions"""
    
    def __init__(self, skill_dir: Path, strict: bool = False):
        self.skill_dir = skill_dir
        self.strict = strict
        self.en_doc = SkillDocument(skill_dir / "SKILL.md")
        self.ja_doc = SkillDocument(skill_dir / "references" / "SKILL.ja.md")
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def check(self) -> Dict:
        """Run all synchronization checks"""
        if not self.en_doc.exists():
            return {
                'status': 'ERROR',
                'message': f'SKILL.md not found in {self.skill_dir}'
            }
        
        if not self.ja_doc.exists():
            return {
                'status': 'ERROR',
                'message': f'references/SKILL.ja.md not found in {self.skill_dir}'
            }
        
        is_system_skill = self._check_system_skill()
        self._check_frontmatter()
        self._check_sections()
        self._check_patterns()
        self._check_examples()
        self._check_tables()
        
        return {
            'status': self._get_overall_status(),
            'is_system_skill': is_system_skill,
            'issues': self.issues,
            'warnings': self.warnings,
            'successes': self.successes,
            'recommendations': self._generate_recommendations()
        }
    
    def _check_system_skill(self) -> bool:
        """Check if this is a system skill (author: RyoMurakami1983)"""
        author = self.en_doc.frontmatter.get('author', '')
        return author == 'RyoMurakami1983'
    
    def _check_frontmatter(self):
        """Check YAML frontmatter synchronization"""
        # Name check
        en_name = self.en_doc.frontmatter.get('name', '')
        ja_name = self.ja_doc.frontmatter.get('name', '')
        
        if en_name == ja_name:
            self.successes.append(('frontmatter', f'name: {en_name} (match)'))
        else:
            self.issues.append(('frontmatter', f'name mismatch: EN="{en_name}" JA="{ja_name}"'))
        
        # Description length check
        en_desc = self.en_doc.frontmatter.get('description', '')
        ja_desc = self.ja_doc.frontmatter.get('description', '')
        
        en_len = len(en_desc)
        ja_len = len(ja_desc)
        
        # Allow 20% variance in description length
        if abs(en_len - ja_len) / max(en_len, ja_len, 1) <= 0.2:
            self.successes.append(('frontmatter', f'description: length match (EN: {en_len} chars, JA: {ja_len} chars)'))
        else:
            if self.strict:
                self.issues.append(('frontmatter', f'description length variance: EN={en_len}, JA={ja_len}'))
            else:
                self.warnings.append(('frontmatter', f'description length variance: EN={en_len}, JA={ja_len}'))
        
        # Author check
        en_author = self.en_doc.frontmatter.get('author', '')
        ja_author = self.ja_doc.frontmatter.get('author', '')
        
        if en_author == ja_author:
            self.successes.append(('frontmatter', f'author: {en_author} (match)'))
        else:
            self.issues.append(('frontmatter', f'author mismatch: EN="{en_author}" JA="{ja_author}"'))
        
        # Tags check
        en_tags = self.en_doc.frontmatter.get('tags', [])
        ja_tags = self.ja_doc.frontmatter.get('tags', [])
        
        if set(en_tags) == set(ja_tags):
            self.successes.append(('frontmatter', f'tags: {len(en_tags)} tags match'))
        else:
            missing_in_ja = set(en_tags) - set(ja_tags)
            extra_in_ja = set(ja_tags) - set(en_tags)
            
            msg = 'tags mismatch: '
            if missing_in_ja:
                msg += f'Missing in JA: {list(missing_in_ja)}. '
            if extra_in_ja:
                msg += f'Extra in JA: {list(extra_in_ja)}.'
            
            self.issues.append(('frontmatter', msg.strip()))
    
    def _check_sections(self):
        """Check H2 section structure"""
        en_sections = self.en_doc.sections
        ja_sections = self.ja_doc.sections
        
        if en_sections == ja_sections:
            self.successes.append(('sections', f'H2 sections: {len(en_sections)}/{len(ja_sections)} match'))
        else:
            # Check count
            if len(en_sections) != len(ja_sections):
                self.issues.append(('sections', f'Section count mismatch: EN={len(en_sections)}, JA={len(ja_sections)}'))
            
            # Check order and names
            for i, (en_sec, ja_sec) in enumerate(zip(en_sections, ja_sections)):
                if en_sec != ja_sec:
                    self.warnings.append(('sections', f'Section {i+1} differs: EN="{en_sec}" JA="{ja_sec}"'))
    
    def _check_patterns(self):
        """Check Pattern count"""
        en_count = self.en_doc.pattern_count
        ja_count = self.ja_doc.pattern_count
        
        if en_count == ja_count:
            self.successes.append(('patterns', f'Pattern count: {en_count}/{ja_count} match'))
        else:
            self.issues.append(('patterns', f'Pattern count mismatch: EN={en_count}, JA={ja_count}'))
    
    def _check_examples(self):
        """Check code example counts"""
        en_good = self.en_doc.good_examples
        ja_good = self.ja_doc.good_examples
        en_bad = self.en_doc.bad_examples
        ja_bad = self.ja_doc.bad_examples
        
        # Allow ±2 variance for examples
        if abs(en_good - ja_good) <= 2:
            self.successes.append(('examples', f'Good examples (✅): EN={en_good}, JA={ja_good} (match)'))
        else:
            self.warnings.append(('examples', f'Good examples (✅): EN={en_good}, JA={ja_good} (variance: {abs(en_good - ja_good)})'))
        
        if abs(en_bad - ja_bad) <= 2:
            self.successes.append(('examples', f'Bad examples (❌): EN={en_bad}, JA={ja_bad} (match)'))
        else:
            self.warnings.append(('examples', f'Bad examples (❌): EN={en_bad}, JA={ja_bad} (variance: {abs(en_bad - ja_bad)})'))
    
    def _check_tables(self):
        """Check table structure"""
        en_tables = len(self.en_doc.tables)
        ja_tables = len(self.ja_doc.tables)
        
        if en_tables == ja_tables:
            self.successes.append(('tables', f'Table count: {en_tables}/{ja_tables} match'))
        else:
            self.warnings.append(('tables', f'Table count differs: EN={en_tables}, JA={ja_tables}'))
    
    def _get_overall_status(self) -> str:
        """Determine overall synchronization status"""
        if self.issues:
            return 'PARTIAL SYNC'
        elif self.warnings:
            return 'SYNC WITH WARNINGS'
        else:
            return 'FULL SYNC'
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for category, message in self.issues:
            if 'tags mismatch' in message.lower():
                if 'Missing in JA:' in message:
                    missing = re.search(r"Missing in JA: \[(.*?)\]", message)
                    if missing:
                        tags = missing.group(1).replace("'", "").split(', ')
                        for tag in tags:
                            recommendations.append(f"Add '{tag}' tag to references/SKILL.ja.md")
            
            elif 'Pattern count mismatch' in message:
                en_match = re.search(r'EN=(\d+)', message)
                ja_match = re.search(r'JA=(\d+)', message)
                if en_match and ja_match:
                    en_count = int(en_match.group(1))
                    ja_count = int(ja_match.group(1))
                    if en_count > ja_count:
                        recommendations.append(f"Add {en_count - ja_count} missing Pattern(s) to references/SKILL.ja.md")
                    else:
                        recommendations.append(f"Remove {ja_count - en_count} extra Pattern(s) from references/SKILL.ja.md")
            
            elif 'name mismatch' in message.lower():
                recommendations.append("Ensure 'name' field matches in both versions")
            
            elif 'author mismatch' in message.lower():
                recommendations.append("Ensure 'author' field matches in both versions")
        
        for category, message in self.warnings:
            if 'Good examples' in message or 'Bad examples' in message:
                if '✅' in message:
                    recommendations.append("Review good example markers (✅) in both versions")
                else:
                    recommendations.append("Review bad example markers (❌) in both versions")
        
        return recommendations


def print_text_report(result: Dict, skill_dir: Path):
    """Print human-readable text report"""
    print("=== EN/JA Synchronization Check ===")
    print(f"Directory: {skill_dir.absolute()}\n")
    
    if result['status'] == 'ERROR':
        print(f"❌ ERROR: {result['message']}")
        return
    
    # System skill detection
    print("[System Skill Detection]")
    if result['is_system_skill']:
        print("✅ author: RyoMurakami1983 detected")
        print("→ Enhanced sync checking enabled\n")
    else:
        print("ℹ️  Community skill detected\n")
    
    # Group results by category
    categories = {
        'frontmatter': 'YAML Frontmatter',
        'sections': 'Section Structure',
        'patterns': 'Patterns',
        'examples': 'Code Examples',
        'tables': 'Tables'
    }
    
    for cat_key, cat_name in categories.items():
        successes = [msg for c, msg in result['successes'] if c == cat_key]
        issues = [msg for c, msg in result['issues'] if c == cat_key]
        warnings = [msg for c, msg in result['warnings'] if c == cat_key]
        
        if successes or issues or warnings:
            print(f"[{cat_name}]")
            
            for msg in successes:
                print(f"✅ {msg}")
            
            for msg in issues:
                print(f"❌ {msg}")
            
            for msg in warnings:
                print(f"⚠️  {msg}")
            
            print()
    
    # Overall status
    print("[Overall Status]")
    status = result['status']
    if status == 'FULL SYNC':
        print("✅ FULL SYNC - No issues found")
    elif status == 'SYNC WITH WARNINGS':
        print(f"⚠️  {status} ({len(result['warnings'])} warning(s) found)")
    else:
        print(f"⚠️  {status} ({len(result['issues'])} issue(s) found)")
    
    print()
    
    # Recommendations
    if result['recommendations']:
        print("Recommended Actions:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"{i}. {rec}")


def print_json_report(result: Dict, skill_dir: Path):
    """Print JSON report"""
    output = {
        'directory': str(skill_dir.absolute()),
        'status': result['status'],
        'is_system_skill': result['is_system_skill'],
        'issues': [{'category': c, 'message': m} for c, m in result['issues']],
        'warnings': [{'category': c, 'message': m} for c, m in result['warnings']],
        'successes': [{'category': c, 'message': m} for c, m in result['successes']],
        'recommendations': result['recommendations']
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description='Check synchronization between EN and JA SKILL.md files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/check_sync.py path/to/skill-directory/
  python scripts/check_sync.py path/to/skill-directory/ --strict
  python scripts/check_sync.py path/to/skill-directory/ --json
        """
    )
    
    parser.add_argument(
        'skill_directory',
        type=str,
        help='Path to the skill directory containing SKILL.md'
    )
    
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Enable strict mode (treat warnings as errors)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Automatically fix issues where possible (not yet implemented)'
    )
    
    args = parser.parse_args()
    
    skill_dir = Path(args.skill_directory)
    
    if not skill_dir.exists():
        print(f"❌ ERROR: Directory not found: {skill_dir}", file=sys.stderr)
        sys.exit(1)
    
    if not skill_dir.is_dir():
        print(f"❌ ERROR: Not a directory: {skill_dir}", file=sys.stderr)
        sys.exit(1)
    
    # Run checks
    checker = SyncChecker(skill_dir, strict=args.strict)
    result = checker.check()
    
    # Output results
    if args.json:
        print_json_report(result, skill_dir)
    else:
        print_text_report(result, skill_dir)
    
    # Exit code
    if result['status'] == 'ERROR':
        sys.exit(2)
    elif result['status'] == 'PARTIAL SYNC':
        sys.exit(1)
    elif result['status'] == 'SYNC WITH WARNINGS' and args.strict:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
