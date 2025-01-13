# ChatRolePlay


> [!NOTE]
>
> :open_book: 本项目为 `多媒体技术 (Fall 2024, RUC)` 大作业
>
> :link: 参考项目 [ChatHaruhi](https://github.com/LC1332/Chat-Haruhi-Suzumiya) 
>

---

## Introduction

:dolls: **ChatRolePlay** 是一套从本地文本数据（小说等）构建自定义角色聊天Agent（chatbot）的轻量级解决方案。 :performing_arts: ​

## Requirements

- Python 3.10 or later
- Conda
- OpenAI's API_KEY

## Usage

### 准备工作

1. 将项目 `clone` 到本地

   ```bash
   git clone https://github.com/Charles-T-T/ChatRolePlay.git
   ```

2.  创建并激活环境

   ```bash
   conda env create -f environment.yml
   conda activate ChatRolePlay
   ```

3. 将你的 `api_key` 配置到系统环境，或者直接添加到 `config.py` 中：

   ```python
   # ChatRolePlay/config.py
   api_keys = {
       "openai": os.getenv("OPENAI_API_KEY", "your_api_key"),
       "doubao": os.getenv("ARK_API_KEY", "your_api_key"),
   }
   ```
   
   > 目前只添加了OpenAI和豆包的api，后续可以在 `config.py` 中继续添加

### 角色数据抽取

这部分主要在 `NovelToRole/TMLH_get.ipynb` （后称 `notebook` ）中进行。

1. 准备好你要抽取的小说或其他文本数据

   > 需要 `.txt` 格式， `.epub` 格式也可以转为 `.txt` ，方法详见 `notebook` 

2. 在 `notebook` 中的第一个代码单元中添加你的文本数据路径，和要抽取的角色姓名：

3. 运行整个 `notebook` 即可，完成后会显示：

   ```bash
   Zipped folder saved to ./role/黛玉_text.zip
   Zipped folder saved to ./role/宝玉_text.zip
   Zipped folder saved to ./role/宝钗_text.zip
   ```

   `NovelToRole/role` 下也有未压缩的原文件夹，可以直接在下一步“构建Agent”使用。

### 构建Agent

1. 导入 `ChatRolePlay` 

   ```python
   from ChatRolePlay import ChatRolePlay
   ```

2. 构建Agent并传入抽取的数据路径、角色姓名等参数

   ```python
   daiyu = ChatRolePlay(
       llm="openai",
       name="林黛玉",
       book_name="红楼梦",
       data_folder_path="data/黛玉",
   )
   ```

   > `llm` , `name` , `data_folder_path` 是必需参数，其他更多定制化参数请查看 `ChatRolePlay.py` 源码。

3. 用 `chat` 方法就可以开始和你的角色聊天啦 :speech_balloon: ​

   ```python
   daiyu.chat(user_role="宝玉", query="妹妹，谁又惹着你了？")
   >>> '林黛玉:「谁生什么气。」'
   daiyu.chat(user_role="宝玉", query="我看你就是在生气。")
   >>> '林黛玉:「我有我的缘故，你那里知道。」'
   daiyu.chat(user_role="宝玉", query="是不是宝姑娘送的东西少了？")
   >>> '林黛玉:「我任凭怎么没见世面，也到不了这步田地，因送的东西少，就生气伤心。我又不是两三岁的小孩子，你也忒把人看得小气了。」'
   daiyu.chat(user_role="宝玉", query="好罢，别再气了，我们去园子里走走如何？")
   >>> '林黛玉:「你要去就去罢，我才懒得理你呢。」'
   ```
   
> [!TIP]
>
> 本项目实现了简单的RAG，以尽可能让角色在遇到和原文相同或相似的场景/对话时，忠于原文展开聊天。例如，上面对话中 `林黛玉` 的语言可以在《红楼梦》第六十七回找到“出处”：
>
> ```tex
> 只见宝玉进房来了，黛玉让坐毕，宝玉见黛玉泪痕满面，便问：“妹妹，又是谁气着你了？”黛玉勉强笑道：“谁生什么气。”旁边紫鹃将嘴向床后桌上一努，宝玉会意，往那里一瞧，见堆着许多东西，就知道是宝钗送来的，便取笑说道：“那里这些东西，不是妹妹要开杂货铺啊？”黛玉也不答言。紫鹃笑着道：“二爷还提东西呢。因宝姑娘送了些东西来，姑娘一看就伤起心来了。我正在这里劝解，恰好二爷来的很巧，替我们劝劝。”宝玉明知黛玉是这个缘故，却也不敢提头儿，只得笑说道：“你们姑娘的缘故想来不为别的，必是宝姑娘送来的东西少，所以生气伤心。妹妹，你放心，等我明年叫人往江南去，与你多多的带两船来，省得你淌眼抹泪的。”黛玉听了这些话，也知宝玉是为自己开心，也不好推，也不好任，因说道：“我任凭怎么没见世面，也到不了这步田地，因送的东西少，就生气伤心。我又不是两三岁的小孩子，你也忒把人看得小气了。我有我的缘故，你那里知道。”说着，眼泪又流下来了。
> ```

## Demo

详见 [ChatRolePlay/demo](https://github.com/Charles-T-T/ChatRolePlay/tree/main/demo) 。

