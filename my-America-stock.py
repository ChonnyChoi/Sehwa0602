
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 글로벌 시가총액 TOP 10 기업 리스트
top_10_companies = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta",
    "TSLA": "Tesla",
    "BRK.B": "Berkshire Hathaway",
    "AVGO": "Broadcom",
    "TSM": "Taiwan Semiconductor"
}

st.title("📈 글로벌 시가총액 TOP 10 기업의 최근 1년간 주가 변화")

# Yahoo Finance에서 데이터 가져오기
data = {}
for ticker in top_10_companies.keys():
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    data[ticker] = df["Close"]

# 데이터프레임 생성
df = pd.DataFrame(data)
df.index = df.index.to_series().dt.strftime("%Y-%m-%d")

# Plotly 그래프 생성
fig = go.Figure()
for ticker, name in top_10_companies.items():
    fig.add_trace(go.Scatter(x=df.index, y=df[ticker], mode="lines", name=name))

fig.update_layout(
    title="최근 1년간 글로벌 시가총액 TOP 10 기업 주가 변화",
    xaxis_title="날짜",
    yaxis_title="주가 (USD)",
    legend_title="기업",
    template="plotly_dark"
)

# Streamlit에서 그래프 표시
st.plotly_chart(fig)
