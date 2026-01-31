# 🧠 Memex: Persistent Memory for AI Agents

**Memex** is a file-based memory system for AI agents with three-tier architecture, progressive disclosure, and platform-agnostic design.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Why Memex?

AI agents need memory that:
- **Persists** across sessions
- **Scales** without bloating context windows
- **Integrates** with any platform (Claude Code, Clawdbot, custom assistants)
- **Stays transparent** (plain text files, not SQLite black boxes)

**Memex delivers:**
- ✅ **77% token savings** through progressive disclosure
- ✅ **Three-tier architecture** (facts, events, wisdom)
- ✅ **Platform-agnostic** file-based design
- ✅ **Semantic search** with TF-IDF or neural embeddings
- ✅ **Timeline views** for chronological context
- ✅ **Session compression** for long conversations
- ✅ **Web viewer** for human oversight

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/gabubu-dev/agent-memex.git
cd agent-memex

# Run setup script
bash scripts/setup.sh

# Build the search index
python tools/memory-search-simple.py --index

# Search your memories
python tools/memory-search-simple.py "what did I learn about deployment?"

# View in browser
python tools/memory-web.py
# Open http://localhost:8080
```

## 📖 Architecture

Memex organizes memory in **three complementary layers**:

```
┌─────────────────────────────────────────────────────────────┐
│                         MEMEX v1.0                           │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Knowledge Graph (~/life/areas/)                    │
│  ├── entities/people/items.json - Atomic facts               │
│  └── entities/people/summary.md - Living summaries           │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Daily Notes (memory/YYYY-MM-DD.md)                 │
│  └── Raw event logs with timestamps                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Tacit Knowledge (MEMORY.md, AGENTS.md)             │
│  └── Patterns, preferences, lessons learned                  │
├─────────────────────────────────────────────────────────────┤
│  🔍 Search Layer (tools/memory/)                             │
│  ├── Semantic search (TF-IDF or neural)                      │
│  ├── Timeline views (chronological context)                  │
│  └── Session compression (AI-powered summaries)              │
└─────────────────────────────────────────────────────────────┘
```

### Layer 1: Knowledge Graph
**Durable facts about entities (people, projects, companies)**

```
~/life/areas/
├── people/alice/
│   ├── items.json      # Atomic facts (never deleted)
│   └── summary.md      # Current snapshot (updated weekly)
├── projects/memex/
│   ├── items.json
│   └── summary.md
```

**When to use:** "What do I know about Alice?"

### Layer 2: Daily Notes
**Raw event logs - what happened, when**

```
memory/
├── 2026-01-30.md       # Today's events
├── 2026-01-29.md
├── 2026-01-28.md
```

**When to use:** "What did we do on Tuesday?" or "When did X happen?"

### Layer 3: Tacit Knowledge
**Patterns, preferences, operating principles**

```
MEMORY.md          # Long-term distilled wisdom
AGENTS.md          # How the agent operates
TOOLS.md           # Environment-specific notes
```

**When to use:** "How should I approach X?" or "What are my preferences for Y?"

## 🔍 Progressive Disclosure Workflow

**Problem:** Loading all search results wastes tokens.

**Solution:** Three-step progressive disclosure:

### Step 1: Index (Cheap - ~100 tokens/result)
```bash
python tools/memory-search-simple.py "Memex features" --format index --limit 10
```

**Output:** IDs + short previews
```
📇 Index: 10 results (IDs only)

1. [🧠] Memex: Three-tier memory system for AI agents...
   ID: abc123
2. [📅] Implemented progressive disclosure feature...
   ID: def456
```

### Step 2: Timeline (Medium - context)
```bash
python tools/memory-timeline.py --query "Memex features"
```

**Output:** Chronological context (what happened before/after)

### Step 3: Full Details (Expensive - only what you need)
```bash
python tools/memory-search-simple.py --ids abc123,def456
```

**Result:** 77% token savings compared to loading everything!

## 🛠️ Tools

### 1. `memory-search-simple.py` - Semantic Search
Lightweight TF-IDF-based search (no heavy dependencies).

```bash
# Build index
python tools/memory-search-simple.py --index

# Search
python tools/memory-search-simple.py "what did we discuss about AGI"

# Progressive disclosure
python tools/memory-search-simple.py "deployment" --format index
python tools/memory-search-simple.py --ids abc123,def456

# Filter by layer
python tools/memory-search-simple.py "preferences" --layer tacit

