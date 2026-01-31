#!/usr/bin/env python3
"""
memory-web.py - Simple HTTP API to browse Gubu's memory

Features:
- Browse memory layers (daily, tacit, knowledge_graph, tools)
- Semantic search via web interface
- View memory by ID
- Progressive disclosure in UI

Usage:
    python memory-web.py              # Start server on port 8080
    python memory-web.py --port 3000  # Start on custom port
"""

import os
import sys
import json
import argparse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import mimetypes

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from memory_search import MemorySearcher, MemoryIndexer, CHROMA_PATH
except ImportError:
    CHROMA_PATH = Path("/home/Gabe/clawd/tools/memory/vector_store")

# Memory system paths
MEMORY_DIR = Path(os.getenv("MEMEX_WORKSPACE", Path.cwd())) / "memory"
LIFE_AREAS_DIR = Path.home() / "life" / "areas"
TOOLS_DIR = Path(os.getenv("MEMEX_WORKSPACE", Path.cwd())) / "tools"

# HTML Template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Gubu's Memory</title>
    <style>
        :root {
            --bg: #0d1117;
            --bg-secondary: #161b22;
            --bg-tertiary: #21262d;
            --text: #c9d1d9;
            --text-secondary: #8b949e;
            --accent: #58a6ff;
            --accent-hover: #79c0ff;
            --border: #30363d;
            --success: #238636;
            --warning: #d29922;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }
        
        header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        h1 { font-size: 1.5rem; color: var(--accent); }
        h1 span { color: var(--text); }
        
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        
        .search-box {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .search-box input {
            flex: 1;
            padding: 0.75rem 1rem;
            font-size: 1rem;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
        }
        
        .search-box input:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        .search-box button {
            padding: 0.75rem 1.5rem;
            background: var(--accent);
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
        }
        
        .search-box button:hover { background: var(--accent-hover); }
        
        .filters {
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 0.5rem 1rem;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 20px;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 0.875rem;
        }
        
        .filter-btn.active {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        
        .stat-card .number {
            font-size: 2rem;
            font-weight: bold;
            color: var(--accent);
        }
        
        .stat-card .label {
            color: var(--text-secondary);
            font-size: 0.875rem;
        }
        
        .memory-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .memory-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.25rem;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .memory-item:hover {
            border-color: var(--accent);
            transform: translateY(-2px);
        }
        
        .memory-item.expanded {
            background: var(--bg-tertiary);
        }
        
        .memory-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5rem;
        }
        
        .memory-layer {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-secondary);
        }
        
        .memory-relevance {
            background: var(--success);
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }
        
        .memory-content {
            color: var(--text);
            line-height: 1.7;
        }
        
        .memory-content.preview {
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .memory-meta {
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid var(--border);
            display: flex;
            gap: 1rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        .memory-full {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
            display: none;
        }
        
        .memory-item.expanded .memory-full {
            display: block;
        }
        
        .citation {
            background: var(--bg-tertiary);
            padding: 0.5rem;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.75rem;
            color: var(--accent);
            margin-top: 0.5rem;
        }
        
        .loading {
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
        }
        
        .empty {
            text-align: center;
            padding: 3rem;
            color: var(--text-secondary);
        }
        
        .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
        
        @media (max-width: 768px) {
            .container { padding: 1rem; }
            .search-box { flex-direction: column; }
            .stats { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <header>
        <div class="container" style="padding: 0;">
            <h1>🧠 <span>Gubu's Memory</span></h1>
        </div>
    </header>
    
    <div class="container">
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search memories... (e.g., \"AGI\", \"Moltbook\", \"deployment\")" autocomplete="off">
            <button onclick="search()">Search</button>
        </div>
        
        <div class="filters">
            <button class="filter-btn active" data-layer="all">All</button>
            <button class="filter-btn" data-layer="daily">📅 Daily</button>
            <button class="filter-btn" data-layer="tacit">🧠 Tacit</button>
            <button class="filter-btn" data-layer="knowledge_graph">🕸️ Knowledge</button>
            <button class="filter-btn" data-layer="tools">🛠️ Tools</button>
        </div>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="number" id="statTotal">-</div>
                <div class="label">Total Memories</div>
            </div>
            <div class="stat-card">
                <div class="number" id="statDaily">-</div>
                <div class="label">Daily Notes</div>
            </div>
            <div class="stat-card">
                <div class="number" id="statKnowledge">-</div>
                <div class="label">Knowledge Graph</div>
            </div>
            <div class="stat-card">
                <div class="number" id="statCompressed">-</div>
                <div class="label">Compressed</div>
            </div>
        </div>
        
        <div class="memory-list" id="results">
            <div class="loading">Loading memories...</div>
        </div>
    </div>
    
    <script>
        let currentFilter = 'all';
        let searchResults = [];
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.dataset.layer;
                if (searchResults.length > 0) {
                    displayResults(searchResults);
                }
            });
        });
        
        // Search on Enter
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') search();
        });
        
        async function search() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;
            
            document.getElementById('results').innerHTML = '<div class="loading">Searching...</div>';
            
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=20`);
                searchResults = await response.json();
                displayResults(searchResults);
            } catch (err) {
                document.getElementById('results').innerHTML = `<div class="empty">Error: ${err.message}</div>`;
            }
        }
        
        function displayResults(results) {
            const container = document.getElementById('results');
            
            // Filter by layer
            let filtered = results;
            if (currentFilter !== 'all') {
                filtered = results.filter(r => r.metadata?.layer === currentFilter);
            }
            
            if (filtered.length === 0) {
                container.innerHTML = `
                    <div class="empty">
                        <div class="empty-icon">🔍</div>
                        <p>No memories found</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = filtered.map(r => `
                <div class="memory-item" onclick="toggleExpand(this)">
                    <div class="memory-header">
                        <span class="memory-layer">
                            ${getLayerIcon(r.metadata?.layer)} ${r.metadata?.layer || 'unknown'}
                        </span>
                        <span class="memory-relevance">${Math.round((r.relevance || 0) * 100)}%</span>
                    </div>
                    <div class="memory-content preview">${escapeHtml(r.content || r.preview || '')}</div>
                    <div class="memory-meta">
                        ${r.metadata?.timestamp ? `<span>📅 ${r.metadata.timestamp}</span>` : ''}
                        ${r.metadata?.entity ? `<span>👤 ${r.metadata.entity}</span>` : ''}
                        <span>📄 ${r.metadata?.source?.split('/').pop() || 'unknown'}</span>
                    </div>
                    <div class="memory-full">
                        <div class="memory-content">${escapeHtml(r.content || '')}</div>
                        <div class="citation">cite: mem-${r.id}</div>
                    </div>
                </div>
            `).join('');
        }
        
        function getLayerIcon(layer) {
            const icons = {
                'daily': '📅',
                'tacit': '🧠',
                'knowledge_graph': '🕸️',
                'tools': '🛠️'
            };
            return icons[layer] || '📝';
        }
        
        function toggleExpand(item) {
            item.classList.toggle('expanded');
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Load stats on page load
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                document.getElementById('statTotal').textContent = stats.total || 0;
                document.getElementById('statDaily').textContent = stats.by_layer?.daily || 0;
                document.getElementById('statKnowledge').textContent = stats.by_layer?.knowledge_graph || 0;
                document.getElementById('statCompressed').textContent = stats.compressed || 0;
            } catch (err) {
                console.error('Failed to load stats:', err);
            }
        }
        
        loadStats();
    </script>
