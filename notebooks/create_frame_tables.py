import os
import argparse
import numpy as np
import pandas as pd
from scripts.utils import *
from scripts.data import *

if __name__=='__main__':
    """
    This script creates the frame tables needed for the R script, both for frame level and for scene level.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-F','--frameskip',default=5, type=int, help='create table every F frames')
    parser.add_argument('-S','--scenes', default=False, type=bool, help='group all frames inside scene')
    args = parser.parse_args()
    
    VIDEO = 'WK'
    VIDEO_NAME = 'Diary'
    results_path = '../results/'
    file = 'results_nss_diary.csv'
    NFRAMES = 2817
    SKIP_FRAMES = args.frameskip
    
    # load videos data
    videos_data = load_video_data()

    # read NSS files
    df = pd.read_csv(os.path.join(results_path, VIDEO, file))
    df_means = df.groupby('ID')[['NSS_vn','NSS_fg']].mean()

    # compare both NSS files
    df_r = pd.read_csv(os.path.join('R', 'FinalTableH3bWK.csv'),sep=';')
    df_compare = pd.merge(df_r, df_means, on='ID', how='inner')
    df_compare.head()[['ID','NSS_fg_x', 'NSS_fg_y', 'NSS_vn_x', 'NSS_vn_y']]
    
    # filter subjects and remove outliers
    ids_data = df_r.ID.unique()
    # TODO: Remove OUTLIERS - Ask Sabine regarding this

    # create timeseries table - align NSS files
    ts_vn = create_timeseries_matrix(df[df.ID.isin(ids_data)].reset_index(), 
                                                  metric_val='NSS_vn',
                                                  nframes = NFRAMES)

    ts_fg = create_timeseries_matrix(df[df.ID.isin(ids_data)].reset_index(), 
                                                  metric_val='NSS_fg',
                                                  nframes = NFRAMES)

    # check/create save path
    results_dir = './results'
    if not os.path.exists(results_dir): os.mkdir(results_dir)
    video_results_dir = os.path.join(results_dir, VIDEO)
    if not os.path.exists(video_results_dir): os.mkdir(video_results_dir)
    
    if args.scenes:
        # SCENE LEVEL
        video_results_dir = os.path.join(video_results_dir, 'scene_tables')
        if not os.path.exists(video_results_dir): os.mkdir(video_results_dir)
        
        # add scenes to dataframe
        # TODO: cambiar path para que sea una entrada de la linea de comandos
        scenes_data =  pd.read_csv('/hdd/ReposPesados/SaliencyADHD/videos_data/Diary/Diary_of_a_Wimpy_Kid_Trailer-Scenes.csv',
                                   header=1)
        saliency_models = ['NSS_vn', 'NSS_fg']
        scenes_wk = calc_scenes(df, scenes_data)
        df['Scenes'] = scenes_wk
        # TODO: agregar que pueda guardar el error estandar de la media de las escenas
        df_scene_vals = df.groupby(['ID', 'Scenes'])[saliency_models].mean().reset_index(level=[1])
        for scene in df_scene_vals.Scenes.unique():
            # exclude tables of unneded frames fr.isin(frame_list)
            if True:
                # format data for R
                aux = df_r.drop(columns=['NSS_vn', 'NSS_fg'])
                vn_col_scene = df_scene_vals[df_scene_vals.Scenes == scene]['NSS_vn'].rename('NSS_vn')
                if vn_col_scene.isna().any():
                    # drop cases if any NaN Value
                    print('NaN in VN column! Frame: {}'.format(scene))
                    continue
                aux = pd.merge(aux, vn_col_scene, left_on='ID', right_index=True, how='inner')
                # TODO: perdi unos 60 sujetos seguramente en la funcion de create timeseries matrix
                #print(aux.shape)
                fg_col_scene =df_scene_vals[df_scene_vals.Scenes == scene]['NSS_fg']
                aux = pd.merge(aux, fg_col_scene, left_on='ID', right_index=True, how='inner')
                # save data in R format for each frame with separator ';'
                aux.to_csv(os.path.join(video_results_dir, 'table_{}_scene_{}.csv'.format(VIDEO_NAME, scene)),
                           index=False, sep=';')
    else:
        # FRAME LEVEL
        # filter timeseries table (subset of frames)
        video_results_dir = os.path.join(video_results_dir, 'frame_tables')
        if not os.path.exists(video_results_dir): os.mkdir(video_results_dir)
        for fr in range(0, NFRAMES, SKIP_FRAMES):
            # exclude tables of unneded frames fr.isin(frame_list)
            if True:
                # format data for R
                aux = df_r.drop(columns=['NSS_vn', 'NSS_fg'])
                #print(aux.shape)
                vn_col = ts_vn.T.iloc[:,fr].rename('NSS_vn')
                if vn_col.isna().any():
                    # drop cases if any NaN Value
                    print('NaN in VN column! Frame: {}'.format(fr))
                    continue
                aux = pd.merge(aux, vn_col, left_on='ID', right_index=True, how='inner')
                # TODO: perdi unos 60 sujetos seguramente en la funcion de create timeseries matrix
                #print(aux.shape)
                fg_col = ts_fg.T.iloc[:,fr].rename('NSS_fg')
                aux = pd.merge(aux, fg_col, left_on='ID', right_index=True, how='inner')
                # save data in R format for each frame with separator ';'
                aux.to_csv(os.path.join(video_results_dir, 'table_{}_{}.csv'.format(VIDEO_NAME, fr)), index=False, sep=';')