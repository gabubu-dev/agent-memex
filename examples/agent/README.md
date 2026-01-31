# Agent Setup Example

Full Memex setup for an autonomous agent with knowledge graph and tacit knowledge.

## Structure

```
workspace/
├── memory/
│   ├── 2026-01-30.md
│   ├── 2026-01-29.md
│   └── summaries/
│       └── 2026-01-30-compressed.json
├── ~/life/areas/
│   ├── people/
│   │   └── alice/
│   │       ├── items.json
│   │       └── summary.md
│   └── projects/
│       └── memex/
│           ├── items.json
│           └── summary.md
├── MEMORY.md
├── AGENTS.md
├── HEARTBEAT.md
├── TOOLS.md
└── tools/
    ├── memory-search-simple.py
    ├── memory-timeline.py
    ├── memory-compress.py
    └── index.pkl
```

## Sample Files

### ~/life/areas/people/alice/items.json
```json
[
  {
    "id": "alice-001",
    "fact": "Alice is a senior engineer at Anthropic",
    "timestamp": "2026-01-30T10:30:00",
    "category": "employment",
    "source": "conversation",
    "supersedes": null
  },
  {
    "id": "alice-002",
    "fact": "Alice prefers async communication over meetings",
    "timestamp": "2026-01-30T14:20:00",
    "category": "preferences",
    "source": "observation",
    "supersedes": null
  }
]
```

### ~/life/areas/people/alice/summary.md
```markdown
# Alice

**Last updated:** 2026-01-30

## Overview
Alice is a senior engineer at Anthropic working on AI safety.

## Key Facts
- Employment: Senior Engineer at Anthropic (since 2024)
- Location: San Francisco
- Expertise: Python, AI safety, distributed systems

## Preferences
- Communication: Prefers async (Slack/email) over meetings
- Work style: Deep focus blocks, minimal interruptions

## Recent Interactions
- 2026-01-30: Discussed memory system architecture
- 2026-01-28: Code review on delegation protocol
```

### AGENTS.md
```markdown
# Agent Operating Manual

## Core Principles

1. **Read before you act** - Check memory/YYYY-MM-DD.md for context
2. **Write it down** - No "mental notes", everything goes in files
3. **Progressive disclosure** - Start with index, drill down as needed

## Daily Routine

### On Startup
1. Read MEMORY.md for long-term context
2. Read memory/YYYY-MM-DD.md (today + yesterday)
3. Check for pending action items

### During Sessions
1. Log important events to daily notes
2. Extract facts to knowledge graph (weekly)
3. Update MEMORY.md with lessons learned

### Heartbeat Tasks (Every 4 hours)
```bash
# Rebuild index if files changed
python tools/memory-search-simple.py --index

# Compress long sessions (>5000 tokens)
python tools/memory-compress.py --recent 1
```
```

### HEARTBEAT.md
```markdown
# Heartbeat Tasks

## Memory Maintenance

### Every 4 Hours
- [ ] Check if index needs rebuilding
- [ ] Compress daily files >5000 tokens

### Daily
- [ ] Review action items from memory search
- [ ] Update knowledge graph with new entities

### Weekly
- [ ] Compress all recent sessions
- [ ] Regenerate knowledge graph summaries
- [ ] Archive old daily notes
```

## Usage

```bash
# Full workflow
python tools/memory-search-simple.py --index
python tools/memory-search-simple.py "Alice preferences" --layer knowledge_graph
python tools/memory-timeline.py --query "Alice" --before 168 --after 0
python tools/memory-search-simple.py --ids abc123,def456
```

## Automation

### Cron Setup (Linux/macOS)
```bash
# Add to crontab: crontab -e
0 */4 * * * cd /path/to/workspace && python tools/memory-search-simple.py --index
0 2 * * 0 cd /path/to/workspace && python tools/memory-compress.py --recent 7
```

### Heartbeat Integration (Clawdbot)
See AGENTS.md for heartbeat tasks.
