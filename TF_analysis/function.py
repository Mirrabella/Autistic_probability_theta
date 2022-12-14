import mne
import os
import os.path as op
import numpy as np
import pandas as pd
from scipy import stats
import copy
import statsmodels.stats.multitest as mul

###################################################################################################################
# функция получения эпох с выделенными частотами с применение раннего логарифмирования, сразу после сложения частот
def make_freq_signal(subj, r, cond, fb, data_path, L_freq, H_freq, f_step, period_start, period_end, baseline, n_cycles, events, events_response, time_bandwidth = 4):
    freqs = np.arange(L_freq, H_freq, f_step)
    # если только одна метка, т.е. одна эпоха, то выдается ошибка, поэтому приводи shape к виду (N,3)
    if events_response.shape == (3,):
        events_response = events_response.reshape(1,3)


    raw_fname = op.join(data_path, '{0}/run{1}_{0}_raw_ica.fif'.format(subj, r))

    raw_data = mne.io.Raw(raw_fname, preload=True)


    picks = mne.pick_types(raw_data.info, meg = True, eog = True)


    #epochs for baseline
    # baseline = None, чтобы не вычитался дефолтный бейзлайн
    epochs = mne.Epochs(raw_data, events, event_id = None, tmin = -1.0, tmax = 1.0, baseline = None, picks = picks, preload = True)
    epochs.resample(300)


    freq_show_baseline = mne.time_frequency.tfr_multitaper(epochs, freqs = freqs, n_cycles = n_cycles, time_bandwidth = time_bandwidth, use_fft = False, return_itc = False, average=False).crop(tmin=baseline[0], tmax=baseline[1], include_tmax=True) #frequency of baseline

    #add up all values according to the frequency axis
    b_line = freq_show_baseline.data.sum(axis=-2)

    # логарифмируем данные для бейзлайн и получаем бейзлайн в дБ
    b_line = 10*np.log10(b_line)

    # Для бейзлайна меняем оси местами, на первом месте число каналов
    b_line = np.swapaxes(b_line, 0, 1)

    # выстраиваем в ряд бейзлайны для каждого из эвентов, как будто они происходили один за другим
    a, b, c = b_line.shape

    b_line_ave = b_line.reshape(a, b * c)

    # Усредняем бейзлайн по всем точкам, получаем одно число (которое будем вычитать из data для каждого канала) (то же самое если вместо смены осей усреднить сначала по времени, а потом по эпохам)

    b = b_line_ave.mean(axis=-1)

    b_line_new_shape = b[:, np.newaxis, np.newaxis]  


    ####### ДЛЯ ДАННЫХ ##############
    # baseline = None, чтобы не вычитался дефолтный бейзлайн
    epochs = mne.Epochs(raw_data, events_response, event_id = None, tmin = period_start, 
                                tmax = period_end, baseline = None, picks = picks, preload = True)

    epochs.resample(300) 

    freq_show = mne.time_frequency.tfr_multitaper(epochs, freqs = freqs, n_cycles = n_cycles, time_bandwidth = time_bandwidth, use_fft = False, return_itc = False, average=False)

    temp = freq_show.data.sum(axis=2)

    # логарифмируем данные и получаем данные в дБ
    temp = 10*np.log10(temp)

    ####### Для данных так же меняем оси местами
    data = np.swapaxes(temp, 0, 1)
    data = np.swapaxes(data, 1, 2)


    #Вычитаем из данных в дБ бейзлайн в дБ
    data_dB = data - b_line_new_shape 

    # меняем оси обратно   
    data_dB = np.swapaxes(data_dB, 1, 2)
    data_dB = np.swapaxes(data_dB, 0, 1)


    freq_show.data = data_dB[:, :, np.newaxis, :]

    #freq_show.data = freq_show.data[:, :, np.newaxis, :]

    #33 is an arbitrary number. We have to set some frequency if we want to save the file
    freq_show.freqs = np.array([33])

    #getting rid of the frequency axis	
    freq_show.data = freq_show.data.mean(axis=2) 

    epochs_tfr = mne.EpochsArray(freq_show.data, freq_show.info, tmin = period_start, events = events_response)
            
    return (epochs_tfr)   

    
##########################################################################################################   
########################### Получение комбинированных планаров для эпох  ################################# 
   
def combine_planar_Epoches_TFR(EpochsTFR, tmin):
	ep_TFR_planar1 = EpochsTFR.copy(); 
	ep_TFR_planar2 = EpochsTFR.copy()
	ep_TFR_planar1.pick_types(meg='planar1')
	ep_TFR_planar2.pick_types(meg='planar2')

	#grad_RMS = np.power((np.power(evk_planar1.data, 2) + np.power(evk_planar2.data, 2)), 1/2)
	combine = ep_TFR_planar1.get_data() + ep_TFR_planar2.get_data()
	ep_TFR_combined = mne.EpochsArray(combine, ep_TFR_planar1.info, tmin = tmin, events = EpochsTFR.events)

	return ep_TFR_combined #возвращает эпохи, которые можно сохранить .fif в файл

