"""Exploration only: no scientifically validated spoilage target is asserted."""
from pathlib import Path
import numpy as np
from scipy.io import wavfile
from scipy import signal

def analyze(path,destination):
    rate,data=wavfile.read(path)
    if data.ndim==2: data=data.astype(np.float64).mean(1)
    data=data.astype(np.float64)
    if rate<1000 or len(data)<256 or not np.isfinite(data).all(): raise ValueError('Invalid/short audio')
    peak=np.max(np.abs(data)); data=data/max(peak,1)
    filtered=signal.sosfilt(signal.butter(4,30,btype='highpass',fs=rate,output='sos'),data)
    f,t,s=signal.spectrogram(filtered,fs=rate)
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(2,1); axs[0].plot(np.arange(len(data))/rate,filtered); axs[0].set(xlabel='Seconds',ylabel='Amplitude')
    axs[1].pcolormesh(t,f,10*np.log10(s+1e-12),shading='auto'); axs[1].set(xlabel='Seconds',ylabel='Hz')
    fig.tight_layout(); fig.savefig(destination); plt.close(fig)
    return {'rms':float(np.sqrt(np.mean(filtered**2))),'duration_seconds':len(data)/rate,
            'classification':'NOT IMPLEMENTED: dataset and defensible target required'}
