import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
import time
import pandas as pd
from io import BytesIO
import os

# ======= 🧠 預設參數與標題 UI =======
st.title("🔍 政府標案_年度查詢工具")
st.subheader("📌 開發者: cycy.exe（2025）")

a = st.text_input("請輸入關鍵字（例如：公司名稱 / 標案關鍵字）", value="乾坤測繪科技有限公司")
b = st.selectbox("標案種類", ["招標", "決標", "公開閱覽及公開徵求", "政府採購預告"])
start_year = st.number_input("起始民國年", min_value=97, max_value=114, value=114)
end_year = st.number_input("結束民國年", min_value=97, max_value=114, value=114)

# ======= 🖥️ 執行爬蟲 =======
if st.button("開始爬蟲，等等你將會獲得整個宇宙 🚀"):
    # 檢查是否在 cloud 環境
    is_cloud = "STREMLIT_CLOUD" in os.environ or "STREMLIT_ENV" in os.environ

    if is_cloud:
        st.error("⚠️ Streamlit Cloud 不支援 Selenium。請於本機執行或改用 API 架構。")
        st.stop()

    with st.spinner("正在擷取資料，請稍候..."):
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            st.error(f"🚨 啟動瀏覽器失敗：{e}")
            st.stop()

        yearly_data = {}
        total_records = 0

        for year in range(start_year, end_year + 1):
            st.write(f"📅 正在處理民國 {year} 年...")
            encoded_query = quote(a)
            status_map = {
                "招標": "TENDER",
                "決標": "AWARD",
                "公開閱覽及公開徵求": "PUBLIC_DISCUSS",
                "政府採購預告": "PROCUREMENT_FORECAST"
            }
            #status_code = status_map.get(b, "AWARD")

            url = (
                f"https://web.pcc.gov.tw/prkms/tender/common/bulletion/readBulletion?"
                f"querySentence={encoded_query}&tenderStatusType={b}"
                f"&sortCol=AWARD_NOTICE_DATE&timeRange={year}&pageSize=100"
            )
            driver.get(url)
            time.sleep(5)

            rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            records = []

            for index, row in enumerate(rows):
                if index < 8:  # 跳過前8行說明
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

            df = pd.DataFrame(records, columns=["項次", "種類", "機關名稱", "標案名稱", "招標公告日期", "決標公告日期", "標案連結", "備註1", "備註2"])
            yearly_data[str(year)] = df
            total_records += len(df)

        driver.quit()

        if total_records == 0:
            st.warning("🥲 沒有抓到任何資料，請確認關鍵字與年份是否正確。")
        else:
            st.success(f"✅ 共擷取 {total_records} 筆資料。")
            # 📊 預覽最新年份資料
            latest_year = str(end_year)
            st.write(f"🧐 預覽資料（民國 {latest_year} 年）")
            st.dataframe(yearly_data[latest_year])

            # Excel 匯出
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
