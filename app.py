import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime

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
# 新增的上传文件组件
uploaded_file = st.file_uploader("支持 .xlsx 或 .csv 格式", type=["xlsx", "csv"])
st.markdown("*(💡 提示：请确保您的表格中包含两列：一列叫 **`产品名称`**，一列叫 **`产品卖点`**)*")

if st.button("⚡ 启动全自动批量生成", use_container_width=True):
    if not api_key:
        st.warning("⚠️ 请先在左侧边栏输入 API Key！")
    elif uploaded_file is None:
        st.warning("⚠️ 请先上传要处理的表格文件！")
    else:
        try:
            # 自动识别并读取表格
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            if "产品卖点" not in df.columns or "产品名称" not in df.columns:
                st.error("❌ 表格格式不对哦！请确保表头有【产品名称】和【产品卖点】这两列。")
            else:
                client = OpenAI(base_url="https://api.deepseek.com", api_key=api_key)
                results = []
                
                # 画一个进度条，让等待过程不枯燥
                progress_bar = st.progress(0)
                total_rows = len(df)
                st.info(f"成功读取 {total_rows} 款产品，AI 正在批量疯狂撰写中，请稍候...")
                
                # 核心大循环：逐行读取 Excel，逐个平台生成
                for index, row in df.iterrows():
                    product_name = row["产品名称"]
                    product_info = row["产品卖点"]
                    
                    for platform, style in platforms.items():
                        response = client.chat.completions.create(
                            model="deepseek-chat", # 批量生成建议用此模型，速度极快且成本极低
                            messages=[
                                {"role": "system", "content": f"你是一个资深教育照明行业新媒体营销专家。当前平台：{platform}。风格：{style}"},
                                {"role": "user", "content": f"请为我们的产品写一篇高转化脚本。产品名称：{product_name}。核心卖点/信息：{product_info}。直击客户痛点。"}
                            ]
                        )
                        content = response.choices[0].message.content
                        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                        
                        # 把结果打包进字典
                        results.append({
                            "产品名称": product_name,
                            "原始卖点": product_info,
                            "分发平台": platform,
                            "生成时间": current_time,
                            "生成脚本内容": content
                        })
                    
                    # 每跑完一款产品，进度条往前走一点
                    progress_bar.progress((index + 1) / total_rows)
                
                # 把最终结果转成 Excel 可读的数据结构
                result_df = pd.DataFrame(results)
                st.success("✅ 震撼！所有产品的矩阵脚本已全部批量生成完毕！")
                
                # 提供下载按钮
                csv_data = result_df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="📥 点击下载【批量矩阵结果总表】",
                    data=csv_data,
                    file_name="科隆达_全线产品内容矩阵.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"❌ 处理过程中出现小错误：{e}")
