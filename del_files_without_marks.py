# -*- coding: utf-8 -*-
"""
Spyder Editor

Удаление пустых файлов, т.е. тех для которых не нашлось нужных эвентов
"""

import os
import os.path as op
import numpy as np

subjects = []
for i in range(0,63):
    if i < 10:
        subjects += ['P00' + str(i)]
    else:
        subjects += ['P0' + str(i)]
        


rounds = [1, 2, 3, 4, 5, 6]


trial_type = ['norisk', 'prerisk', 'risk', 'postrisk']

feedback = ['positive', 'negative']

for subj in subjects:
    for r in rounds:
    
        for t in trial_type:
            for fb in feedback:
                
                try:
                    
                    # загружаем массив эвентов, разбитые по условиям
                    events_by_cond = np.loadtxt('/home/vtretyakova/Рабочий стол/probability_learning/marks_extraction/events_clean_resp_not_trained/{0}_run{1}_{2}_fb_{3}.txt'.format(subj, r, t, fb), dtype='int')
                    
                    if events_by_cond.size == 0:
                        os.remove('/home/vtretyakova/Рабочий стол/probability_learning/marks_extraction/events_clean_resp_not_trained/{0}_run{1}_{2}_fb_{3}.txt'.format(subj, r, t, fb))
                        print('File removed successfully')
                except OSError:
                    
                    print('This file not exist')
                    
