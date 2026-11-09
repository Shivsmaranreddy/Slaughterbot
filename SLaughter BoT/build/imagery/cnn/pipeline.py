"""MobileNetV3 transfer learning with explicit group-split manifest and held-out evaluation."""
from pathlib import Path
import argparse, copy, json
import numpy as np
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
from build.integration.common import ROOT, seed_all, finalize, read_json, sha256, write_json
from .data import validate_manifest

MEAN = [0.485,0.456,0.406]
STD = [0.229,0.224,0.225]

def transform(training=False):
    steps = [transforms.Resize((224,224))]
    if training:
        steps += [transforms.RandomHorizontalFlip()]
    return transforms.Compose(steps + [transforms.ToTensor(), transforms.Normalize(MEAN,STD)])

def network(n, pretrained=False):
    model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, n)
    return model

class Images(Dataset):
    def __init__(self, manifest, root, split, labels):
        self.rows = [s for s in manifest['samples'] if s['split']==split]
        self.root, self.labels, self.tf = Path(root), labels, transform(split=='train')
    def __len__(self): return len(self.rows)
    def __getitem__(self, i):
        row = self.rows[i]
        with Image.open(self.root / row['path']) as image:
            if image.width < 16 or image.height < 16:
                raise ValueError('Image too small')
            tensor = self.tf(image.convert('RGB'))
        return tensor, self.labels.index(row['label'])

def train(manifest_path, data_root, epochs=10, batch_size=16, seed=42, resume=None):
    seed_all(seed)
    m = validate_manifest(manifest_path,data_root)
    labels = sorted({s['label'] for s in m['samples'] if s['split']=='train'})
    if len(labels)<2 or any(s['label'] not in labels for s in m['samples']):
        raise ValueError('Need at least two train classes and matching evaluation labels')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    loaders = {s:DataLoader(Images(m,data_root,s,labels),batch_size=batch_size,shuffle=s=='train',num_workers=0) for s in ['train','val','test']}
    model = network(len(labels), pretrained=not bool(resume)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    best_loss, start, best = float('inf'), 0, None
    fingerprint = sha256(manifest_path)
    history = []
    if resume:
        c = torch.load(resume,map_location=device,weights_only=True)
        if c['dataset_sha256'] != fingerprint or c['labels'] != labels:
            raise ValueError('Resume dataset/classes mismatch')
        model.load_state_dict(c['model']); optimizer.load_state_dict(c['optimizer'])
        start, best_loss, best, history = c['epoch']+1,c['best_loss'],c['best'],c['history']
        torch.set_rng_state(c['rng'].cpu())
    for epoch in range(start,epochs):
        losses = {}
        for split in ['train','val']:
            model.train(split=='train'); total=0.; count=0
            for x,y in loaders[split]:
                x,y=x.to(device),y.to(device)
                with torch.set_grad_enabled(split=='train'):
                    loss=nn.functional.cross_entropy(model(x),y)
                    if split=='train':
                        optimizer.zero_grad(); loss.backward(); optimizer.step()
                total += loss.item()*len(y); count += len(y)
            losses[split] = total/count
        if losses['val'] < best_loss:
            best_loss=losses['val']; best=copy.deepcopy(model.state_dict())
        history.append({'epoch':epoch,**losses})
        checkpoint=ROOT/'output/checkpoints/visual_last.pt'; checkpoint.parent.mkdir(parents=True,exist_ok=True)
        torch.save({'model':model.state_dict(),'optimizer':optimizer.state_dict(),'epoch':epoch,
                    'labels':labels,'dataset_sha256':fingerprint,'best_loss':best_loss,'best':best,
                    'history':history,'rng':torch.get_rng_state()},checkpoint)
    if best is None:
        raise ValueError('No successful training epoch')
    model.load_state_dict(best); model.eval(); actual=[]; predicted=[]; confidences=[]
    with torch.no_grad():
        for x,y in loaders['test']:
            probs=model(x.to(device)).softmax(1).cpu()
            actual.extend(y.tolist()); predicted.extend(probs.argmax(1).tolist()); confidences.extend(probs.max(1).values.tolist())
    report=classification_report(actual,predicted,labels=list(range(len(labels))),target_names=labels,output_dict=True,zero_division=0)
    report['confusion_matrix']=confusion_matrix(actual,predicted,labels=list(range(len(labels)))).tolist()
    report['test_count']=len(actual); report['coverage_at_0.8']=float(np.mean(np.array(confidences)>=0.8))
    report['confidence_note']='Softmax confidence is uncalibrated; 0.8 is provisional, not a safety threshold.'
    folder=ROOT/'output/models/model_1_visual_cnn'; folder.mkdir(parents=True,exist_ok=True)
    artifact=folder/'weights.pt'; torch.save({'state_dict':{k:v.cpu() for k,v in best.items()},'labels':labels},artifact)
    finalize(folder,'model_1_visual_cnn',artifact,{'epochs':epochs,'seed':seed,'dataset_sha256':fingerprint,'history':history},report,{'size':[224,224],'mean':MEAN,'std':STD,'threshold':0.8},m['provenance'])
    write_json(ROOT/'output/experiment_logs/visual_history.json',history)
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(); ax.plot([r['train'] for r in history],label='train'); ax.plot([r['val'] for r in history],label='validation'); ax.legend(); ax.set(xlabel='Epoch',ylabel='Cross entropy')
    target=ROOT/'output/visualizations/visual_training.png'; target.parent.mkdir(parents=True,exist_ok=True); fig.savefig(target); plt.close(fig)
    return report

def predict(folder, image_path):
    c=torch.load(Path(folder)/'weights.pt',map_location='cpu',weights_only=True)
    model=network(len(c['labels'])); model.load_state_dict(c['state_dict']); model.eval()
    with Image.open(image_path) as image:
        if image.width<16 or image.height<16: raise ValueError('Image too small')
        x=transform()(image.convert('RGB')).unsqueeze(0)
    with torch.no_grad(): p=model(x).softmax(1)[0]
    confidence,index=p.max(0); confidence=float(confidence)
    return {'status':'EXPERIMENTAL' if confidence>=0.8 else 'ABSTAIN',
            'label':c['labels'][int(index)] if confidence>=0.8 else 'unknown',
            'confidence':confidence,'calibrated':False}

def saliency(folder, image_path, destination):
    # Input-gradient saliency is a limited explainability tool, not proof of causal features.
    c=torch.load(Path(folder)/'weights.pt',map_location='cpu',weights_only=True)
    model=network(len(c['labels'])); model.load_state_dict(c['state_dict']); model.eval()
    with Image.open(image_path) as im: x=transform()(im.convert('RGB')).unsqueeze(0).requires_grad_(True)
    logits=model(x); logits[0,logits.argmax(1)[0]].backward()
    heat=x.grad.abs().max(1).values[0].detach().numpy()
    import matplotlib.pyplot as plt
    plt.imsave(destination,heat,cmap='magma')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--manifest',required=True); p.add_argument('--data-root',required=True)
    p.add_argument('--epochs',type=int,default=10); p.add_argument('--resume'); a=p.parse_args()
    print(json.dumps(train(a.manifest,a.data_root,a.epochs,resume=a.resume),indent=2))
