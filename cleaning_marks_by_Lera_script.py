# Script by Valeria

import numpy as np
import copy
import mne
import pandas as pd

# P307 have on run 5, so we will 
#subjects = ['P307']
#runs = [''run1', 'run2', 'run3', 'run4', 'run6']

# autists

subjects = [
            'P301', 'P304', 'P307', 'P308', 'P309', 'P311', 'P312', 'P313', 'P314', 'P316', 'P318', 'P320', 
            'P321', 'P322', 'P323', 'P324', 'P325', 'P326', 'P327', 'P328', 'P329', 'P330', 'P331', 'P332', 
            'P333', 'P334', 'P335', 'P336', 'P338', 'P340', 'P341']

# control
#subjects = [ 
#    'P063', 'P064', 'P065', 'P066']


runs = ['run1', 'run2', 'run3', 'run4', 'run5', 'run6']


response = [40, 41, 42, 43, 44, 45, 46, 47]
norisk = [40, 41, 46, 47]
risk = [42, 43, 44, 45]
rew = [40, 41, 42, 43]
lose = [44, 45, 46, 47]
fb = [50, 51, 52, 53]
events_id = {1:'Fixation Cross', 10: 'Stimulus (left side)', 11: 'Stimulus (right side)', 20: 'Button (left)',
             21: 'Button (right)', 22: 'Button (external)', 40: 'Response REW VAL (left button)',
             41: 'Response REW VAL (right button)', 42: 'Response REW INV (left button)',
             43: 'Response REW INV (right button)', 44: 'Response LOSE VAL (left button)',
             45: 'Response LOSE VAL (right button)', 46: 'Response LOSE INV (left button)',
             47: 'Response LOSE INV (right button)', 50: 'Feedback REW VAL', 51: 'Feedback REW INV',
             52: 'Feedback LOSE VAL', 53: 'Feedback LOSE INV', 60: 'Show Bank'}
latency = {1: 23, 10:19, 11:19, 20:1, 21:1, 22:1, 40: -12, 41: -12, 42: -12, 43: -12, 44: -12, 45: -12, 46: -12, 47: -12, 50: 19, 51: 19, 52: 19, 53: 19, 60: 27}

#fname = '/net/server/data/Archive/prob_learn/vtretyakova/ICA_cleaned/{}/{}_{}_raw_ica.fif'

tab1 = np.reshape(np.array(['subj', 'run', 'event[0] (time)', 'event[1]', 'event[2] (label)', 'label type', 'added or not', 'learning criteria', 'response class', 'prev_fb', 'cur_fb', 'real time', 'response time class', 'response time']), (1, 14))
tab2 = np.reshape(np.array(['subj', 'run', 'event[0] (time)', 'event[1]', 'event[2] (label)', 'label type', 'added or not', 'learning criteria', 'response class', 'prev_fb', 'cur_fb', 'real time', 'response time class', 'response time']), (1, 14))
deleted_tab = np.reshape(np.array(['subj', 'run', 'event[0] (time)', 'event[1]', 'event[2] (label)', 'rationale']), (1, 6))


