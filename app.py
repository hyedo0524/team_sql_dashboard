from pathlib import Path
import plotly.graph_objects as go
import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots


### 데이터 파일 위치 지정
TARGET_DIR = 'data'
TARGET_CSV = 'data.csv'

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / TARGET_DIR / TARGET_CSV

df = pd.read_csv(DATA_PATH, encoding='euc-kr')
###

### 데이터 품질 확인
# df.head()
# df.shape
# df.isna().sum()
# df.duplicated().sum()
# dt.shape
dt = df.drop_duplicates() # 결측치 제거
st.set_page_config(
	page_title = '집가고 싶SQL 대시보드',
	layout = 'wide',
	)

st.title('한중일 해운에서 국내항만별 특성 분석')
st.caption('출처:해양수산부_해운항만물류정보_한중일물류 입출항정보_20250731')


### 항만별 화물 처리량(톤)
result = dt.groupby('항구청코드')['양적하화물톤'].sum().sort_values(ascending=False)
print(result.apply(lambda x: f"{x:,.0f}"))
###

### 어떤 종류의 선박이 가장 많은가
dt['선박종류명'].value_counts()
###

### 항구 지역별 물류량
#부산
#busan = dt[dt['항구청코드'] == '부산']
#print(busan['선박종류명'].value_counts())

#울산
#ulsan = dt[dt['항구청코드'] == '울산']
#print(ulsan['선박종류명'].value_counts())

#인천
#incheon = dt[dt['항구청코드'] == '인천']
#print(incheon['선박종류명'].value_counts())

result = dt[dt['항구청코드'].isin(['부산','울산','인천'])].groupby('항구청코드')['선박종류명'].value_counts()
print(result)
###

### 위험물 처리
danger = dt.groupby('항구청코드')['위험물톤수'].sum().sort_values(ascending=False)
print(danger)

# 예천 데이터 확인
yeocheon = dt[dt['항구청코드']=='대산']
yeocheon['선박종류명'].value_counts()
###

### 차항지 분석

dt['차항지국가명'].value_counts()

# 중국 항구별 확인
china = dt[dt['차항지국가명'] =='중국']
china['차항지항구명'].value_counts()

# 일본 항구별 확인
japan = dt[dt['차항지국가명'] =='일본']
japan['차항지항구명'].value_counts()

#한국에서는 어느 항구로 많이 가는가

korea = dt[dt['차항지국가명'] =='대한민국']
korea['차항지항구명'].value_counts()


## 분석 및 시각화를 편리하게 하기 위한 새로운 컬럼 추가
dt['항만별 입출항 총수'] = dt.groupby('항구청코드')['항구청코드'].transform('count')

dt['항만별 화물 처리량(톤)'] = dt.groupby('항구청코드')['양적하화물톤'].transform('sum')
dt['항만별 화물 처리량(톤)_표시'] = dt['항만별 화물 처리량(톤)'].apply(lambda x: f"{x:,.0f}")

dt['항만별 위험물 처리량(톤)'] = dt.groupby('항구청코드')['위험물톤수'].transform('sum')
## 


## 상관계수 계산(기존의 화물 처리량이 str형태롤 저장되어 분석을 위해 타입 변경)
dt['항만별 화물 처리량(톤)_표시'] = dt['항만별 화물 처리량(톤)'].astype(int)

cols = ['항만별 입출항 총수','항만별 화물 처리량(톤)_표시', '항만별 위험물 처리량(톤)']

corr = dt[cols].corr()

print(corr)
## 

result = dt.groupby('항구청코드')['양적하화물톤'].sum().sort_values(ascending=False)
result = result.reset_index()

port_count = dt['항구청코드'].value_counts().reset_index()

combined = result.merge(port_count, on='항구청코드')


### 기본적인 streamlit layout
st.set_page_config(
    page_title='항만 별 통계',
    layout='wide',
    page_icon='🛳',
    initial_sidebar_state='locked'
)

# Metric에 넣기 위한 정리

입출항_총수 = dt['항만별 입출항 총수'].sum()
화물처리량 = dt['항만별 화물 처리량(톤)'].sum()
위험물처리량 = dt['항만별 위험물 처리량(톤)'].sum()

### KPI Metric 정리
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        '항만별 입출항 총수',
        value=f'{입출항_총수:,.2f}',
        border=True
    )

with col2:
    st.metric(
        '항만별 화물 처리량(톤)',
        value=f'{화물처리량:,.2f}',
        border=True
    )

with col3:
    st.metric(
        '항만별 위험물 처리량(톤)',
        value=f'{위험물처리량:,.2f}',
        border=True
    )

st.title('국내 항만 별 입출항 통계 및 화물 처리량')
left, right = st.columns(2)

with left:
    st.subheader('항만 별 입출항 통계')
    fig = px.bar(
    port_count,
    x = '항구청코드',
    y = 'count',
    title = '항만별 입출항 통계'
)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader('항만 별 화물 처리량')
    fig = px.bar(
    result,
    x = '항구청코드',
    y = '양적하화물톤',
    title = '항만별 화물 처리량(톤)'
)
    st.plotly_chart(fig, use_container_width=True)

