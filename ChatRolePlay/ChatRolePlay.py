import gc

from .config import *
from .utils import *
from .prompts import *
from .KnowledgeDB import KnowledgeDB


class ChatRolePlay:
    """
    ChatRolePlay
    """

    def __init__(
        self,
        llm: str,
        base_prompt: str,
        name: str,
        max_output_tokens=256,
        max_summary_tokens= 500,
        max_history_tokens=500,
        data_folder_path: str = None,
        data_file_path: str = None,
        data_type="txt",
        embedding_name="openai",
        top_k=2,
        debug=False,
    ):
        self.client = get_client(llm)  # 采用的LLM实例
        self.model = models[llm]  # 后续对话采用的模型
        self.base_prompt = base_prompt  # 基本prompt
        self.name = name  # 扮演的角色
        self.max_output_tokens = max_output_tokens  # 一次最多输入出的token数
        self.max_summary_tokens = max_summary_tokens
        self.max_history_tokens = max_history_tokens
        self.chat_history = []  # 聊天记录
        self.chat_summary = []  # 聊天总结
        self.speak_prefix = "「"  # 角色开始说话标识符
        self.speak_suffix = "」"  # 角色结束说话标识符
        self.debug = debug

        # 构建角色知识库
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

        self.prompt_tokens = count_token(
            self.base_prompt + HISTORY_PROMPT + STORY_BG_PROMPT + NEW_RESPONSE_PROMPT
        )

    def chat(self, query: str, user_role="user") -> str:
        """获取llm的回复，并更新聊天记录

        Args:
            query (str): 用户发送的内容

        Returns:
            str: llm根据用户发送的query给出的回复
        """
        messages = self.organize_messages(query, user_role)
        ans = self.get_llm_ans(
            messages=messages,
            max_tokens=self.max_output_tokens,
            temperature=0.8,
        )

        # 更新历史记录
        user_msg = f"{user_role}:{self.speak_prefix}{query}{self.speak_suffix}"
        # llm_msg = f"{self.name}:{self.speak_prefix}{ans}{self.speak_suffix}"
        llm_msg = ans

        self.chat_history.append({"role": "user", "content": user_msg})
        self.chat_history.append({"role": "assistant", "content": llm_msg})

        return ans

    def organize_messages(self, query: str, user_role="user") -> list:
        """
        将用户发送内容与prompt、相关情节、聊天记录整合
        并整理为api可接收的格式

        Args:
            query (str): 用户发送内容
            user_role (str, optional): 用户扮演的角色. Defaults to "user".

        Returns:
            list: 整合后待发送的messages
        """
        messages = []
        sys_prompt = self.base_prompt

        # TODO 考虑user_role为scene、旁白等的情况
        user_query = f"{user_role}: {self.speak_prefix}{query}{self.speak_suffix}"

        # 将相关情节整合到待发送消息
        if self.story_db:
            # TODO 此处用于RAG的历史记录条数或许可以进一步优化
            dialogues = ""
            for msg in self.chat_history[-2:]:
                dialogues += msg["content"]
                dialogues += "\n"
            dialogues += user_query
            plot = self.story_db.get_related_info(dialogues)
            sys_prompt += STORY_BG_PROMPT
            sys_prompt += plot

        # 刷新聊天记录，确保聊天记录和总结在 token 限制内
        self.refresh_history()

        sys_prompt += NEW_RESPONSE_PROMPT

        # 将对话总结整合到待发送消息
        if self.chat_summary:
            sys_prompt += HISTORY_PROMPT
            sys_prompt += "<history>\n"
            for summary in self.chat_summary:
                sys_prompt += summary
                sys_prompt += "\n"
            sys_prompt += "</history>\n\n"
        messages.append({"role": "system", "content": sys_prompt})

        # 将聊天记录整合到待发送消息
        messages.extend(self.chat_history)

        # 将新query整合到待发送消息
        messages.append({"role": "user", "content": user_query})

        if self.debug:
            print("----------------------Messages to be Sent----------------------")
            for msg in messages:
                for key, value in msg.items():
                    print(f"[{key}]")
                    print(value)

            print(f"\ntokens sent: {count_token(str(messages))}")
            print("---------------------------------------------------------------")

        return messages

    def refresh_history(self):
        """
        刷新聊天记录，以确保聊天记录在token数量限制内

        如果超过，则对早期对话进行总结并存储在chat_summary中

        chat_summary也满了则抛弃最早的总结
        """
        while self.count_history_tokens() > self.max_history_tokens:
            if len(self.chat_history) <= 2:
                break

            # 提取早期聊天记录进行总结（每次总结一半）
            split = len(self.chat_history) // 2
            to_sum_messages = self.chat_history[:split]
            remain_messages = self.chat_history[split:]

            ask_sum_prompt = ASK_SUM_PROMPT
            for msg in to_sum_messages:
                line = msg["content"]
                if msg["role"] == "user":
                    ask_sum_prompt += line
                else:
                    ask_sum_prompt += f"{self.name}:{line}"
                ask_sum_prompt += "\n"
            summary = self.get_llm_ans(ask_sum_prompt)

            # 刷新聊天记录
            self.chat_summary.append(summary)
            self.chat_history = remain_messages

        while self.count_summary_tokens() > self.max_summary_tokens:
            self.chat_summary = self.chat_summary[1:]

    def count_history_tokens(self) -> int:
        """计算当前聊天记录的总token数"""
        return sum(count_token(str(msg)) for msg in self.chat_history)

    def count_summary_tokens(self) -> int:
        """计算当前聊天总结的总token数"""
        return sum(count_token(str(msg)) for msg in self.chat_summary)

    def get_llm_ans(
        self,
        query=None,
        role="user",
        messages=None,
        max_tokens=256,
        temperature=1.0,
        # frequency_penalty=0.0,
    ) -> str:
        """获取llm的回复

        Args:
            query (str): 发送的内容
            role (str, optional): user/system/assistant. Defaults to "user".
            messages (list, optional): 发送的消息列表. Defaults to None.
            max_tokens (int, optional): 生成文本的最大token数. Defaults to 256.
            temperature (float, optional): 生成内容的随机程度(0.0 to 2.0). Defaults to 1.0.
            frequency_penalty (float, optional): 对重复内容的惩罚(-2.0 to 2.0). Defaults to 0.0.

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
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return response.choices[0].message.content.strip()

    def _clear_history(self):
        self.chat_history.clear()
        self.chat_summary.clear()
        gc.collect()

    def _display_history(self):
        if not self.chat_history and not self.chat_summary:
            print("no chat history yet.")
        for dialogue in self.chat_history:
            line = dialogue["content"]
            if dialogue["role"] == "assistant":
                print(f"{self.name}:{self.speak_prefix}{line}{self.speak_suffix}")
            else:
                print(line)
