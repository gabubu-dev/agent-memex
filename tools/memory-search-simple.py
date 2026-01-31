#!/usr/bin/env python3
"""
memory-search-simple.py - Lightweight semantic search without heavy dependencies

Uses scikit-learn for TF-IDF + cosine similarity instead of neural embeddings.
Faster to install, lighter on resources, good for smaller memory collections.

Usage:
    python memory-search-simple.py "what did we discuss about AGI"
    python memory-search-simple.py --index              # Rebuild index
    python memory-search-simple.py --install-deps       # Install required packages
"""

import os
import sys
import json
import re
import pickle
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

# Configuration - Override via environment variables
WORKSPACE_DIR = Path(os.getenv('MEMEX_WORKSPACE', Path.cwd()))
MEMORY_DIR = WORKSPACE_DIR / "memory"
LIFE_AREAS_DIR = Path.home() / "life" / "areas"
MEMORY_MD = WORKSPACE_DIR / "MEMORY.md"
AGENTS_MD = WORKSPACE_DIR / "AGENTS.md"
HEARTBEAT_MD = WORKSPACE_DIR / "HEARTBEAT.md"
TOOLS_DIR = WORKSPACE_DIR / "tools"
INDEX_PATH = WORKSPACE_DIR / "tools" / "index.pkl"

@dataclass
class MemoryEntry:
    """A single memory entry with metadata."""
    id: str
    content: str
    source: str
    layer: str
    timestamp: Optional[str] = None
    entity: Optional[str] = None
    category: Optional[str] = None
    
    @classmethod
    def generate_id(cls, content: str, source: str) -> str:
        hash_input = f"{source}:{content[:200]}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


