#!/usr/bin/env python3
"""Generate publication figures + tables for the PolyInterview demo paper
from the all-account review snapshot. Outputs to paper/figures/."""
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG=os.path.join(ROOT,"paper","figures"); os.makedirs(FIG,exist_ok=True)
S=json.load(open(os.path.join(ROOT,"analysis","corpus_stats_all.json")))

plt.rcParams.update({
    "font.family":"serif","font.serif":["Times New Roman","DejaVu Serif"],
    "font.size":8,"axes.linewidth":0.8,"savefig.bbox":"tight","savefig.pad_inches":0.02,
    "axes.spines.top":False,"axes.spines.right":False,"pdf.fonttype":42,"ps.fonttype":42,
})
C_TEXT="#3B6FB6"; C_AUDIO="#2BA88B"; C_VIDEO="#E1813A"; INK="#222633"; MUT="#8a93a6"
REVIEW_RED="#C00000"

# ---------- Figure A: deployment scale ----------
m=S["meta"]; u=S["usage_evidence"]
fig,ax=plt.subplots(figsize=(3.3,1.35)); ax.set_xlim(0,4); ax.set_ylim(0,1); ax.axis("off")
metrics=[("Accounts",m["users"]),("Sessions",m["sessions"]),
         ("Questions",m["questions"]),("Scored answers",m["pooled_scored_answers"])]
for index,(label,value) in enumerate(metrics):
    ax.add_patch(FancyBboxPatch((index+0.05,0.18),0.9,0.62,
                 boxstyle="round,pad=0.02,rounding_size=0.04",
                 fc="#F7F8FA",ec="#D9DEE7",lw=0.8))
    ax.text(index+0.5,0.56,f"{value:,}",ha="center",va="center",
            fontsize=12,color=REVIEW_RED,fontweight="bold")
    ax.text(index+0.5,0.31,label,ha="center",va="center",fontsize=6.5,color=REVIEW_RED)
ax.set_title("All-account deployment scale (statistics under verification)",fontsize=7,color=REVIEW_RED,pad=2)
fig.savefig(os.path.join(FIG,"fig_deployment_summary.pdf")); plt.close(fig)
print("wrote fig_deployment_summary.pdf")

# ---------- Figure B: positive workflow and personalization evidence ----------
alignment=u["role_alignment"]
coverage=[
    ("Five-stage question sets",100*u["complete_five_stage_sessions"]/m["sessions"]),
    ("Matched JD > cross-role baseline",100*alignment["win_rate"]),
    ("Matched JD ranks first",100*alignment["rank_one_rate"]),
    ("Returning accounts",100*m["returning_users"]/m["users"]),
]
fig,ax=plt.subplots(figsize=(3.3,1.75))
y=np.arange(len(coverage))[::-1]
ax.barh(y,[value for _,value in coverage],color=[C_TEXT,C_AUDIO,C_VIDEO,"#6C78A8"],height=0.56)
for yi,(_,value) in zip(y,coverage):
    ax.text(value+1.2,yi,f"{value:.1f}%",ha="left",va="center",fontsize=7,color=REVIEW_RED,fontweight="bold")
ax.set_yticks(y); ax.set_yticklabels([label for label,_ in coverage],fontsize=6.5,color=REVIEW_RED)
ax.set_xlim(0,105); ax.set_xlabel("Share of the corresponding all-account sample",fontsize=6.5,color=REVIEW_RED)
ax.tick_params(axis="x",labelsize=6,colors=REVIEW_RED)
ax.set_title("Workflow coverage and role-conditioned question evidence",fontsize=7,color=REVIEW_RED)
fig.savefig(os.path.join(FIG,"fig_deployment_evidence.pdf")); plt.close(fig)
print("wrote fig_deployment_evidence.pdf")

# ---------- Figure C: three-layer architecture ----------
fig,ax=plt.subplots(figsize=(6.6,2.95)); ax.set_xlim(0,100); ax.set_ylim(0,100); ax.axis("off")
def box(x,y,w,h,text,fc,ec,fs=7.0,tc=INK,bold=False,r=0.06):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0.4,rounding_size={r*100}",
                 fc=fc,ec=ec,lw=1.0,mutation_scale=1,zorder=3))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",fontsize=fs,color=tc,zorder=4,
            fontweight="bold" if bold else "normal",linespacing=1.15)
def arrow(x1,y1,x2,y2,col=MUT,lw=0.9):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=7,color=col,lw=lw,zorder=2))
# column headers
for x,t in [(11,"Multimodal input"),(36,"Layer 1 · Features (13)"),(73,"Layer 2 · Aspects (10)"),(93.5,"Layer 3 · Proficiency")]:
    ax.text(x,97.5,t,ha="center",fontsize=7.0,color="#0F5FD7",fontweight="bold")