</body>
</html>
'''


class MemoryWebHandler(BaseHTTPRequestHandler):
    """HTTP request handler for memory web interface."""
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        if path == '/' or path == '/index.html':
            self._serve_html()
        elif path == '/api/search':
            self._handle_search(query)
        elif path == '/api/stats':
            self._handle_stats()
        elif path == '/api/memory':
            self._handle_memory_list(query)
        else:
            self._serve_404()
    
    def _serve_html(self):
        """Serve the main HTML page."""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode())
    
    def _handle_search(self, query):
        """Handle search API requests."""
        try:
            q = query.get('q', [''])[0]
            limit = int(query.get('limit', ['10'])[0])
            layer = query.get('layer', [None])[0]
            
            if not q:
                self._serve_json({'error': 'Query required'}, 400)
                return
            
            # Try to use memory_search module
            try:
                from memory_search import MemorySearcher
                searcher = MemorySearcher()
                results = searcher.search(
                    query=q,
                    limit=limit,
                    layer=layer,
                    format_output='detailed'
                )
            except Exception as e:
                # Fallback to simple file search
                results = self._fallback_search(q, limit)
            
            self._serve_json(results)
            
        except Exception as e:
            self._serve_json({'error': str(e)}, 500)
    
    def _handle_stats(self):
        """Handle stats API requests."""
        try:
            stats = self._calculate_stats()
            self._serve_json(stats)
        except Exception as e:
            self._serve_json({'error': str(e)}, 500)
    
    def _handle_memory_list(self, query):
        """Handle memory list API requests."""
        try:
            layer = query.get('layer', [None])[0]
            limit = int(query.get('limit', ['20'])[0])
            
            memories = self._list_memories(layer, limit)
            self._serve_json(memories)
            
        except Exception as e:
            self._serve_json({'error': str(e)}, 500)
    
    def _fallback_search(self, query: str, limit: int) -> list:
        """Fallback search when vector DB not available."""
        results = []
        query_lower = query.lower()
        
        # Search memory files
        if MEMORY_DIR.exists():
            for file_path in MEMORY_DIR.glob("2026-*.md"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if query_lower in content.lower():
                        # Find the relevant section
                        sections = content.split('\n## ')
                        for section in sections:
                            if query_lower in section.lower():
                                results.append({
                                    'id': 'file-' + file_path.stem,
                                    'content': section[:500] + '...' if len(section) > 500 else section,
                                    'metadata': {
                                        'source': str(file_path),
                                        'layer': 'daily',
                                        'timestamp': self._extract_date(file_path.name)
                                    },
                                    'relevance': 0.8
                                })
                                break
                        
                        if len(results) >= limit:
                            break
                except:
                    pass
        
        return results[:limit]
    
    def _list_memories(self, layer: Optional[str], limit: int) -> list:
        """List memories from filesystem."""
        memories = []
        
        if not layer or layer == 'daily':
            if MEMORY_DIR.exists():
                for file_path in sorted(MEMORY_DIR.glob("2026-*.md"), reverse=True)[:limit]:
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        memories.append({
                            'id': 'daily-' + file_path.stem,
                            'preview': content[:200] + '...',
                            'metadata': {
                                'source': str(file_path),
                                'layer': 'daily',
                                'timestamp': self._extract_date(file_path.name)
                            }
                        })
                    except:
                        pass
        
        return memories
    
    def _calculate_stats(self) -> dict:
        """Calculate memory statistics."""
        stats = {
            'total': 0,
            'by_layer': {},
            'compressed': 0
        }
        
        # Count daily notes
        if MEMORY_DIR.exists():
            daily_count = len(list(MEMORY_DIR.glob("2026-*.md")))
            stats['by_layer']['daily'] = daily_count
            stats['total'] += daily_count
        
        # Count knowledge graph
        if LIFE_AREAS_DIR.exists():
            kg_count = 0
            for items_file in LIFE_AREAS_DIR.rglob("items.json"):
                try:
                    with open(items_file) as f:
                        items = json.load(f)
                        kg_count += len(items)
                except:
                    pass
            stats['by_layer']['knowledge_graph'] = kg_count
            stats['total'] += kg_count
        
        # Count compressed summaries
        summaries_dir = MEMORY_DIR / "summaries"
        if summaries_dir.exists():
            compressed_count = len(list(summaries_dir.glob("*.json")))
            stats['compressed'] = compressed_count
        
        # Try to get Chroma stats
        try:
            from memory_search import MemorySearcher
            searcher = MemorySearcher()
            searcher._init_chroma()
            count = searcher.collection.count()
            stats['vector_indexed'] = count
        except:
            stats['vector_indexed'] = 0
        
        return stats
    
    def _extract_date(self, filename: str) -> Optional[str]:
        """Extract date from filename."""
        import re
        match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        return match.group(1) if match else None
    
    def _serve_json(self, data: dict, status: int = 200):
        """Serve JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _serve_404(self):
        """Serve 404 response."""
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Not found'}).encode())


def main():
    parser = argparse.ArgumentParser(description="Web interface for Gubu's memory")
    parser.add_argument('--port', '-p', type=int, default=8080, help='Port to serve on')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    
    args = parser.parse_args()
    
    server = HTTPServer((args.host, args.port), MemoryWebHandler)
    
    print(f"🧠 Gubu's Memory Web")
    print(f"=" * 40)
    print(f"Server running at: http://{args.host}:{args.port}")
    print(f"Press Ctrl+C to stop")
    print(f"=" * 40)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        server.shutdown()


if __name__ == '__main__':
    main()
