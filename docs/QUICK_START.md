# Memex Quick Start Guide

Get up and running with Memex in 5 minutes.

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/gabubu-dev/agent-memex.git
cd agent-memex
```

### 2. Run Setup Script

```bash
bash scripts/setup.sh
```

This will:
- Install Python dependencies (scikit-learn)
- Create memory directory structure
- Build initial search index
- Run test query

### 3. Verify Installation

```bash
python tools/memory-search-simple.py --help
```

You should see the help text. If you get errors, see Troubleshooting below.

## Basic Usage

### Create Your First Memory

1. Create a daily note:
```bash
mkdir -p memory
cat > memory/$(date +%Y-%m-%d).md << 'EOF'
# $(date +%Y-%m-%d)

## Morning

### 09:00 - Started using Memex
- Installed the memory system
- Learning the three-tier architecture
- Goal: Build persistent agent memory

### 10:00 - First knowledge graph entry
- Created entry for project "Memex"
- Added key facts about the system
EOF
```

2. Create a knowledge graph entry:
```bash
mkdir -p ~/life/areas/projects/memex
cat > ~/life/areas/projects/memex/items.json << 'EOF'
[
  {
    "id": "memex-001",
    "fact": "Memex is a file-based memory system for AI agents",
    "timestamp": "$(date -Iseconds)",
    "category": "overview",
    "source": "documentation",
    "supersedes": null
  },
  {
    "id": "memex-002",
    "fact": "Uses three-tier architecture: facts, events, wisdom",
    "timestamp": "$(date -Iseconds)",
    "category": "architecture",
    "source": "documentation",
    "supersedes": null
  }
]
EOF
```

3. Create tacit knowledge:
```bash
cat > MEMORY.md << 'EOF'
# Long-Term Memory

## About Memex

### Core Insight
File-based memory beats databases for transparency and portability.

### Token Savings
Progressive disclosure (index → timeline → full) saves ~77% tokens.

## Preferences

### Search Workflow
1. Start with `--format index` to get IDs
2. Use timeline to see context
3. Load full details only for relevant items
EOF
```

### Build the Search Index

```bash
python tools/memory-search-simple.py --index
```

**Output:**
```
🔍 Indexing memories (TF-IDF mode)...
  📅 Daily notes: 5 entries
  🧠 Tacit knowledge: 3 entries
  🕸️ Knowledge graph: 2 entries
  🛠️ Tools/skills: 0 entries
✅ Indexed 10 memories
   Vocabulary size: 347
```

### Search Your Memories

**Simple search (full results):**
```bash
python tools/memory-search-simple.py "Memex architecture"
```

**Progressive disclosure (recommended):**
```bash
# Step 1: Get index
python tools/memory-search-simple.py "Memex" --format index --limit 10

# Output shows IDs like: abc123, def456, ghi789

# Step 2: Get full details for selected IDs
python tools/memory-search-simple.py --ids abc123,def456
```

### View Timeline

```bash
# Timeline around today
python tools/memory-timeline.py --date $(date +%Y-%m-%d)

# Timeline around a search result
python tools/memory-timeline.py --query "Memex"
```

### Compress Long Sessions

```bash
# Compress today's notes
python tools/memory-compress.py --file memory/$(date +%Y-%m-%d).md

# Interactive mode (recommended)
python tools/memory-compress.py --interactive
```

### Browse in Web UI

```bash
# Start web server
python tools/memory-web.py

# Open in browser
open http://localhost:8080
```

## The 3-Layer Workflow (Progressive Disclosure)

**Why?** Save ~77% tokens by filtering before loading full content.

### Scenario: "What have I learned about agent delegation?"

#### Step 1: Get Index (Cheap)
```bash
python tools/memory-search-simple.py "agent delegation" --format index --limit 10
```

**Output:**
```
📇 Index: 10 results (IDs only)

1. [🧠] Agent delegation requires clear protocols...
   ID: abc123
2. [📅] Implemented delegation handoff system...
   ID: def456
3. [🕸️] Multi-agent coordination patterns...
   ID: ghi789
```

**Cost:** ~1,000 tokens

#### Step 2: See Timeline (Medium)
```bash
python tools/memory-timeline.py --id mem-abc123 --before 48 --after 24
```

**Output:**
```
📅  TIMELINE: 2026-01-28 → 2026-01-31

🎯  ANCHOR POINT:
    Agent delegation requires clear protocols...

📊  8 EVENTS:

  ▸ 2026-01-28
  📝 Started researching agent delegation
  
  ▸ 2026-01-29
  📝 Designed handoff protocol
  🧠 Learned: State must be serializable
  
  ▸ 2026-01-30  ← ANCHOR
  📝 Implemented delegation system
```

**Cost:** ~3,000 tokens

#### Step 3: Load Full Details (Expensive)
```bash
python tools/memory-search-simple.py --ids abc123,ghi789
```

**Output:** Full content for just those 2 entries

**Cost:** ~2,000 tokens

**Total:** ~6,000 tokens vs. ~25,000 without progressive disclosure (76% savings!)

## Common Tasks

### Update Daily Notes

```bash
# Add to today's file
cat >> memory/$(date +%Y-%m-%d).md << 'EOF'

