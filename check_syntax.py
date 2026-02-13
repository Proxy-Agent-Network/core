import compileall
import os
import sys
import re

def run_preflight():
    """
    Proxy Protocol Syntax Audit
    Target: Only .py files
    Ignores: .jsx, .html, .js, .md
    """
    print("🚀 Starting Proxy Protocol Syntax Audit...")
    print("-" * 40)
    
    # regex to specifically target Python files
    # This prevents the linter from choking on JSX or HTML files in the repo
    python_regex = re.compile(r'\.py$')
    
    # force=True: ensures it re-checks even if .pyc files exist
    # quiet=0: prints the filenames it is checking
    # rx: the regex filter applied to the directory scan
    success = compileall.compile_dir(
        '.', 
        force=True, 
        quiet=0, 
        rx=python_regex
    )
    
    print("-" * 40)
    if success:
        print("✅ PASS: All Python files are syntactically valid.")
        sys.exit(0)
    else:
        print("❌ FAIL: Syntax errors detected in Python files. Check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    run_preflight()