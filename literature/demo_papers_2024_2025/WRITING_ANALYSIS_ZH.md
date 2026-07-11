# ACL/EMNLP 2024–2025 相近 Demo Paper 写法分析

## 结论先行

这 10 篇中，对 PolyInterview 最值得精读的五篇是：

1. **LM-Interview**：与“规划—追问—分析”的完整面试流程最接近。
2. **MathBuddy**：与“理论指导的多模态感知—自适应交互—用户研究”最接近。
3. **AERA Chat**：与“分数必须能追溯到证据、并在界面中可核验”最接近。
4. **Metamo**：摘要、实时性、安全机制和 coaching 叙事写得最完整。
5. **iPET**：真实部署、在线 A/B 测试和长期用户证据最强。

共同的高胜率写法不是“把系统功能列全”，而是：

> 一个具体用户痛点 → 2–3 个现有系统缺口 → 与缺口一一对应的模块 → 用户看得见的工作流 → 多层证据 → 可访问的 demo/code/video。

PolyInterview 已经具备很好的素材：完整用户旅程、具身交互、可追踪评分、真实部署和诚实的失败审计。当前最需要改的是压缩摘要、合并章节、让实际证据与未来计划分开，以及减少技术栈式罗列。

## 十篇论文对照

| Paper | 与 PolyInterview 最接近的部分 | 正文组织 | 主要证据 | 最值得借鉴 | 不宜照搬 |
|---|---|---|---|---|---|
| LM-Interview | 预先规划、动态追问、访后分析 | Intro → 三阶段 Interview System → Experiments → Conclusion | 7 名学生；人类与系统访谈对照；专家评分；分析相关性 | 用真实任务流程直接定义系统模块 | 小样本却声称“媲美熟练访谈者”，证据偏弱 |
| EmpathyEar | 数字人、文本/语音/视觉输入与语音/头像输出 | Intro → Related Work → 8 步 Workflow → Implementation → Demo Scenarios → Evaluation | 自动指标 + 20 个查询的人评 | 把多模态 I/O 写得非常具体；先总流程再拆模块 | “pioneering/new standard”等措辞过满 |
| OpenOmni | 实时多模态对话、端到端工程约束 | Intro → Related Work → Requirements/Architecture → 两个 Demo Scenario → Conclusion | 不同配置的延迟、准确性和人工标注 | 把 latency–accuracy–cost–privacy 写成系统核心约束 | 引言和讨论较散，重复较多 |
| AutoGen Studio | 多智能体系统、可视化工作流、部署 | Intro → Design Goals → System/UI/API → Usage → Design Patterns | 20 万次安装、135+ GitHub issues | 从真实使用问题提炼设计原则，而不只报下载量 | 缺少任务效果评测，不能作为 PolyInterview 有效性的模板 |
| iPET | 个性化对话、记忆、长期真实部署 | Intro → 三模块系统 → Offline/Online Evaluation → User Statistics → Case Study | 200+ 天、百万用户、7 天 A/B；使用时长 +48.6% | 三个现实挑战精确对应三个模块；部署数字进入贡献 | 从个案推断心理改善的表述风险较高 |
| AgentMaster | 多智能体编排、分层架构、并行/动态路由 | Intro → General Framework → Case Study Architecture → Evaluation | 23 个查询；BERTScore、G-Eval、人评 | 区分“通用框架”和“具体实例”，架构层级清楚 | 21 页且重复多；指标与真实用户价值距离较远 |
| MathBuddy | 多模态行为感知、理论驱动适配、训练系统 | Motivation → Design & Implementation → Auto Eval/Ablation → 30 人 User Study | 八个教学维度、消融、30 人 within-subject study、实时识别准确率 | 把理论映射到系统决策；同时报告 60% 的真实识别准确率 | “massive gain”等宣传式语言不够克制 |
| AERA Chat | 可解释评分、证据高亮、界面可核验 | Intro → 两个 UI → Implementation → Model/Human/User Evaluation | 多数据集；专家 rationale 评测；16 人用户研究 | 让“explainability”成为具体交互：高亮、并排比较、修改与追问 | 评测内容较多，六页版需要更强取舍 |
| Metamo | coaching、追问、理论标签、头像、安全与实时性 | Intro → System Design → Benchmark/Prompt/Latency → Demo Scenario → 38 人评测 | 公共语料、人评、prompt sensitivity、成本/延迟、38 人 | 摘要用一段覆盖机制、延迟、安全、评测和适用性 | 心理学标签在实际部署中的有效性仍需专业验证 |
| LearnLens | 个性化、理论/课程 grounding、可操作反馈 | Intro → 双端 Interface/Architecture → User + Agent Evaluation → Conclusion | 30 名有教学经验者；100 个真实答案；延迟与成本 | 三个现有缺陷严格对应三个模块；结果写到部署优先级 | 摘要太短且无结果数字，系统价值主要靠正文补全 |

