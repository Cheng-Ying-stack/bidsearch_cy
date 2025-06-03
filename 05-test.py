import streamlit as st
import requests
import pandas as pd
from urllib.parse import quote
from io import BytesIO

st.title("🔍 政府標案_年度標案查詢工具")
st.subheader("📌開發者: cycy.exe, 2025")

# 使用者輸入
a = st.text_input("請輸入關鍵字（例如：公司名稱/標案關鍵字）", value="乾坤測繪科技有限公司")
b = st.selectbox("標案種類", ["招標", "決標", "公開閱覽及公開徵求", "政府採購預告"])
start_year = st.number_input("起始民國年", min_value=97, max_value=114, value=110)
end_year = st.number_input("結束民國年", min_value=97, max_value=114, value=114)

# 類型對應後端參數
type_map = {
    "招標": "tenderNotice",
    "決標": "awardNotice",
    "公開閱覽及公開徵求": "publicNotice",
    "政府採購預告": "procurementForecast"
}

def fetch_api_data(keyword, status_key, year):
    url = "https://web.pcc.gov.tw/prkms/prms-api/v1/procurement/search"
    payload = {
        "queryData": {
            "keyword": keyword,
            "dateType": "awardNoticeDate",
            "tenderStatusType": status_key,
            "range": {
                "dateStart": f"{year - 1911}-01-01",
                "dateEnd": f"{year - 1911}-12-31"
            }
        },
        "page": 1,
        "size": 100
    }
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["data"]["tenders"]
    else:
        return []

if st.button("開始爬蟲，等等你將會獲得整個宇宙 🚀"):
    with st.spinner("正在擷取資料，請稍候..."):
        yearly_data = {}

        for year in range(start_year, end_year + 1):
            st.write(f"📅 正在處理民國 {year} 年...")
            raw_data = fetch_api_data(a, type_map[b], year)

            records = []
            for tender in raw_data:
                records.append([
                    tender.get("tenderNo"),
                    tender.get("tenderName"),
                    tender.get("orgName"),
                    tender.get("awardNoticeDate") or "",
                    tender.get("tenderNoticeDate") or "",
                    tender.get("tenderUrl")
                ])

            df = pd.DataFrame(records, columns=["標案編號", "標案名稱", "機關名稱", "決標日期", "招標日期", "標案連結"])
            yearly_data[str(year)] = df

        st.session_state.yearly_data = yearly_data
        st.session_state.data_loaded = True
        st.success("✅ 資料擷取完成！")

        # 下載 Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for year, df in yearly_data.items():
                df.to_excel(writer, sheet_name=year, index=False)

        st.download_button(
            label="⬇️ 下載 Excel 檔",
            data=output.getvalue(),
            file_name=f"{start_year}-{end_year}_{a}{b}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
