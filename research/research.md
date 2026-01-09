# HakureiPOI 

## 1. A Survey of Large Language Models in Finance (FinLLMs)

[A Survey of Large Language Models in Finance (FinLLMs)](https://arxiv.org/abs/2402.02315)

重点关注第六节 **Opportunities and Challenges**，从五个方面梳理了当前 FinLLMs 面临的问题与发展方向 

1. Datasets
    - 机会： **instruction fine-tuned financial datasets** （可能如果需要微调大模型的时候能够用上）
    - 挑战： collecting high-quality financial data in diverse format （毕设的重点不会落在这里）

2. Techniques
    - 机会： **Retrieval Agumented Generation (RAG)** （不关键？如果使用 coze 的话）
    - 挑战： 用户和机构的隐私保护，**确保模型输出符合金融合规要求（避免误导性建议）**，保护数据隐私（避免敏感金融信息暴露在训练过程中）
    
    毕设可以去追求的一个目标就是**确保模型输出符合金融合规要求**，剩下俩在毕设范围内应该接触不到

3. Evaluation 
    - 机会： **引入金融专家参与评估（学生评估）**，**采用金融专业指标（夏普率、回测收益等）**
    - 挑战： 当前评估过度依赖通用 NLP 指标，缺乏人机对齐机制，任务复杂度与评估成本不匹配

4. Implementation
    - 机会： （不关键）
    - 挑战： **成本与性能的权衡（是否指的训练专用 FinLLM，有时通用LLM + Prompting + RAG 更高效**），对低延迟高可靠性的要求，跨领域工程能力

    我的毕设某种意义上来说也就是一个 **通用LLM + Prompting + RAG**？

5. Applications
    - 机会： 智能投顾、量化、自动生成财报摘要、合同审查、低代码金融分析工具、生成式AI金融文档理解与创作 
    - 挑战： 行业壁垒高，专家-工程师鸿沟，伦理与问责、数据隐私与安全


**总结对毕设的思考：**

路线：通用 LLM（Coze）+ 结构化预测模型/信号 + XAI + RAG + 合规/忠实度约束生成 + 评估体系

关键在 解释忠实度（faithfulness）与证据可核验性（grounding/verifiability）：
解释必须与 XAI 归因方向一致，并能逐条追溯到 RAG 检索证据

## 2. Evaluation of Retrieval-Augmented Generation

[Evaluation of Retrieval-Augmented Generation](https://arxiv.org/pdf/2405.07437)

关键内容 **Auepora 三问**
- What to Evaluate?
- How to Evaluate?
- How to Measure?

（本篇内容在当前阶段不关键，预计在具体实现以及评估的时候可以借鉴一下评估方法）

## 3. 同花顺问财AI

属于很典型的 **Agentic RAG + 质量闭环** 路线，底层大模型为 HithinkGPT

个人使用体验：附加功能（如在回答时同时展示k线数据）等做的很好，特色是有着相当大的数据支撑，以及在增强回答的时候会结合收集到的财经网站上的相关文章

但是很明显的是同花顺的问财还是更偏向于搜索，快速检索到相关内容。在具体给出建议的时候往往因为 “模型冲突” 导致生成不完全，甚至出现接口调用失败未能正确获取数据的情况

## 4. 妙想金融大模型

和同花顺类似，在回答时会去集中检索信息然后通过训练过的比较专业化的语言表达出来。但根据妙想模型进行深度思考时的研究导图可以看出，所谓深度研究的操作只是将检索目标投向了更细节的信息如近期公告等。同时模型会检索其它量化模型是否对指定股票进行了预测（但是又往往检索不到）


总的来说，我觉得对于我的毕设，最大的创新点就是将量化和大模型结合，以量化的理性结果为主要 RAG 信息，以各项非结构化信息为辅助。区别于市场上 大模型 + 相关信息检索 RAG 的方式，提供更为理性全面的解读
