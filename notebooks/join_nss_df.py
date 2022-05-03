import os
import argparse
import pandas as pd
from functools import reduce
from scripts.preprocessing import preprocess_fixations
from scripts.data import load_video_data

def add_frame_idx(df,
                  vid_name,
                  videos_data,
                  etfile_path=None):
    
    dfs_list = []
    for idx in df.ID.unique():
    
        df_aux       = df[df.ID==idx].copy()
        et_file      = df_aux.ET_FILE.iloc[0]
        if etfile_path==None:
            df_et = pd.read_csv(et_file)
        else:
            df_et = pd.read_csv(os.path.join(etfile_path, vid_name))
            print('Not tested yet')
            
        frame_timest = videos_data.loc[vid_name,'FramesTimestamps']
        df_fix, _    = preprocess_fixations(df_et, frame_timest)
        frame_id     = df_fix.frames_seen.apply(lambda x: x[0])
        df_aux       = df_aux.merge(frame_id,how='right',left_on='FIX_idx',right_index=True)    
        dfs_list.append(df_aux)
        
    df_exploded_frames = pd.concat(dfs_list)
    df_exploded_frames.rename({'frames_seen':'FRAME_idx'}, axis=1, inplace=True)
    return df_exploded_frames

if __name__=='__main__':
    # join and save all results in the same dataframe
    data_path    = os.path.join('..','data','ETFinalCutSampleEC07','ETFinalCutSample')
    results_path = os.path.join('..', 'results')
    videos_path  = os.path.join('..', 'videos_data')
    
    vid_codes   = {'Diary': 'WK', 'Fractals': 'FF', 'Present': 'TP'}
    videos_data = load_video_data(videos_path)
    
    df_dict = {'Diary':[], 'Present':[], 'Fractals':[]}
    for vid in df_dict.keys():
        path = os.path.join(results_path, vid_codes[vid])
        dfs = [pd.read_csv(os.path.join(path, 'results_nss_vinet.csv')).rename(columns={'NSS':'NSS_vn'}),
            pd.read_csv(os.path.join(path, 'results_nss_deepgazeii.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_dg'}),
            pd.read_csv(os.path.join(path, 'results_nss_spectral.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_sp'}),
            pd.read_csv(os.path.join(path, 'results_nss_finegrained.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_fg'})]
    
        df_dict[vid] = reduce(lambda left,right: pd.merge(left,right,on=['ID', 'FIX_idx']), dfs).drop(columns='NSS_MEAN')
        print(f'Adding frame id in {vid}...')
        df_dict[vid] = add_frame_idx(df_dict[vid], vid, videos_data)
        print('Done')
        df_dict[vid].to_csv(os.path.join(results_path, vid_codes[vid] ,f'results_nss_{vid}.csv'.lower()), index=False)
