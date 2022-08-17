# Autistic_probability_theta

***Частотно - временной анализ, общий порядок***  
**Предварительная подготовка**
0. **function.py** - 

1. ICA - удаление сердечных артефактов и морганий
2. **cleaning_marks_by_Lera_script.py** Чистка меток 
3. **raw_marks_without_trash.py** Получение списков меток очищенных от "мусорных" меток
4. **extract_events_from_table.R** Сортируем метки из таблицы, полученной в п.2 по choice types и знаку фидбека (скрипт от Ксении Сайфулиной)
5. **del_files_without_marks.py** - удаляем пустые файлы (если в этом фидбэке, либо в этом choice type не было ни одного трайла
6. **mio_cleaning_for_cond_events.py** - 
