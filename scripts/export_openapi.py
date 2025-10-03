#!/usr/bin/env python3
# scripts/export_openapi.py
import importlib
import json
import sys

def load_app(dotted):
    if ':' in dotted:
        module_name, attr = dotted.split(':', 1)
    else:
        module_name, attr = dotted, 'app'
    mod = importlib.import_module(module_name)
    return getattr(mod, attr)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: export_openapi.py <module:app> [output.json]")
        sys.exit(2)
    module = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "openapi.json"
    app = load_app(module)
    with open(out, "w") as f:
        json.dump(app.openapi(), f, indent=2)
    print(f"Wrote {out}")
