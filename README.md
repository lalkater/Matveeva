# Food Help
Ссылка на дневник прогресса проекта: https://docs.google.com/document/d/1UF996Of--UMqBKKjPl14SZO6-HvwY3EQDDTpUERZUoU/edit?usp=sharing

ссылка на датасет: https://www.kaggle.com/datasets/vlad15lav/recipes-corpus-textual-data-for-nlprecsys
Был выбран, потому что в нем есть колонка "тип кухни" и КБЖУ, поэтому из него легко взять только русские рецепты

Используемый алгоритм - Random Forest
гиперпараметры и метрики для каждой модели:
```
Параметры:
Количество деревьев: 300
Максимальная глубина: 25
Минимальное число объектов в узле: 2
____________________________________________________________
  похудение
  Test F1: 0.9182
  Test Recall: 0.9166
  Test Precision: 0.9198
____________________________________________________________
  набор мышц
  Test F1: 0.8996
  Test Recall: 0.9060
  Test Precision: 0.8934
____________________________________________________________
  поддержание веса
  Test F1: 0.8532
  Test Recall: 0.8713
  Test Precision: 0.8358
____________________________________________________________
  lкето-диета
  Test F1: 0.9399
  Test Recall: 0.9425
  Test Precision: 0.9372
```

Структура проекта

```
food-change/
│
├── .venv/
├── data/
│   ├── original/                           # исходные данные
│   │   └── food-dataset-ru.csv             # датасет с рецептами 
│   └── processed/                          # обработанные данные
│       ├── rus_recipes_clean.csv           # после очистки (CSV)
│       └── rus_recipes_clean_final.parquet # Parquet
├── models/                                 # сохранённые модели
│   ├──  rf_models.pkl                      # обученные Random Forest модели
│   ├──  tfidf_rf.pkl                       # TF-IDF векторизатор
│   └──  feature_info.pkl                   # информация о признаках
├──  notebooks/                             # Jupyter ноутбуки
│   └──  rf-change-food.ipynb               # обучение Random Forest моделей
├──  src/                                   # функции для python
│   ├──  __init__.py                        # делает папку пакетом
│   └──  create_dataset.py                  # функции для обработки данных
├──  backend.py                             # бэкенд на FastAPI  
├──  frontend.py                            # фронтенд на Streamlit
├──  .gitignore                             # файлы, игнорируемые Git
├──  README.md                              # описание проекта
└──  requirements.txt                       # библиотеки
```
