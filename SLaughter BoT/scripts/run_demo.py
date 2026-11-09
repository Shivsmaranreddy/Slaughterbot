"""Starts only when explicitly invoked by the user."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
if __name__=='__main__':
    import uvicorn
    uvicorn.run('build.backend.app:app',host='127.0.0.1',port=8000)
