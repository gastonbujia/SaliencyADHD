import os
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

def is_sorted_descending(lista):
    flag = True
    i = 1
    while i < len(lista):
        if(lista[i] > lista[i - 1]):
            return False
        i += 1
    return flag

def frame_saliency_binary_map(frame_sal, cut):
    sal_bin = np.zeros(frame_sal.shape)
    ixy = np.where(frame_sal > np.percentile(frame_sal, q = cut))
    for x,y in zip(ixy[0],ixy[1]):
        sal_bin[x,y] = 1
    return sal_bin

def explode(frame, columns):
    """
    This helper function explodes a new row
        for each value in an array of values.
    If there is more than one column to be exploded,
        the array lengths must be the same (row-wise)
    (Adapted from a SE code snippet)
    Args:
        frame: The input dataframe
        columns: the columns with arrays to explode
    Returns:
        transformed dataframe
    """
    # all columns that are not arrays of values
    idx_cols = frame.columns.difference(columns)

    # calculate lengths of arrays
    lens = frame[columns[0]].str.len()

    return pd.DataFrame({
        col: np.repeat(frame[col].values, lens)
        for col in idx_cols
    }).assign(**{col: np.concatenate(frame[col].values)
                 for col in columns}).loc[:, frame.columns]

# TIMESERIES TOOLS
def get_timeseries(df, sid, ind ='FRAME_idx',val='NSS'):
    # ind is 'FIX_ts' or 'FRAME_id'
    # sid is subject's id
    ret = df[df.ID==sid][[ind ,val]].sort_values([ind],ascending=True).copy()
    return ret

def create_timeseries_matrix(df,  nframes, skip_first = 24, metric_val='NSS', interpolation='linear'):
    
    frame_index = list(range(0, nframes))
    dummy_df = pd.DataFrame(frame_index,columns=['FRAME_idx'])
    ts_list = []
    ids_list = []
    for sid in df.ID.unique():
        ts = get_timeseries(df, sid, ind ='FRAME_idx', val=metric_val)
        # porque estoy usando 24?
        if ts.FRAME_idx.iloc[0] <= skip_first:
            ts_alineado = dummy_df.merge(ts, left_on = 'FRAME_idx', right_on='FRAME_idx', how='outer')
            ts_alineado[metric_val] = ts_alineado[metric_val].interpolate(interpolation)
            ts_alineado = ts_alineado.set_index('FRAME_idx')#.drop(columns=['FRAME_idx'])
            ts_list.append(ts_alineado)
            ids_list.append(sid)
    
    df_ts = pd.concat(ts_list,axis=1)
    df_ts.columns = ids_list
    return df_ts

def plot_timeseries(timeseries, video_full_name, metric_name = 'NSS'):
    _, ax = plt.subplots(figsize=(15,8))
    m = timeseries.mean(axis=1)
    sm = timeseries.std(axis=1)
    plt.plot(m)
    plt.axhline(y = m.mean(), color = 'r', linestyle = '-.', alpha=0.7)
    plt.fill_between(m.index, m - 1 * sm, m + 1 * sm, alpha=0.2);
    ax.set_ylabel(metric_name, fontsize=15)
    #ax.legend('Frame', fontsize=14);
    plt.title(video_full_name, fontsize=18);
    return None

# SCENES TOOLS
def calc_scenes(df, df_scenes):
    """_summary_

    Args:
        df (_type_): _description_
        df_scenes (_type_): _description_

    Returns:
        _type_: _description_
    """
    scenes_vals = [j for j in range(df_scenes.shape[0]) for _ in range(df_scenes.iloc[j]['Start Frame'], df_scenes.iloc[j]['End Frame'])]
    scenes_fram = range(df_scenes.iloc[-1]['End Frame'])
    assert len(scenes_vals) == len(scenes_fram)
    scenes_dict = dict(zip(scenes_fram, scenes_vals))
    new_col = df['FRAME_idx'].map(scenes_dict)
    return new_col

def plot_sample_scenes(scene: int, video_name: str, images_path = os.path.join('..','..','videos_data')):
    
    images = []
    images_path = os.path.join(images_path, video_name)
    for f in os.listdir(images_path):
        if f[-4:] == '.jpg':
            if int(f.split('-')[-2]) == scene:
                images.append(f)
        
    _, axs = plt.subplots(1, 3, figsize=(18, 10))
    axs = axs.flatten()
    for img_file, ax in zip(images, axs):
        img = mpimg.imread(os.path.join(images_path,img_file))
        ax.imshow(img)
    plt.show()
    
def plot_sample_frames(framenum: int, video_name: str = 'Diary/Diary_of_a_Wimpy_Kid_Trailer.mp4',
                       video_path = os.path.join('/hdd/ReposPesados/SaliencyADHD/videos_data')):
    
    video_path = os.path.join(video_path, video_name)
    
    def get_frame(vidurl,framenum):
        
        vidcap = cv2.VideoCapture(vidurl)
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, framenum)
        _, frame = vidcap.read()
        return frame
    
    images = [get_frame(video_path, framenum + i) for i in [-10,0,10]]
    _, axs = plt.subplots(1, 3, figsize=(18, 10))
    axs = axs.flatten()
    for img_frame, ax in zip(images, axs):
        #img = mpimg.imread(os.path.join(video_path,img_file))
        img = img_frame
        ax.imshow(img)
    
    plt.show()
    
    #return images