## 逐篇写法拆解

### 1. LM-Interview：最像 PolyInterview 的流程骨架

它没有按模型组件起章节，而是按真实访谈的三个阶段组织：访前 guide construction、访中 dialogue、访后 analysis。这个组织方式使系统设计天然成为用户任务，而不是一张后台模块清单。Introduction 先解释半结构访谈为何难，再列出三个系统挑战：访谈者控制、动作灵活性、访后分析；后文三个模块逐一回答。

对 PolyInterview 的直接启发是把叙事稳定在：**Setup/Planning → Live Adaptive Interview → Multimodal Evaluation → Actionable Report**。当前论文已经这样写了一部分，但 “System Overview / Adaptive Multi-Agent Questioning / Explainable Multimodal Scoring” 被拆成三个主章节，读者需要自己重新拼回一次完整体验。可以考虑把后二者变成 System Design 下的两个技术小节。

### 2. EmpathyEar：多模态系统要把输入、推理和输出画清楚

它的首张架构图把系统分成 Encoding → Reasoning → Generating，并在图上明确 text/speech/vision 输入与 text/speech/talking-face 输出。随后用八个编号步骤走完一轮交互，再展开技术实现。写法的优点是读者先知道“用户发什么、系统回什么”，之后才看模型。

PolyInterview 的架构图也应优先表达一轮 interview turn：candidate text/audio/video → response check/follow-up → four evaluators → feature/aspect/track → UI evidence。模型名和服务名应后置。

### 3. OpenOmni：把真实工程约束写成贡献，而不是附录杂项

它用 latency、accuracy、cost、privacy 四个现实约束定义问题，并在 demo scenario 中报告不同配置的端到端延迟。即使结果并不漂亮，工程瓶颈仍然构成论文信息量。

这与 PolyInterview 的真实部署失败审计高度相容。31.8% 的视频评估 silent failure 不应只是“系统有 bug”，而应写成：真实 webcam 条件下的可观测可靠性指标、失败分类、对均值的影响，以及 retry/fallback/capture QA 的修复路径。不过不能把它包装成系统有效性；它支持的是 **traceability 和部署审计价值**。

### 4. AutoGen Studio：从产品使用反馈提炼设计原则

它没有仅写“20 万下载”，而是分析 135+ GitHub issues，从用户痛点归纳出 define-and-compose、debugging/sensemaking、export/deployment、collaboration/sharing 四类设计原则。这让 usage data 变成研究洞察。

PolyInterview 的 120 个清洗后 session 也应如此：不只报用户数，而是把 log 变成系统性结论。当前关于视频失败、模态非冗余的分析已经走在正确方向。若篇幅允许，可再加一个清晰的 failure taxonomy，而不是更多平均分。

### 5. iPET：部署型 demo 的证据模板

iPET 的引言提出三个现实挑战：长期个性化、角色持续演化、大规模部署；随后正好给出 Dialogue、Memory、World Simulation 三个模块。评测分为 offline、online A/B、user statistics、case study 四层，最后把“200+ 天、百万用户、时长 +48.6%”放进贡献和摘要。

对 PolyInterview 而言，最值得学的是**贡献中直接出现部署证据**。但我们的 pilot 是 self-report，日志中又有大量短/未完成 session，因此只能写成 “deployed and audited”，不能写成 “validated effectiveness”。

### 6. AgentMaster：通用框架与具体案例分开写

它先给 general system framework，再用一个 multimodal retrieval case study 说明落地。这样避免把“架构可以做什么”与“当前实例确实做了什么”混为一谈。

PolyInterview 可借鉴这种边界感：四类 feature agents 的架构能力是一层；当前部署中真正稳定产生的 text/audio/video 结果是另一层。尤其视频模块必须明确区分 expected pipeline 与 observed reliability。

### 7. MathBuddy：最值得模仿的整体证据链

MathBuddy 与 PolyInterview 的结构相似度最高：文本 + webcam 感知用户状态，把多模态信号映射到理论支持的教学策略，再生成自适应响应。它同时做自动评测、消融、30 人 within-subject 用户研究，并在正文承认实时多模态情绪聚合准确率只有 60%。

