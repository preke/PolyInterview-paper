# PolyInterview — Presentation Script (双语 / Bilingual)

- **Deck**: `main_optimized.pptx` (15 slides)
- **Duration**: 20 minutes (≈ 18.5 min talk + 1.5 min buffer for transitions / Q&A handoff)
- **Audience**: PolyU faculty (academic, mixed CS / language-teaching / education backgrounds)
- **Speaker**: Zhiyuan Wen, Research Assistant Professor, COMP & IHERD
- **Tone**: Academic but conversational; lead with the problem, ground every design choice in evidence, end on responsible deployment.

> Pacing tip: ~140–150 English words per minute (slightly slower for an academic talk). Chinese ~220–240 字/分钟. The word counts below are tuned to the time budget — feel free to compress if Q&A starts running into your slot.

---

## Slide 1 — Title (≈ 30 s)

**EN**
> Good afternoon, everyone — thank you for making the time. I'm Zhiyuan Wen, a Research Assistant Professor jointly with COMP and IHERD. What I'd like to share today is **PolyInterview** — a project we've built around a simple question: *can AI become a genuine learning tool for interview skills, not just a Q&A bot?* Over the next twenty minutes I'll walk you through why we started this, how the system is designed, what the first hundred-plus users told us, and how we are handling student data. I'll keep some time at the end for your questions.

**中文**
> 各位老师下午好，非常感谢大家抽空来参加。我是温智渊，是 COMP 和 IHERD 联聘的 Research Assistant Professor。今天想和各位分享的项目叫 **PolyInterview**。我们想回答一个比较简单的问题——**AI 能不能真正成为一种学习面试技能的工具，而不仅仅是一个问答机器人？** 接下来 20 分钟，我会先讲我们为什么做这件事，再介绍系统的设计、首轮一百多位用户的反馈，以及我们如何处理学生的数据。最后会留几分钟给各位老师提问。

---

## Slide 2 — Why the Pressure Is Intensifying (≈ 2 min)

**EN**
> Let me start with the picture our students are facing. The Hong Kong graduate market has been **shrinking** — JIJIS data from February shows openings continuing to fall, youth unemployment for ages 20–24 sat at **12.3 %** in late 2025, and salary growth for new hires is barely half a per cent. At the same time, employers have **raised the bar**: NACE and SHRM both report that companies have shifted to skills-based hiring, that they actively run skills tests *inside* the interview, and that soft skills are now ranked **equal to or above** hard skills.
>
> The result you can see on the right: **80 %** of professionals feel unprepared for the 2026 cycle, and **93 %** report interview anxiety. Realistically each opening attracts about 242 applications, of which only **2 %** reach an interview at all.
>
> So the funnel is brutal — and that's exactly the gap that traditional preparation can't fill. Real interviews are too rare to learn from. Expert mock interviews from services like Interviewing.io cost **180 US dollars or more** per session — they cannot scale during peak recruitment. And practising alone in front of a mirror almost never surfaces the *probing* follow-ups that decide an offer. **Without realistic, repeatable, feedback-rich practice, capability rarely converts into an offer.** That's the gap PolyInterview tries to close.
>
> 🙋 **Audience question** *(quick show of hands, ~15 s)* — *Before I move on, I'm curious — how many of you, just in this past semester, had a student come to your office and ask "could you help me practise for an interview?" … Yeah, that's about what we expected. Now imagine doing that for every one of them, every recruiting season — that's the wall we're trying to take down.*

