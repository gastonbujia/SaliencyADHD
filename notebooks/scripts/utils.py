import os
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
    