#############################################################################################################	
##############################  Получение комбинированных планаров для Evoked  ###############################	
def combine_planar_Evoked(evoked):
	planar1 = evoked.copy(); 
	planar2 = evoked.copy()
	planar1.pick_types(meg='planar1')
	planar2.pick_types(meg='planar2')

	#grad_RMS = np.power((np.power(evk_planar1.data, 2) + np.power(evk_planar2.data, 2)), 1/2)
	combined = planar1.data + planar2.data
	
	return planar1, planar2, combined #возвращает планары, которые можно сохранить .fif в файл и np.array() из суммы планаров

###########################################################################################################	
################################ Сборка таблицы для LMEM ###############################
    
def make_subjects_df(combined_planar, s, subj, r, t, fb_cur, tmin, tmax, step, scheme, times_list, cl, feedback_prev_data):

    
    time_intervals = np.arange(tmin, tmax, step)
    list_of_time_intervals = []
    i = 0
    while i < (len(time_intervals) - 1):
        interval = time_intervals[i:i+2]
        list_of_time_intervals.append(interval)
        #print(interval)
        i = i+1
    
    list_of_beta_power = []    
    for i in list_of_time_intervals:
        combined_planar_in_interval = combined_planar.copy()
        combined_planar_in_interval = combined_planar_in_interval.crop(tmin=i[0], tmax=i[1], include_tmax=True)

        mean_combined_planar = combined_planar_in_interval.get_data().mean(axis=-1)
    
        beta_power = []

        for j in range(len(mean_combined_planar)):
            a = mean_combined_planar[j][s]
            beta_power.append(a)
        list_of_beta_power.append(beta_power)
    
    trial_number = range(len(mean_combined_planar))
    
    subject = [subj]*len(mean_combined_planar)
    run = ['run{0}'.format(r)]*len(mean_combined_planar)
    trial_type = [t]*len(mean_combined_planar)
    feedback_cur = [fb_cur]*len(mean_combined_planar)
    
    # путь к предыдущему фб описывается вне функции
    
    if feedback_prev_data.shape == (3,):
        feedback_prev_data = feedback_prev_data.reshape(1,3)
    
    FB_rew = [50, 51]
    FB_lose = [52, 53]

    feedback_prev = []
    for i in feedback_prev_data:
        if i[2] in FB_rew:
            a = 'positive'
            
        else:
            a = 'negative'
            
        feedback_prev.append(a)
        
    #print(len(feedback_prev))
    #print(len(mean_combined_planar))   
        
    # схема подкрепления   
    a = scheme.loc[(scheme['fname'] == subj) & (scheme['block'] == r)]['scheme'].tolist()[0]
    sch = [a]*len(mean_combined_planar)
    
    criterion_learning = [cl]*len(mean_combined_planar)
    
       
    
    df = pd.DataFrame()
    
    
    df['trial_number'] = trial_number
    
    # beta на интервалах
    for idx, beta in enumerate(list_of_beta_power):
        df['beta power %s'%list_of_time_intervals[idx]] = beta
    

    #df['beta_power'] = beta_power
    df['subject'] = subject
    df['round'] = run
    df['trial_type'] = trial_type
    df['criterion_learning'] = criterion_learning
    df['feedback_cur'] = feedback_cur
    df['feedback_prev'] = feedback_prev
    df['scheme'] = sch
    df['times_of_response'] = times_list
        
    return (df)
    
###############################################################################################    
############################ FUNCTION FOR TTEST ############################
######################### парный ttest #########################################

def ttest_pair(data_path, subjects, parameter1, parameter2, freq_range, planar, n): # n - количество временных отчетов
	contr = np.zeros((len(subjects), 2, 102, n))

	for ind, subj in enumerate(subjects):
		temp1 = mne.Evoked(op.join(data_path, '{0}_{1}_evoked_{2}_resp_{3}.fif'.format(subj, parameter1, freq_range, planar)))
		temp2 = mne.Evoked(op.join(data_path, '{0}_{1}_evoked_{2}_resp_{3}.fif'.format(subj, parameter2, freq_range, planar)))
		

		contr[ind, 0, :, :] = temp1.data
		contr[ind, 1, :, :] = temp2.data
		
	comp1 = contr[:, 0, :, :]
	comp2 = contr[:, 1, :, :]
	t_stat, p_val = stats.ttest_rel(comp2, comp1, axis=0)

	comp1_mean = comp1.mean(axis=0)
	comp2_mean = comp2.mean(axis=0)
	
	return t_stat, p_val, comp1_mean, comp2_mean

#############################################################################
##################### непарный ttest #######################################	
def ttest_vs_zero(data_path, subjects, parameter1, freq_range, planar, n): # n - количество временных отчетов
	contr = np.zeros((len(subjects), 1, 102, n))

	for ind, subj in enumerate(subjects):
		temp1 = mne.Evoked(op.join(data_path, '{0}_{1}_evoked_{2}_resp_{3}.fif'.format(subj, parameter1, freq_range, planar)))
		
		contr[ind, 0, :, :] = temp1.data
				
	comp1 = contr[:, 0, :, :]
	t_stat, p_val = stats.ttest_1samp(comp1, 0, axis=0)

	comp1_mean = comp1.mean(axis=0)
		
	return t_stat, p_val, comp1_mean	