最好的写法是“理论不是背景引用，而是控制系统行为”：情绪类别决定 challenge 或 motivate。PolyInterview 也需要把 KSA/STAR 写成可观察的决策链：哪一种 question type 激活哪些 aspect、哪一个缺失的 STAR 元素产生哪一种反馈，而不是只说“grounded in KSA×STAR”。

### 8. AERA Chat：可解释性必须在 UI 中可操作

AERA Chat 没把 explainability 停留在 rationale 输出。它提供关键元素高亮、正负证据区分、多模型并排、label correction、rationale preference、人工编辑和追问。评测也区分 scoring performance、rationale correctness/preference、platform usability。

PolyInterview 当前最强的 UI 叙事正是逐级 drill-down。建议用一个具体例子贯穿全文：某个回答 → 某个 feature evidence → 某个 aspect → report 中的 tip。这样 “traceable” 是读者亲眼看到的操作，而不是形容词。

### 9. Metamo：摘要和实时 coaching 叙事的最佳样本

Metamo 的摘要包含：使用场景、核心机制、单次调用、低于两秒、头像/标签、安全层、公共数据评测、用户研究和 model-agnostic 意义。信息密度高但仍围绕一个中心句：cognition-aware real-time coaching。

PolyInterview 可模仿它的“机制 + 约束 + 证据”三件套，但不要照搬其长度。PolyInterview 当前摘要约 289 词，而这 10 篇摘要的中位数约 149 词；建议压至 170–200 词。

### 10. LearnLens：缺口与模块一一对应的最干净范例

它把现有系统的三个问题写成：(i) 只打分、不理解部分推理；(ii) 反馈缺少课程 grounding；(iii) 教师无法控制或修正。下一段马上对应 Error-aware Assessor、Curriculum-grounded Generator、Educator-in-the-loop Interface。

PolyInterview 当前引言提出 personalization、interaction、assessment 三个 gap，但贡献列成四项，后文又分更多模块。可以重排为三条主线：**personalized/adaptive interviewing、multimodal traceable feedback、deployed evidence**；数字人和 multi-agent 是实现这些主线的机制，不必各自抢一条主贡献。

## 跨论文的稳定写法

### 1. 摘要通常是五拍，而不是功能清单

高频结构是：

1. 一个现实任务为什么重要/昂贵；
2. 现有系统缺少什么；
3. “We present X” + 一句话定位；
4. 2–3 个核心模块或关键机制；
5. 最强证据数字 + demo/code/video。

PolyInterview 当前摘要同时讲市场痛点、四类缺口、六屏旅程、所有 agent、13→10→2、两轮 pilot、screencast、120 sessions 和 31.8% failure，信息过载。六屏和 screencast 属于正文/demo requirements，不应占摘要核心空间。

### 2. 第一张大图承担“十秒理解”

这批论文常在第一页或第二页放 UI 或端到端 architecture。最有效的图不是组件最多的图，而是让读者回答：用户输入什么、系统做什么、用户得到什么。PolyInterview 应保留 Setup → Live → Report 的 hero journey，并让 Match/Convince 或 adaptive/traceable 两条创新轴直接标在图上。

### 3. 系统章节围绕用户可见行为

强 demo paper 会把界面动作与后台机制绑定：用户上传什么、点击什么、系统在哪一步调用哪个模块、结果如何显示。单独罗列 Vue/Flask/Qwen/ports/SDK 的信息收益很低。可复现性所需的技术栈留一小段，版本和服务细节移到附录或仓库。

### 4. 评测普遍采用至少两类证据

常见组合包括：

- 组件/任务指标：准确率、相关性、延迟、成本；
- 人工评测：专家判断 rationale、回答或访谈质量；
- 用户研究：可用性、满意度、学习/行为变化；
- 真实部署：在线 A/B、使用时长、日志、失败率。

PolyInterview 有部署日志和 self-report pilot，但尚无专家一致性或学习增益，因此写法应明确：**系统已部署、使用体验被初步接受、评分有效性尚未建立**。

### 5. 诚实的失败结果会增加可信度，但必须界定它证明什么

MathBuddy 报告实时情绪识别只有 60%；OpenOmni 报告数十秒延迟；AgentMaster 报告误分类；这些没有毁掉 demo paper，反而说明系统真的运行过。PolyInterview 的 silent failure 是有价值的实证材料，但它证明“分层可观测性发现了问题”，不证明视频评分有效。