for subject in subjects:
    for run in runs:
        print(subject)
        print(run)
        try:
        
            raw = mne.io.read_raw_fif(fname.format(subject, run, subject), allow_maxshield=False, preload=True, verbose=None)

            events = mne.find_events(raw, stim_channel='STI101', output='onset', consecutive='increasing', min_duration=0, shortest_event=1, mask=None, uint_cast=False, mask_type='and', initial_event=False, verbose=None)

            #events = np.loadtxt('/net/server/data/Archive/prob_learn/data_processing/Autists/mio_free_events/{0}/{0}_{1}_mio_free.txt'.format(subject, run), dtype='int')
            initial_events = copy.deepcopy(events)

            ii = -1
            deleted = []
            reason = []

            #delete groups without FIX or stimuli from the beginning
            for i in range(len(events)-1):
                ii += 1
                if events[ii, 2] != 1:
                    if events[ii, 2] in [10, 11]:
                        if events[ii+1, 2] not in [20, 21, 40, 41, 42, 43, 44, 45, 46, 47]:
                            deleted.append(list(events[ii, :]))
                            reason.append('wrong start')
                            events = np.delete(events, (ii), axis = 0)
                            ii = ii-1
                        else:
                            break
                    else:
                        deleted.append(list(events[ii, :]))
                        reason.append('wrong start')
                        events = np.delete(events, (ii), axis = 0)
                        ii = ii-1
                else:
                    break

            ii = -1        

            #delete trash labels
            for i in range(len(events)):
                ii += 1
                if events[ii, 2] not in latency.keys():
                    deleted.append(list(events[ii, :]))
                    reason.append('wrong label')
                    events = np.delete(events, (ii), axis = 0)
                    ii = ii-1
                elif events[ii, 1] in response:
                    deleted.append(list(events[ii-1, :]))
                    reason.append('double response')
                    events = np.delete(events, (ii-1), axis = 0)
                    ii = ii-1
                elif (events[ii, 1] != 0) and (events[ii, 2] == 60):
                    deleted.append(list(events[ii, :]))
                    reason.append('bank in wrong place')
                    events = np.delete(events, (ii), axis = 0)
                    ii = ii-1
                elif events[ii, 1] in fb:
                    deleted.append(list(events[ii-1, :]))
                    reason.append('double fb')
                    events = np.delete(events, (ii-1), axis = 0)
                    ii = ii-1
                elif events[ii, 1] in [10, 11]:
                    deleted.append(list(events[ii-1, :]))
                    reason.append('double sti')
                    events = np.delete(events, (ii-1), axis = 0)
                    ii = ii-1
                elif (events[ii, 1] == 0) and (events[ii, 2] == 60) and (len(events) - ii == 2):
                    deleted.append(list(events[ii+1, :]))
                    reason.append('label after bank')
                    events = np.delete(events, (ii+1), axis = 0)
                    ii = ii-1


            deleted = np.array(deleted)
            reason = np.reshape(np.array(reason), (len(reason), 1))

            #add missing responses
            added = []
            ii = -1
            for i in range(len(events)-1):
                ii += 1
                if (events[ii, 2] in [20, 21]) and (events[ii+1, 2] in fb):
                    new = np.reshape(copy.deepcopy(events[ii, :]), (1, 3))
                    new[0, 0] = new[0, 0] + 5
                    if (events[ii, 2] == 20) and (events[ii+1, 2] == 50):
                        new[0, 2] = 40
                    elif (events[ii, 2] == 21) and (events[ii+1, 2] == 50):
                        new[0, 2] = 41
                    elif (events[ii, 2] == 20) and (events[ii+1, 2] == 51):
                        new[0, 2] = 42
                    elif (events[ii, 2] == 21) and (events[ii+1, 2] == 51):
                        new[0, 2] = 43
                    elif (events[ii, 2] == 20) and (events[ii+1, 2] == 52):
                        new[0, 2] = 44
                    elif (events[ii, 2] == 21) and (events[ii+1, 2] == 52):
                        new[0, 2] = 45
                    elif (events[ii, 2] == 20) and (events[ii+1, 2] == 53):
                        new[0, 2] = 46
                    elif (events[ii, 2] == 21) and (events[ii+1, 2] == 53):
                        new[0, 2] = 47
                    events = np.vstack((events[:ii+1, :], new, events[ii+1:, :]))
                    added.append('not')
                    added.append('added')
                    ii += 1
                else:
                    added.append('not')

            added.append('not')
            added = np.reshape(np.array(added), (len(added), 1))

            resp_only = []
            l = len(events)

            for i in range(l):
                if events[i, 2] in response:
                    resp_only.append(list(events[i, :]))
            resp_only = np.array(resp_only)

            #learning criteria
            ll = len(resp_only)
            count = 0
            good = 0
            bad = 0

            learning_time = events[l-1, 0]

            for i in range(ll):
                if resp_only[i, 2] in norisk:
                    count += 1
                    if count == 4:
                        for j in range(i+1, ll, 1):
                            if resp_only[j, 2] in norisk:
                                good += 1
                            else:
                                bad += 1
                        if ((good+bad) != 0) and (good/(good+bad)) >= 0.65:
                            learning_time = resp_only[i, 0]
                            break
                        else:
                            count = count-1
                            good = 0
                            bad = 0
                else:
                    count = 0

            learning = ['learning' for j in range(l)]

            for i in range(l-1):
                if events[i, 0] > learning_time:
                    learning[i+1] = 'trained' #+1 to exclude learning FB

            learning = np.reshape(np.array(learning), (l, 1))

            #compute real time
            real_time = copy.deepcopy(events[:, 0])

            for i in range(l):
                lab = events[i, 2]
                if lab in latency.keys():
                    real_time[i] = real_time[i] + latency.get(lab)

            #early and late responses
            early = 300
            late = 4000

            time_class = [['NA' for j in range(2)] for i in range(l)]


            for i in range(l-2):
                if (events[i, 2] in [10, 11]) and (events[i+2, 2] in response):
                    RT = real_time[i+2] - real_time[i]
                    time_class[i+2][1] = str(RT)
                    if RT < early:
                        time_class[i+2][0] = 'early'
                    elif RT > late:
                        time_class[i+2][0] = 'late'
                    else:
                        time_class[i+2][0] = 'normal'

            for i in range(l-2):
                if (events[i, 2] in [10, 11]) and (events[i+1, 2] in response):
                    RT = real_time[i+1] - real_time[i]
                    time_class[i+1][1] = str(RT)
                    if RT < early:
                        time_class[i+1][0] = 'early'
                    elif RT > late:
                        time_class[i+1][0] = 'late'
                    else:
                        time_class[i+1][0] = 'normal'

            time_class = np.array(time_class)
            real_time = np.reshape(real_time, (l, 1))

            #labels classification
            event_descriptions = ['noname' for j in range(l)]
            for i in range (len(events)):
                event_descriptions[i] = events_id.get(events[i, 2])

            responses_only = []
            times = []
            delta = []
            for i in range(l):
                if events[i, 2] in response:
                    responses_only.append(events[i, 2])
                    times.append(events[i, 0])

            for i in range(len(times)-1):
                delta.append(times[i+1]-times[i])

            #responses classification
            classes = {} 
            classes[times[0]] = 'first'

            for i in range(1, len(responses_only)-1, 1):
                if delta[i-1] > 1000:
                    if (responses_only[i-1] in norisk) and (responses_only[i] in norisk) and (responses_only[i+1] in norisk):
                        classes[times[i]] = 'no_risk'
                    elif (responses_only[i-1] in norisk) and (responses_only[i] in norisk) and (responses_only[i+1] in risk):
                        classes[times[i]] = 'pre_risk'
                    elif (responses_only[i-1] in risk) and (responses_only[i] in norisk) and (responses_only[i+1] in norisk):
                        classes[times[i]] = 'post_risk'
                    elif (responses_only[i-1] in risk) and (responses_only[i] in norisk) and (responses_only[i+1] in risk):
                        classes[times[i]] = 'post_risk and pre_risk'
                    else:
                        classes[times[i]] = 'risk'
                else:
                    classes[times[i]] = 'double'

            classes[times[len(times)-1]] = 'last'

            classes_prev_fb = {}
            classes_prev_fb[times[0]] = 'first'

            for i in range(1, len(responses_only), 1):
                if delta[i-1] > 1000:
                    if (responses_only[i-1] in rew):
                        classes_prev_fb[times[i]] = 'prev_rew'
                    else:
                        classes_prev_fb[times[i]] = 'prev_lose'
                else:
                    classes_prev_fb[times[i]] = 'double'

            classes_cur_fb = {}
            for i in range(len(responses_only)):
                if delta[i-1] > 1000:
                    if (responses_only[i] in rew):
                        classes_cur_fb[times[i]] = 'cur_rew'
                    else:
                        classes_cur_fb[times[i]] ='cur_lose'
                else:
                    classes_cur_fb[times[i]] = 'double'

            classification = [['NA' for j in range(3)]for i in range(l)]

            for i in range(l):
                if events[i, 0] in times:
                    classification[i][0] = classes.get(events[i, 0])
                    classification[i][1] = classes_prev_fb.get(events[i, 0])
                    classification[i][2] = classes_cur_fb.get(events[i, 0])

            classification = np.array(classification)
            event_descriptions = np.reshape(np.array(event_descriptions), (len(event_descriptions),1))
            subj = np.reshape(np.array([subject for j in range(l)]), (l,1))
            run1 = np.reshape(np.array([run for j in range(l)]), (l,1))

            classification = np.hstack((subj, run1, events, event_descriptions, added, learning, classification, real_time, time_class))
            initial_classification = copy.deepcopy(classification)

            #return deleted
            if deleted != []:
                other = ['to be deleted']
                for j in range(8):
                    other.append('NA')
                other = [other for i in range(len(deleted))]
                other = np.reshape(np.array(other), (len(deleted),9))

                deleted_events = np.hstack((subj[:len(deleted), :], run1[:len(deleted), :], deleted, other))
                deleted_events[:, 6] = reason[:, 0]


                for i in range(len(deleted)):
                    if int(classification[0, 2]) > deleted[i, 0]:
                        classification = np.vstack((deleted_events[i, :], classification))
                    elif int(classification[len(classification)-1, 2]) < deleted[i, 0]:
                        classification = np.vstack((classification, deleted_events[i, :]))
                    else:
                        for j in range(len(classification)-1):
                            if (int(classification[j, 2]) < deleted[i, 0]) and (deleted[i, 0] < int(classification[j+1, 2])):
                                classification = np.vstack((classification[:j+1, :], deleted_events[i, :], classification[j+1:, :]))

                deleted_events = np.hstack((subj[:len(deleted), :], run1[:len(deleted), :], deleted, reason))
                deleted_tab = np.vstack((deleted_tab, deleted_events))

            tab1 = np.vstack((tab1, initial_classification)) #clean events
            tab2 = np.vstack((tab2, classification)) #all events
        
        except (OSError):
        
            print('This file not exist') 

        
        
#save tables
columns = ['subj', 'run', 'event[0] (time)', 'event[1]', 'event[2] (label)', 'label type', 'added or not', 'learning criteria', 'response class', 'prev_fb', 'cur_fb', 'real time', 'response time class', 'response time']
final_table = pd.DataFrame(data = tab1[1:, :], index = None, columns = columns)
final_table.to_csv('/net/server/data/Archive/prob_learn/data_processing/Autists/mio_free_events/events_classification_clean.tsv', sep = '\t', float_format='%.4f')
final_table2 = pd.DataFrame(data = tab2[1:, :], index = None, columns = columns)
final_table2.to_csv('/net/server/data/Archive/prob_learn/data_processing/Autists/mio_free_events/events_classification_full.tsv', sep = '\t', float_format='%.4f')

del_columns = ['subj', 'run', 'event[0] (time)', 'event[1]', 'event[2] (label)', 'rationale']
del_table = pd.DataFrame(data = deleted_tab[1:, :], index = None, columns = del_columns)
del_table.to_csv('/net/server/data/Archive/prob_learn/data_processing/Autists/mio_free_events/deleted.tsv', sep = '\t', float_format='%.4f')   

