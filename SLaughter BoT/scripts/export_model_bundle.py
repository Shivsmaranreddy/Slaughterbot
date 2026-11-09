"""Package a verified model for download/handoff. Does not convert model formats."""
import argparse, shutil, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build.integration.common import ROOT
from build.integration.registry import verify

def export(model_id):
    record=verify(model_id)
    if record['status']!='TRAINED_EXPERIMENTAL':
        raise ValueError('Train and evaluate this model before export')
    folder=Path(record['folder'])
    destination=ROOT/'output/exported_models'/model_id
    destination.parent.mkdir(parents=True,exist_ok=True)
    return Path(shutil.make_archive(str(destination),'zip',root_dir=folder.parent,base_dir=folder.name))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('model_id'); args=parser.parse_args()
    print(export(args.model_id))
