import openai
import tiktoken


class BaseRole:
    """roleplay聊天机器人的baseline"""

    def __init__(
        self,
        sys_prompt,
        name,
        model="gpt-3.5-turbo",
        enc=tiktoken.get_encoding("cl100k_base"),
        max_history_len=1200,
    ):
        self.sys_prompt = sys_prompt  # 有关角色的 prompt
        self.name = name  # 角色名
        self.history_query = []  # 用户发送内容的记录
        self.history_response = []  # llm回复内容的记录
        self.model = model
        self.enc = enc  # 解码工具
        self.max_history_len = max_history_len

    def get_completion_from_messages(self, messages, temperature=0):
        """一个封装 OpenAI ChatCompletion API 的函数，用于获取模型回复

        Args:
            messages: 与对话相关的核心参数，包含多轮对话的消息
            temperature (float): 0~1，由低到高控制模型回复内容的随机程度

        Returns:
            str: 模型的回复
        """
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def organize_message(self, new_query):
        """整合实际发送给llm的消息（添加prompt和聊天记录）"""
        messages = [{"role": "system", "content": self.sys_prompt}]

        if len(self.history_query) != len(self.history_response):
            print("warning, unmatched history_char length, clean and start new chat")
            self.history_query = []
            self.history_response = []

        for i in range(len(self.history_query)):
            messages.append({"role": "user", "content": self.history_query[i]})
            messages.append({"role": "assistant", "content": self.history_response[i]})

        messages.append({"role": "user", "content": new_query})

        return messages

    def keep_tail(self):
        """更新聊天记录

        确保保留聊天记录在给定的最大token长度限制内，优先保留最新的记录

        Returns:
            tuple: 更新后的聊天记录
            - history_query (list): 用户发送内容记录
            - history_response (list): 模型回复内容记录
        """
        n = len(self.history_query)
        if n == 0:
            return [], []

        if n != len(self.history_response):
            print("warning, unmatched history_char length, clean and start new chat")
            return [], []

        token_len = []
        for i in range(n):
            chat_len = len(self.enc.encode(self.history_query[i]))
            res_len = len(self.enc.encode(self.history_response[i]))
            token_len.append(chat_len + res_len)

        keep_k = 1
        count = token_len[n - 1]

        for i in range(1, n):
            count += token_len[n - 1 - i]
            if count > self.max_history_len:
                break
            keep_k += 1

        self.history_query, self.response_history = (
            self.history_query[-keep_k:],
            self.history_response[-keep_k:],
        )

    def get_response(self, new_query):
        """获取模型对于新发送内容(new_query)的回复，并保存聊天记录

        Args:
            new_query (str): 用户新发送的内容

        Returns:
            str: 模型回复内容
        """
        # 将用户发送内容，预设的 prompt 和聊天记录整合为新的 message
        messages = self.organize_message(new_query)

        # 获取回复
        response = self.get_completion_from_messages(messages)

        # 保存聊天记录
        self.history_query.append(new_query)
        self.history_response.append(response)
        self.keep_tail()

        return response

    def show_history(self):
        """展示聊天记录"""
        for i in range(len(self.history_query)):
            print(f"user: {self.history_query[i]}")
            print(f"{self.name}: {self.history_response[i]}")   
            print()

    def clear_history(self):
        """清除聊天记录"""
        self.history_query.clear()
        self.history_response.clear()