import os
import cv2
import argparse

if __name__=='__main__':
    
    saliency = 'vinet'
    vid_name = 'Diary'
    background_path = f'./{vid_name}/frames/'
    overlay_path = f'./../videos_sal/{saliency}/{vid_name}/'
    save_folder = './extras/'
    background_weight = 0.80
    overlay_weight = 0.20
    
    bkg_files = [f for f in os.listdir(background_path) if not f.startswith('.')]
    over_files = [f for f in os.listdir(overlay_path) if not f.startswith('.')]
    i = 0
    for bkg, over in zip(sorted(bkg_files), sorted(over_files)):
        
        if i%100 ==0: print('Frame: ', bkg)
        background = cv2.imread(os.path.join(background_path, bkg))
        # podria truncar los valores bajos para que no quede tan raro
        overlay = cv2.imread(os.path.join(overlay_path, over))
        overlay = cv2.applyColorMap(overlay, cv2.COLORMAP_JET)
        added_image = cv2.addWeighted(background,background_weight,overlay,overlay_weight,0)

        cv2.imwrite(os.path.join(save_folder, f'extra_{vid_name}_{saliency}_{i:04d}.jpg'.lower()), added_image)
        i+=1
        
# para armar el video
#ffmpeg -framerate 60 -i ./extras/extra_diary_vinet_%04d.jpg diary_vinet_overlay.mp4