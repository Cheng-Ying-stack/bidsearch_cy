import streamlit as st
from datetime import timedelta, date

def main():
    st.title("日期計算器：標案死線版")

    start_date = st.date_input("起始日期", value=date.today())
    days_passed = st.number_input("經過的日曆天", min_value=1, value=1, step=1)

    # 計算結束日期（包含起始日）
    end_date = start_date + timedelta(days=days_passed - 1)

    st.success(f"結束日期為：{end_date.strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()
