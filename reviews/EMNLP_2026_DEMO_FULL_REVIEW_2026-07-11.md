# PolyInterview：EMNLP 2026 Demo Paper 全面审稿报告

> 审查对象：`paper/main.tex` 与 2026-07-11 14:04 生成的 `paper/main.pdf`  
> 审查日期：2026-07-11（Asia/Hong_Kong）  
> 审查口径：EMNLP 2026 System Demonstrations 官方征稿要求、ACL 官方格式要求，以及论文、图表、分析产物、项目说明和公开演示入口之间的交叉核验  
> 总结论：**当前版本不应直接投稿。按现状提交，至少存在 1 个明确的 desk-reject 风险、1 个必须在投稿前纠正的研究诚信问题，以及多组会显著削弱可信度的图文、数据、理论和伦理不一致。建议按 Major Revision 处理。**

## 1. 一页结论

论文的核心产品故事是清楚且有潜力的：一个把 JD/CV 条件化提问、回答感知追问、数字人交互和多模态形成性反馈整合起来的面试练习系统。系统规模、界面完成度和端到端工作流也足以形成一篇 Demo paper 的基础。真正的问题不在于“产品有没有做出来”，而在于当前稿件把若干**尚未被当前证据支持的强主张**写成了既成事实，并且内部材料与正文之间存在直接冲突。

最严重的六项问题如下：

1. **第 5 节“十名人类专家”与分析产物直接矛盾。**正文声称十名 human experts；但 `analysis/llm_agent_panel/summary.json` 明确记录 `human_experts: 0`、`llm_agents: 10`，README 还明确写着该研究“not a human-expert study and must not be reported as one”。表 3 的所有数字与这组 LLM-agent pilot 完全一致。这不是普通措辞问题，必须在投稿前纠正。
2. **公开 Demo/视频/代码入口目前为空链接。**论文脚注指向的 landing page 中 Paper、GitHub、Online Demo、Video 均为 `#`，teaser 为空，摘要还是占位文本。EMNLP 2026 Demo Call 将可访问的 live demo 或 installable package 列为严格要求，缺少链接可直接 desk reject。项目内确有一段 116.45 秒、1280×656、H.264/AAC 的 `Demo.mp4`，时长和格式合格，但没有被公开入口实际链接。
3. **“13→10→2”评估本体在正文、图 4、附录表 4 和 UI 中四种不同。**图 4 实际列出 11 个 aspect，额外包含 Big-Five Personality；正文说 10 个且“不推断人格”；附录表 4 只映射了 12/13 个底层特征（Fluency 未使用）；UI 雷达图只显示 9 个维度（缺 Persuasiveness）。这是核心贡献自身不自洽。
4. **“全面多模态评估已在部署中运行”的证据被显著夸大。**正文把 1,425 条 score record 说成覆盖 text/audio/video；实际可用音频特征约 357/1,425（25.1%），VLM 成功约 378/1,425（26.5%），另有 879 条无视频、168 条 VLM 失败。1,425 个 pooled scored answers 还大于 1,274 个 answered question records，单位没有解释。
5. **Ethics Statement 与项目说明中的安全实现相冲突。**正文写“encrypted storage、strict access controls、per-user isolation、metadata only”；现有项目说明却记录 unrestricted CORS、部分 Flask 路由无认证、内部 HTTPS `verify=False`、SQLite 和音视频明文存储、缺少自动删除生命周期。项目说明可能已过期，但在提交前必须用当前部署证据逐项验证；不能在无法证明时保留绝对表述。
6. **摘要—Introduction—贡献—正文—Conclusion 的证据链没有闭合。**第 5 节质量评估既未进入摘要和贡献列表，也未进入结论；结论避开了该评估最弱的三项结果。CV-specific、immersive、comprehensive、traceable 等核心词的实证支持也不足。

若只允许一句编辑决定：**Reject as-is / Major Revision before submission。**如果把第 5 节立即如实改为“Profiled LLM-Agent Protocol Pilot”、修好公开入口、收缩无法证实的主张，并解决 13→10→2 与覆盖率问题，稿件才进入“可继续打磨并考虑投稿”的状态；若要保留“human expert evaluation”和更强的 assessment-quality 主张，则必须补做真实、可追溯的人类评审。

## 2. 审查范围、证据与严重度

本报告不是只做语言润色，而是执行了六层交叉检查：

- 对 `main.tex` 与最终 PDF 逐节、逐图、逐表检查；
- 对 PDF 页数、纸张、字体嵌入、引用解析、LaTeX 警告和元数据检查；
- 对 `analysis/corpus_stats_all.json`、角色匹配分析、LLM-agent panel 及其生成脚本复算；
- 对论文中的图形源文件和 UI 截图进行视觉核对；
- 对项目说明中的部署、安全与数据处理描述和 Ethics Statement 比对；
- 对 EMNLP 2026 Demo Call、ACL 格式规则、商业产品当前功能和关键参考文献进行外部核验。

严重度定义：

| 等级 | 含义 | 投稿前要求 |
|---|---|---|
| **P0 / Blocker** | 可导致 desk reject、研究诚信质疑、核心结论失效或伦理风险 | 必须修复并重新审计 |
| **P1 / Major** | 不一定直接拒稿，但会显著降低正确性、可信度、novelty 或可复现性 | 强烈建议投稿前完成 |
| **P2 / Minor** | 清晰度、术语、版式、元数据、文献细节等 | 最终提交前清零 |

## 3. EMNLP Demo 硬门槛审计

