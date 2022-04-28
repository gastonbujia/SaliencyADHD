import os
import pandas as pd
import numpy as np

def empirical_saliency_map(fix, scale=0.1, resol_width=800, resol_hight=600):
    mu    = np.array(fix)
    var   = resol_width * scale
    sigma = var*np.diag(np.diag(np.array((1,1))))
    x = np.arange(0, resol_width,1)
    y = np.arange(0, resol_hight,1)
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

def calculate_CC_row(row_fix, saliency, vid_resol_width, vid_resol_hight, trial_resol_width=800, trial_resol_hight=600):
    fix_x = int(np.floor((row_fix.x_mean/trial_resol_width) * vid_resol_width))
    fix_y = int(np.floor((row_fix.y_mean/trial_resol_hight) * vid_resol_hight))
    
    frame_seen = row_fix['frames_seen'][0]
    saliency_map = saliency[:,:,frame_seen]
    emp_sal_map = empirical_saliency_map((fix_x,fix_y), resol_hight=vid_resol_hight, resol_width=vid_resol_width)
    
    return CC(saliency_map, emp_sal_map)

def calculate_CC_apply(df, saliency, trial_resol_width=800, trial_resol_hight=600):
    cc_score = []
    vid_resol_width = saliency.shape[0]
    vid_resol_hight = saliency.shape[1]
    cc_score = df.apply(lambda x: calculate_CC_row(x, saliency, vid_resol_width, vid_resol_hight, trial_resol_width, trial_resol_hight, ),axis=1)
    return cc_score

# NSS
def NSS(saliency_map, xs, ys):
    xs = np.asarray(xs, dtype=int)
    ys = np.asarray(ys, dtype=int)
    mean = saliency_map.mean()
    std  = saliency_map.std()
    value  = saliency_map[xs, ys].copy()
    value -= mean
    if std:
        value /= std

    return value

def calculate_NSS(df, saliency, trial_resol_width=800, trial_resol_hight=600):
    nss_score =[]
    vid_resol_width = saliency.shape[0]
    vid_resol_hight = saliency.shape[1]
    for idx, row_fix in df.iterrows():
        fix_x = int(np.floor((row_fix.x_mean/trial_resol_width) * vid_resol_width))
        fix_y = int(np.floor((row_fix.y_mean/trial_resol_hight) * vid_resol_hight))
        frame_seen = row_fix['frames_seen'][0]
        saliency_map = saliency[:,:,frame_seen]
        nss_score.append(NSS(saliency_map, fix_x, fix_y))
    
    return nss_score

def calculate_NSS_row(row_fix, saliency, vid_resol_width, vid_resol_hight, trial_resol_width=800, trial_resol_hight=600):
    fix_x = int(np.floor((row_fix.x_mean/trial_resol_width) * vid_resol_width))
    fix_y = int(np.floor((row_fix.y_mean/trial_resol_hight) * vid_resol_hight))
    frame_seen = row_fix['frames_seen'][0]
    saliency_map = saliency[:,:,frame_seen]
    return NSS(saliency_map, fix_x, fix_y)

def calculate_NSS_apply(df, saliency, trial_resol_width=800, trial_resol_hight=600):
    nss_score =[]
    vid_resol_width = saliency.shape[0]
    vid_resol_hight = saliency.shape[1]
    nss_score = df.apply(lambda x: calculate_NSS_row(x, saliency, trial_resol_width, trial_resol_hight, vid_resol_width, vid_resol_hight),axis=1)
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