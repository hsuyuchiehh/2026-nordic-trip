import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- 1. 設定頁面與樣式 ---
st.set_page_config(page_title="2026 北歐壯遊手冊", page_icon="❄️", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .day-card {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border-left: 8px solid #1e3a8a; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        height: 100%;
    }
    .timeline { font-family: monospace; color: #1e3a8a; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 完整行程資料庫 (根據 19 天行程表重構) ---
itinerary_db = {
    "🇸🇪 瑞典 (D1-D2)": {
        "days": {
            "10/18 (D1)": {
                "title": "斯德哥爾摩：抵達與整備", "lat": 59.3293, "lon": 18.0686, 
                "activity": "<span class='timeline'>09:00</span> 抵達 ARN 機場、搭乘機場快線<br><span class='timeline'>13:00</span> 裝備採買 (XXL/Stadium 雪靴、防寒衣)<br><span class='timeline'>16:00</span> 老城區 (Gamla Stan) 彩色房子攝影", 
                "eat": "早：Max Burger<br>午：Kajsas Fisk 魚湯<br>晚：瑞典經典料理", 
                "stay": "Stockholm Generator"
            },
            "10/19 (D2)": {
                "title": "斯德哥爾摩：日出與夕陽攝影", "lat": 59.3193, "lon": 18.0786, 
                "activity": "<span class='timeline'>07:30</span> 船島 (Skeppsholmen) 日出攝影<br><span class='timeline'>11:00</span> 南島漫步、市政廳周邊<br><span class='timeline'>16:00</span> Mariaberget 觀景台夕陽", 
                "eat": "早：青旅自理<br>午：市區簡餐<br>晚：市區外食", 
                "stay": "Stockholm Generator"
            },
        }
    },
    "🇳🇴 挪威 (D3-D5)": {
        "days": {
            "10/20 (D3)": {
                "title": "特羅姆瑟：飛向北極圈", "lat": 69.6492, "lon": 18.9553, 
                "activity": "<span class='timeline'>09:00</span> 搭機飛往特羅姆瑟 (Tromsø)<br><span class='timeline'>14:00</span> Eurospar 超市大採買 (三日份食材)<br><span class='timeline'>17:00</span> Fjellheisen 纜車觀賞極地夜景", 
                "eat": "午：移動簡餐<br>晚：自炊挪威鮭魚", 
                "stay": "45 Strandvegen 民宿"
            },
            "10/21 (D4)": {
                "title": "特羅姆瑟：峽灣與桑拿跳海", "lat": 69.6480, "lon": 18.9600, 
                "activity": "<span class='timeline'>09:00</span> 雪地摩托車 / 峽灣遊船 (半日探索)<br><span class='timeline'>16:00</span> Pust 桑拿 (碼頭跳海降溫體驗)", 
                "eat": "午：活動含餐/自備<br>晚：自炊北極蝦", 
                "stay": "45 Strandvegen 民宿"
            },
            "10/22 (D5)": {
                "title": "特羅姆瑟：惡魔牙齒與極光守候", "lat": 69.4891, "lon": 17.3000, 
                "activity": "<span class='timeline'>08:30</span> Senja 一日團 (惡魔牙齒景觀公路)<br><span class='timeline'>18:00</span> 傍晚返回市區、等待極光", 
                "eat": "午：戶外野餐<br>晚：自炊海鮮大餐", 
                "stay": "45 Strandvegen 民宿"
            },
        }
    },
    "🇮🇸 冰島 (D6-D15)": {
        "days": {
            "10/23 (D6)": {
                "title": "雷克雅維克：冰島降臨", "activity": "<span class='timeline'>中午</span> 搭機飛往凱夫拉維克 (KEF)<br><span class='timeline'>16:00</span> 機場領車 (Kia Sportage 4x4)、超市補給", "eat": "午：移動簡餐<br>晚：自炊羊肉湯", "stay": "雷克雅維克市區",
                "route": [{"name": "凱夫拉維克機場 (KEF)", "lat": 63.9850, "lon": -22.6056}, {"name": "雷克雅維克市區", "lat": 64.1466, "lon": -21.9426}]
            },
            "10/24 (D7)": {
                "title": "南部金圈：經典巡禮", "activity": "<span class='timeline'>09:00</span> 金圈巡禮 (辛格韋德利、秘境瀑布)<br><span class='timeline'>14:00</span> 間歇泉、黃金瀑布、Kerið 火口湖", "eat": "午：自備三明治<br>晚：民宿自炊", "stay": "Hvolsvöllur 區民宿",
                "route": [{"name": "雷克雅維克", "lat": 64.1466, "lon": -21.9426}, {"name": "辛格韋德利", "lat": 64.2559, "lon": -21.1295}, {"name": "間歇泉", "lat": 64.3104, "lon": -20.3024}, {"name": "黃金瀑布", "lat": 64.3271, "lon": -20.1199}, {"name": "Hvolsvöllur", "lat": 63.7498, "lon": -20.2243}]
            },
            "10/25 (D8)": {
                "title": "南岸瀑布：黑沙灘與水簾洞", "activity": "<span class='timeline'>09:30</span> 出發前往尤達洞穴、黑沙灘、斯科加瀑布<br><span class='timeline'>15:00</span> [攝影重點] 水簾洞 (順光拍攝彩虹)", "eat": "午：景點簡餐<br>晚：民宿自炊", "stay": "Vík Cottages",
                "route": [{"name": "Hvolsvöllur", "lat": 63.7498, "lon": -20.2243},{"name": "Gígjagjá (尤達洞穴)", "lat": 63.4169143, "lon": -18.7632538},{"name": "Reynisfjara (黑沙灘)", "lat": 63.4027, "lon": -19.0441},{"name": "Skógafoss (斯科加瀑布)", "lat": 63.5321, "lon": -19.5114},{"name": "Seljalandsfoss (水簾洞)", "lat": 63.6156, "lon": -19.9886}, {"name": "Vík", "lat": 63.4186, "lon": -19.0060}]
            },
            "10/26 (D9)": {
                "title": "東南岸：熔岩苔原與羽毛峽谷", "activity": "<span class='timeline'>09:30</span> Eldhraun 熔岩苔原、教堂城補給<br><span class='timeline'>13:00</span> 羽毛峽谷 (Fjaðrárgljúfur) 步道健行", "eat": "午：自備輕食<br>晚：木屋自炊", "stay": "教堂城周邊木屋",
                "route": [{"name": "Vík", "lat": 63.4186, "lon": -19.0060}, {"name": "Eldhraun", "lat": 63.6769, "lon": -18.1408}, {"name": "羽毛峽谷 (Fjaðrárgljúfur)", "lat": 63.7713, "lon": -18.1718}, {"name": "教堂城", "lat": 63.7828, "lon": -18.0514}]
            },
            "10/27 (D10)": {
                "title": "冰河湖區：鑽石沙灘落日", "activity": "<span class='timeline'>10:00</span> 小冰河湖、傑古沙龍大湖<br><span class='timeline'>15:30</span> [攝影重點] 鑽石沙灘發光冰塊落日", "eat": "午：餐車簡餐<br>晚：民宿自炊", "stay": "Hali 區民宿",
                "route": [{"name": "教堂城", "lat": 63.7828, "lon": -18.0514}, {"name": "傑古沙龍冰河湖", "lat": 64.0484, "lon": -16.1794}, {"name": "Diamond Beach (鑽石沙灘)", "lat": 64.0441, "lon": -16.1827}, {"name": "Hali", "lat": 64.1275, "lon": -16.0188}]
            },
            "10/28 (D11)": {
                "title": "冰河湖區：深度冰川健行", "activity": "<span class='timeline'>09:00</span> 瓦特納深度冰川健行 (6 小時)<br><span class='timeline'>16:00</span> 體力消耗大，返回民宿休息整理照片", "eat": "午：冰上自備乾糧<br>晚：民宿自炊", "stay": "Hali 區民宿",
                "route": [{"name": "Hali", "lat": 64.1275, "lon": -16.0188}, {"name": "瓦特納冰川集合點", "lat": 64.0158, "lon": -16.9664}, {"name": "Hali", "lat": 64.1275, "lon": -16.0188}]
            },
            "10/29 (D12)": {
                "title": "東部峽灣：快艇遊船與長征", "activity": "<span class='timeline'>10:00</span> Zodiac 冰河湖快艇遊船<br><span class='timeline'>14:00</span> 沿東部峽灣公路長征至北部", "eat": "午：霍芬鎮龍蝦餐<br>晚：民宿自炊", "stay": "埃伊爾斯塔濟民宿",
                "route": [{"name": "Hali", "lat": 64.1275, "lon": -16.0188}, {"name": "霍芬 (Höfn)", "lat": 64.2539, "lon": -15.2120}, {"name": "埃伊爾斯塔濟", "lat": 65.2669, "lon": -14.3948}]
            },
            "10/30 (D13)": {
                "title": "北部米湖：火山地熱探索", "activity": "<span class='timeline'>09:00</span> 黛提瀑布 (全歐水量最大瀑布)<br><span class='timeline'>13:00</span> 克拉火山、Hverir 地熱、眾神瀑布", "eat": "午：自備輕食<br>晚：民宿自炊", "stay": "阿克雷里市區",
                "route": [{"name": "埃伊爾斯塔濟", "lat": 65.2669, "lon": -14.3948}, {"name": "Krafla Viti (火口湖)", "lat": 65.7174, "lon": -16.7538}, {"name": "阿克雷里", "lat": 65.6835, "lon": -18.1105}]
            },
            "10/31 (D14)": {
                "title": "西部長征：返回首都慶功", "activity": "<span class='timeline'>10:00</span> 阿克雷里市區採買、愛心紅綠燈<br><span class='timeline'>14:00</span> [換手點] 巨人峽谷攝影與休息 (長征 5.5h)", "eat": "午：自備輕食<br>晚：首都外食慶功", "stay": "雷克雅維克市區",
                "route": [{"name": "阿克雷里", "lat": 65.6835, "lon": -18.1105}, {"name": "Kolugljúfur (巨人峽谷)", "lat": 65.3334, "lon": -20.5713}, {"name": "雷克雅維克", "lat": 64.1466, "lon": -21.9426}]
            },
            "11/01 (D15)": {
                "title": "雷克雅維克：首都慢活與溫泉", "activity": "<span class='timeline'>10:00</span> 首都漫步 (哈爾格林姆教堂、太陽航海者)<br><span class='timeline'>16:00</span> Sky Lagoon 絕美海景溫泉泡湯", "eat": "午：知名熱狗堡<br>晚：市區外食", "stay": "雷克雅維克市區",
                "route": [{"name": "雷克雅維克市區", "lat": 64.1466, "lon": -21.9426}, {"name": "Sky Lagoon", "lat": 64.1164, "lon": -21.9489}]
            },
        }
    },
    "🇬🇧 英國 (D16-D18) & 返程 (D19)": {
        "days": {
            "11/02 (D16)": {
                "title": "倫敦：飛抵與泰晤士河夜景", "lat": 51.5000, "lon": -0.1400, 
                "activity": "<span class='timeline'>09:30</span> KEF 機場還車、搭機飛往倫敦 (LHR/LGW)<br><span class='timeline'>16:00</span> 抵達倫敦市區飯店、泰晤士河夜景", 
                "eat": "午：機場簡餐<br>晚：Flat Iron 牛排", 
                "stay": "倫敦 (Victoria 區)"
            },
            "11/03 (D17)": {
                "title": "倫敦：市集與 Hamilton 音樂劇", "lat": 51.5128, "lon": -0.1230, 
                "activity": "<span class='timeline'>09:00</span> 大笨鐘、西敏寺、柯芬園市集<br><span class='timeline'>19:30</span> [藝文重點] 觀賞《Hamilton》音樂劇", 
                "eat": "午：英式下午茶<br>晚：劇院周邊速食", 
                "stay": "倫敦 (Victoria 區)"
            },
            "11/04 (D18)": {
                "title": "倫敦：博物館與伴手禮採買", "lat": 51.5194, "lon": -0.1270, 
                "activity": "<span class='timeline'>10:00</span> 大英博物館、攝政街採買伴手禮<br><span class='timeline'>15:00</span> 前往機場、辦理退稅、搭機返台", 
                "eat": "午：倫敦市區<br>晚：機上供餐", 
                "stay": "機上休息"
            },
            "11/05 (D19)": {
                "title": "抵達台灣：圓滿結束", "lat": 25.0330, "lon": 121.5654, 
                "activity": "帶著極光與冰川的回憶回家！", 
                "eat": "-", 
                "stay": "溫暖的家"
            },
        }
    }
}

# --- 3. 側邊欄設定 ---
st.sidebar.title("❄️ 2026 北歐圓夢計畫")
main_menu = st.sidebar.radio("請選擇類別", ["詳細行程表", "💰 費用預計", "🎒 行前準備"])

# --- 4. 頁面邏輯：詳細行程表 ---
if main_menu == "詳細行程表":
    chapter = st.sidebar.selectbox("請選擇旅遊區域", list(itinerary_db.keys()))
    st.title(f"📍 {chapter}")
    
    current_chapter_data = itinerary_db[chapter]
    day_options = list(current_chapter_data["days"].keys())
    
    if f"btn_{chapter}" not in st.session_state:
        st.session_state[f"btn_{chapter}"] = day_options[0]

    st.write("### 📅 日程選擇")
    n_cols = min(5, len(day_options)) # 處理英國段只有 4 天的情況
    for i in range(0, len(day_options), n_cols):
        cols = st.columns(n_cols)
        for j, day_key in enumerate(day_options[i:i+n_cols]):
            if cols[j].button(day_key):
                st.session_state[f"btn_{chapter}"] = day_key

    st.divider()

    selected_day = st.session_state[f"btn_{chapter}"]
    data = current_chapter_data["days"][selected_day]
    
    st.markdown(f"## {selected_day} - {data['title']}")
    
    col_map, col_text = st.columns([1.2, 1])

    with col_map:
        if "route" in data:
            lats = [pt["lat"] for pt in data["route"]]
            lons = [pt["lon"] for pt in data["route"]]
            center_lat = sum(lats) / len(lats)
            center_lon = sum(lons) / len(lons)
            
            m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles="CartoDB positron")
            coords = []
            
            for i, pt in enumerate(data["route"]):
                coords.append((pt['lat'], pt['lon']))
                folium.Marker(
                    location=[pt['lat'], pt['lon']],
                    tooltip=f"站點 {i+1}: {pt['name']}",
                    icon=folium.DivIcon(html=f"""
                        <div style="background-color: #0f7b3e; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; font-weight: bold; border: 2px solid white; box-shadow: 1px 1px 3px rgba(0,0,0,0.5);">
                            {i+1}
                        </div>
                        """)
                ).add_to(m)
            
            folium.PolyLine(coords, color="#0f7b3e", weight=4, opacity=0.8).add_to(m)
            m.fit_bounds([[min(lats)-0.1, min(lons)-0.1], [max(lats)+0.1, max(lons)+0.1]]) # 加大邊界避免裁切
            
            st_folium(m, use_container_width=True, height=450, returned_objects=[])
        else:
            map_df = pd.DataFrame({'lat': [data['lat']], 'lon': [data['lon']]})
            st.map(map_df, zoom=11 if selected_day != "11/05 (D19)" else 5) # 台灣那天的 zoom 縮小一點

    with col_text:
        st.markdown(f"""
        <div class="day-card">
            <h4 style="color: #1e3a8a; margin-top: 0;">📋 今日重點</h4>
            <p><b>🏃 核心活動：</b><br>{data['activity']}</p>
            <hr style="margin: 10px 0;">
            <p><b>🍴 餐飲安排：</b><br>{data['eat']}</p>
            <hr style="margin: 10px 0;">
            <p><b>🏨 住宿地點：</b><br>{data['stay']}</p>
        </div>
        """, unsafe_allow_html=True)

# --- 5. 頁面邏輯：費用預計 ---
elif main_menu == "💰 費用預計":
    st.title("💰 2026 壯遊費用精算")
    budget_data = {
        "項目": ["長程機票 (台歐)", "區域航段 (三段)", "瑞典/挪威段", "冰島環島段", "倫敦藝文段", "行政/保險/eSIM", "彈性金"],
        "預算 (TWD)": [35000, 13000, 36000, 75000, 16000, 6000, 5000],
        "說明": ["含來回行李", "北歐跨國飛行", "含 Tromsø 住宿等", "4x4 租車全險+住宿", "Hamilton 音樂劇", "ETIAS/旅平險", "採買與緊急預備"]
    }
    df_budget = pd.DataFrame(budget_data)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.table(df_budget)
    with col2:
        fig = px.pie(df_budget, values='預算 (TWD)', names='項目', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("預計總費用 / 人", "NT$ 186,000")
    c2.metric("瑞典/挪威段預算", "NT$ 36,000")
    c3.metric("Tromsø 3晚總房費", "NT$ 22,665")

# --- 6. 頁面邏輯：行前準備 ---
elif main_menu == "🎒 行前準備":
    st.title("🎒 行前必備清單")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📄 行政與證件")
        st.checkbox("護照正本 (效期 6 個月以上)")
        st.checkbox("英國 ETA 申請完成")
        st.checkbox("申根保險證明 (英文版)")
        st.checkbox("國際駕照 & 台灣駕照正本")
        st.checkbox("Parka & EasyPark App 下載並綁定卡片")

    with col2:
        st.subheader("❄️ 極地裝備")
        st.checkbox("XXL/Stadium 專業雪靴")
        st.checkbox("防風防水外套 (Gore-Tex)")
        st.checkbox("攝影腳架 & 減光鏡")
        st.checkbox("相機備用電池 (低溫消耗極快)")
        st.checkbox("空位行李箱 (倫敦購物用)")