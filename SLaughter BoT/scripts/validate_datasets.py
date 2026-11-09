import sys, argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build.imagery.cnn.data import validate_manifest
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('manifest'); p.add_argument('data_root'); p.add_argument('--modality',default='image'); a=p.parse_args()
    m=validate_manifest(a.manifest,a.data_root,a.modality); print('Validated',len(m['samples']),'samples')