### 6. 限制写具体机制，不写泛泛 future work

好的 limitations 会说明：哪种输入失败、原因是什么、影响哪项 claim、下一步如何测。PolyInterview 可按 reliability、criterion validity、learning gain 三层写，但“计划做的评测”更适合放 Limitations/Future Work，不宜成为 Evaluation 主体。

## 对当前 PolyInterview 稿件的具体建议

### 已经写对的部分

- 以 running system 和完整 user journey 为中心，而非只讲模型。
- “At the demo” 明确说明现场如何演示，这是 demo track 喜欢看到的内容。
- 把 traceability 落到 report drill-down，而不只是方法口号。
- 清洗测试账户并主动报告真实视频失败，可信度明显高于只报漂亮均值。
- Related Work 已经围绕 adaptive / multimodal / explainable 形成清晰定位。

### 优先修改项

1. **摘要从约 289 词压到 170–200 词。** 删除六屏、screencast 格式和过细 agent 列表；保留一句机制、两句差异、一个部署数字、一个可靠性发现。
2. **让三条 gap 对应三条贡献。** 推荐：adaptive embodied interview；KSA×STAR-grounded multimodal traceable feedback；real deployment and reliability audit。
3. **合并系统章节。** 可用 `System Walkthrough and Design`，下设 User Journey、Adaptive Interviewing、Traceable Multimodal Feedback、Implementation。减少主章节切换。
4. **把实际评测集中在一个章节。** Deployment corpus、video failure audit、modality analysis、pilot feedback 放在一起；Planned validation 移到 Limitations/Future Work。
5. **减少技术栈密度。** 正文保留实时链路、四个 evaluator、并行执行、数字人和关键部署约束；Vue 版本、端口、JWT 天数等放附录/仓库。
6. **用一个回答贯穿 traceability。** 从原始回答和三模态记录，一路追到 feature、aspect、two tracks、最终 tip；这会比再加一个抽象表更有说服力。
7. **收紧 claim。** 在没有专家一致性和 learning-gain 实验前，用 “deployed”, “audited”, “self-reported” 和 “operational” 而不用 “validated”, “effective” 或笼统的 “first”。
8. **补清 pilot 方法。** 若现有材料允许，写清两轮各自 N、招募方式、问题、量表、缺失数据与原始计数；129 这个大 N 只有在 protocol 清楚时才有力量。

## 推荐的六页正文骨架

| Section | 建议篇幅 | 内容 |
|---|---:|---|
| Abstract | 170–200 words | problem → gap → system → mechanism → evidence |
| 1 Introduction | 0.75 page | 三个 gap、三条贡献、结果 preview |
| 2 Related Work | 0.5 page | interview systems、multimodal assessment、explainable coaching；保留精简对比表 |
| 3 System Walkthrough and Design | 2.0 pages | hero journey；adaptive interview；13→10→2 traceability；一个 running example |
| 4 Implementation and Deployment | 0.5 page | 实时链路、并行性、demo setup、privacy/reliability boundaries |
| 5 Evaluation and Deployment Audit | 1.5–1.75 pages | clean corpus、video failure、模态分析、pilot protocol/results |
| 6 Conclusion | 0.2–0.25 page | 一句系统、一句证据、一句边界 |

Limitations 与 Ethics 单列，明确评分是 student-facing advisory tool，不用于招聘 gatekeeping。

## 可直接套用的摘要骨架

> Mock interviews rarely provide adaptive probing or actionable feedback on how candidates speak and present themselves. We present **PolyInterview**, a deployed multi-agent system for embodied interview practice that combines answer-aware follow-up questioning with traceable feedback over text, audio, and video. A planner personalizes the interview from a CV and job description; an interviewer agent probes unclear or inconsistent answers; and four parallel evaluators map 13 behavioral features to 10 KSA×STAR-grounded aspects and two proficiency tracks, each exposed in the report with supporting evidence. PolyInterview is publicly deployed and has been piloted across six institutions. An audit of 120 cleaned deployment sessions shows both the value and current limits of this design: the feature-level pipeline reveals that the non-verbal evaluator silently failed on 31.8% of video-relevant answers, motivating explicit capture checks and fallback evaluation. The system, live demo, and screencast support an end-to-end demonstration from setup to actionable feedback.

这只是结构示例；最终版本还应根据 EMNLP 2026 的匿名性、链接和字数要求微调。
