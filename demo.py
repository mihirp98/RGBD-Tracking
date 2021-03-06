# %%
import matplotlib
import matplotlib.pyplot as plt
import os
import matplotlib.patches as patches
import numpy as np
import pickle as pkl
import cv2
from Dataloader import Dataloader
from src.Vision import Vision
from src.DepthTracker import DepthTracker
from tqdm import tqdm
import time
import gc
from random import random


# %%
def runPrediction(dt,dl,T,R,p=1):
    deltaT = 1/30.0
    bestP = []
    gtP = []
    W = []
    error=0
    lastIdx = 0
    start = time.time()
    c = np.random.choice([0,1],p=[p,1-p])
    for i in tqdm(range(dl.bboxes.shape[0])):
        scanFrame = False
        if i==0:
            scanFrame = True
            xyz = dl.getXYZ(i)
        else:
            if c == 1:
                xyz = dl.getXYZ(i)
            else:
                xyz = np.empty((480,640,3))
                xyz[:,:,:] = np.nan
        img = dl.getRGB(i)
        bbox,_ = dl.getBbox(i)
        bestParticle,idx = dt.updateMeasurements(img,xyz,bbox,T,R,deltaT,scanFrame)
        w = np.sum(dt.particleFilter.weights*dt.particleFilter.weights)
        W.append((1/w)/particleN)
        if bestParticle is not None:
            lastIdx = idx
            bestP.append(bestParticle)
        else:
            bestP.append(dt.particleFilter.particles[lastIdx])
            
        if np.all(bbox[0]>0) == True:
            gt_xyz = dl.getXYZ(i)
            u,v = dt.vision.getBBoxCenter(bbox[0])
            gt_origin = gt_xyz[u,v,:]
            error += np.linalg.norm(bestP[-1][:3]-gt_origin)
            gtP.append(gt_origin)
        else:
            gtP.append([None,None,None])
    end = time.time()
    deltaT = end-start
    return (bestP,gtP,W,error,deltaT)

T = np.array([0,0,0])
R = np.eye(3)
particleN = 100
particleCov = 0.001*np.diag([.01,.01,.01,.001,.001,.001])
dl = Dataloader('bear_front/')

# %%
dt = DepthTracker(dl.K,particleN,particleCov,0.6,'sift')
siftData=runPrediction(dt,dl,T,R,1)
siftPlot = np.array(siftData[0])[:,:3]
plt.plot(siftPlot)
plt.title('SIFT',fontsize=18)
plt.xlabel('Runtime: '+str(round(siftData[4],3))+' secs\nMSE: '+str(round(siftData[3]/len(siftData[0]),3))+' m',fontsize=12)
plt.legend(plt.gca(),labels=['X','Y','Z'],
           loc="top right",
           borderaxespad=2,
           )
plt.savefig('descriptors.eps',bbox_inches='tight')
