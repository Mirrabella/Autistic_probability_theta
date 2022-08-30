import mne
import os
import os.path as op
import numpy as np
from function import make_freq_signal


L_freq = 2
H_freq = 8
f_step = 1

time_bandwidth = 4 #(by default = 4)
# if delta (1 - 4 Hz) 
#n_cycles = np.array([1, 1, 1, 2]) # уточнить

#for others
freqs = np.arange(L_freq, H_freq, f_step)
n_cycles = freqs//2

period_start = -1.750
period_end = 2.750

baseline = (-0.35, -0.05)

freq_range = 'theta_4_7_trf_early_log'

description = 'Theta, И для данных и для бейзлайн логарифмирование проводим на самых ранных этапах - сразу после суммирования по частотам.'

subjects = ['P301', 'P304', 'P307', 'P308', 'P309', 'P311', 'P312', 'P313', 'P314', 'P316', 'P318', 'P320', 
            'P321', 'P322', 'P323', 'P324', 'P325', 'P326', 'P327', 'P328', 'P329', 'P330', 'P331', 'P332', 
            'P333', 'P334', 'P335', 'P336', 'P338', 'P340', 'P341', 'P342']
   

rounds = [1, 2, 3, 4, 5, 6]
trial_type = ['norisk', 'prerisk', 'risk', 'postrisk']

feedback = ['positive', 'negative']

data_path = '/net/server/data/Archive/prob_learn/vtretyakova/ICA_cleaned'
os.makedirs('/net/server/mnt/Archive/prob_learn/data_processing/theta_4_7/Sensors/Autists/{0}'.format(freq_range), exist_ok = True)
os.makedirs('/net/server/mnt/Archive/prob_learn/data_processing/theta_4_7/Sensors/Autists/{0}/{0}_epo'.format(freq_range), exist_ok = True)

########################## Обязательно делать файл, в котором будет показано какие параметры были заданы, иначе проверить вводные никак нельзя, а это необходимо при возникновении некоторых вопросов ############################################

lines = ["freq_range = {}".format(freq_range), description, "L_freq = {}".format(L_freq), "H_freq = {}, в питоне последнее число не учитывается, т.е. по факту частота (H_freq -1) ".format(H_freq), "f_step = {}".format(f_step), "time_bandwidth = {}".format(time_bandwidth), "period_start = {}".format(period_start), "period_end = {}".format(period_end), "baseline = {}".format(baseline)]


with open("/net/server/mnt/Archive/prob_learn/data_processing/theta_4_7/Sensors/Autists/{0}/{0}_epo/config.txt".format(freq_range), "w") as file:
    for  line in lines:
        file.write(line + '\n')


##############################################################################################################


for subj in subjects:
    for r in rounds:
        for cond in trial_type:
            for fb in feedback:
                    #read events
                    #events for baseline
                    # download marks of positive feedback

                try:
                    events_pos = np.loadtxt("/net/server/mnt/Archive/prob_learn/data_processing/fix_cross_mio_corr/{0}_run{1}_norisk_fb_cur_positive_fix_cross.txt".format(subj, r), dtype='int')

                    # если только одна метка, т.е. одна эпоха, то выдается ошибка, поэтому приводим shape к виду (N,3)
                    if events_pos.shape == (3,):
                        events_pos = events_pos.reshape(1,3)


                except (OSError):
                    print('There is no positive fb in norisk %s, run %s'% (subj, r))
                    events_pos = np.empty((0,3), dtype="int")

                     # download marks of negative feedback   
                try:

                    events_neg = np.loadtxt("/net/server/mnt/Archive/prob_learn/data_processing/fix_cross_mio_corr/{0}_run{1}_norisk_fb_cur_negative_fix_cross.txt".format(subj, r), dtype='int')
                    if events_neg.shape == (3,):
                        events_neg = events_neg.reshape(1,3)


                except (OSError):
                    print('There is no negative fb in norisk %s, %s'% (subj, r))
                    events_neg = np.empty((0,3), dtype="int")

                    #объединяем негативные и позитивные фидбеки для получения общего бейзлайна по ним, и сортируем массив, чтобы времена меток шли в порядке возрастания    
                events = np.vstack([events_pos, events_neg])
                events = np.sort(events, axis = 0)
                
                
                if events.size == 0:
                    print('Jump to next condition, there is nothing to catch')

                else:
                    try:

                        #events, which we need
                        events_response = np.loadtxt('/net/server/mnt/Archive/prob_learn/data_processing/events_trained_by_cond_WITH_mio_corrected/{0}_run{1}_{2}_fb_cur_{3}.txt'.format(subj, r, cond, fb), dtype='int')
                        
                        epochs_tfr = make_freq_signal(subj, r, cond, fb, data_path, L_freq, H_freq, f_step, period_start, period_end, baseline, n_cycles, events, events_response, time_bandwidth = time_bandwidth)
                        epochs_tfr.save('/net/server/mnt/Archive/prob_learn/data_processing/theta_4_7/Sensors/Autists/{0}/{0}_epo/{1}_run{2}_{3}_fb_cur_{4}_{0}_epo.fif'.format(freq_range, subj, r, cond, fb), overwrite=True)
                 
                    except (OSError):
                        print(f'{subj} run{r} {cond} {fb} not exist')