## Afternoon

### 14:00 - Learned something important
- Key insight here
- Action: Follow up tomorrow
EOF
```

### Add Knowledge Graph Fact

```bash
# Add to existing entity's items.json
# (You'd typically do this programmatically or via heartbeat)
```

### Weekly Review

```bash
# Compress last 7 days
python tools/memory-compress.py --recent 7

# Search compressed summaries
python tools/memory-search-simple.py "weekly summary"
```

### Rebuild Index After Changes

```bash
python tools/memory-search-simple.py --index
```

## Directory Structure

After setup, your workspace should look like:

```
agent-memex/
├── tools/
│   ├── memory-search-simple.py
│   ├── memory-timeline.py
│   ├── memory-compress.py
│   └── memory-web.py
├── memory/
│   ├── 2026-01-30.md
│   └── summaries/
│       └── 2026-01-30-compressed.json
├── ~/life/areas/
│   ├── people/
│   ├── projects/
│   │   └── memex/
│   │       ├── items.json
│   │       └── summary.md
│   └── companies/
├── MEMORY.md
├── AGENTS.md
└── TOOLS.md
```

## Filter Options

### By Layer

```bash
# Daily notes only
python tools/memory-search-simple.py "meeting" --layer daily

# Knowledge graph only
python tools/memory-search-simple.py "Alice" --layer knowledge_graph

# Tacit knowledge only
python tools/memory-search-simple.py "workflow" --layer tacit
```

### By Date

```bash
# Since Jan 28
python tools/memory-search-simple.py "bug fix" --since 2026-01-28

# Specific date range (use timeline)
python tools/memory-timeline.py --date 2026-01-30 --before 168 --after 0  # Last week
```

### By Entity

```bash
# All memories about Alice
python tools/memory-search-simple.py "status" --entity alice

# All about Memex project
python tools/memory-search-simple.py "" --entity memex
```

### Combined

```bash
# Daily notes about Alice since Jan 28
python tools/memory-search-simple.py "preferences" \
  --layer daily \
  --entity alice \
  --since 2026-01-28
```

## Integration with Your Agent

### Option 1: Direct Python Calls

```python
# In your agent code
import subprocess
import json

def search_memory(query, format='index', limit=10):
    """Search agent memory."""
    cmd = [
        'python', 'tools/memory-search-simple.py',
        query,
        '--format', format,
        '--limit', str(limit)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

# Use it
results = search_memory("deployment process", format='index')
print(results)
```

### Option 2: Shell Commands

```bash
# In AGENTS.md or heartbeat scripts
QUERY="action items"
python tools/memory-search-simple.py "$QUERY" --format index --limit 5
```

### Option 3: MCP Tool (Claude Code)

See [examples/integration/claude-code-mcp.ts](../examples/integration/claude-code-mcp.ts)

## Troubleshooting

### "No module named 'sklearn'"

```bash
pip install scikit-learn
```

### "No index found"

```bash
python tools/memory-search-simple.py --index
```

### Search returns no results

1. Check index is built:
```bash
python tools/memory-search-simple.py --index --force
```

2. Try broader queries:
```bash
# Too specific: "Memex three-tier architecture implementation"
# Better: "Memex architecture"
```

3. Check files exist:
```bash
ls -la memory/
ls -la ~/life/areas/
```

### Slow search

First search loads the index (~1s). Subsequent searches are fast (<100ms).

If consistently slow:
```bash
# Rebuild index
python tools/memory-search-simple.py --index --force
```

### Web viewer shows no results

1. Build index first:
```bash
python tools/memory-search-simple.py --index
```

2. Check memory files exist:
```bash
ls -la memory/
```

3. Try search via CLI first to debug:
```bash
python tools/memory-search-simple.py "test"
```

## Next Steps

1. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** for deep dive
2. **Read [CLAUDE_MEM_COMPARISON.md](CLAUDE_MEM_COMPARISON.md)** to understand trade-offs
3. **Explore [examples/](../examples/)** for integration patterns
4. **Customize** `AGENTS.md` and `TOOLS.md` for your setup

## Tips for Daily Use

### Morning Routine
```bash
# Catch up on recent events
python tools/memory-search-simple.py "" --layer daily --since $(date -d '2 days ago' +%Y-%m-%d)
```

### Before Conversations
```bash
# Load context about a person
python tools/memory-search-simple.py "Alice" --layer knowledge_graph
```

### After Learning Something New
```bash
# Rebuild index
python tools/memory-search-simple.py --index
```

### Weekly Review
```bash
# Compress old sessions
python tools/memory-compress.py --recent 7

# Review compressed summaries
python tools/memory-search-simple.py "summary"
```

---

**Questions?** Check the [README](../README.md) or open an issue on GitHub.

**Happy memory building!** 🧠✨
