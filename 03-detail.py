import streamlit as st
import pandas as pd
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

st.set_page_config(page_title="決標資訊擷取工具", layout="wide")

st.title("📊 標案決標資訊擷取工具")

uploaded_file = st.file_uploader("請上傳含有標案連結的 Excel 檔案", type=["xlsx"])

if uploaded_file:
    dfs = pd.read_excel(uploaded_file, sheet_name=None)  # 讀取所有工作表
    st.success(f"成功讀取 {len(dfs)} 個工作表")

    output_rows = []
    error_links = []

    if st.button("🚀 開始抓取資料"):
        # 啟動 Selenium driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        st.info("Selenium 瀏覽器已啟動，請勿手動關閉視窗")

        for sheet_name, df in dfs.items():
            st.write(f"🔍 處理工作表：{sheet_name}")
            for idx, row in df.iterrows():
                try:
                    link = str(row[6]) #G欄位
                    if link.startswith("http"):
                        driver.get(link)
                        time.sleep(30)

                        # 抓取欄位
                        def get_text_by_label(label):
                            try:
                                return driver.find_element(By.XPATH, f"//*[contains(text(),'{label}')]/following-sibling::td").text.strip()
                            except:
                                return "無資料"

                        detail_vendor = get_text_by_label("得標廠商")
                        original_bid = get_text_by_label("底價金額")
                        final_price = get_text_by_label("決標金額")
                        contract_period = get_text_by_label("履約起迄日期")

                        row_data = list(row) + [detail_vendor, original_bid, final_price, contract_period]
                        output_rows.append(row_data)

                except Exception as e:
                    error_links.append((row[6], str(e)))
                    continue

        driver.quit()
        st.success("✅ 抓取完成")

        # 匯出結果 CSV
        result_df = pd.DataFrame(output_rows, columns=list(df.columns) + ["得標廠商", "底價金額", "決標金額", "履約起迄日期"])
        result_df.to_csv("output_決標資料.csv", index=False, encoding="utf-8-sig")

        st.download_button("📥 下載結果檔案", data=result_df.to_csv(index=False, encoding="utf-8-sig"), file_name="決標資料結果.csv", mime="text/csv")

        if error_links:
            st.warning(f"⚠️ 有 {len(error_links)} 筆資料無法讀取")
            for link, err in error_links:
                st.text(f"{link} - {err}")
