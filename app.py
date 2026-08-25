import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
# 页面配置
st.set_page_config(
    page_title="卡路里追踪器", 
    page_icon="🍎", 
    layout="wide",
    initial_sidebar_state="expanded"
)
# 自定义样式
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    div[data-testid="stMetric"] label {
        font-size: 14px !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: bold !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)
# ==================== 数据库 ====================
FOOD_DB = {
    "常见": [
        {"name": "米饭", "cal": 116, "emoji": "🍚", "protein": 2.6, "fat": 0.3, "carbs": 25.6},
        {"name": "面条", "cal": 110, "emoji": "🍜", "protein": 3.5, "fat": 0.5, "carbs": 23.0},
        {"name": "馒头", "cal": 221, "emoji": "🍞", "protein": 7.0, "fat": 1.1, "carbs": 47.0},
        {"name": "鸡蛋", "cal": 144, "emoji": "🥚", "protein": 13.3, "fat": 9.5, "carbs": 1.5},
        {"name": "牛奶", "cal": 54, "emoji": "🥛", "protein": 3.0, "fat": 3.2, "carbs": 3.4},
        {"name": "苹果", "cal": 52, "emoji": "🍎", "protein": 0.3, "fat": 0.2, "carbs": 13.8},
        {"name": "香蕉", "cal": 89, "emoji": "🍌", "protein": 1.1, "fat": 0.3, "carbs": 22.8},
        {"name": "豆浆", "cal": 31, "emoji": "🥛", "protein": 2.9, "fat": 1.6, "carbs": 1.2},
    ],
    "主食杂粮": [
        {"name": "糙米饭", "cal": 111, "emoji": "🍚", "protein": 2.6, "fat": 0.9, "carbs": 23.0},
        {"name": "燕麦片", "cal": 379, "emoji": "🥣", "protein": 15.0, "fat": 6.7, "carbs": 61.6},
        {"name": "红薯", "cal": 86, "emoji": "🍠", "protein": 1.6, "fat": 0.1, "carbs": 20.1},
        {"name": "玉米", "cal": 96, "emoji": "🌽", "protein": 3.4, "fat": 1.2, "carbs": 19.9},
        {"name": "全麦面包", "cal": 246, "emoji": "🍞", "protein": 10.0, "fat": 3.4, "carbs": 41.3},
        {"name": "包子", "cal": 227, "emoji": "🥟", "protein": 8.0, "fat": 5.0, "carbs": 35.0},
        {"name": "饺子", "cal": 186, "emoji": "🥟", "protein": 7.5, "fat": 4.0, "carbs": 28.0},
    ],
    "肉蛋奶": [
        {"name": "鸡胸肉", "cal": 133, "emoji": "🍗", "protein": 31.0, "fat": 1.2, "carbs": 0},
        {"name": "牛肉", "cal": 125, "emoji": "🥩", "protein": 26.1, "fat": 3.7, "carbs": 0},
        {"name": "猪里脊", "cal": 155, "emoji": "🥩", "protein": 20.2, "fat": 7.9, "carbs": 0},
        {"name": "鸡腿肉", "cal": 181, "emoji": "🍗", "protein": 16.0, "fat": 13.0, "carbs": 0},
        {"name": "三文鱼", "cal": 139, "emoji": "🐟", "protein": 21.3, "fat": 5.9, "carbs": 0},
        {"name": "酸奶", "cal": 72, "emoji": "🥛", "protein": 3.5, "fat": 2.7, "carbs": 9.3},
        {"name": "虾仁", "cal": 48, "emoji": "🦐", "protein": 10.4, "fat": 0.3, "carbs": 0},
    ],
    "蔬菜": [
        {"name": "西兰花", "cal": 34, "emoji": "🥦", "protein": 2.8, "fat": 0.4, "carbs": 6.6},
        {"name": "番茄炒蛋", "cal": 98, "emoji": "🍅", "protein": 5.5, "fat": 6.8, "carbs": 5.2},
        {"name": "黄瓜", "cal": 16, "emoji": "🥒", "protein": 0.7, "fat": 0.1, "carbs": 3.6},
        {"name": "胡萝卜", "cal": 41, "emoji": "🥕", "protein": 0.9, "fat": 0.2, "carbs": 9.6},
        {"name": "菠菜", "cal": 23, "emoji": "🥬", "protein": 2.9, "fat": 0.4, "carbs": 3.6},
        {"name": "炒青菜", "cal": 45, "emoji": "🥬", "protein": 1.5, "fat": 3.0, "carbs": 3.0},
    ],
    "水果": [
        {"name": "苹果", "cal": 52, "emoji": "🍎", "protein": 0.3, "fat": 0.2, "carbs": 13.8},
        {"name": "香蕉", "cal": 89, "emoji": "🍌", "protein": 1.1, "fat": 0.3, "carbs": 22.8},
        {"name": "橙子", "cal": 47, "emoji": "🍊", "protein": 0.9, "fat": 0.1, "carbs": 11.8},
        {"name": "葡萄", "cal": 69, "emoji": "🍇", "protein": 0.7, "fat": 0.2, "carbs": 18.1},
        {"name": "草莓", "cal": 32, "emoji": "🍓", "protein": 0.7, "fat": 0.3, "carbs": 7.7},
        {"name": "西瓜", "cal": 30, "emoji": "🍉", "protein": 0.6, "fat": 0.1, "carbs": 7.6},
    ],
    "中式菜品": [
        {"name": "宫保鸡丁", "cal": 162, "emoji": "🍲", "protein": 15.2, "fat": 8.5, "carbs": 7.3},
        {"name": "麻婆豆腐", "cal": 121, "emoji": "🍲", "protein": 8.5, "fat": 7.8, "carbs": 5.2},
        {"name": "红烧肉", "cal": 285, "emoji": "🥩", "protein": 12.3, "fat": 24.5, "carbs": 4.8},
        {"name": "酸辣土豆丝", "cal": 84, "emoji": "🥔", "protein": 2.0, "fat": 3.8, "carbs": 11.2},
        {"name": "番茄蛋汤", "cal": 45, "emoji": "🍅", "protein": 2.5, "fat": 2.2, "carbs": 4.0},
    ],
    "西式快餐": [
        {"name": "汉堡", "cal": 254, "emoji": "🍔", "protein": 12.0, "fat": 9.5, "carbs": 31.0},
        {"name": "薯条", "cal": 312, "emoji": "🍟", "protein": 3.4, "fat": 15.0, "carbs": 41.4},
        {"name": "披萨", "cal": 266, "emoji": "🍕", "protein": 11.0, "fat": 10.4, "carbs": 33.0},
        {"name": "炸鸡腿", "cal": 279, "emoji": "🍗", "protein": 17.5, "fat": 21.3, "carbs": 6.8},
    ],
    "日韩料理": [
        {"name": "寿司", "cal": 148, "emoji": "🍣", "protein": 5.8, "fat": 2.1, "carbs": 26.4},
        {"name": "拉面", "cal": 132, "emoji": "🍜", "protein": 4.5, "fat": 3.2, "carbs": 22.8},
        {"name": "石锅拌饭", "cal": 168, "emoji": "🍚", "protein": 5.2, "fat": 4.8, "carbs": 27.5},
        {"name": "韩式烤肉", "cal": 195, "emoji": "🥩", "protein": 18.5, "fat": 13.2, "carbs": 2.8},
    ],
    "饮品": [
        {"name": "可乐", "cal": 42, "emoji": "🥤", "protein": 0, "fat": 0, "carbs": 10.6},
        {"name": "橙汁", "cal": 45, "emoji": "🍊", "protein": 0.7, "fat": 0.2, "carbs": 10.4},
        {"name": "咖啡", "cal": 2, "emoji": "☕", "protein": 0.3, "fat": 0, "carbs": 0},
        {"name": "拿铁", "cal": 135, "emoji": "☕", "protein": 6.3, "fat": 4.5, "carbs": 16.0},
        {"name": "奶茶", "cal": 80, "emoji": "🧋", "protein": 1.5, "fat": 2.5, "carbs": 13.5},
    ],
    "甜点零食": [
        {"name": "巧克力", "cal": 546, "emoji": "🍫", "protein": 4.9, "fat": 31.3, "carbs": 59.4},
        {"name": "蛋糕", "cal": 347, "emoji": "🎂", "protein": 4.5, "fat": 15.5, "carbs": 50.0},
        {"name": "冰淇淋", "cal": 207, "emoji": "🍦", "protein": 3.5, "fat": 11.0, "carbs": 24.0},
        {"name": "饼干", "cal": 466, "emoji": "🍪", "protein": 5.0, "fat": 20.0, "carbs": 65.0},
    ],
}
ACTIVITY_DB = {
    "有氧运动": [
        {"name": "跑步", "cal_per_min": 10, "emoji": "🏃"},
        {"name": "游泳", "cal_per_min": 8, "emoji": "🏊"},
        {"name": "骑车", "cal_per_min": 7, "emoji": "🚴"},
        {"name": "跳绳", "cal_per_min": 12, "emoji": "🤸"},
        {"name": "快走", "cal_per_min": 5, "emoji": "🚶"},
        {"name": "有氧操", "cal_per_min": 6, "emoji": "💃"},
    ],
    "力量训练": [
        {"name": "举重", "cal_per_min": 6, "emoji": "🏋️"},
        {"name": "俯卧撑", "cal_per_min": 8, "emoji": "💪"},
        {"name": "仰卧起坐", "cal_per_min": 5, "emoji": "🏋️"},
        {"name": "深蹲", "cal_per_min": 7, "emoji": "🏋️"},
    ],
    "日常活动": [
        {"name": "走路", "cal_per_min": 4, "emoji": "🚶"},
        {"name": "做家务", "cal_per_min": 3.5, "emoji": "🧹"},
        {"name": "站立", "cal_per_min": 1.5, "emoji": "🧍"},
        {"name": "逛街", "cal_per_min": 3, "emoji": "🛍️"},
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
    return data.get(today, {'meals': {}, 'burn': []})
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
        data[today] = {'meals': {}, 'burn': []}
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
        data[today] = {'meals': {}, 'burn': []}
    cal = activity['cal_per_min'] * duration
    data[today]['burn'].append({
        'activity': activity['name'],
        'emoji': activity['emoji'],
        'duration_min': duration,
        'calories': round(cal, 1),
        'time': datetime.now().strftime('%H:%M')
    })
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
    st.markdown("---")
    
    page = st.radio(
        "导航",
        ["📝 记录饮食", "🏃 记录运动", "📊 今日统计", "📈 周趋势", "💡 饮食建议"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # 今日概览
    today_data = get_today_data()
    total_intake = sum(sum(item['calories'] for item in meal) for meal in today_data.get('meals', {}).values())
    total_burn = sum(r['calories'] for r in today_data.get('burn', []))
    
    st.markdown("### 📊 今日概览")
    st.metric("摄入", f"{total_intake:.0f} 千卡")
    st.metric("消耗", f"{total_burn:.0f} 千卡")
    st.metric("净摄入", f"{total_intake - total_burn:.0f} 千卡")
    
    st.markdown("---")
    st.caption("v1.0 | 数据保存在云端")
# ==================== 记录饮食 ====================
if page == "📝 记录饮食":
    st.markdown("# 📝 记录饮食")
    
    today_data = get_today_data()
    
    # 餐次统计
    col1, col2, col3, col4 = st.columns(4)
    for col, (meal_name, meal_key) in zip([col1, col2, col3, col4], MEAL_TYPES.items()):
        meal_cal = sum(item['calories'] for item in today_data.get('meals', {}).get(meal_key, []))
        with col:
            st.metric(meal_name, f"{meal_cal:.0f} 千卡")
    
    st.markdown("---")
    
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
    
    st.subheader(f"选择食物 ({len(filtered_foods)}种)")
    
    # 食物网格
    foods_per_row = 4
    for i in range(0, len(filtered_foods), foods_per_row):
        cols = st.columns(foods_per_row)
        for j, col in enumerate(cols):
            if i + j < len(filtered_foods):
                food = filtered_foods[i + j]
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{food['emoji']} {food['name']}**")
                        st.caption(f"{food['cal']} 千卡 | 蛋白{food['protein']}g")
                        weight = st.number_input(
                            "克", min_value=10, max_value=1000, value=100, step=10,
                            key=f"w_{food['name']}_{selected_meal}_{i+j}",
                            label_visibility="collapsed"
                        )
                        if st.button("➕ 添加", key=f"add_{food['name']}_{selected_meal}_{i+j}", use_container_width=True):
                            save_meal(food, weight, selected_meal)
                            st.success(f"✅ {food['name']} {weight}g")
                            st.rerun()
    
    # 今日记录
    st.markdown("---")
    st.subheader("📋 今日饮食记录")
    
    for meal_type, meal_name in MEAL_TYPES.items():
        records = today_data.get('meals', {}).get(meal_type, [])
        if records:
            meal_cal = sum(r['calories'] for r in records)
            with st.expander(f"{meal_name} ({len(records)}项, {meal_cal:.0f} 千卡)", expanded=True):
                for idx, record in enumerate(records):
                    col1, col2, col3 = st.columns([4, 1, 1])
                    with col1:
                        st.write(f"{record.get('emoji', '🍴')} {record['food']} - {record['weight_g']}g")
                    with col2:
                        st.write(f"**{record['calories']:.0f} 千卡**")
                    with col3:
                        if st.button("🗑️", key=f"del_{meal_type}_{idx}"):
                            delete_record('meal', meal_type, idx)
                            st.rerun()
# ==================== 记录运动 ====================
elif page == "🏃 记录运动":
    st.markdown("# 🏃 记录运动")
    
    today_data = get_today_data()
    total_burn = sum(r['calories'] for r in today_data.get('burn', []))
    total_duration = sum(r['duration_min'] for r in today_data.get('burn', []))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔥 今日消耗", f"{total_burn:.0f} 千卡")
    with col2:
        st.metric("⏱️ 运动时长", f"{total_duration} 分钟")
    with col3:
        st.metric("📊 运动次数", f"{len(today_data.get('burn', []))} 次")
    
    st.markdown("---")
    
    # 运动选择
    activity_category = st.selectbox("运动类型", list(ACTIVITY_DB.keys()))
    activities = ACTIVITY_DB[activity_category]
    
    activity_names = [f"{a['emoji']} {a['name']}" for a in activities]
    selected_idx = st.radio("选择运动", activity_names, horizontal=True)
    selected_activity = activities[activity_names.index(selected_idx)]
    
    duration = st.slider("运动时长（分钟）", min_value=5, max_value=180, value=30, step=5)
    estimated_cal = selected_activity['cal_per_min'] * duration
    
    st.info(f"💡 预计消耗: **{estimated_cal:.0f} 千卡** (约 {selected_activity['cal_per_min']} 千卡/分钟)")
    
    if st.button("✅ 记录运动", type="primary", use_container_width=True):
        save_burn(selected_activity, duration)
        st.success(f"🎉 已记录 {selected_activity['name']} {duration}分钟 = {estimated_cal:.0f} 千卡")
        st.balloons()
        st.rerun()
    
    # 运动记录
    st.markdown("---")
    st.subheader("📋 今日运动记录")
    
    burn_records = today_data.get('burn', [])
    if burn_records:
        for idx, record in enumerate(burn_records):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.write(f"{record.get('emoji', '🏃')} {record['activity']}")
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
    st.markdown("# 📊 今日统计")
    
    today_data = get_today_data()
    total_intake = sum(sum(item['calories'] for item in meal) for meal in today_data.get('meals', {}).values())
    total_burn = sum(r['calories'] for r in today_data.get('burn', []))
    net_calories = total_intake - total_burn
    
    # 核心指标
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🍽️ 总摄入", f"{total_intake:.0f} 千卡")
    with col2:
        st.metric("🔥 总消耗", f"{total_burn:.0f} 千卡")
    with col3:
        delta = "超标" if net_calories > 2000 else "正常" if net_calories > 0 else "偏低"
        st.metric("📈 净摄入", f"{net_calories:.0f} 千卡", delta=delta)
    
    st.markdown("---")
    
    # 营养素分析
    all_intake = []
    for meal_records in today_data.get('meals', {}).values():
        all_intake.extend(meal_records)
    
    if all_intake:
        total_protein = sum(r.get('protein', 0) for r in all_intake)
        total_fat = sum(r.get('fat', 0) for r in all_intake)
        total_carbs = sum(r.get('carbs', 0) for r in all_intake)
        
        st.subheader("🥗 营养素分析")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("蛋白质", f"{total_protein:.1f}g")
        with col2:
            st.metric("脂肪", f"{total_fat:.1f}g")
        with col3:
            st.metric("碳水", f"{total_carbs:.1f}g")
        
        # 营养素饼图
        if total_protein + total_fat + total_carbs > 0:
            fig = px.pie(
                values=[total_protein * 4, total_fat * 9, total_carbs * 4],
                names=['蛋白质', '脂肪', '碳水'],
                title='营养素热量占比',
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#FFE66D']
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 餐次分布
    st.subheader("🍽️ 餐次分布")
    meal_data = {}
    for meal_type, meal_name in MEAL_TYPES.items():
        meal_cal = sum(item['calories'] for item in today_data.get('meals', {}).get(meal_type, []))
        if meal_cal > 0:
            meal_data[meal_name] = meal_cal
    
    if meal_data:
        fig = px.pie(
            values=list(meal_data.values()),
            names=list(meal_data.keys()),
            title='各餐热量占比',
            color_discrete_sequence=['#FF9A9E', '#FAD0C4', '#A18CD1', '#FBC2EB']
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无饮食记录")
# ==================== 周趋势 ====================
elif page == "📈 周趋势":
    st.markdown("# 📈 一周趋势")
    
    weekly_data = get_weekly_data()
    
    # 柱状图
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[d['day'] for d in weekly_data],
        y=[d['intake'] for d in weekly_data],
        name='摄入',
        marker_color='#FF6B6B'
    ))
    fig.add_trace(go.Bar(
        x=[d['day'] for d in weekly_data],
        y=[d['burn'] for d in weekly_data],
        name='消耗',
        marker_color='#4ECDC4'
    ))
    fig.update_layout(
        title='一周摄入 vs 消耗',
        xaxis_title='日期',
        yaxis_title='千卡',
        barmode='group',
        template='plotly_white'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 净热量趋势
    net_data = [d['intake'] - d['burn'] for d in weekly_data]
    fig2 = px.line(
        x=[d['day'] for d in weekly_data],
        y=net_data,
        title='净热量趋势',
        markers=True,
        labels={'x': '日期', 'y': '净热量 (千卡)'}
    )
    fig2.update_traces(line_color='#667eea', line_width=3)
    st.plotly_chart(fig2, use_container_width=True)
    
    # 统计卡片
    avg_intake = sum(d['intake'] for d in weekly_data) / 7
    avg_burn = sum(d['burn'] for d in weekly_data) / 7
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("日均摄入", f"{avg_intake:.0f} 千卡")
    with col2:
        st.metric("日均消耗", f"{avg_burn:.0f} 千卡")
    with col3:
        st.metric("日均净摄入", f"{avg_intake - avg_burn:.0f} 千卡")
# ==================== 饮食建议 ====================
elif page == "💡 饮食建议":
    st.markdown("# 💡 饮食建议")
    
    today_data = get_today_data()
    total_intake = sum(sum(item['calories'] for item in meal) for meal in today_data.get('meals', {}).values())
    total_burn = sum(r['calories'] for r in today_data.get('burn', []))
    
    all_intake = []
    for meal_records in today_data.get('meals', {}).values():
        all_intake.extend(meal_records)
    
    total_protein = sum(r.get('protein', 0) for r in all_intake)
    total_fat = sum(r.get('fat', 0) for r in all_intake)
    total_carbs = sum(r.get('carbs', 0) for r in all_intake)
    
    # 今日评估
    st.subheader("📊 今日评估")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("摄入热量", f"{total_intake:.0f} 千卡", help="建议每日1800-2200千卡")
        st.metric("消耗热量", f"{total_burn:.0f} 千卡", help="建议每日300-500千卡")
    with col2:
        st.metric("蛋白质", f"{total_protein:.1f}g", help="建议每日60-80g")
        st.metric("脂肪", f"{total_fat:.1f}g", help="建议每日50-70g")
        st.metric("碳水", f"{total_carbs:.1f}g", help="建议每日200-300g")
    
    st.markdown("---")
    
    # 个性化建议
    st.subheader("🎯 个性化建议")
    
    suggestions = []
    
    if total_intake == 0:
        suggestions.append("📝 今天还没有记录饮食，快来记录吧！")
    elif total_intake < 1500:
        suggestions.append("⚠️ 摄入热量偏低，建议适当增加食物摄入，保证营养均衡。")
    elif total_intake > 2500:
        suggestions.append("⚠️ 摄入热量偏高，建议减少高热量食物，增加蔬菜摄入。")
    else:
        suggestions.append("✅ 摄入热量适中，继续保持！")
    
    if total_protein < 50 and total_intake > 0:
        suggestions.append("🥩 蛋白质摄入不足，建议增加鸡胸肉、牛肉、鸡蛋等高蛋白食物。")
    elif total_protein >= 60:
        suggestions.append("💪 蛋白质摄入充足，有助于肌肉恢复和增长。")
    
    if total_burn < 200 and total_intake > 0:
        suggestions.append("🏃 今日运动量较少，建议增加30分钟有氧运动。")
    elif total_burn >= 400:
        suggestions.append("🎉 今日运动量充足，记得补充水分和蛋白质！")
    
    if total_intake > 0 and total_protein + total_fat + total_carbs > 0:
        protein_pct = total_protein * 4 / total_intake * 100
        fat_pct = total_fat * 9 / total_intake * 100
        if fat_pct > 35:
            suggestions.append("🍳 脂肪占比偏高，建议减少油炸食品。")
    
    for s in suggestions:
        st.info(s)
    
    st.markdown("---")
    
    # 推荐食物
    st.subheader("🍽️ 推荐食物")
    
    st.write("**高蛋白低脂肪：**")
    for name in ["鸡胸肉", "鱼肉", "虾仁", "鸡蛋", "豆腐"]:
        for foods in FOOD_DB.values():
            for f in foods:
                if f['name'] == name:
                    st.write(f"- {f['emoji']} {f['name']}: {f['cal']}千卡/100g, 蛋白{f['protein']}g")
    
    st.write("**低热量蔬菜：**")
    for name in ["黄瓜", "菠菜", "西兰花", "番茄", "胡萝卜"]:
        for foods in FOOD_DB.values():
            for f in foods:
                if f['name'] == name:
                    st.write(f"- {f['emoji']} {f['name']}: {f['cal']}千卡/100g")
