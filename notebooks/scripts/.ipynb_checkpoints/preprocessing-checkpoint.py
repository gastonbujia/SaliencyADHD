import cv2
import numpy as np
import pandas as pd

def get_frame(vidurl,sec):
    vidcap = cv2.VideoCapture(vidurl)
    vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
    hasFrames, image = vidcap.read()
    #if hasFrames and sv:
    #    cv2.imwrite("frame"+str(sec*1000)+"ms.jpg", image)     # save frame as JPG file
    return image

def save_frame(frames):
    return frames

def str2list(s):
    ls = s.lstrip('[').rstrip(']').split(',')
    return [float(x) for x in ls]

def time_filter(x, frames_ts, trial_init=0, scale=1/1000):
    return np.where((frames_ts+trial_init*scale >= x['start_time']) & (frames_ts+trial_init*scale <= x['end_time']))[0]

def preprocess_fixations(df, frames_ts, trial_init, trial_resol_width, trial_resol_hight, drop_off_fixations = True):
    """
    Input:
        - df: pd.DataFrame directly loaded from ET csv
        - frames_ts
        - trial_init
        - trial_resol_width, trial_resol_hight
        - drop_off_fixations: boolean, if True , fixations in dataframe previous
            to video's start and after video's end and out of video's dimensions
            are dropped.
    Output:
        - df_fix: pd.DataFrame 
        - flag: int, debug purposes, if 1, more than 5% of fixations are outside the video
    """
    # TODO: add and assertion or a warning if the subject has not finished the video
    
    df_fix = df[df.fix==1].copy()
    df_fix['xlist'] = df_fix['x'].apply(lambda x: str2list(x))
    df_fix['ylist'] = df_fix['y'].apply(lambda x: str2list(x))
    df_fix['dur'] = df_fix['end_time'] - df_fix['start_time']
    df_fix['x_mean']= df_fix['xlist'].apply(lambda x: np.array(x).mean())
    df_fix['y_mean']= df_fix['ylist'].apply(lambda x: np.array(x).mean())
    df_fix['x_std']= df_fix['xlist'].apply(lambda x: np.array(x).std())
    df_fix['y_std']= df_fix['ylist'].apply(lambda x: np.array(x).std())
    df_fix.drop(columns=['x','y'], inplace=True)
    
    n_fix = len(df_fix)
    if n_fix==0:
        flag = -1
        return df_fix.drop(columns=['xlist','ylist']), flag
    else:
        df_fix['frames_seen'] = df_fix[['start_time','end_time']].apply(time_filter, args=(frames_ts, trial_init), axis=1)
        
    if drop_off_fixations:
        df_fix = df_fix[df_fix['frames_seen'].map(len)>0]
        n_fix_in_vid_fix = len(df_fix)
        df_fix = df_fix[(df_fix.x_mean >= 0) & (df_fix.x_mean < trial_resol_width)]
        df_fix = df_fix[(df_fix.y_mean >= 0) & (df_fix.y_mean < trial_resol_hight)]
        n_fix_outside = n_fix_in_vid_fix - len(df_fix)
        
        if n_fix_in_vid_fix==0:
            flag = -1
        elif n_fix_outside/n_fix_in_vid_fix > 0.05:
            flag = 1
        else:
            flag = 0
            
    return df_fix.drop(columns=['xlist','ylist']), flag

def preprocess_fixations_new_dataset(df, frames_ts, trial_init, sdt_correction = False, drop_off_fixations=True):
    """
    INPUT:
        - df: pd.DataFrame directly loaded from ET csv
        - frames_ts
        - trial_init
        - std_correction
        - drop_off_fixations
    OUTPUT:
        - df_fix: pd.DataFrame 
        - flag: int, debug purposes, if 1, more than 5% of fixations are outside the video
    """
    # TODO: add and assertion or a warning if the subject has not finished the video
    # TODO: add SDT option
    
    df_fix = df[df.fix==1].copy()
    df_fix['xlist'] = df_fix['x'].apply(lambda x: str2list(x))
    df_fix['ylist'] = df_fix['y'].apply(lambda x: str2list(x))
    df_fix['dur'] = df_fix['end_time'] - df_fix['start_time']
    df_fix['x_mean']= df_fix['xlist'].apply(lambda x: np.array(x).mean())
    df_fix['y_mean']= df_fix['ylist'].apply(lambda x: np.array(x).mean())
    df_fix['x_std']= df_fix['xlist'].apply(lambda x: np.array(x).std())
    df_fix['y_std']= df_fix['ylist'].apply(lambda x: np.array(x).std())
    df_fix.drop(columns=['x','y'], inplace=True)
    
    # some constants
    flag  = 0
    n_fix = len(df_fix)
    scale = 1
    sdt_frame_delay = 0

    if n_fix==0:
        flag = -1
        return df_fix.drop(columns=['xlist','ylist']), flag
    else:
        if sdt_correction:
            # estimated saccadic dead time (sdt)
            sdt_frame_delay = 2
        df_fix['frames_seen'] = df_fix[['start_time','end_time']].apply(time_filter, args=(frames_ts, scale), axis=1) - sdt_frame_delay
        # drop negative frames if any
        
    if drop_off_fixations:
        df_fix = df_fix[df_fix['frames_seen'].map(len)>0]
        n_fix_in_vid_fix = len(df_fix)
        n_fix_outside = n_fix_in_vid_fix - len(df_fix)
        
        if n_fix_in_vid_fix==0:
            flag = -1
        elif n_fix_outside/n_fix_in_vid_fix > 0.05:
            flag = 1
        else:
            flag = 0
        
    return df_fix.drop(columns=['xlist','ylist']), flag