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

def preprocess_fixations(df:pd.DataFrame, frames_ts, sdt_correction = False, drop_off_fixations=True):
    
    """
    INPUT:
        - df: pd.DataFrame, loaded ET csv
        - frames_ts: list, each frame timestamps, equal to range(0, VIDEO_LENGTH/NFRAME)
        - std_correction: bool, add a correccion for saccadic dead time
        - drop_off_fixations: bool, drop fixations that after the video ended
    OUTPUT:
        - df_fix: pd.DataFrame
        - flag: int, debug purposes,
                if 0, everything is ok
                if 1, more than 5% of fixations are outside the video
                if -1, there are no fixations on the csv
    """
    
    df_fix = df[df.fix==1].copy()
    n_fix  = len(df_fix)
    flag   = 0
    
    if n_fix==0:
        flag = -1
        return df_fix, flag
    
    df_fix['x']   = df_fix['x'].apply(lambda x: str2list(x))
    df_fix['y']   = df_fix['y'].apply(lambda x: str2list(x))
    df_fix['dur'] = df_fix['end_time'] - df_fix['start_time']
    
    # summary measures
    df_fix['x_mean'] = df_fix['x'].apply(lambda x: np.array(x).mean())
    df_fix['y_mean'] = df_fix['y'].apply(lambda x: np.array(x).mean())
    df_fix['x_std']  = df_fix['x'].apply(lambda x: np.array(x).std())
    df_fix['y_std']  = df_fix['y'].apply(lambda x: np.array(x).std())
    
    df_fix['sample_timestamps'] = df_fix.apply(lambda x: np.arange(x.start_time, x.end_time, step = x.dur/x.event_len), axis=1)
    
    # some constants
    scale = 1
    sdt_frame_delay = 0

    if sdt_correction:
        # estimated saccadic dead time (sdt)
        sdt_frame_delay = 2

    # calculate frames seen by that fixation
    df_fix['frames_seen'] = df_fix[['start_time','end_time']].apply(time_filter, args=(frames_ts, scale), axis=1) - sdt_frame_delay
        
    if drop_off_fixations:
        df_fix = df_fix[df_fix['frames_seen'].map(len)>0]
        n_fix_in_vid_fix = len(df_fix)
        n_fix_outside = n_fix_in_vid_fix - len(df_fix)
        #df_fix = df_fix[df_fix['start_time']//frame_dur < video.shape[-1]]
        if n_fix_in_vid_fix==0:
            flag = -1
        elif n_fix_outside/n_fix_in_vid_fix > 0.05:
            flag = 1
        else:
            flag = 0
        
    return df_fix, flag