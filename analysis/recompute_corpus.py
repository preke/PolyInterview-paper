#!/usr/bin/env python3
"""PolyInterview corpus recompute: cleaning, per-session manifest, per-feature
means (with/without failed VLM evals), nonverbal-failure decomposition, and
cross-modality correlations. Reads only local files; nothing leaves the machine.
Outputs: analysis/manifest_clean.csv, analysis/corpus_stats.json
"""
import json, glob, os, csv, wave, statistics as st
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS = os.path.join(ROOT, "users")

# 39 test/seed/junk/self-test accounts (documented rule-based exclusion; from dashboard)
REMOVED = set("5865 5899 5890 5951 7 5879 5841 5883 5877 5870 5884 6 1 8 5885 5871 "
              "5876 5882 5840 5878 5861 5893 5923 5936 5889 5842 5845 5873 5887 5880 "
              "5874 5875 5881 5886 5844 5888 5843 2 5".split())

TEXT_PROF = ["conceptual_accuracy","terminology_usage","problem_solving_logic_chain"]
TEXT_EXPR = ["structural_clarity","coherence","word_usage_pattern"]
VIDEO     = ["eye_contact","facial_expression","body_posture","gesture"]
AUDIO     = ["accuracy","prosody","fluency"]
TEXT = TEXT_PROF + TEXT_EXPR
ALLFEAT = TEXT + VIDEO + AUDIO
MOD = {**{f:"text" for f in TEXT}, **{f:"video" for f in VIDEO}, **{f:"audio" for f in AUDIO}}

def wav_dur(p):
    try:
        with wave.open(p,'rb') as w:
            return w.getnframes()/float(w.getframerate() or 1)
    except Exception:
        return None

def getscore(d):
    if isinstance(d,dict) and "score" in d:
        try: return float(d["score"])
        except: return None
    return None

all_users = sorted([d for d in os.listdir(USERS) if os.path.isdir(os.path.join(USERS,d))])
clean_users = [u for u in all_users if u not in REMOVED]

rows=[]
# per-question records for correlation / pooled means
q_records=[]   # dict feat->score (+meta) per evaluated question
nv_total_q=0; nv_failed_q=0; nv_novideo_q=0; nv_ok_q=0

for u in clean_users:
    udir=os.path.join(USERS,u)
    for sess in sorted(os.listdir(udir)):
        sdir=os.path.join(udir,sess)
        if not os.path.isdir(sdir): continue
        log=os.path.join(sdir,"interview_log.json")
        if not os.path.exists(log): continue
        try: L=json.load(open(log))
        except: continue
        status=L.get("status","")
        position=L.get("position_name","")
        style=L.get("interview_style","")
        # recordings
        vdir=os.path.join(sdir,"video"); adir=os.path.join(sdir,"audio")
        webm=len(glob.glob(os.path.join(vdir,"*.webm"))) if os.path.isdir(vdir) else 0
        mp4 =len(glob.glob(os.path.join(vdir,"*.mp4")))  if os.path.isdir(vdir) else 0
        wavs=glob.glob(os.path.join(adir,"*.wav")) if os.path.isdir(adir) else []
        durs=[d for d in (wav_dur(p) for p in wavs) if d]
        tot_dur=sum(durs) if durs else 0.0
        # answers in log
        qs=L.get("questions",[]) or []
        n_q=len(qs)
        n_answered=sum(1 for q in qs if (q.get("answer") or "").strip())
        # evaluation file
        evs=sorted(glob.glob(os.path.join(sdir,"evaluations","*.json")), key=os.path.getsize, reverse=True)
        feat_vals=defaultdict(list)
        per_q_scores=[]; nv_fail_this=0; nv_novid_this=0; nv_ok_this=0; n_eval_q=0
        if evs:
            try: E=json.load(open(evs[0]))
            except: E={}
            for q in E.get("evaluations",[]) or []:
                r=q.get("result",{}) or {}
                ac=r.get("assessment_criteria",{}) or {}
                qscore=getscore({"score":r.get("score")}) if "score" in r else None
                # collect features
                rec={"user":u,"session":sess,"category":q.get("category","")}
                got_any=False
                for grp,feats in [("professional_performance",TEXT_PROF),("way_of_expression",TEXT_EXPR),
                                  ("nonverbal",VIDEO),("oral_expression",AUDIO)]:
                    g=ac.get(grp,{}) or {}
                    for f in feats:
                        s=getscore(g.get(f,{}))
                        if s is not None:
                            rec[f]=s; got_any=True
                # nonverbal failure classification
                nvg=ac.get("nonverbal",{}) or {}
                tv=nvg.get("total_videos", r.get("nonverbal",{}).get("total_videos") if isinstance(r.get("nonverbal"),dict) else None)
                nve=nvg.get("num_videos_evaluated")
                just=" ".join(str((nvg.get(f,{}) or {}).get("justification","")) for f in VIDEO)
                failed = ("Evaluation failed" in just) or (isinstance(nve,int) and nve==0 and (tv or 0)>0)
                novideo = (tv in (0,None)) and not failed and all(rec.get(f,0)==0 for f in VIDEO)
                if any(f in rec for f in VIDEO) or tv:
                    nv_total_q+=1
                    if failed: nv_failed_q+=1; nv_fail_this+=1; rec["nv_failed"]=1
                    elif novideo: nv_novideo_q+=1; nv_novid_this+=1; rec["nv_failed"]=0; rec["nv_novideo"]=1
                    else: nv_ok_q+=1; nv_ok_this+=1; rec["nv_failed"]=0
                if got_any:
                    n_eval_q+=1
                    if qscore is not None: per_q_scores.append(qscore)
                    for f in ALLFEAT:
                        if f in rec: feat_vals[f].append(rec[f])
                    q_records.append(rec)
        sess_feat_means={f:(sum(v)/len(v) if v else None) for f,v in feat_vals.items()}
        overall=(sum(per_q_scores)/len(per_q_scores)) if per_q_scores else None
        rows.append({
            "user":u,"session_id":sess,"status":status,"position":position,"style":style,
            "n_questions":n_q,"n_answered":n_answered,"n_eval_questions":n_eval_q,
            "overall_score":round(overall,3) if overall is not None else "",
            "n_webm":webm,"n_mp4":mp4,"n_wav":len(wavs),
            "total_dur_sec":round(tot_dur,1),
            "nv_failed_q":nv_fail_this,"nv_ok_q":nv_ok_this,"nv_novideo_q":nv_novid_this,
            **{f"feat_{f}":(round(sess_feat_means[f],3) if sess_feat_means.get(f) is not None else "") for f in ALLFEAT},
        })

