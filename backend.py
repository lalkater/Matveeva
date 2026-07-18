import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib

# загрузка датасета
recipes = pd.read_parquet("data/processed/rus_recipes_clean_final.parquet")
# создание понятных для модели типов блюд
meal_map = {
    'Завтрак': 'breakfast',
    'Суп': 'lunch',
    'Бульон': 'lunch',
    'Основное блюдо': 'dinner',
    'Выпечка': 'dessert',
    'Закуска': 'snack',
    'Салат': 'snack',
    'Напиток': 'other',
    'Соус': 'other',
    'Заготовка': 'other',
    'Паста или пицца': 'dinner',
    'Сэндвич': 'snack',
    'Ризотто': 'dinner',
}
recipes['meal_type'] = recipes['dish_type'].map(meal_map).fillna('other')


# подготовка ингредиентов
recipes['ingredients_str'] = recipes['ingredients_list'].apply(lambda x: ' '.join(x) if isinstance(x, list) else str(x))

# загрузка обученых моделей
models = joblib.load('model/rf_models.pkl')
# загрузка векторизатора
tfidf = joblib.load('model/tfidf_rf.pkl')

# инфорация о признаках
feature_info = joblib.load('model/feature_info.pkl')
X_rf_columns = feature_info['X_rf_columns']
meal_type_dummies_columns = feature_info['meal_type_dummies_columns']
numeric_features = feature_info['numeric_features']

meal_type_dummies = pd.DataFrame(columns=meal_type_dummies_columns)

models = joblib.load('model/rf_models.pkl')
print(type(models))
print(models.keys() if isinstance(models, dict) else "Not a dict")


# функция, отвечающая нужно ли заменить блюдо

def change_recipe(recipe, user_goal):
 
    calories = recipe['calories']
    protein = recipe['protein_g']
    fat = recipe['fat_g']
    carbs = recipe['carbs_g']
# вычисление кбжу в пропорциях
    total = protein + fat + carbs
    if total == 0:
        return {
            'verdict': 'Нет данных',
            'reason': 'Не удалось вычислить пропорции',
            'score': 0,
            'ratios': {'protein': 0, 'fat': 0, 'carbs': 0}
        }
    
    protein_pct = (protein/total) * 100
    fat_pct = (fat/total) * 100
    carbs_pct = (carbs/total) * 100
    
    
    ratios = {
        'protein_pct': protein_pct,
        'fat_pct': fat_pct,
        'carbs_pct': carbs_pct,
        'total': total,
        'calories': calories
    }
    
