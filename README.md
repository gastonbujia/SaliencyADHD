# SaliencyADHD

This repository contains the code to calculate Normalized Scanpath Saliency (**NSS**) metric for each subject of the dataset ET-ADHD and for a video.

## NSS calculations

To calculate NSS for a video and a saliency model, from the notebook folder:

<code>
python calculate_nss.py -V 'Present' -S 'spectral'
</code>
<br/><br/>

To join all results of NSS for each saliency model:

<code>
python join_nss_df.py
</code/>
<br/><br/>
    
To download saliency maps and results:

TBD

## Directory
    
This repository is linked as follow

```bash
├── cache
├── data
│   ├── archive
│   ├── ETFinalCutSampleEC07
│       └── ETFinalCutSample
├── notebooks
│   └── scripts
├── results
│   ├── FF
│   ├── TP
│   └── WK
├── videos_data
│   ├── Diary
│   ├── Fractals
│   └── Present
└── videos_sal
    ├── deepgazeii
    │   ├── Diary
    │   ├── Fractals
    │   └── Present
    ├── finegrained
    │   ├── Diary
    │   ├── Fractals
    │   └── Present
    ├── spectral
    │   ├── Diary
    │   ├── Fractals
    │   └── Present
    └── vinet
        ├── Diary
        ├── Fractals
        └── Present
```
