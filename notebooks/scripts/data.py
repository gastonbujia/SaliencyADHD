import numpy as np
import pandas as pd
import os
from scripts.preprocessing import str2list

def get_ids(file):
    file_splitted = file.split('/')
    subj_folder_id = file_splitted[-2]
    video_id =  file_splitted[-1].split('_')[1]
    return subj_folder_id, video_id

def load_trials_data(trial_data_path = os.path.join('..','data/VideoMatchingSrate_corr.csv')):
    
    trial_data = pd.read_csv(trial_data_path)
    trial_data['ID'] = trial_data['FilePath'].apply(lambda x: x.split('/')[-2])
    trial_data['Video_ID'] = trial_data['FilePath'].apply(lambda x: x.split('/')[-1].split('_')[1])
    trial_data['VideoName'] = trial_data['VideoName'].apply(lambda s: s.lstrip())
    _trial_data_midx_ = pd.MultiIndex.from_frame(trial_data[['ID', 'Video_ID']])

    return trial_data.set_index(_trial_data_midx_).drop(columns=_trial_data_midx_.names)
    
def load_video_data(video_data_path=os.path.join('..','videos_data')):
                                                 
    video_data_path = os.path.join(video_data_path,'VideoData.csv')
    video_data = pd.read_csv(video_data_path)
    video_data['FramesTimestamps'] = video_data.Time.apply(lambda x: np.array(str2list(x)))
    video_list = ['Diary_of_a_Wimpy_Kid_Trailer.mp4',
              'Fun_Fractals_v2.mp4',
              'The Present_Short.mp4',
              'Three_Little_Kittens_Despicable_Me.mp4']
    video_saliency = list(map(lambda s: s[:-4]+'_saliency_cb.npy', video_list))
    video_saliency_nocb = list(map(lambda s: s[:-4]+'_saliency.npy', video_list))
    video_percentils = list(map(lambda s: s[:-4]+'_percentils.npy', video_saliency))
    video_percentils_nocb = list(map(lambda s: s[:-7]+'_percentils.npy', video_saliency))
    videos_ids = pd.DataFrame(zip(['Diary','Fractals','Present','Despicable'],video_list, video_saliency, video_saliency_nocb, video_percentils, video_percentils_nocb),
                              columns=['VideoName','Video', 'VideoSaliency','VideoSaliencyNOcb','VideoSalPercentils','VideoSalPercentilsNOcb'])
    
    video_data = pd.merge(video_data, videos_ids, on='Video').set_index('VideoName')
    video_data['Short Name'] = ['WK','FF', 'TP', 'DM']
    return video_data.drop(columns=['Time'])

def load_metadata(metadata_path = os.path.join('..','data')):
    
    metadata_path = os.path.join(metadata_path,'PhenoDataFinal.csv')
    metadata = pd.read_csv(metadata_path)
    metadata['SWAN']= pd.to_numeric(metadata.SWAN_Total.str.replace(",", "Nan"), errors='coerce')
    metadata['Age'] = metadata.Age.replace('.',0).astype(float)
    return metadata

def load_subj_et_data(folder_subj, video_id, data_path, preffered_eye = 'right'):
    
    df_et = pd.read_csv(data_path + folder_subj +'/'+ '_'.join([folder_subj, 'Video-'+video_id, 'ET', preffered_eye])+'.csv')
    
    return df_et

def create_video_table(path_to_data, path_to_metadata):
    
    return 
