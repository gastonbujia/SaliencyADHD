import os
import pandas as pd
import numpy as np
from scipy.stats import multivariate_normal, entropy

def get_saliency_values(y,x,saliency, crux = True):
    """
    Get saliency values for fixation x, y. Clarification: in the data x measures the width and y measures the height of the image,
    but the salience is a matrix for which the first coordinate (x) measures the height and the second (y) measures the width. 
    So saliency map is accessed as [y,x].

    Args:
        y (int), x (int): fixation 
        saliency (np.array(int)): frame saliency map

    Returns:
        sal_val: the average saliency value using a radiuos of 1 () 
    """    
    h, w = saliency.shape
    c = 1
    
    # if fixation fall outside of video magins are sent inside (this is not longer necessary)    
    if x<0: x=0
    if y<0: y=0
    if x>h-1: x=h-1
    if y>w-1: y=w-1
    sal_val = float(saliency[x,y])
    if crux:
        if x < h-1:
            sal_val += saliency[x+1,y]
            c+=1
        if x > 0:
            sal_val += saliency[x-1,y]
            c+=1
        if y < w-1:
            sal_val += saliency[x,y+1]
            c+=1
        if y > 0:
            sal_val += saliency[x,y-1]    
            c+=1

    #sal_val += float(saliency[x,y])
        
    return sal_val/c

def empirical_saliency_map(fix, scale=0.1, resol_width=800, resol_height=600):
    mu    = np.array(fix)
    var   = resol_width * scale
    sigma = var*np.diag(np.diag(np.array((1,1))))
    x = np.arange(0, resol_width,1)
    y = np.arange(0, resol_height,1)
    X, Y = np.meshgrid(x, y)
    pos  = np.dstack((X, Y))
    rv   = multivariate_normal(mu, sigma)
    empirical_saliency = rv.pdf(pos)
    return empirical_saliency

def CC(saliency_map_1, saliency_map_2):
    def normalize(saliency_map):
        saliency_map -= saliency_map.mean()
        std = saliency_map.std()
        if std:
            saliency_map /= std
        return saliency_map, std == 0

    smap1, constant1 = normalize(saliency_map_1.copy())
    smap2, constant2 = normalize(saliency_map_2.copy())
    if constant1 and not constant2:
        return 0.0
    else:
        return np.corrcoef(smap1.flatten(), smap2.flatten())[0, 1]

def calculate_CC_row(row_fix, saliency, vid_resol_width, vid_resol_height, trial_resol_width=800, trial_resol_height=600):
    fix_x = int(np.floor((row_fix.x_mean/trial_resol_width) * vid_resol_width))
    fix_y = int(np.floor((row_fix.y_mean/trial_resol_height) * vid_resol_height))
    
    frame_seen = row_fix['frames_seen'][0]
    saliency_map = saliency[:,:,frame_seen]
    emp_sal_map = empirical_saliency_map((fix_x,fix_y), resol_height=vid_resol_height, resol_width=vid_resol_width)
    
    return CC(saliency_map, emp_sal_map)

def calculate_CC_apply(df, saliency, trial_resol_width=800, trial_resol_height=600):
    cc_score = []
    vid_resol_width = saliency.shape[0]
    vid_resol_height = saliency.shape[1]
    cc_score = df.apply(lambda x: calculate_CC_row(x, saliency, vid_resol_width, vid_resol_height, trial_resol_width, trial_resol_height, ),axis=1)
    return cc_score


def NSS(saliency, sal_mean, sal_std, xs, ys, ts, frame_dur):
    xs = np.asarray(xs, dtype=int)
    ys = np.asarray(ys, dtype=int)
    values = []
    
    for x,y,t in zip(xs, ys, ts):
        # para calcular el indice del frame, divido el timestamp por lo que dura cada frame
        fr = int(t//frame_dur)
        # hay microfijaciones por fuera de la duracion del video
        if fr >= saliency.shape[-1]:
            continue
         
        saliency_map = saliency[:,:,fr]
        mean = sal_mean[fr]
        std  = sal_std[fr]
        # TODO pasarlo a parametros
        crux = False
        value = get_saliency_values(x,y,saliency_map, crux=crux)
        value -= mean
        if std:
            value /= std
        values.append(value)

    return np.array(values).mean()

def calculate_NSS(df, saliency, sal_mean, sal_std, frame_dur, trial_resol_width=800, trial_resol_height=600):
    nss_score =[]
    vid_resol_width = saliency.shape[1]
    vid_resol_height = saliency.shape[0]
    for row_fix in df.itertuples():
        fix_x = list(map(lambda t: int(np.floor((t/trial_resol_width) * vid_resol_width)), row_fix.x))
        fix_y = list(map(lambda t: int(np.floor((t/trial_resol_height) * vid_resol_height)), row_fix.y))
        nss_score.append(NSS(saliency, sal_mean, sal_std, fix_x, fix_y, row_fix.sample_timestamps, frame_dur))
        
    return nss_score

# Jensen-Shannon div
def jsd(p, q, base=np.e):
    '''
        Taken from https://gist.github.com/zhiyzuo/f80e2b1cfb493a5711330d271a228a3d
    '''
    ## convert to np.array
    p, q = np.asarray(p), np.asarray(q)
    ## normalize p, q to probabilities
    p, q = p/p.sum(), q/q.sum()
    m = 1./2*(p + q)
    return entropy(p,m, base=base)/2. +  entropy(q, m, base=base)/2.