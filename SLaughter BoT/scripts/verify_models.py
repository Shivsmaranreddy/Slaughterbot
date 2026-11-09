import sys, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build.integration.registry import status
if __name__=='__main__':
    results=status(); print(json.dumps(results,indent=2))
    sys.exit(1 if any(r['status']=='INVALID' for r in results) else 0)
