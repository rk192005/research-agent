#!/usr/bin/env python3
"""
Batch runner — watches a CSV queue and processes pending topics.
Local equivalent of Make.com's scheduled trigger. Free edition.

Usage:
    python batch_runner.py                         # Process all pending
    python batch_runner.py --watch                 # Poll every 15 min
    python batch_runner.py --watch --interval 300  # Poll every 5 min
"""

import argparse
import csv
import time
import sys
from datetime import datetime
from pathlib import Path

from research_agent import run as run_research

QUEUE_FILE = Path(__file__).parent / "research_queue.csv"


def load_queue() -> list[dict]:
    """Load research topics from the CSV queue."""
    if not QUEUE_FILE.exists():
        print(f"❌ Queue file not found: {QUEUE_FILE}")
        print(f"   Copy research_queue_template.csv → research_queue.csv first:")
        print(f"   cp research_queue_template.csv research_queue.csv")
        sys.exit(1)

    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save_queue(rows: list[dict]):
    """Write updated queue back to CSV."""
    if not rows:
        return
    fieldnames = rows[0].keys()
    with open(QUEUE_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_pending():
    """Find and process all pending research topics."""
    rows = load_queue()
    pending = [(i, r) for i, r in enumerate(rows) if r.get("status", "").strip() == "pending"]

    if not pending:
        print("✅ No pending topics. Queue is clear.")
        return 0

    print(f"📋 Found {len(pending)} pending topic(s)\n")
    processed = 0

    for idx, row in pending:
        topic = row["topic"].strip()
        depth = row.get("depth", "deep").strip() or "deep"

        # Mark running
        rows[idx]["status"] = "running"
        save_queue(rows)

        try:
            filepath = run_research(topic, depth)
            rows[idx]["status"] = "done"
            rows[idx]["report_link"] = str(filepath)
            rows[idx]["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            processed += 1
        except SystemExit:
            rows[idx]["status"] = "failed"
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            rows[idx]["status"] = "failed"
        finally:
            save_queue(rows)

    print(f"\n{'='*60}")
    print(f"📊 Batch complete: {processed}/{len(pending)} topics processed")
    print(f"{'='*60}")
    return processed


def watch_mode(interval: int):
    """Poll the queue on a loop — local equivalent of Make.com's scheduler."""
    print(f"👁️  Watch mode — checking every {interval}s (Ctrl+C to stop)\n")
    try:
        while True:
            now = datetime.now().strftime("%H:%M:%S")
            print(f"\n⏰ [{now}] Checking queue...")
            process_pending()
            print(f"💤 Next check in {interval}s...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n\n🛑 Watch mode stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch research agent runner (free edition)")
    parser.add_argument("--watch", action="store_true", help="Run continuously on a timer")
    parser.add_argument("--interval", type=int, default=900, help="Seconds between checks (default: 900 = 15min)")
    args = parser.parse_args()

    if args.watch:
        watch_mode(args.interval)
    else:
        process_pending()