##############################################################################################
#################################### FDR CORRECTION ########################################

############ space FDR for each sensor independently ######################################
def space_fdr(p_val_n):
    #print(p_val_n.shape)
    temp = copy.deepcopy(p_val_n)
    for i in range(temp.shape[1]):
        _, temp[:,i] = mul.fdrcorrection(p_val_n[:,i])
    return temp


################## Full FDR -the correction is made once for the intire data array ############
def full_fdr(p_val_n):
    s = p_val_n.shape
    #print(p_val_n.shape)
    temp = copy.deepcopy(p_val_n)
    pval = np.ravel(temp)
    _, pval_fdr = mul.fdrcorrection(pval)
    pval_fdr_shape = pval_fdr.reshape(s)
    return pval_fdr_shape

################ make binary dataframe from pvalue (0 or 1) #########################
def p_val_binary(p_val_n, treshold):
	p_val =  copy.deepcopy(p_val_n)
	for raw in range(p_val.shape[0]):
		for collumn in range(p_val.shape[1]):
			if p_val[raw, collumn] < treshold:
				p_val[raw, collumn] = 1
			else:
				p_val[raw, collumn] = 0
	return p_val


###########################################################################################################
######################################### PLOT TOPOMAPS  ################################################

###################### строим topomaps со статистикой, для разницы между условиями #########################
# temp - donor (see "temp1" in def ttest_pair)
# mean1, mean2 - Evoked average between subjects (see def ttest_pair)
# average - averaging in mne.plot_topomaps

def plot_deff_topo(p_val, temp, mean1, mean2, time_to_plot, title): 	
    #Если мы будем использовать донор Evoked из тех, которые усредняются, то время и так будет то, которое необходимо, тогда менять время нет необходимости и присваиваем только новые данные (see temp.data)
    '''
	temp.first = -206
	temp.last = 1395

	temp.times = np.arange(-0.206, 1.395, 0.001)
    '''
	
    binary = p_val_binary(p_val, treshold = 0.05)
    temp.data = mean2 - mean1

	#temp_shift = temp.shift_time(-0.600, relative=False)
	
    fig1 = temp.plot_topomap(times = time_to_plot, ch_type='planar1', scalings = 1, average=0.2, units = 'dB', show = False, time_unit='s', title = title);
    fig2 = temp.plot_topomap(times = time_to_plot, ch_type='planar1', scalings = 1, average=0.2, units = 'dB', show = False, vmin = -1.2, vmax = 1.2, time_unit='s', title = title, colorbar = True, extrapolate = "local", mask = np.bool_(binary), mask_params = dict(marker='o',			markerfacecolor='white', markeredgecolor='k', linewidth=0, markersize=7, markeredgewidth=2))



    return fig1, fig2, temp # temp - "Evoked" for difference mean1 and mean2, which can be save if it is needed   

###################### строим topomaps со статистикой, для разницы между условиями #########################

def plot_topo_vs_zero(p_val, temp, mean1, time_to_plot, title): 	
    #Если мы будем использовать донор Evoked из тех, которые усредняются, то время и так будет то, которое необходимо, тогда менять время нет необходимости и присваиваем только новые данные (see temp.data)
    '''
	temp.first = -206
	temp.last = 1395

	temp.times = np.arange(-0.206, 1.395, 0.001)
    '''
	
    binary = p_val_binary(p_val, treshold = 0.05)
    temp.data = mean1

	#temp_shift = temp.shift_time(-0.600, relative=False)
	
	#fig1 = temp.plot_topomap(times = time_to_plot, ch_type='planar1', average=0.2, show = False,  vmin = -5.0, vmax = 5.0, time_unit='ms', title = title);
    fig = temp.plot_topomap(times = time_to_plot, ch_type='planar1', scalings = 1, average=0.2, units = 'dB', show = False, vmin = -4.5, vmax = 4.5, time_unit='s', title = title, colorbar = True, extrapolate = "local", mask = np.bool_(binary), mask_params = dict(marker='o',		markerfacecolor='white', markeredgecolor='k', linewidth=0, markersize=7, markeredgewidth=2))



    return fig, temp # temp - "Evoked" , which can be save if it is needed   

########################################################################          
##############  empty topomaps line (without color) ##################



# загружаем донора (любой Evoked с комбинированными планарами или одним планаром - чтобы было 102 сеносора). 
n = 17 # количество говов в ряду

# задаем временные точнки, в которых будем строить головы, затем мы присвоим их для донора (template)
times_array = np.array([-0.8, -0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4])

def nocolor_topomaps_line (n, temp, times_array ):
  
    df = np.zeros((102, 17))
    temp.data = df

    # задаем временные точки в которые мы будем строить головы
    temp.times = times_array

    return temp        

