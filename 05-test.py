import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote
from io import BytesIO

# 🧠 標案種類與對應參數對照
type_map = {
    "招標": "tenderDeclaration",
    "決標": "award",
    "公開閱覽及公開徵求": "publicReview",
    "政府採購預告": "procurementForecast",
}

# 🌐 抓取資料函式
def fetch_tenders(keyword, tender_type, year):
    base_url = "https://web.pcc.gov.tw/prkms/tender/common/bulletion/readBulletion"
    params = {
        "querySentence": keyword,
        "tenderStatusType": tender_type,
        "sortCol": "AWARD_NOTICE_DATE",
        "timeRange": year,
        "pageSize": 100,
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(base_url, params=params, headers=headers)

    if res.status_code != 200:
        st.warning(f"⚠️ {year} 年資料擷取失敗（HTTP {res.status_code}）")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table")
    if not table:
        st.info(f"📭 {year} 年沒有找到資料表格。")
        return []

    rows = table.find_all("tr")
    data = []
    for row in rows[1:]:  # 跳過表頭
        cols = row.find_all("td")
        if len(cols) >= 9:
            values = [col.get_text(strip=True) for col in cols[:9]]
            link_tag = cols[6].find("a")
            values[6] = link_tag["href"] if link_tag else values[6]
            data.append(values)

    return data

# 🖥️ Streamlit UI
st.title("🔍 政府標案_年度標案查詢工具")
st.subheader("📌 開發者: cycy.exe, 2025")

a = st.text_input("請輸入關鍵字（例如：公司名稱/標案關鍵字）", value="乾坤測繪科技有限公司")
b = st.selectbox("標案種類", list(type_map.keys()))
start_year = st.number_input("起始民國年", min_value=97, max_value=114, value=110)
end_year = st.number_input("結束民國年", min_value=97, max_value=114, value=114)

if st.button("開始爬蟲，等等你將會獲得整個宇宙 🚀"):
    with st.spinner("📡 資料抓取中，請稍候..."):
        yearly_data = {}

        for year in range(start_year, end_year + 1):
            st.write(f"📅 正在處理民國 {year} 年...")
            records = fetch_tenders(a, type_map[b], year)
            if records:
                df = pd.DataFrame(records, columns=["項次", "種類", "機關名稱", "標案名稱", "招標公告日期", "決標公告日期", "標案連結", "欄位8", "欄位9"])
                yearly_data[str(year)] = df

        if not yearly_data:
            st.error("😢 沒有找到任何資料。")
        else:
            st.success("✅ 資料擷取完成！")

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