依据 [EMNLP 2026 System Demonstrations Call](https://2026.emnlp.org/calls/demos/) 与 [ACL 官方格式说明](https://acl-org.github.io/ACLPUB/formatting.html)：

| 检查项 | 当前状态 | 结论与证据 |
|---|---|---|
| 正文最多 6 页 | 通过 | Conclusion 结束于第 6 页。 |
| 附录最多 2 页 | 通过 | 附录为第 9–10 页；第 7–8 页是 Limitations/Ethics/References。 |
| A4、双栏、字体嵌入 | 通过 | PDF 为 595.276×841.89 pt；字体均嵌入。 |
| 作者与单位可见（single-blind） | 通过 | 首页含完整作者和单位。 |
| 系统必须有 evaluation | 表面通过、实质有阻断项 | 有 usage、lexical diagnostic 和第 5 节，但第 5 节 provenance 错误，multimodal coverage 也被夸大。 |
| Demo video ≤2.5 分钟 | 时长/编码通过，内容与提交条件未通过 | `paper_sources/Demo.mp4` 为 116.45 秒、H.264/AAC；但 landing page 的 Video 链接为空。视频主体长期停留在 live-answer/20% progress，未完整展示 setup→interview→report，且未检测到字幕轨。 |
| live demo 或 installable package | **不通过，P0** | 论文脚注 landing page 的 Online Demo/GitHub 均指向 `#`。官方明确说明无链接可 desk reject。 |
| 软件许可信息 | **不通过，P1** | 正文、附录和 landing page 都没有 license。官方 call 明确要求说明 license。 |
| Limitations 的位置 | 内容存在，排版有风险 | `\clearpage` 强制 Limitations 从新页开始；ACL 规则要求其紧随 Conclusion 且不人为分页。 |
| review/final 样式 | 需向 chairs 确认 | 当前为 `\usepackage[final]{acl}`，没有 review ruler/page numbers。Demo 为 single-blind，但这不自动等于 final camera-ready 样式；应按提交系统模板或向 chairs 确认。 |
| Abstract ≤200 words、纯文本 | 边缘通过但应修 | 可见正文约 185 words；若将脚注/链接计入，工具计数约 204。摘要中还有粗体、脚注和 hyperlink，不符合纯文本元数据的稳妥写法。 |
| 参考文献/引用解析 | 基本通过 | 无 undefined citation/reference；但 DOI、产品来源与若干引用语义需要修。 |

此外，当前 PDF 的 Title、Author、Subject、Keywords 元数据均为空，PDF 未 tagged；这通常不是 desk-reject 项，但属于应在最终包中补齐的专业性问题。

## 4. P0：必须先处理的阻断问题

### 4.1 第 5 节把 LLM-agent pilot 写成了十名人类专家

正文第 5 节（PDF p.6；`main.tex` 220–227）声称：

- 邀请了 ten human experts；
- 背景包括 HR、language assessment、communication；
- 12 个去标识化 artifact、120 次 artifact review、360 个 criterion rating；
- 表 3 报告 “Expert SD” 和 ±1 agreement。

但本地证据是：

| 项目 | 论文写法 | 分析产物实际记录 |
|---|---|---|
| 参与者 | 10 human experts | 10 profiled LLM agents；human experts = 0 |
| 研究类型 | Human Expert Evaluation | `profiled_llm_agent_protocol_pilot` |
| 结论边界 | assessment quality 的人类证据 | README 明确禁止报告为 human-expert study |
| 表中 SD | Expert SD | 10 个 agent module mean 的 SD；不是 rating-level SD |
| `n=4` | 读者容易理解为样本/专家数 | 每个 module 的 artifact 数 |
| ±1 agree | 未定义 | 所有 agent-pair 评分差≤1的比例；不是 ICC/Krippendorff's α |

表 3 的 4.62、3.68、3.74，0.15、0.18、0.37，以及 100.0%、98.9%、91.3% 与 `summary.json` 完全吻合。原始 agent pilot 的 rating-level SD 实际约为 0.55、0.99、1.06；按现有评分还可算出 exact pair agreement 约 76.1%、60.4%、49.6%，ICC(2,1) 约 0.627、0.797、0.684，但这些仍然只是模拟评审的一致性，不能变成人类证据。

还存在采样偏差：生成 packet 的脚本倾向挑选完成度/长度/丰富度高的 artifact，follow-up 与 feedback 还限定于 synthetic/test accounts；这不是随机或代表性抽样，也不包含真实音频、视频或 outcome validity。

**必须二选一：**

1. 快速诚实方案：将第 5 节改名为 **Profiled LLM-Agent Protocol Pilot**，把“human experts”全部改成“profiled LLM agents”，把 `Expert SD` 改成 `Agent SD`，明示 artifact 的 purposive selection、prompt/model/configuration 和结论边界；摘要/贡献/结论只把它写成“用于预检人工评审协议的 pilot”，不得称作 assessment-quality validation。
2. 科学上更强的方案：重新做真实 human study，保存招募、资历、同意/IRB、随机化抽样、盲评协议、评分 rubric、原始匿名 ratings，报告 ICC 或 Krippendorff's α 与置信区间，并让真实专家接触论文所声称的模态证据。只有这样才能保留现有章节标题和人类验证主张。

在这项问题澄清前，不应继续对该节做“语言润色”，因为那会把错误 provenance 包装得更像事实。

### 4.2 Demo 入口不满足 strict requirement

摘要脚注指向 `https://dannywang1922.github.io/polyinterview`。截至审查日，页面状态如下：

- Paper、GitHub、Online Demo、Video 四个按钮均为 `#`；
- teaser image 的 `src` 为空；
- 示例内容与摘要为占位文本；
- 占位摘要出现“beats strong LLM baselines”等论文没有报告的主张；
- 页面标题/内容与当前论文标题和系统叙述不完全一致。

本地 `paper_sources/Demo.mp4` 的时长和编码合格，说明素材并非不存在；问题是**审稿人无法通过论文给出的入口获得它**。同时，论文一方面写 “publicly accessible”，另一方面第 4 节写 “runs on the university network”；PolyU 官方新闻也将其描述为校内试用并涉及 PolyUWLAN/预约容量，而不是无条件公网访问。

投稿前验收标准：

- 匿名/公开浏览器中点击论文唯一 URL，可实际打开视频、在线系统或安装包；
- 若系统需登录、校园网或预约，明确写出限制并提供 reviewer guest account、sample mode 或可安装 fallback；
- 视频、PDF report、sample CV/JD 和关键交互路径无需作者手工介入即可访问；
- 所有按钮返回真实 200/可下载资源，禁止 `#`；
- 页面删除未经论文支持的 baseline 优越性主张；
- README 写明 license、依赖、最低硬件/浏览器、模型/API 前提和数据处理告知。

### 4.3 Ethics/Security 的可证实性不足

Ethics Statement（PDF p.7）使用了多项绝对表述：encrypted storage、strict access controls、per-user isolation、raw data not retained for secondary use、provider no-training、all research use IRB-approved、analysis uses metadata only。

当前工作区中的项目说明（2026-03-13 版本）却记录：

- Flask `CORS(app)` 无来源限制；
- 若干业务 API 未见认证保护；
- 内部服务使用自签名证书并出现 `verify=False`；
- SQLite、音频、视频和评估结果为明文存储；
- 缺少自动 retention/deletion lifecycle；
- 登录失败次数限制等控制缺失。

此外，论文的角色对齐分析实际处理 JD 文本与生成问题；LLM-agent packet 中也包含 JD/回答片段，所以 “metadata only” 至少在通常含义下不成立。项目说明可能没有反映最新部署，因此本报告不据此断言线上系统当前必然不安全；但**现有证据不足以支持论文的确定性合规表述**。

投稿前需要一份逐项 evidence checklist：当前代码路径、认证中间件、CORS allowlist、TLS/证书验证、at-rest encryption、密钥管理、访问日志、删除测试、retention schedule、第三方 DPA/no-training 条款、IRB 编号/豁免范围、GDPR/PDPO 法律依据。无法出示证据的句子应改为可验证、范围明确的描述，而不是保留保证式语言。

公平、无障碍和项目级告知也没有闭合。当前材料没有 documented keyboard/screen-reader path、live captions、text-response mode、camera-off alternative，也没有按口音、语言、性别、肤色/光照、设备、残障或神经多样性报告 ASR/VLM failure。通用大学隐私政策不能替代本服务在上传 CV、开启麦克风和摄像头前展示的项目级 Personal Information Collection Statement：应列出具体用途、处理方、传输地域、保留期、删除 SLA、研究 opt-in 和投诉渠道。视频与 PDF 也应补字幕/标签等基本可访问性。

### 4.4 核心评估本体自相矛盾

论文反复把“13 behavior-level features → 10 aspects → 2 tracks”作为最核心的 technical contribution，但目前至少有四套版本：

| 位置 | 实际内容 | 冲突 |
|---|---|---|
| 正文 §2.3 | 13 → 10 → 2；Big Five 只“informs”，不推断人格 | 目标叙述 |
| 图 4 | 列出 11 个中层节点，含 **Big-Five Personality** | 与 10 aspects 和“不报告人格”直接冲突 |
| 附录表 4 | 10 aspects，但只使用 12 个底层特征 | Fluency 未进入任何 aspect；“13→10”不可重建 |
| UI Figure 3(e) | 雷达图只有 9 轴 | 缺 Persuasiveness |

图 4 还把语音模型写成 `Audio-LLM`，正文则写 Azure Speech / speech-based evaluator。图中 “Big-five”“STAR Methods” 与正文 “Big Five”“STAR structure/framework” 也不一致。

验收标准很简单：建立一份机器可读的 canonical ontology；正文、所有图、附录表、UI 标签和实际评分代码都由同一份配置生成；逐项列出 13 个 feature 是否参与映射、缺失模态如何处理、primary group 内如何平均、70/30 如何应用、question-level 如何聚合为 track/session score。未使用的 Fluency 要么进入映射，要么从“13”中移除并解释。

### 4.5 数据口径与模态覆盖不能支持当前强结论

按 `corpus_stats_all.json` 复算，表面数字大多算术正确，但论文将“有文件/有记录”写成了“成功完成多模态分析”：

| 指标 | 原始/复算值 | 当前稿件的问题 |
|---|---:|---|
| Accounts | 101 | 含 test/internal/seed/placeholder/team，摘要仍突出显示，容易被理解为真实用户。 |
| Returning accounts | 62/101 = 61.4% | 图 5 称 “returning-account evidence”，但账户集合含测试类账号，不能当 retention/adoption。 |
| Sessions | 1,564 | 其中 completed 仅 217（13.9%）；1,162 in progress，185 disconnected。 |
| Five-stage sets | 1,422/1,564 = 90.9% | 这是“生成问题类别齐全”，不是 90.9% 完成五阶段访谈。 |
| Generated questions | 7,665 | Answered records 仅 1,274（约 16.6%）。 |
| Follow-up coverage | 208/1,274 = 16.3% answered records | 只证明追问路径被触发，不证明适配质量。 |
| Follow-up turns | 342 | 对有追问的记录平均约 1.64 turns。 |
| Pooled scored answers | 1,425 | 大于 1,274 answered records；另一特征表只把 743/1,425 标为 answered subset，单位需对账。 |
| 有效 audio features | 357/1,425 = 25.1% | 不能把全部 1,425 条写成 vocal assessment。 |
| VLM success | 378/1,425 = 26.5% | 879 无视频，168 VLM 失败；不能把全部写成 non-verbal assessment。 |

进一步核对生成逻辑后，`pooled_scored_answers=1,425` 实际只是 `evaluation.records`：脚本只要求任一 feature 存在，并未要求回答非空。`eval_per_category.csv` 把其中仅 743 条标为 answered，另外 682 条为 unanswered；从分组均值关系看，未回答记录基本以 0 进入 pooled mean。因此 `score.mean=2.5051` 不能解释为已回答样本的平均质量；answered 条件均值约为 4.805，二者回答的是不同问题。§4 “1,425 per-question score records over textual, vocal, and non-verbal behavior” 以及 “show that ... multimodal assessment operate[s] ... at scale” 需要改成分模态 denominator 和成功/失败率。录音文件数量也不能替代实际可分析 coverage。

“clean cohort” 也不是稳定定义：panel packet 脚本把账号 5868 明确列为 synthetic user，但 clean-corpus 排除表没有排除它。该账号占 clean set 的 11/78 sessions、44/265 questions、10/115 answered records；若按 synthetic 定义排除，clean totals 会变成 43 users、67 sessions、221 questions、105 answered。投稿前必须用一份唯一的 cohort manifest 生成所有 clean/all-account 统计。

角色对齐结果 93.7%/82.4% 算术上可复现，但当前 baseline 太容易：它只拿 matched JD 与**不同职位** JD 比较，无法支持“goes beyond inserting a position name”。同职位、不同 JD 的更严格敏感性诊断显示：在可比较的 262 个 session 中，matched similarity 高于 same-position different-JD median 的比例约 76.7%，rank-first 约 34.7%。这不是论文已预注册的正式结果，但清楚说明 position-title signal 可能贡献了大部分 93.7%/82.4%。至少应：

- 把 “goes beyond inserting a position name” 删除或改为待验证；
- 补充同职位不同 JD、去掉职位名、CV ablation 和语义 embedding/人工质量评审；
- 写全 TF-IDF 配置、tokenization、stopwords、n-gram、baseline 构造、重复 JD 处理、bootstrap 和 snapshot hash；
- 将 93.7% 定位为 lexical role-conditioning diagnostic，而不是 personalization quality。

### 4.6 比较表含当前事实错误和不可审计判断

表 1 没有定义 full/partial/absent 的可操作判据，也没有给商业产品来源和访问日期。核验当前官方文档后，至少两项已经明显不稳：

- Yoodli 官方文档已明确描述根据回答动态生成 follow-up questions；表中 Adaptive follow-ups = absent 不成立。
- Big Interview 当前官方材料描述了基于岗位/简历/对话的动态问题，并提供单独的视频 body-language、eye-contact、pacing 分析；表中的 adaptive/multimodal 标签需要重新按清晰定义编码。

此外，表把商业练习工具、招聘筛选系统、研究原型和 human coaching 放在同一矩阵，比较对象并不同质；Interviewing.io 的 multimodal 用 `---`，其他“不适用”却用 absent。SimInterview、MockLLM 的能力概述也偏弱，容易造成 straw-man impression；还遗漏了与本 venue/demo 形式相近的 LM-Interview 等邻近系统。

建议把表改为“能力定义 + 可核验来源 + access date”的窄表，并只保留真正可比的 practice systems。每个格子都应能由论文或官方产品文档支持；若商业产品功能随订阅层变化，写 `plan-dependent / not independently verified`，不要凭印象打叉。

## 5. Storyline 一致性审计

### 5.1 当前故事线是什么

摘要和 Introduction 实际讲的是同一条三段式故事：

1. **Access gap**：真实面试少、专家 coaching 贵、自练缺少适配对话和结构化反馈；
2. **Integrated system**：JD/CV 个性化问题 + 数字人 + answer-aware follow-up + text/audio/video assessment + KSA/STAR；
3. **Deployment evidence**：101 accounts、1,564 sessions、7,665 questions、five-stage coverage 和 JD lexical alignment。

这条主线在摘要与 Introduction 之间总体一致，贡献列表也对应 simulation、assessment、usage 三项。问题出在后半篇：正文突然增加 **Human Expert Evaluation of Assessment Quality**，但这一证据完全没有被纳入摘要、贡献或结论；同时正文能支持的 evidence 比摘要和结论中的强形容词弱。

### 5.2 跨章节承诺—证据矩阵

| 核心主张 | Abstract | Intro/Contributions | Body evidence | Conclusion | 审查结论 |
|---|---|---|---|---|---|
| 端到端、multi-stage interview | 强调 | Contribution 1 | 系统流程与问题类别有实现证据 | 重复 | 基本一致；但 90.9% 是生成集合齐全，不是完成率。 |
| JD- and CV-conditioned personalization | 强调 JD+CV | 强调 JD+CV | 只评估了 JD lexical alignment；无 CV-specific test | 重复 JD+CV | **证据链断裂**：CV 贡献没有任何 ablation/人工检验。 |
| answer-aware follow-up | 强调 | Contribution 1 | 208 条 record 触发追问；agent pilot 显示 answer dependence 3.28、diagnostic depth 3.13 | 只重复正面能力 | 能证明“有追问”，不能证明“质量好”；结论选择性省略弱项。 |
| immersive digital human | 标题和摘要强主张 | Contribution 1 | 有 UI/视频/实现描述 | 重复 | “immersive” 未经用户研究、presence 或 usability 评估；宜改为“lip-synced digital-human interface”。 |
| comprehensive multimodal assessment | 标题、摘要强主张 | Contribution 2 | 架构描述完整，但有效 audio/video coverage 仅约 25%/26.5%；本体冲突 | 重复 | **过度主张**；要么补成功率/有效性，要么收缩为“multimodal formative feedback pipeline”。 |
| KSA×STAR grounded | 强调 | Contribution 2 | KSA、STAR、Big Five 在不同环节松耦合使用 | KSA- and STAR-grounded | “×” 暗示统一、验证过的联合框架，实际不是；建议改为“KSA-inspired rubric with STAR-structured feedback”。 |
| evidence-linked / traceable | 强调 | Contribution 2 | 主要是 feature→aspect 映射；70/30 和缺失模态不能完整重建；faithfulness 2.75 | 重复 | 当前不足以称“每个 score 都可追溯”；应展示一条完整 provenance example 并修本体。 |
| assessment quality evaluation | 不出现 | 不在贡献中 | 独立第 5 节，占重要篇幅 | 不出现 | **orphan experiment**；且 provenance 错误。 |
| public accessibility | 明确声称 | access motivation | 第 4 节说 university network | 不提 | **前后冲突**，公开入口也未工作。 |
| usage/deployment | 给总量 | Contribution 3 | 有日志统计 | 重复正面数字 | 算术一致，但样本构成、完成率和 coverage 需要同步披露。 |

### 5.3 贡献与 Conclusion 是否一致

表面上，Conclusion 的三个句群确实覆盖前三项贡献：personalized interview、multimodal report、usage statistics。更深层的问题有四个：

- Contribution 1 说 CV/JD personalization，Conclusion 重复它，但真正的分析只验证 JD 与不同职位的词汇相似度；
- Contribution 2 说 KSA×STAR、13→10→2、traceable，Conclusion 重复正面总结，却没有承认 13→10→2 的图/表/UI 冲突和模态覆盖不足；
- Contribution 3 说 workflow analysis，Conclusion 把 90.9% 与 82.4% 当主要成果，却没有交代 completed sessions 只有 217/1,564；
- 第 5 节既不是 contribution，也没有进入 conclusion；其最关键的负面发现（answer dependence 3.28、diagnostic depth 3.13、faithfulness 2.75）被留在正文，不影响结论语气。

因此答案是：**形式上大致一致，证据上不闭合，且 conclusion 有选择性总结。**

### 5.4 推荐的统一故事线

建议把稿件收束为以下一条更可信、也更适合 Demo track 的 storyline：

> 现有面试练习工具往往把个性化对话、数字人交互和跨模态形成性反馈分散在不同产品或流程中。PolyInterview 的贡献是一个已部署的端到端 demo：根据 JD 和可选 CV 规划多阶段问题，在语音交互中进行受限追问，并把文本、语音和视频信号组织为分层的**形成性反馈**。我们用可复现的部署审计报告功能触达率、失败率与角色条件化诊断，并用如实标注的 protocol pilot 或真实人类评审检验问题、追问和反馈质量；我们不把这些分数解释为 hiring validity 或实际求职结果。

这条线有几个好处：系统 integration 是主贡献；evaluation 与 contribution 对齐；弱化未经验证的 “comprehensive/immersive/theory-grounded validity”；Ethics 也更容易守住“practice, not selection”的边界。

## 6. 标题、摘要和 Introduction

### 6.1 标题

当前标题：

> PolyInterview: An LLM-based Platform for Immersive Mock-Interview Practice with Comprehensive Multimodal Assessment

问题：

- ACL title case 下应写 **LLM-Based**；
- 名词短语通常写 **Mock Interview Practice**，这里的 `Mock-Interview` 不自然；
- “Immersive” 没有 presence/user-experience 证据；
- “Comprehensive” 与实际约 25% audio、26.5% successful video coverage 及本体冲突不相称；
- “Assessment” 容易被理解为经过有效性验证的测评，与实际 formative practice tool 的定位有张力。

更稳妥的首选标题：

> **PolyInterview: An LLM-Based Platform for Adaptive Mock Interview Practice and Multimodal Formative Feedback**

如确实希望突出数字人：

> **PolyInterview: Adaptive Mock Interview Practice with a Digital-Human Interviewer and Multimodal Feedback**

### 6.2 摘要

优点是 problem—system—mechanism—deployment evidence 顺序清楚，读者能快速知道系统做什么。需要修改的点：

1. 去掉摘要中的 `\textbf`、脚注和 hyperlink；把 Demo URL 放在标题下脚注、正文 Demo Interaction 段或专门的 `Resources` 句中。
2. “publicly accessible” 在入口真正可访问前不能写；若仅校园网，准确写成 “deployed in a university trial”。
3. “candidate-specific from CV” 没有评价支持；至少改为系统能力描述，不要让后面的 JD 实验看起来也验证了 CV 个性化。
4. “comprehensive multimodal assessment” 改为 “multimodal formative feedback”，或同步报告每个模态的实际成功率。
5. 101 accounts 和 1,564 sessions 必须在同一句提示 all-account snapshot 含 internal/test activity，否则首屏数字有 marketing impression。
6. 1,422 “five-stage question sets” 应明确是 generated sets with all categories，不是 completed five-stage interviews。
7. 93.7% 应称 matched-vs-cross-role lexical diagnostic；不要暗示整体问题质量、CV grounding 或 beyond-title personalization。
8. 若保留第 5 节为真实人类评估，摘要必须加入最重要的结果和限制；若改为 LLM-agent protocol pilot，可以不进摘要，但正文应明确其辅助地位。

### 6.3 Introduction

Introduction 的宏观顺序合理，但 novelty gap 写得过满：

- “they do not jointly support ...” 完全依赖表 1，而表 1 当前没有可审计标准且含事实错误；
- 现有工作按 conversational realism、LLM question generation、video assessment 三组罗列，但没有说明为什么“integration”本身在 Demo track 具有技术新颖性；
- “KSA×STAR” 的理论地位被抬高到“grounded pipeline”，而引用只支持框架背景，不支持自定义 10 aspects、70/30 权重或 2 tracks；
- “each score linked to behavioral evidence” 比系统实际提供的可追溯信息更强；
- 第一页和第二页密集重复 abstract 中的相同功能和数字，浪费 6 页正文额度。

建议 Introduction 用一段明确列出三个 engineering challenges：实时 multi-agent orchestration、跨模态 failure-aware aggregation、从 feature 到 formative recommendation 的可检查 provenance。这样比仅说“我们把已有能力放在一起”更能建立 technical novelty。

贡献列表建议改成可验证动词：`we implement / we expose / we audit`，避免 `comprehensive / theory-grounded / preserves a traceable path` 这类尚未被验证的价值判断。若真实人评是正式贡献，贡献列表必须新增 evaluation；若不是，就删除“human expert”叙事并降为 protocol pilot。

## 7. 逐图、逐表的图文一致性

### 7.1 Figure 1：teaser/workflow

总体是全文最稳定的一张图，能支持 setup→interview→assessment→feedback 的主故事。需要检查图中文字在单栏宽度和打印版是否仍可读，并在 caption 中避免“evidence-linked”先于正文被定义。若图中使用实际用户数据或头像，应说明是合成/示例数据。

### 7.2 Figure 2：system pipeline

主要冲突：

- 图中使用 `Professional Skills / Communication Skills`，正文使用 `Professional Competency / Communication Competency`；
- 图中存在独立 `Follow-up Agent`，正文 §2.2 说由 `Interviewer Agent` 产生 follow-ups；
- 图用英式 `Behaviour`、`Analyser`，正文整体为美式 `Behavior`、`Analyzer`；
- 图中的组件关系比正文多，但没有说明哪些是实际独立 service/agent，哪些只是逻辑模块；
- Caption 与 Figure 1 都声称 evidence-linked feedback，功能重复较多。

建议以实际代码/service boundary 为准：统一 agent 名称，在图例中区分 online interview path、offline assessment path 和 external APIs；注明错误/缺失模态 fallback，而不是只画 happy path。

### 7.3 Figure 3：六联 UI 图

这是 Demo paper 的关键图，但当前 PDF 第 5 页在正常阅读比例下文字过小，且六个 panel 来自不同 demo sessions，直到 Limitations 才披露。具体问题：

- setup 图显示 CV 为 **Optional**，并显示 PDF/DOC/DOCX，正文 p.2 却写 candidate “uploads a CV in PDF format”；
- overall report 显示 0 分/“Needs Improvement”，会让读者怀疑 demo 是否正常或样例是否完整；
- 正文称 `session verdict`，Ethics 又说不做 pass/fail；“verdict/Needs Improvement”具有 gatekeeping 语气；
- KSA radar 只显示 9 个轴，与正文 10 aspects 不一致；
- 行为特征和 per-question 文本难以辨认，不能有效支持“traceability”；
- caption 暗示一条连续用户旅程，实际上来自不同 session。

建议只保留 3–4 个最能证明贡献的 crop，放大关键文字；用显式标签写 `illustrative screens from separate demo sessions`；换成成功、非零且经过隐私处理的一致 sample session；将 `verdict` 改成 `practice summary` 或 `formative overview`。

### 7.4 Figure 4：assessment framework

这是当前最严重的图文错误：caption 写 13→10→2，图中却有 11 个 aspect，并出现 Big-Five Personality；与正文“不推断或报告人格”直接冲突。`Audio-LLM` 也与 Azure Speech 不一致。必须重新生成，不能只改 caption。

建议新版在视觉上明确三层：

1. 13 个 feature，标明 text/audio/video 来源；
2. 正好 10 个 author-defined formative aspects；
3. 正好 2 个 tracks；

同时用虚线或脚注表示 KSA/STAR 只是 rubric inspiration/feedback structure，而不是经过验证的测量模型；Big Five 若不输出人格，不应作为第 11 个评分节点。

### 7.5 Figure 5：deployment evidence

数值本身与文中 90.9%、93.7%、82.4%、61.4% 一致，但可视化语义有问题：

- `Returning accounts` 含测试、内部和 placeholder 账户，不应称 adoption/retention evidence；
- 90.9% 是 question-set category coverage，不是 interview completion；
- 红色、小字号“验证式”标注视觉上像审稿中的临时批注，且打印可读性不足；
- 四个条形的 denominator 不同，却共享一个 “share of corresponding all-account sample” 轴，读者很难即时理解。

建议将 completed sessions 13.9%、answered/generated 16.6%、audio-valid 25.1%、video-success 26.5% 一并报告，形成真正的 funnel/coverage 图；把 role-alignment 单独成图并加同职位对照。

### 7.6 Figure 6：question generation

Caption 说输入包括 JD、CV、duration，但图中看不到 CV；问题预算也没有体现五阶段中的 candidate questions。若图只表示部分路径，caption 应限缩；若表示完整 planner，需补齐 CV、company/persona、五类问题、duration-specific budget 和 evidence attribution。

### 7.7 Figure 7：adaptive follow-up

Caption/正文写 `consistency, clarity, relevance`，图中则使用 `Contradiction, Clarity, Interest`；概念并不等价。图写 `max3`，正文又说明 Basic/Intermediate/Advanced 分别为 1/2/3。exit/proceed 箭头也不够清楚。应统一一组触发条件、一个 agent 名称和 persona-specific limit，并展示超时/低置信度/空回答的路径。

### 7.8 Table 1：system comparison

除前述当前事实错误外，还需：

- 在 caption 或脚注定义每一列的 full/partial/absent 判据；
- 为商业产品逐项加官方来源与访问日期；
- 区分 practice、screening、research prototype、human service；
- 解释 `—` 与 `×` 的区别；
- 对 PolyInterview 使用与其他系统同一严格标准，特别是 “theory-grounded”“multimodal”“traceable”；
- 如果实际有效 video/audio coverage 不完整，ours 也不能无条件打 full。

### 7.9 Table 2：all-account snapshot

表内数字可追溯，但混合了四种不同单位：account、session、question/answer、file。需增加 snapshot date、抽取版本/hash、去重规则和状态定义。`Completed sessions = 217` 应在正文中同等醒目，而不是只放表里；`pooled scored answers = 1,425` 必须与 answered records = 1,274 对账。

### 7.10 Table 3：quality evaluation

当前表必须撤回或重标。除参与者 provenance 外：

- `n=4` 需要写成 `artifacts/module=4`；
- `Expert SD` 的计算层级错误，应写 agent-module-mean SD；
- `±1 agree` 必须定义 pair construction，最好换成合适的 reliability statistic；
- 12 个 artifact 的选择规则、criteria、scale anchors、模型/提示词和随机性都缺失；
- 均值保留两位与表中 4.62/正文 4.625 的精度要统一。

### 7.11 Table 4：aspect–feature mapping

表是让 70/30 可复现的关键，但目前还不能重建计算：

- Fluency 未出现，实际只使用 12/13 features；
- primary group 内多个特征怎样聚合未说明；secondary 同理；
- 缺失 audio/video 时是 renormalize、impute、置零还是不评分未说明；
- question-level aspect 如何跨问题聚合为 session-level track 未说明；
- 2 tracks 的权重与 overall mean 只在正文零散描述；
- 缩写 `Pron`、`Coher`、`Gest` 可读性较差。

建议增加一个完整数值例子：从某一回答的原始 13 features，经 missing-modality rule、question gating、70/30、跨题聚合，最终得到 aspect、track 和 overall score。只有这样 “reconstructable/traceable” 才有实质内容。

## 8. 术语与命名一致性

当前需要建立 glossary，并在全文、图、UI、代码和表格中统一。建议标准形式如下：

| 当前变体 | 建议统一形式 | 说明 |
|---|---|---|
| `Professional Skills` / `Professional Competency` | **Professional Competency Track** | “Skills” 与 “Competency” 不应混用。 |
| `Communication Skills` / `Communication Competency` | **Communication Competency Track** | 与另一 track 对称。 |
| Big Five / Big-Five / Big-five | **Big Five** | 若不测人格，建议仅在 related/framework discussion 出现。 |
| STAR framework / structure / Method / Methods | **STAR response structure** | 不要暗示它是完整测量理论。 |
| Non-verbal Behavior / Behaviors / Behaviour | **Nonverbal Behavior** 或 **Non-verbal Behavior** | 选一种美式写法全篇统一。 |
| skill-QA / Skill QA / Skill Questions | **skill-focused questions** | `QA` 未定义且不自然。 |
| Follow-up Agent / Follow-up Generator / Interviewer Agent | 选择实际组件名 | 必须与 Figure 2 和实现一致。 |
| Audio-LLM / speech service / Oral Expression evaluator | **Speech-Based Oral Delivery Evaluator** | 同时写明 Azure/Qwen 的真实职责。 |
| Accuracy / pronunciation accuracy / Pron | **Pronunciation Accuracy** | 不要与内容 correctness 混淆。 |
| digital-human / digital human | **digital-human interviewer**（作定语） | 全文一致。 |
| verdict / overall evaluation / result | **formative practice summary** | 与“非 gatekeeping”伦理定位一致。 |
| JD | 首次写 **job description (JD)** | Conclusion 不能首次直接使用缩写。 |
| assessment / feedback | 原始分数用 **formative indicators/feedback** | 在没有 criterion validity 前避免正式测评语义。 |
| KSA×STAR | **KSA-inspired rubric with STAR-structured feedback** | 更准确反映两个框架分别进入不同环节。 |

另需统一大小写：LLM-Based（标题）、WebRTC、Wav2Lip、Qwen3-VL-Plus、Qwen3-ASR；以及英文拼写体系（behavior/analyzer，而不是与 behaviour/analyser 混合）。

## 9. 系统、方法与 Evaluation 审计

### 9.1 User journey 和 implementation

系统描述让人能理解用户大体如何操作，但离“审稿人能复现 demo”仍差关键细节：

- CV 在 UI 中可选，正文却写成必传；没有说明无 CV 时如何退化；
- 8/15/30 分钟怎样映射为每阶段问题预算没有完整表；
- Appendix Figure 6 没有 candidate-question budget；
- Basic/Intermediate/Advanced persona 除追问上限外是否改变语气、难度、rubric 未说明；
- streaming ASR、TTS、digital human、four evaluators 的调用时序和 timeout/fallback 不清楚；
- session pool 只支持 5 个并发，却没有 queue wait、P50/P95 latency、端到端响应时间、成本或 failure rate；
- “network-independent fallback” 实际只是 prerecorded video/PDF，不是可交互 fallback，措辞应准确；
- 外部模型/API 的数据流、区域、持久化、版本和 license 未说明。

Demo paper 不一定要做大规模算法 benchmark，但应给出可演示性指标：启动/排队时间、ASR-to-next-question latency、report generation latency、模态失败率、支持的浏览器/设备、一次 demo 的 API 成本、并发上限及 reviewer fallback。

### 9.2 问题生成与追问

角色 lexical alignment 只能证明某种 role-specific vocabulary signal，不能证明问题：

- 与 CV 中具体经历相关；
- 对 JD 要求有实质覆盖而非词面重叠；
- 难度适当、无歧视、无重复、跨五阶段平衡；
- answer-aware follow-up 确实依赖回答，而不是通用追问模板。

现有 agent pilot 恰好暴露了 answer dependence 和 diagnostic depth 较弱。建议正式 evaluation 至少包含：

1. JD-only、CV-only、JD+CV、no-context 的 ablation；
2. 去掉职位名后的 same-position JD discrimination；
3. 人工盲评 relevance、specificity、coverage、redundancy、safety；
4. follow-up 的 counterfactual test：交换答案后，追问是否合理变化；
5. 报告 refusal/empty answer/ASR error 下的 bounded behavior。

### 9.3 多模态评分的构念效度

最需要谨慎的是把 eye contact、facial expression、posture、gesture、prosody 等信号映射到 General Intelligence、Leadership、Persuasiveness 等高层构念。当前引用不足以支持这些具体映射，70/30 也像作者自定启发式，而不是经验证的测量模型。

这会带来两类问题：

- **科学问题**：表面可追溯不等于构念有效；模型可以解释“分数从哪些 feature 算来”，但不能证明 feature 合理测量 leadership/intelligence。
- **公平性问题**：眼神、姿态、语速和表情高度受文化、口音、残障、神经多样性、摄像头条件和肤色影响；即使只用于练习，也可能给用户造成错误规范压力。

建议把 10 aspects 明确称为 **author-defined formative response indicators**，不要声称心理测量或 hiring validity；删除/重命名 General Intelligence、Leadership 等过宽标签，或用真实专家与 criterion measures 做构念验证。系统应允许关闭摄像头、跳过视觉反馈，提供字幕/文本模式，并明确低置信度与缺失模态不扣分。

### 9.4 KSA、STAR、Big Five 的理论角色

- O*NET/KSA 文献可以支持 job-analysis vocabulary，但不能自动验证当前 10 aspects、2 tracks 或 70/30。
- Janz (1982) 支持 behavior-description interview 的早期基础，但不是当前四字母 STAR acronym/操作化的直接来源；需要更直接来源，或准确写成“STAR-like structure rooted in behavior-description interviewing”。
- McCrae & Costa (1987) 证明 five-factor model，不支持把 communication、leadership、persuasiveness 作为本系统的 social aspect mapping；当前 Appendix D 所称 “prevents ad-hoc labels” 反而缺乏推导。
- `KSA×STAR` 不准确：KSA 用于 aspect 命名/问题规划，STAR 用于行为问题结构和建议，Big Five 又是第三条松耦合支线，并没有一个经验证的叉乘模型。

最稳妥的处理是删除 Big Five 作为评分“grounding”，将 social aspects 直接定义为产品的 formative rubric；KSA 写成 inspiration/organization，STAR 写成 response-structuring heuristic。若坚持 theory-grounded，则需给出从理论构念到 item、feature、权重、评分解释和验证假设的完整 measurement argument。

### 9.5 Usage analysis

优点：作者已经在正文承认 all-account totals 含内部/测试活动，这一点比许多 demo paper 更诚实。问题是该 caveat 没有同步到摘要、图 5 和 Conclusion 的显著位置，而且 completed/answered/valid-modality 的漏斗被隐藏。

建议将 usage section 改为一张数据字典加一个 funnel：

`1,564 created sessions → 217 completed sessions → 1,274 answered records → 743/或明确口径的 scored answered records → 357 valid audio → 378 successful video`。

对每层明确 denominator、去重和失败原因。101 accounts 不应被称作用户；最多称 account directories。若能排除 internal/test 后再给 external-user counts，才可谈 adoption。

### 9.6 Evaluation 设计的最低可接受版本

对于一篇 6 页 Demo paper，不需要把所有构念一次验证完，但至少应形成互补的三层证据：

| 层次 | 回答的问题 | 推荐证据 |
|---|---|---|
| System reliability | 功能是否真实、稳定运行？ | 端到端 task completion、latency、queue、ASR/VLM/audio success/failure、缺失模态 fallback。 |
| Adaptive content quality | 问题/追问是否真的依赖 JD/CV/回答？ | ablation + same-position control + blinded human rating + counterfactual follow-up。 |
| Feedback usefulness/faithfulness | 建议是否基于用户回答且可操作？ | 真实专家评分、supporting-span attribution、hallucination/unsupported-context rate；必要时小型用户 study。 |

当前稿件每层都有一些素材，但三层都没有完整回答：reliability 隐藏失败率，content quality baseline 过松，feedback quality 被错误报告为人类研究。

## 10. 可复现性与工程证据

### 10.1 模型与配置缺失

附录给出 Qwen-Plus/Qwen-Flash、Qwen3-VL-Plus、Qwen3-ASR、Edge-TTS、Azure Speech、LiveTalking、Wav2Lip，但缺少：

- provider model snapshot/version 和访问日期；
- 每个 agent 的 system prompt、temperature、top-p、max tokens、重试策略；
- VLM frame sampling、分辨率、帧数、失败判定；
- ASR/VAD、音频采样和 pronunciation score 配置；
- 随机种子、缓存、并发与 timeout；
- latency/cost/hardware/software version；
- 外部服务区域与数据保留设置。

此外，Bai et al. (2023) 是 Qwen-VL 论文，不能直接作为 Qwen3-VL-Plus 版本说明。应引用当前模型官方 technical report/model card/API documentation，并保留基础论文作为背景。

### 10.2 本地分析流水线漂移

当前工作区存在明显的 artifact drift：

- `recompute_corpus.py` 指向不存在的根目录 `users/`，而实际数据路径是 `backend/users`；
- `make_figures.py` 会生成与当前论文不同的红色“under verification”风格；
- `aggregate_panel.py` 会正确生成 `Agent SD` 和 simulated pilot caption，但论文中的表被手工改成 “Expert SD/ten human experts”；
- 找不到生成部分 `eval_*.csv` 的完整脚本；
- LLM-agent ratings 缺少模型、prompt、seed、运行器版本和时间戳。

另外，panel packet 中名为 `source_digest` 的字段只对**相对路径字符串**做哈希，不是源文件内容哈希；源内容改变但路径不变时 digest 不变。12 个 artifact 实际只对应 8 个不同路径 digest，且没有 input hash、commit、snapshot timestamp 或 selection manifest。十份 agent rating 虽可重新汇总出同样的表格数字，但不能重新运行或验证评分生成过程的独立性。

分析脚本之间还存在公式分叉：一个脚本先求/四舍五入 session mean 再平均，另一个使用 pooled question scores；nonverbal failure 的归类规则也不同。综合报告脚本又混合当前重算统计与静态 clean CSV，并硬编码若干日期和百分比。当前仓库可复算部分 JSON，不等于历史快照可独立追溯。

这意味着从 raw snapshot 到 paper table/figure 不是单一、可重复的 pipeline。建议设置一个 `make paper-data` 或等价命令，从带 hash 的只读 snapshot 生成所有 JSON/CSV/TeX/figure；CI 检查正文中的数字与生成物一致，禁止手工覆写 provenance-sensitive caption。

### 10.3 License 与可安装性

论文和页面都没有 license。需要区分：

- PolyInterview 自有代码的 license；
- Wav2Lip/LiveTalking/模型/API 的各自条款；
- sample CV/JD、头像、音视频、UI screenshot 的使用权；
- 商业 API key 不进入公开包时，reviewer 如何运行。

若无法开源全部系统，可以提供受控 live demo、部分代码、mock backend 和清晰 license boundary；但不能只写“public access”而不给任何可用资源。

## 11. 引用与 Related Work 审计

### 11.1 是否存在虚构或未解析引用

没有发现明显虚构文献；20 个实际 citation key 均能在 bibliography 中解析，BibTeX 编译无 undefined citation。参考文献库中有两条未使用项：`schmidt1998validity`、`ambady1992thin`，建议清理或真正使用。

### 11.2 引用存在但不充分支持相邻主张

| 引用/位置 | 当前用途 | 问题 | 建议 |
|---|---|---|---|
| Peterson et al. (2001) | 支撑 KSA、10 aspects、professional track | 只能支持 O*NET/job-analysis vocabulary，不能验证作者自定映射和权重 | 降低到 `KSA-inspired`; 补具体操作化依据或验证。 |
| Janz (1982) | 支撑 STAR | 是 behavior-description interview 早期论文，不是 STAR acronym 的直接操作化来源 | 补直接 STAR 来源，或改为 rooted in BDI。 |
| McCrae & Costa (1987) | 支撑 social aspects | 不支持 communication/leadership/persuasiveness 的具体映射 | 删除该理论 grounding，或提供正式推导与验证。 |
| Hickman et al. (2022) | 支撑“individual scores difficult to inspect” | 论文更直接支持 reliability/validity/generalizability 风险 | 改写为真正被来源支持的限制。 |
| Zheng et al. (2023) | 支撑 VLM/评估偏差 | LLM-as-a-judge benchmark 不直接验证非语言 VLM 评估风险 | 补直接 multimodal/AVI bias 文献。 |
| Bai et al. (2023) | Qwen3-VL-Plus | 引用的是早期 Qwen-VL，不是当前产品版本 | 增加当前官方 model card/technical report。 |
| SimInterview / MockLLM | 相关系统比较 | 描述过窄，可能低估 resume/job grounding、real-time/two-sided evaluation 等功能 | 回到原文逐项编码，避免 straw man。 |

### 11.3 缺少直接来源

以下系统/服务在正文承担技术角色，却没有直接引用或官方文档：Qwen3-VL-Plus、Qwen3-ASR、Qwen-Plus/Flash、Azure Speech pronunciation assessment、Edge-TTS、LiveTalking；商业产品表也没有任何来源。对易变的产品能力，应写 access date。

建议补充最近且同任务的系统，至少核对 LM-Interview 这类 ACL/EMNLP demo 邻居；是否纳入 GAN I hire you?、Zara、Virtual Interviewers、Real Results 等，应由任务可比性决定，不要为了堆 citation 扩散范围。

### 11.4 DOI 与条目完整性

ACL 格式建议在可用时提供 DOI。至少以下条目可补：

- Hickman et al. (2022): `10.1037/apl0000695`
- Prajwal et al. (2020): `10.1145/3394171.3413532`
- Naim et al. (2018): `10.1109/TAFFC.2016.2614299`
- Hemamou et al. (2019): `10.1609/aaai.v33i01.3301573`
- Janz (1982): `10.1037/0021-9010.67.5.577`
- McCrae & Costa (1987): `10.1037/0022-3514.52.1.81`

本地 `acl.sty` 与当前官方版本一致；`acl_natbib.bst` 与当前 master 相比缺一项近期的超长作者列表修复，现有文献作者数未触发输出差异，但最终提交前仍应整体替换为官方 submission package，而不是只拷贝单个文件。

## 12. 语言、格式、拼写与低级错误

### 12.1 已通过的项目

- PDF 为 A4、10 页，正文/附录页数合规；
- 字体嵌入，无 overfull box；
- 无 undefined reference/citation；
- 没有发现明显普通英文拼写错误，拼写检查命中的多数是专名/模型名；
- 表格编号、图编号和 section reference 均能解析；
- 作者与单位在 single-blind 稿中可见。

### 12.2 需要修复的格式/编辑问题

1. 源文件第 25 行仍有 `% TODO(authors): confirm exact emails...`；提交包中不能留未解决 TODO。
2. 标题 `LLM-based` 应按 title case 改为 `LLM-Based`；`Mock-Interview` 应改为 `Mock Interview`。
3. `\clearpage` 人为把 Limitations 推到第 7 页；ACL 要求 Limitations 紧随 Conclusion 且不强制分页。删除该命令后重新排版检查页数。
4. 摘要中的粗体、脚注、URL 不利于 200-word/纯文本元数据合规；移出摘要。
5. Figure 3、4、5、6、7 中大量字体过小；必须按 100% PDF/打印而不是原图放大后评估。
6. Figure/Table 的 caption 有些只是重复标题，没有交代 sample、denominator、成功/失败或 panel 非同一 session。
7. `session verdict`、`all-account snapshot`、`returning-account evidence` 等词带来超出数据的语义，应精准化。
8. 数字精度不完全统一：4.625/4.62、0.055/0.0058/9.4-fold；应根据统计意义统一有效位数并给 CI。
9. Commercial product 名称/功能需要 access date；`HireVue × (removed 2020)` 这种单元格注释没有来源，且时间敏感。
10. `Interviewing.io (human)` 的 checkmark 在 PDF 抽取时显示为 X，颜色/符号依赖可能影响黑白打印和无障碍；应增加文本标签或使用更稳健符号。
11. PDF metadata 的 title/author/keywords 为空；最终生成时补 `\hypersetup{pdftitle=...,pdfauthor=...}` 等。
12. PDF 未 tagged；如模板/工具链允许，提升 accessibility。至少确保图有可理解 caption、颜色不是唯一编码。
13. 图 5 使用绿色/红色类语义时需检查色盲和灰度打印；表 1 的绿/橙/红也不应只靠颜色表达 full/partial/absent。
14. `JD` 在 Conclusion 中直接出现，应在首次全称后统一缩写，或结论继续写 job description。
15. “current snapshot” 没有日期；所有部署统计必须给 cut-off timestamp。
16. 本地 Demo video 没有字幕轨，且没有覆盖完整 setup→interview→report；应重剪端到端 walkthrough，配人工校对字幕与静态 report fallback。

LaTeX 日志只有 underfull box 警告，没有严重排版溢出。它们不构成拒稿问题，但在删改图表后应重新检查断行和空白。

## 13. Section-by-section 最终诊断

| 部分 | 优点 | 主要问题 | 建议动作 |
|---|---|---|---|
| Title | 系统名与任务一眼可见 | 两个强形容词无证据；大小写/连字符 | 采用更窄、更可验证标题。 |
| Abstract | 结构流畅、信息密度高 | public/comprehensive/CV/93.7% 过强；URL/脚注；样本 caveat 后置 | 重写为能力 + 有限证据 + 明确 scope。 |
| Introduction | access gap 和三项贡献清楚 | novelty gap 依赖错误比较表；理论 grounding 过满；重复摘要 | 用 engineering challenge 建 novelty，统一 contribution/evidence。 |
| Table 1/Related Work | 覆盖商业与研究系统 | 无定义/来源/访问日期，Yoodli 等事实过时，比较对象异质 | 重建窄而可审计的矩阵。 |
| System Overview | 用户流程完整 | CV optional 冲突、agent 名称漂移、happy path only | 增加 fallback、latency、组件边界。 |
| Assessment | 分层表达有潜力 | 13/10/2 不一致、构念/权重未验证、缺失模态未定义 | 建 canonical ontology；降为 formative indicators。 |
| Implementation | 技术栈具体 | model/config/version/licence/latency/cost 缺失 | 补复现表与 demo reliability。 |
| Usage Analysis | 有原始日志与 caveat | completed/answered/valid modality 被弱化；baseline 过松 | 用 funnel 与 same-position controls 重做。 |
| Section 5 | 报告了正负面结果 | 人类 provenance 错误；采样/可靠性/模态不足 | 撤回或重标；最好补真实专家研究。 |
| Conclusion | 简洁并回扣三项能力 | 选择性报告，遗漏 Section 5/失败率/限制；重复强主张 | 严格按证据总结，并加入 scope boundary。 |
| Limitations | 承认内部账号、观察性、无 outcome validity | 仍称 human study；关键 caveat 未前置；强制分页 | 改 provenance，前置核心限制，删 clearpage。 |
| Ethics | 明确 practice-not-hiring 和敏感数据 | 与项目说明冲突；无证据的合规保证；公平/可访问性不足 | 先做技术/法律证据审计，再重写。 |
| Appendix | 补了流程、stack、mapping | 图文冲突、配置不足、70/30 不可重建 | 用少量高价值复现细节替代重复叙述。 |

## 14. 优先级修改路线图

### Wave 0：先止血，不满足就不要投稿

| 任务 | 验收标准 |
|---|---|
| 纠正第 5 节 provenance | 论文、表、caption、Limitations、生成脚本全部一致；human 就有真实原始评分/同意/协议，agent 就明确写 agent pilot。 |
| 修复公开 Demo 入口 | 新浏览器无登录上下文可访问真实视频和 live/installable demo；所有链接非 `#`；页面与当前论文一致。 |
| 核验 Ethics | 每项安全/合规主张有当前部署证据；不成立或未证实的绝对句删除/降级。 |
| 统一 13→10→2 | 正文、图 4、表 4、Figure 3 UI、实际配置逐项一致；Fluency 与 Persuasiveness 去向明确。 |
| 重写多模态 coverage | 对 text/audio/video 各报 denominator、成功、缺失、失败；不再把 1,425 全部称为三模态记录。 |
| 重建 Table 1 | 清晰判据、来源、访问日期；修正 Yoodli/Big Interview；对 ours 使用同一标准。 |

### Wave 1：让核心证据链成立

| 任务 | 验收标准 |
|---|---|
| 重做 personalization evaluation | 加 same-position/different-JD、去职位名、CV ablation；提供方法与 CI；删除不被支持的 “beyond inserting title”。 |
| 增加系统可靠性评估 | task completion、P50/P95 latency、queue、各模态 failure、report generation 和 fallback。 |
| 收缩构念主张 | 将未验证的 intelligence/leadership 等明确为 formative indicators，或提供专家/criterion validation。 |
| 对齐 storyline | 摘要、3 项/4 项贡献、章节和 Conclusion 使用同一组 claims/evidence/caveats；Section 5 不再孤立。 |
| 统一术语与图 | glossary 全局检查；Figure 2/4/6/7 和 UI 重新导出。 |
| 补复现信息 | snapshot date/hash、模型版本、prompt/config、frame/audio processing、缺失值规则、聚合公式。 |

### Wave 2：提交质量清零

| 任务 | 验收标准 |
|---|---|
| ACL 格式 | 使用官方 submission package；确认 single-blind review mode；删除 `\clearpage`；重新审计 6+2 页。 |
| 文献 | 补 DOI、产品官方来源和访问日期；更新 Qwen3/ASR/Azure/LiveTalking 文档；清理未用条目。 |
| 页面与许可 | 写清 source/demo/data/license boundary、guest credentials、安装/运行说明。 |
| 图表可读性 | A4 100% 与灰度打印可读；不用颜色作为唯一编码；caption 自包含。 |
| 元数据/清洁 | 删除 TODO，确认邮箱，补 PDF metadata，重新跑 BibTeX/LaTeX/chktex/link checker。 |

### 建议的稿件取舍

六页正文空间有限。最优取舍不是继续加内容，而是：

- 压缩重复的 abstract/intro/system 形容词；
- 缩小/拆分 Figure 3，只保留可读 panel；
- Table 1 改成少量真正可比系统；
- 把 Figure 4 做成唯一 canonical assessment diagram；
- 将 usage 统计换成可靠性 funnel；
- 把省下的篇幅用于一项可信的 adaptive-content evaluation 和一项真实/诚实的 feedback-quality evaluation。

## 15. 投稿前逐条核对清单

- [ ] 第 5 节参与者身份与原始记录一致；没有把 agent 写成人。
- [ ] Demo、video、paper、code/package 每个链接都实际可点。
- [ ] 入口权限限制与 “publicly accessible” 的表述一致。
- [ ] License 已写清。
- [ ] 13 features、10 aspects、2 tracks 在图/表/UI/代码一致。
- [ ] Fluency 被映射或从计数中删除。
- [ ] 缺失 audio/video 不会被当作低分；规则在文中可重建。
- [ ] 1,425 与 1,274/743 的统计单位已对账。
- [ ] Completed sessions 217/1,564 与 workflow coverage 1,422/1,564 被清楚区分。
- [ ] 摘要/图/结论明确账户包含内部和测试活动。
- [ ] Role alignment 加入 same-position 与 CV ablation，或收缩结论。
- [ ] Table 1 每格有定义与来源；Yoodli/Big Interview 已更新。
- [ ] 所有 security/privacy/IRB/provider claims 有证据。
- [ ] 不再把 Big Five 画成输出人格分数。
- [ ] General Intelligence/Leadership/Persuasiveness 的构念范围和公平风险已处理。
- [ ] 摘要、贡献、Section 5、Conclusion 一一对应。
- [ ] 标题不再使用未验证的 “Immersive/Comprehensive”，或补足证据。
- [ ] 模型版本、prompt/config、latency、failure rate、snapshot date/hash 已写。
- [ ] Figure 3–7 在 A4 100% 可读，caption 与内容一致。
- [ ] Demo video 在 2.5 分钟内完整展示 setup→live interaction→report，并有字幕。
- [ ] 删除 source TODO、摘要脚注、Limitations 前的 `\clearpage`。
- [ ] 用官方 ACL submission package 重编译并检查 page limit/font/citations。

## 16. 作者必须能回答的十个问题

1. 第 5 节十名“人类专家”的原始招募、同意和评分记录在哪里？为什么所有数值与 10 个 LLM agents 完全相同？
2. 审稿人从论文 URL 出发，怎样在不联系作者的情况下运行系统或安装 package？
3. 13 个 feature 中的 Fluency 最终进入哪个 aspect？为什么 UI 只有 9 轴、图 4 有 11 个中层节点？
4. 1,425 score records、1,274 answered records 和 743 answered subset 分别是什么单位、怎样关联？
5. 为什么只约四分之一记录有有效 audio/video feature，论文却称 1,425 条都覆盖三模态？
6. 如果删掉职位名并只在同职位不同 JD 之间比较，个性化结果还剩多少？CV 到底贡献多少？
7. 70/30 的经验或理论依据是什么？缺失模态和组内多特征如何计算？
8. 眼神、姿态如何有效且公平地支撑 General Intelligence、Leadership、Persuasiveness？用户能否关闭视觉评价？
9. encrypted storage、strict access、no-training、IRB-approved、metadata-only 各自有什么当前证据？
10. 为什么 quality evaluation 的最弱结果没有进入 Conclusion，而仍保留 comprehensive/traceable 的无条件措辞？

## 17. 审核证据索引

### 17.1 本地材料

- [当前 PDF](../paper/main.pdf) 与 [LaTeX 源稿](../paper/main.tex)
- [全账户统计](../analysis/corpus_stats_all.json)
- [LLM-agent panel README](../analysis/llm_agent_panel/README.md)、[summary](../analysis/llm_agent_panel/summary.json)、[evaluation packet](../analysis/llm_agent_panel/evaluation_packet.json)
- [Figure 4 assessment framework](../paper/figures/flow/assessment_framework.png)
- [当前 landing-page source snapshot/项目材料所在目录](../paper_sources/)
- `paper_sources/PolyInterview 项目说明文档 - 飞书云文档.pdf`
- `paper_sources/Demo.mp4`

### 17.2 官方与当前外部来源

- [EMNLP 2026 System Demonstrations Call](https://2026.emnlp.org/calls/demos/)
- [ACL paper formatting guidelines](https://acl-org.github.io/ACLPUB/formatting.html)
- [论文当前给出的 PolyInterview landing page](https://dannywang1922.github.io/polyinterview/)
- [PolyU 官方 PolyInterview 试用新闻](https://www.polyu.edu.hk/iherd/news-and-events/news/2026/20260427-polyinterview/)
- [Yoodli 官方动态追问说明](https://support.yoodli.ai/en/articles/9550465-practice-with-yoodli)
- [Big Interview 官方 interview simulator](https://www.biginterview.com/platform/practice-with-interview-simulator)
- [Big Interview PracticeAI 官方说明](https://support.biginterview.com/en/article/practiceai-qxju4/)

### 17.3 结论边界

本报告审的是**当前工作区中这一个版本**，并不推断作者在工作区外一定没有真实 human study、更新后的安全部署或未公开的 reviewer 入口。如果这些材料确实存在，它们可以解除部分 blocker；但在当前提交包中不可见，而且第 5 节数字与 LLM-agent pilot 完全相同，所以审稿人只能按现有证据作出上述判断。

同样，项目说明是 2026-03-13 版本，可能早于当前部署；报告据此指出的是“论文绝对表述目前缺乏一致证据”，而不是未经线上渗透测试就断言现网必然保持旧缺陷。最稳妥的处理是以当前代码和部署审计逐项取证。

## 18. 五视角独立审稿面板

为避免单一审稿偏好主导结论，本次审查分别采用 editorial/venue、methods/statistics、domain/theory、cross-disciplinary/user-risk、devil's-advocate 五种视角。五位审稿视角在看到其他意见前先独立判断，再进行证据交叉核对。

评分含义：`block` 表示该维度存在足以阻止当前版本接收的问题；`warn` 表示重大缺陷但未单独达到阻断；`pass` 表示没有发现实质问题。

| 视角 | 方法严谨性 | 领域准确性 | 论证一致性 | 跨学科/用户影响 | 写作与结构 | 编辑决定 |
|---|---|---|---|---|---|---|
| Editor / venue compliance | block | block | warn | warn | block | Reject / Major Revision |
| Methods & statistics | block | block | block | warn | warn | Reject / Major Revision |
| Domain & theory | block | block | block | block | block | Reject / Major Revision |
| Cross-disciplinary / UX-risk | block | block | block | warn | block | Reject / Major Revision |
| Devil's advocate | block | block | block | block | block | Reject / Major Revision |

共识强度：

- **5/5** 将 methodology 和 domain accuracy 判为 block；
- **4/5** 将 argumentative coherence 判为 block，另 1 位为 warn；
- **2/5** 将 cross-disciplinary/user impact 判为 block，另 3 位为 warn；
- **4/5** 将 writing/structure 判为 block，另 1 位为 warn；
- **5/5** 给出 `Reject or Major Revision`，没有一位建议按现状接收或小修。

一致认定的核心问题是：human/LLM provenance、demo strict link、13→10→2 冲突、multimodal denominator、证据过度外推。分歧只在于安全/公平/写作问题是否单独构成 block，而不是这些问题是否存在。

### 面板共同认可的优点

- 任务适合 Demo track，端到端用户旅程和系统集成具有展示价值；
- 有真实的大学试用部署和较丰富的日志，不是纯概念 mock-up；
- 技术栈、WebRTC、四服务和并发上限提供了一定工程细节；
- Limitations 已承认内部/测试活动和缺少长期 outcome validity；
- “仅用于练习、不用于招聘决策”的伦理方向是正确的，只是产品与证据尚未完全兑现。

### Devil's-advocate：对作者最有利的解释

最宽容的解释是：真正的人类评审在仓库外完成，只是暂时误复用了 LLM pilot 数字；安全文档是旧版本；公开入口准备在正式提交时替换；图和 UI 来自不同系统版本。系统本身、部署日志和本地视频也确实可能是真实的。

即便如此，当前版本仍不能通过，因为这要求多个巧合同时成立：真实人类结果逐项等于模拟 panel；表格只把 `Agent SD`/simulated caption 改成 `Expert SD`/human caption；旧安全缺陷均已修复但没有证据；四个公开按钮都恰好尚未替换。审稿只能评价当前提交记录，不能用未来材料补足当前事实。

能够推翻本报告主要 blocker 的证据也很明确：真实专家的匿名原始评分与招募/伦理记录；当前部署的安全审计；可从干净浏览器运行的 reviewer path；统一且由代码生成的 13→10→2 schema；按模态和回答状态拆分的版本化数据字典与一键复算流程。若这些证据提供并与新稿完全一致，应重新审查，而不是机械沿用本次结论。

## 19. 最终编辑决定

**当前状态：Reject as-is；内部处理级别：Major Revision。**

这不是因为论文缺少一个更漂亮的图或几句更顺的英文，而是因为当前最重要的 evaluation provenance、demo availability、assessment schema 和 modality accounting 都没有达到可核验的一致状态。它们修好以后，PolyInterview 仍然有机会成为一篇有吸引力的 Demo paper；但在修好以前，继续强化 “human-expert validated / comprehensive / publicly accessible / theory-grounded” 只会增加风险。

最合理的下一版成功标准是：**所有重要名词都能在同一张 canonical schema 中找到；所有重要数字都能从带 hash 的 snapshot 一键生成；所有关键主张都能指向一项匹配的证据；所有公开/伦理陈述都能由审稿人独立验证。**
