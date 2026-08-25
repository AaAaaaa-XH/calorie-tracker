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
