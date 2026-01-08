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

> 总结对毕设的思考：
> - 路线：通用 LLM（Coze）+ 结构化预测模型/信号 + XAI + RAG + 合规/忠实度约束生成 + 评估体系，关键在 XAI 和 忠实度上




