#!/usr/bin/env python3
"""
Simple web UI server for local development
Serves the HTML interface without Docker
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support"""
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_web_ui():
    """Start the web UI server"""
    print("🌐 Starting web UI server...")
    
    # Change to web-ui directory
    web_ui_dir = Path("web-ui")
    if not web_ui_dir.exists():
        print("❌ web-ui directory not found")
        return False
    
    os.chdir(web_ui_dir)
    
    # Start HTTP server
    port = 8081
    server = HTTPServer(('localhost', port), CORSHTTPRequestHandler)
    
    print(f"📍 Web UI available at: http://localhost:{port}")
    print("💡 To stop the web UI server, press Ctrl+C")
    print("")
    
    try:
        # Open browser
        webbrowser.open(f"http://localhost:{port}")
        
        # Start server
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Web UI server stopped by user")
        server.shutdown()
    except Exception as e:
        print(f"❌ Web UI server failed: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🌐 Qualcomm Linux RAG Q&A Service - Web UI")
    print("=" * 50)
    
    # Check if web-ui directory exists
    if not Path("web-ui").exists():
        print("❌ web-ui directory not found")
        print("   Make sure you're in the project root directory")
        sys.exit(1)
    
    # Start web UI
    start_web_ui()

if __name__ == "__main__":
    main() 