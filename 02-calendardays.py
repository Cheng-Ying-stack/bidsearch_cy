import streamlit as st
from datetime import date

def main():
    st.title("日曆天數計算器_計算天數版")

    st.write("請選擇起始日期與結束日期，計算兩日期間的天數（含起訖日）")

    start_date = st.date_input("起始日期", value=date.today())
    end_date = st.date_input("結束日期", value=date.today())

    if start_date > end_date:
        st.error("錯誤：起始日期不能晚於結束日期")
    else:
        delta_days = (end_date - start_date).days + 1
        st.success(f"兩日期間包含起訖日共有 {delta_days} 天")

if __name__ == "__main__":
    main()
