import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# 1. 페이지 설정
st.set_page_config(
    page_title="거래 내역 분석 대시보드",
    page_icon="💸",
    layout="wide"
)

# 2. 커스텀 CSS
st.markdown("""
<style>
    /* 사이드바 전체 스타일 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #2d5a87 100%);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* 사이드바 헤더 스타일 */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
        padding: 0.5rem 0;
    }

    /* 필터 카드 스타일 */
    .filter-card {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    .filter-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .filter-desc {
        font-size: 0.75rem;
        opacity: 0.8;
        margin-bottom: 0.5rem;
    }

    /* 선택 요약 박스 */
    .summary-box {
        background: rgba(76, 175, 80, 0.3);
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-left: 4px solid #4CAF50;
    }

    .summary-item {
        font-size: 0.8rem;
        margin: 0.3rem 0;
    }

    /* 프리셋 버튼 스타일 */
    .stButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: white !important;
        font-size: 0.8rem !important;
        padding: 0.3rem 0.8rem !important;
        border-radius: 20px !important;
        transition: all 0.3s ease !important;
    }

    .stButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        border-color: rgba(255, 255, 255, 0.5) !important;
    }

    /* 리셋 버튼 특별 스타일 */
    [data-testid="stSidebar"] .reset-btn button {
        background: rgba(244, 67, 54, 0.3) !important;
        border-color: #f44336 !important;
        width: 100%;
    }

    /* Expander 스타일 */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }

    /* 멀티셀렉트 스타일 */
    [data-testid="stSidebar"] .stMultiSelect {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 0.5rem;
    }

    /* 메인 KPI 카드 스타일 */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    [data-testid="metric-container"] label {
        color: rgba(255, 255, 255, 0.8) !important;
    }

    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. 타이틀
st.title("📊 거래 내역 분석 대시보드")

# 4. 파일 업로드 (다중 파일 지원)
st.markdown("### 📁 데이터 파일 업로드")
st.caption("여러 파일을 동시에 업로드하면 데이터가 자동으로 병합됩니다.")
uploaded_files = st.file_uploader(
    "Excel(.xlsx) 또는 CSV 파일을 업로드하세요",
    type=["xlsx", "csv"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.warning("⚠️ 분석할 데이터 파일이 아직 업로드되지 않았습니다.")
    st.info("👆 위 영역에 파일을 업로드하면 대시보드가 자동으로 열립니다.")
    st.stop()

# 데이터 로드 함수 (단일 파일)
@st.cache_data
def load_single_file(file_name, file_data):
    try:
        if file_name.endswith('.csv'):
            df = pd.read_csv(file_data)
        else:
            df = pd.read_excel(file_data)
        df['_source_file'] = file_name  # 소스 파일 추적용
        return df
    except Exception as e:
        return None

# 여러 파일 로드 및 병합
dataframes = []
failed_files = []

for uploaded_file in uploaded_files:
    df_single = load_single_file(uploaded_file.name, uploaded_file)
    if df_single is not None:
        dataframes.append(df_single)
    else:
        failed_files.append(uploaded_file.name)

if not dataframes:
    st.error("❌ 모든 파일을 읽는 데 실패했습니다. 올바른 형식의 파일인지 확인해주세요.")
    st.stop()

# 데이터 병합
df = pd.concat(dataframes, ignore_index=True)

# 업로드 결과 표시
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("업로드된 파일", f"{len(dataframes)}개")
with col2:
    st.metric("총 데이터 행", f"{len(df):,}개")
with col3:
    if failed_files:
        st.metric("실패한 파일", f"{len(failed_files)}개", delta="오류", delta_color="inverse")
    else:
        st.metric("실패한 파일", "0개")

# 실패한 파일 목록 표시
if failed_files:
    with st.expander("⚠️ 로드 실패한 파일 보기"):
        for f in failed_files:
            st.text(f"- {f}")

# 업로드된 파일 목록
with st.expander("📂 업로드된 파일 목록 보기"):
    for i, f in enumerate(dataframes):
        file_name = f['_source_file'].iloc[0]
        st.text(f"{i+1}. {file_name} ({len(f):,}행)")

st.success(f"✅ {len(dataframes)}개 파일 업로드 완료! 총 {len(df):,}개 행")
st.divider()

# 데이터 전처리
if 'TRANSACTION_APPROVED_MONTH' in df.columns:
    df['TRANSACTION_APPROVED_MONTH'] = df['TRANSACTION_APPROVED_MONTH'].astype(str)
if 'CUSTOMER_CREATEDDATE_MONTH' in df.columns:
    df['CUSTOMER_CREATEDDATE_MONTH'] = df['CUSTOMER_CREATEDDATE_MONTH'].astype(str)

# 기본 리스트 준비
country_list = sorted(df['country'].unique())
service_list = sorted(df['PAYMENT_SERVICE_DIV'].unique())
month_list = sorted(df['TRANSACTION_APPROVED_MONTH'].unique()) if 'TRANSACTION_APPROVED_MONTH' in df.columns else []
source_file_list = sorted(df['_source_file'].unique()) if '_source_file' in df.columns else []

# Top 10 국가 계산
top_10_countries = df.groupby('country')['VOLUMN'].sum().nlargest(10).index.tolist()

# =============================================================================
# 사이드바 - 리디자인
# =============================================================================

# 사이드바 헤더
st.sidebar.markdown("# 🎛️ 분석 필터")

# 필터 초기화 함수
def reset_filters():
    st.session_state.country_select = top_10_countries
    st.session_state.service_select = service_list.copy()
    st.session_state.month_select = month_list.copy()
    if source_file_list:
        st.session_state.source_file_select = source_file_list.copy()

# --- 소스 파일 필터 섹션 (여러 파일 업로드 시에만 표시) ---
if len(source_file_list) > 1:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 소스 파일 필터")
    st.sidebar.caption("분석할 파일을 선택하세요")

    # 소스 파일 프리셋 버튼
    src_col1, src_col2 = st.sidebar.columns(2)
    with src_col1:
        if st.button("전체 파일", key="src_all", use_container_width=True):
            st.session_state.source_file_select = source_file_list.copy()
            st.rerun()
    with src_col2:
        if st.button("선택 해제", key="src_clear", use_container_width=True):
            st.session_state.source_file_select = []
            st.rerun()

    # 소스 파일 멀티셀렉트
    selected_sources = st.sidebar.multiselect(
        "소스 파일 선택",
        source_file_list,
        default=source_file_list,
        key="source_file_select",
        label_visibility="collapsed"
    )
else:
    selected_sources = source_file_list

# --- 국가 필터 섹션 ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌍 국가 필터")
st.sidebar.caption("분석할 국가를 선택하세요")

# 국가 프리셋 버튼
preset_col1, preset_col2, preset_col3 = st.sidebar.columns(3)
with preset_col1:
    if st.button("Top 10", key="country_top10", use_container_width=True):
        st.session_state.country_select = top_10_countries
        st.rerun()
with preset_col2:
    if st.button("전체", key="country_all", use_container_width=True):
        st.session_state.country_select = country_list.copy()
        st.rerun()
with preset_col3:
    if st.button("초기화", key="country_clear", use_container_width=True):
        st.session_state.country_select = []
        st.rerun()

# 국가 멀티셀렉트
selected_countries = st.sidebar.multiselect(
    "국가 선택",
    country_list,
    default=top_10_countries,
    key="country_select",
    label_visibility="collapsed"
)

# --- 서비스 필터 섹션 ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 💳 서비스 타입 필터")
st.sidebar.caption("분석할 서비스 유형을 선택하세요")

# 서비스 프리셋 버튼
svc_col1, svc_col2 = st.sidebar.columns(2)
with svc_col1:
    if st.button("전체 선택", key="svc_all", use_container_width=True):
        st.session_state.service_select = service_list.copy()
        st.rerun()
with svc_col2:
    if st.button("선택 해제", key="svc_clear", use_container_width=True):
        st.session_state.service_select = []
        st.rerun()

# 서비스 멀티셀렉트
selected_services = st.sidebar.multiselect(
    "서비스 타입 선택",
    service_list,
    default=service_list,
    key="service_select",
    label_visibility="collapsed"
)

# --- 기간 필터 섹션 ---
if month_list:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 거래 기간 필터")
    st.sidebar.caption("분석할 거래 월을 선택하세요")

    # 기간 프리셋 버튼
    month_col1, month_col2 = st.sidebar.columns(2)
    with month_col1:
        if st.button("전체 기간", key="month_all", use_container_width=True):
            st.session_state.month_select = month_list.copy()
            st.rerun()
    with month_col2:
        if st.button("선택 해제", key="month_clear", use_container_width=True):
            st.session_state.month_select = []
            st.rerun()

    # 월 멀티셀렉트
    selected_months = st.sidebar.multiselect(
        "거래 월 선택",
        month_list,
        default=month_list,
        key="month_select",
        label_visibility="collapsed"
    )
else:
    selected_months = None

# --- 전체 초기화 버튼 ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔄 필터 관리")

if st.sidebar.button("🔄 모든 필터 초기화", key="reset_all", use_container_width=True):
    reset_filters()
    st.rerun()

# --- 선택 현황 요약 표시 ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 현재 선택 요약")

source_summary = f"""
    <div style="margin-bottom: 0.5rem;">
        <span style="font-size: 1.2rem;">📂</span>
        <strong>파일:</strong> {len(selected_sources) if selected_sources else len(source_file_list)}개 / {len(source_file_list)}개
    </div>
""" if len(source_file_list) > 1 else ""

summary_html = f"""
<div style="background: rgba(255,255,255,0.1); border-radius: 10px; padding: 1rem; margin-top: 0.5rem;">
    {source_summary}
    <div style="margin-bottom: 0.5rem;">
        <span style="font-size: 1.2rem;">🌍</span>
        <strong>국가:</strong> {len(selected_countries)}개 / {len(country_list)}개
    </div>
    <div style="margin-bottom: 0.5rem;">
        <span style="font-size: 1.2rem;">💳</span>
        <strong>서비스:</strong> {len(selected_services)}개 / {len(service_list)}개
    </div>
    <div>
        <span style="font-size: 1.2rem;">📅</span>
        <strong>기간:</strong> {len(selected_months) if selected_months else 0}개월
    </div>
</div>
"""
st.sidebar.markdown(summary_html, unsafe_allow_html=True)

# 선택된 국가 미리보기 (5개까지)
if selected_countries:
    preview = selected_countries[:5]
    preview_text = ", ".join(preview)
    if len(selected_countries) > 5:
        preview_text += f" 외 {len(selected_countries) - 5}개"
    st.sidebar.caption(f"선택된 국가: {preview_text}")

# =============================================================================
# 필터 적용
# =============================================================================
if not selected_countries:
    selected_countries = country_list
if not selected_services:
    selected_services = service_list
if not selected_sources:
    selected_sources = source_file_list

filtered_df = df[
    (df['country'].isin(selected_countries)) &
    (df['PAYMENT_SERVICE_DIV'].isin(selected_services))
]

# 소스 파일 필터 적용
if selected_sources and '_source_file' in df.columns:
    filtered_df = filtered_df[filtered_df['_source_file'].isin(selected_sources)]

if selected_months and 'TRANSACTION_APPROVED_MONTH' in df.columns:
    filtered_df = filtered_df[filtered_df['TRANSACTION_APPROVED_MONTH'].isin(selected_months)]

# =============================================================================
# 탭 구성
# =============================================================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 상세분석", "📉 트렌드", "📥 데이터"])

# =============================================================================
# Tab 1: Overview (Enhanced)
# =============================================================================
with tab1:
    # =========================================================================
    # Section 1: 핵심 KPI (8개 - 2행 4열)
    # =========================================================================
    st.markdown("### 📌 핵심 성과 지표 (KPI)")

    # KPI 계산
    total_vol = filtered_df['VOLUMN'].sum()
    total_trx = filtered_df['TRX_COUNT'].sum()
    avg_vol = total_vol / len(filtered_df) if len(filtered_df) > 0 else 0
    per_trx_avg = total_vol / total_trx if total_trx > 0 else 0
    top_country = filtered_df.groupby('country')['VOLUMN'].sum().idxmax() if not filtered_df.empty else "-"
    unique_customers = filtered_df['CUSTOMERID'].nunique() if 'CUSTOMERID' in filtered_df.columns else 0
    top_service = filtered_df.groupby('PAYMENT_SERVICE_DIV')['VOLUMN'].sum().idxmax() if not filtered_df.empty else "-"
    unique_countries = filtered_df['country'].nunique() if not filtered_df.empty else 0

    # 증감율 계산
    vol_delta = None
    trx_delta = None
    customer_delta = None
    mom_growth = None

    if 'TRANSACTION_APPROVED_MONTH' in filtered_df.columns and len(filtered_df) > 0:
        months = sorted(filtered_df['TRANSACTION_APPROVED_MONTH'].unique())
        if len(months) >= 2:
            latest_month = months[-1]
            prev_month = months[-2]

            current_data = filtered_df[filtered_df['TRANSACTION_APPROVED_MONTH'] == latest_month]
            prev_data = filtered_df[filtered_df['TRANSACTION_APPROVED_MONTH'] == prev_month]

            current_vol = current_data['VOLUMN'].sum()
            prev_vol = prev_data['VOLUMN'].sum()
            current_trx = current_data['TRX_COUNT'].sum()
            prev_trx = prev_data['TRX_COUNT'].sum()

            if prev_vol > 0:
                vol_delta = f"{((current_vol - prev_vol) / prev_vol) * 100:.1f}%"
                mom_growth = ((current_vol - prev_vol) / prev_vol) * 100
            if prev_trx > 0:
                trx_delta = f"{((current_trx - prev_trx) / prev_trx) * 100:.1f}%"

            # 고객 증감율
            if 'CUSTOMERID' in filtered_df.columns:
                current_customers = current_data['CUSTOMERID'].nunique()
                prev_customers = prev_data['CUSTOMERID'].nunique()
                if prev_customers > 0:
                    customer_delta = f"{((current_customers - prev_customers) / prev_customers) * 100:.1f}%"

    # KPI 카드 표시 - Row 1
    kpi_row1 = st.columns(4)
    kpi_row1[0].metric("💰 총 거래 금액", f"{total_vol:,.0f}", delta=vol_delta)
    kpi_row1[1].metric("📊 총 거래 건수", f"{total_trx:,.0f}건", delta=trx_delta)
    kpi_row1[2].metric("💵 건당 평균 거래액", f"{per_trx_avg:,.0f}")
    kpi_row1[3].metric("👥 고유 고객 수", f"{unique_customers:,}명", delta=customer_delta)

    # KPI 카드 표시 - Row 2
    kpi_row2 = st.columns(4)
    kpi_row2[0].metric("🏆 최대 거래 국가", top_country)
    kpi_row2[1].metric("⭐ 최다 이용 서비스", top_service)
    kpi_row2[2].metric("🌍 활성 국가 수", f"{unique_countries}개국")
    if mom_growth is not None:
        growth_emoji = "📈" if mom_growth >= 0 else "📉"
        kpi_row2[3].metric(f"{growth_emoji} MoM 성장률", f"{mom_growth:.1f}%")
    else:
        kpi_row2[3].metric("📈 MoM 성장률", "-")

    st.divider()

    # =========================================================================
    # Section 2: Top 5 순위표 + 미니 트렌드
    # =========================================================================
    st.markdown("### 🏅 Top 5 순위표 & 빠른 트렌드")

    rank_col1, rank_col2, rank_col3 = st.columns(3)

    # Top 5 국가
    with rank_col1:
        st.markdown("#### 🌍 국가별 거래금액 Top 5")
        if not filtered_df.empty:
            top5_countries = filtered_df.groupby('country').agg({
                'VOLUMN': 'sum',
                'TRX_COUNT': 'sum'
            }).sort_values('VOLUMN', ascending=False).head(5).reset_index()
            top5_countries['순위'] = range(1, len(top5_countries) + 1)
            top5_countries['거래금액'] = top5_countries['VOLUMN'].apply(lambda x: f"{x:,.0f}")
            top5_countries['거래건수'] = top5_countries['TRX_COUNT'].apply(lambda x: f"{x:,.0f}")

            # 스타일링된 테이블
            display_df = top5_countries[['순위', 'country', '거래금액', '거래건수']].rename(columns={'country': '국가'})
            st.dataframe(display_df, use_container_width=True, hide_index=True, height=220)

    # Top 5 서비스
    with rank_col2:
        st.markdown("#### 💳 서비스별 거래금액 Top 5")
        if not filtered_df.empty:
            top5_services = filtered_df.groupby('PAYMENT_SERVICE_DIV').agg({
                'VOLUMN': 'sum',
                'TRX_COUNT': 'sum'
            }).sort_values('VOLUMN', ascending=False).head(5).reset_index()
            top5_services['순위'] = range(1, len(top5_services) + 1)
            top5_services['거래금액'] = top5_services['VOLUMN'].apply(lambda x: f"{x:,.0f}")
            top5_services['점유율'] = (top5_services['VOLUMN'] / total_vol * 100).apply(lambda x: f"{x:.1f}%")

            display_svc = top5_services[['순위', 'PAYMENT_SERVICE_DIV', '거래금액', '점유율']].rename(columns={'PAYMENT_SERVICE_DIV': '서비스'})
            st.dataframe(display_svc, use_container_width=True, hide_index=True, height=220)

    # 미니 트렌드 스파크라인
    with rank_col3:
        st.markdown("#### 📈 최근 거래 트렌드")
        if 'TRANSACTION_APPROVED_MONTH' in filtered_df.columns and not filtered_df.empty:
            monthly_trend = filtered_df.groupby('TRANSACTION_APPROVED_MONTH')['VOLUMN'].sum().reset_index()
            monthly_trend = monthly_trend.sort_values('TRANSACTION_APPROVED_MONTH').tail(6)

            if len(monthly_trend) >= 2:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=monthly_trend['TRANSACTION_APPROVED_MONTH'],
                    y=monthly_trend['VOLUMN'],
                    mode='lines+markers+text',
                    fill='tozeroy',
                    fillcolor='rgba(102, 126, 234, 0.3)',
                    line=dict(color='#667eea', width=3),
                    marker=dict(size=8, color='#667eea'),
                    text=[f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}K" for v in monthly_trend['VOLUMN']],
                    textposition='top center',
                    textfont=dict(size=10)
                ))
                fig.update_layout(
                    height=200,
                    margin=dict(l=10, r=10, t=10, b=30),
                    xaxis=dict(title='', tickangle=45),
                    yaxis=dict(title='', showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("트렌드 표시를 위한 데이터가 부족합니다")
        else:
            st.info("시계열 데이터가 없습니다")

    st.divider()

    # =========================================================================
    # Section 3: 전월 대비 비교 분석
    # =========================================================================
    st.markdown("### 📊 전월 대비 상세 비교")

    if 'TRANSACTION_APPROVED_MONTH' in filtered_df.columns and len(filtered_df) > 0:
        months = sorted(filtered_df['TRANSACTION_APPROVED_MONTH'].unique())
        if len(months) >= 2:
            latest_month = months[-1]
            prev_month = months[-2]

            current_data = filtered_df[filtered_df['TRANSACTION_APPROVED_MONTH'] == latest_month]
            prev_data = filtered_df[filtered_df['TRANSACTION_APPROVED_MONTH'] == prev_month]

            compare_col1, compare_col2 = st.columns(2)

            # 국가별 성장률 Top 5
            with compare_col1:
                st.markdown(f"#### 🚀 국가별 성장률 Top 5 ({prev_month} → {latest_month})")

                current_by_country = current_data.groupby('country')['VOLUMN'].sum()
                prev_by_country = prev_data.groupby('country')['VOLUMN'].sum()

                # 공통 국가만 비교
                common_countries = set(current_by_country.index) & set(prev_by_country.index)
                growth_data = []
                for c in common_countries:
                    curr = current_by_country.get(c, 0)
                    prev = prev_by_country.get(c, 0)
                    if prev > 0:
                        growth = ((curr - prev) / prev) * 100
                        growth_data.append({
                            '국가': c,
                            '이전': prev,
                            '현재': curr,
                            '성장률': growth
                        })

                if growth_data:
                    growth_df = pd.DataFrame(growth_data).sort_values('성장률', ascending=False).head(5)

                    fig = px.bar(
                        growth_df,
                        x='성장률',
                        y='국가',
                        orientation='h',
                        color='성장률',
                        color_continuous_scale=['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1'],
                        text=growth_df['성장률'].apply(lambda x: f"{x:+.1f}%")
                    )
                    fig.update_layout(
                        height=250,
                        margin=dict(l=10, r=10, t=10, b=10),
                        showlegend=False,
                        coloraxis_showscale=False,
                        xaxis_title="성장률 (%)",
                        yaxis_title=""
                    )
                    fig.update_traces(textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("비교할 수 있는 데이터가 없습니다")

            # 서비스별 전월 대비
            with compare_col2:
                st.markdown(f"#### 💳 서비스별 전월 대비 ({prev_month} → {latest_month})")

                current_by_svc = current_data.groupby('PAYMENT_SERVICE_DIV')['VOLUMN'].sum().reset_index()
                current_by_svc.columns = ['서비스', '현재']
                prev_by_svc = prev_data.groupby('PAYMENT_SERVICE_DIV')['VOLUMN'].sum().reset_index()
                prev_by_svc.columns = ['서비스', '이전']

                compare_svc = pd.merge(current_by_svc, prev_by_svc, on='서비스', how='outer').fillna(0)
                compare_svc['변화'] = compare_svc['현재'] - compare_svc['이전']
                compare_svc['변화율'] = ((compare_svc['현재'] - compare_svc['이전']) / compare_svc['이전'].replace(0, 1) * 100)

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name='이전',
                    x=compare_svc['서비스'],
                    y=compare_svc['이전'],
                    marker_color='#a4b0be'
                ))
                fig.add_trace(go.Bar(
                    name='현재',
                    x=compare_svc['서비스'],
                    y=compare_svc['현재'],
                    marker_color='#667eea'
                ))
                fig.update_layout(
                    height=250,
                    margin=dict(l=10, r=10, t=10, b=10),
                    barmode='group',
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                    xaxis_title="",
                    yaxis_title=""
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("전월 대비 비교를 위해 최소 2개월 이상의 데이터가 필요합니다")
    else:
        st.info("시계열 데이터가 없어 전월 비교가 불가능합니다")

    st.divider()

    # =========================================================================
    # Section 4: 거래금액 분포 분석
    # =========================================================================
    st.markdown("### 📊 거래 분포 분석")

    dist_col1, dist_col2 = st.columns(2)

    # 국가별 거래금액 분포 (히스토그램)
    with dist_col1:
        st.markdown("#### 📈 국가별 거래금액 분포")
        if not filtered_df.empty:
            country_volumes = filtered_df.groupby('country')['VOLUMN'].sum().reset_index()
            country_volumes = country_volumes.sort_values('VOLUMN', ascending=False)

            # 구간 분류 (5구간)
            max_vol = country_volumes['VOLUMN'].max()
            min_vol = country_volumes['VOLUMN'].min()

            # 로그 스케일로 구간 나누기 (더 의미있는 분포)
            bins = [0, max_vol * 0.01, max_vol * 0.05, max_vol * 0.2, max_vol * 0.5, max_vol * 1.1]
            labels = ['하위', '중하위', '중위', '중상위', '상위']
            country_volumes['구간'] = pd.cut(country_volumes['VOLUMN'], bins=bins, labels=labels, include_lowest=True)

            # 구간별 국가 수 집계
            dist_summary = country_volumes.groupby('구간', observed=True).agg({
                'country': 'count',
                'VOLUMN': 'sum'
            }).reset_index()
            dist_summary.columns = ['구간', '국가수', '거래금액']

            # 가로 바 차트
            colors = ['#95a5a6', '#3498db', '#2ecc71', '#f39c12', '#e74c3c']
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=dist_summary['구간'],
                x=dist_summary['국가수'],
                orientation='h',
                marker_color=colors[:len(dist_summary)],
                text=dist_summary['국가수'].apply(lambda x: f"{x}개국"),
                textposition='inside',
                textfont=dict(color='white', size=12)
            ))
            fig.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="국가 수",
                yaxis_title="",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

            # 구간별 국가 목록
            with st.expander("📋 구간별 국가 목록 보기"):
                for label in ['상위', '중상위', '중위', '중하위', '하위']:
                    countries_in_range = country_volumes[country_volumes['구간'] == label]['country'].tolist()
                    if countries_in_range:
                        emoji = {'상위': '🔴', '중상위': '🟠', '중위': '🟢', '중하위': '🔵', '하위': '⚪'}
                        st.markdown(f"**{emoji.get(label, '')} {label}** ({len(countries_in_range)}개국)")
                        st.caption(", ".join(countries_in_range))

    # 국가 Tier 분류 (가로 바 차트)
    with dist_col2:
        st.markdown("#### 🏅 국가 Tier 분류")
        if not filtered_df.empty:
            country_volumes = filtered_df.groupby('country')['VOLUMN'].sum().sort_values(ascending=False)

            # Tier 분류: 상위 10%, 중상위 25%, 중위 35%, 하위 30%
            total_countries = len(country_volumes)
            tier1_n = max(1, int(total_countries * 0.10))
            tier2_n = max(1, int(total_countries * 0.25))
            tier3_n = max(1, int(total_countries * 0.35))
            tier4_n = total_countries - tier1_n - tier2_n - tier3_n

            tier_data = {
                'Tier': ['Tier 1 (상위 10%)', 'Tier 2 (상위 25%)', 'Tier 3 (중위 35%)', 'Tier 4 (하위 30%)'],
                '국가수': [tier1_n, tier2_n, tier3_n, tier4_n],
                '거래금액': [
                    country_volumes.head(tier1_n).sum(),
                    country_volumes.iloc[tier1_n:tier1_n+tier2_n].sum(),
                    country_volumes.iloc[tier1_n+tier2_n:tier1_n+tier2_n+tier3_n].sum(),
                    country_volumes.tail(tier4_n).sum() if tier4_n > 0 else 0
                ]
            }
            tier_df = pd.DataFrame(tier_data)
            tier_df['점유율'] = (tier_df['거래금액'] / tier_df['거래금액'].sum() * 100).round(1)

            # 가로 바 차트
            fig = go.Figure()
            colors = ['#ffd700', '#c0c0c0', '#cd7f32', '#95a5a6']

            fig.add_trace(go.Bar(
                y=tier_df['Tier'],
                x=tier_df['거래금액'],
                orientation='h',
                marker_color=colors,
                text=tier_df.apply(lambda row: f"{row['국가수']}개국 | {row['점유율']:.1f}%", axis=1),
                textposition='inside',
                textfont=dict(color='white', size=12, family='Arial Black'),
                hovertemplate="<b>%{y}</b><br>거래금액: %{x:,.0f}<br>국가수: %{customdata[0]}개<br>점유율: %{customdata[1]:.1f}%<extra></extra>",
                customdata=tier_df[['국가수', '점유율']].values
            ))

            fig.update_layout(
                height=280,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis_title="거래금액",
                yaxis_title="",
                yaxis=dict(categoryorder='array', categoryarray=tier_df['Tier'].tolist()[::-1]),
                showlegend=False
            )
            fig.update_xaxes(tickformat=",")
            st.plotly_chart(fig, use_container_width=True)

            # Tier별 국가 목록 표시
            with st.expander("📋 Tier별 국가 목록 보기"):
                tier_countries = {
                    '🥇 Tier 1': country_volumes.head(tier1_n).index.tolist(),
                    '🥈 Tier 2': country_volumes.iloc[tier1_n:tier1_n+tier2_n].index.tolist(),
                    '🥉 Tier 3': country_volumes.iloc[tier1_n+tier2_n:tier1_n+tier2_n+tier3_n].index.tolist(),
                    '📊 Tier 4': country_volumes.tail(tier4_n).index.tolist() if tier4_n > 0 else []
                }

                for tier_name, countries in tier_countries.items():
                    if countries:
                        st.markdown(f"**{tier_name}** ({len(countries)}개국)")
                        st.caption(", ".join(countries))

            st.caption(f"💡 총 {total_countries}개 국가를 거래금액 기준으로 4개 Tier로 분류")

    st.divider()

    # =========================================================================
    # Section 5: 기존 차트 (개선된 버전)
    # =========================================================================
    st.markdown("### 📈 주요 차트")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌍 국가별 거래 금액 (Top 10)")
        if not filtered_df.empty:
            country_vol = filtered_df.groupby('country')['VOLUMN'].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(
                country_vol,
                x='country',
                y='VOLUMN',
                color='VOLUMN',
                color_continuous_scale='Blues',
                template='plotly_white',
                text=country_vol['VOLUMN'].apply(lambda x: f"{x/1e6:.1f}M" if x >= 1e6 else f"{x/1e3:.0f}K")
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False, height=350)
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("💳 서비스 점유율")
        if not filtered_df.empty:
            service_vol = filtered_df.groupby('PAYMENT_SERVICE_DIV')['VOLUMN'].sum().reset_index()
            fig = px.pie(
                service_vol,
                values='VOLUMN',
                names='PAYMENT_SERVICE_DIV',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# Tab 2: 상세분석
# =============================================================================
with tab2:
    st.markdown("### 🔥 서비스별 국가 거래 현황")

    if not filtered_df.empty:
        top_countries_chart = filtered_df.groupby('country')['VOLUMN'].sum().nlargest(15).index.tolist()
        heatmap_df = filtered_df[filtered_df['country'].isin(top_countries_chart)]

        # 서비스 타입 목록
        service_types = sorted(heatmap_df['PAYMENT_SERVICE_DIV'].unique())

        # 색상 팔레트
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']

        # 그리드 레이아웃 (3열)
        num_cols = 3
        rows = (len(service_types) + num_cols - 1) // num_cols  # 올림 나눗셈

        for row_idx in range(rows):
            cols = st.columns(num_cols)
            for col_idx in range(num_cols):
                svc_idx = row_idx * num_cols + col_idx
                if svc_idx < len(service_types):
                    service = service_types[svc_idx]
                    color = colors[svc_idx % len(colors)]

                    with cols[col_idx]:
                        # 해당 서비스 데이터 필터링
                        svc_data = heatmap_df[heatmap_df['PAYMENT_SERVICE_DIV'] == service]
                        svc_by_country = svc_data.groupby('country')['VOLUMN'].sum().sort_values(ascending=True).tail(10).reset_index()

                        # 서비스별 바차트
                        fig = px.bar(
                            svc_by_country,
                            x='VOLUMN',
                            y='country',
                            orientation='h',
                            title=f"💳 {service}",
                            color_discrete_sequence=[color]
                        )
                        fig.update_layout(
                            height=300,
                            margin=dict(l=10, r=10, t=40, b=10),
                            showlegend=False,
                            xaxis_title="",
                            yaxis_title="",
                            title_font_size=14
                        )
                        fig.update_xaxes(tickformat=",")
                        st.plotly_chart(fig, use_container_width=True)

        st.caption("💡 각 서비스별 Top 10 국가의 거래금액을 표시합니다")

        # 전체 히트맵 (접기)
        with st.expander("📊 전체 히트맵 보기"):
            pivot = heatmap_df.pivot_table(
                values='VOLUMN',
                index='country',
                columns='PAYMENT_SERVICE_DIV',
                aggfunc='sum',
                fill_value=0
            )

            # 로그 스케일 적용
            pivot_log = np.log1p(pivot)

            fig = px.imshow(
                pivot_log,
                color_continuous_scale='YlOrRd',
                aspect='auto',
                labels=dict(x="서비스 타입", y="국가", color="거래금액(log)")
            )

            fig.update_traces(
                customdata=pivot.values,
                hovertemplate="국가: %{y}<br>서비스: %{x}<br>거래금액: %{customdata:,.0f}<extra></extra>"
            )

            fig.update_layout(
                height=500,
                coloraxis_colorbar=dict(title="거래금액(log)")
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- 국가별 개별 트리맵 ---
    st.markdown("### 🌳 국가별 서비스 구성 트리맵")

    if not filtered_df.empty:
        # Top 9 국가 선택 (3x3 그리드)
        top_9_countries = filtered_df.groupby('country')['VOLUMN'].sum().nlargest(9).index.tolist()

        # 색상 팔레트
        treemap_colors = ['Blues', 'Greens', 'Oranges', 'Purples', 'Reds', 'YlOrBr', 'BuGn', 'PuRd', 'YlGn']

        # 그리드 레이아웃 (3열)
        num_cols = 3
        rows = (len(top_9_countries) + num_cols - 1) // num_cols

        for row_idx in range(rows):
            cols = st.columns(num_cols)
            for col_idx in range(num_cols):
                country_idx = row_idx * num_cols + col_idx
                if country_idx < len(top_9_countries):
                    country = top_9_countries[country_idx]
                    color_scale = treemap_colors[country_idx % len(treemap_colors)]

                    with cols[col_idx]:
                        # 해당 국가 데이터 필터링
                        country_data = filtered_df[filtered_df['country'] == country]
                        country_svc = country_data.groupby('PAYMENT_SERVICE_DIV')['VOLUMN'].sum().reset_index()

                        if not country_svc.empty:
                            # 국가별 트리맵 (서비스 구성)
                            fig = px.treemap(
                                country_svc,
                                path=['PAYMENT_SERVICE_DIV'],
                                values='VOLUMN',
                                color='VOLUMN',
                                color_continuous_scale=color_scale,
                                title=f"🌍 {country}"
                            )
                            fig.update_layout(
                                height=280,
                                margin=dict(l=5, r=5, t=35, b=5),
                                title_font_size=13,
                                coloraxis_showscale=False
                            )
                            fig.update_traces(
                                textinfo="label+percent root",
                                hovertemplate="<b>%{label}</b><br>거래금액: %{value:,.0f}<br>비율: %{percentRoot:.1%}<extra></extra>"
                            )
                            st.plotly_chart(fig, use_container_width=True)

        st.caption("💡 각 국가별 서비스 구성 비율을 트리맵으로 표시합니다 (Top 9 국가)")

        # 전체 트리맵 (접기)
        with st.expander("🌳 전체 통합 트리맵 보기"):
            treemap_data = filtered_df.groupby(['country', 'PAYMENT_SERVICE_DIV'])['VOLUMN'].sum().reset_index()
            treemap_data = treemap_data[treemap_data['country'].isin(top_countries_chart)]

            fig = px.treemap(
                treemap_data,
                path=['country', 'PAYMENT_SERVICE_DIV'],
                values='VOLUMN',
                color='VOLUMN',
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # --- 국가별 서비스 분포 바차트 ---
    st.markdown("### 📊 국가별 서비스 분포")
    if not filtered_df.empty:
        stack_data = filtered_df[filtered_df['country'].isin(top_countries_chart[:10])]
        stack_agg = stack_data.groupby(['country', 'PAYMENT_SERVICE_DIV'])['VOLUMN'].sum().reset_index()

        fig = px.bar(
            stack_agg,
            x='country',
            y='VOLUMN',
            color='PAYMENT_SERVICE_DIV',
            template='plotly_white',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(height=450, legend_title="서비스 타입")
        st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# Tab 3: 트렌드
# =============================================================================
with tab3:
    if 'TRANSACTION_APPROVED_MONTH' not in filtered_df.columns:
        st.warning("⚠️ 시계열 분석을 위한 'TRANSACTION_APPROVED_MONTH' 컬럼이 없습니다.")
    else:
        # --- 전체 트렌드 ---
        st.markdown("### 📈 전체 거래 트렌드")

        monthly = filtered_df.groupby('TRANSACTION_APPROVED_MONTH').agg({
            'VOLUMN': 'sum',
            'TRX_COUNT': 'sum'
        }).reset_index().sort_values('TRANSACTION_APPROVED_MONTH')

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 월별 거래금액 추이")
            fig = px.line(
                monthly,
                x='TRANSACTION_APPROVED_MONTH',
                y='VOLUMN',
                markers=True,
                template='plotly_white'
            )
            fig.update_traces(line_color='#1f77b4', line_width=3)
            fig.update_layout(xaxis_title="월", yaxis_title="거래금액")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("📊 월별 거래건수 추이")
            fig = px.line(
                monthly,
                x='TRANSACTION_APPROVED_MONTH',
                y='TRX_COUNT',
                markers=True,
                template='plotly_white'
            )
            fig.update_traces(line_color='#2ca02c', line_width=3)
            fig.update_layout(xaxis_title="월", yaxis_title="거래건수")
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # --- 국가별 트렌드 ---
        st.markdown("### 🌍 국가별 거래 트렌드")

        if not filtered_df.empty:
            # Top 9 국가 선택
            top_trend_countries = filtered_df.groupby('country')['VOLUMN'].sum().nlargest(9).index.tolist()

            # 색상 팔레트
            trend_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE']

            # 그리드 레이아웃 (3열)
            num_cols = 3
            rows = (len(top_trend_countries) + num_cols - 1) // num_cols

            for row_idx in range(rows):
                cols = st.columns(num_cols)
                for col_idx in range(num_cols):
                    country_idx = row_idx * num_cols + col_idx
                    if country_idx < len(top_trend_countries):
                        country = top_trend_countries[country_idx]
                        color = trend_colors[country_idx % len(trend_colors)]

                        with cols[col_idx]:
                            # 해당 국가 월별 데이터
                            country_monthly = filtered_df[filtered_df['country'] == country].groupby('TRANSACTION_APPROVED_MONTH').agg({
                                'VOLUMN': 'sum',
                                'TRX_COUNT': 'sum'
                            }).reset_index().sort_values('TRANSACTION_APPROVED_MONTH')

                            if not country_monthly.empty:
                                fig = px.line(
                                    country_monthly,
                                    x='TRANSACTION_APPROVED_MONTH',
                                    y='VOLUMN',
                                    markers=True,
                                    title=f"🌍 {country}"
                                )
                                fig.update_traces(line_color=color, line_width=2, marker_size=8)
                                fig.update_layout(
                                    height=250,
                                    margin=dict(l=10, r=10, t=40, b=10),
                                    xaxis_title="",
                                    yaxis_title="",
                                    title_font_size=13,
                                    showlegend=False
                                )
                                fig.update_yaxes(tickformat=",")
                                st.plotly_chart(fig, use_container_width=True)

            st.caption("💡 Top 9 국가의 월별 거래금액 추이를 표시합니다")

            # 전체 국가 비교 (접기)
            with st.expander("📈 전체 국가 트렌드 비교"):
                country_trend = filtered_df[filtered_df['country'].isin(top_trend_countries)].groupby(
                    ['TRANSACTION_APPROVED_MONTH', 'country']
                )['VOLUMN'].sum().reset_index()

                fig = px.line(
                    country_trend,
                    x='TRANSACTION_APPROVED_MONTH',
                    y='VOLUMN',
                    color='country',
                    markers=True,
                    template='plotly_white'
                )
                fig.update_layout(
                    height=450,
                    xaxis_title="월",
                    yaxis_title="거래금액",
                    legend_title="국가"
                )
                st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # --- 서비스별 트렌드 ---
        st.markdown("### 💳 서비스별 월간 트렌드")
        service_monthly = filtered_df.groupby(['TRANSACTION_APPROVED_MONTH', 'PAYMENT_SERVICE_DIV'])['VOLUMN'].sum().reset_index()
        service_monthly = service_monthly.sort_values('TRANSACTION_APPROVED_MONTH')

        fig = px.line(
            service_monthly,
            x='TRANSACTION_APPROVED_MONTH',
            y='VOLUMN',
            color='PAYMENT_SERVICE_DIV',
            markers=True,
            template='plotly_white',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            xaxis_title="월",
            yaxis_title="거래금액",
            legend_title="서비스 타입",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        if 'CUSTOMER_CREATEDDATE_MONTH' in filtered_df.columns and not filtered_df.empty:
            st.divider()
            st.subheader("👥 코호트 분석: 가입월별 거래 패턴")

            cohort_grouped = filtered_df.groupby('CUSTOMER_CREATEDDATE_MONTH')['VOLUMN'].sum()
            if len(cohort_grouped) > 0:
                top_cohorts = cohort_grouped.nlargest(5).index.tolist()
                cohort_data = filtered_df.groupby(['CUSTOMER_CREATEDDATE_MONTH', 'TRANSACTION_APPROVED_MONTH'])['VOLUMN'].sum().reset_index()
                cohort_data = cohort_data[cohort_data['CUSTOMER_CREATEDDATE_MONTH'].isin(top_cohorts)]

                if not cohort_data.empty:
                    fig = px.line(
                        cohort_data,
                        x='TRANSACTION_APPROVED_MONTH',
                        y='VOLUMN',
                        color='CUSTOMER_CREATEDDATE_MONTH',
                        markers=True,
                        template='plotly_white'
                    )
                    fig.update_layout(
                        xaxis_title="거래월",
                        yaxis_title="거래금액",
                        legend_title="가입월 (코호트)",
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# Tab 4: 데이터
# =============================================================================
with tab4:
    st.markdown("### 📋 필터링된 데이터")

    col1, col2, col3 = st.columns(3)
    col1.metric("총 행 수", f"{len(filtered_df):,}개")
    col2.metric("국가 수", f"{filtered_df['country'].nunique()}개")
    col3.metric("서비스 타입 수", f"{filtered_df['PAYMENT_SERVICE_DIV'].nunique()}개")

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 3])

    # 다운로드용 데이터 준비 (_source_file 컬럼 제외)
    download_df = filtered_df.drop(columns=['_source_file'], errors='ignore')

    # Excel 최대 행 수 제한
    EXCEL_MAX_ROWS = 1048576

    with col1:
        csv = download_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV 다운로드",
            data=csv,
            file_name="filtered_data.csv",
            mime="text/csv"
        )

    with col2:
        if len(download_df) > EXCEL_MAX_ROWS:
            # 데이터가 너무 큰 경우 경고 표시
            st.warning(f"⚠️ 데이터가 Excel 한계({EXCEL_MAX_ROWS:,}행)를 초과하여 Excel 다운로드 불가")
            st.caption("CSV 다운로드를 이용해주세요")
        else:
            # Excel 파일 생성
            excel_buffer = io.BytesIO()
            download_df.to_excel(excel_buffer, index=False, sheet_name='Data', engine='openpyxl')
            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="📥 Excel 다운로드",
                data=excel_data,
                file_name="filtered_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    st.divider()

    st.dataframe(
        filtered_df,
        use_container_width=True,
        height=500
    )
