import numpy as np
import scipy.ndimage

class SaliencyScorer():
    
    def __init__(self, metric='auc'):
        if metric == 'auc':
            self.metric = auc_borji()       
        elif metric == 'nss':
            self.metric = nss()
        elif metric == 'cc':
            self.metric = cc()
        elif metric == 'infogain'
            self.metric = infogain()
        elif metric == 'emd':
            self.metric = emd()
        elif metric == 'kldiv':
            self.metric = kldiv()
        elif metric == 'sauc':
            self.metric = sauc()
        else:
            raise NotImplementedError('Saliency metric not available, metrics implemented are: auc, sauc, nss, cc, infogain, emd and kldiv')
            
    def auc_borji():
        return None
    
    def nss(saliencyMap, fixationMap):
        # saliencyMap is the saliency map
        # fixationMap is the human fixation map (binary matrix)
        smap = double(imresize(saliencyMap,size(fixationMap)));
        # normalize saliency map
        smap = (smap - mean(smap(:)))/std(smap(:)); 
        # mean value at fixation locations
        score = mean(smap(logical(fixationMap))); 
        return score
    
    def infogain():
        return None
    
    def cc(saliencymap1, saliencymap2):
        # saliencysmap1 and saliencysmap2 are 2 real-valued matrices
        smap1 = im2double(imresize(saliencysmap1, size(saliencysmap2)));
        smap2 = im2double(saliencysmap2);
        # normalize both maps
        smap1 = (smap1 - mean(smap1(:))) / std(smap1(:)); 
        smap2 = (smap2 - mean(smap2(:))) / std(smap2(:)); 

        score = corr2(smap2, smap1)
        return score
    
    def emd():
        return None
    
    def kldiv(saliencyMap, fixationMap):
        # saliencyMap is the saliency map
        # fixationMap is the human fixation map
        smap1 = im2double(imresize(saliencyMap, size(fixationMap)));
        smap2 = im2double(fixationMap);
        # make sure smap1 and smap2 sum to 1
        if any(smap1(:))
            smap1 = smap1/sum(smap1(:));
        end
        if any(smap2(:))
            smap2 = smap2/sum(smap2(:));
        end
        # compute KL-divergence
        score = sum(sum(smap2 .* log(eps + smap2./(smap1+eps))));
        return score
    
    def sauc():
        return None
    
    def calculate_score(self, *kwd):
        return score