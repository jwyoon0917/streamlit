import streamlit as st
import FinanceDataReader as fdr
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO
import plotly.graph_objects as go
import openpyxl
import pandas as pd
import plotly.figure_factory as ff
import plotly.io as pio # Plotly input output
import plotly.express as px # 빠르게 그리는 방법
import plotly.graph_objects as go # 디테일한 설정
import plotly.figure_factory as ff # 템플릿 불러오기
from plotly.subplots import make_subplots # subplot 만들기
from plotly.validators.scatter.marker import SymbolValidator # Symbol 꾸미기에 사용됨

def get_stock_info():
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
    method = "download"
    url = "{0}?method={1}".format(base_url, method)   
    df = pd.read_html(url, header=0, encoding='cp949')[0]
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df

def get_ticker_symbol(company_name):     
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values    
    ticker_symbol = code[0]
    return ticker_symbol

with st.sidebar:
    st.header("회사 이름과 기간을 입력하세요")
    stock_name = st.text_input("회사 이름", "삼성전자")
    date_range = st.date_input(
            "시작일 - 종료일",
            (datetime.date(2019, 1, 1), datetime.date(2021, 12, 31)),
            format="YYYY.MM.DD"
    )
    button_result = st.button('추가 데이터 확인')

st.title("무슨 주식을 사야 부자가 되려나...")

if button_result and stock_name and date_range:
    ticker_symbol = get_ticker_symbol(stock_name)
    start_p = date_range[0]
    end_p = date_range[1] + datetime.timedelta(days=1) 
    df = fdr.DataReader(ticker_symbol, start_p, end_p, exchange="KRX")
    df.index = df.index.date
    st.subheader(f"[{stock_name}] 주가 데이터")
    st.dataframe(df.head())

    df_origin = df.copy()
    df = df.reset_index()
    data = [df['index'], df['Close']]
    
    flg = px.line(df, x = "index", y = "Close", 
                  title="월별 주가 데이터", 
                  labels={
                     "index": "날짜",
                     "Close": "주가",
                  },
                  range_x=[start_p, end_p]
                  )
    
    flg.update_xaxes(showgrid=True, gridwidth=1, gridcolor='gray',
                     showline=True, linecolor='black', linewidth=2,
                     tickformat="%Y-%m"  # 원하는 날짜 형식으로 설정
                     )

    flg.update_yaxes(showgrid=True,gridwidth=1, gridcolor='gray',
                     showline=True, linecolor='black', linewidth=2,
                     tickformat=",.0f"  # 원하는 숫자 형식으로 설정
                     )
    
    flg.update_layout(title="월별 주가 데이터",
                      title_x=0.5,  # 0은 왼쪽, 1은 오른쪽, 0.5는 중앙
                      showlegend=True,
                      plot_bgcolor='white',
                      paper_bgcolor='white'
                      )
    st.plotly_chart(flg)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button('CSV 파일 다운로드', data=df_origin.to_csv(), file_name = f'{stock_name} 주가 정보.csv')
    with col2:
        excel_data = BytesIO()
        df_origin.to_excel(excel_data)
        excel_data.seek(0)
        st.download_button('엑셀 파일 다운로드', data=excel_data.read(), file_name=f'{stock_name} 주가 정보.xlsx')
