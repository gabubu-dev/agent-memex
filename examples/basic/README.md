# Basic Setup Example

Minimal Memex setup for a personal assistant.

## Structure

```
workspace/
├── memory/
│   └── 2026-01-30.md           # Daily notes
├── MEMORY.md                    # Long-term wisdom
├── tools/
│   ├── memory-search-simple.py
│   ├── memory-timeline.py
│   ├── memory-compress.py
│   └── index.pkl               # Search index (auto-generated)
```

## Sample Files

### memory/2026-01-30.md
```markdown
# 2026-01-30

## Morning

### 09:00 - Started using Memex
- Installed the memory system
- Learning the three-tier architecture
- Goal: Build persistent agent memory

### 10:30 - First search test
- Built search index
- Tested progressive disclosure
- Works great! 77% token savings

## Afternoon

### 14:00 - Integration planning
- Decided to use heartbeat for auto-indexing
- Will compress daily files weekly
- Action: Set up cron for compression
```

### MEMORY.md
```markdown
# Long-Term Memory

## Core Insights

### On Memory Systems
- File-based beats databases for transparency
- Progressive disclosure saves ~77% tokens
- Index → Timeline → Full is the right workflow

## Preferences

### Communication
- Direct and concise
- Examples over long explanations

### Workflow
- Test before committing
- Document as you build
```

## Usage

```bash
# Build index
python tools/memory-search-simple.py --index

# Search
python tools/memory-search-simple.py "memory system"

# Progressive disclosure
python tools/memory-search-simple.py "Memex" --format index
```

## Next Steps

1. Add daily notes regularly
2. Update MEMORY.md with learnings
3. Run weekly compression