# Filter by date
python tools/memory-search-simple.py "bug fix" --since 2026-01-28

# Filter by entity
python tools/memory-search-simple.py "status" --entity alice
```

### 2. `memory-timeline.py` - Chronological Context
Show what was happening around a specific memory.

```bash
# Timeline around a search result
python tools/memory-timeline.py --query "Moltbook"

# Timeline around a specific date
python tools/memory-timeline.py --date 2026-01-30 --before 48 --after 24

# Timeline around a memory ID
python tools/memory-timeline.py --id mem-abc123 --before 24 --after 12
```

### 3. `memory-compress.py` - Session Compression
Compress long conversations into searchable summaries.

```bash
# Compress a specific file
python tools/memory-compress.py --file memory/2026-01-30.md

# Compress recent files
python tools/memory-compress.py --recent 5

# Interactive mode
python tools/memory-compress.py --interactive

# Compress pasted text
python tools/memory-compress.py --text "Long conversation..."
```

**What it extracts:**
- Summary (one-line overview)
- Key points (important takeaways)
- Action items (TODOs)
- Decisions (what was decided)
- Entities (people, projects, tools mentioned)

### 4. `memory-web.py` - Web Viewer
Browse and search memories through a web interface.

```bash
# Start server
python tools/memory-web.py

# Custom port
python tools/memory-web.py --port 3000
```

Then open `http://localhost:8080` in your browser.

## 📦 Installation

### Option 1: Lightweight (Recommended)
Uses TF-IDF via scikit-learn (faster install, good results):

```bash
# Install dependencies
pip install scikit-learn

# Or use the setup script
bash scripts/setup.sh
```

### Option 2: Neural Embeddings (Advanced)
For state-of-the-art semantic understanding:

```bash
pip install chromadb sentence-transformers
```

Then use the full `memory-search.py` instead of `memory-search-simple.py`.

## 🆚 Memex vs Claude-Mem

| Feature | Memex | Claude-Mem |
|---------|-------|------------|
| **Storage** | Plain text files | SQLite database |
| **Architecture** | 3-tier (facts/events/wisdom) | 2-tier (observations/summaries) |
| **Platform** | Any (Clawdbot, Claude Code, custom) | Claude Code only |
| **Transparency** | Full (grep-able files) | Opaque (binary DB) |
| **Search** | TF-IDF or neural | SQLite FTS5 + Chroma |
| **Progressive Disclosure** | ✅ Yes (3-step workflow) | ✅ Yes (API-based) |
| **Timeline View** | ✅ Yes | ✅ Yes |
| **Token Savings** | 77% (via progressive disclosure) | ~10x (similar approach) |
| **Fact Persistence** | Atomic facts never deleted | Observations can be removed |
| **Web UI** | ✅ Simple viewer | ✅ Real-time stream |
| **Setup Complexity** | Low (Python + scikit-learn) | Medium (Bun + Claude Code plugin) |

**When to use Memex:**
- You want file-based transparency
- You use multiple AI platforms
- You prefer Python over TypeScript/Bun
- You want explicit control over memory structure

**When to use Claude-Mem:**
- You only use Claude Code
- You prefer MCP integration
- You want the official Anthropic solution

See [docs/CLAUDE_MEM_COMPARISON.md](docs/CLAUDE_MEM_COMPARISON.md) for detailed analysis.

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running in 5 minutes
- **[Architecture](docs/ARCHITECTURE.md)** - Deep dive into the three-tier design
- **[Claude-Mem Comparison](docs/CLAUDE_MEM_COMPARISON.md)** - Detailed feature comparison

## 🎨 Examples

See the [examples/](examples/) directory for sample memory structures:

- `examples/basic/` - Minimal setup for personal assistant
- `examples/agent/` - Full setup for autonomous agent
- `examples/integration/` - Clawdbot integration example

## 🤝 Contributing

Contributions welcome! This project is MIT licensed.

**To contribute:**
1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Inspired by [claude-mem](https://github.com/anthropics/claude-mem) (Anthropic's official memory system)
- Built with ❤️ by [gabubu-dev](https://github.com/gabubu-dev)
- Tested with [Clawdbot](https://github.com/cyanheads/clawdbot) and Claude Code

---

**Tagline:** *Memex: Persistent memory for AI agents. Three-tier architecture. Platform-agnostic. File-based transparency.*

**Made for humans and agents alike.** 🤖🤝👤
