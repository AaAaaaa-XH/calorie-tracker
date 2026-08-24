import streamlit as st
import json
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="卡路里追踪器", page_icon="🍎", layout="wide")

FOOD_DB = {
    "🍚 主食": {
        "米饭": {"cal": 116, "emoji": "🍚", "protein": 2.6, "fat": 0.3, "carbs": 25.6},
        "面条": {"cal": 110, "emoji": "🍜", "protein": 3.5, "fat": 0.5, "carbs": 23.0},
        "馒头": {"cal": 221, "emoji": "🍞", "protein": 7.0, "fat": 1.1, "carbs": 47.0},
        "包子": {"cal": 227, "emoji": "🥟", "protein": 8.0, "fat": 2.0, "carbs": 30.0},
        "饺子": {"cal": 186, "emoji": "🥟", "protein": 9.0, "fat": 3.0, "carbs": 25.0},
        "粥": {"cal": 46, "emoji": "🥣", "protein": 1.0, "fat": 0.1, "carbs": 10.0},
        "面包": {"cal": 265, "emoji": "🍞", "protein": 8.0, "fat": 3.2, "carbs": 49.0},
        "油条": {"cal": 386, "emoji": "🥖", "protein": 6.0, "fat": 17.0, "carbs": 51.0},
        "煎饼": {"cal": 233, "emoji": "🥞", "protein": 8.0, "fat": 5.0, "carbs": 38.0},
        "烧饼": {"cal": 260, "emoji": "🫓", "protein": 7.0, "fat": 2.0, "carbs": 50.0},
        "红薯": {"cal": 86, "emoji": "🍠", "protein": 1.6, "fat": 0.1, "carbs": 20.0},
        "玉米": {"cal": 96, "emoji": "🌽", "protein": 3.2, "fat": 1.2, "carbs": 19.0},
    },
    "🥩 肉类": {
        "鸡胸肉": {"cal": 133, "emoji": "🍗", "protein": 31.0, "fat": 1.2, "carbs": 0},
        "鸡腿": {"cal": 181, "emoji": "🍗", "protein": 16.0, "fat": 13.0, "carbs": 0},
        "猪肉": {"cal": 242, "emoji": "🥩", "protein": 13.2, "fat": 37.0, "carbs": 0},
        "牛肉": {"cal": 125, "emoji": "🥩", "protein": 26.1, "fat": 3.7, "carbs": 0},
        "羊肉": {"cal": 203, "emoji": "🍖", "protein": 19.0, "fat": 14.0, "carbs": 0},
        "排骨": {"cal": 264, "emoji": "🍖", "protein": 18.0, "fat": 20.0, "carbs": 0},
        "培根": {"cal": 405, "emoji": "🥓", "protein": 12.0, "fat": 37.0, "carbs": 1.0},
        "香肠": {"cal": 301, "emoji": "🌭", "protein": 12.0, "fat": 25.0, "carbs": 2.0},
        "火腿": {"cal": 155, "emoji": "🍖", "protein": 16.0, "fat": 10.0, "carbs": 1.0},
    },
    "🐟 海鲜": {
        "鱼肉": {"cal": 96, "emoji": "🐟", "protein": 20.4, "fat": 3.2, "carbs": 0},
        "虾": {"cal": 87, "emoji": "🦐", "protein": 20.4, "fat": 1.7, "carbs": 0.1},
        "螃蟹": {"cal": 95, "emoji": "🦀", "protein": 18.0, "fat": 2.0, "carbs": 0},
        "三文鱼": {"cal": 139, "emoji": "🍣", "protein": 21.0, "fat": 6.0, "carbs": 0},
        "金枪鱼": {"cal": 130, "emoji": "🐟", "protein": 29.0, "fat": 1.0, "carbs": 0},
    },
    "🥚 蛋奶豆": {
        "鸡蛋": {"cal": 144, "emoji": "🥚", "protein": 12.6, "fat": 9.5, "carbs": 0.7},
        "牛奶": {"cal": 42, "emoji": "🥛", "protein": 3.4, "fat": 1.0, "carbs": 5.0},
        "酸奶": {"cal": 72, "emoji": "🥛", "protein": 3.5, "fat": 2.7, "carbs": 7.0},
        "豆腐": {"cal": 80, "emoji": "🧊", "protein": 8.0, "fat": 4.0, "carbs": 1.0},
        "豆浆": {"cal": 31, "emoji": "🥛", "protein": 2.8, "fat": 0.5, "carbs": 3.5},
        "奶酪": {"cal": 328, "emoji": "🧀", "protein": 25.0, "fat": 24.0, "carbs": 1.0},
    },
    "🥬 蔬菜": {
        "白菜": {"cal": 13, "emoji": "🥬", "protein": 1.2, "fat": 0.1, "carbs": 2.2},
        "生菜": {"cal": 15, "emoji": "🥬", "protein": 1.4, "fat": 0.2, "carbs": 2.9},
        "菠菜": {"cal": 23, "emoji": "🥬", "protein": 2.9, "fat": 0.4, "carbs": 3.6},
        "番茄": {"cal": 18, "emoji": "🍅", "protein": 0.9, "fat": 0.2, "carbs": 3.9},
        "黄瓜": {"cal": 15, "emoji": "🥒", "protein": 0.7, "fat": 0.1, "carbs": 3.6},
        "胡萝卜": {"cal": 41, "emoji": "🥕", "protein": 0.9, "fat": 0.2, "carbs": 9.6},
        "土豆": {"cal": 76, "emoji": "🥔", "protein": 2.0, "fat": 0.1, "carbs": 17.5},
        "西兰花": {"cal": 34, "emoji": "🥦", "protein": 2.8, "fat": 0.4, "carbs": 6.6},
        "茄子": {"cal": 25, "emoji": "🍆", "protein": 1.0, "fat": 0.2, "carbs": 6.0},
        "青椒": {"cal": 20, "emoji": "🫑", "protein": 0.9, "fat": 0.2, "carbs": 4.6},
        "洋葱": {"cal": 39, "emoji": "🧅", "protein": 1.1, "fat": 0.1, "carbs": 9.3},
        "蘑菇": {"cal": 22, "emoji": "🍄", "protein": 3.1, "fat": 0.3, "carbs": 3.3},
        "玉米": {"cal": 86, "emoji": "🌽", "protein": 3.2, "fat": 1.2, "carbs": 19.0},
    },
    "🍎 水果": {
        "苹果": {"cal": 52, "emoji": "🍎", "protein": 0.3, "fat": 0.2, "carbs": 13.8},
        "香蕉": {"cal": 89, "emoji": "🍌", "protein": 1.1, "fat": 0.3, "carbs": 22.8},
        "橙子": {"cal": 47, "emoji": "🍊", "protein": 0.9, "fat": 0.1, "carbs": 11.8},
        "葡萄": {"cal": 69, "emoji": "🍇", "protein": 0.7, "fat": 0.2, "carbs": 18.1},
        "西瓜": {"cal": 30, "emoji": "🍉", "protein": 0.6, "fat": 0.2, "carbs": 7.6},
        "草莓": {"cal": 32, "emoji": "🍓", "protein": 0.7, "fat": 0.3, "carbs": 7.7},
        "蓝莓": {"cal": 57, "emoji": "🫐", "protein": 0.7, "fat": 0.3, "carbs": 14.5},
        "芒果": {"cal": 60, "emoji": "🥭", "protein": 0.8, "fat": 0.4, "carbs": 15.0},
        "桃子": {"cal": 39, "emoji": "🍑", "protein": 0.9, "fat": 0.3, "carbs": 9.5},
        "梨": {"cal": 57, "emoji": "🍐", "protein": 0.4, "fat": 0.1, "carbs": 15.2},
        "猕猴桃": {"cal": 61, "emoji": "🥝", "protein": 1.1, "fat": 0.5, "carbs": 14.7},
        "樱桃": {"cal": 50, "emoji": "🍒", "protein": 1.0, "fat": 0.3, "carbs": 12.2},
    },
    "🍕 中式菜品": {
        "红烧肉": {"cal": 490, "emoji": "🍖", "protein": 15.0, "fat": 40.0, "carbs": 2.0},
        "番茄炒蛋": {"cal": 98, "emoji": "🍳", "protein": 7.0, "fat": 8.0, "carbs": 4.0},
        "宫保鸡丁": {"cal": 180, "emoji": "🍗", "protein": 15.0, "fat": 12.0, "carbs": 5.0},
        "麻婆豆腐": {"cal": 130, "emoji": "🌶️", "protein": 8.0, "fat": 10.0, "carbs": 3.0},
        "回锅肉": {"cal": 250, "emoji": "🥩", "protein": 14.0, "fat": 20.0, "carbs": 4.0},
        "鱼香肉丝": {"cal": 190, "emoji": "🐟", "protein": 12.0, "fat": 14.0, "carbs": 6.0},
        "青椒肉丝": {"cal": 170, "emoji": "🫑", "protein": 13.0, "fat": 12.0, "carbs": 5.0},
        "蒜苔炒肉": {"cal": 155, "emoji": "🧄", "protein": 11.0, "fat": 10.0, "carbs": 6.0},
        "干煸豆角": {"cal": 120, "emoji": "🫛", "protein": 5.0, "fat": 8.0, "carbs": 8.0},
        "酸辣土豆丝": {"cal": 95, "emoji": "🥔", "protein": 2.0, "fat": 5.0, "carbs": 12.0},
        "清炒时蔬": {"cal": 45, "emoji": "🥬", "protein": 2.0, "fat": 3.0, "carbs": 4.0},
        "蛋炒饭": {"cal": 180, "emoji": "🍚", "protein": 5.0, "fat": 7.0, "carbs": 24.0},
        "炒面": {"cal": 160, "emoji": "🍜", "protein": 5.0, "fat": 6.0, "carbs": 22.0},
        "水煮鱼": {"cal": 170, "emoji": "🐟", "protein": 18.0, "fat": 10.0, "carbs": 2.0},
        "糖醋排骨": {"cal": 280, "emoji": "🍖", "protein": 15.0, "fat": 18.0, "carbs": 15.0},
        "可乐鸡翅": {"cal": 215, "emoji": "🍗", "protein": 14.0, "fat": 12.0, "carbs": 12.0},
    },
    "🍔 西式快餐": {
        "汉堡": {"cal": 254, "emoji": "🍔", "protein": 12.0, "fat": 12.0, "carbs": 24.0},
        "薯条": {"cal": 312, "emoji": "🍟", "protein": 3.4, "fat": 15.0, "carbs": 41.0},
        "炸鸡": {"cal": 280, "emoji": "🍗", "protein": 18.0, "fat": 18.0, "carbs": 10.0},
        "披萨": {"cal": 266, "emoji": "🍕", "protein": 11.0, "fat": 10.0, "carbs": 33.0},
        "意面": {"cal": 131, "emoji": "🍝", "protein": 5.0, "fat": 1.5, "carbs": 25.0},
        "三明治": {"cal": 250, "emoji": "🥪", "protein": 12.0, "fat": 10.0, "carbs": 28.0},
        "热狗": {"cal": 290, "emoji": "🌭", "protein": 10.0, "fat": 18.0, "carbs": 24.0},
        "炸薯条": {"cal": 312, "emoji": "🍟", "protein": 3.4, "fat": 15.0, "carbs": 41.0},
    },
    "🍜 日韩料理": {
        "寿司": {"cal": 143, "emoji": "🍣", "protein": 6.0, "fat": 2.0, "carbs": 26.0},
        "拉面": {"cal": 125, "emoji": "🍜", "protein": 5.0, "fat": 3.0, "carbs": 20.0},
        "咖喱饭": {"cal": 155, "emoji": "🍛", "protein": 5.0, "fat": 6.0, "carbs": 20.0},
        "石锅拌饭": {"cal": 175, "emoji": "🍚", "protein": 6.0, "fat": 5.0, "carbs": 28.0},
        "泡菜": {"cal": 32, "emoji": "🥬", "protein": 2.0, "fat": 0.5, "carbs": 5.0},
        "紫菜包饭": {"cal": 140, "emoji": "🍙", "protein": 4.0, "fat": 3.0, "carbs": 24.0},
    },
    "🧋 饮品": {
        "可乐": {"cal": 43, "emoji": "🥤", "protein": 0, "fat": 0, "carbs": 10.6},
        "奶茶": {"cal": 65, "emoji": "🧋", "protein": 1.0, "fat": 2.0, "carbs": 11.0},
        "咖啡": {"cal": 2, "emoji": "☕", "protein": 0.1, "fat": 0, "carbs": 0},
        "果汁": {"cal": 45, "emoji": "🧃", "protein": 0.5, "fat": 0, "carbs": 11.0},
        "啤酒": {"cal": 43, "emoji": "🍺", "protein": 0.5, "fat": 0, "carbs": 3.6},
        "红酒": {"cal": 85, "emoji": "🍷", "protein": 0.1, "fat": 0, "carbs": 2.6},
        "柠檬水": {"cal": 20, "emoji": "🍋", "protein": 0.1, "fat": 0, "carbs": 5.0},
    },
    "🍰 甜点零食": {
        "蛋糕": {"cal": 347, "emoji": "🍰", "protein": 4.0, "fat": 18.0, "carbs": 46.0},
        "巧克力": {"cal": 546, "emoji": "🍫", "protein": 5.0, "fat": 31.0, "carbs": 61.0},
        "饼干": {"cal": 466, "emoji": "🍪", "protein": 5.0, "fat": 20.0, "carbs": 66.0},
        "冰淇淋": {"cal": 207, "emoji": "🍦", "protein": 3.5, "fat": 11.0, "carbs": 24.0},
        "薯片": {"cal": 536, "emoji": "🍿", "protein": 5.0, "fat": 35.0, "carbs": 50.0},
        "坚果": {"cal": 607, "emoji": "🥜", "protein": 20.0, "fat": 50.0, "carbs": 20.0},
        "果冻": {"cal": 70, "emoji": "🍮", "protein": 0.5, "fat": 0, "carbs": 17.0},
    },
    "🥣 粥汤": {
        "白粥": {"cal": 46, "emoji": "🥣", "protein": 1.0, "fat": 0.1, "carbs": 10.0},
        "皮蛋瘦肉粥": {"cal": 78, "emoji": "🥣", "protein": 4.5, "fat": 2.0, "carbs": 10.0},
        "番茄蛋汤": {"cal": 35, "emoji": "🍲", "protein": 2.5, "fat": 2.0, "carbs": 2.5},
        "紫菜蛋花汤": {"cal": 28, "emoji": "🍲", "protein": 2.0, "fat": 1.5, "carbs": 2.0},
        "排骨汤": {"cal": 65, "emoji": "🍲", "protein": 5.0, "fat": 4.0, "carbs": 2.0},
    },
}

