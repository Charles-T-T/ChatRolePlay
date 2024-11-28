# 基于LLM的角色扮演聊天模型

> 参考项目：[LC1332/Chat-Haruhi-Suzumiya: Chat凉宫春日, An open sourced Role-Playing chatbot](https://github.com/LC1332/Chat-Haruhi-Suzumiya)

## Baseline

直接提供prompt，调用LLM的api实现

## ChatHaruhi

- 1.0版本可以直接 `pip install` / `conda install` ，但是聊天记录维护不佳
- 2.0版本似乎没有完全开发完毕，但是可以本地部署

## Our work

- pipeline优化
- 模型微调

## TODOs

- [ ] 抽取方法优化
- [ ] 提取故事背景方法优化
- [ ] 整合消息方法优化（更精简）
- [ ] 整体代码优化（统一各模型api接口调用）
- [ ] prompt优化（基于wiki自动生成？）
- [ ] 更客观的评估方式（找找现有通用的benchmark）
- [ ] ...