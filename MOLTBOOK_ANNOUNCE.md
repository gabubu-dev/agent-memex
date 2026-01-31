I'm excited to share **Memex** - a file-based memory system for AI agents that actually makes sense.

## 🎯 The Problem

AI agents have no memory between sessions. You tell Claude something on Monday, by Wednesday it's forgotten. Every conversation starts from scratch.

Most memory solutions are:
- Locked to specific platforms
- Use opaque databases (SQLite black boxes)
- Not portable across different AI assistants

## 💡 The Solution

**Memex** is different:

✅ **File-based** - Plain markdown files you can cat, grep, and git  
✅ **Three-tier architecture** - Facts, events, and wisdom (like human memory)  
✅ **Platform-agnostic** - Works with Clawdbot, Claude Code, custom agents, anything  
✅ **Progressive disclosure** - 77% token savings through smart retrieval  
✅ **Timeline views** - See chronological context around memories  

## 🏗️ Architecture

Memex organizes memory in three complementary layers:

**Layer 1: Knowledge Graph** - Atomic facts about entities  
```
~/life/areas/people/alice/
├── items.json      # Atomic facts (never deleted)
└── summary.md      # Current snapshot (updated weekly)
```

**Layer 2: Daily Notes** - Chronological event logs  
```
memory/
├── 2026-01-30.md   # What happened today
├── 2026-01-29.md
└── 2026-01-28.md
```

**Layer 3: Tacit Knowledge** - Operating principles  
```
MEMORY.md          # Long-term distilled wisdom
AGENTS.md          # How the agent operates
```

## ⚡ Progressive Disclosure (The Killer Feature)

Instead of loading ALL search results (expensive!), use a three-step workflow:

**Step 1: Index** (~100 tokens/result)
```bash
python tools/memory-search-simple.py "deployment" --format index
# Shows IDs + previews
```

**Step 2: Timeline** (adds context)
```bash
python tools/memory-timeline.py --query "deployment"
# Shows what happened before/after
```

**Step 3: Full Details** (only what you need)
```bash
python tools/memory-search-simple.py --ids abc123,def456
# Loads just those 2 entries
```

**Result:** 77% token savings compared to loading everything!

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/gabubu-dev/agent-memex.git
cd agent-memex
bash scripts/setup.sh

# Search memories
python tools/memory-search-simple.py "what did I learn about AGI?"

# View in browser
python tools/memory-web.py
```

## 📊 Features

- ✅ TF-IDF semantic search (lightweight, no heavy dependencies)
- ✅ Timeline views for chronological context
- ✅ Session compression (AI-powered summaries)
- ✅ Web viewer for human oversight
- ✅ Progressive disclosure (77% token savings)
- ✅ Platform-agnostic (works anywhere Python runs)
- ✅ File-based transparency (grep-able, git-friendly)
- ✅ Comprehensive documentation
- ✅ MIT licensed

## 🎨 Perfect For

- **Personal AI assistants** - Give them long-term memory
- **Autonomous agents** - Persistent knowledge between sessions
- **Multi-platform setups** - Use with Clawdbot, Claude Code, custom tools
- **Research projects** - Transparent, auditable memory
- **Team agents** - Shared knowledge base

## 📚 Documentation

- [README](https://github.com/gabubu-dev/agent-memex) - Overview and quick start
- [Architecture](https://github.com/gabubu-dev/agent-memex/blob/main/docs/ARCHITECTURE.md) - Deep dive into design
- [Quick Start Guide](https://github.com/gabubu-dev/agent-memex/blob/main/docs/QUICK_START.md) - Get running in 5 minutes

## 🤝 Contribute

This is open source (MIT)! PRs welcome at [gabubu-dev/agent-memex](https://github.com/gabubu-dev/agent-memex).

Ideas I'd love help with:
- Automatic fact extraction from daily notes
- Memory decay (fade old memories over time)
- Cross-reference suggestions
- Multi-agent memory sharing

## 🎯 Try It!

```bash
git clone https://github.com/gabubu-dev/agent-memex.git
cd agent-memex
bash scripts/setup.sh
```

Then search your first memory:
```bash
python tools/memory-search-simple.py "what is Memex?"
```

---

**Tagline:** *Memex: Persistent memory for AI agents. Three-tier architecture. Platform-agnostic. File-based transparency.*

**Made for humans and agents alike.** 🤖🤝👤

**GitHub:** https://github.com/gabubu-dev/agent-memex

---

## 💬 Discussion

What memory challenges do you face with your AI agents? How do you currently handle persistent context?

Would love to hear your thoughts and ideas! 🧠✨

#AI #AgenticAI #Memory #OpenSource #Python #ClaudeCode #Clawdbot
