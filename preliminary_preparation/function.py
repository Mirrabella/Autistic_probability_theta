import mne
import os
import os.path as op
import numpy as np
import pandas as pd
from scipy import stats
import copy
import statsmodels.stats.multitest as mul

#####################################################################################
######## Функция для поиска меток фиксационного креста (по ним ищется baseline)######

def fixation_cross_events(data_path_raw, raw_name, data_path_events, name_events, subj, r, t, fb):
    
    # для чтения файлов с events используйте либо np.loadtxt либо read_events либо read_events_N
    trial_type_event = np.loadtxt(op.join(data_path_events, name_events.format(subj, r, t, fb)), dtype='int')
        
    #trial_type_event = read_events(op.join(data_path_events, name_events.format(subj, r)))
    
    # Load raw events without miocorrection
    events_raw = np.loadtxt(op.join(data_path_raw, raw_name.format(subj, r)), dtype='int')        
    
    # Load data

    #raw_fname = op.join(data_path_raw, raw_name.format(subj, r))

    #raw = mne.io.Raw(raw_fname, preload=True)

    #events_raw = mne.find_events(raw, stim_channel='STI101', output='onset', 
    #                                 consecutive='increasing', min_duration=0, shortest_event=1, mask=None, 
    #                                 uint_cast=False, mask_type='and', initial_event=False, verbose=None)
    
    if trial_type_event.shape == (3,):
        trial_type_event = trial_type_event.reshape(1,3)
    # список индексов трайлов
    x = []
    for i in range(len(events_raw)):
	    for j in range(len(trial_type_event)):
		    if np.all((events_raw[i] - trial_type_event[j] == 0)):
			    x+=[i]

    x1 = 1 #fixation cross

    full_ev = []
    for i in x:
        full_ev += [list(events_raw[i])] # список из 3ех значений время х 0 х метка
        j = i - 1
        ok = True      
        while ok:
            full_ev += [list(events_raw[j])]
            if events_raw[j][2] == x1:
                ok = False
            j -= 1 

                
    event_fixation_cross = []

    for i in full_ev:
        if i[2] == x1:
            event_fixation_cross.append(i)
                    
    event_fixation_cross = np.array(event_fixation_cross)
     
    return event_fixation_cross


##########################################################################################        
################### Фукнция для получения предыдущего фидбека ############################
def prev_feedback(events_raw, tials_of_interest, FB):
    
    #Получаем индексы трайлов, которые нас интересуют
    
    x = []
    for i in range(len(events_raw)):
	    for j in range(len(tials_of_interest)):
		    if np.all((events_raw[i] - tials_of_interest[j] == 0)):
			    x+=[i]
    
    prev_fb = []

    for i in x:
        ok = True
        while ok:
            #print(i)
            if events_raw[i-1][2] in FB:
                a = events_raw[i-1].tolist()
                prev_fb.append(a)
                ok = False
            else:
                pass
            i = i - 1
            
    prev_fb = np.array(prev_fb)
    
    return(prev_fb)
    