# ---- dataset aggregates ----
def pooled_mean(feat, records, cond=None):
    vals=[r[feat] for r in records if feat in r and (cond is None or cond(r))]
    return (sum(vals)/len(vals), len(vals)) if vals else (None,0)

evaluated_sessions=[r for r in rows if r["n_eval_questions"]>0]
print(f"all user dirs: {len(all_users)} | removed: {len(REMOVED)} | clean users: {len(clean_users)}")
print(f"clean sessions (have interview_log): {len(rows)} | evaluated sessions (>=1 scored q): {len(evaluated_sessions)}")
print(f"clean recordings: wav={sum(r['n_wav'] for r in rows)} webm={sum(r['n_webm'] for r in rows)} mp4={sum(r['n_mp4'] for r in rows)}")
print(f"pooled evaluated questions: {len(q_records)}")
print()
print("=== Nonverbal (video) evaluation outcome decomposition (per question) ===")
print(f"  total nonverbal-relevant questions: {nv_total_q}")
print(f"  VLM FAILED (recorded as 0): {nv_failed_q}  ({100*nv_failed_q/max(nv_total_q,1):.1f}%)")
print(f"  no video recorded:          {nv_novideo_q} ({100*nv_novideo_q/max(nv_total_q,1):.1f}%)")
print(f"  VLM succeeded (genuine):    {nv_ok_q}      ({100*nv_ok_q/max(nv_total_q,1):.1f}%)")
print()
print("=== Per-feature pooled means: ALL evaluated questions vs. GENUINE-only (video excl. failed) ===")
print(f"{'feature':28s}{'mod':6s}{'mean_all':>10s}{'n_all':>7s}{'mean_genuine':>14s}{'n_gen':>7s}")
agg={}
for f in ALLFEAT:
    mall,nall=pooled_mean(f,q_records)
    if f in VIDEO:
        mgen,ngen=pooled_mean(f,q_records,cond=lambda r: not r.get("nv_failed"))
    else:
        mgen,ngen=mall,nall
    agg[f]={"mod":MOD[f],"mean_all":mall,"n_all":nall,"mean_genuine":mgen,"n_genuine":ngen}
    print(f"{f:28s}{MOD[f]:6s}{(f'{mall:.2f}' if mall is not None else '-'):>10s}{nall:>7d}"
          f"{(f'{mgen:.2f}' if mgen is not None else '-'):>14s}{ngen:>7d}")

