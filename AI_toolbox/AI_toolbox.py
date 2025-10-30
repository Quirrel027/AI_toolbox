import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image
import requests
import os

# -------------------- 側邊欄 --------------------
with st.sidebar:
    choose = option_menu(
        "工具欄",  # <-- 標題文字
        ["簡介", "AI聊天", "AI繪圖"],
        icons=['house', 'person lines fill', 'app-indicator'],
        menu_icon="list",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "25px"},
            # 1. 選項文字改為黑色
            "nav-link": {"font-size": "16px", "text-align": "left", "color": "black", "--hover-color": "#eee"},
            # 1. 選中選項文字改為黑色
            "nav-link-selected": {"background-color": "#24A608", "color": "black"},
            # 1. 選單標題「工具欄」文字改為黑色
            "menu-title": {"font-size": "18px", "font-weight": "bold", "color": "black"}
        }
    )
# -------------------- 簡介 --------------------
if choose == "簡介":
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.markdown("""
        <style>
        .font {
            font-size:35px;
            font-family:'Cooper Black';
            color:#FF9633;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown('<p class="font">關於作者</p>', unsafe_allow_html=True)

    with col2:
        # 假設 logo.jpg 檔案存在
        try:
            logo = Image.open("logo.jpg")
            st.image(logo, width=130)
        except FileNotFoundError:
            st.warning("⚠ logo.jpg 檔案未找到，無法顯示圖片。")

    st.markdown("---") # 分隔線

    # 2. 新增的繁體中文介紹文字
    intro_text = """
    
    **AI 百寶箱，整合多種免費 AI 工具，歡迎使用！**

    ChatGPT 最近在網際網路上掀起了一陣熱潮，其高度智能化的功能能夠給我們的現實生活帶來諸多的便利。它可以幫助你寫文章、寫報告、寫週報、做表格、做策劃，甚至還會寫程式碼。只要與文字相關的工作，它幾乎都能給出一份滿意的答卷。
    
    作者趁著有空上去玩了一下，也發現了其中的強大之處。

    那麼本篇文章作者就透過 Streamlit 框架來搭建一個 **AI 百寶箱** 的網頁，其中裡面集成了一系列功能，包括智能聊天機器人、智能繪畫師。大家有興趣還可以另外添加例如配音等功能，核心邏輯就是呼叫第三方的 API 接口，然後做一層封裝和優化。
    
    原出處:https://www.jb51.net/article/276253.htm
    """
    st.markdown(intro_text)

    # 3. 加上左側選擇工具開始使用的提示
    st.markdown("---")
    st.info("💡 請利用左側的**工具欄**選擇功能開始使用！")

# -------------------- AI 聊天（使用 OpenRouter） --------------------
elif choose == "AI聊天":
    st.title("AI聊天機器人 🤖（OpenRouter 免費接口）")

    openrouter_api_key = st.text_input("請輸入你的 OpenRouter API 金鑰：", type="password")

    if openrouter_api_key:
        def chat_with_openrouter(prompt):
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-app-name.streamlit.app",  # 可改成你的網站
                "X-Title": "AI Toolbox Chat"
            }
            data = {
                "model": "gpt-3.5-turbo",  # 或 "mistralai/mixtral-8x7b" 等免費模型
                "messages": [{"role": "user", "content": prompt}],
            }

            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"❌ API 錯誤 ({response.status_code})：{response.text}"

        user_query = st.text_area("請輸入你的問題：", "請問 Python 是什麼？")

        if st.button("發送"):
            with st.spinner("🧠 AI 正在思考中..."):
                try:
                    answer = chat_with_openrouter(user_query)
                    st.success("回答如下：")
                    st.write(answer)
                except Exception as e:
                    st.error(f"發生錯誤：{e}")
    else:
        st.warning("⚠ 請先輸入 OpenRouter API 金鑰")

# -------------------- AI 繪圖（使用 Stability AI） --------------------
elif choose == "AI繪圖":
    st.title("AI繪圖 🎨（Stability AI 免費接口）")

    stability_key = st.text_input("請輸入你的 Stability AI API 金鑰：", type="password")

    if stability_key:
        user_prompt = st.text_input("請輸入你想生成的圖片描述：", "Dogs")

        if st.button("生成圖片"):
            with st.spinner("🎨 AI 正在繪製中，請稍等..."):
                try:
                    os.makedirs("./image", exist_ok=True)

                    # 正確的 multipart/form-data + Accept:image/* 格式
                    response = requests.post(
                        "https://api.stability.ai/v2beta/stable-image/generate/core",
                        headers={
                            "Authorization": f"Bearer {stability_key}",
                            "Accept": "image/*",  # 必須是這個
                        },
                        files={
                            "none": (None, ""),  # 必須包含這個，不然會報 content-type 錯
                        },
                        data={
                            "prompt": user_prompt,
                            "output_format": "png",  # 可改 "jpeg"
                        }
                    )

                    if response.status_code == 200:
                        image_path = "./image/stability.png"
                        with open(image_path, "wb") as f:
                            f.write(response.content)

                        st.success("✅ 圖片生成完成！")
                        img = Image.open(image_path)
                        st.image(img, width=500, caption='Image by Stability AI')
                    else:
                        st.error(f"❌ 生成失敗，錯誤代碼：{response.status_code}\n\n{response.text}")

                except Exception as e:
                    st.error(f"❌ 發生錯誤：{e}")
    else:
        st.warning("⚠ 請先輸入 Stability AI API 金鑰")