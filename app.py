import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
st.set_page_config(page_icon="\U0001f34e", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
    .cartoon-title {
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2rem; font-weight: bold; text-align: center; padding: 10px 0;
    }
    .stat-card {
        background: linear-gradient(135deg, #a8edea, #fed6e3);
        border-radius: 15px; padding: 15px; text-align: center; border: 2px dashed #ff9a9e;
    }
    .mini-food {
        background: white; border-radius: 12px; padding: 8px 4px; text-align: center;
        border: 2px solid #eee; transition: all 0.2s; min-height: 85px;
    }
    .mini-food:hover { border-color: #ff6b6b; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .suggestion-card {
        background: linear-gradient(135deg, #667eea, #764ba2); color: white;
        border-radius: 20px; padding: 20px; margin: 10px 0;
    }
    .progress-bar { background: #e9ecef; border-radius: 12px; height: 22px; overflow: hidden; margin: 8px 0; }
    .progress-fill {
        height: 100%; border-radius: 12px; display: flex; align-items: center;
        justify-content: center; color: white; font-weight: bold; font-size: 0.85rem;
    }
    .cute-divider { text-align: center; margin: 12px 0; font-size: 1.2rem; }
    section[data-testid="stSidebar"] { background: linear-gradient(180deg, #ffecd2, #fcb69f); }
</style>
""", unsafe_allow_html=True)
FOOD_DB = {
    "🍚 主食": [
        {"name":"米饭","cal":116,"e":"🍚","p":2.6,"f":0.3,"c":25.6},
        {"name":"面条","cal":110,"e":"🍜","p":3.5,"f":0.5,"c":23.0},
        {"name":"馒头","cal":221,"e":"🍞","p":7.0,"f":1.1,"c":47.0},
        {"name":"糙米饭","cal":111,"e":"🍚","p":2.6,"f":0.9,"c":23.0},
        {"name":"燕麦片","cal":379,"e":"🥣","p":15.0,"f":6.7,"c":61.6},
        {"name":"红薯","cal":86,"e":"🍠","p":1.6,"f":0.1,"c":20.1},
        {"name":"玉米","cal":96,"e":"🌽","p":3.4,"f":1.2,"c":19.9},
        {"name":"全麦面包","cal":246,"e":"🍞","p":10.0,"f":3.4,"c":41.3},
    ],
    "🥩 肉蛋奶": [
        {"name":"鸡胸肉","cal":133,"e":"🍗","p":31.0,"f":1.2,"c":0},
        {"name":"牛肉","cal":125,"e":"🥩","p":26.1,"f":3.7,"c":0},
        {"name":"猪里脊","cal":155,"e":"🥩","p":20.2,"f":7.9,"c":0},
        {"name":"鸡蛋","cal":144,"e":"🥚","p":13.3,"f":9.5,"c":1.5},
        {"name":"三文鱼","cal":139,"e":"🐟","p":21.3,"f":5.9,"c":0},
        {"name":"虾仁","cal":48,"e":"🦐","p":10.4,"f":0.3,"c":0},
        {"name":"牛奶","cal":54,"e":"🥛","p":3.0,"f":3.2,"c":3.4},
        {"name":"酸奶","cal":72,"e":"🥛","p":3.5,"f":2.7,"c":9.3},
    ],
    "🥬 蔬菜": [
        {"name":"西兰花","cal":34,"e":"🥦","p":2.8,"f":0.4,"c":6.6},
        {"name":"番茄","cal":18,"e":"🍅","p":0.9,"f":0.2,"c":3.9},
        {"name":"黄瓜","cal":16,"e":"🥒","p":0.7,"f":0.1,"c":3.6},
        {"name":"菠菜","cal":23,"e":"🥬","p":2.9,"f":0.4,"c":3.6},
        {"name":"胡萝卜","cal":41,"e":"🥕","p":0.9,"f":0.2,"c":9.6},
        {"name":"生菜","cal":15,"e":"🥬","p":1.3,"f":0.3,"c":2.8},
    ],
    "🍎 水果": [
        {"name":"苹果","cal":52,"e":"🍎","p":0.3,"f":0.2,"c":13.8},
        {"name":"香蕉","cal":89,"e":"🍌","p":1.1,"f":0.3,"c":22.8},
        {"name":"橙子","cal":47,"e":"🍊","p":0.9,"f":0.1,"c":11.8},
        {"name":"草莓","cal":32,"e":"🍓","p":0.7,"f":0.3,"c":7.7},
        {"name":"西瓜","cal":30,"e":"🍉","p":0.6,"f":0.1,"c":7.6},
        {"name":"葡萄","cal":69,"e":"🍇","p":0.7,"f":0.2,"c":18.1},
    ],
    "🍲 菜品": [
        {"name":"宫保鸡丁","cal":162,"e":"🍲","p":15.2,"f":8.5,"c":7.3},
        {"name":"番茄炒蛋","cal":98,"e":"🍅","p":5.5,"f":6.8,"c":5.2},
        {"name":"红烧肉","cal":285,"e":"🥩","p":12.3,"f":24.5,"c":4.8},
        {"name":"清炒时蔬","cal":45,"e":"🥬","p":2.0,"f":3.0,"c":3.0},
        {"name":"蛋花汤","cal":28,"e":"🍲","p":2.0,"f":1.5,"c":2.5},
    ],
    "🍔 快餐": [
        {"name":"汉堡","cal":254,"e":"🍔","p":12.0,"f":9.5,"c":31.0},
        {"name":"薯条","cal":312,"e":"🍟","p":3.4,"f":15.0,"c":41.4},
        {"name":"披萨","cal":266,"e":"🍕","p":11.0,"f":10.4,"c":33.0},
        {"name":"沙拉","cal":65,"e":"🥗","p":3.0,"f":4.0,"c":5.0},
    ],
    "☕ 饮品": [
        {"name":"咖啡","cal":2,"e":"☕","p":0.3,"f":0,"c":0},
        {"name":"拿铁","cal":135,"e":"☕","p":6.3,"f":4.5,"c":16.0},
        {"name":"奶茶","cal":80,"e":"🧋","p":1.5,"f":2.5,"c":13.5},
        {"name":"可乐","cal":42,"e":"🥤","p":0,"f":0,"c":10.6},
        {"name":"橙汁","cal":45,"e":"🍊","p":0.7,"f":0.2,"c":10.4},
    ],
    "🍰 零食": [
        {"name":"巧克力","cal":546,"e":"🍫","p":4.9,"f":31.3,"c":59.4},
        {"name":"蛋糕","cal":347,"e":"🎂","p":4.5,"f":15.5,"c":50.0},
        {"name":"冰淇淋","cal":207,"e":"🍦","p":3.5,"f":11.0,"c":24.0},
        {"name":"坚果","cal":607,"e":"🥜","p":20.0,"f":50.0,"c":20.0},
    ],
}
ACTIVITY_DB = {
    "🏃 有氧": [
        {"name":"跑步","cpm":10,"e":"🏃"},{"name":"游泳","cpm":8,"e":"🏊"},
        {"name":"骑车","cpm":7,"e":"🚴"},{"name":"跳绳","cpm":12,"e":"🤸"},
        {"name":"快走","cpm":5,"e":"🚶"},
    ],
    "💪 力量": [
        {"name":"举重","cpm":6,"e":"🏋️"},{"name":"俯卧撑","cpm":8,"e":"💪"},
        {"name":"深蹲","cpm":7,"e":"🏋️"},{"name":"平板支撑","cpm":5,"e":"🧘"},
    ],
    "🧘 柔韧": [
        {"name":"瑜伽","cpm":4,"e":"🧘"},{"name":"拉伸","cpm":3,"e":"🤸"},
    ],
    "🏠 日常": [
        {"name":"走路","cpm":4,"e":"🚶"},{"name":"做家务","cpm":3.5,"e":"🧹"},
        {"name":"逛街","cpm":3,"e":"🛍️"},
    ],
}
MEAL_TYPES = {"🌅 早餐":"breakfast","☀️ 午餐":"lunch","🌙 晚餐":"dinner","🍪 加餐":"snack"}
DATA_FILE = Path('calorie_data.json')
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    return {}
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)
def today_str(): return datetime.now().strftime('%Y-%m-%d')
def get_today_data():
    d = load_data(); t = today_str()
    ensure_day(d, t)
    return d[t]
def get_all_foods():
    foods = []
    for cat, items in FOOD_DB.items():
        for it in items:
            c = it.copy(); c['category'] = cat; foods.append(c)
    return foods
def ensure_day(d, t):
    if t not in d: d[t] = {}
    d[t].setdefault('meals', {})
    d[t].setdefault('burn', [])
    d[t].setdefault('goal', None)
def save_meal(food, weight, meal_type):
    d = load_data(); t = today_str()
    ensure_day(d, t)
    if meal_type not in d[t]['meals']: d[t]['meals'][meal_type] = []
    cal = food['cal'] * weight / 100
    d[t]['meals'][meal_type].append({
        'food':food['name'],'emoji':food['e'],'weight_g':weight,
        'calories':round(cal,1),'protein':round(food['p']*weight/100,1),
        'fat':round(food['f']*weight/100,1),'carbs':round(food['c']*weight/100,1),
        'time':datetime.now().strftime('%H:%M')
    })
    save_data(d)
def save_burn(act, dur):
    d = load_data(); t = today_str()
    ensure_day(d, t)
    cal = act['cpm'] * dur
    d[t]['burn'].append({
        'activity':act['name'],'emoji':act['e'],'duration_min':dur,
        'calories':round(cal,1),'time':datetime.now().strftime('%H:%M')
    })
    save_data(d)
def save_goal(goal):
    d = load_data(); t = today_str()
    ensure_day(d, t)
    d[t]['goal'] = goal; save_data(d)
def delete_record(rtype, meal_type=None, idx=None):
    d = load_data(); t = today_str()
    if t not in d: return
    if rtype=='meal' and meal_type and idx is not None:
        if meal_type in d[t].get('meals',{}): d[t]['meals'][meal_type].pop(idx)
    elif rtype=='burn' and idx is not None:
        d[t]['burn'].pop(idx)
    save_data(d)
def get_weekly():
    d = load_data(); weekly = []
    for i in range(6,-1,-1):
        date = (datetime.now()-timedelta(days=i)).strftime('%Y-%m-%d')
        dd = d.get(date,{'meals':{},'burn':[]})
        intake = sum(sum(r['calories'] for r in m) for m in dd.get('meals',{}).values())
        burn = sum(r['calories'] for r in dd.get('burn',[]))
        wd = ['周一','周二','周三','周四','周五','周六','周日']
        weekly.append({'date':date,'day':wd[datetime.strptime(date,'%Y-%m-%d').weekday()],
                       'intake':round(intake,1),'burn':round(burn,1)})
    return weekly
def calc_bmi(h, w):
    hm = h / 100
    bmi = w / (hm ** 2)
    if bmi < 18.5: return bmi, "偏瘦", "#4facfe", "📉"
    elif bmi < 24: return bmi, "正常", "#43e97b", "✅"
    elif bmi < 28: return bmi, "偏胖", "#feca57", "📈"
    else: return bmi, "肥胖", "#ff6b6b", "⚠️"
def get_goal_name(gt):
    return {"lose_fat":"🔥 减脂","lose_weight":"⚖️ 减肥","gain_muscle":"💪 增肌","gain_weight":"📈 增重","maintain":"✅ 保持"}.get(gt,"未知")
# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("## \U0001f34e 卡路里追踪器")
    st.markdown("*记录饮食 · 追踪营养 · 健康生活*")
    st.markdown("---")
    page = st.radio("功能", ["\U0001f4dd 记录饮食","\U0001f3c3 记录运动","\U0001f4ca 今日统计","\U0001f4c8 周趋势","\U0001f4a1 BMI与建议"], label_visibility="collapsed")
    st.markdown("---")
    td = get_today_data()
    ti = sum(sum(r['calories'] for r in m) for m in td.get('meals',{}).values())
    tb = sum(r['calories'] for r in td.get('burn',[]))
    st.markdown("### \U0001f4ca 今日速览")
    st.metric("\U0001f37d\ufe0f 摄入", f"{ti:.0f} 千卡")
    st.metric("\U0001f525 消耗", f"{tb:.0f} 千卡")
    st.metric("\U0001f4c8 净摄入", f"{ti-tb:.0f} 千卡")
    st.markdown("---")
    g = td.get('goal')
    if g:
        gc = g.get('calories',2000)
        p = min(100,int(ti/gc*100))
        st.markdown(f"**目标:** {get_goal_name(g.get('type',''))} {gc}千卡")
        st.progress(p/100)
        st.caption(f"{ti:.0f}/{gc} ({p}%)")
# ==================== 页面1: 记录饮食 ====================
if page == "\U0001f4dd 记录饮食":
    st.markdown('<p class="cartoon-title">📝 记录饮食</p>', unsafe_allow_html=True)
    meal_label = st.selectbox("选择餐次", list(MEAL_TYPES.keys()))
    meal_key = MEAL_TYPES[meal_label]
    target_cal = st.number_input("目标热量 (千卡)", min_value=500, max_value=5000, value=2000, step=50, key="target_cal")
    if st.button("📌 保存今日目标", use_container_width=True):
        save_goal({"type":"maintain","calories":target_cal})
        st.success(f"目标已保存: {target_cal}千卡/天")
    st.markdown('<div class="cute-divider">--- 🍽️ 选择食物 ---</div>', unsafe_allow_html=True)
    keyword = st.text_input("🔍 搜索食物", placeholder="输入食物名称...")
    categories = ["全部"] + list(FOOD_DB.keys())
    sel_cat = st.selectbox("📂 分类筛选", categories)
    goal_filter = st.selectbox("🎯 目标筛选", ["全部","减脂","减肥","增肌","增重","保持"], key="gf")
    filtered = get_all_foods()
    if keyword: filtered = [f for f in filtered if keyword.lower() in f['name'].lower()]
    if sel_cat != "全部": filtered = [f for f in filtered if f['category'] == sel_cat]
    if filtered:
        cols_per_row = 7
        for i in range(0, len(filtered), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                idx = i + j
                if idx >= len(filtered): break
                f = filtered[idx]
                with col:
                    if st.button(f"{f['e']}\n{f['name']}\n{f['cal']}kcal", key=f"food_{f['name']}_{idx}", use_container_width=True):
                        st.session_state['selected_food'] = f
                        st.rerun()
    else:
        st.info("没有找到匹配的食物")
    if 'selected_food' in st.session_state:
        sf = st.session_state['selected_food']
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("热量", f"{sf['cal']}千卡/100g")
        c2.metric("蛋白质", f"{sf['p']}g")
        c3.metric("脂肪", f"{sf['f']}g")
        c4.metric("碳水", f"{sf['c']}g")
        weight = st.slider("份量 (克)", 10, 500, 100, step=10)
        real_cal = sf['cal'] * weight / 100
        st.info(f"这份 {sf['name']} ({weight}g) = **{real_cal:.1f}千卡** | 蛋白 {sf['p']*weight/100:.1f}g | 脂肪 {sf['f']*weight/100:.1f}g | 碳水 {sf['c']*weight/100:.1f}g")
        c1, c2 = st.columns([1,1])
        with c1:
            if st.button("✅ 添加记录", type="primary", use_container_width=True):
                save_meal(sf, weight, meal_key)
                del st.session_state['selected_food']
                st.success(f"已记录: {sf['e']} {sf['name']} {weight}g ({real_cal:.1f}千卡) -> {meal_label}")
                st.rerun()
        with c2:
            if st.button("❌ 取消", use_container_width=True):
                del st.session_state['selected_food']
                st.rerun()
    st.markdown('<div class="cute-divider">--- 📋 今日已记录 ---</div>', unsafe_allow_html=True)
    td = get_today_data()
    total_today = 0
    for mlabel, mkey in MEAL_TYPES.items():
        items = td.get('meals', {}).get(mkey, [])
        if items:
            sub = sum(r['calories'] for r in items)
            total_today += sub
            with st.expander(f"{mlabel} ({len(items)}项, {sub:.0f}千卡)", expanded=True):
                for i, r in enumerate(items):
                    cols = st.columns([3,1,1,1,1,1])
                    cols[0].write(f"{r['emoji']} {r['food']} ({r['weight_g']}g)")
                    cols[1].write(f"{r['calories']}kcal")
                    cols[2].write(f"蛋白{r['protein']}g")
                    cols[3].write(f"脂{r['fat']}g")
                    cols[4].write(f"碳{r['carbs']}g")
                    if cols[5].button("🗑️", key=f"del_{mkey}_{i}"):
                        delete_record('meal', mkey, i)
                        st.rerun()
    st.metric("今日总摄入", f"{total_today:.1f} 千卡")
# ==================== 页面2: 记录运动 ====================
elif page == "\U0001f3c3 记录运动":
    st.markdown('<p class="cartoon-title">🏃 记录运动</p>', unsafe_allow_html=True)
    act_cat = st.selectbox("选择类型", list(ACTIVITY_DB.keys()))
    acts = ACTIVITY_DB[act_cat]
    act_names = [f"{a['e']} {a['name']} ({a['cpm']}千卡/分钟)" for a in acts]
    act_idx = st.selectbox("选择运动", range(len(act_names)), format_func=lambda x: act_names[x])
    act = acts[act_idx]
    dur = st.slider("运动时长 (分钟)", 1, 120, 30)
    est = act['cpm'] * dur
    st.info(f"预估消耗: **{est} 千卡** ({act['cpm']}千卡/分钟 x {dur}分钟)")
    if st.button("✅ 记录运动", type="primary", use_container_width=True):
        save_burn(act, dur)
        st.success(f"已记录: {act['e']} {act['name']} {dur}分钟 = {est}千卡")
        st.rerun()
    st.markdown("---")
    st.markdown("### 📋 今日运动记录")
    td = get_today_data()
    burns = td.get('burn', [])
    total_burn = 0
    if burns:
        for i, r in enumerate(burns):
            total_burn += r['calories']
            cols = st.columns([4,1,1,1])
            cols[0].write(f"{r['emoji']} {r['activity']} ({r['duration_min']}分钟)")
            cols[1].write(f"{r['calories']}kcal")
            cols[2].write(r.get('time',''))
            if cols[3].button("🗑️", key=f"del_burn_{i}"):
                delete_record('burn', idx=i)
                st.rerun()
    else:
        st.info("今天还没有运动记录")
    st.metric("今日总消耗", f"{total_burn:.1f} 千卡")
# ==================== 页面3: 今日统计 ====================
elif page == "\U0001f4ca 今日统计":
    st.markdown('<p class="cartoon-title">📊 今日统计</p>', unsafe_allow_html=True)
    td = get_today_data()
    ti = sum(sum(r['calories'] for r in m) for m in td.get('meals',{}).values())
    tb = sum(r['calories'] for r in td.get('burn',[]))
    tp = sum(sum(r['protein'] for r in m) for m in td.get('meals',{}).values())
    tf = sum(sum(r['fat'] for r in m) for m in td.get('meals',{}).values())
    tc = sum(sum(r['carbs'] for r in m) for m in td.get('meals',{}).values())
    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown('<div class="stat-card"><h3>🍽️</h3><h2>' + f"{ti:.0f}" + '</h2><p>摄入千卡</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-card"><h3>🔥</h3><h2>' + f"{tb:.0f}" + '</h2><p>消耗千卡</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="stat-card"><h3>📈</h3><h2>' + f"{ti-tb:.0f}" + '</h2><p>净摄入千卡</p></div>', unsafe_allow_html=True)
    with c4:
        g = td.get('goal',{})
        gc = g.get('calories',2000)
        p = min(100,int(ti/gc*100)) if gc else 0
        st.markdown('<div class="stat-card"><h3>🎯</h3><h2>' + f"{p}%" + '</h2><p>目标进度</p></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🥗 营养素分布")
    macros = [{"name":"蛋白质","value":tp,"color":"#4facfe","unit":"g"},
              {"name":"脂肪","value":tf,"color":"#feca57","unit":"g"},
              {"name":"碳水","value":tc,"color":"#43e97b","unit":"g"}]
    for m in macros:
        cols = st.columns([1,3,1])
        cols[0].markdown(f"**{m['name']}**")
        pct = min(100, int(m['value']/max(1,tp+tf+tc)*100))
        cols[1].markdown(f'<div class="progress-bar"><div class="progress-fill" style="width:{max(pct,8)}%;background:{m["color"]}">{m["value"]:.1f}{m["unit"]}</div></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🍽️ 各餐明细")
    for mlabel, mkey in MEAL_TYPES.items():
        items = td.get('meals',{}).get(mkey,[])
        if items:
            sub = sum(r['calories'] for r in items)
            foods_str = " | ".join([f"{r['emoji']}{r['food']}{r['weight_g']}g={r['calories']}kcal" for r in items])
            st.markdown(f"**{mlabel}** {sub:.0f}千卡")
            st.caption(foods_str)
# ==================== 页面4: 周趋势 ====================
elif page == "\U0001f4c8 周趋势":
    st.markdown('<p class="cartoon-title">📈 一周趋势</p>', unsafe_allow_html=True)
    weekly = get_weekly()
    days = [w['day'] for w in weekly]
    intakes = [w['intake'] for w in weekly]
    burns = [w['burn'] for w in weekly]
    import pandas as pd
    df = pd.DataFrame({"日期": days, "摄入": intakes, "消耗": burns})
    st.bar_chart(df.set_index("日期"))
    st.markdown("### 📋 每日详情")
    for w in weekly:
        net = w['intake'] - w['burn']
        cols = st.columns([2,1,1,1])
        cols[0].write(f"**{w['day']}** ({w['date']})")
        cols[1].write(f"🍽️ {w['intake']}kcal")
        cols[2].write(f"🔥 {w['burn']}kcal")
        cols[3].write(f"📈 净{net:.0f}kcal")
    avg_in = sum(intakes)/7
    avg_burn = sum(burns)/7
    st.markdown("---")
    c1,c2,c3 = st.columns(3)
    c1.metric("日均摄入", f"{avg_in:.0f} 千卡")
    c2.metric("日均消耗", f"{avg_burn:.0f} 千卡")
    c3.metric("日均净摄入", f"{avg_in-avg_burn:.0f} 千卡")
# ==================== 页面5: BMI与建议 ====================
elif page == "\U0001f4a1 BMI与建议":
    st.markdown('<p class="cartoon-title">💡 BMI计算与饮食建议</p>', unsafe_allow_html=True)
    st.markdown("### 📐 计算你的BMI")
    c1, c2, c3 = st.columns(3)
    height = c1.number_input("身高 (cm)", min_value=100, max_value=250, value=170, step=1)
    weight = c2.number_input("体重 (kg)", min_value=30, max_value=200, value=65, step=1)
    age = c3.number_input("年龄", min_value=10, max_value=100, value=25, step=1)
    gender = st.radio("性别", ["男","女"], horizontal=True)
    bmi, bmi_label, bmi_color, bmi_emoji = calc_bmi(height, weight)
    st.markdown(f'<div style="text-align:center;padding:20px;background:white;border-radius:20px;border:3px solid {bmi_color};margin:10px 0;">'
                f'<span style="font-size:3rem;">{bmi_emoji}</span><br>'
                f'<span style="font-size:2rem;font-weight:bold;color:{bmi_color};">BMI: {bmi:.1f}</span><br>'
                f'<span style="font-size:1.3rem;">分类: {bmi_label}</span></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🎯 选择你的目标")
    if bmi < 18.5:
        default_goal = "gain_weight"
        rec = "你偏瘦，建议增重或增肌"
    elif bmi < 24:
        default_goal = "maintain"
        rec = "体重正常，建议保持或塑形"
    elif bmi < 28:
        default_goal = "lose_fat"
        rec = "偏胖，建议减脂"
    else:
        default_goal = "lose_weight"
        rec = "肥胖，建议健康减肥"
    st.info(f"💡 基于你的BMI，推荐目标: **{rec}**")
    goal = st.selectbox("你的目标", ["lose_fat","lose_weight","gain_muscle","gain_weight","maintain"],
                        format_func=get_goal_name, index=["lose_fat","lose_weight","gain_muscle","gain_weight","maintain"].index(default_goal))
    btmr = st.slider("活动水平", 1.0, 2.0, 1.55, 0.05, format="%.2f", key="bmr_level")
    if gender == "男":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    tdee = bmr * btmr
    if goal == "lose_fat": target = tdee - 300; protein_r = weight * 1.8
    elif goal == "lose_weight": target = tdee - 500; protein_r = weight * 1.5
    elif goal == "gain_muscle": target = tdee + 300; protein_r = weight * 2.0
    elif goal == "gain_weight": target = tdee + 500; protein_r = weight * 1.6
    else: target = tdee; protein_r = weight * 1.2
    st.markdown("---")
    st.markdown("### 📊 你的个性化方案")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("🌡️ 基础代谢", f"{bmr:.0f} 千卡/天")
    c2.metric("🏃 每日消耗", f"{tdee:.0f} 千卡/天")
    c3.metric("🎯 每日目标", f"{target:.0f} 千卡")
    c4.metric("💪 蛋白质", f"{protein_r:.0f}g/天")
    total_protein_cal = protein_r * 4
    fat_r = (target - total_protein_cal) * 0.3 / 9
    carb_r = (target - total_protein_cal - fat_r * 9) / 4
    st.markdown(f"""
    | 营养素 | 每日目标 | 占比 |
    |--------|---------|------|
    | 蛋白质 | {protein_r:.0f}g ({protein_r*4:.0f}千卡) | {protein_r*4/target*100:.0f}% |
    | 脂肪 | {fat_r:.0f}g ({fat_r*9:.0f}千卡) | {fat_r*9/target*100:.0f}% |
    | 碳水 | {carb_r:.0f}g ({carb_r*4:.0f}千卡) | {carb_r*4/target*100:.0f}% |
    """)
    st.markdown("---")
    st.markdown("### 🍽️ 每餐分配建议")
    st.markdown(f"""
    | 餐次 | 热量分配 | 热量 | 蛋白质 | 说明 |
    |------|---------|------|--------|------|
    | 🌅 早餐 | 25% | {target*0.25:.0f}kcal | {protein_r*0.25:.0f}g | 全谷物+蛋奶+水果 |
    | ☀️ 午餐 | 35% | {target*0.35:.0f}kcal | {protein_r*0.35:.0f}g | 主食+肉蛋+蔬菜 |
    | 🌙 晚餐 | 30% | {target*0.30:.0f}kcal | {protein_r*0.30:.0f}g | 清淡为主+适量蛋白 |
    | 🍪 加餐 | 10% | {target*0.10:.0f}kcal | {protein_r*0.10:.0f}g | 坚果/酸奶/水果 |
    """)
    if goal in ("lose_fat", "lose_weight"):
        st.markdown("### 🔥 减脂/减肥饮食建议")
        deficit = tdee - target
        weeks_500g = 500 / (deficit / 7700 * 1000) if deficit > 0 else 999
        st.info(f"每日热量缺口 **{deficit:.0f}千卡** → 约 {weeks_500g:.1f} 周减0.5kg")
        st.markdown("""
        **✅ 推荐食物:** 鸡胸肉、三文鱼、虾仁、西兰花、黄瓜、番茄、糙米、红薯、苹果、草莓
        **❌ 少吃:** 奶茶、汉堡、薯条、蛋糕、巧克力、白米饭
        **💡 技巧:**
        - 每餐先吃蔬菜和蛋白质，最后吃主食
        - 饭前喝一杯水
        - 细嚼慢咽，每餐20分钟以上
        - 晚餐在睡前3小时吃完
        """)
    elif goal == "gain_muscle":
        st.markdown("### 💪 增肌饮食建议")
        st.info(f"每日盈余 **{target-tdee:.0f}千卡** + 高蛋白 **{protein_r:.0f}g**")
        st.markdown("""
        **✅ 推荐食物:** 鸡胸肉、牛肉、鸡蛋、三文鱼、燕麦片、全麦面包、香蕉、坚果
        **💡 技巧:**
        - 每餐保证30-40g蛋白质
        - 训练后30分钟内补充蛋白质+碳水
        - 睡前可补充酪蛋白（牛奶/酸奶）
        - 每公斤体重至少1.6g蛋白质
        """)
    elif goal == "gain_weight":
        st.markdown("### 📈 增重饮食建议")
        st.info(f"每日盈余 **{target-tdee:.0f}千卡**，逐步增重")
        st.markdown("""
        **✅ 推荐食物:** 红烧肉、牛奶、坚果、巧克力、香蕉、米饭、馒头、面包
        **💡 技巧:**
        - 少食多餐，一天5-6顿
        - 选择热量密度高的食物
        - 坚果、花生酱是增重好帮手
        - 配合力量训练增加肌肉量
        """)
    else:
        st.markdown("### ✅ 保持体重建议")
        st.info(f"维持当前 **{target:.0f}千卡/天** 即可")
        st.markdown("""
        **✅ 均衡饮食:** 蛋白质、碳水、脂肪合理搭配
        **🏃 保持运动:** 每周3-5次，每次30分钟以上
        **💡 定期监测:** 每周称重1-2次，及时调整
        """)
