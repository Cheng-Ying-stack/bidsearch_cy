import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
import time
import pandas as pd
from io import BytesIO

# Streamlit UI
st.title("🔍 政府標案_年度標案查詢工具")
st.subheader("📌開發者: CYCY得第一, 2025")

a = st.text_input("請輸入關鍵字（例如：公司名稱/標案關鍵字）", value="乾坤測繪科技有限公司")
b = st.selectbox("標案種類", ["招標","決標","公開閱覽及公開徵求","政府採購預告" ])
start_year = st.number_input("起始民國年", min_value=97, max_value=114, value=113)
end_year = st.number_input("結束民國年", min_value=97, max_value=114, value=114)

if st.button("開始爬蟲，等等你將會獲得整個宇宙，此網頁目前不能用河河河 🚀"):
    with st.spinner("正在擷取資料，請稍候..."):
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        yearly_data = {}

        for year in range(start_year, end_year + 1):
            st.write(f"📅 正在處理民國 {year} 年...")

            a_encoded = quote(a)
            url = (
                f"https://web.pcc.gov.tw/prkms/tender/common/bulletion/readBulletion?"
                f"querySentence={a_encoded}&tenderStatusType={b}"
                f"&sortCol=AWARD_NOTICE_DATE&timeRange={year}&pageSize=100"
            )
            driver.get(url)
            time.sleep(5)

            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            records = []
            for index, row in enumerate(rows):
                if index < 8:
                    continue
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 9:
                    row_data = [col.text.strip() for col in cols[:9]]
                    try:
                        vendor_cell = cols[9]
                        a_tag = vendor_cell.find_element(By.TAG_NAME, "a")
                        vendor_link = a_tag.get_attribute("href")
                        row_data[6] = vendor_link
                    except:
                        row_data[6] = cols[9].text.strip()
                    records.append(row_data)
            df = pd.DataFrame(records, columns=["項次", "種類", "機關名稱", "標案名稱", "招標公告日期", "決標公告日期", "標案連結", "8", "9"])
            yearly_data[str(year)] = df

        driver.quit()
        st.success("✅ 資料擷取完成！")

        # 顯示預覽
        for year, df in yearly_data.items():
            st.subheader(f"📄 民國 {year} 年")
            st.dataframe(df)

        # 下載連結
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for year, df in yearly_data.items():
                df.to_excel(writer, sheet_name=year, index=False)
        st.download_button(
            label="⬇️ 下載 Excel 檔",
            data=output.getvalue(),
            file_name=f"{start_year}-{end_year}_{a}_{b}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        
