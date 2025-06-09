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

@st.cache_data(ttl=600)  # 데이터를 캐시하여 10분 동안 유지 (중복 실행 방지)
def load_combined_data(url1, url2):
    """ CSV 데이터 로드 및 전처리 (처음 한 번만 실행) """
    df1 = pd.read_csv(url1, encoding="utf-8", low_memory=False)
    df2 = pd.read_csv(url2, encoding="utf-8", low_memory=False)
    df = pd.concat([df1, df2], ignore_index=True)

    df.columns = df.columns.str.strip().str.lower()  # 컬럼 정리 (공백 제거 + 소문자 변환)

    # '위도경도' 컬럼 존재 여부 확인
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

    # '주소' 컬럼이 존재하는지 확인 후 지역 정보 추출
    if '주소' in df.columns:
        df['시도'] = df['주소'].str.split().str[0]
        df['구군'] = df['주소'].str.split().str[1]
    else:
        st.error("❌ '주소' 컬럼이 존재하지 않습니다!")
        return pd.DataFrame()

    return df

# 📍 데이터 로딩 (처음 한 번만 실행)
df = load_combined_data(url1, url2)

if not df.empty:
    # 모든 시/도 목록 가져오기
    시도_목록 = sorted(df['시도'].dropna().unique())
    선택한_시도 = st.selectbox("시/도 선택", 시도_목록)

    # 선택한 시도의 구/군 목록 가져오기
    구군_목록 = sorted(df[df['시도'] == 선택한_시도]['구군'].dropna().unique())
    선택한_구군 = st.selectbox("구/군 선택", 구군_목록)

    # 선택한 지역의 중심 좌표 계산 (지도 중심 변경)
    지역_데이터 = df[df['시도'] == 선택한_시도]
    if not 지역_데이터.empty:
        중심_위도 = 지역_데이터['위도'].mean()
        중심_경도 = 지역_데이터['경도'].mean()
    else:
        중심_위도, 중심_경도 = 37.5009, 126.9872  # 기본값 (서울 세화고등학교)

    # 📌 ✅ **주변 지역만 포함**
    반경_km = 5  # 설정한 반경 내 데이터만 불러오기
    df['거리'] = ((df['위도'] - 중심_위도)**2 + (df['경도'] - 중심_경도)**2)**0.5 * 111  # 거리 계산 (약 111km = 1도)
    df = df[df['거리'] < 반경_km]  # 반경 내 데이터만 선택

    with st.spinner("🚗 충전소 데이터를 불러오는 중입니다..."):
        # 📊 충전소별 그룹핑 및 집계
        if {'충전기타입', '충전소명', '주소', '시설구분(대)', '시설구분(소)'}.issubset(df.columns):
            grouped = df.groupby(['위도', '경도', '충전소명', '주소'])
            summary_df = grouped.agg({
                '충전기타입': lambda x: ', '.join(sorted(set(x))),
                '시설구분(대)': 'first',
                '시설구분(소)': 'first'
            }).reset_index()
        else:
            st.error("❌ CSV 파일에 필요한 컬럼이 없습니다!")
            summary_df = pd.DataFrame()

        # 🗺️ 지도 생성 및 마커 추가
        m = folium.Map(location=[중심_위도, 중심_경도], zoom_start=12)  # 선택한 도시로 지도 중심 이동
        marker_cluster = MarkerCluster().add_to(m)

        # 📍 마커 추가
        for _, row in summary_df.iterrows():
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
