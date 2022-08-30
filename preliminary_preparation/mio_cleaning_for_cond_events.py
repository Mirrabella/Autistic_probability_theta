import mne
import os
import os.path as op
import numpy as np

subjects = ['P301', 'P304', 'P307', 'P308', 'P309', 'P311', 'P312', 'P313', 'P314', 'P316', 'P318', 'P320', 
            'P321', 'P322', 'P323', 'P324', 'P325', 'P326', 'P327', 'P328', 'P329', 'P330', 'P331', 'P332', 
            'P333', 'P334', 'P335', 'P336', 'P338', 'P340', 'P341', 'P342', 'P063', 'P064', 'P065', 'P066', 
            'P067']
        
   

rounds = [1, 2, 3, 4, 5, 6]


trial_type = ['norisk', 'prerisk', 'risk', 'postrisk']

feedback = ['positive', 'negative']

for subj in subjects:
    for r in rounds:
    
        for t in trial_type:
            for fb in feedback:
                
                try:
                    # загружаем массив эвентов, прошедших миокоррекцию
                    events_mio_corrected = np.loadtxt('/net/server/data/Archive/prob_learn/data_processing/mio_free_events/{0}/{0}_run{1}_mio_free.txt'.format(subj, r))
                    
                    
                    events_mio_corrected = events_mio_corrected.tolist()
                    # загружаем массив эвентов, разбитые по условиям
                    events_by_cond = np.loadtxt('/home/vtretyakova/Рабочий стол/probabitily_teta/trained/{0}_run{1}_{2}_fb_{3}.txt'.format(subj, r, t, fb), dtype='int')
                    
                    if events_by_cond.shape == (3,):
                        events_by_cond = events_by_cond.reshape(1,3)
                        
                   
                    
                    events_by_cond = events_by_cond.tolist()
                    

                    events_by_cond_mio_corr = []
                    for i in events_by_cond:
                        if i in events_mio_corrected:
                            events_by_cond_mio_corr.append(i)
                            
                    events_by_cond_mio_corr = np.array(events_by_cond_mio_corr)
                    
                    #if events_by_cond_mio_corr.shape == (3,):
                    #    events_by_cond_mio_corr = events_by_cond_mio_corr.reshape(1,3)
                    
                    n = np.size(events_by_cond_mio_corr)
                    
                    if n != 0:

                        np.savetxt("/net/server/data/Archive/prob_learn/data_processing/events_trained_by_cond_WITH_mio_corrected/{0}_run{1}_{2}_fb_cur_{3}.txt".format(subj, r, t, fb), events_by_cond_mio_corr, fmt="%s")
                    else:
                        print(f'{subj} run{r} {t} {fb} all trials were delited by miocorrected')
                except OSError:
                    
                    print(f'{subj} run{r} {t} {fb} not exist')
                    

                    
                    
                    