ACTIVITY_DB = {
    "🏃 有氧运动": {
        "跑步": {"met": 8.0, "emoji": "🏃"},
        "快走": {"met": 5.0, "emoji": "🚶"},
        "游泳": {"met": 6.0, "emoji": "🏊"},
        "骑车": {"met": 7.5, "emoji": "🚴"},
        "跳绳": {"met": 10.0, "emoji": "🤸"},
        "跳舞": {"met": 5.0, "emoji": "💃"},
        "爬山": {"met": 7.0, "emoji": "🧗"},
        "打球": {"met": 5.5, "emoji": "🏀"},
    },
    "💪 力量训练": {
        "健身": {"met": 6.0, "emoji": "💪"},
        "瑜伽": {"met": 3.0, "emoji": "🧘"},
        "普拉提": {"met": 3.5, "emoji": "🧘"},
        "引体向上": {"met": 8.0, "emoji": "💪"},
        "俯卧撑": {"met": 8.0, "emoji": "💪"},
    },
    "🏠 日常活动": {
        "走路": {"met": 3.5, "emoji": "🚶"},
        "做家务": {"met": 3.5, "emoji": "🧹"},
        "办公": {"met": 1.5, "emoji": "💻"},
        "看电视": {"met": 1.0, "emoji": "📺"},
        "睡觉": {"met": 0.8, "emoji": "😴"},
    },
}

