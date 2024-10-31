# Kerbal Space Program: Kerbin to Eve
Autopilot for the game Kerbal Space Program for flying from 'Kerbin to Eve' implemented using kRPC 0.5.4

## Kerbal Space Program: От Кербина до Евы
Репозиторий содержит код для автопилота, выполняющего полет с поверхности Кербина до Евы и выход на её круговую орбиту


### Ракета созданная для выполнения полёта в Kerbal Space Program
Основной модуль

![image](https://github.com/user-attachments/assets/67ee34d9-aeb1-4774-9136-142da10e3bf4)

Ракета в целом

![image](https://github.com/user-attachments/assets/ef05902f-72da-44f2-bc5a-b74517cf9c03)

Файл с моделью [ракеты](_KSP_project_rocket.craft)


### Программы 
Программы для автопилота для полета с Кербина на Еву написаны на языке **Python** с использованием библиотеки **kRPC**
- Программа главного файла [автопилота запускающего подпрограммы](KSP_proj.py)
- Программа для [расчета времени ожидания до стартового окна и угла выхода с орбиты Кербина](KTE/angle_calculation.py)
- Программа для [выхода на орбиту Кербина](KTE/orbital_launch.py)
- Программа для [изменения орбиты вокруг Кербина на круговую](KTE/circularization.py)
- Программа для [выполнения Гомановского перехода между орбитами Кербина и Евы](KTE/interorbital_flight.py)
- Программа для [корректирования Гомановского перехода, чтобы попасть в SOI Евы](KTE/correction_node.py)
- Программа для [замедления рядом с Евой и выхода на её круговую орбиту](KTE/slowdown.py)
- Программа для [отображения уведомлений в консоль и вывода их в игре](KTE/notification.py)
  
### Ссылка на видеоотчет на YouTube