**中文**
> 我们先看学生现在面对的处境。香港的应届生市场在**持续收缩**——JIJIS 二月份的数据显示岗位还在减少，2025 年下半年 20–24 岁青年失业率达 **12.3 %**，新入职平均薪资同比仅增长 **0.5 %**。与此同时，雇主**门槛在提高**：NACE 和 SHRM 的报告显示，公司普遍转向基于技能的招聘，**直接在面试中加入技能测试**，并且把软技能放到和硬技能同等甚至更重要的位置。
>
> 右边这组数字大家可以感受一下：**80%** 的求职者觉得自己没准备好，**93%** 表示有面试焦虑；平均每个岗位收到约 **242 份简历**，最终只有约 **2%** 的人能走进面试。
>
> 漏斗已经非常残酷，而传统的准备方式恰恰在这里失灵。真实面试太少，几乎没法从中学习；像 Interviewing.io 这样的专家模拟面试，单次价格在 **180 美元以上**，招聘高峰时根本扩不上去；学生自己对着镜子练，几乎练不到那些**真正决定录用与否的追问**。**没有真实、可重复、带反馈的练习，能力很难转化成 offer**——这就是 PolyInterview 想要补上的缺口。
>
> 🙋 **互动提问** *（举手即可，约 15 秒）* —— *讲下一页之前我想先问一下各位老师——**就这一个学期**，有多少位老师有学生跑来你办公室问"能不能帮我练一下面试"？麻烦举个手……差不多就是这个比例。再想象一下，如果每个招聘季都要为每一个学生这样做一遍——这正是我们想要拆掉的那堵墙。*

---

## Slide 3 — Limitations of Existing AI Interview Platforms (≈ 1 min 30 s)

**EN**
> AI is the obvious response, and there are already well-known platforms — Google Warmup, Yoodli, Big Interview, HireVue, Interviewing.io, and others. We surveyed them across four dimensions and found a consistent gap pattern.
>
> **One — personalisation**: most rely on static question banks, or personalise only the very first question, with no real follow-up reasoning. **Two — feedback depth**: tools tend to return surface metrics like word count and filler-word rate, or hand back a polished model answer, without grounding any of it in pedagogical theory. **Three — multimodal assessment**: most are still audio-plus-text only; facial expression, voice, fluency are largely overlooked — HireVue actually *removed* its facial-analysis feature back in 2020 under public pressure. **Four — scenario continuity**: almost all are one-off Q&A; nobody simulates a coherent multi-stage HR-then-behavioural-then-technical interview.
>
> So the bottom line is: **students still cannot rehearse a realistic, end-to-end interview** on existing tools. Generic questions, shallow feedback, and none of the dynamic of a live conversation. That gap is what we set out to design against.

**中文**
> AI 是一个很直接的解法，市面上其实已经有不少代表产品——Google Warmup、Yoodli、Big Interview、HireVue、Interviewing.io 等。我们沿着四个维度做了一轮调研，发现它们的不足非常一致。
>
> **第一，个性化与出题**：大多依赖静态题库，或者只对第一个问题做个性化，没有真正的追问推理。**第二，反馈深度**：往往只给一些表层指标，或者直接返回一个"标准答案"，背后**没有理论支撑**。**第三，多模态**：基本停留在音频加文本，面部表情、语音、流畅度几乎被忽略——HireVue 在 2020 年甚至**主动下线**了人脸分析功能。**第四，场景连贯性**：几乎都是一问一答，没有人完整模拟"HR — 行为 — 技术"的多阶段面试。
>
> 一句话——**学生在现有工具上仍然无法练完一场真正完整的面试**：题目泛、反馈浅、缺少真实对话的张力。这正是我们设计 PolyInterview 时要正面解决的问题。

---

## Slide 4 — Framing: Match × Convince (≈ 1 min 30 s)

**EN**
> Before showing the system, I want to share the conceptual frame we use. Drawing from HK and global employer surveys — HKU CEDARS' 2025 survey of 320-plus employers, LinkedIn's skills-based-hiring report, and the classic Schmidt-and-Hunter meta-analysis — we converged on a very simple equation: **an offer equals Match times Convince.**
>
> **Match** is whether your ability fits what the role actually needs — work attitude, interpersonal skills, problem solving — what HR translates into the **KSA** model: Knowledge, Skills, Abilities.
>
> **Convince** is whether you can communicate that fit clearly. Structured interviews predict job performance with a correlation of **0.51**, versus 0.38 for unstructured ones; thin-slice judgments — within the first five minutes — already carry a 0.39 correlation with the final outcome. **STAR** has been the de-facto behavioural-answer structure since DDI introduced it in 1974.
>
> It's a multiplication, not an addition — if either side is zero, you don't get the offer. So PolyInterview targets **both**: personalised questions for the Match side, multimodal coaching for the Convince side. Everything that follows maps back to this equation.

