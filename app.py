import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path

# 页面配置
st.set_page_config(
    page_title="🍎 卡路里追踪器", 
    page_icon="🍎", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 卡通风格CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&display=swap');
    
    * {
        font-family: 'Noto Sans SC', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    }
    
    /* 卡通标题 */
    .cartoon-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        padding: 20px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 卡通卡片 */
    .cartoon-card {
        background: white;
        border-radius: 25px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 3px solid #f0f0f0;
        margin: 10px 0;
        transition: transform 0.3s;
    }
    .cartoon-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    /* 统计卡片 */
    .stat-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 20px;
        padding: 25px;
        text-align: center;
        border: 3px dashed #ff9a9e;
    }
    .stat-card h3 {
        font-size: 2rem;
        margin: 0;
    }
    .stat-card p {
        color: #666;
        margin: 5px 0 0 0;
    }
    
    /* 食物卡片 */
    .food-card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border-radius: 20px;
        padding: 15px;
        text-align: center;
        border: 3px solid #e9ecef;
        transition: all 0.3s;
        cursor: pointer;
    }
    .food-card:hover {
        border-color: #ff6b6b;
        transform: scale(1.05);
    }
    .food-emoji {
        font-size: 3rem;
        margin: 10px 0;
    }
    .food-name {
        font-weight: bold;
        font-size: 1.1rem;
        color: #333;
    }
    .food-cal {
        color: #ff6b6b;
        font-weight: bold;
    }
    
    /* 运动卡片 */
    .activity-card {
        background: linear-gradient(145deg, #a8edea, #fed6e3);
        border-radius: 20px;
        padding: 15px;
        text-align: center;
        border: 3px solid #fff;
    }
    
    /* 餐次标签 */
    .meal-tab {
        display: inline-block;
        padding: 10px 25px;
        margin: 5px;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
    }
    .meal-tab.breakfast { background: #fff3cd; color: #856404; }
    .meal-tab.lunch { background: #d4edda; color: #155724; }
    .meal-tab.dinner { background: #cce5ff; color: #004085; }
    .meal-tab.snack { background: #f8d7da; color: #721c24; }
    
    /* 建议卡片 */
    .suggestion-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 20px;
        margin: 10px 0;
    }
    .suggestion-card h4 {
        margin: 0 0 10px 0;
    }
    
    /* 目标按钮 */
    .goal-btn {
        display: inline-block;
        padding: 15px 30px;
        margin: 8px;
        border-radius: 30px;
        font-weight: bold;
        font-size: 1.1rem;
        cursor: pointer;
        border: 3px solid transparent;
        transition: all 0.3s;
    }
    .goal-btn.lose-fat {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
    }
    .goal-btn.lose-weight {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
    }
    .goal-btn.gain-weight {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        color: white;
    }
    .goal-btn.gain-muscle {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }
    .goal-btn:hover {
        transform: scale(1.1);
        box-shadow: 0 5px 20px rgba(0,0,0,0.2);
    }
    
    /* 进度条 */
    .progress-bar {
        background: #e9ecef;
        border-radius: 15px;
        height: 25px;
        overflow: hidden;
        margin: 10px 0;
    }
    .progress-fill {
        height: 100%;
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        transition: width 0.5s;
    }
    .progress-fill.intake { background: linear-gradient(90deg, #ff9a9e, #fecfef); }
    .progress-fill.burn { background: linear-gradient(90deg, #a8edea, #fed6e3); }
    
    /* 分隔线 */
    .cute-divider {
        text-align: center;
        margin: 20px 0;
        font-size: 1.5rem;
    }
    
    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffecd2 0%, #fcb69f 100%);
    }
</style>
""", unsafe_allow_html=True)

# ==================== 数据库 ====================
FOOD_DB = {
    "🍚 主食": [
        {"name": "米饭", "cal": 116, "emoji": "🍚", "protein": 2.6, "fat": 0.3, "carbs": 25.6, "tags": ["减脂", "增肌"]},
        {"name": "面条", "cal": 110, "emoji": "🍜", "protein": 3.5, "fat": 0.5, "carbs": 23.0, "tags": ["增重"]},
        {"name": "馒头", "cal": 221, "emoji": "🍞", "protein": 7.0, "fat": 1.1, "carbs": 47.0, "tags": ["增重"]},
        {"name": "糙米饭", "cal": 111, "emoji": "🍚", "protein": 2.6, "fat": 0.9, "carbs": 23.0, "tags": ["减脂", "减肥"]},
        {"name": "燕麦片", "cal": 379, "emoji": "🥣", "protein": 15.0, "fat": 6.7, "carbs": 61.6, "tags": ["增肌", "减脂"]},
        {"name": "红薯", "cal": 86, "emoji": "🍠", "protein": 1.6, "fat": 0.1, "carbs": 20.1, "tags": ["减脂", "减肥"]},
        {"name": "玉米", "cal": 96, "emoji": "🌽", "protein": 3.4, "fat": 1.2, "carbs": 19.9, "tags": ["减脂"]},
        {"name": "全麦面包", "cal": 246, "emoji": "🍞", "protein": 10.0, "fat": 3.4, "carbs": 41.3, "tags": ["增肌"]},
    ],
    "🥩 肉蛋奶": [
        {"name": "鸡胸肉", "cal": 133, "emoji": "🍗", "protein": 31.0, "fat": 1.2, "carbs": 0, "tags": ["增肌", "减脂", "减肥"]},
        {"name": "牛肉", "cal": 125, "emoji": "🥩", "protein": 26.1, "fat": 3.7, "carbs": 0, "tags": ["增肌"]},
        {"name": "猪里脊", "cal": 155, "emoji": "🥩", "protein": 20.2, "fat": 7.9, "carbs": 0, "tags": ["增重"]},
        {"name": "鸡蛋", "cal": 144, "emoji": "🥚", "protein": 13.3, "fat": 9.5, "carbs": 1.5, "tags": ["增肌", "减脂"]},
        {"name": "三文鱼", "cal": 139, "emoji": "🐟", "protein": 21.3, "fat": 5.9, "carbs": 0, "tags": ["增肌", "减脂"]},
        {"name": "虾仁", "cal": 48, "emoji": "🦐", "protein": 10.4, "fat": 0.3, "carbs": 0, "tags": ["减脂", "减肥"]},
        {"name": "牛奶", "cal": 54, "emoji": "🥛", "protein": 3.0, "fat": 3.2, "carbs": 3.4, "tags": ["增重", "增肌"]},
        {"name": "酸奶", "cal": 72, "emoji": "🥛", "protein": 3.5, "fat": 2.7, "carbs": 9.3, "tags": ["减脂"]},
    ],
    "🥬 蔬菜": [
        {"name": "西兰花", "cal": 34, "emoji": "🥦", "protein": 2.8, "fat": 0.4, "carbs": 6.6, "tags": ["减脂", "减肥", "增肌"]},
        {"name": "番茄", "cal": 18, "emoji": "🍅", "protein": 0.9, "fat": 0.2, "carbs": 3.9, "tags": ["减肥", "减脂"]},
        {"name": "黄瓜", "cal": 16, "emoji": "🥒", "protein": 0.7, "fat": 0.1, "carbs": 3.6, "tags": ["减肥", "减脂"]},
        {"name": "菠菜", "cal": 23, "emoji": "🥬", "protein": 2.9, "fat": 0.4, "carbs": 3.6, "tags": ["减脂", "增肌"]},
        {"name": "胡萝卜", "cal": 41, "emoji": "🥕", "protein": 0.9, "fat": 0.2, "carbs": 9.6, "tags": ["增重"]},
        {"name": "生菜", "cal": 15, "emoji": "🥬", "protein": 1.3, "fat": 0.3, "carbs": 2.8, "tags": ["减肥"]},
    ],
    "🍎 水果": [
        {"name": "苹果", "cal": 52, "emoji": "🍎", "protein": 0.3, "fat": 0.2, "carbs": 13.8, "tags": ["减脂", "减肥"]},
        {"name": "香蕉", "cal": 89, "emoji": "🍌", "protein": 1.1, "fat": 0.3, "carbs": 22.8, "tags": ["增肌", "增重"]},
        {"name": "橙子", "cal": 47, "emoji": "🍊", "protein": 0.9, "fat": 0.1, "carbs": 11.8, "tags": ["减脂"]},
        {"name": "草莓", "cal": 32, "emoji": "🍓", "protein": 0.7, "fat": 0.3, "carbs": 7.7, "tags": ["减肥", "减脂"]},
        {"name": "西瓜", "cal": 30, "emoji": "🍉", "protein": 0.6, "fat": 0.1, "carbs": 7.6, "tags": ["减肥"]},
        {"name": "葡萄", "cal": 69, "emoji": "🍇", "protein": 0.7, "fat": 0.2, "carbs": 18.1, "tags": ["增重"]},
    ],
    "🍲 中式菜品": [
        {"name": "宫保鸡丁", "cal": 162, "emoji": "🍲", "protein": 15.2, "fat": 8.5, "carbs": 7.3, "tags": ["增肌"]},
        {"name": "番茄炒蛋", "cal": 98, "emoji": "🍅", "protein": 5.5, "fat": 6.8, "carbs": 5.2, "tags": ["增重"]},
        {"name": "红烧肉", "cal": 285, "emoji": "🥩", "protein": 12.3, "fat": 24.5, "carbs": 4.8, "tags": ["增重"]},
        {"name": "清炒时蔬", "cal": 45, "emoji": "🥬", "protein": 2.0, "fat": 3.0, "carbs": 3.0, "tags": ["减肥", "减脂"]},
        {"name": "蛋花汤", "cal": 28, "emoji": "🍲", "protein": 2.0, "fat": 1.5, "carbs": 2.5, "tags": ["减肥"]},
    ],
    "🍔 西式快餐": [
        {"name": "汉堡", "cal": 254, "emoji": "🍔", "protein": 12.0, "fat": 9.5, "carbs": 31.0, "tags": ["增重"]},
        {"name": "薯条", "cal": 312, "emoji": "🍟", "protein": 3.4, "fat": 15.0, "carbs": 41.4, "tags": []},
        {"name": "披萨", "cal": 266, "emoji": "🍕", "protein": 11.0, "fat": 10.4, "carbs": 33.0, "tags": ["增重"]},
        {"name": "沙拉", "cal": 65, "emoji": "🥗", "protein": 3.0, "fat": 4.0, "carbs": 5.0, "tags": ["减肥", "减脂"]},
    ],
    "☕ 饮品": [
        {"name": "咖啡", "cal": 2, "emoji": "☕", "protein": 0.3, "fat": 0, "carbs": 0, "tags": ["减脂"]},
        {"name": "拿铁", "cal": 135, "emoji": "☕", "protein": 6.3, "fat": 4.5, "carbs": 16.0, "tags": ["增重"]},
        {"name": "奶茶", "cal": 80, "emoji": "🧋", "protein": 1.5, "fat": 2.5, "carbs": 13.5, "tags": []},
        {"name": "可乐", "cal": 42, "emoji": "🥤", "protein": 0, "fat": 0, "carbs": 10.6, "tags": []},
        {"name": "鲜榨橙汁", "cal": 45, "emoji": "🍊", "protein": 0.7, "fat": 0.2, "carbs": 10.4, "tags": ["增重"]},
    ],
    "🍰 甜点零食": [
        {"name": "巧克力", "cal": 546, "emoji": "🍫", "protein": 4.9, "fat": 31.3, "carbs": 59.4, "tags": ["增重"]},
        {"name": "蛋糕", "cal": 347, "emoji": "🎂", "protein": 4.5, "fat": 15.5, "carbs": 50.0, "tags": ["增重"]},
        {"name": "冰淇淋", "cal": 207, "emoji": "🍦", "protein": 3.5, "fat": 11.0, "carbs": 24.0, "tags": []},
        {"name": "坚果", "cal": 607, "emoji": "🥜", "protein": 20.0, "fat": 50.0, "carbs": 20.0, "tags": ["增肌", "增重"]},
    ],
}

ACTIVITY_DB = {
    "🏃 有氧运动": [
        {"name": "跑步", "cal_per_min": 10, "emoji": "🏃", "difficulty": "中等"},
        {"name": "游泳", "cal_per_min": 8, "emoji": "🏊", "difficulty": "中等"},
        {"name": "骑车", "cal_per_min": 7, "emoji": "🚴", "difficulty": "简单"},
        {"name": "跳绳", "cal_per_min": 12, "emoji": "🤸", "difficulty": "困难"},
        {"name": "快走", "cal_per_min": 5, "emoji": "🚶", "difficulty": "简单"},
    ],
    "💪 力量训练": [
        {"name": "举重", "cal_per_min": 6, "emoji": "🏋️", "difficulty": "困难"},
        {"name": "俯卧撑", "cal_per_min": 8, "emoji": "💪", "difficulty": "中等"},
        {"name": "深蹲", "cal_per_min": 7, "emoji": "🏋️", "difficulty": "中等"},
        {"name": "平板支撑", "cal_per_min": 5, "emoji": "🧘", "difficulty": "中等"},
    ],
    "🧘 柔韧训练": [
        {"name": "瑜伽", "cal_per_min": 4, "emoji": "🧘", "difficulty": "简单"},
        {"name": "拉伸", "cal_per_min": 3, "emoji": "🤸", "difficulty": "简单"},
    ],
    "🏠 日常活动": [
        {"name": "走路", "cal_per_min": 4, "emoji": "🚶", "difficulty": "简单"},
        {"name": "做家务", "cal_per_min": 3.5, "emoji": "🧹", "difficulty": "简单"},
        {"name": "逛街", "cal_per_min": 3, "emoji": "🛍️", "difficulty": "简单"},
    ],
}

MEAL_TYPES = {
    "🌅 早餐": "breakfast",
    "☀️ 午餐": "lunch", 
    "🌙 晚餐": "dinner",
    "🍪 加餐": "snack"
}

# ==================== 数据函数 ====================
DATA_FILE = Path('calorie_data.json')

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_today_str():
    return datetime.now().strftime('%Y-%m-%d')

def get_today_data():
    data = load_data()
    today = get_today_str()
    return data.get(today, {'meals': {}, 'burn': [], 'goal': None})

def get_all_foods():
    foods = []
    for category, items in FOOD_DB.items():
        for item in items:
            item_copy = item.copy()
            item_copy['category'] = category
            foods.append(item_copy)
    return foods

def save_meal(food, weight, meal_type):
    data = load_data()
    today = get_today_str()
    if today not in data:
        data[today] = {'meals': {}, 'burn': [], 'goal': None}
    if meal_type not in data[today]['meals']:
        data[today]['meals'][meal_type] = []
    cal = food['cal'] * weight / 100
    data[today]['meals'][meal_type].append({
        'food': food['name'],
        'emoji': food['emoji'],
        'weight_g': weight,
        'calories': round(cal, 1),
        'protein': round(food['protein'] * weight / 100, 1),
        'fat': round(food['fat'] * weight / 100, 1),
        'carbs': round(food['carbs'] * weight / 100, 1),
        'time': datetime.now().strftime('%H:%M')
    })
    save_data(data)

def save_burn(activity, duration):
    data = load_data()
    today = get_today_str()
    if today not in data:
        data[today] = {'meals': {}, 'burn': [], 'goal': None}
    cal = activity['cal_per_min'] * duration
    data[today]['burn'].append({
        'activity': activity['name'],
        'emoji': activity['emoji'],
        'duration_min': duration,
        'calories': round(cal, 1),
        'time': datetime.now().strftime('%H:%M')
    })
    save_data(data)

def save_goal(goal):
    data = load_data()
    today = get_today_str()
    if today not in data:
        data[today] = {'meals': {}, 'burn': [], 'goal': None}
    data[today]['goal'] = goal
    save_data(data)

def delete_record(record_type, meal_type=None, index=None):
    data = load_data()
    today = get_today_str()
    if today not in data:
        return
    if record_type == 'meal' and meal_type and index is not None:
        if meal_type in data[today].get('meals', {}):
            data[today]['meals'][meal_type].pop(index)
    elif record_type == 'burn' and index is not None:
        data[today]['burn'].pop(index)
    save_data(data)

def get_weekly_data():
    data = load_data()
    weekly = []
    for i in range(6, -1, -1):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        day_data = data.get(date, {'meals': {}, 'burn': []})
        intake = sum(sum(item['calories'] for item in meal) for meal in day_data.get('meals', {}).values())
        burn = sum(r['calories'] for r in day_data.get('burn', []))
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday = weekday_names[datetime.strptime(date, '%Y-%m-%d').weekday()]
        weekly.append({
            'date': date,
            'day': weekday,
            'intake': round(intake, 1),
            'burn': round(burn, 1)
        })
    return weekly

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## 🍎 卡路里追踪器")
    st.markdown("### 记录饮食 · 追踪营养 · 健康生活")
    st.markdown("---")
    
    page = st.radio(
        "功能导航",
        ["📝 记录饮食", "🏃 记录运动", "📊 今日统计", "📈 周趋势", "💡 饮食建议"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    today_data = get_today_data()
    total_intake = sum(sum(item['calories'] for item in meal) for meal in today_data.get('meals', {}).values())
    total_burn = sum(r['calories'] for r in today_data.get('burn', []))
    
    st.markdown("### 📊 今日速览")
    st.metric("🍽️ 摄入", f"{total_intake:.0f} 千卡")
    st.metric("🔥 消耗", f"{total_burn:.0f} 千卡")
    st.metric("📈 净摄入", f"{total_intake - total_burn:.0f} 千卡")
    
    st.markdown("---")
    st.markdown("### 🎯 今日目标")
    
    goal = today_data.get('goal')
    if goal:
        goal_cal = goal.get('calories', 2000)
        progress = min(100, int(total_intake / goal_cal * 100))
        st.progress(progress / 100)
        st.caption(f"{total_intake:.0f} / {goal_cal} 千卡 ({progress}%)")
    else:
        st.info("未设置目标")

# ==================== 记录饮食 ====================
if page == "📝 记录饮食":
    st.markdown('<h1 class="cartoon-title">📝 记录饮食</h1>', unsafe_allow_html=True)
    
    today_data = get_today_data()
    
    # 餐次统计
    col1, col2, col3, col4 = st.columns(4)
    for col, (meal_name, meal_key) in zip([col1, col2, col3, col4], MEAL_TYPES.items()):
        meal_cal = sum(item['calories'] for item in today_data.get('meals', {}).get(meal_key, []))
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <h3>{meal_name.split(' ')[0]}</h3>
                <p>{meal_cal:.0f} 千卡</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="cute-divider">✨ ✨ ✨</div>', unsafe_allow_html=True)
    
    # 选择餐次
    selected_meal_name = st.radio("选择餐次", list(MEAL_TYPES.keys()), horizontal=True)
    selected_meal = MEAL_TYPES[selected_meal_name]
    
    # 搜索和分类
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 搜索食物", placeholder="输入食物名称...")
    with col2:
        categories = ["全部"] + list(FOOD_DB.keys())
        selected_category = st.selectbox("分类", categories)
    
    # 过滤食物
    all_foods = get_all_foods()
    if search_query:
        filtered_foods = [f for f in all_foods if search_query.lower() in f['name'].lower()]
    elif selected_category != "全部":
        filtered_foods = FOOD_DB.get(selected_category, [])
    else:
        filtered_foods = all_foods
    
    st.subheader(f"🍽️ 选择食物 ({len(filtered_foods)}种)")
    
    # 食物网格
    foods_per_row = 4
    for i in range(0, len(filtered_foods), foods_per_row):
        cols = st.columns(foods_per_row)
        for j, col in enumerate(cols):
            if i + j < len(filtered_foods):
                food = filtered_foods[i + j]
                with col:
                    st.markdown(f"""
                    <div class="food-card">
                        <div class="food-emoji">{food['emoji']}</div>
                        <div class="food-name">{food['name']}</div>
                        <div class="food-cal">{food['cal']} 千卡/100g</div>
                        <div>蛋白 {food['protein']}g</div>
                    </div>
                    """, unsafe_allow_html=True)
                    weight = st.number_input(
                        "克", min_value=10, max_value=1000, value=100, step=10,
                        key=f"w_{food['name']}_{selected_meal}_{i+j}",
                        label_visibility="collapsed"
                    )
                    if st.button("➕ 添加", key=f"add_{food['name']}_{selected_meal}_{i+j}", use_container_width=True):
                        save_meal(food, weight, selected_meal)
                        st.success(f"✅ 已添加 {food['emoji']} {food['name']} {weight}g")
                        st.rerun()
    
    st.markdown('<div class="cute-divider">📋 📋 📋</div>', unsafe_allow_html=True)
    
    # 今日记录
    st.subheader("📋 今日饮食记录")
    
    for meal_type, meal_name in MEAL_TYPES.items():
        records = today_data.get('meals', {}).get(meal_type, [])
        if records:
            meal_cal = sum(r['calories'] for r in records)
            with st.expander(f"{meal_name} ({len(records)}项, {meal_cal:.0f} 千卡)", expanded=True):
                for idx, record in enumerate(records):
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.write(f"{record.get('emoji', '🍴')} **{record['food']}** - {record['weight_g']}g")
                    with col2:
                        st.write(f"**{record['calories']:.0f} 千卡**")
                    with col3:
                        if st.button("🗑️", key=f"del_{meal_type}_{idx}"):
                            delete_record('meal', meal_type, idx)
                            st.rerun()

# ==================== 记录运动 ====================
elif page == "🏃 记录运动":
    st.markdown('<h1 class="cartoon-title">🏃 记录运动</h1>', unsafe_allow_html=True)
    
    today_data = get_today_data()
    total_burn = sum(r['calories'] for r in today_data.get('burn', []))
    total_duration = sum(r['duration_min'] for r in today_data.get('burn', []))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);">
            <h3>🔥 {total_burn:.0f}</h3>
            <p>今日消耗（千卡）</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
            <h3>⏱️ {total_duration}</h3>
            <p>运动时长（分钟）</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h3>📊 {len(today_data.get('burn', []))}</h3>
            <p>运动次数</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="cute-divider">✨ ✨ ✨</div>', unsafe_allow_html=True)
    
    # 运动选择
    activity_category = st.selectbox("运动类型", list(ACTIVITY_DB.keys()))
    activities = ACTIVITY_DB[activity_category]
    
    activity_names = [f"{a['emoji']} {a['name']} ({a['difficulty']})" for a in activities]
    selected_idx = st.radio("选择运动", activity_names, horizontal=True)
    selected_activity = activities[activity_names.index(selected_idx)]
    
    duration = st.slider("运动时长（分钟）", min_value=5, max_value=180, value=30, step=5)
    estimated_cal = selected_activity['cal_per_min'] * duration
    
    st.markdown(f"""
    <div class="suggestion-card">
        <h4>💡 预计消耗</h4>
        <p style="font-size: 2rem; margin: 0;">{estimated_cal:.0f} 千卡</p>
        <p>{selected_activity['emoji']} {selected_activity['name']} {duration}分钟</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("✅ 记录运动", type="primary", use_container_width=True):
        save_burn(selected_activity, duration)
        st.success(f"🎉 已记录 {selected_activity['emoji']} {selected_activity['name']} {duration}分钟 = {estimated_cal:.0f} 千卡")
        st.balloons()
        st.rerun()
    
    st.markdown('<div class="cute-divider">📋 📋 📋</div>', unsafe_allow_html=True)
    
    # 运动记录
    st.subheader("📋 今日运动记录")
    
    burn_records = today_data.get('burn', [])
    if burn_records:
        for idx, record in enumerate(burn_records):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{record.get('emoji', '🏃')} **{record['activity']}**")
            with col2:
                st.write(f"{record['duration_min']} 分钟")
            with col3:
                st.write(f"**{record['calories']:.0f} 千卡**")
            with col4:
                if st.button("🗑️", key=f"del_burn_{idx}"):
                    delete_record('burn', index=idx)
                    st.rerun()
    else:
        st.info("🏃 今天还没有运动记录，快来运动吧！")

# ==================== 今日统计 ====================
elif page == "📊 今日统计":
    st.markdown('<h1 class="cartoon-title">📊 今日统计</h1>', unsafe_allow_html=True)
    
    today_data = get_today_data()
    total_intake = sum(sum(item['calories'] for item in meal) for meal in today_data.get('meals', {}).values())
    total_burn = sum(r['calories'] for r in today_data.get('burn', []))
    net_calories = total_intake - total_burn
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);">
            <h3>🍽️ {total_intake:.0f}</h3>
            <p>总摄入（千卡）</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
            <h3>🔥 {total_burn:.0f}</h3>
            <p>总消耗（千卡）</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        color = "#ff6b6b" if net_calories > 2000 else "#4ecdc4"
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <h3>📈 {net_calories:.0f}</h3>
            <p>净摄入（千卡）</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="cute-divider">✨ ✨ ✨</div>', unsafe_allow_html=True)
    
    # 营养素分析
    all_intake = []
    for meal_records in today_data.get('meals', {}).values():
        all_intake.extend(meal_records)
    
    if all_intake:
        total_protein = sum(r.get('protein', 0) for r in all_intake)
        total_fat = sum(r.get('fat', 0) for r in all_intake)
        total_carbs = sum(r.get('carbs', 0) for r in all_intake)
        
        st.subheader("🥗 营养素分析")
        
        # 进度条
        protein_cal = total_protein * 4
        fat_cal = total_fat * 9
        carbs_cal = total_carbs * 4
        total_macro_cal = protein_cal + fat_cal + carbs_cal
        
        if total_macro_cal > 0:
            protein_pct = int(protein_cal / total_macro_cal * 100)
            fat_pct = int(fat_cal / total_macro_cal * 100)
            carbs_pct = int(carbs_cal / total_macro_cal * 100)
            
            st.markdown(f"""
            <div style="margin: 10px 0;">
                <p>🥩 蛋白质: {total_protein:.1f}g ({protein_pct}%)</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {protein_pct}%; background: linear-gradient(90deg, #ff6b6b, #ffa502);">{protein_pct}%</div>
                </div>
            </div>
            <div style="margin: 10px 0;">
                <p>🧈 脂肪: {total_fat:.1f}g ({fat_pct}%)</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {fat_pct}%; background: linear-gradient(90deg, #feca57, #ff9ff3);">{fat_pct}%</div>
                </div>
            </div>
            <div style="margin: 10px 0;">
                <p>🍞 碳水: {total_carbs:.1f}g ({carbs_pct}%)</p>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {carbs_pct}%; background: linear-gradient(90deg, #48dbfb, #0abde3);">{carbs_pct}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<div class="cute-divider">🍽️ 🍽️ 🍽️</div>', unsafe_allow_html=True)
        
        # 各餐热量
        st.subheader("🍽️ 各餐热量")
        for meal_type, meal_name in MEAL_TYPES.items():
            records = today_data.get('meals', {}).get(meal_type, [])
            if records:
                meal_cal = sum(r['calories'] for r in records)
                with st.expander(f"{meal_name} - {meal_cal:.0f} 千卡"):
                    for r in records:
                        st.write(f"{r.get('emoji', '🍴')} {r['food']} {r['weight_g']}g = {r['calories']:.0f} 千卡")

# ==================== 周趋势 ====================
elif page == "📈 周趋势":
    st.markdown('<h1 class="cartoon-title">📈 一周趋势</h1>', unsafe_allow_html=True)
    
    weekly_data = get_weekly_data()
    
    # 进度条显示
    st.subheader("📊 本周概览")
    for d in weekly_data:
        if d['intake'] > 0 or d['burn'] > 0:
            st.markdown(f"**{d['day']}** ({d['date']})")
            
            intake_pct = min(100, int(d['intake'] / 2500 * 100))
            burn_pct = min(100, int(d['burn'] / 500 * 100))
            
            st.markdown(f"""
            <div style="margin: 5px 0;">
                <p>🍽️ 摄入: {d['intake']:.0f} 千卡</p>
                <div class="progress-bar">
                    <div class="progress-fill intake" style="width: {intake_pct}%;">{d['intake']:.0f}</div>
                </div>
                <p>🔥 消耗: {d['burn']:.0f} 千卡</p>
                <div class="progress-bar">
                    <div class="progress-fill burn" style="width: {burn_pct}%;">{d['burn']:.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="cute-divider">✨ ✨ ✨</div>', unsafe_allow_html=True)
    
    # 统计卡片
    avg_intake = sum(d['intake'] for d in weekly_data) / 7
    avg_burn = sum(d['burn'] for d in weekly_data) / 7
    max_intake = max(d['intake'] for d in weekly_data)
    max_burn = max(d['burn'] for d in weekly_data)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("日均摄入", f"{avg_intake:.0f} 千卡")
    with col2:
        st.metric("日均消耗", f"{avg_burn:.0f} 千卡")
    with col3:
        st.metric("最高摄入", f"{max_intake:.0f} 千卡")
    with col4:
        st.metric("最高消耗", f"{max_burn:.0f} 千卡")

# ==================== 饮食建议 ====================
elif page == "💡 饮食建议":
    st.markdown('<h1 class="cartoon-title">💡 饮食建议</h1>', unsafe_allow_html=True)
    
    # 目标选择
    st.subheader("🎯 选择你的目标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔥 减脂", use_container_width=True):
            save_goal({"type": "lose_fat", "calories": 1500})
            st.rerun()
    with col2:
        if st.button("⚖️ 减肥", use_container_width=True):
            save_goal({"type": "lose_weight", "calories": 1200})
            st.rerun()
    with col3:
        if st.button("💪 增肌", use_container_width=True):
            save_goal({"type": "gain_muscle", "calories": 2500})
            st.rerun()
    with col4:
        if st.button("📈 增重", use_container_width=True):
            save_goal({"type": "gain_weight", "calories": 2800})
            st.rerun()
    
    st.markdown('<div class="cute-divider">✨ ✨ ✨</div>', unsafe_allow_html=True)
    
    today_data = get_today_data()
    goal = today_data.get('goal')
    
    total_intake = sum(sum(item['calories'] for item in meal) for meal in today_data.get('meals', {}).values())
    total_burn = sum(r['calories'] for r in today_data.get('burn', []))
    
    all_intake = []
    for meal_records in today_data.get('meals', {}).values():
        all_intake.extend(meal_records)
    
    total_protein = sum(r.get('protein', 0) for r in all_intake)
    total_fat = sum(r.get('fat', 0) for r in all_intake)
    total_carbs = sum(r.get('carbs', 0) for r in all_intake)
    
    if goal:
        goal_type = goal.get('type', '')
        goal_cal = goal.get('calories', 2000)
        
        st.subheader(f"📊 今日目标：{goal_type.replace('_', ' ').title()}")
        
        # 目标进度
        progress = min(100, int(total_intake / goal_cal * 100))
        st.markdown(f"""
        <div class="progress-bar">
            <div class="progress-fill" style="width: {progress}%; background: linear-gradient(90deg, #667eea, #764ba2);">
                {total_intake:.0f} / {goal_cal} 千卡 ({progress}%)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="cute-divider">💡 💡 💡</div>', unsafe_allow_html=True)
        
        # 不同目标的建议
        if goal_type == "lose_fat":
            st.markdown("""
            <div class="suggestion-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <h4>🔥 减脂目标建议</h4>
                <ul>
                    <li>🎯 每日热量控制在1500-1800千卡</li>
                    <li>🥩 蛋白质摄入：体重(kg) × 1.5-2g，保持肌肉</li>
                    <li>🍞 碳水选择：糙米、燕麦、红薯等低GI食物</li>
                    <li>🧈 脂肪控制：少吃油炸，多吃坚果、鱼油</li>
                    <li>🏃 有氧运动：每周3-5次，每次30-45分钟</li>
                    <li>💪 力量训练：每周2-3次，防止肌肉流失</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("**推荐食物：**")
            st.write("- 🍗 鸡胸肉、🐟 鱼肉、🦐 虾仁（高蛋白低脂）")
            st.write("- 🥦 西兰花、🥒 黄瓜、🍅 番茄（低热量高纤维）")
            st.write("- 🍚 糙米、🍠 红薯、🥣 燕麦（优质碳水）")
            
        elif goal_type == "lose_weight":
            st.markdown("""
            <div class="suggestion-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                <h4>⚖️ 减肥目标建议</h4>
                <ul>
                    <li>🎯 每日热量控制在1200-1500千卡</li>
                    <li>🥗 多吃蔬菜，增加饱腹感</li>
                    <li>🥩 保证蛋白质摄入，防止肌肉流失</li>
                    <li>🚫 避免：奶茶、甜点、油炸食品</li>
                    <li>💧 多喝水，每天至少2000ml</li>
                    <li>🚶 增加日常活动量，多走路</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("**推荐食物：**")
            st.write("- 🥒 黄瓜、🥬 生菜、🍅 番茄（几乎无热量）")
            st.write("- 🍗 鸡胸肉、🥚 鸡蛋（优质蛋白）")
            st.write("- 🍎 苹果、🍓 草莓（低糖水果）")
            
        elif goal_type == "gain_muscle":
            st.markdown("""
            <div class="suggestion-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                <h4>💪 增肌目标建议</h4>
                <ul>
                    <li>🎯 每日热量摄入2200-2800千卡</li>
                    <li>🥩 蛋白质摄入：体重(kg) × 2-2.5g</li>
                    <li>🍞 碳水充足：训练前后补充碳水</li>
                    <li>⏰ 少食多餐：每天5-6餐</li>
                    <li>💪 力量训练：每周4-5次，渐进超负荷</li>
                    <li>😴 充足睡眠：每天7-8小时</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("**推荐食物：**")
            st.write("- 🍗 鸡胸肉、🥩 牛肉、🐟 三文鱼（增肌必备）")
            st.write("- 🍚 米饭、🍞 全麦面包、🍌 香蕉（训练后补充）")
            st.write("- 🥜 坚果、🥛 牛奶（健康脂肪）")
            
        elif goal_type == "gain_weight":
            st.markdown("""
            <div class="suggestion-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                <h4>📈 增重目标建议</h4>
                <ul>
                    <li>🎯 每日热量摄入2500-3000千卡</li>
                    <li>🍞 碳水为主：每餐都要有主食</li>
                    <li>🥩 适量蛋白质：体重(kg) × 1.5-2g</li>
                    <li>🥑 健康脂肪：坚果、牛油果、橄榄油</li>
                    <li>⏰ 少食多餐：每天5-6餐</li>
                    <li>💪 配合力量训练：增加肌肉而非脂肪</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("**推荐食物：**")
            st.write("- 🍚 米饭、🍜 面条、🍞 馒头（高碳水主食）")
            st.write("- 🥜 坚果、🍫 巧克力、🍌 香蕉（高热量零食）")
            st.write("- 🥛 牛奶、🎂 蛋糕、🍔 汉堡（快速增热量）")
    
    else:
        st.info("👆 请先选择你的目标（减脂/减肥/增肌/增重）")
        
        # 通用建议
        st.subheader("📝 通用健康建议")
        st.markdown("""
        <div class="cartoon-card">
            <h4>🌟 健康饮食原则</h4>
            <ul>
                <li>🥗 蔬菜占每餐的一半</li>
                <li>🥩 蛋白质占四分之一</li>
                <li>🍞 碳水占四分之一</li>
                <li>💧 每天喝8杯水</li>
                <li>🚫 少油少盐少糖</li>
                <li>⏰ 三餐规律，不熬夜</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
