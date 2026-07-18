# Food Help
ссылка на датасет: https://www.kaggle.com/datasets/vlad15lav/recipes-corpus-textual-data-for-nlprecsys
Был выбран, потому что в нем есть колонка "тип кухни" и КБЖУ, поэтому из него легко взять только русские рецепты

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
├──  tests/                                 # тесты
├──  backend.py                             # бэкенд на FastAPI  
├──  frontend.py                            # фронтенд на Streamlit
├──  .gitignore                             # файлы, игнорируемые Git
├──  README.md                              # описание проекта
└──  requirements.txt                       # библиотеки
```
