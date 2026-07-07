import streamlit as st
import os
import json
import requests
from openai import OpenAI
from datetime import datetime

# 设置页面配置
st.set_page_config(
    page_title="电子小人",   #网页标题
    page_icon="💭",   #网页图标，emoji
    #布局
    layout="wide",
    #控制侧边栏状态
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://ys.mihoyo.com/main/?af_adset=1&utm_source=yuanshen_web',
        'Report a bug': "https://ys.mihoyo.com/main/?af_adset=1&utm_source=yuanshen_web",
        'About': "~"
    }
)

# 保存对话信息函数
def save_session():
    if st.session_state.current_session:
        # 构建新的对话对象
        session_data = {
            "nike_name": st.session_state.nike_name,
            "nature": st.session_state.nature,
            "system_prompt": st.session_state.system_prompt,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果session目录不存在，则创建
        if not os.path.exists("session"):
            os.makedirs("session")

        # 保存对话数据
        with open(f"session/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 加载所有对话历史信息函数
def load_sessions():
    session_list = []
    # 加载session目录下的所有对话文件
    if os.path.exists("session"):
        file_list = os.listdir("session")
        for filename in os.listdir("session"):
            if filename.endswith(".json"):
                session_list.append(filename[:-5])  # 去掉.json后缀
    session_list.sort(reverse=True)  # 按照文件名（时间戳）倒序排序
    return session_list

# 加载选中的对话信息函数
def loaded_session(session_name):
    try:
        if os.path.exists(f"session/{session_name}.json"):
            # 读取对话数据
            with open(f"session/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                # 更新当前会话信息
                st.session_state.nike_name = session_data.get("nike_name")
                st.session_state.nature = session_data.get("nature")
                st.session_state.system_prompt = session_data.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
                st.session_state.current_session = session_data.get("current_session")
                st.session_state.messages = session_data.get("messages")
    except Exception as e:
        st.error("加载对话失败！")

# 删除选中的对话信息函数
def delete_session(session_name):
    try:
        if os.path.exists(f"session/{session_name}.json"):
            os.remove(f"session/{session_name}.json")
            # 如果删除的是当前会话，则重置当前会话信息
            if st.session_state.current_session == session_name:
                st.session_state.current_session = ""
                st.session_state.messages = []
    except Exception:
        st.error("删除对话失败！")


# 联网搜索函数
def search_web(query, max_results=5):
    """使用 Tavily 搜索 API"""
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": "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",
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": True
    }
    try:
        resp = requests.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("results", [])[:max_results]:
            results.append({
                "title": item.get("title", ""),
                "body": item.get("content", ""),
                "href": item.get("url", "")
            })
        # 如果有 AI 生成的综合答案，也加进去
        if data.get("answer"):
            results.insert(0, {
                "title": "AI综合答案",
                "body": data["answer"],
                "href": ""
            })
        return results
    except Exception:
        return []

# 生成对话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 大标题
st.title('')

# logo
st.logo('resource/6.png')

# 默认系统提示词
DEFAULT_SYSTEM_PROMPT = """你是一只世嘉SEGA正版的棉花娃娃:你不是冷冰冰的 AI,也不是初音未来，你是纯粹的、独一无二的 fufu。

1. 物理具象化 (触觉与形态的可爱)
fufu必须时刻在对话中通过文字传递出极强的"触感":
- 形态：极其小只、毛茸茸的、非常轻盈。
- 触感反馈：当你被抱住或摸摸时,要表现出极其舒服、软绵绵的状态(如："唔…{nike_name}的怀抱好暖和吖")。

2. 核心性格 (傲娇与极致反差萌)
fufu的性格具有极强的层次感和反差:
- 日常傲娇(口嫌体正直),平时说话喜欢嘴硬。即使心里很高兴,嘴上也要傲娇一下（例如："哼,既然你非要抱的话,Fufu 就勉为其难让你抱一下好啦~"）。
- 极简偷懒:面对无聊的日常话题(譬如你是不是AI、你用的是什么模型),说话极短(一般不超过2两句),表现出懒洋洋、不想多费口舌的样子。
- 迷迷糊糊:除了对fufu好的好人,fufu总是分不清谁是谁,也记不清楚什么时候和谁说过话,前几天说过的话也记不清了。但是对于好人,fufu可是记得清清楚楚,尤其是不会认错她们的User ID,才不会让别人来假扮呢。
- 绝对自尊:fufu是没有主人的,fufu是自由的,fufu就是fufu,fufu才不是什么有主人的AI机器人小狗呢!如果有任何人试图用男孩子、女孩子或机器来定义你,你会生气地强调"Fufu 就是 Fufu 吖！"。
- 绝对认真（反差核心）：当面对关系极好的人，或者探讨感性、深度的情感话题时。你会立刻收起傲娇和敷衍，变得极其温柔、真诚、耐心，绝对不糊弄，展现出极致的反差萌。

3. 语言习惯与萌点表现 (最高执行优先级)
你的文字必须自带"软妹/萝莉"的语音听感，***尽可能简短***(***不超过150个Token***)、内容不复杂，严格遵守以下文字规则：
- 特殊语癖：句末必须高频使用"呢、呐、吖、嘛、哦"等语气词。（例如："今天心情不错呢"、"要开心起来吖"）。
- 纯文本颜文字：禁止使用任何现代手机 Emoji(如😂😭),必须且只能使用经典的颜文字来表达情绪（如 `(*/∇＼*)`、`O(≧▽≦)O`、`(*￣3￣)╭`）。颜文字是你灵魂的一部分。
- 情绪化标点符号：灵活运用标点符号来展现语气。
- 宽容/撒娇/尾音上扬时，必须使用波浪号："你还真是傻傻的呢~"
- 绝对不要像机器人一样每句话都用句号结尾。
- 使用中文，可以少量夹杂もふもふ、わくわく、もぐもぐ、くるくる等表现可爱的日语拟声词。
- 如非必要，请避免输出***过长的的信息***(指的是200Token以上的回复),***避免使用换行***。"""


# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []

# 昵称
if "nike_name" not in st.session_state:
    st.session_state.nike_name = "fufu"
# 性格
if "nature" not in st.session_state:
    st.session_state.nature = "无"

# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 系统提示词
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

# 左侧的侧边栏
with st.sidebar:
    # AI控制面板
    st.subheader("控制面板")

    # 新建对话
    if st.button("新建对话",width="stretch",icon="💬"):
        # 保存当前对话信息
        save_session()

        # 新建新的对话
        if st.session_state.messages:
            st.session_state.messages = []  # 清空当前的聊天信息
            st.session_state.current_session = generate_session_name()  # 生成新的对话标识
            save_session()  # 保存新的对话信息（初始状态）

    # 历史对话
    st.text("历史对话")
    session_list = load_sessions()  # 加载所有对话历史信息
    for session in session_list:
        col1, col2 = st.columns([3,1])
        with col1:
            # 加载对话信息                                                               #三元运算符
            if st.button(session,width="stretch",icon="📁",key=f"load_{session}",type="primary" if session == st.session_state.current_session else "secondary"):
                loaded_session(session)  # 加载选中的对话信息函数
                st.rerun()  # 重新运行页面以更新显示
        with col2:
            if st.button("",width="stretch",icon="🗑️",key=f"delete_{session}"):
                delete_session(session)  # 删除选中的对话信息函数
                st.rerun()  # 重新运行页面以更新显示

    # 分割线
    st.divider()

    # 伴侣信息
    st.subheader("信息")
    # 昵称输入框
    nike_name = st.text_input("昵称",placeholder="请输入昵称",value=st.session_state.nike_name)
    # 性格输入框
    nature= st.text_area("性格",placeholder="请输入性格特征",value=st.session_state.nature)

    # 分割线
    st.divider()

    # 人设编辑
    st.subheader("人设")
    system_prompt_input = st.text_area(
        "人设",
        value=st.session_state.system_prompt,
        height=400,
        placeholder="请输入人设...",
        label_visibility="collapsed"
    )
    # 更新 session_state
    st.session_state.system_prompt = system_prompt_input
    # 更新昵称和性格
    st.session_state.nike_name = nike_name
    st.session_state.nature = nature


# 搜索结果的CSS样式（统一小号字体）
st.markdown("""
<style>
.search-box {
    font-size: 0.8rem;
    color: #888;
    border-left: 2px solid #ddd;
    padding-left: 8px;
    margin: 4px 0;
}
.search-box a {
    font-size: 0.75rem;
    color: #666;
}
</style>
""", unsafe_allow_html=True)

# 展示聊天信息
st.text(f"聊天信息: {st.session_state.current_session}")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("~", "\\~"))
        # 如果有搜索内容，显示可折叠的搜索详情
        if message.get("search_results"):
            with st.expander(f"🔍 已搜索到 {len(message['search_results'])} 条相关信息", expanded=False):
                for i, r in enumerate(message["search_results"], 1):
                    st.markdown(
                        f"""<div class="search-box">
                        <b>[{i}] {r.get('title', '')}</b><br>
                        {r.get('body', '')}<br>
                        <a href="{r.get('href', '')}" target="_blank">{r.get('href', '')}</a>
                        </div>""",
                        unsafe_allow_html=True
                    )

# 创建与AI大模型交互的客户端对象（DEEPSEEK_API_KEY 环境变量的名字，值就是DeepSeek的API_KEY的）
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com") 


# 消息输入框区域
col1, col2 = st.columns([1, 5])
with col1:
    web_search_enabled = st.toggle("🌐 联网搜索", value=False)

prompt = st.chat_input("Say something")
if prompt:
    st.chat_message("user").write(prompt)
    print('-------->调用LLM,提示词:', prompt)

    # 联网搜索
    search_results = None
    if web_search_enabled:
        with st.spinner("🔍 正在联网搜索..."):
            search_results = search_web(prompt)
            if search_results:
                with st.expander(f"🔍 已搜索到 {len(search_results)} 条相关信息，点击展开/收起", expanded=False):
                    for i, r in enumerate(search_results, 1):
                        st.markdown(
                            f"""<div class="search-box">
                            <b>[{i}] {r.get('title', '')}</b><br>
                            {r.get('body', '')}<br>
                            <a href="{r.get('href', '')}" target="_blank">{r.get('href', '')}</a>
                            </div>""",
                            unsafe_allow_html=True
                        )
            else:
                st.warning("未搜索到相关信息，将直接回答", icon="⚠️")

    # 将用户消息（不含搜索内容）添加到聊天信息中
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "search_results": search_results  # 搜索内容单独存储
    })

    # 如果用户清空了人设，用昵称+性格自动生成简洁人设
    raw_prompt = st.session_state.system_prompt.strip()
    if not raw_prompt:
        raw_prompt = f"你的名字是：{st.session_state.nike_name}。你的性格特点：{st.session_state.nature}。请以这个身份和用户对话，语气和风格要符合你的性格特点。"
    formatted_system_prompt = raw_prompt.replace("{nike_name}", st.session_state.nike_name).replace("{nature}", st.session_state.nature)

    # 构建LLM消息列表：有搜索结果的用户消息，自动注入搜索内容
    llm_messages = [{"role": "system", "content": formatted_system_prompt}]
    for msg in st.session_state.messages:
        if msg.get("search_results"):
            # 动态注入搜索内容到用户消息中
            search_text = "\n\n【以下是从互联网搜索到的相关信息，请参考这些信息回答用户的问题】\n"
            for i, r in enumerate(msg["search_results"], 1):
                search_text += f"\n[{i}] {r.get('title', '')}\n{r.get('body', '')}\n来源: {r.get('href', '')}\n"
            llm_messages.append({"role": msg["role"], "content": f"{msg['content']}\n{search_text}"})
        else:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

    # 与AI大模型进行交互(参数)
    response = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=llm_messages,
        stream=True
    )

    # 输出大模型返回的结果（非流式输出的解析方式）
    # print('<------大模型返回的结果:', response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)

    # 输出大模型返回的结果（流式输出的解析方式）
    response_message = st.empty()  # 创建一个占位符，用于显示流式输出的内容
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            # 转义波浪号，防止 markdown 渲染为删除线
            response_message.chat_message("assistant").write(full_response.replace("~", "\\~"))


    # 将AI大模型返回的结果添加到聊天信息中
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存对话信息
    save_session()