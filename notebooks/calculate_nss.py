import os
import json
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
from numpy.lib.format import open_memmap

from scripts.data import *
from scripts.preprocessing import *
from scripts.utils import *
from scripts.saliency_metrics import *

# auxiliar funcs
def create_saliency_matrix(video_folder, saliency_path ='../videos_sal/vinet'):
    
    maps = []
    for img in sorted(os.listdir(os.path.join(saliency_path, video_folder))):
        if img[0] == '.':
            continue
        maps.append(cv2.imread(os.path.join(saliency_path, video_folder, img), cv2.IMREAD_GRAYSCALE))
    return np.stack(maps, axis=2)

# add frame idx
def add_frame_idx(df,
                  vid_name,
                  data_path,
                  trials_data,
                  videos_data):
    
    dfs_list = []
    for idx in df.ID.unique():
    
        df_aux       = df[df.ID==idx].copy()
        et_file      = df_aux.ET_FILE.iloc[0]
        df_et        = pd.read_csv(os.path.join(data_path,et_file[2:]))
        frame_timest = videos_data.loc[vid_name,'FramesTimestamps']
        trial_init   = trials_data.loc[idx].set_index('VideoName').loc[vid_name].Start
        df_fix, flag = preprocess_fixations(df_et, frame_timest, trial_init)
        frame_id     = df_fix.frames_seen.apply(lambda x: x[0])
        df_aux       = df_aux.merge(frame_id,how='right',left_on='FIX_idx',right_index=True)    
        dfs_list.append(df_aux)
        
    df_exploded_frames = pd.concat(dfs_list)
    df_exploded_frames.rename({'frames_seen':'FRAME_idx'}, axis=1, inplace=True)
    return df_exploded_frames