**中文**
> 在介绍系统之前，我想先分享一下我们用的概念框架。结合港大 CEDARS 2025 年对 320 多家香港雇主的调研、LinkedIn 的技能招聘报告，以及 Schmidt 和 Hunter 那篇经典的元分析，我们提炼出一个非常简单的等式——**录用 = Match × Convince（匹配 × 表达）**。
>
> **Match**，是你的能力是否真的匹配这个岗位——工作态度、人际、解决问题——HR 把它翻译成 **KSA 模型**：Knowledge（知识）、Skills（技能）、Abilities（能力）。
>
> **Convince**，是你能不能把这种匹配清楚地传达出去。结构化面试预测工作绩效的相关性是 **0.51**，非结构化只有 0.38；面试官前 5 分钟形成的"薄片判断"，与最终结果相关性已经达到 0.39；**STAR** 自 1974 年 DDI 提出后，一直是行为面试题事实上的回答结构。
>
> 这是**乘法关系**——任何一边为零，offer 都拿不到。所以 PolyInterview 要同时做两件事：用**个性化提问**支撑 Match，用**多模态反馈**支撑 Convince。后面整套设计都会回到这个等式。

---

## Slide 5 — Journey Walk-Through (≈ 20 s, transition slide)

**EN**
> Now let me walk you through how a student actually uses the system. There are three stages — **Setup**, **Live Interview**, and **Report**. Setup configures the session, the live interview is where the multimodal Q&A happens, and the report turns everything into actionable feedback. We'll go through each.

**中文**
> 接下来我带各位看一下学生**真正使用这个系统的全流程**。一共三个阶段——**配置（Setup）**、**实时面试（Live Interview）**、**报告（Report）**。配置阶段定下整场面试的参数，实时面试阶段做多模态问答，报告阶段把整场面试转化成可执行的反馈。我们一段一段来。

---

## Slide 6 — Setup: Four Parameters on One Screen (≈ 1 min)

**EN**
> Setup is deliberately one screen and four parameters. **First**, choose your interviewer — three personas: Amy the friendly coach, David the strict expert, and James the structured analyst; the persona drives how aggressive the follow-ups will be. **Second**, pick the target job, either from a pre-defined bank with role descriptions, or upload your own. **Third**, set duration — 8, 15, or 30 minutes — and the system maps that to a tailored question count. **Fourth**, upload your CV; we parse it on the fly so every question is grounded in the candidate's actual skills and experience. One screen, four parameters, a fully personalised session. The user never has to write a prompt.

**中文**
> 配置页我们刻意做成**一屏四个参数**。**第一**，选面试官——三个 persona：友善型教练 Amy、严格型专家 David、结构化分析师 James；persona 决定追问的力度。**第二**，选岗位——内置岗位库带 JD，也可以自定义上传。**第三**，选时长——8、15 或 30 分钟，系统会把时长映射成对应的题量。**第四**，上传简历——我们当场解析，让每一个问题都贴着学生真实的技能和经历去出。一屏、四个参数，一场完全个性化的面试，**学生不需要会写 prompt**。

---

## Slide 7 — Live Interview: Three Follow-Up Strategies (≈ 1 min 30 s)

