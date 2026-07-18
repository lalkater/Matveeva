import streamlit as st
import requests

st.set_page_config(
    page_title="Food Help",

)

st.title("Питайся вкусно и полезно!")
st.subheader("Введите блюдо, и мы подскажем заменить его или нет")
recipe_name = st.text_input(
        "Название блюда",
        placeholder="Например: Куриный суп"
    )
meal_type = st.selectbox(
        "Тип блюда",
        ["breakfast", "lunch", "dinner", "dessert", "snack"],
        format_func=lambda x: {
            'breakfast': 'завтрак',
            'lunch': 'суп',
            'dinner': 'основное блюдо',
            'dessert': 'десерт',
            'snack': 'перекус'
        }[x]
    )
user_goal = st.selectbox(
        "Ваша цель",
        ["weight_loss", "muscle_gain", "maintenance", "low_carb"],
        format_func=lambda x: {
            'weight_loss': 'похудение',
            'muscle_gain': 'набор мышц',
            'maintenance': 'поддержание',
            'low_carb': 'низкоуглеводная'
        }[x]
    )
    
n_rec = st.slider("Количество замен", 1, 5, 1)



if st.button("Посмотреть рекомендации", type="primary", use_container_width=True):
    
    if not recipe_name:
        st.warning("Пожалуйста, введите название блюда!")
        st.stop()
    
    try:
        requests.get("http://localhost:8000/", timeout=1)
    except:
        st.error("Сервер не запущен!")
        st.stop()
    
    with st.spinner("Анализируем блюдо..."):
        try:
            response = requests.post(
                "http://localhost:8000/recommend",
                json={
                    "recipe_name": recipe_name,
                    "meal_type": meal_type,
                    "user_goal": user_goal,
                    "n_recommendations": n_rec
                },
                timeout=10
            )
            
            if response.status_code != 200:
                st.error(f"Ошибка сервера: {response.status_code}")
                st.stop()
            
            data = response.json()
            
        except Exception as e:
            st.error(f"Ошибка: {str(e)}")
            st.stop()
    
    
    original = data.get('original')
    evaluation = data.get('evaluation')
    recommendations = data.get('recommendations', [])
    total = data.get('total', 0)
    
    if original is None:
        st.warning(f"Блюдо {recipe_name} не найдено в датасете, попробуйте изменить тип")
        st.stop()
    
    st.subheader("Ваше блюдо")
    
    cols = st.columns(4)
    cols[0].metric("Калории", f"{original['calories']:.0f} ккал")
    cols[1].metric("Белки", f"{original['protein_g']:.1f} г")
    cols[2].metric("Жиры", f"{original['fat_g']:.1f} г")
    cols[3].metric("Углеводы", f"{original['carbs_g']:.1f} г")
    

    st.markdown("---")
    st.subheader("Рекомендации для вас")
    
    if evaluation:
        verdict = evaluation['verdict']
        reason = evaluation['reason']
        score = evaluation['score']
        
        if score>55:
            color = "#65B81D"
  
        elif score==55 :
            color = "#F0B800"

        else:
            color = "#FF4B4B"

    

    if evaluation and score>55:
        st.markdown(f"""
        <div style="background-color: #f0ffe3; border-radius:10px; padding:20px; margin:10px 0; border: 2px solid {color};">
            <h3 style="color:{color};">{verdict}</h3>
            <p><strong>{reason}</p>
            <p>{original['name']} идеально подходит для вашей цели! Замены не требуются.</p>
        </div>
        """, unsafe_allow_html=True)

    elif evaluation and score<55:
        st.markdown(f"""
        <div style="background-color: #fff1f0; border-radius:10px; padding:20px; margin:10px 0; border: 2px solid {color};">
            <h3 style="color:{color};">{verdict}</h3>
            <p><strong>{reason}</p>
            <p>{original['name']} не совсем подходит для вашей цели.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if recommendations:

            st.subheader("Рекомендуемые замены")
            st.markdown(f"*Найдено {len(recommendations)} замен из {total} подходящих*")
            
            for i, rec in enumerate(recommendations, 1):
                prob = rec['prob'] * 100
                
                with st.container():
                    st.markdown(f"""
                    <div style="background-color:#f8f9fa; border-radius:10px; padding:15px; margin:10px 0; border: 2px solid #F0F2F6;">
                        <h4>{i}. {rec['name']}</h4>
                        <p style="color:#65B81D; font-weight:bold;">{prob:.1f}% вероятность</p>
                        <p>{rec['calories']:.0f} ккал   |   белки: {rec['protein']:.1f}г   |   жиры: {rec['fat']:.1f}г   |   углеводы: {rec['carbs']:.1f}г</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if rec.get('ingredients'):
                        with st.expander(f"Ингредиенты", expanded=True):
                            for ing in rec['ingredients']:
                                st.write(f"• {ing}")
                    else:
                        with st.expander(f"Ингредиенты", expanded=False):
                            st.write("Нет данных об ингредиентах")
        else:
            st.info("Не найдено подходящих замен. Попробуйте другие параметры.")
    

    elif evaluation and score==55:
        st.markdown(f"""
        <div style="background-color: #fff8e0; border-radius:10px; padding:20px; margin:10px 0; border: 2px solid {color};">
            <h3 style="color:{color};">{verdict}</h3>
            <p><strong>{reason}</p>
            <p>{original['name']} подходит, но можно найти и лучше.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if recommendations:
            st.subheader("Улучшенные варианты")
            
            for i, rec in enumerate(recommendations[:2], 1):
                prob = rec['prob'] * 100
                st.markdown(f"""
                <div style="background-color:#f8f9fa; border-radius:10px; padding:15px; margin:10px 0; border: 2px solid #F0F2F6;">
                    <h4>{i}. {rec['name']}</h4>
                    <p style="color:#65B81D; font-weight:bold;">{prob:.1f}% вероятность</p>
                    <p>{rec['calories']:.0f} ккал   |   белки: {rec['protein']:.1f}г   |   жиры: {rec['fat']:.1f}г   |   углеводы: {rec['carbs']:.1f}г</p>
                </div>
                """, unsafe_allow_html=True)
                if rec.get('ingredients'):
                        with st.expander(f"Ингредиенты", expanded=True):
                            for ing in rec['ingredients']:
                                st.write(f"• {ing}")
                else:
                    with st.expander(f"Ингредиенты", expanded=False):
                            st.write("Нет данных об ингредиентах")