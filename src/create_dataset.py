#регулярные выражения для парсинга energy

KCAL_RE = re.compile(r"Калорий\s*([\d.]+)\s*ккал", re.IGNORECASE)
PROTEIN_RE = re.compile(r"Белки\s*([\d.]+)\s*грамм", re.IGNORECASE)
FAT_RE = re.compile(r"Жиры\s*([\d.]+)\s*грамм", re.IGNORECASE)
CARBS_RE = re.compile(r"Углеводы\s*([\d.]+)\s*грамм", re.IGNORECASE)

# парсинг нутриентов

def parse_energy(raw):

    if not isinstance(raw, str):
        return np.nan, np.nan, np.nan, np.nan
    
    kcal_match = KCAL_RE.search(raw)
    protein_match = PROTEIN_RE.search(raw)
    fat_match = FAT_RE.search(raw)
    carbs_match = CARBS_RE.search(raw)
    
    calories = float(kcal_match.group(1)) if kcal_match else np.nan
    protein = float(protein_match.group(1)) if protein_match else np.nan
    fat = float(fat_match.group(1)) if fat_match else np.nan
    carbs = float(carbs_match.group(1)) if carbs_match else np.nan
    
    return calories, protein, fat, carbs


# парсинг ингредиентов

ITEM_SEP = "|"

def parse_ingredients(raw):

    if not isinstance(raw, str) or not raw.strip():
        return []
    
    items = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk or ":" not in chunk:
            continue
        
        name, _amount = chunk.split(":", 1)
        name = name.strip().strip(".").lower()
        
        if not name:
            continue
        
        items.append(name)
    
    return items

def ingredients_to_string(items):
    return ITEM_SEP.join(items)

def ingredients_from_string(raw):
    if not isinstance(raw, str) or not raw:
        return []
    return [name for name in raw.split(ITEM_SEP) if name]

# распаковка и упаковка файлов датасета
INPUT_PATH = "../data/original/food-dataset-ru.csv" 
OUTPUT_PATH = "../data/processed/rus_recipes_clean.csv"
OUTPUT_PATH_NO_OUTLIERS = "../data/processed/rus_recipes_clean_final.csv"
OUTPUT_PATH_PARQ = "../data/processed/rus_recipes_clean_final.parquet"

df = pd.read_csv(INPUT_PATH)

parsed_energy = df["energy"].apply(parse_energy)
df["calories"] = parsed_energy.apply(lambda x: x[0])
df["protein_g"] = parsed_energy.apply(lambda x: x[1])
df["fat_g"] = parsed_energy.apply(lambda x: x[2])
df["carbs_g"] = parsed_energy.apply(lambda x: x[3])

parsed_ing = df["ingredient"].apply(parse_ingredients)
df["ingredients_list"] = parsed_ing.apply(ingredients_to_string)
df["ingredients_count"] = parsed_ing.apply(len)

# формирование  датасета

final_cols = [
    "name",
    "label", 
    "ingredients_list",
    "calories",
    "protein_g",
    "fat_g",
    "carbs_g",
]


result = df[final_cols].rename(columns={"label": "dish_type"})

result = result.drop_duplicates(subset=["name", "ingredients_list"]).reset_index(drop=True)

result = result.dropna(subset=["calories", "protein_g", "fat_g", "carbs_g", "ingredients_list"])

result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
result.to_parquet(OUTPUT_PATH_PARQ, index=False)