**EN**
> This slide is where Match really shows up. The same student answer — *"I led a team to redesign the checkout flow and it improved conversion"* — produces three very different follow-ups, depending on the persona.
>
> 🙋 **Audience question** *(rhetorical, ~20 s — pause briefly, don't wait for an answer)* — *Before I reveal what the three personas actually do, let me ask the room — if that were **your** student sitting in front of you, which kind of follow-up would you instinctively reach for? Something encouraging? Something that drills for the data? Or something counterfactual — "what if it had failed?" Hold that intuition for a second — let's see what the system does, and whether it matches your instinct as a teacher.*
>
> Amy, the friendly coach, asks **one** basic follow-up: *"What's one thing you learned from the project?"* — encouraging.
>
> David, the strict expert, runs **two** intermediate follow-ups, drilling for evidence: *"By how much did conversion improve, and over what time window?"*
>
> James, the structured analyst, runs **three** advanced follow-ups, including counterfactuals: *"What would you have done differently if the A/B test regressed in the first week?"*
>
> So the depth is configurable — students can scale up the difficulty as they get more confident — and the agent decides on the fly which dimensions to probe based on the CV and the previous answer. **This is what we mean by personalisation that goes beyond the first question.**

**中文**
> 这一页是 **Match 真正落地**的地方。同样一句学生回答——"我带队重新设计了结账流程，转化率有提升"——三个 persona 会给出完全不同的追问。
>
> 🙋 **互动提问** *（修辞性提问，约 20 秒——停顿一下，不必等回答）* —— *在我揭晓三个 persona 的追问之前，想先问问各位老师——如果这个学生坐在**你**面前，**你**会本能地用哪一种追问？是偏鼓励的？还是逼数据的？还是反事实的——"如果失败了你会怎么办"？请各位先把这个直觉记在心里——我们看看系统的处理，是不是和**你作为老师的直觉**对得上。*
>
> 友善型 Amy：**1 个基础追问**——"你从这个项目中最大的一个收获是什么？" 偏鼓励。
>
> 严格型 David：**2 个进阶追问**，逼数据——"转化率提升了多少？时间窗口是多久？"
>
> 结构化型 James：**3 个高阶追问**，包括反事实——"如果 A/B 测试在第一周就回退，你会怎么做？"
>
> 所以**追问深度是可配置的**，学生可以随着自信心提升逐渐加难度；而且 agent 会根据简历和上一轮回答**临场决定**该往哪个维度追。这就是我们说的——**真正能延伸到首问之外的个性化**。

---

## Slide 8 — Live Interview: Embodied Interaction (≈ 1 min 30 s)

**EN**
> If Slide 7 was Match, this is where **Convince** comes alive. Three things to highlight here.
>
> One — the interviewer is a **digital human**, not a chatbot. Real-time face and lip-sync render the chosen persona as a live video avatar. The candidate is talking to *a face*, which immediately reintroduces the social pressure that flat-text practice cannot reproduce.
>
> Two — **synchronous capture**. Voice, facial expression, and body language all stream in live. Every signal the candidate produces is recorded and analysable downstream.
>
> Three — **beyond the words**. The system evaluates not just *what* the candidate says, but *how* — reasoning, fluency, composure, non-verbal presence. This is what existing tools simply do not see.
>
> The takeaway: we deliberately move from a scripted Q&A to a **face-to-face, embodied interaction**, because that's what a real interview actually is.

**中文**
> 第 7 页是 Match，这一页是 **Convince 真正活起来的地方**。三个重点。
>
> 第一，**面试官是数字人**，不是聊天机器人。实时人脸和口型同步把所选 persona 渲染成一段直播 avatar。学生面对的是**一张脸**，那种社交压力会立刻回来——这是文字对话练不出来的。
>
> 第二，**同步采集**。语音、表情、肢体动作同时实时上传，候选人产生的**每一路信号**都被录下、可分析。
>
> 第三，**超越文字**。我们评估的不只是"说了什么"，更是"怎么说"——推理、流畅度、镇定感、非语言表现。这正是现有工具看不见的层面。
>
> 一句话总结——我们刻意从"脚本式问答"走到**"面对面、具身的交互"**，因为真实的面试本来就是这样的。

---

## Slide 9 — Convince Architecture (≈ 2 min)

**EN**
> This is the most technical slide, so let me take a moment. We score Convince through a **three-layer evaluation architecture**.
>
> **Layer one — Features.** Thirteen signals on a 0-to-10 scale. Four feature agents run **in parallel** on every answer: a Professional-Performance agent and a Way-of-Expression agent that work on the text via an LLM; a Non-Verbal-Behaviour agent that works on the video via a vision-language model — eye contact, posture, expression; and an Oral-Expression agent that works on the audio via Azure speech.
>
> **Layer two — Aspects.** An aggregation agent maps those features into ten **KSA-aligned dimensions**: three cognitive, three background, four social — the social ones are designed to be Big-Five aware. The aggregation is a 70-30 weighting between primary and secondary mappings, and the LLM picks **which aspects are relevant for each question** — you don't score "teamwork" on a question that isn't about teamwork.
>
> **Layer three — Proficiency.** Aspects roll up into two competency tracks: **Professional Competency** combining cognitive and background, and **Communication Competency** combining social and expression. The overall score is the average, and the result feeds the report you'll see next slide.
>
> Two things I want to underline. First, the parallel-agent design means a 30-minute interview gets scored in roughly the time of a single answer's compute, not 30 times that. Second, every score traces back through the layers — students don't just see a number, they see exactly which signal pulled it up or down.

**中文**
> 这一页是技术性最强的一页，我多花一点时间。我们通过**三层评估架构**来打分。
>
> **第一层——特征（Features）**：13 个 0-10 分的信号。每个回答上，**四个特征 agent 并行**：Professional Performance 和 Way of Expression 由 LLM 处理文本；Non-Verbal Behaviour 由视觉语言模型（VLM）处理视频——眼神、姿态、表情；Oral Expression 由 Azure 语音处理音频。
>
> **第二层——维度（Aspects）**：聚合 agent 把特征映射到 **10 个 KSA 维度**——3 个认知、3 个背景、4 个社交（社交维度刻意做了 Big-Five 兼容）。映射用 **70/30 主-副权重**，并且 LLM 会判断**当前题目应该激活哪些维度**——一道不考"团队协作"的题就不打"团队协作"分。
>
> **第三层——能力（Proficiency）**：维度向上聚成两条赛道——专业能力（认知 + 背景）和沟通能力（社交 + 表达）。总分取均值，最后送进报告。
>
> 两点想特别强调。第一，**并行 agent** 让 30 分钟的面试打分时间约等于单题的计算时间，而不是 30 倍。第二，**每个分数都能层层回溯**——学生看到的不只是一个数字，而是清楚地知道是哪个信号把分拉高或拉低的。

---

## Slide 10 — Feedback & Report (≈ 1 min 30 s)

**EN**
> What the student actually receives is **two-tier feedback**.
>
> **Per-question replay** is delivered the moment each answer ends. They see a 0-to-10 score, the full transcript, a Suggestion card with summary / strengths / improvements / a worked example, and a **Polished card** that rewrites their *own* answer into a higher-scoring version — same content, better structure. This is the loop we want them in: answer, see the gap, see the rewrite, try the next question better.
>
> **Whole-interview report** is compiled when the session ends, in three integrated panes. **Overall Evaluation** — the headline verdict, the two competency scores, an executive summary. **Competency Overview** — a radar chart over the ten KSA aspects with a per-aspect coaching tip. **Skills & Behaviours** — the thirteen multimodal features, including eye contact, posture, oral delivery.
>
> So the design here is intentionally pedagogical: **each answer becomes the next better attempt**, and the whole session becomes a roadmap.

**中文**
> 学生最终拿到的是**两层反馈**。
>
> **逐题回放**——每答完一题就出。包含 0-10 分、完整逐字稿、一张 Suggestion 卡（小结 / 优点 / 改进 / 范例），以及一张 **Polished 卡——把学生自己的回答改写成一份更高分的版本**。同样的内容，更好的结构。我们希望学生进入这样一个循环：作答 → 看到差距 → 看到改写 → 下一题答得更好。
>
> **整场报告**——面试结束后整合呈现，三个面板：**Overall Evaluation**（总评：定性结论 + 两条能力分 + 执行摘要）；**Competency Overview**（10 个 KSA 维度的雷达图，每个维度配一句教练式建议）；**Skills & Behaviors**（13 个多模态特征——眼神接触、姿态、口语表达等）。
>
> 所以这一页的设计**本质上是教学性的**——**每一题都成为下一题进步的起点**，整场面试变成一条可执行的成长路径。

---

## Slide 11 — User Testing (≈ 1 min 30 s)

**EN**
> We've run pilot testing with **129 participants across six institutions** — PolyU, CUHK, CityU, UESTC, and an industry group at Xiaomi — covering eight-plus disciplines from CS and EE through to psychology and multimedia, from bachelor's all the way to postdoc. Importantly for this room, **nine faculty reviewers** from PolyU's ELC and LEI English-language teams sat with us in Round 1.
>
> **Round 1 in March** — broad-base review with 13 participants — confirmed the core experience. The top praise points were UI clarity at **67 %**, the immersive digital-interviewer experience at **58 %**, the depth of the report at **50 %**, and the feel of the personalised questions at **42 %**.
>
> **Round 2 in April** — deeper interviews with 116 senior students preparing tech-track interviews — was qualitative. The recurring themes from those sessions: *"smooth flow — I'd actually use it to practice"*, *"questions felt highly professional and on-topic"*, *"the digital interviewer felt close to a real session"*. Those are exactly the signals we wanted — that the system passes the **realism bar**.

**中文**
> 我们已经完成了一轮 pilot，**129 位参与者，覆盖 6 个机构**——PolyU、中大、城大、电子科大，还有小米的产业方代表——8 个以上学科（CS、EE、机械、土木、城市、管理、心理、多媒体），从本科一直到博士后。在座各位老师可能更关心这一点：第一轮我们邀请了 **9 位 PolyU 的英语教学老师**（ELC 和 LEI），他们一起参与了评测。
>
> **第一轮（3 月）**——13 位广泛评审，主要确认核心体验。点赞最多的是：UI 清晰 **67%**、数字面试官沉浸感 **58%**、报告详尽 **50%**、个性化提问 **42%**。
>
> **第二轮（4 月）**——116 位准备技术岗位的高年级同学的深度访谈，更偏定性。反复出现的反馈是："**整体流畅，我真的会拿它来练**"、"**题目专业、贴主题**"、"**数字面试官接近真实**"。这正是我们想要的信号——系统**通过了"真实感"这个门槛**。

---

## Slide 12 — Welcome to Experience (≈ 30 s)

**EN**
> A practical note before we go on. The platform is live now on PolyU's network — the URL on the slide, accessible from PolyUWLAN. There is a built-in booking function; one slot is one hour, and bookings have priority, but if there's spare capacity you can walk in. **I'd genuinely value if any of you tried it on a real role you were going to interview a student for** — the feedback channel is the email at the bottom of the slide. Any questions, suggestions, or technical issues, please write directly to me.

**中文**
> 这里插一段实操信息。平台目前已经在 PolyU 校园网上线——网址在屏幕上，**通过 PolyUWLAN 可以访问**。我们有内置的预约功能，每个 slot 一小时，**预约用户优先**，有空位时也接受 walk-in。**很希望各位老师能用一份真实的岗位 JD 试一下**——比如你下一次会面试学生的那种岗位。屏幕下方是反馈邮箱，**任何问题、建议、技术问题都欢迎直接发给我**。

---

## Slide 13 — Theoretical Framework: KSA × STAR (≈ 1 min 30 s)

**EN**
> I want to come back to theory for a moment, because this audience cares — and rightly — about what the scores actually mean.
>
> Two industry-validated frameworks ground every score we produce. **KSA** describes *what* we assess — Knowledge, Skills, Abilities — the competency model from the US Office of Personnel Management, standard in I-O psychology and structured hiring. We adopt it for three reasons. It separates three evidence levels — recall versus execution versus capability. Each K, S, or A binds to a feature our LLM, VLM, or speech pipeline can actually detect. And recruiters already think this way, so the scores are interpretable to them. KSA drives our **professional track** — six of the ten aspects.
>
> **STAR** — Situation, Task, Action, Result — describes *how* candidates should answer. DDI introduced it in 1974, and it remains the de-facto behavioural-answer structure. Three reasons we adopt it: it gives us a **shared schema** so behavioural answers can be scored objectively; **missing parts produce concrete feedback** — no Result means unquantified impact, no Action means unclear contribution; and it's **teachable** — students adopt the same structure they're being scored against. STAR drives our **communication track** — four social aspects plus way-of-expression features.
>
> So when a student sees a score, that score is not a black box — it is **traceable to a published framework that recruiters already use.**

**中文**
> 我想花一分钟回到理论，因为我相信在座各位老师会关心——这些分数到底**意味着什么**。
>
> 我们用两个**业界验证过的框架**来支撑每一个分数。**KSA**——Knowledge / Skills / Abilities，源自美国人事管理局（US OPM），是 I-O 心理学和结构化招聘里的标准能力模型，回答的是**"我们评什么"**。我们采用它有三个理由：它把**回忆 / 执行 / 能力**这三个证据层级区分开；每一个 K/S/A 都能绑定到我们的 LLM、VLM 或语音管线能识别的特征；HR 本来就是用这套框架在思考，分数对他们就是**可解释的**。KSA 支撑我们的**专业赛道**——10 个维度里的 6 个。
>
> **STAR**——Situation / Task / Action / Result，DDI 在 1974 年提出，至今仍是行为面试题事实上的回答结构，回答的是**"学生该怎么答"**。三个理由：它给了我们一个**共同 schema**，行为题可以**客观打分**；**缺哪段就给哪段反馈**——没 Result 就指出影响没量化，没 Action 就指出贡献不清楚；而且 **STAR 本身是可教的**——学生学的就是被打分用的那套结构。STAR 支撑我们的**沟通赛道**——4 个社交维度加上表达类特征。
>
> 所以学生看到的分数**不是一个黑箱**——它**完全可以回溯到一个 HR 在用、文献也支持的框架**。

---

## Slide 14 — Journey Recap (≈ 20 s, transition slide)

> **Note for speaker**: this slide repeats Slide 5. Use it as a brief recap before the privacy slide, or skip it if time is tight.

**EN**
> Quickly recapping where we've been — Setup, Live Interview, Report — three stages, one platform. Now to the question I imagine most of you are quietly holding: *what about the data?*

**中文**
> 简单回顾一下——配置、实时面试、报告——**三个阶段，一个平台**。接下来我想正面回应一个我相信在座各位老师**心里都在想的问题**——数据怎么办？

---

## Slide 15 — Trust & Data Privacy (≈ 1 min 30 s)

**EN**
> Privacy is designed in, not bolted on. Four guarantees, top-left to bottom-right.
>
> **Network — campus only.** All raw data — video, audio, CV — stays on PolyU servers. The application is reachable **only from PolyUWLAN**. Data does not leave the campus network.
>
> **Storage — encrypted at rest.** PostgreSQL with `pg_tde` transparent encryption. If a disk is physically removed, every record on it is ciphertext.
>
> **Access control — per-user isolation.** Each candidate's video and audio sit under their own `user/timestamp` directory. JWT auth, per-route guards, rate limiting — no cross-account read.
>
> **User control — students own their data.** One-click delete erases the candidate's full history. Any research use is **de-identified and IRB-approved** — aligned with GDPR and Hong Kong's PDPO.
>
> One honest note on the roadmap. **Today**, our LLM scoring goes through DashScope and Azure under enterprise contracts that explicitly disallow training on our data. **Next**, we are migrating scoring to **on-campus models** — HKGAI or a locally hosted Qwen — so eventually even text never leaves PolyU. We're being transparent about that gap because we think you deserve to know exactly where the data flows today and where it will flow tomorrow.
>
> That brings me to the end. PolyInterview is **personalised on the Match side, multimodal on the Convince side, theoretically grounded, pilot-validated, and privacy-respecting**. I'd love to hear your questions — and especially what you'd want to see before recommending it to your own students. Thank you.

**中文**
> 隐私是**设计进来的，不是事后加的**。四条保障，从左上到右下。
>
> **网络层——仅限校园网**：所有原始数据（视频、音频、简历）只存在 PolyU 服务器上，应用**只能从 PolyUWLAN 访问**，数据不出校园网络。
>
> **存储层——静态加密**：PostgreSQL + `pg_tde` 透明加密。即使硬盘被物理拆走，**每一条记录在盘上都是密文**。
>
> **访问控制——按用户隔离**：每位候选人的视频和音频在 `user/timestamp` 目录下；JWT 鉴权、路由守卫、限流——**不存在跨账户读取**。
>
> **用户控制——数据归学生所有**：一键删除即可清除全部历史。任何科研用途都会**去标识并通过 IRB 审批**，符合 GDPR 和香港 PDPO。
>
> 路线图这里我也想坦诚一句。**当下**，我们的 LLM 打分确实走了 DashScope 和 Azure，但都是**企业合同明确禁止用我们的数据训练**的版本。**下一步**，我们要把打分迁到**校内模型**——HKGAI 或者本地 Qwen——让**连文本都不离开 PolyU**。我们把这一点讲清楚，是因为各位老师**有权知道数据现在流向哪里、未来会流向哪里**。
>
> 这就是我今天想和各位分享的全部。**PolyInterview——Match 端做个性化，Convince 端做多模态，理论有支撑，用户已验证，隐私有边界**。非常欢迎各位老师提问，也特别想听听**你们觉得我们还需要补上什么，才放心把它推荐给自己的学生**。谢谢大家。

---

## 时间核对 / Time Budget Check

| Slide | Topic | Time |
|---|---|---|
| 1 | Title | 0:30 |
| 2 | Pressure & gap **+ 🙋 audience question** | 2:15 |
| 3 | Existing-tool limitations | 1:30 |
| 4 | Match × Convince framing | 1:30 |
| 5 | Journey overview | 0:20 |
| 6 | Setup (4 parameters) | 1:00 |
| 7 | Three follow-up strategies **+ 🙋 audience question** | 1:50 |
| 8 | Embodied interaction | 1:30 |
| 9 | Three-layer architecture | 2:00 |
| 10 | Feedback & report | 1:30 |
| 11 | User testing | 1:30 |
| 12 | Welcome to experience | 0:30 |
| 13 | KSA × STAR | 1:30 |
| 14 | Journey recap (optional) | 0:20 |
| 15 | Trust & privacy + close | 1:30 |
| **Total** | | **≈ 19:15** |

剩余 ~45 秒作为页面切换与衔接缓冲（buffer for transitions / Q&A handoff）。如果 Slide 2 的举手互动比预期热烈，可省掉 Slide 14 的 recap。

---

## 演讲小贴士 / Delivery Tips

- **Pace** — 英文 140–150 wpm；中文每分钟 220–240 字。学术听众更喜欢稍慢的节奏。
- **Slide 2 数字** — 数字密集，建议读出 12.3 % / 80 % / 93 % / 242 / 2 % 时停半拍，让听众消化。
- **Slide 9** — 技术页一定要慢，不要在三层之间一气呵成；每一层讲完停半秒再进入下一层。
- **Slide 11** — 强调 PolyU 老师参与了评审（"九位 PolyU 老师 / nine PolyU faculty"），呼应今天的听众身份。
- **Slide 15** — 路线图那一段（DashScope/Azure → HKGAI/Qwen）**坦诚地讲**，不要回避；学术听众会因为透明而加分。
- **结尾** — 不要替听众回答"会不会推荐给学生"，而是**邀请他们告诉你还缺什么**——这会自然引出 Q&A。
- **互动提问的尺度** —
  - **Slide 2** 的举手提问是**真实问题**：等 2–3 秒看举手数，再笑着回应"差不多就是这个比例"——千万不要还没等举手就接下一句。
  - **Slide 7** 的提问是**修辞性的**：不要真的等老师回答"我选 David"，停顿 1–2 秒、给个微笑，立刻揭晓三个 persona——节奏感比互动本身重要。
  - 如果现场气氛偏冷或时间吃紧，**两个互动都可以缩成一句话**："凭直觉想一下，如果是你的学生，你会怎么追问？"
