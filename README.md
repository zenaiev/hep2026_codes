## Матеріали курсів "Програмні коди" (магістри, 2 курс, 2026)

 <!--<details>-->
   <!--<summary> -->

#### [Записи занять](https://cernbox.cern.ch/s/AGKt3cRI6t6PQip)

  <!--</summary>-->
  Додакткові матеріали:  
  - 27.01.2026 Використовували CMS open data МК файл для процесів із ttbar та методи ROOT TTree::GetEntry(), TTree::Draw(), RdataFrame для побудови розподілів різних кінматичних змінних і обчислення ефективності обмежень на поперечний імпульс лептонів. Розбирали різницю між імперативним та декларативним стилями програмування.
     - [слайди1](https://github.com/zenaiev/hep2026_codes/blob/main/20260127/OZ_dataValidation_Top_2016.12.13.pdf) [слайди2](https://github.com/zenaiev/hep2026_codes/blob/main/20260127/cms_od_ttbar.pdf) 
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260127/play_ttbar.py)
  - 03.02.2026 Розбирали різницю між імперативним та декларативним стилями програмування. Малювали графіки кінематичних розподілів топ і антитоп кварків, рахували кореляцію між px(top) i px(antitop).
     - [слайди](https://github.com/zenaiev/hep2026_codes/blob/main/20260203/programming_styles.pdf)
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260203/play_ttbar.py)
     - Домашнє завдання: порахувати кореляцію між px(top) i px(antitop) використовуючи декларативний стиль програмування (без циклу по подіях).
  - 10.02.2026 Рахували кореляцію між px(top) i px(antitop) з використанням RDataFrame. Малювали графіки кореляцій імпульсів px, py нейтрино на генераторному рівні і МЕТ на детекторному рівні.
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260210/play_ttbar.py)
     - [ноутбук гугл коллаб](https://github.com/zenaiev/hep2026_codes/tree/main/20260210/play_ttbar.ipynb)
     - Домашнє завдання: порахувати кореляцію (до числа) між px(nu)+px(nubar) та px(MET), py(nu)+py(nubar) та py(MET).
  - 17.02.2026 Рахували кореляційні матриці для різних величин, використовували argparse.
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260217/play_ttbar.py)
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260217/corr.py)
  - 24.02.2026 Рахували метчінг20260312 (співставлення) між генераторним і реконструйованими рівнями для лептонів.
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260224/matching.py)
  - 03.03.2026 Рахували метчінг (співставлення) між генераторним і реконструйованими рівнями для лептонів, записували нове дерево, рахували кореляції та роздільну здатність.
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260303/matching.py)
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260303/corr.py)
  - 12.03.2026 Рахували метчінг (співставлення) між генераторним і реконструйованими рівнями використовуючи RDataFrame (C++ код).
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260312/matching_rdf.cxx)
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260312/matching.py)
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260312/corr.py)
  - 20.03.2026 Рахували метчінг (співставлення) для електронів і мюонів, розглядали анфолдінг TUnfold
     - [код](https://github.com/zenaiev/hep2026_codes/tree/main/20260320/matching_rdf.cxx)
     - [слайди по TUnfold](https://github.com/zenaiev/hep2026_codes/tree/main/20260320/unfolding.pdf)
  - 24.03.2026 Продовжували розглядати анфолдінг TUnfold, рахували матрицю відгуку
     - [слайди по TUnfold](https://github.com/zenaiev/hep2026_codes/tree/main/20260320/unfolding.pdf)
     - [код по TUnfold](https://github.com/zenaiev/hep2026_codes/tree/main/20260324/unfold.py)
     - [код по TUnfold](https://github.com/zenaiev/hep2026_codes/tree/main/20260324/unfold.cpp)
     - [код для матриці відгуку](https://github.com/zenaiev/hep2026_codes/tree/main/20260324/matching.py)
