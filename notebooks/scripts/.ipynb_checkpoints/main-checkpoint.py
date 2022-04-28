import numpy as np
import pandas as pd
from sklearn.metrics import auc

# TODO: agregar filtros para distintas resoluciones y sacar el if true
# TODO: agregar campos que asumimos en el data frame
# TODO: implementar (o borrar) criterio

def fixation_sal_percentils(row_fix, vid_saliency, vid_resol_width, vid_resol_hight, trial_resol_width, trial_resol_hight, percentils, vid_percentils, criterion):
    
    # here will go criterion -> first
    frame_seen = row_fix['frames_seen'][0]

    # if needed reescale fixation (map) to vid_saliency
    if True:
        fix_x = int(np.floor((row_fix.x_mean/trial_resol_width) * vid_resol_width))
        fix_y = int(np.floor((row_fix.y_mean/trial_resol_hight) * vid_resol_hight))

    predicted_sal = vid_saliency[fix_x,fix_y,frame_seen]
    tpos = (vid_percentils[:,frame_seen] <= predicted_sal)
    dictout = dict(zip([str(100-int(p)) for p in percentils],tpos))
        
    return pd.Series(dictout)
    
def fixations_subj_auc(fixations_df,
                       vid_saliency,
                       vid_saliency_percentils,
                       trial_resol_width = 800,
                       trial_resol_hight = 600,
                       npercentils=21,
                       criterion='first'):
    """
    INPUT:
        - fixations_df: pd.DataFrame (O USAR SOLAMENTE UNA FIJACION?)
        - vid_saliency: np.array
        - vid_saliency_percentils: 
        - trial_resol_width, trial_resol_hight: 
        - npercentils: int, number of percentils to use
        - criterion: str, criterion for aggregation of frames. mean, median, first, last, all - NOT FINISHED
    OUTPUT:
        - auc
        - tpr: pd.DataFrame -> row
        - percentils: debug purpose
        - flags: deprecated
    """
    
    percentils = np.linspace(0,100,npercentils)
    vid_resol_width = vid_saliency.shape[0]
    vid_resol_hight = vid_saliency.shape[1]
    
    bin_df = fixations_df.apply(lambda x: fixation_sal_percentils(x, 
                                                                  vid_saliency,
                                                                  vid_resol_width,
                                                                  vid_resol_hight,
                                                                  trial_resol_width,
                                                                  trial_resol_hight,
                                                                  percentils,
                                                                  vid_saliency_percentils,
                                                                  criterion), 
                                                           axis=1)
    
    tpr = bin_df.mean(axis=0)[-1::-1]
    return auc(percentils/100, tpr), (percentils/100, tpr)