class SimpleMemoryIndexer:
    """Simple indexer using TF-IDF + cosine similarity."""
    
    def __init__(self):
        self.entries: List[MemoryEntry] = []
        self.vectorizer = None
        self.matrix = None
        
    def has_sklearn(self) -> bool:
        """Check if sklearn is available."""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            return True
        except ImportError:
            return False
    
    def install_deps(self):
        """Install required dependencies."""
        print("Installing scikit-learn...")
        os.system("pip install scikit-learn --quiet")
        print("✅ Dependencies installed. Please restart.")
        
    def index_all(self, force_reindex: bool = False):
        """Index all memory sources."""
        if not self.has_sklearn():
            print("❌ scikit-learn not installed.")
            print("Run: python memory-search-simple.py --install-deps")
            return 0
        
        print("🔍 Indexing memories (TF-IDF mode)...")
        
        self.entries = []
        self.entries.extend(self._index_daily_notes())
        self.entries.extend(self._index_tacit_knowledge())
        self.entries.extend(self._index_knowledge_graph())
        self.entries.extend(self._index_tools())
        
        if not self.entries:
            print("⚠️  No entries to index")
            return 0
        
        # Build TF-IDF matrix
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        documents = [e.content for e in self.entries]
        self.matrix = self.vectorizer.fit_transform(documents)
        
        # Save index
        self._save_index()
        
        print(f"✅ Indexed {len(self.entries)} memories")
        print(f"   Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        return len(self.entries)
    
    def _index_daily_notes(self) -> List[MemoryEntry]:
        """Index daily memory notes."""
        entries = []
        
        if not MEMORY_DIR.exists():
            return entries
            
        for file_path in sorted(MEMORY_DIR.glob("*.md")):
            # Skip summaries directory
            if file_path.is_dir():
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                sections = self._split_by_sections(content)
                
                for section in sections:
                    if len(section.strip()) < 50:
                        continue
                        
                    entry = MemoryEntry(
                        id=MemoryEntry.generate_id(section, str(file_path)),
                        content=section,
                        source=str(file_path),
                        layer="daily",
                        timestamp=self._extract_date_from_filename(file_path.name),
                        category=self._extract_category_from_section(section)
                    )
                    entries.append(entry)
                    
            except Exception as e:
                print(f"  ⚠️  Error reading {file_path}: {e}")
                
        print(f"  📅 Daily notes: {len(entries)} entries")
        return entries
    
    def _index_tacit_knowledge(self) -> List[MemoryEntry]:
        """Index tacit knowledge files."""
        entries = []
        
        tacit_files = [MEMORY_MD, AGENTS_MD, HEARTBEAT_MD]
        
        for file_path in tacit_files:
            if not file_path.exists():
                continue
                
            try:
                content = file_path.read_text(encoding='utf-8')
                sections = self._split_by_sections(content)
                
                for section in sections:
                    if len(section.strip()) < 30:
                        continue
                        
                    entry = MemoryEntry(
                        id=MemoryEntry.generate_id(section, str(file_path)),
                        content=section,
                        source=str(file_path),
                        layer="tacit",
                        category=self._extract_category_from_section(section)
                    )
                    entries.append(entry)
                    
            except Exception as e:
                print(f"  ⚠️  Error reading {file_path}: {e}")
        
        print(f"  🧠 Tacit knowledge: {len(entries)} entries")
        return entries
    
    def _index_knowledge_graph(self) -> List[MemoryEntry]:
        """Index knowledge graph."""
        entries = []
        
        if not LIFE_AREAS_DIR.exists():
            return entries
        
        for area_type in ['people', 'companies', 'projects', 'skills', 'workflows']:
            area_dir = LIFE_AREAS_DIR / area_type
            if not area_dir.exists():
                continue
                
            for entity_dir in area_dir.iterdir():
                if not entity_dir.is_dir():
                    continue
                    
                entity_name = entity_dir.name
                
                summary_file = entity_dir / "summary.md"
                if summary_file.exists():
                    try:
                        content = summary_file.read_text(encoding='utf-8')
                        entry = MemoryEntry(
                            id=MemoryEntry.generate_id(content, str(summary_file)),
                            content=content,
                            source=str(summary_file),
                            layer="knowledge_graph",
                            entity=entity_name,
                            category=f"summary:{area_type}"
                        )
                        entries.append(entry)
                    except Exception as e:
                        print(f"  ⚠️  Error reading {summary_file}: {e}")
                
                items_file = entity_dir / "items.json"
                if items_file.exists():
                    try:
                        with open(items_file) as f:
                            items = json.load(f)
                        
                        # Handle both list and dict formats
                        if isinstance(items, dict):
                            items = items.get('items', [])
                        
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                            fact_text = item.get('fact', '')
                            if not fact_text:
                                continue
                                
                            entry = MemoryEntry(
                                id=item.get('id', MemoryEntry.generate_id(fact_text, str(items_file))),
                                content=fact_text,
                                source=str(items_file),
                                layer="knowledge_graph",
                                entity=entity_name,
                                timestamp=item.get('timestamp'),
                                category=item.get('category', 'fact')
                            )
                            entries.append(entry)
                    except Exception as e:
                        print(f"  ⚠️  Error reading {items_file}: {e}")
        
        print(f"  🕸️  Knowledge graph: {len(entries)} entries")
        return entries
    
    def _index_tools(self) -> List[MemoryEntry]:
        """Index tool documentation."""
        entries = []
        
        if not TOOLS_DIR.exists():
            return entries
        
        for skill_file in TOOLS_DIR.rglob("SKILL.md"):
            try:
                content = skill_file.read_text(encoding='utf-8')
                entry = MemoryEntry(
                    id=MemoryEntry.generate_id(content, str(skill_file)),
                    content=content,
                    source=str(skill_file),
                    layer="tools",
                    category="skill"
                )
                entries.append(entry)
            except Exception as e:
                print(f"  ⚠️  Error reading {skill_file}: {e}")
        
        print(f"  🛠️  Tools/skills: {len(entries)} entries")
        return entries
    
    def _split_by_sections(self, content: str) -> List[str]:
        """Split markdown content into sections."""
        parts = re.split(r'\n(?=#{1,3}\s)', content)
        return [p.strip() for p in parts if p.strip()]
    
    def _extract_date_from_filename(self, filename: str) -> Optional[str]:
        """Extract date from filename."""
        match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else None
    
    def _extract_category_from_section(self, section: str) -> Optional[str]:
        """Extract category from section header."""
        lines = section.split('\n')
        for line in lines[:3]:
            if line.startswith('#'):
                return line.lstrip('#').strip().lower()
        return None
    
    def _save_index(self):
        """Save index to disk."""
        INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        index_data = {
            'entries': [{
                'id': e.id,
                'content': e.content,
                'source': e.source,
                'layer': e.layer,
                'timestamp': e.timestamp,
                'entity': e.entity,
                'category': e.category
            } for e in self.entries],
            'vectorizer': self.vectorizer,
            'matrix': self.matrix,
            'indexed_at': datetime.now().isoformat()
        }
        
        with open(INDEX_PATH, 'wb') as f:
            pickle.dump(index_data, f)
    
    def load_index(self) -> bool:
        """Load index from disk."""
        if not INDEX_PATH.exists():
            return False
        
        try:
            with open(INDEX_PATH, 'rb') as f:
                index_data = pickle.load(f)
            
            self.entries = [MemoryEntry(**e) for e in index_data['entries']]
            self.vectorizer = index_data['vectorizer']
            self.matrix = index_data['matrix']
            return True
        except Exception as e:
            print(f"⚠️  Error loading index: {e}")
            return False


class SimpleMemorySearcher:
    """Search using TF-IDF similarity."""
    
    def __init__(self):
        self.indexer = SimpleMemoryIndexer()
        
    def search(
        self,
        query: str,
        limit: int = 10,
        layer: Optional[str] = None,
        since: Optional[str] = None,
        entity: Optional[str] = None
    ) -> List[Dict]:
        """Search memories."""
        
        if not self.indexer.load_index():
            print("⚠️  No index found. Building...")
            self.indexer.index_all()
            self.indexer.load_index()
        
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Vectorize query
        query_vec = self.indexer.vectorizer.transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vec, self.indexer.matrix).flatten()
        
        # Get top indices
        top_indices = similarities.argsort()[::-1]
        
        results = []
        for idx in top_indices:
            entry = self.indexer.entries[idx]
            
            # Apply filters
            if layer and entry.layer != layer:
                continue
            if since and entry.timestamp and entry.timestamp < since:
                continue
            if entity and entry.entity != entity:
                continue
            
            results.append({
                'id': entry.id,
                'content': entry.content,
                'metadata': {
                    'source': entry.source,
                    'layer': entry.layer,
                    'timestamp': entry.timestamp or '',
                    'entity': entry.entity or '',
                    'category': entry.category or ''
                },
                'relevance': float(similarities[idx])
            })
            
            if len(results) >= limit:
                break
        
        return results


