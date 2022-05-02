# SaliencyADHD

To calculate NSS for a video and a saliency map from notebook folder:

<code>
python calculate_nss.py -V 'Present' -S 'spectral'
</code>

Then to join the resulting dfs:

<code>
python join_nss_df.py
</code>

To download saliency maps and results:

LINK

Dir structs

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