DAILY_TARGET = {'calories': 2000, 'protein': 65, 'fat': 60, 'carbs': 300, 'fiber': 25}

def load_data():
    data_file = Path('calorie_data.json')
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open('calorie_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_all_foods():
    foods = {}
    for category, items in FOOD_DB.items():
        for name, info in items.items():
            foods[name] = info
    return foods

def get_all_activities():
    activities = {}
    for category, items in ACTIVITY_DB.items():
        for name, info in items.items():
            activities[name] = info
    return activities

st.markdown("""
<style>
.food-card {
    padding: 10px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin: 5px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("🍎 卡路里追踪器")
st.caption("记录饮食 · 追踪营养 · 健康生活")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🍽️ 记录饮食", "🏃 记录运动", "📊 营养查询", "📈 今日统计", "💡 饮食建议"])

with tab1:
    st.subheader("选择食物")
    
    selected_category = st.selectbox("选择分类", list(FOOD_DB.keys()))
    
    foods_in_category = FOOD_DB[selected_category]
    
    cols = st.columns(4)
    selected_food = None
    for i, (name, info) in enumerate(foods_in_category.items()):
        with cols[i % 4]:
            if st.button(f"{info['emoji']} {name}\n{info['cal']}千卡/100g", key=f"food_{name}", use_container_width=True):
                selected_food = name
                st.session_state.selected_food = name
    
    if 'selected_food' in st.session_state:
        food_name = st.session_state.selected_food
        food_info = get_all_foods()[food_name]
        
        st.info(f"已选择: {food_info['emoji']} **{food_name}** ({food_info['cal']}千卡/100g)")
        
        food_weight = st.slider("重量(g)", 10, 500, 100, key="food_weight")
        
        if st.button("✓ 添加记录", type="primary"):
            data = load_data()
            today = datetime.now().strftime('%Y-%m-%d')
            if today not in data:
                data[today] = {'intake': [], 'burn': []}
            cal = food_info['cal'] * food_weight / 100
            data[today]['intake'].append({
                'food': food_name, 
                'weight_g': food_weight, 
                'calories': round(cal, 1),
                'emoji': food_info['emoji']
            })
            save_data(data)
            st.success(f"✓ 已记录: {food_info['emoji']} {food_name} {food_weight}g = {cal:.1f}千卡")
            del st.session_state.selected_food
            st.rerun()

with tab2:
    st.subheader("选择运动")
    
    selected_act_category = st.selectbox("选择分类", list(ACTIVITY_DB.keys()))
    
    acts_in_category = ACTIVITY_DB[selected_act_category]
    
    cols = st.columns(4)
    for i, (name, info) in enumerate(acts_in_category.items()):
        with cols[i % 4]:
            if st.button(f"{info['emoji']} {name}\nMET={info['met']}", key=f"act_{name}", use_container_width=True):
                st.session_state.selected_act = name
    
    if 'selected_act' in st.session_state:
        act_name = st.session_state.selected_act
        act_info = get_all_activities()[act_name]
        
        st.info(f"已选择: {act_info['emoji']} **{act_name}** (MET={act_info['met']})")
        
        duration = st.slider("时长(分钟)", 5, 180, 30, key="act_duration")
        
        calories_burned = act_info['met'] * 65 * duration / 60
        
        st.info(f"预计消耗: 🔥 **{calories_burned:.1f}千卡**")
        
        if st.button("✓ 添加记录", type="primary", key="add_act"):
            data = load_data()
            today = datetime.now().strftime('%Y-%m-%d')
            if today not in data:
                data[today] = {'intake': [], 'burn': []}
            data[today]['burn'].append({
                'activity': act_name, 
                'duration': duration, 
                'calories': round(calories_burned, 1),
                'emoji': act_info['emoji']
            })
            save_data(data)
            st.success(f"✓ 已记录: {act_info['emoji']} {act_name} {duration}分钟 = {calories_burned:.1f}千卡")
            del st.session_state.selected_act
            st.rerun()

with tab3:
    st.subheader("查询食物营养")
    
    query_category = st.selectbox("选择分类", list(FOOD_DB.keys()), key="q_cat")
    
    query_food = st.selectbox("选择食物", list(FOOD_DB[query_category].keys()), key="q_food")
    
    query_weight = st.slider("重量(g)", 10, 500, 100, key="q_weight")
    
    if st.button("查询", key="query_btn"):
        food_info = FOOD_DB[query_category][query_food]
        f = query_weight / 100
        
        st.markdown(f"### {food_info['emoji']} {query_food} ({query_weight}g)")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("热量", f"{food_info['cal']*f:.1f}", "千卡")
        col2.metric("蛋白质", f"{food_info['protein']*f:.1f}", "g")
        col3.metric("脂肪", f"{food_info['fat']*f:.1f}", "g")
        col4.metric("碳水", f"{food_info['carbs']*f:.1f}", "g")
        
        total = food_info['protein']*f + food_info['fat']*f + food_info['carbs']*f
        if total > 0:
            protein_pct = food_info['protein']*f / total * 100
            fat_pct = food_info['fat']*f / total * 100
            carbs_pct = food_info['carbs']*f / total * 100
            
            st.progress(protein_pct/100, text=f"蛋白质: {protein_pct:.0f}%")
            st.progress(fat_pct/100, text=f"脂肪: {fat_pct:.0f}%")
            st.progress(carbs_pct/100, text=f"碳水: {carbs_pct:.0f}%")

with tab4:
    st.subheader("今日统计")
    
    data = load_data()
    today = datetime.now().strftime('%Y-%m-%d')
    today_data = data.get(today, {'intake': [], 'burn': []})
    
    total_intake = sum(r['calories'] for r in today_data['intake'])
    total_burn = sum(r['calories'] for r in today_data['burn'])
    net = total_intake - total_burn
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🍽️ 总摄入", f"{total_intake:.1f} 千卡", f"{len(today_data['intake'])}次")
    col2.metric("🔥 总消耗", f"{total_burn:.1f} 千卡", f"{len(today_data['burn'])}次")
    col3.metric("📊 净摄入", f"{net:.1f} 千卡")
    
    st.progress(min(total_intake / DAILY_TARGET['calories'], 1.0), 
                text=f"热量进度: {total_intake:.0f}/{DAILY_TARGET['calories']}千卡")
    
    if today_data['intake']:
        st.subheader("🍽️ 摄入记录")
        for r in today_data['intake']:
            emoji = r.get('emoji', '🍽️')
            st.write(f"{emoji} **{r['food']}**: {r['weight_g']}g = {r['calories']}千卡")
    
    if today_data['burn']:
        st.subheader("🔥 运动记录")
        for r in today_data['burn']:
            emoji = r.get('emoji', '🏃')
            st.write(f"{emoji} **{r['activity']}**: {r['duration']}分钟 = {r['calories']}千卡")
    
    if today_data['intake']:
        st.subheader("📊 营养分析")
        daily = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
        for r in today_data['intake']:
            all_foods = get_all_foods()
            if r['food'] in all_foods:
                info = all_foods[r['food']]
                f = r['weight_g'] / 100
                daily['calories'] += info['cal'] * f
                daily['protein'] += info['protein'] * f
                daily['fat'] += info['fat'] * f
                daily['carbs'] += info['carbs'] * f
        
        names = {'calories':'热量', 'protein':'蛋白质', 'fat':'脂肪', 'carbs':'碳水'}
        for k, target in DAILY_TARGET.items():
            if k in daily:
                actual = daily[k]
                ratio = actual / target * 100
                status = "✅ 充足" if 80 <= ratio <= 120 else "⚠️ 偏低" if ratio < 80 else "⚠️ 偏高"
                st.write(f"**{names.get(k,k)}**: {actual:.1f}/{target} ({ratio:.0f}%) {status}")

with tab5:
    st.subheader("💡 饮食建议")
    
    goal = st.radio("选择目标", ["健康饮食", "减脂", "增肌"], horizontal=True)
    
    data = load_data()
    today = datetime.now().strftime('%Y-%m-%d')
    today_data = data.get(today, {'intake': [], 'burn': []})
    
    if today_data['intake']:
        daily = {'calories': 0, 'protein': 0, 'fat': 0, 'carbs': 0}
        for r in today_data['intake']:
            all_foods = get_all_foods()
            if r['food'] in all_foods:
                info = all_foods[r['food']]
                f = r['weight_g'] / 100
                daily['calories'] += info['cal'] * f
                daily['protein'] += info['protein'] * f
                daily['fat'] += info['fat'] * f
                daily['carbs'] += info['carbs'] * f
        
        st.markdown("### 📋 今日建议")
        
        if goal == "减脂":
            st.info("🎯 **减脂目标**")
            st.write("- 每餐先吃蔬菜，再吃蛋白质，最后吃主食")
            st.write("- 细嚼慢咽，每餐用时20分钟以上")
            st.write("- 晚餐尽量在19点前完成")
            st.write("- 每天饮水2000ml以上")
        elif goal == "增肌":
            st.info("💪 **增肌目标**")
            st.write("- 增加优质蛋白质摄入（鸡胸肉、鸡蛋、鱼肉）")
            st.write("- 训练后30分钟内补充蛋白质")
            st.write("- 碳水化合物摄入要充足")
            st.write("- 每天蛋白质摄入量：体重(kg) x 1.6-2.2g")
        else:
            st.info("🥗 **健康饮食**")
            st.write("- 保持饮食多样化，每天摄入12种以上食物")
            st.write("- 减少加工食品和外卖频率")
            st.write("- 多吃全谷物和粗粮")
            st.write("- 适量摄入健康脂肪")
        
        st.markdown("### 📊 营养状况")
        
        if daily['protein'] < 50:
            st.warning("⚠️ 蛋白质不足，建议添加: 🍗鸡胸肉、🥚鸡蛋、🐟鱼肉")
        if daily['fat'] > 80:
            st.warning("⚠️ 脂肪偏高，建议减少油炸食品")
        if daily['carbs'] < 200:
            st.warning("⚠️ 碳水不足，建议添加: 🍚米饭、🍜面条、🥔土豆")
        if daily['calories'] < 1500:
            st.warning("⚠️ 热量偏低，注意补充能量")
        elif daily['calories'] > 2500:
            st.warning("⚠️ 热量偏高，建议减少高热量食物")
    else:
        st.info("请先记录今日饮食，获取个性化建议")
