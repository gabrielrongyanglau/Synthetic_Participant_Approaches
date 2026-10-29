"""One-command local preview. No secrets are needed for the fictional demonstration."""
from pathlib import Path
import os,subprocess,sys,venv
ROOT=Path(__file__).resolve().parent
if sys.version_info[:2] not in ((3,12),(3,13)):raise SystemExit('Install Python 3.12 or 3.13, then rerun this command.')
home=ROOT/'.venv';exe=home/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
if not exe.exists():venv.create(home,with_pip=True)
marker=home/'dependencies.txt';signature=(ROOT/'requirements.txt').read_text()
if not marker.exists() or marker.read_text()!=signature:
    subprocess.run([str(exe),'-m','pip','install','--only-binary=:all:','-r',str(ROOT/'requirements.txt')],check=True);marker.write_text(signature)
print('Open http://127.0.0.1:8000 in your browser. Keep this terminal open. Ctrl+C stops the app.',flush=True)
subprocess.run([str(exe),'-m','uvicorn','app:app','--host','127.0.0.1','--port','8000'],cwd=ROOT,check=True)
