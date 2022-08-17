# -*- coding: utf-8 -*-
"""
Spyder Editor

Удаление пустых файлов, т.е. тех для которых не нашлось нужных эвентов
"""

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
remove_files = []
for subj in subjects:
    for r in rounds:
    
        for t in trial_type:
            for fb in feedback:
                
                try:
                    
                    # загружаем массив эвентов, разбитые по условиям
                    events_by_cond = np.loadtxt('/home/vtretyakova/Рабочий стол/probabitily_teta/trained/{0}_run{1}_{2}_fb_{3}.txt'.format(subj, r, t, fb), dtype='int')
                    
                    if events_by_cond.size == 0:
                        os.remove('/home/vtretyakova/Рабочий стол/probabitily_teta/trained/{0}_run{1}_{2}_fb_{3}.txt'.format(subj, r, t, fb))
                        #print('File removed successfully')
                        name_remove = f'{subj} run{r} {t} {fb}'
                        remove_files.append(name_remove)
                except OSError:
                    
                    print(f'{subj} run{r} {t} {fb} not exist')
print(remove_files)                    
