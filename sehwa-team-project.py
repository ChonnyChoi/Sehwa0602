import streamlit as st
import pandas as pd
import folium
import subprocess
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Folium 설치 확인 (Streamlit Cloud용)
try:
    import folium
except ModuleNotFoundError:
    subprocess.run(["pip", "install", "folium"])
    import folium

# GitHub Raw CSV URLs
url1 = "https://raw.githubusercontent.com/ZackWoo05/Sehwa/main/chargerinfo_part1.csv"
url2 = "https://raw.githubusercontent.com/ZackWoo05/Sehwa/main/chargerinfo_part2.csv"

st.set_page_config(page_title="전기차 충전소 지도", layout="wide")
st.title("🔌 전국 전기차 충전소 클러스터 지도")

@st.cache_data(ttl=600)  # 처음 로딩 후 10분 동안 데이터 유지 (중복 로딩 방지)
def load_combined_data(url1, url2):
    df1 = pd.read_csv(url1, encoding="utf-8", low_memory=False)
    df2 = pd.read_csv(url2, encoding="utf-8", low_memory=False)
    df = pd.concat([df1, df2], ignore_index=True)

    df.columns = df.columns.str.strip().str.lower()  # 컬럼 정리

    # '위도경도' 컬럼 확인
    if '위도경도' in df.columns:
        df[['위도', '경도']] = df['위도경도'].str.split(',', expand=True)
    else:
        st.error("❌ '위도경도' 컬럼이 CSV 파일에 존재하지 않습니다!")
        return pd.DataFrame()

    # 숫자형 변환 및 NaN 제거
    df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
    df['경도'] = pd.to_numeric(df['경도'], errors='coerce')
    df.dropna(subset=['위도', '경도'], inplace=True)

    # 대한민국 좌표 범위 내 데이터만 필터링
    df = df[(df['위도'] > 33) & (df['위도'] < 39) & (df['경도'] > 124) & (df['경도'] < 132)]

    # '주소' 컬럼 확인 후 지역 정보 추출
    if '주소' in df.columns:
        df['시도'] = df['주소'].str.split().str[0]
        df['구군'] = df['주소'].str.split().str[1]
    else:
        st.error("❌ '주소' 컬럼이 존재하지 않습니다!")
        return pd.DataFrame()

    return df

# 📍 데이터 로딩 (처음 한 번만 실행)
if "df" not in st.session_state:
    st.session_state.df = load_combined_data(url1, url2)  # 시도와 구군 변경 전까지 유지

df = st.session_state.df

# ✅ 시도 & 구군 선택 유지
if "선택한_시도" not in st.session_state:
    st.session_state.선택한_시도 = df['시도'].dropna().unique()[0]  # 기본값 설정
if "선택한_구군" not in st.session_state:
    st.session_state.선택한_구군 = df[df['시도'] == st.session_state.선택한_시도]['구군'].dropna().unique()[0]

# 🔄 시도 변경
선택한_시도 = st.selectbox("시/도 선택", sorted(df['시도'].dropna().unique()), index=list(df['시도'].dropna().unique()).index(st.session_state.선택한_시도))
if 선택한_시도 != st.session_state.선택한_시도:
    st.session_state.선택한_시도 = 선택한_시도
    st.session_state.선택한_구군 = df[df['시도'] == 선택한_시도]['구군'].dropna().unique()[0]  # 기본 구 선택

# 🔄 구군 변경
구군_목록 = sorted(df[df['시도'] == st.session_state.선택한_시도]['구군'].dropna().unique())
선택한_구군 = st.selectbox("구/군 선택", 구군_목록, index=구군_목록.index(st.session_state.선택한_구군))
if 선택한_구군 != st.session_state.선택한_구군:
    st.session_state.선택한_구군 = 선택한_구군

# 🔎 선택 지역 필터링 (새로 로딩하지 않음)
filtered_df = df[(df['시도'] == st.session_state.선택한_시도) & (df['구군'] == st.session_state.선택한_구군)]

# ✅ 지도 중심 좌표 설정
중심_위도, 중심_경도 = filtered_df['위도'].mean(), filtered_df['경도'].mean()

# 🗺️ 지도 생성 및 마커 추가
m = folium.Map(location=[중심_위도, 중심_경도], zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

# 📍 마커 추가
for _, row in filtered_df.iterrows():
    folium.Marker(
        location=[row['위도'], row['경도']],
        tooltip=row['충전소명'],
        popup=folium.Popup(f"""
            <b>{row['충전소명']}</b><br>
            📍 주소: {row['주소']}<br>
            ⚡ 충전기 타입: {row['충전기타입']}<br>
            🏢 시설: {row['시설구분(대)']} - {row['시설구분(소)']}<br>
        """, max_width=300),
        icon=folium.Icon(color="green", icon="flash")
    ).add_to(marker_cluster)

# 🚀 Streamlit에서 지도 출력
st_folium(m, width=900, height=600)
