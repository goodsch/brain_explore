#!/usr/bin/env python3
"""
Manage automated Calibre book ingestion services.

Provides easy commands to start/stop/status automated ingestion.
"""

import argparse
import subprocess
import sys
import signal
import psutil
from pathlib import Path

def find_process_by_script(script_name):
    """Find running process by script name."""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and any(script_name in cmd for cmd in proc.info['cmdline']):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def start_daemon():
    """Start the auto-ingest daemon."""
    proc = find_process_by_script('auto_ingest_daemon.py')
    if proc:
        print(f"Auto-ingest daemon already running (PID: {proc.pid})")
        return
    
    print("Starting auto-ingest daemon...")
    subprocess.Popen([
        sys.executable, 'scripts/auto_ingest_daemon.py'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("Auto-ingest daemon started in background")

def start_watcher():
    """Start the file watcher."""
    proc = find_process_by_script('calibre_watcher.py')
    if proc:
        print(f"File watcher already running (PID: {proc.pid})")
        return
    
    print("Starting Calibre file watcher...")
    subprocess.Popen([
        sys.executable, 'scripts/calibre_watcher.py'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("File watcher started in background")

def stop_services():
    """Stop all ingestion services."""
    stopped = 0
    
    for script_name in ['auto_ingest_daemon.py', 'calibre_watcher.py']:
        proc = find_process_by_script(script_name)
        if proc:
            print(f"Stopping {script_name} (PID: {proc.pid})")
            proc.terminate()
            stopped += 1
    
    if stopped == 0:
        print("No ingestion services running")
    else:
        print(f"Stopped {stopped} service(s)")

def status():
    """Show status of ingestion services."""
    services = [
        ('Auto-ingest daemon', 'auto_ingest_daemon.py'),
        ('File watcher', 'calibre_watcher.py')
    ]
    
    print("Ingestion Services Status:")
    print("-" * 40)
    
    for name, script in services:
        proc = find_process_by_script(script)
        if proc:
            print(f"✅ {name}: Running (PID: {proc.pid})")
        else:
            print(f"❌ {name}: Not running")
    
    print("\nLog files:")
    print(f"  Auto-ingest: logs/auto_ingest.log")
    print(f"  File watcher: logs/calibre_watcher.log")

def process_now():
    """Process books immediately."""
    print("Processing books now...")
    result = subprocess.run([
        sys.executable, 'scripts/auto_ingest_daemon.py', '--once'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Processing complete")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ Processing failed")
        if result.stderr:
            print(result.stderr)

def main():
    parser = argparse.ArgumentParser(description="Manage Calibre ingestion services")
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    subparsers.add_parser('start', help='Start both daemon and watcher')
    subparsers.add_parser('stop', help='Stop all services')
    subparsers.add_parser('status', help='Show service status')
    subparsers.add_parser('restart', help='Restart all services')
    subparsers.add_parser('now', help='Process books immediately')
    
    # Individual service commands
    subparsers.add_parser('start-daemon', help='Start auto-ingest daemon only')
    subparsers.add_parser('start-watcher', help='Start file watcher only')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        start_daemon()
        start_watcher()
    elif args.command == 'start-daemon':
        start_daemon()
    elif args.command == 'start-watcher':
        start_watcher()
    elif args.command == 'stop':
        stop_services()
    elif args.command == 'status':
        status()
    elif args.command == 'restart':
        stop_services()
        import time
        time.sleep(2)
        start_daemon()
        start_watcher()
    elif args.command == 'now':
        process_now()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()