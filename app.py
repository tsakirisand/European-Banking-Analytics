import os
import sys

# Ensure repository root is in python path
repo_root = os.path.dirname(os.path.abspath(__file__))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Execute main dashboard entrypoint
dashboard_app = os.path.join(repo_root, "dashboard", "app.py")
with open(dashboard_app, "r", encoding="utf-8") as f:
    code = compile(f.read(), dashboard_app, 'exec')
    exec(code, {'__file__': dashboard_app, '__name__': '__main__'})
