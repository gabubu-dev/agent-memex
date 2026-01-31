#!/usr/bin/env python3
"""
memory-compress.py - Session compression for long conversations

Uses AI to generate summaries of longer conversations, creating a compressed
representation that can be stored in the memory system.

Features:
- Compress long conversations into key points
- Extract action items, decisions, and insights
- Generate searchable summaries
- Integrate with the vector index

Usage:
    python memory-compress.py --file conversation.md
    python memory-compress.py --session-id agent:main:abc123
    python memory-compress.py --interactive
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Memory system paths
MEMORY_DIR = Path(os.getenv("MEMEX_WORKSPACE", Path.cwd())) / "memory"
COMPRESSION_LOG = Path(os.getenv("MEMEX_WORKSPACE", Path.cwd())) / "tools" / "compression.log"

@dataclass
class CompressionResult:
    """Result of compressing a session."""
    original_tokens: int
    summary: str
    key_points: List[str]
    action_items: List[str]
    decisions: List[str]
    entities_mentioned: List[str]
    timestamp: str
    source: str


class SessionCompressor:
    """Compress long sessions into searchable summaries."""
    
    def __init__(self):
        self.compression_patterns = {
            'greeting': r"^(hi|hello|hey|good morning|good evening|what's up)[,!]?\s*",
            'acknowledgment': r"^(got it|ok|okay|sure|thanks|thank you)[.!]?\s*",
            ' filler': r"\b(um|uh|like|you know|so yeah|i mean)\b",
        }
    
    def compress_file(self, file_path: Path, max_length: int = 50000) -> CompressionResult:
        """Compress a memory file into a summary."""
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        content = file_path.read_text(encoding='utf-8')
        
        # Estimate tokens (rough approximation: ~4 chars per token)
        original_tokens = len(content) // 4
        
        # If file is small enough, don't compress
        if original_tokens < 1000:
            return self._create_minimal_result(content, original_tokens, str(file_path))
        
        # Extract structured information
        sections = self._extract_sections(content)
        key_points = self._extract_key_points(sections)
        action_items = self._extract_action_items(content)
        decisions = self._extract_decisions(content)
        entities = self._extract_entities(content)
        
        # Generate summary
        summary = self._generate_summary(sections, key_points)
        
        return CompressionResult(
            original_tokens=original_tokens,
            summary=summary,
            key_points=key_points[:20],  # Limit key points
            action_items=action_items[:10],
            decisions=decisions[:10],
            entities_mentioned=entities[:15],
            timestamp=datetime.now().isoformat(),
            source=str(file_path)
        )
    
    def compress_text(self, text: str, source: str = "unknown") -> CompressionResult:
        """Compress raw text content."""
        
        original_tokens = len(text) // 4
        
        if original_tokens < 500:
            return self._create_minimal_result(text, original_tokens, source)
        
        # Split into segments by headers or double newlines
        segments = re.split(r'\n\n+|\n#{1,3}\s', text)
        segments = [s.strip() for s in segments if len(s.strip()) > 50]
        
        # Extract information
        key_points = self._extract_key_points_from_segments(segments)
        action_items = self._extract_action_items(text)
        decisions = self._extract_decisions(text)
        entities = self._extract_entities(text)
        
        summary = self._generate_summary_from_segments(segments, key_points)
        
        return CompressionResult(
            original_tokens=original_tokens,
            summary=summary,
            key_points=key_points[:20],
            action_items=action_items[:10],
            decisions=decisions[:10],
            entities_mentioned=entities[:15],
            timestamp=datetime.now().isoformat(),
            source=source
        )
    
    def _create_minimal_result(self, content: str, tokens: int, source: str) -> CompressionResult:
        """Create a minimal result for short content."""
        return CompressionResult(
            original_tokens=tokens,
            summary=content[:500] + "..." if len(content) > 500 else content,
            key_points=[],
            action_items=[],
            decisions=[],
            entities_mentioned=[],
            timestamp=datetime.now().isoformat(),
            source=source
        )
    
    def _extract_sections(self, content: str) -> List[Dict]:
        """Extract sections from markdown content."""
        sections = []
        
        # Split by headers
        pattern = r'\n(?=#{1,3}\s)'
        parts = re.split(pattern, content)
        
        for part in parts:
            if not part.strip():
                continue
            
            lines = part.split('\n')
            header = lines[0].strip() if lines else ""
            body = '\n'.join(lines[1:]).strip()
            
            sections.append({
                'header': header,
                'body': body,
                'length': len(body)
            })
        
        return sections
    
    def _extract_key_points(self, sections: List[Dict]) -> List[str]:
        """Extract key points from sections."""
        key_points = []
        
        for section in sections:
            header = section['header'].lower()
            body = section['body']
            
            # Important headers indicate key points
            important_patterns = [
                r'decision', r'action', r'plan', r'goal', r'outcome',
                r'result', r'learned', r'lesson', r'insight', r'conclusion',
                r'summary', r'next', r'priority', r'important', r'key'
            ]
            
            if any(re.search(p, header) for p in important_patterns):
                # Extract the main point
                first_sentence = body.split('.')[0] if body else header
                point = f"{header}: {first_sentence[:200]}"
                key_points.append(point)
            
            # Look for bullet points
            bullets = re.findall(r'^[\s]*[-*]\s+(.+)$', body, re.MULTILINE)
            for bullet in bullets[:3]:  # Limit bullets per section
                if len(bullet) > 20 and len(bullet) < 300:
                    key_points.append(bullet)
        
        return list(set(key_points))  # Deduplicate
    
    def _extract_key_points_from_segments(self, segments: List[str]) -> List[str]:
        """Extract key points from text segments."""
        key_points = []
        
        for segment in segments[:10]:  # Limit segments
            # First sentence often contains the key point
            sentences = segment.split('.')
            if sentences:
                first = sentences[0].strip()
                if len(first) > 30 and len(first) < 300:
                    key_points.append(first)
            
            # Look for emphasis markers
            emphasized = re.findall(r'\*\*(.+?)\*\*|__(.+?)__', segment)
            for match in emphasized[:3]:
                text = match[0] or match[1]
                if len(text) > 10:
                    key_points.append(text)
        
        return list(set(key_points))
    
    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items and todos."""
        action_items = []
        
        # Patterns for action items
        patterns = [
            r'(?:TODO|todo|To do|TO DO)[\s:>-]+(.+?)(?:\n|$)',
            r'(?:ACTION|Action)[\s:>-]+(.+?)(?:\n|$)',
            r'(?:need to|needs to|should|must|will)\s+(.{10,150}?)(?:\.|\n|$)',
            r'(?:\[ \]|\[x\])\s*(.+?)(?:\n|$)',  # Checkboxes
            r'(?:next step|follow up|follow-up)[\s:>-]+(.+?)(?:\.|\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                item = match.strip()
                if len(item) > 10 and len(item) < 200:
                    action_items.append(item)
        
        return list(set(action_items))[:10]
    
    def _extract_decisions(self, content: str) -> List[str]:
        """Extract decisions made."""
        decisions = []
        
        patterns = [
            r'(?:decided|decision)[\s:>-]+(.{10,200}?)(?:\.|\n|$)',
            r'(?:we will|I will|let\'s|lets)\s+(.{10,200}?)(?:\.|\n|$)',
            r'(?:going to|plan to)\s+(.{10,200}?)(?:\.|\n|$)',
            r'(?:agreed|agreement)[\s:>-]+(.{10,200}?)(?:\.|\n|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                decision = match.strip()
                if len(decision) > 10:
                    decisions.append(decision)
        
        return list(set(decisions))[:10]
    
    def _extract_entities(self, content: str) -> List[str]:
        """Extract mentioned entities (people, projects, tools)."""
        entities = set()
        
        # Look for capitalized terms (potential proper nouns)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        
        # Filter for likely entities
        common_words = {'The', 'A', 'An', 'This', 'That', 'These', 'Those', 'I', 'We', 'You', 'It', 'He', 'She', 'They'}
        tech_terms = {'Claude', 'GPT', 'AI', 'API', 'CLI', 'Git', 'GitHub', 'Python', 'JavaScript', 'Docker', 'Kubernetes'}
        
        for noun in proper_nouns:
            if noun not in common_words and len(noun) > 2:
                entities.add(noun)
        
        # Add known tech terms if mentioned
        for term in tech_terms:
            if term.lower() in content.lower():
                entities.add(term)
        
        return sorted(list(entities))[:15]
    
    def _generate_summary(self, sections: List[Dict], key_points: List[str]) -> str:
        """Generate a concise summary."""
        # Combine section headers and key content
        summary_parts = []
        
        for section in sections[:5]:  # Top 5 sections
            header = section['header'].lstrip('#').strip()
            if header and not header.startswith('!'):
                summary_parts.append(header)
        
        # Add key points
        if key_points:
            summary_parts.append("Key points: " + "; ".join(key_points[:3]))
        
        return " | ".join(summary_parts)[:500]
    
    def _generate_summary_from_segments(self, segments: List[str], key_points: List[str]) -> str:
        """Generate summary from segments."""
        summary_parts = []
        
        for segment in segments[:3]:
            first_line = segment.split('\n')[0][:100]
            if first_line:
                summary_parts.append(first_line)
        
        if key_points:
            summary_parts.append("Key: " + "; ".join(key_points[:3]))
        
        return " | ".join(summary_parts)[:500]
    
    def save_compressed(self, result: CompressionResult, output_dir: Path = MEMORY_DIR / "summaries") -> Path:
        """Save compressed result to file."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        date_str = datetime.now().strftime("%Y-%m-%d")
        source_name = Path(result.source).stem
        filename = f"{date_str}-{source_name}-compressed.json"
        output_path = output_dir / filename
        
        # Save as JSON
        data = {
            'timestamp': result.timestamp,
            'source': result.source,
            'original_tokens': result.original_tokens,
            'summary': result.summary,
            'key_points': result.key_points,
            'action_items': result.action_items,
            'decisions': result.decisions,
            'entities_mentioned': result.entities_mentioned,
            'compression_ratio': len(result.summary) / (result.original_tokens * 4) if result.original_tokens > 0 else 1.0
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Log compression
        self._log_compression(result, output_path)
        
        return output_path
    
    def _log_compression(self, result: CompressionResult, output_path: Path):
        """Log compression activity."""
        log_entry = {
            'timestamp': result.timestamp,
            'source': result.source,
            'original_tokens': result.original_tokens,
            'output': str(output_path),
            'key_points_count': len(result.key_points),
            'action_items_count': len(result.action_items)
        }
        
        # Append to log
        with open(COMPRESSION_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')


class InteractiveCompressor:
    """Interactive session for compressing memories."""
    
    def __init__(self):
        self.compressor = SessionCompressor()
    
    def run(self):
        """Run interactive compression session."""
        print("🗜️  Memory Compression Tool")
        print("=" * 50)
        print()
        
        # List recent memory files
        recent_files = self._get_recent_memory_files(10)
        
        if not recent_files:
            print("No recent memory files found.")
            return
        
        print("Recent memory files:")
        for i, f in enumerate(recent_files, 1):
            size_kb = f.stat().st_size / 1024
            print(f"  {i}. {f.name} ({size_kb:.1f} KB)")
        
        print()
        print("Options:")
        print("  1-N: Compress specific file")
        print("  a: Compress all recent files")
        print("  p: Paste text to compress")
        print("  q: Quit")
        print()
        
        choice = input("Choose: ").strip().lower()
        
        if choice == 'q':
            return
        elif choice == 'p':
            self._compress_pasted_text()
        elif choice == 'a':
            self._compress_all(recent_files)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(recent_files):
                self._compress_single(recent_files[idx])
            else:
                print("Invalid selection.")
        else:
            print("Invalid choice.")
    
    def _get_recent_memory_files(self, limit: int = 10) -> List[Path]:
        """Get recent memory files sorted by date."""
        if not MEMORY_DIR.exists():
            return []
        
        files = [f for f in MEMORY_DIR.glob("2026-*.md") if f.is_file()]
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return files[:limit]
    
    def _compress_single(self, file_path: Path):
        """Compress a single file."""
        print(f"\nCompressing: {file_path.name}")
        
        try:
            result = self.compressor.compress_file(file_path)
            output_path = self.compressor.save_compressed(result)
            
            print(f"\n✅ Compressed: {result.original_tokens} → {len(result.summary)} chars")
            print(f"📁 Saved to: {output_path}")
            print(f"\nSummary: {result.summary[:200]}...")
            
            if result.key_points:
                print(f"\nKey Points ({len(result.key_points)}):")
                for i, point in enumerate(result.key_points[:5], 1):
                    print(f"  {i}. {point[:100]}...")
            
            if result.action_items:
                print(f"\nAction Items ({len(result.action_items)}):")
                for item in result.action_items[:5]:
                    print(f"  • {item[:80]}...")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _compress_all(self, files: List[Path]):
        """Compress all files."""
        print(f"\nCompressing {len(files)} files...")
        
        for file_path in files:
            try:
                result = self.compressor.compress_file(file_path)
                output_path = self.compressor.save_compressed(result)
                print(f"  ✅ {file_path.name} → {output_path.name}")
            except Exception as e:
                print(f"  ❌ {file_path.name}: {e}")
        
        print("\n✅ All files compressed!")
    
    def _compress_pasted_text(self):
        """Compress pasted text."""
        print("\nPaste text to compress (Ctrl+D when done):")
        print("-" * 50)
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        text = '\n'.join(lines)
        
        if not text.strip():
            print("No text provided.")
            return
        
        result = self.compressor.compress_text(text, source="pasted")
        output_path = self.compressor.save_compressed(result)
        
        print(f"\n✅ Compressed!")
        print(f"Summary: {result.summary}")
        print(f"Saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Compress long conversations into searchable summaries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --file memory/2026-01-30.md
    %(prog)s --interactive
    %(prog)s --recent 5
        """
    )
    
    parser.add_argument('--file', '-f', type=Path, help='Compress specific file')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')
    parser.add_argument('--recent', '-r', type=int, help='Compress N most recent files')
    parser.add_argument('--text', '-t', help='Compress provided text')
    parser.add_argument('--output', '-o', type=Path, help='Output file (default: summaries/)')
    
    args = parser.parse_args()
    
    compressor = SessionCompressor()
    
    if args.interactive:
        interactive = InteractiveCompressor()
        interactive.run()
    elif args.file:
        result = compressor.compress_file(args.file)
        output_path = compressor.save_compressed(result, args.output or MEMORY_DIR / "summaries")
        print(f"✅ Compressed: {args.file.name}")
        print(f"📁 Saved: {output_path}")
        print(f"\nSummary:\n{result.summary}")
    elif args.recent:
        files = sorted(MEMORY_DIR.glob("2026-*.md"), key=lambda f: f.stat().st_mtime, reverse=True)[:args.recent]
        print(f"Compressing {len(files)} recent files...")
        for f in files:
            try:
                result = compressor.compress_file(f)
                compressor.save_compressed(result)
                print(f"  ✅ {f.name}")
            except Exception as e:
                print(f"  ❌ {f.name}: {e}")
    elif args.text:
        result = compressor.compress_text(args.text)
        print(json.dumps({
            'summary': result.summary,
            'key_points': result.key_points,
            'action_items': result.action_items,
            'decisions': result.decisions,
            'entities': result.entities_mentioned
        }, indent=2))
    else:
        parser.print_help()
        print("\n❌ Error: Specify --file, --interactive, --recent, or --text")


if __name__ == '__main__':
    main()
