import os
import re

# The mapping of where modules used to be -> where they are now
MODULE_MAP = {
    # Subsystems moved to backend/
    'api': 'backend.api',
    'auth': 'backend.auth',
    'economics': 'backend.economics',
    'governance': 'backend.governance',
    'reputation': 'backend.reputation',
    'settlement': 'backend.settlement',
    'middleware': 'backend.middleware',
    'ops': 'backend.ops',
    
    # Core files moved to backend/core/
    'models': 'backend.core.models',
    'verifier': 'backend.core.verifier',
    'proxy_client': 'backend.core.proxy_client',
    'pulse': 'backend.core.pulse',
    'migrate_db': 'backend.core.migrate_db',
    
    # Hardware moved to hardware-node/
    'attest_node': 'hardware_node.attest_node',
    'hardware_heartbeat': 'hardware_node.hardware_heartbeat',
    'heartbeat_daemon': 'hardware_node.heartbeat_daemon',
    'consensus': 'hardware_node.consensus',
    'redundancy': 'hardware_node.redundancy',
}

def fix_imports(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    # 1. Fix "from X import Y" patterns
    for old_mod, new_mod in MODULE_MAP.items():
        pattern = fr'(^|\n)from {old_mod}(\.| )'
        replacement = fr'\1from {new_mod}\2'
        content = re.sub(pattern, replacement, content)

    # 2. Fix direct "import X" patterns
    for old_mod, new_mod in MODULE_MAP.items():
        if "." in new_mod:
            parent, child = new_mod.rsplit('.', 1)
            pattern = fr'(^|\n)import {old_mod}\s*$'
            replacement = fr'\1from {parent} import {child}'
            content = re.sub(pattern, replacement, content)
        else:
            pattern = fr'(^|\n)import {old_mod}\s*$'
            replacement = fr'\1import {new_mod}'
            content = re.sub(pattern, replacement, content)

    if content != original_content:
        print(f"🔧 Patching imports in: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    print("🚀 Starting Import Fixer...")
    dirs_to_scan = ['backend', 'hardware-node']
    
    for root_dir in dirs_to_scan:
        if not os.path.exists(root_dir):
            print(f"⚠️ Warning: Directory '{root_dir}' not found.")
            continue
            
        for root, _, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.py'):
                    fix_imports(os.path.join(root, file))
    
    if os.path.exists('backend/app.py'):
        fix_imports('backend/app.py')

    print("✅ Import patching complete.")

if __name__ == "__main__":
    main()