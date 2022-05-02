import os
import argparse
import pandas as pd
from functools import reduce

if __name__=='__main__':
    # join and save all results in the same dataframe
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-dp','--datapath', type=str, help='Path to subjects data directory', default=None)
    parser.add_argument('-rp','--respath',  type=str, help='Path to store results', default=None)
    args = parser.parse_args()
    
    # initialize paths by default
    if args.datapath is None: data_path    = os.path.join('..','data','ETFinalCutSampleEC07','ETFinalCutSample')
    if args.respath is None: results_path  = os.path.join('..', 'results')
    
    df_dict = {'WK':[], 'TP':[], 'FF':[]}
    for vid in df_dict.keys():
        path = os.path.join(results_path, vid)
        dfs = [pd.read_csv(os.path.join(path, 'results_nss_vinet.csv')).rename(columns={'NSS':'NSS_vn'}),
            pd.read_csv(os.path.join(path, 'results_nss_deepgazeii.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_dg'}),
            pd.read_csv(os.path.join(path, 'results_nss_spectral.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_sp'}),
            pd.read_csv(os.path.join(path, 'results_nss_finegrained.csv'))[['ID','FIX_idx','NSS']].rename(columns={'NSS':'NSS_fg'})]
    
        df_dict[vid] = reduce(lambda left,right: pd.merge(left,right,on=['ID', 'FIX_idx']), dfs).drop(columns='NSS_MEAN')
        df_dict[vid].to_csv(os.path.join(results_path, vid ,f'results_nss_{vid}.csv'.lower()), index=False)
