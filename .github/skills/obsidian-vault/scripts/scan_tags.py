#!/usr/bin/env python3
"""
Obsidian Tag Scanner

Scans all markdown files in Second Brain and extracts:
- Frontmatter tags (tags: [...])
- Inline tags (#tag/subtag)

Usage:
    python scan_tags.py [--json] [--by-file]
"""

import os
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict
from typing import Set, Dict, List


def find_second_brain() -> Path:
    """Find Second Brain directory by walking up from script location."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "Second Brain"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find 'Second Brain' directory")


def extract_frontmatter_tags(content: str) -> Set[str]:
    """Extract tags from YAML frontmatter."""
    tags = set()
    
    # Match frontmatter block
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not frontmatter_match:
        return tags
    
    frontmatter = frontmatter_match.group(1)
    
    # Match tags: [...] or tags: tag1, tag2
    tags_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter)
    if tags_match:
        tag_str = tags_match.group(1)
        # Parse individual tags
        for tag in re.findall(r'[\w/\-]+', tag_str):
            tags.add(tag)
    
    return tags


def extract_inline_tags(content: str) -> Set[str]:
    """Extract inline #tags from content."""
    tags = set()
    
    # Skip frontmatter
    content_body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    
    # Match #tag or #tag/subtag (but not inside code blocks)
    # Simple approach: find all #word patterns
    for match in re.finditer(r'(?<!\S)#([\w\-]+(?:/[\w\-]+)*)', content_body):
        tag = match.group(1)
        # Skip hex colors and common false positives
        if not re.match(r'^[0-9a-fA-F]{3,6}$', tag):
            tags.add(tag)
    
    return tags


def scan_vault(vault_path: Path) -> Dict[str, Dict[str, Set[str]]]:
    """Scan all markdown files and return tags by file."""
    results = {}
    
    for md_file in vault_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            frontmatter_tags = extract_frontmatter_tags(content)
            inline_tags = extract_inline_tags(content)
            
            if frontmatter_tags or inline_tags:
                rel_path = str(md_file.relative_to(vault_path))
                results[rel_path] = {
                    'frontmatter': frontmatter_tags,
                    'inline': inline_tags
                }
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
    
    return results


def aggregate_tags(results: Dict[str, Dict[str, Set[str]]]) -> Dict[str, List[str]]:
    """Aggregate all tags with files that use them."""
    tag_to_files = defaultdict(list)
    
    for file_path, tags_data in results.items():
        all_tags = tags_data['frontmatter'] | tags_data['inline']
        for tag in all_tags:
            tag_to_files[tag].append(file_path)
    
    return dict(sorted(tag_to_files.items()))


def print_summary(results: Dict[str, Dict[str, Set[str]]]):
    """Print a human-readable summary."""
    aggregated = aggregate_tags(results)
    
    print(f"\n{'='*60}")
    print(f"OBSIDIAN TAG SCAN - Second Brain")
    print(f"{'='*60}\n")
    
    print(f"📁 Files scanned: {len(results)}")
    print(f"🏷️  Unique tags: {len(aggregated)}\n")
    
    # Group by tag prefix
    prefixes = defaultdict(list)
    for tag in aggregated.keys():
        prefix = tag.split('/')[0] if '/' in tag else tag
        prefixes[prefix].append(tag)
    
    print("Tags by category:\n")
    for prefix, tags in sorted(prefixes.items()):
        print(f"  {prefix}/")
        for tag in sorted(tags):
            count = len(aggregated[tag])
            print(f"    {tag} ({count} files)")
    
    print(f"\n{'='*60}\n")


def print_by_file(results: Dict[str, Dict[str, Set[str]]]):
    """Print tags organized by file."""
    print(f"\n{'='*60}")
    print(f"TAGS BY FILE")
    print(f"{'='*60}\n")
    
    for file_path, tags_data in sorted(results.items()):
        all_tags = sorted(tags_data['frontmatter'] | tags_data['inline'])
        if all_tags:
            print(f"📄 {file_path}")
            print(f"   {', '.join(all_tags)}\n")


def main():
    parser = argparse.ArgumentParser(description='Scan Obsidian vault for tags')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--by-file', action='store_true', help='Show tags by file')
    parser.add_argument('--path', type=str, help='Custom vault path')
    args = parser.parse_args()
    
    try:
        vault_path = Path(args.path) if args.path else find_second_brain()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    
    if not vault_path.exists():
        print(f"Error: Vault path not found: {vault_path}")
        return 1
    
    results = scan_vault(vault_path)
    
    if args.json:
        # Convert sets to lists for JSON serialization
        json_results = {
            'files': {
                path: {
                    'frontmatter': list(data['frontmatter']),
                    'inline': list(data['inline'])
                }
                for path, data in results.items()
            },
            'aggregated': {
                tag: files for tag, files in aggregate_tags(results).items()
            }
        }
        print(json.dumps(json_results, indent=2))
    elif args.by_file:
        print_by_file(results)
    else:
        print_summary(results)
    
    return 0


if __name__ == '__main__':
    exit(main())
