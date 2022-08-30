import mne
import os
import os.path as op
import numpy as np
from function import fixation_cross_events

subjects = ['P301', 'P304', 'P307', 'P308', 'P309', 'P311', 'P312', 'P313', 'P314', 'P316', 'P318', 'P320', 
            'P321', 'P322', 'P323', 'P324', 'P325', 'P326', 'P327', 'P328', 'P329', 'P330', 'P331', 'P332', 
            'P333', 'P334', 'P335', 'P336', 'P338', 'P340', 'P341', 'P342', 'P063', 'P064', 'P065', 'P066', 
            'P067']
            
rounds = [1, 2, 3, 4, 5, 6]


trial_type = ['norisk', 'prerisk', 'risk', 'postrisk']
#trial_type = ['norisk']

feedback = ['positive', 'negative']

# events without trash marks
data_path_raw = '/net/server/mnt/Archive/prob_learn/data_processing/Raw_events_without_trash_marks' 
raw_name = '{0}_run{1}_events_clean.txt'
data_path_events = '/net/server/mnt/Archive/prob_learn/data_processing/events_trained_by_cond_WITH_mio_corrected'
name_events = '{0}_run{1}_{2}_fb_cur_{3}.txt' 

for subj in subjects:
    for r in rounds:
    
        for t in trial_type:
            for fb in feedback:
                
                try:
                    event_fixation_cross_norisk = fixation_cross_events(data_path_raw, raw_name, data_path_events, name_events, subj, r, t, fb)
                
                    np.savetxt("/net/server/mnt/Archive/prob_learn/data_processing/fix_cross_mio_corr/{0}_run{1}_{2}_fb_cur_{3}_fix_cross.txt".format(subj, r, t, fb), event_fixation_cross_norisk, fmt="%s")
                    
                    

                except OSError:
                   print(f'{subj} run{r} {t} {fb} not exist')
                    

                    
                    