def calculate_metric_subject(df_et,
                             videos_data,
                             vid_name,
                             saliency,
                             sal_mean,
                             sal_std,
                             metric,
                             frame_dur=None,
                             frame_timest=None):
    """
        Warning, this function assumes that every subject has a resolution size of trial_resol_width=800, trial_resol_height=600

    Args:
        df_et (pd.DataFrame): _description_
        videos_data (_type_): _description_
        vid_name (_type_): _description_
        saliency (_type_): _description_
        sal_mean (_type_): _description_
        sal_std (_type_): _description_
        metric (_type_): _description_
        frame_dur (_type_, optional): _description_. Defaults to None.
        frame_timest (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    
    if frame_dur is None:
        frame_dur = (videos_data.loc[vid_name].FramesTimestamps[1])
    if frame_timest is None:
        frame_timest = videos_data.loc[vid_name,'FramesTimestamps']
    
    df_fix, flag = preprocess_fixations(df_et, frame_timest, sdt_correction = False)
    # drop fixations after video ended
    df_fix = df_fix[df_fix['start_time']//frame_dur < saliency.shape[-1]]
    
    # as it is assumed that trial_resol_width=800, trial_resol_height=600, we checked it
    trial_resol_width=800 #x
    trial_resol_height=600 #y
    assert (df_fix.x.apply(max)>=trial_resol_width).sum() == 0
    assert (df_fix.y.apply(max)>=trial_resol_height).sum() == 0
    
    #print(fold_subj)
    if flag==-1:
        # subject has no fixations
        return None
    elif metric =='CC':
        score = calculate_CC_apply(df_fix, saliency)
    elif metric=='NSS':
        score = calculate_NSS(df_fix, saliency, sal_mean, sal_std, frame_dur, trial_resol_width=800, trial_resol_height=600)
    else:
        print('Metric not implemented')
        return None
    
    mean_score = np.mean(np.array(score))

    return df_fix, score, mean_score, flag

def calculate_metric_dataset(data_path, 
                             videos_data,
                             metadata,
                             vid_name,
                             saliency = None,
                             metric = 'NSS',
                             saliency_path = ''):
    """
    Calculate the specific metric for all subjects that saw the video.

    Args:
        data_path (str): _description_
        videos_data (_type_): _description_
        metadata (_type_): _description_
        vid_name (_type_): _description_
        saliency (_type_, optional): _description_. Defaults to None.
        metric (str, optional): _description_. Defaults to 'NSS'.
        saliency_path (str, optional): _description_. Defaults to ''.

    Returns:
        _type_: _description_
    """
    
    frame_dur = (videos_data.loc[vid_name].FramesTimestamps[1])
    vid = {'Diary': 'WK', 'Fractals': 'FF', 'Present': 'TP'}
    
    if saliency is None:
        saliency = create_saliency_matrix(videos_data.loc[vid_name].Video[:-4], saliency_path=saliency_path)
        
    video_not_seen   = []
    missing_metadata = []
    error_list       = []
    results          = []
    
    # precalculate saliency metrics
    sal_mean = saliency.mean(axis=(0,1))
    sal_std = np.zeros(saliency.shape[-1])
    for i in range(saliency.shape[-1]):
        sal_std[i] = saliency[:,:,i].std()
    
    print('Warning: the data is assumed to be in the following resolution: trial_resol_width=800, trial_resol_height=600')
    # itereate over subjects
    datadir = sorted(os.listdir(data_path))
    with tqdm(range(len(datadir))) as pbar:
        for fold_subj in datadir:

            # check if metadata is present
            if fold_subj not in list(metadata['ID'].unique()):
                missing_metadata.append(fold_subj)

            # ignore hidden folders
            if fold_subj.startswith('.'):
                pbar.update()
                continue
            
            # load correspondig csv file if video seen
            csv_files    = os.listdir(os.path.join(data_path,fold_subj))
            csv_vid_file = [f for f in csv_files if vid[vid_name] in f]
            if len(csv_vid_file) ==0:
                video_not_seen.append(fold_subj)
                pbar.update()
                continue
            
            # load et file
            et_file      = os.path.join(data_path, fold_subj, csv_vid_file[0])
            df_et        = pd.read_csv(et_file)

            # get video frame timestamps
            frame_timest = videos_data.loc[vid_name,'FramesTimestamps']

            try:  
                df_fix, score, mean_score, flag = calculate_metric_subject(df_et,
                                                                           videos_data, 
                                                                           vid_name, 
                                                                           saliency, 
                                                                           sal_mean, 
                                                                           sal_std,
                                                                           metric, 
                                                                           frame_dur, 
                                                                           frame_timest)

                results.append((fold_subj,  df_fix.index, score, mean_score, len(df_fix), flag, vid_name, et_file))
                pbar.update()
            except:
                error_list.append(fold_subj)
                pbar.update()
                continue
            
    return results, {'missing_metadata': missing_metadata, 
                     'video_not_seen': video_not_seen,
                     'errors': error_list}

def main():
    return None

if __name__=="__main__":
    
    # IMPROVE: Change the hardcoded trial resolution size if necessary
    
    # init parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-V','--video',required='True',type=str,choices=['Diary','Present','Fractals'])
    parser.add_argument('-S','--saliency',required='True',type=str,choices=['vinet','deepgazeii','spectral','finegrained'],help='saliency model')
    parser.add_argument('-dp','--datapath',default = None,type=str, help='Path to subjects data')
    parser.add_argument('-sp','--salpath', default = None,type=str, help='Path to saliency models as images')
    parser.add_argument('-rp','--respath', default = None,type=str, help='Path to results folders')
    parser.add_argument('-vp','--vidpath', default = None,type=str, help='Path to VideoData file')
    parser.add_argument('-mp','--metapath', default = None,type=str, help='Path to PhenoDataFinal file') 
    args = parser.parse_args()
    
    VIDEO = args.video
    SALIENCY = args.saliency
    
    # video names to codes
    vid_codes   = {'Diary': 'WK', 'Fractals': 'FF', 'Present': 'TP'}
    
    if args.datapath is None: data_path     = os.path.join('..','data','ETFinalCutSampleEC07','ETFinalCutSample')
    if args.respath is None:  results_path  = os.path.join('..', 'results')
    if args.salpath is None:  saliency_path = os.path.join('..', 'videos_sal', SALIENCY)
    if args.vidpath is None:  videos_path   = os.path.join('..', 'videos_data')
    if args.metapath is None: metadata_path = os.path.join('..', 'data')
    
    # initialize trials, video and metadata dfs
    videos_data = load_video_data(videos_path)
    metadata    = load_metadata(metadata_path)
            
    print('Loading saliency map...')
    saliency = create_saliency_matrix(VIDEO, saliency_path=saliency_path)

    print('Calculating metric...')
    results_nss = calculate_metric_dataset(data_path, 
                                           videos_data,
                                           metadata,
                                           saliency = saliency,
                                           vid_name = VIDEO,
                                           saliency_path = saliency_path)
    
    print('Postprocessing...')
    df_nss_aux = pd.DataFrame(results_nss[0])
    df_nss_aux.columns = ['ID', 'FIX_idx', 'NSS','NSS_MEAN', 'FIX_IN_VID', 'FLAG', 'VIDEO_NAME', 'ET_FILE']
    df_nss_exploded = explode(df_nss_aux, ['FIX_idx','NSS']).reset_index(drop=True)
    
    # save results
    df_nss_exploded.drop(columns=['FLAG']).to_csv(os.path.join(results_path, vid_codes[VIDEO], 
                                                                        f'results_nss_{SALIENCY}.csv'), index=False)

    # dump debug
    with open(os.path.join(results_path, vid_codes[VIDEO], f'dump_nss_{SALIENCY}.json'), 'w') as jf:
        json.dump(results_nss[1], jf)
        
    #print('Ok! BUT NOT SAVED')
    print('Ok and saved!')