def print_index(results: List[Dict]):
    """Print index-only results (ID + preview for progressive disclosure)."""
    if not results:
        print("\n❌ No memories found.")
        return
    
    print(f"\n📇 Index: {len(results)} results (IDs only)\n")
    
    layer_emoji = {
        'daily': '📅',
        'tacit': '🧠',
        'knowledge_graph': '🕸️',
        'tools': '🛠️'
    }
    
    ids = []
    for i, r in enumerate(results, 1):
        emoji = layer_emoji.get(r['metadata']['layer'], '📝')
        preview = r['content'][:80].replace('\n', ' ')
        
        print(f"{i}. [{emoji}] {preview}...")
        print(f"   ID: {r['id']}")
        ids.append(r['id'])
    
    print(f"\n💡 Get full details: python memory-search-simple.py --ids {','.join(ids[:3])}")
    print(f"   Token savings: ~90% (showing previews only)")

def print_results(results: List[Dict]):
    """Print search results."""
    if not results:
        print("\n❌ No memories found.")
        return
    
    print(f"\n🔍 Found {len(results)} relevant memories:\n")
    
    layer_emoji = {
        'daily': '📅',
        'tacit': '🧠',
        'knowledge_graph': '🕸️',
        'tools': '🛠️'
    }
    
    for i, r in enumerate(results, 1):
        emoji = layer_emoji.get(r['metadata']['layer'], '📝')
        preview = r['content'][:150] + '...' if len(r['content']) > 150 else r['content']
        
        print(f"{i}. [{emoji}] {preview[:100]}")
        print(f"   ID: {r['id']} | Source: {os.path.basename(r['metadata']['source'])}")
        if r['metadata'].get('timestamp'):
            print(f"   Date: {r['metadata']['timestamp']}")
        print(f"   Relevance: {r['relevance']:.3f}")
        print()
    
    print(f"💡 Cite by ID: mem-{results[0]['id']}")


def main():
    parser = argparse.ArgumentParser(description="Simple semantic search for memories")
    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--index', action='store_true', help='Rebuild index')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies')
    parser.add_argument('--limit', '-n', type=int, default=10)
    parser.add_argument('--layer', choices=['daily', 'tacit', 'knowledge_graph', 'tools'])
    parser.add_argument('--since', help='Filter by date (YYYY-MM-DD)')
    parser.add_argument('--entity', help='Filter by entity name')
    parser.add_argument('--force', action='store_true', help='Force reindex')
    parser.add_argument('--ids', help='Get full details for specific IDs (comma-separated, e.g. abc123,def456)')
    parser.add_argument('--format', choices=['full', 'index'], default='full', help='Output format: full (default) or index (ID + preview only)')
    
    args = parser.parse_args()
    
    if args.install_deps:
        SimpleMemoryIndexer().install_deps()
        return
    
    if args.index:
        indexer = SimpleMemoryIndexer()
        count = indexer.index_all(force_reindex=args.force)
        print(f"\n✅ Indexed {count} memories")
        return
    
    # Handle ID-based lookup
    if args.ids:
        searcher = SimpleMemorySearcher()
        if not searcher.indexer.load_index():
            print("❌ No index found. Run --index first.")
            sys.exit(1)
        
        requested_ids = [id.strip() for id in args.ids.split(',')]
        results = []
        
        for entry in searcher.indexer.entries:
            if entry.id in requested_ids:
                results.append({
                    'id': entry.id,
                    'content': entry.content,
                    'metadata': {
                        'source': entry.source,
                        'layer': entry.layer,
                        'timestamp': entry.timestamp or '',
                        'entity': entry.entity or '',
                        'category': entry.category or ''
                    },
                    'relevance': 1.0  # Direct lookup, always 100% relevant
                })
        
        print_results(results)
        return
    
    if not args.query:
        parser.print_help()
        print("\n❌ Query required (or use --index or --ids)")
        sys.exit(1)
    
    searcher = SimpleMemorySearcher()
    results = searcher.search(
        query=args.query,
        limit=args.limit,
        layer=args.layer,
        since=args.since,
        entity=args.entity
    )
    
    if args.format == 'index':
        print_index(results)
    else:
        print_results(results)


if __name__ == '__main__':
    main()