# inputs
ins=[("Text\n(transcript)",C_TEXT),("Audio\n(speech)",C_AUDIO),("Video\n(frames)",C_VIDEO)]
for i,(t,c) in enumerate(ins):
    box(3,68-i*24,16,16,t,"white",c,7.0,c,bold=True)
# layer1 agents
agents=[("Professional\nPerformance (LLM)",C_TEXT),("Way of\nExpression (LLM)",C_TEXT),
        ("Oral Expression\n(Audio)",C_AUDIO),("Non-verbal\nBehaviour (VLM)",C_VIDEO)]
ay=[78,58,34,10]
for (t,c),yy in zip(agents,ay):
    box(26,yy,20,15,t,"#F4F8FF",c,6.4,INK)
# arrows input->agents
arrow(19,76,26,85.5,C_TEXT); arrow(19,76,26,65.5,C_TEXT)
arrow(19,52,26,41.5,C_AUDIO); arrow(19,28,26,17.5,C_VIDEO)
# features summary box
box(50,30,8,46,"13\nfeatures\n(0–10)","#EEF1F6","#9aa3b2",6.4,INK,bold=True)
for yy in ay: arrow(46,yy+7.5,50,53,"#cfd6e0",0.7)
# layer2 aspects (3 groups)
groups=[("Cognitive\n· gen. intelligence\n· applied mental\n· creativity","#EAF2FB",C_TEXT,70),
        ("Background\n· job knowledge\n· education\n· experience","#EAF7F2",C_AUDIO,43),
        ("Social\n· communication · interpersonal\n· leadership · persuasiveness","#FCEFE6",C_VIDEO,14)]
for t,fc,ec,yy in groups:
    box(60,yy,26,20,t,fc,ec,5.9,INK)
arrow(58,53,60,80); arrow(58,53,60,53); arrow(58,53,60,24)
# layer3 competencies
box(89,62,9,22,"Professional\nCompetency","#EAF2FB",C_TEXT,6.3,INK,bold=True)
box(89,30,9,22,"Communication\nCompetency","#FCEFE6",C_VIDEO,6.3,INK,bold=True)
arrow(86,80,89,77); arrow(86,53,89,69)   # cognitive+background -> professional
arrow(86,24,89,41)                          # social -> communication
box(89,4,9,16,"Overall =\nmean","#FFF7E6","#E1A93A",6.3,INK,bold=True)
arrow(93.5,62,93.5,20.5,"#E1A93A",0.9); arrow(93.5,30,93.5,20.5,"#E1A93A",0.9)
ax.text(50,2.0,"Question-type gating: only aspects relevant to each question type are scored · every score traces feature→aspect→competency",
        ha="center",fontsize=5.7,color=MUT,style="italic")
fig.savefig(os.path.join(FIG,"fig_arch.pdf")); plt.close(fig)
print("wrote fig_arch.pdf")

# ---------- Table: all-account deployment snapshot ----------
m=S["meta"]; u=S["usage_evidence"]; rec=m["recordings"]
tex=r"""\begin{table}[t]\centering\small
{\color{red}
\begin{tabular}{@{}p{0.67\linewidth}r@{}}
\toprule
\textbf{Statistic} & \textbf{Snapshot} \\
\midrule
Accounts & %d \\
Returning accounts & %d \\
Sessions & %s \\
Generated questions & %s \\
Completed sessions & %d \\
Five-stage question sets & %s \\
Distinct position titles & %d \\
Answered question records & %s \\
Recorded follow-up turns & %d \\
Pooled scored answers & %s \\
Audio/video files (wav/webm) & %s / %s \\
\bottomrule
\end{tabular}
\caption{All-account deployment snapshot used for the statistics under review. It includes accounts previously labeled as test, internal-seed, placeholder, or team accounts; the totals therefore describe system activity rather than verified external candidates.}
\label{tab:deploy}
}
\end{table}
""" % (m["users"], m["returning_users"], f"{m['sessions']:,}".replace(",", "{,}"),
       f"{m['questions']:,}".replace(",", "{,}"), m["statuses"]["completed"],
       f"{u['complete_five_stage_sessions']:,}".replace(",", "{,}"),
       u["distinct_position_titles"],
       f"{u['answered_question_records']:,}".replace(",", "{,}"),
       u["recorded_followup_turns"],
       f"{m['pooled_scored_answers']:,}".replace(",", "{,}"),
       f"{rec['wav']:,}".replace(",", "{,}"), f"{rec['webm']:,}".replace(",", "{,}"))
open(os.path.join(FIG,"table_deploy.tex"),"w").write(tex)
print("wrote table_deploy.tex")
print("DONE")
