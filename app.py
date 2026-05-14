import streamlit as st
import csv
from openai import OpenAI
from datetime import datetime
import os

# ================= 1. 网页全局设置 =================
st.set_page_config(page_title="科隆达 - 内容矩阵引擎", page_icon="💡", layout="centered")

st.title("💡 教室灯新媒体矩阵生成器")
st.write("只需输入产品卖点，一键生成适配【抖音、小红书、视频号】的 B 端高转化业务脚本，并支持导出表格。")

# ================= 2. 侧边栏：系统配置区 =================
st.sidebar.header("⚙️ 底层引擎配置")
st.sidebar.write("首次使用请配置大模型接口。")
api_key = st.sidebar.text_input("请输入你的 DeepSeek API 密钥", type="password")

# ================= 3. 主界面：用户操作区 =================
st.subheader("📦 核心产品信息")
product_info = st.text_area(
    "在这里输入或修改产品卖点：", 
    value="专业护眼教室灯。核心卖点：资质证书齐全，包过验收，验收报告齐全。"
)

platforms = {
    "抖音": "受众是刷短视频的工程商和集成商。前3秒犀利痛点留人，强调包过验收，引导私信。",
    "小红书": "受众是私立学校决策者。采用避坑指南形式，展示厚厚的资质证书，打造靠谱专业感。",
    "微信视频号": "受众是校长、教育局干事。语气稳重专业，强调项目合规性、零风险交付。"
}

# ================= 4. 核心执行逻辑 =================
if st.button("🚀 一键生成多平台脚本", use_container_width=True):
    
    if not api_key:
        st.warning("⚠️ 别急，请先在左侧边栏输入你的 DeepSeek API 密钥！")
    else:
        with st.spinner("AI 正在深度思考，疯狂撰写矩阵内容中..."):
            try:
                client = OpenAI(
                    base_url="https://api.deepseek.com/v1",
                    api_key=api_key
                )
                
                script_data = []
                tabs = st.tabs(list(platforms.keys()))
                
                for index, (platform, style) in enumerate(platforms.items()):
                    response = client.chat.completions.create(
                        model="deepseek-v4-pro",
                        messages=[
                            {"role": "system", "content": f"你是一个资深教育照明行业的 B 端新媒体营销专家。当前平台：{platform}。风格要求：{style}"},
                            {"role": "user", "content": f"请为我们的产品写一篇高转化脚本。产品信息：{product_info}。切忌写成C端卖货文案，直击工程验收痛点。"}
                        ]
                    )
                    
                    content = response.choices[0].message.content
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
                    script_data.append([platform, current_time, content])
                    
                    with tabs[index]:
                        st.markdown(content)
                
                # ================= 5. 生成 CSV 并提供下载 =================
                filename = "教室灯_B端矩阵.csv"
                with open(filename, mode='w', encoding='utf-8-sig', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["分发平台", "生成时间", "脚本内容"])
                    writer.writerows(script_data)
                
                st.success("✅ 矩阵脚本全部生成完毕！")
                
                with open(filename, "rb") as file:
                    st.download_button(
                        label="📥 点击下载 Excel 表格",
                        data=file,
                        file_name=filename,
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"❌ 哎呀，连接似乎出了点小问题：{e}")
