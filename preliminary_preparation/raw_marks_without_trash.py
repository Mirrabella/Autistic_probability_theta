import numpy as np
import pandas as pd

# load table with classification events without trash marks (by Lera Scavronskaya script probability_final.ipynb) or cleaning_marks_by_Lera_script.py

table = pd.read_csv('/net/server/data/Archive/prob_learn/data_processing/Events_no_mio_cleaned/events_classification_clean.tsv', sep = '\t')

#create unique lists of subjects and runs
subjects = set(table['subj'].tolist())
runs = set(table['run'].tolist())

for subj in subjects:
    for r in runs:
        subj_table = table.loc[(table['subj'] == subj) & (table['run'] == r)]
        
        first = subj_table['event[0] (time)'].tolist()
        second = subj_table['event[1]'].tolist()
        third = subj_table['event[2] (label)'].tolist()
        
        all_events = []
        for i in range(len(subj_table)):
            event = []
            event.append(first[i])
            event.append(second[i])
            event.append(third[i])
            all_events.append(event) 
            
        all_ev_array = np.array(all_events)
        
        np.savetxt("/net/server/data/Archive/prob_learn/data_processing/Raw_events_without_trash_marks/{0}_{1}_events_clean.txt".format(subj, r), all_ev_array,  fmt="%s")
        
        
        #load txt
        #ontent = np.loadtxt('/home/vtretyakova/Рабочий стол/probabitily_teta/test.txt', dtype='int')       
        
        

