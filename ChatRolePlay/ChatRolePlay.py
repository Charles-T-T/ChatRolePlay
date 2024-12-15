from .config import *
from .utils import *
from .prompts import *
from .KnowledgeDB import KnowledgeDB


class ChatRolePlay:
    """
    ChatRolePlay
    核心类
    多轮对话
    """

    def __init__(
        self,
        llm: str,
        base_prompt: str,
        name: str,
        max_input_token=20000,
        data_folder_path: str = None,
        data_file_path: str = None,
        data_type="txt",
        embedding_name="openai",
        top_k=4,
        debug=False,
    ):
        self.client = get_client(llm)  # 采用的LLM实例
        self.model = models[llm]  # 后续对话采用的模型
        self.base_prompt = base_prompt  # 基本prompt
        self.name = name  # 扮演的角色
        self.max_input_token = max_input_token  # 一次最多输入的token数
        self.chat_history = []  # 聊天记录
        self.chat_summary = []  # 聊天总结
        self.speak_prefix = "「"  # 角色开始说话标识符
        self.speak_suffix = "」"  # 角色结束说话标识符
        self.debug = debug

        if data_folder_path or data_file_path:
            self.story_db = KnowledgeDB(
                data_folder_path,
                data_file_path,
                data_type,
                embedding_name,
                top_k,
                debug=False,
            )
        else:
            self.story_db = None

        self.base_prompt += f"请记住，你是{self.name}， 不是大语言模型\n\n"
        self.prompt_tokens = count_token(
            self.base_prompt + HISTORY_PROMPT + STORY_BG_PROMPT
        )

    def chat(self, query: str, user_role="user") -> str:
        """获取llm的回复，并更新聊天记录

        Args:
            query (str): 用户发送的内容

        Returns:
            str: llm根据用户发送的query给出的回复
        """
        messages = self.organize_messages(query, user_role)
        ans = self.get_llm_ans(messages=messages)

        # 更新历史记录
        user_msg = f"{user_role}:{self.speak_prefix}{query}{self.speak_suffix}"
        llm_msg = f"{self.name}:{self.speak_prefix}{ans}{self.speak_suffix}"

        self.chat_history.append(user_msg)
        self.chat_history.append(llm_msg)

        # TODO 根据实际表现决定返回ans还是llm_msg
        return ans

    def organize_messages(self, query: str, user_role="user") -> list:
        """
        将用户发送内容与prompt、聊天记录整合
        并整理为api可接收的格式

        Args:
            query (str): 用户发送内容
            user_role (str, optional): 用户扮演的角色. Defaults to "user".

        Returns:
            list: 整合后待发送的messages
        """
        # messages = [{"role": "user", "content": self.base_prompt}]
        messages = []
        sys_prompt = self.base_prompt

        # TODO 考虑user_role为scene、旁白等的情况
        user_query = f"{user_role}: {self.speak_prefix}{query}{self.speak_suffix}"

        # 刷新聊天记录，确保最终发送的messages在token限制内
        query_tokens = count_token(user_query)
        available_tokens = self.max_input_token - self.prompt_tokens - query_tokens
        self.refresh_history(available_tokens)

        # 将聊天记录整合到待发送消息
        # messages.append(
        #     {"role": "system", "content": f"{HISTORY_PROMPT}{self.chat_history}"}
        # )
        sys_prompt += HISTORY_PROMPT
        sys_prompt += "<history>\n"
        for dialogue in self.chat_history:
            sys_prompt += dialogue
            sys_prompt += "\n"
        sys_prompt += "<\history>\n\n"

        # 将故事背景整合到待发送消息
        if self.story_db:
            bg = self.story_db.get_related_info(user_query)
            # messages.append({"role": "system", "content": f"{STORY_BG_PROMPT}{bg}"})
            sys_prompt += STORY_BG_PROMPT
            sys_prompt += "<story>\n"
            sys_prompt += bg
            sys_prompt += "<\story>\n\n"

        # 将新query整合到待发送消息
        sys_prompt += NEW_RESPONSE_PROMPT
        messages.append({"role": "system", "content": sys_prompt})
        messages.append({"role": "user", "content": user_query})

        if self.debug:
            print("----------------------Messages to be Sent----------------------")
            for msg in messages:
                for key, value in msg.items():
                    print(f"[{key}]")
                    print(value)
            print("---------------------------------------------------------------")

        return messages

    def refresh_history(self, available_tokens: int):
        """
        刷新聊天记录，以确保发送内容在token数量限制内
        如果超过，则对早期对话进行总结并存储在summaries中

        Args:
            available_tokens (int): 剩余可输入的token数（除去prompt和新query）
        """
        while True:
            tokens = self.count_history_tokens()
            if tokens <= available_tokens:
                return

            if len(self.chat_history) < 4:
                return

            # 提取早期聊天记录进行总结（每次总结一半）
            split = len(self.chat_history) // 2
            to_sum_messages = self.chat_history[:split]
            remain_messages = self.chat_history[split:]

            ask_sum_prompt = ASK_SUM_PROMPT
            for msg in to_sum_messages:
                ask_sum_prompt += msg
                ask_sum_prompt += "\n"
            summary = self.get_llm_ans(ask_sum_prompt)

            # 刷新聊天记录
            self.chat_history = [summary] + remain_messages

    def count_history_tokens(self) -> int:
        """计算当前聊天记录的总token数"""
        return sum(count_token(msg) for msg in self.chat_history)

    def get_llm_ans(self, query=None, role="user", messages=None) -> str:
        """获取llm的回复

        Args:
            query (str): 发送的内容
            role (str, optional): user/system/assistant. Defaults to "user".
            messages (list, optional): 发送的消息列表. Defaults to None.

        Returns:
            str: llm对发送内容的回复
        """
        # TODO 考虑temperature等其他更多参数的选择
        if messages is None:
            if query is None:
                print("Error: empty query / messages!")
                return
            messages = [{"role": role, "content": query}]

        response = self.client.chat.completions.create(
            model=self.model, messages=messages
        )

        return response.choices[0].message.content.strip()
    
    def _clear_history(self):
        self.chat_history = []

    def _display_history(self):
        for dialogue in self.chat_history:
            print(dialogue)
