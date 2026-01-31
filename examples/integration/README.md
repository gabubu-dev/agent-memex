# Integration Examples

How to integrate Memex with various platforms.

## Clawdbot Integration

### AGENTS.md Snippet
```markdown
## Memory System

Before doing anything:
1. Read `memory/$(date +%Y-%m-%d).md` (today + yesterday)
2. Read `MEMORY.md` for long-term context

### Heartbeat Tasks
```bash
# Check if index needs update
if [ memory/*.md -nt tools/index.pkl ]; then
    python tools/memory-search-simple.py --index
fi

# Auto-compress long sessions
for file in memory/$(date +%Y-%m-%d).md; do
    if [ $(wc -c < "$file") -gt 20000 ]; then
        python tools/memory-compress.py --file "$file"
    fi
done
```

## Claude Code MCP Integration

### memory-tool.ts
```typescript
import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export const memorySearchTool: Tool = {
  name: 'search_memory',
  description: 'Search agent memory with progressive disclosure',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Search query' },
      format: { 
        type: 'string', 
        enum: ['index', 'full'], 
        default: 'index',
        description: 'Output format (index for previews, full for details)'
      },
      layer: {
        type: 'string',
        enum: ['daily', 'tacit', 'knowledge_graph', 'tools'],
        description: 'Filter by memory layer'
      },
      ids: {
        type: 'string',
        description: 'Comma-separated IDs for full details'
      }
    },
    required: ['query']
  }
};

export async function handleMemorySearch(args: any): Promise<string> {
  const { query, format = 'index', layer, ids } = args;
  
  let cmd = `python tools/memory-search-simple.py "${query}" --format ${format}`;
  if (layer) cmd += ` --layer ${layer}`;
  if (ids) cmd += ` --ids ${ids}`;
  
  const { stdout } = await execAsync(cmd);
  return stdout;
}

export const memoryTimelineTool: Tool = {
  name: 'memory_timeline',
  description: 'Show chronological context around a memory',
  inputSchema: {
    type: 'object',
    properties: {
      query: { type: 'string', description: 'Search query to find anchor point' },
      id: { type: 'string', description: 'Memory ID (mem-abc123)' },
      date: { type: 'string', description: 'ISO date (YYYY-MM-DD)' },
      before: { type: 'number', default: 24, description: 'Hours before' },
      after: { type: 'number', default: 24, description: 'Hours after' }
    }
  }
};

export async function handleMemoryTimeline(args: any): Promise<string> {
  const { query, id, date, before = 24, after = 24 } = args;
  
  let cmd = 'python tools/memory-timeline.py';
  if (query) cmd += ` --query "${query}"`;
  if (id) cmd += ` --id ${id}`;
  if (date) cmd += ` --date ${date}`;
  cmd += ` --before ${before} --after ${after}`;
  
  const { stdout } = await execAsync(cmd);
  return stdout;
}
```

## Python Agent Integration

### agent.py
```python
import subprocess
import json
from pathlib import Path

class MemoryInterface:
    """Interface to Memex memory system."""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.tools_dir = workspace_dir / 'tools'
    
    def search(self, query: str, format: str = 'index', limit: int = 10, 
               layer: str = None) -> list:
        """Search memory with progressive disclosure."""
        cmd = [
            'python', str(self.tools_dir / 'memory-search-simple.py'),
            query,
            '--format', format,
            '--limit', str(limit)
        ]
        if layer:
            cmd.extend(['--layer', layer])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return self._parse_results(result.stdout)
    
    def get_by_ids(self, ids: list[str]) -> list:
        """Get full details for specific memory IDs."""
        cmd = [
            'python', str(self.tools_dir / 'memory-search-simple.py'),
            '--ids', ','.join(ids)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return self._parse_results(result.stdout)
    
    def timeline(self, query: str = None, date: str = None, 
                 before: int = 24, after: int = 24) -> dict:
        """Get timeline context around a memory."""
        cmd = ['python', str(self.tools_dir / 'memory-timeline.py')]
        if query:
            cmd.extend(['--query', query])
        if date:
            cmd.extend(['--date', date])
        cmd.extend(['--before', str(before), '--after', str(after), '--json'])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return json.loads(result.stdout)
    
    def rebuild_index(self):
        """Rebuild search index."""
        cmd = [
            'python', str(self.tools_dir / 'memory-search-simple.py'),
            '--index'
        ]
        subprocess.run(cmd)
    
    def _parse_results(self, output: str) -> list:
        """Parse CLI output into structured results."""
        # Simple parser - you'd make this more robust
        results = []
        for line in output.split('\n'):
            if line.strip().startswith('ID:'):
                results.append({'id': line.split(':')[1].strip()})
        return results

# Usage example
memory = MemoryInterface(Path.cwd())

# Progressive disclosure workflow
index_results = memory.search("deployment process", format='index', limit=10)
print(f"Found {len(index_results)} relevant memories")

# Get timeline context
timeline = memory.timeline(query="deployment process", before=48, after=24)
print(f"Timeline has {len(timeline.get('events', []))} events")

# Get full details for selected IDs
full_details = memory.get_by_ids(['abc123', 'def456'])
print(f"Loaded {len(full_details)} full memories")
```

## API Server (Optional)

### server.py
```python
from flask import Flask, request, jsonify
from pathlib import Path
import subprocess

app = Flask(__name__)
WORKSPACE = Path.cwd()

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    format = request.args.get('format', 'index')
    layer = request.args.get('layer')
    
    cmd = ['python', 'tools/memory-search-simple.py', query, '--format', format]
    if layer:
        cmd.extend(['--layer', layer])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return jsonify({'results': result.stdout})

@app.route('/api/timeline', methods=['GET'])
def timeline():
    query = request.args.get('q')
    date = request.args.get('date')
    
    cmd = ['python', 'tools/memory-timeline.py', '--json']
    if query:
        cmd.extend(['--query', query])
    if date:
        cmd.extend(['--date', date])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
    app.run(port=5000)
```

## Environment Variables

All tools support configuration via environment variables:

```bash
# Set workspace directory (default: current directory)
export MEMEX_WORKSPACE=/path/to/workspace

# Use in scripts
python tools/memory-search-simple.py "query"
```

## Tips

1. **Always use progressive disclosure** - Start with `--format index`
2. **Rebuild index after changes** - `--index` flag
3. **Use timeline for context** - Understand what happened around an event
4. **Compress regularly** - Keep daily files manageable
5. **Automate with heartbeats** - Don't manually manage indexing
