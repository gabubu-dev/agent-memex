#!/usr/bin/env python3
"""
Memory Timeline Tool
Inspired by Claude-Mem's timeline feature - show chronological context around a memory

Usage:
    python memory-timeline.py --query "Moltbook"
    python memory-timeline.py --date 2026-01-30
    python memory-timeline.py --id mem-abc123 --before 48 --after 24
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Import search function using importlib (handles hyphenated filenames)
import os
import sys
import importlib.util

# Load memory-search-simple module
SCRIPT_DIR = Path(__file__).parent.absolute()
search_module_path = SCRIPT_DIR / "memory-search-simple.py"

if not search_module_path.exists():
    print(f"⚠️  memory-search-simple.py not found in {SCRIPT_DIR}", file=sys.stderr)
    sys.exit(1)

spec = importlib.util.spec_from_file_location("memory_search_simple", search_module_path)
memory_search_simple = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_search_simple)

SimpleMemorySearcher = memory_search_simple.SimpleMemorySearcher

def get_timeline(memory_id=None, date=None, query=None, hours_before=24, hours_after=24):
    """
    Get chronological context around a specific point in time.
    
    Args:
        memory_id: ID of a specific memory (mem-abc123...)
        date: ISO date string (YYYY-MM-DD)
        query: Search query to find the anchor point
        hours_before: How many hours before to show
        hours_after: How many hours after to show
    """
    
    # Find anchor point
    anchor_time = None
    anchor_context = None
    
    searcher = SimpleMemorySearcher()
    
    if memory_id:
        # Search by ID
        clean_id = memory_id.replace('mem-', '')
        if not searcher.indexer.load_index():
            print("❌ No index found. Run: python memory-search-simple.py --index", file=sys.stderr)
            return {}
        
        for entry in searcher.indexer.entries:
            if entry.id == clean_id:
                anchor_context = {
                    'content': entry.content,
                    'metadata': {
                        'source': entry.source,
                        'timestamp': entry.timestamp
                    }
                }
                if entry.timestamp and len(entry.timestamp) == 10:  # YYYY-MM-DD
                    try:
                        anchor_time = datetime.strptime(entry.timestamp, '%Y-%m-%d')
                    except:
                        pass
                break
    
    elif date:
        try:
            anchor_time = datetime.fromisoformat(date)
        except ValueError:
            print(f"❌ Invalid date format: {date}. Use YYYY-MM-DD", file=sys.stderr)
            return {}
    
    elif query:
        results = searcher.search(query, limit=1)
        if results:
            anchor_context = results[0]
            timestamp = results[0].get('metadata', {}).get('timestamp', '')
            if timestamp and len(timestamp) == 10:
                try:
                    anchor_time = datetime.strptime(timestamp, '%Y-%m-%d')
                except:
                    pass
    
    if not anchor_time:
        print("❌ Could not determine anchor point", file=sys.stderr)
        print("💡 Try: --date YYYY-MM-DD or --query 'search term'", file=sys.stderr)
        return {}
    
    # Calculate time window
    start_date = (anchor_time - timedelta(hours=hours_before)).strftime('%Y-%m-%d')
    end_date = (anchor_time + timedelta(hours=hours_after)).strftime('%Y-%m-%d')
    
    # Gather memories in time window
    timeline_events = []
    
    # Daily notes
    memory_dir = Path(os.getenv('MEMEX_WORKSPACE', Path.cwd())) / 'memory'
    if memory_dir.exists():
        for md_file in sorted(memory_dir.glob('*.md')):
            if md_file.stem.count('-') == 2:  # YYYY-MM-DD format
                file_date = md_file.stem
                if start_date <= file_date <= end_date:
                    with open(md_file, 'r') as f:
                        content = f.read()
                        # Extract headings as events
                        for line in content.split('\n'):
                            if line.startswith('##'):
                                timeline_events.append({
                                    'date': file_date,
                                    'type': 'daily_note',
                                    'event': line.strip('# '),
                                    'file': str(md_file)
                                })
    
    # Knowledge graph updates (check modification times)
    kg_dir = Path.home() / 'life' / 'areas'
    if kg_dir.exists():
        for items_file in kg_dir.rglob('items.json'):
            mtime = datetime.fromtimestamp(items_file.stat().st_mtime)
            if anchor_time - timedelta(hours=hours_before) <= mtime <= anchor_time + timedelta(hours=hours_after):
                try:
                    with open(items_file, 'r') as f:
                        items = json.load(f)
                        for item in items[-5:]:  # Last 5 items
                            timeline_events.append({
                                'date': item.get('timestamp', ''),
                                'type': 'knowledge_graph',
                                'event': item.get('fact', ''),
                                'file': str(items_file),
                                'entity': items_file.parent.name
                            })
                except:
                    pass
    
    # Sort by date (handle both string dates and unix timestamps)
    def sort_key(event):
        date = event.get('date', '')
        if isinstance(date, int):
            return str(date)  # Unix timestamp as string
        return date or ''
    
    timeline_events.sort(key=sort_key)
    
    return {
        'anchor': anchor_context,
        'time_window': {
            'start': start_date,
            'end': end_date,
            'hours_before': hours_before,
            'hours_after': hours_after
        },
        'events': timeline_events
    }

def main():
    parser = argparse.ArgumentParser(description='Show timeline context around a memory')
    parser.add_argument('--id', help='Memory ID (mem-abc123...)')
    parser.add_argument('--date', help='ISO date (YYYY-MM-DD)')
    parser.add_argument('--query', help='Search query to find anchor point')
    parser.add_argument('--before', type=int, default=24, help='Hours before (default: 24)')
    parser.add_argument('--after', type=int, default=24, help='Hours after (default: 24)')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    if not (args.id or args.date or args.query):
        parser.error('Provide --id, --date, or --query')
    
    timeline = get_timeline(
        memory_id=args.id,
        date=args.date,
        query=args.query,
        hours_before=args.before,
        hours_after=args.after
    )
    
    if args.json:
        print(json.dumps(timeline, indent=2))
    else:
        # Human-readable output
        tw = timeline.get('time_window', {})
        events = timeline.get('events', [])
        
        print("\n" + "=" * 70)
        print(f"📅  TIMELINE: {tw.get('start', '')} → {tw.get('end', '')}")
        print(f"    Window: {tw.get('hours_before', 0)}h before, {tw.get('hours_after', 0)}h after")
        print("=" * 70)
        
        if timeline.get('anchor'):
            anchor = timeline['anchor']
            preview = anchor.get('content', '')[:120].replace('\n', ' ')
            print(f"\n🎯  ANCHOR POINT:")
            print(f"    {preview}...")
            print()
        
        if not events:
            print("\n⚠️  No events found in this time window\n")
            return
        
        print(f"\n📊  {len(events)} EVENTS:\n")
        
        current_date = None
        for event in events:
            event_date = event.get('date', '')
            
            # Print date header when it changes
            if event_date != current_date:
                if current_date is not None:
                    print()  # Blank line between days
                print(f"  ▸ {event_date}")
                current_date = event_date
            
            icon = '  📝' if event['type'] == 'daily_note' else '  🧠'
            event_text = event.get('event', '')[:70]
            entity_info = f" [{event['entity']}]" if 'entity' in event else ""
            
            print(f"{icon} {event_text}{entity_info}")
        
        print("\n" + "=" * 70 + "\n")

if __name__ == '__main__':
    main()
