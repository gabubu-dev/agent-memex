#!/bin/bash
# Memex Setup Script
# Sets up the memory system in your workspace

set -e  # Exit on error

echo "🧠 Memex Setup"
echo "=============================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install --quiet scikit-learn 2>&1 | grep -v "already satisfied" || true
echo "✓ scikit-learn installed"

# Create directory structure
echo ""
echo "📁 Creating directory structure..."

mkdir -p memory
mkdir -p memory/summaries
mkdir -p tools
echo "✓ Created memory/ and tools/ directories"

# Check for knowledge graph directory
if [ ! -d "$HOME/life/areas" ]; then
    echo "ℹ️  Knowledge graph directory not found"
    echo "   Creating ~/life/areas/ structure..."
    mkdir -p "$HOME/life/areas"/{people,companies,projects,skills,workflows}
    echo "✓ Created ~/life/areas/ structure"
fi

# Create initial files if they don't exist
if [ ! -f "MEMORY.md" ]; then
    cat > MEMORY.md << 'EOF'
# Long-Term Memory

## Core Insights

### On Memory Systems
- File-based memory provides transparency
- Progressive disclosure saves ~77% tokens
- Index → Timeline → Full is the optimal workflow

## Preferences

### Communication
- Direct and concise
- Code examples over long explanations

### Workflow
- Test before committing
- Document as you build
EOF
    echo "✓ Created MEMORY.md"
fi

if [ ! -f "AGENTS.md" ]; then
    cat > AGENTS.md << 'EOF'
# Agent Operating Manual

## Core Principles

1. **Read before you act** - Check memory for context
2. **Write it down** - No "mental notes", everything goes in files
3. **Progressive disclosure** - Start with index, drill down as needed

## Daily Routine

### On Startup
1. Read MEMORY.md for long-term context
2. Read today's memory file
3. Check for pending action items

### Memory Maintenance
- Rebuild index after major changes
- Compress long sessions weekly
- Update knowledge graph monthly
EOF
    echo "✓ Created AGENTS.md"
fi

# Create a sample daily note for today
TODAY=$(date +%Y-%m-%d)
if [ ! -f "memory/$TODAY.md" ]; then
    cat > "memory/$TODAY.md" << EOF
# $TODAY

## Setup

### $(date +%H:%M) - Installed Memex
- Ran setup script
- Created initial memory structure
- Ready to start building memory!

## Next Steps

- [ ] Read the documentation
- [ ] Try the search tools
- [ ] Set up heartbeat automation
EOF
    echo "✓ Created memory/$TODAY.md"
fi

# Build initial index
echo ""
echo "🔍 Building search index..."
if [ -f "tools/memory-search-simple.py" ]; then
    python3 tools/memory-search-simple.py --index
    echo "✓ Search index built"
else
    echo "⚠️  memory-search-simple.py not found in tools/"
    echo "   Copy it from the repo to tools/ directory"
fi

# Test search
echo ""
echo "🧪 Testing search..."
if [ -f "tools/memory-search-simple.py" ]; then
    echo ""
    python3 tools/memory-search-simple.py "Memex" --format index --limit 3
    echo ""
    echo "✓ Search test passed"
fi

# Summary
echo ""
echo "=============================================="
echo "✅ Memex setup complete!"
echo ""
echo "📚 Next steps:"
echo "   1. Read docs/QUICK_START.md"
echo "   2. Try: python tools/memory-search-simple.py \"your query\""
echo "   3. Add daily notes to memory/YYYY-MM-DD.md"
echo "   4. Build knowledge graph in ~/life/areas/"
echo ""
echo "💡 Pro tip: Use progressive disclosure to save tokens!"
echo "   python tools/memory-search-simple.py \"query\" --format index"
echo ""
echo "Happy memory building! 🧠✨"
