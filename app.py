import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime
import io
import PyPDF2  # 新增：引入 PDF 解析引擎

st.set_page_config(page_title="科隆达 - 私有知识库矩阵引擎", page_icon="🧠", layout="centered")

st.title("🧠 科隆达增强版内容矩阵生成器")
st.write("不仅能批量生成，更能直接读取【TXT/PDF 内部知识库】，让每一句文案都有据可查！")

st.sidebar.header("⚙️ 底层引擎配置")
api_key = st.sidebar.text_input("请输入您的 DeepSeek 官方 API Key", type="password")

platforms = {
    "抖音": "受众是工程商。前3秒犀利痛点留人，强调核心优势，引导私信。",
    "小红书": "受众是决策者或年轻人。采用避坑指南形式，展示硬核参数和证书，打造专业感。",
    "微信视频号": "受众是朋友圈的校长及同行。语气稳重专业，强调项目合规、零风险交付。"
}

# ================= 升级：支持 TXT 和 PDF 的上传 =================
st.subheader("📚 第一步：上传科隆达内部知识库 (支持 TXT / PDF)")
kb_file = st.file_uploader("请上传包含具体参数、证书编号的文件", type=["txt", "pdf"])

knowledge_text = ""
if kb_file:
    # 识别文件类型并分别处理
    if kb_file.name.endswith('.txt'):
        knowledge_text = kb_file.read().decode("utf-8")
        st.success("✅ TXT 知识库读取成功！")
        
    elif kb_file.name.endswith('.pdf'):
        # === 新增：PDF 解析逻辑 ===
        pdf_reader = PyPDF2.PdfReader(kb_file)
        # 循环读取 PDF 的每一页内容并拼接起来
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                knowledge_text += extracted + "\n"
        st.success(f"✅ PDF 知识库读取成功！共解析了 {len(pdf_reader.pages)} 页绝密文件！")

    with st.expander("点击查看 AI 脑子里提取到的文本内容"):
        st.write(knowledge_text)

# ================= 产品表格上传模块 =================
st.subheader("📁 第二步：上传产品分发名单 (Excel/CSV)")
uploaded_file = st.file_uploader("支持 .xlsx 或 .csv 格式", type=["xlsx", "csv"])

if st.button("⚡ 融合知识库，启动批量生成", use_container_width=True):
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
                st.error("❌ 表格格式不对哦！请确保表头有【产品名称】和【产品卖点】。")
            else:
                client = OpenAI(base_url="https://api.deepseek.com", api_key=api_key)
                results = []
                progress_bar = st.progress(0)
                total_rows = len(df)
                
                for index, row in df.iterrows():
                    product_name = row["产品名称"]
                    product_info = row["产品卖点"]
                    
                    for platform, style in platforms.items():
                        system_prompt = f"你是一个资深教育照明行业新媒体营销专家。当前平台：{platform}。风格：{style}。"
                        if knowledge_text != "":
                            system_prompt += f"\n\n【科隆达内部核心知识库】：\n{knowledge_text}\n\n请务必从上述知识库中提取具体的数据（如0.001）、证书编号或专业术语，自然地融入到文案中，增强权威感和说服力！"
                        
                        response = client.chat.completions.create(
                            model="deepseek-chat", 
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"请写一篇高转化脚本。产品名称：{product_name}。核心卖点：{product_info}。"}
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
                st.success("✅ 震撼！融入了私有知识库的顶级专业矩阵脚本已生成！")
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    result_df.to_excel(writer, index=False, sheet_name='增强版矩阵脚本')
                excel_data = output.getvalue()
                
                st.download_button(
                    label="📥 点击下载【专业版 Excel 脚本总表】",
                    data=excel_data,
                    file_name="科隆达_知识库增强版矩阵.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"❌ 处理过程中出现小错误：{e}")