# пропорции для каждой цели
    
    if user_goal == 'weight_loss':
        if protein_pct >= 30 and fat_pct <= 30 and carbs_pct <= 30 and calories<=600:
            return {
                'verdict': 'Отлично подходит',
                'reason': f'Белки: {protein_pct:.0f}%, Жиры: {fat_pct:.0f}%, Углеводы: {carbs_pct:.0f}% — отличный баланс для похудения',
                'score': 95,
                'ratios': ratios
            }
        elif protein_pct >= 25 and fat_pct <= 35 and calories<=600:
            return {
                'verdict': 'Подходит',
                'reason': f'Хорошее соотношение: белки {protein_pct:.0f}% доминируют, жиры {fat_pct:.0f}% в норме',
                'score': 80,
                'ratios': ratios
            }
        elif protein_pct >= 25 and fat_pct <= 40 and calories<=600:
            return {
                'verdict': 'Условно подходит',
                'reason': f'Белков {protein_pct:.0f}%, жиров {fat_pct:.0f}% — стоит увеличить белок и снизить жиры',
                'score': 55,
                'ratios': ratios
            }
        else:
            reasons = []
            if protein_pct < 25:
                reasons.append(f'Мало белка ({protein_pct:.0f}%)')
            if fat_pct > 40:
                reasons.append(f'Много жиров ({fat_pct:.0f}%)')
            if carbs_pct > 40:
                reasons.append(f'Много углеводов ({carbs_pct:.0f}%)')
            if calories>600:
                reasons.append(f'Калорийно ({carbs_pct:.0f})')
            return {
                'verdict': 'Требуется замена',
                'reason': ', '.join(reasons) if reasons else 'Несбалансированное соотношение БЖУ',
                'score': 20,
                'ratios': ratios
            }
    
    elif user_goal == 'muscle_gain':
        if protein_pct >= 35 and 20 <= fat_pct <= 35 and 20 <= carbs_pct <= 35 and 300 <= calories <= 1000:
            return {
                'verdict': 'Отлично подходит',
                'reason': f'Белки: {protein_pct:.0f}%, Жиры: {fat_pct:.0f}%, Углеводы: {carbs_pct:.0f}% — идеально для роста мышц',
                'score': 95,
                'ratios': ratios
            }
        elif protein_pct >= 30 and 15 <= fat_pct <= 40 and 300 <= calories <= 1000:
            return {
                'verdict': 'Подходит',
                'reason': f'Хороший белок ({protein_pct:.0f}%), умеренные жиры и углеводы',
                'score': 75,
                'ratios': ratios
            }
        elif protein_pct >= 25 and fat_pct <= 45 and 300 <= calories <= 1000:
            return {
                'verdict': 'Условно подходит',
                'reason': f'Белков {protein_pct:.0f}% — стоит увеличить долю белка',
                'score': 50,
                'ratios': ratios
            }
        else:
            reasons = []
            if protein_pct < 25:
                reasons.append(f'Мало белка ({protein_pct:.0f}%)')
            if fat_pct > 45:
                reasons.append(f'Много жиров ({fat_pct:.0f}%)')
            if carbs_pct > 50:
                reasons.append(f'Много углеводов ({carbs_pct:.0f}%)')
            if calories>1000:
                reasons.append(f'Калорийно ({carbs_pct:.0f})')
            return {
                'verdict': 'Требуется замена',
                'reason': ', '.join(reasons) if reasons else 'Несбалансированное соотношение БЖУ',
                'score': 20,
                'ratios': ratios
            }
    
    elif user_goal == 'maintenance':
        if 25 <= protein_pct <= 35 and 25 <= fat_pct <= 35 and 30 <= carbs_pct <= 40 and calories <= 800:
            return {
                'verdict': 'Отлично подходит',
                'reason': f'Белки: {protein_pct:.0f}%, Жиры: {fat_pct:.0f}%, Углеводы: {carbs_pct:.0f}% — идеальный баланс',
                'score': 95,
                'ratios': ratios
            }
        elif 20 <= protein_pct <= 40 and 20 <= fat_pct <= 40 and calories <= 800:
            return {
                'verdict': 'Подходит',
                'reason': f'Сбалансированное питание: белки {protein_pct:.0f}%, жиры {fat_pct:.0f}%, углеводы {carbs_pct:.0f}%',
                'score': 75,
                'ratios': ratios
            }
        else:
            reasons = []
            if protein_pct < 20:
                reasons.append(f'Мало белка ({protein_pct:.0f}%)')
            if protein_pct > 45:
                reasons.append(f'Много белка ({protein_pct:.0f}%)')
            if fat_pct < 15:
                reasons.append(f'Мало жиров ({fat_pct:.0f}%)')
            if fat_pct > 45:
                reasons.append(f'Много жиров ({fat_pct:.0f}%)')
            if carbs_pct > 50:
                reasons.append(f'Много углеводов ({carbs_pct:.0f}%)')
            if carbs_pct < 20:
                reasons.append(f'Мало углеводов ({carbs_pct:.0f}%)')
            if calories>800:
                reasons.append(f'Калорийно ({carbs_pct:.0f})')
            return {
                'verdict': 'Стоит пересмотреть',
                'reason': ', '.join(reasons) if reasons else 'Несбалансированное соотношение БЖУ',
                'score': 40,
                'ratios': ratios
            }
    
    elif user_goal == 'low_carb':

        if carbs_pct <= 20 and protein_pct >= 35 and 30 <= fat_pct <= 50 and calories <= 900:
            return {
                'verdict': 'Отлично подходит',
                'reason': f'Углеводы: {carbs_pct:.0f}%, Белки: {protein_pct:.0f}%, Жиры: {fat_pct:.0f}% — идеально для кето/низкоуглеводной',
                'score': 95,
                'ratios': ratios
            }
        elif carbs_pct <= 30 and protein_pct >= 30 and calories <= 900:
            return {
                'verdict': 'Подходит',
                'reason': f'Умеренное содержание углеводов ({carbs_pct:.0f}%), хороший белок ({protein_pct:.0f}%)',
                'score': 75,
                'ratios': ratios
            }
        elif carbs_pct <= 40 and protein_pct >= 25 and calories <= 900:
            return {
                'verdict': 'Условно подходит',
                'reason': f'Углеводов {carbs_pct:.0f}% — стоит снизить их долю для лучшего результата',
                'score': 50,
                'ratios': ratios
            }
        else:
            reasons = []
            if carbs_pct > 40:
                reasons.append(f'Много углеводов ({carbs_pct:.0f}%)')
            if protein_pct < 25:
                reasons.append(f'Мало белка ({protein_pct:.0f}%)')
            if calories>900:
                reasons.append(f'Калорийно ({carbs_pct:.0f})')
            return {
                'verdict': 'Требуется замена',
                'reason': ', '.join(reasons) if reasons else 'Не подходит для низкоуглеводной диеты',
                'score': 20,
                'ratios': ratios
            }
    
    return {
        'verdict': 'Неизвестная цель',
        'reason': 'Пожалуйста, выберите одну из целей',
        'score': 0,
        'ratios': ratios
    }