# modality-level means
def mod_mean(mods, key):
    vs=[agg[f][key] for f in ALLFEAT if MOD[f] in mods and agg[f][key] is not None]
    return sum(vs)/len(vs) if vs else None
print()
print("=== Modality-level means (avg of features) ===")
for mlabel,mset in [("text",{"text"}),("audio",{"audio"}),("video",{"video"})]:
    print(f"  {mlabel:6s} all={mod_mean(mset,'mean_all'):.2f}  genuine={mod_mean(mset,'mean_genuine'):.2f}")

# ---- correlations across modalities (session-level, evaluated sessions) ----
def corr(xs,ys):
    pts=[(x,y) for x,y in zip(xs,ys) if isinstance(x,(int,float)) and isinstance(y,(int,float))]
    if len(pts)<3: return None,len(pts)
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    num=sum((x-mx)*(y-my) for x,y in pts)
    dx=sum((x-mx)**2 for x in xs)**.5; dy=sum((y-my)**2 for y in ys)**.5
    return (num/(dx*dy) if dx and dy else None), len(pts)

def sess_mod(r, feats):
    vs=[r[f"feat_{f}"] for f in feats if r.get(f"feat_{f}") not in ("",None)]
    return sum(vs)/len(vs) if vs else None

text_s=[sess_mod(r,TEXT) for r in evaluated_sessions]
audio_s=[sess_mod(r,AUDIO) for r in evaluated_sessions]
video_s=[sess_mod(r,VIDEO) for r in evaluated_sessions]
print()
print("=== Cross-modality correlations (session-level, evaluated sessions, incl. zeros) ===")
for a,b,an,bn in [(text_s,audio_s,"text","audio"),(text_s,video_s,"text","video"),(audio_s,video_s,"audio","video")]:
    c,n=corr(a,b); print(f"  {an}-{bn}: r={c:.3f} (n={n})" if c is not None else f"  {an}-{bn}: n/a")

# overall score stats (evaluated, nonzero)
ov=[r["overall_score"] for r in evaluated_sessions if isinstance(r["overall_score"],(int,float))]
ovnz=[x for x in ov if x>0]
print()
print(f"=== Overall score (per-session mean of per-question scores) ===")
print(f"  evaluated sessions with overall: {len(ov)} | nonzero: {len(ovnz)}")
if ov: print(f"  mean(all)={sum(ov)/len(ov):.2f}  mean(nonzero)={ (sum(ovnz)/len(ovnz)) if ovnz else 0:.2f}  max={max(ov):.2f}")

# ---- write outputs ----
os.makedirs(os.path.join(ROOT,"analysis"),exist_ok=True)
mf=os.path.join(ROOT,"analysis","manifest_clean.csv")
cols=["user","session_id","status","position","style","n_questions","n_answered","n_eval_questions",
      "overall_score","n_webm","n_mp4","n_wav","total_dur_sec","nv_failed_q","nv_ok_q","nv_novideo_q"]+[f"feat_{f}" for f in ALLFEAT]
with open(mf,"w",newline="") as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader()
    for r in rows: w.writerow(r)
stats={
  "meta":{"users_all":len(all_users),"users_removed":len(REMOVED),"users_clean":len(clean_users),
          "sessions_clean":len(rows),"sessions_evaluated":len(evaluated_sessions),
          "recordings_clean":{"wav":sum(r['n_wav'] for r in rows),"webm":sum(r['n_webm'] for r in rows),"mp4":sum(r['n_mp4'] for r in rows)},
          "pooled_eval_questions":len(q_records)},
  "nonverbal_outcome":{"total":nv_total_q,"vlm_failed":nv_failed_q,"no_video":nv_novideo_q,"vlm_ok":nv_ok_q},
  "features":agg,
  "modality_means":{m:{"all":mod_mean({m},'mean_all'),"genuine":mod_mean({m},'mean_genuine')} for m in ["text","audio","video"]},
  "overall":{"n":len(ov),"nonzero":len(ovnz),"mean_all":(sum(ov)/len(ov) if ov else None),
             "mean_nonzero":((sum(ovnz)/len(ovnz)) if ovnz else None),"max":(max(ov) if ov else None)},
}
json.dump(stats,open(os.path.join(ROOT,"analysis","corpus_stats.json"),"w"),indent=2)
print("\nWROTE analysis/manifest_clean.csv and analysis/corpus_stats.json")
