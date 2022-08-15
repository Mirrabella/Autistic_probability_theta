library(data.table)

df <- fread('C:/Users/Ksenia/Desktop/events_classification_clean_final.csv') #Lera's table
path <- 'C:/Users/Ksenia/Desktop/Events/events_clean_resp_TT_CF/' #out_path

cols <- c('event[0] (time)','event[1]','event[2] (label)','response class','cur_fb')

df$`response class` <- gsub('_','',df$`response class`) #pre_risk to prerisk (delete '_')
df[cur_fb=="cur_lose",cur_fb:='negative'] #rename
df[cur_fb=="cur_rew",cur_fb:='positive']

df <- df[`response time class`=='normal' & `learning criteria`=='trained'] #filter df


for (subject in unique(df$subj)){
  for (runn in c('run1','run2','run3','run4','run5','run6')){
    for (trial_type in c('norisk','prerisk','risk','postrisk')){
      for (fb in c('negative','positive')) {

        print(paste0(subject,'_',runn,'_',trial_type,'_',fb))

        temp <- df[subj==subject & run==runn & `response class`==trial_type & cur_fb==fb, ..cols]

        cols_final <- c('event[0] (time)','event[1]','event[2] (label)')
        temp <- temp[, ..cols_final]
        temp$`event[1]` <- as.integer(temp$`event[1]`)
        temp$`event[2] (label)` <- as.integer(temp$`event[2] (label)`)
        filename <- paste0(path, subject,'_',runn,'_',trial_type,'_fb_',fb,'.txt')
        
        write.table(temp, filename, append = FALSE, sep = " ",
                      row.names = FALSE, col.names = FALSE)
        

      }
    }
  }
}