# FastAPI
app = FastAPI(title="Рекомендации блюд")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# какие данные ожидаем  
class Request(BaseModel):
    recipe_name: str
    meal_type: str
    user_goal: str
    n_recommendations: int = 3

@app.post("/recommend")
async def recommend(req: Request):

    filtered = recipes[recipes['meal_type'] == req.meal_type].copy()
    if len(filtered) == 0:
        filtered = recipes.copy()
    
    original = None
    mask = filtered['name'].str.contains(req.recipe_name, case=False, na=False)
    if mask.any():
        original = filtered[mask].iloc[0].to_dict()
    
    evaluation = None
    if original is not None:
        evaluation = change_recipe(original, req.user_goal)
    
    X_ingredients = tfidf.transform(filtered['ingredients_str'])
    ingredients_df = pd.DataFrame(
        X_ingredients.toarray(),
        columns=[f'ing_{i}' for i in range(X_ingredients.shape[1])],
        index=filtered.index
    )
    
    meal_type_dummies_filtered = pd.get_dummies(filtered['meal_type'], prefix='meal')
    for col in meal_type_dummies_columns:
        if col not in meal_type_dummies_filtered.columns:
            meal_type_dummies_filtered[col] = 0
    
    X_filtered = pd.concat([
        filtered[numeric_features],
        meal_type_dummies_filtered,
        ingredients_df
    ], axis=1).fillna(0)
    
    for col in X_rf_columns:
        if col not in X_filtered.columns:
            X_filtered[col] = 0
    X_filtered = X_filtered[X_rf_columns]

    model = models[req.user_goal]
    predictions = model.predict(X_filtered)
    probabilities = model.predict_proba(X_filtered)[:, 1]
    
    filtered['suitable'] = predictions
    filtered['prob'] = probabilities
    
    suitable = filtered[filtered['suitable'] == 1].sort_values('prob', ascending=False)
    if original is not None:
        suitable = suitable[suitable['name'] != original['name']]
    
    recommendations = []
    for _, row in suitable.head(req.n_recommendations).iterrows():
        ingredients = row.get('ingredients_list', [])
        
        if isinstance(ingredients, str):
            try:

                ingredients = [x.strip() for x in ingredients.split('|') if x.strip()]
            except:
                ingredients = [ingredients]
        elif not isinstance(ingredients, list):
            ingredients = []
        
        ingredients_display = ingredients
        rec = {
            'name': row['name'],
            'prob': float(row['prob']),
            'calories': float(row['calories']),
            'protein': float(row['protein_g']),
            'fat': float(row['fat_g']),
            'carbs': float(row['carbs_g']),
            'ingredients': ingredients_display
        }
        recommendations.append(rec)
    
    return {
        'original': original,
        'evaluation': evaluation,
        'recommendations': recommendations,
        'total': len(suitable)
    }


@app.get("/")
async def root():
    return {"message": "работает", "goals": list(models.keys())}

@app.get("/health")
async def health():
    return {"status": "healthy", "models_loaded": True}

if __name__ == "__main__":
    import uvicorn
    print("  СЕРВЕР ЗАПУЩЕН!")
    print("   http://localhost:8000")
    print("   http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
