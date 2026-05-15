import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime
import io # 新增：用于处理原生的文件流

st.set_page_config(page_title="科隆达 - 批量矩阵引擎", page_icon="🚀", layout="centered")

st.title("🚀 科隆达批量内容矩阵生成器")
st.write("上传包含产品参数的表格，一键为您全线产品批量生成【抖音、小红书、视频号】的营销脚本！")

st.sidebar.header("⚙️ 底层引擎配置")
api_key = st.sidebar.text_input("请输入您的 DeepSeek 官方 API Key", type="password")

platforms = {
    "抖音": "受众是刷短视频的工程商或家长。前3秒犀利痛点留人，强调核心优势和背书，引导私信。",
    "小红书": "受众是决策者或年轻人。采用避坑指南形式，展示硬核参数和证书，打造靠谱专业感。",
    "微信视频号": "受众是朋友圈的校长、教育局干事及同行。语气稳重专业，强调项目合规、零风险交付。"
}

st.subheader("📁 第一步：上传产品表格")
uploaded_file = st.file_uploader("支持 .xlsx 或 .csv 格式", type=["xlsx", "csv"])
st.markdown("*(💡 提示：请确保您的表格中包含两列：一列叫 **`产品名称`**，一列叫 **`产品卖点`**)*")

if st.button("⚡ 启动全自动批量生成", use_container_width=True):
    if not api_key:
        st.warning("⚠️ 请先在左侧边栏输入 API Key！")
    elif uploaded_file is None:
        st.warning("⚠️ 请先上传要处理的表格文件！")
    else:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            if "产品卖点" not in df.columns or "产品名称" not in df.columns:
                st.error("❌ 表格格式不对哦！请确保表头有【产品名称】和【产品卖点】这两列。")
            else:
                client = OpenAI(base_url="https://api.deepseek.com", api_key=api_key)
                results = []
                
                progress_bar = st.progress(0)
                total_rows = len(df)
                st.info(f"成功读取 {total_rows} 款产品，AI 正在批量疯狂撰写中，请稍候...")
                
                for index, row in df.iterrows():
                    product_name = row["产品名称"]
                    product_info = row["产品卖点"]
                    
                    for platform, style in platforms.items():
                        response = client.chat.completions.create(
                            model="deepseek-chat", 
                            messages=[
                                {"role": "system", "content": f"你是一个资深教育照明行业新媒体营销专家。当前平台：{platform}。风格：{style}"},
                                {"role": "user", "content": f"请为我们的产品写一篇高转化脚本。产品名称：{product_name}。核心卖点/信息：{product_info}。直击客户痛点。"}
                            ]
                        )
                        content = response.choices[0].message.content
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        results.append({
                            "产品名称": product_name,
                            "原始卖点": product_info,
                            "分发平台": platform,
                            "生成时间": current_time,
                            "生成脚本内容": content
                        })
                    
                    progress_bar.progress((index + 1) / total_rows)
                
                result_df = pd.DataFrame(results)
                st.success("✅ 震撼！所有产品的矩阵脚本已全部批量生成完毕！")
                
                # ================= 核心修改区：直接导出原生 Excel =================
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # 把数据写入内存中的 Excel 文件
                    result_df.to_excel(writer, index=False, sheet_name='矩阵脚本总表')
                excel_data = output.getvalue()
                
                # 下载按钮现在提供的是正宗的 .xlsx 文件
                st.download_button(
                    label="📥 点击下载【原生 Excel 脚本总表】",
                    data=excel_data,
                    file_name="科隆达_全线产品内容矩阵.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ 处理过程中出现小错误：{e}")
