import streamlit as st
import pandas as pd
import math
from io import BytesIO

# 計算某距離處的新座標
def get_point_on_line(x0, y0, x1, y1, a):
    dx = x1 - x0
    dy = y1 - y0
    length = math.hypot(dx, dy)  # 等同 sqrt(dx**2 + dy**2)
    if length == 0:
        return x0, y0
    ratio = a / length
    x = x0 + dx * ratio
    y = y0 + dy * ratio
    return x, y

# Streamlit UI
st.title("📍 透地雷達各標註點坐標計算小工具_CYtool")

uploaded_file = st.file_uploader("請上傳包含 [X0_raw], [Y0_raw], [X1_raw], [Y1_raw], 移動距離A 欄位的 Excel 檔案", type=["xls", "xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        # 驗證欄位
        required_cols = ['X0', 'Y0', 'X1', 'Y1', 'A']
        if not all(col in df.columns for col in required_cols):
            st.error(f"❌ Excel 檔案需包含以下欄位：{required_cols}")
        else:
            Ax_list, Ay_list = [], []
            for _, row in df.iterrows():
                ax, ay = get_point_on_line(row['X0'], row['Y0'], row['X1'], row['Y1'], row['A'])
                Ax_list.append(ax)
                Ay_list.append(ay)

            df['Ax'] = Ax_list
            df['Ay'] = Ay_list

            st.success("✅ 計算完成！以下是結果預覽：")
            st.dataframe(df)

            # 下載 Excel 檔案
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            st.download_button(
                label="📥 下載結果 Excel",
                data=output,
                file_name="coordinate_result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"🚨 發生錯誤：{e}")
