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
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-V','--videoname', type=str, default=None, help='Video name')
    parser.add_argument('-W','--wildcard', type=str, default=None, help='Wildcard to match the video files')
    args = parser.parse_args()
    
    # join and save all results in the same dataframe
    data_path    = os.path.join('..','data','ETFinalCutSampleEC07','ETFinalCutSample')
    results_path = os.path.join('..', 'results')
    videos_path  = os.path.join('..', 'videos_data')
    
    vid_codes   = {'Diary': 'WK', 'Fractals': 'FF', 'Present': 'TP'}
    videos_data = load_video_data(videos_path)
    
    if args.videoname==None:
        df_dict = {'Diary':[], 'Present':[], 'Fractals':[]}
    else:
        df_dict = {args.videoname: []}
        
    for vid in df_dict.keys():
        path = os.path.join(results_path, vid_codes[vid])
        print('Path: ', path)
        if args.wildcard==None:
            print('Loading the four files...')
            dfs = [pd.read_csv(os.path.join(path, 'results_nss_vinet.csv')).rename(columns={'NSS':'NSS_vn'}),
                pd.read_csv(os.path.join(path, 'results_nss_deepgazeii.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_dg'}),
                pd.read_csv(os.path.join(path, 'results_nss_spectral.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_sp'}),
                pd.read_csv(os.path.join(path, 'results_nss_finegrained.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_fg'})]

        else:
            key_dict = {'vinet':'NSS_vn', 'deepgaze':'NSS_dg', 'spectral':'NSS_sp', 'finegrained':'NSS_fg'}
            files = [file for file in os.listdir(path) if args.wildcard in file and ~file.startswith('.')]
            print('Total of ', len(files), ' files found: ', files)
            # NOTE: asumo que el nombre del archivo siempre es results_nss_<saliency> 
            dfs = [pd.read_csv(os.path.join(path, file))[['ID','FIX_idx','NSS']].rename(columns={'NSS':key_dict[file.split('_')[2]]}) for file in files]
            print('Total of ', len(dfs), ' files loaded')
        
        if args.videoname==None:
            df_dict[vid] = reduce(lambda left,right: pd.merge(left,right,on=['ID', 'FIX_idx']), dfs).drop(columns='NSS_MEAN')
        else:
            df_dict_aux = reduce(lambda left,right: pd.merge(left,right,on=['ID', 'FIX_idx']), dfs).drop(columns='NSS_MEAN', errors='ignore')
            df_dict[vid] = pd.merge(df_dict_aux, pd.read_csv(os.path.join(path, files[0]))[['ID','FIX_idx','ET_FILE']], on=['ID', 'FIX_idx'], how='left')
            print('Shape: ', df_dict_aux.shape)
            print('Shape: ', df_dict[vid].shape)
            
        print(f'Adding frame id in {vid}...')
        df_dict[vid] = add_frame_idx(df_dict[vid], vid, videos_data)
        print('Done')
        if args.wildcard == None:
            df_dict[vid].to_csv(os.path.join(results_path, vid_codes[vid] ,f'results_nss_{vid}.csv'.lower()), index=False)
        else:
            df_dict[vid].to_csv(os.path.join(results_path, vid_codes[vid] ,f'results_nss_{vid}_{args.wildcard}.csv'.lower()), index=False)