total_area = st.container(border=True)
total_area.subheader('항만 별 입출항 횟수와 화물 처리량')

### 항만 이름을 기준으로 화물량과 건수를 하나의 그래프로 합치기
fig_dual = make_subplots(specs=[[{'secondary_y': True}]])

fig_dual.add_trace(
    go.Bar(
        x=combined['항구청코드'],
        y=combined['양적하화물톤'],
        name='화물 처리량(톤)'
    ),
    secondary_y=False
)

fig_dual.add_trace(
    go.Scatter(
        x=combined['항구청코드'],
        y=combined['count'],
        mode='lines+markers',
        name='입출항 건수',
        line=dict(color='red'),
        marker=dict(size=10)
    ),
    secondary_y=True
)

fig_dual.update_yaxes(title_text='화물 처리량(톤)', secondary_y=False)
fig_dual.update_yaxes(title_text='입출항 건수(건)', secondary_y=True)

total_area.plotly_chart(fig_dual, use_container_width=True)
###

result_area1 = st.container(border=True)
result_area1.subheader('항만의 입출항이 많을 수록 화물 처리량이 많다.')
fig = px.scatter(
    combined,
    x = 'count',
    y = '양적하화물톤',
    hover_name = '항구청코드',
    range_x= [0,4000]
)

result_area1.plotly_chart(fig, use_container_width=True)

st.title('TOP3 항만 분석')
st.subheader('어떤 종류의 선박이 가장 많은가?')
ship_category = dt['선박종류명'].value_counts().reset_index()

fig1 = px.bar(
    ship_category,
    x = '선박종류명',
    y = 'count',
)

st.plotly_chart(
    fig1,
    use_container_width=True,
    key='ship_category_chart'
)

st.subheader('항만 별 적재비중')

col4, col5, col6 = st.columns(3)

# 부산
with col4:
    busan = dt[
        (dt['항구청코드'] == '부산') &
        (dt['적재화물명'] != '해당없음') &
        (dt['적재톤수'] > 0)
    ]

    busan_cargo = (
        busan.groupby('적재화물명', as_index=False)['적재톤수']
        .sum()
    )

    fig_busan = px.pie(
        busan_cargo,
        names='적재화물명',
        values='적재톤수',
        title='부산항 적재화물 비중'
    )

    st.plotly_chart(
        fig_busan,
        use_container_width=True,
        key='busan_cargo_pie'
    )


# 울산
with col5:
    ulsan = dt[
        (dt['항구청코드'] == '울산') &
        (dt['적재화물명'] != '해당없음') &
        (dt['적재톤수'] > 0)
    ]

    ulsan_cargo = (
        ulsan.groupby('적재화물명', as_index=False)['적재톤수']
        .sum()
    )

    fig_ulsan = px.pie(
        ulsan_cargo,
        names='적재화물명',
        values='적재톤수',
        title='울산항 적재화물 비중'
    )

    st.plotly_chart(
        fig_ulsan,
        use_container_width=True,
        key='ulsan_cargo_pie'
    )


# 인천
with col6:
    inchon = dt[
        (dt['항구청코드'] == '인천') &
        (dt['적재화물명'] != '해당없음') &
        (dt['적재톤수'] > 0)
    ]

    inchon_cargo = (
        inchon.groupby('적재화물명', as_index=False)['적재톤수']
        .sum()
    )

    fig_inchon = px.pie(
        inchon_cargo,
        names='적재화물명',
        values='적재톤수',
        title='인천항 적재화물 비중'
    )

    st.plotly_chart(
        fig_inchon,
        use_container_width=True,
        key='inchon_cargo_pie'
    )
###

## 히트맵 작성 
fig = px.imshow(corr, text_auto=True, aspect='auto', title='주요 KPI의 상관관계')

st.plotly_chart(fig, use_container_width=True)
##

### 분석 결과 요약
st.title('분석 결과 요약')

summary_area = st.container(border=True)

with summary_area:
    st.subheader('1. 항만별 입출항 수와 화물 처리량의 관계')
    st.write(
        '입출항 횟수가 많은 항만일수록 화물 처리량도 많은 경향이 나타났으며, '
        '특히 부산·울산·인천항의 순위가 동일하게 나타났다.'
    )

    st.subheader('2. 부산·울산·인천항의 항만 특성')
    st.write(
        '부산항은 컨테이너, 울산항은 석유·화학제품, '
        '인천항은 컨테이너와 국제카페리 중심의 항만 특성이 나타났다.'
    )

    st.subheader('3. 항만별 위험물 처리 특성')
    st.write(
        '울산항과 여천항의 위험물 처리량이 높았으며, '
        '석유·화학제품 및 가스 운송 선박의 높은 비중과 관련된 것으로 분석되었다.'
    )
###