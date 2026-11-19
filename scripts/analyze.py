#!/usr/bin/env python3
"""Phân tích kết quả thí nghiệm CUTOFF: bảng thống kê + đồ thị.

Chạy (từ thư mục gốc repo):  python3 scripts/analyze.py
Đầu vào : results/benchmark_results.csv   (dataset,n,cutoff,rep,time_ms)
Đầu ra  : results/summary.csv, results/summary.md, results/charts/*.png
"""
import os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = "results/benchmark_results.csv"
OUT = "results"
CH = os.path.join(OUT, "charts")
os.makedirs(CH, exist_ok=True)

df = pd.read_csv(CSV)
datasets = ["random", "sorted", "reverse", "nearly", "dups"]
sizes = sorted(df.n.unique())
cutoffs = sorted(df.cutoff.unique())

# ---------- 1. Bảng thống kê: mean, median, std, 95% CI theo (dataset, n, cutoff) ----------
def ci95(x):
    x = np.asarray(x)
    if len(x) < 2:
        return 0.0
    return stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))

g = df.groupby(["dataset", "n", "cutoff"]).time_ms
summ = g.agg(reps="count", mean="mean", median="median", std="std", min="min").reset_index()
summ["ci95"] = g.apply(ci95).values
summ["rel_to_c1"] = np.nan   # thời gian trung bình / thời gian mergesort thuần (cutoff=1)
for (d, n), sub in summ.groupby(["dataset", "n"]):
    base = sub.loc[sub.cutoff == 1, "mean"].iloc[0]
    summ.loc[sub.index, "rel_to_c1"] = sub["mean"] / base
summ.to_csv(os.path.join(OUT, "summary.csv"), index=False, float_format="%.4f")

# ---------- 2. Cutoff tốt nhất + so sánh cặp với 7 và 10 ----------
rows = []
for d in datasets:
    for n in sizes:
        sub = summ[(summ.dataset == d) & (summ.n == n)]
        best = sub.loc[sub["mean"].idxmin()]
        # nhóm cutoff "không khác biệt có ý nghĩa" so với best (paired t-test, p>=0.05)
        piv = df[(df.dataset == d) & (df.n == n)].pivot(index="rep", columns="cutoff", values="time_ms")
        ok = []
        for c in cutoffs:
            if c == best.cutoff:
                ok.append(c)
                continue
            p = stats.ttest_rel(piv[c], piv[int(best.cutoff)]).pvalue
            if p >= 0.05:
                ok.append(c)
        t7, t10 = sub[sub.cutoff == 7]["mean"].iloc[0], sub[sub.cutoff == 10]["mean"].iloc[0]
        p7_10 = stats.ttest_rel(piv[7], piv[10]).pvalue
        rows.append(dict(dataset=d, n=n, best_cutoff=int(best.cutoff), best_mean_ms=best["mean"],
                         pure_mean_ms=sub[sub.cutoff == 1]["mean"].iloc[0],
                         speedup_vs_pure=sub[sub.cutoff == 1]["mean"].iloc[0] / best["mean"],
                         mean_c7_ms=t7, mean_c10_ms=t10, p_7_vs_10=p7_10,
                         statistically_tied_with_best=" ".join(map(str, ok))))
best_df = pd.DataFrame(rows)
best_df.to_csv(os.path.join(OUT, "best_cutoff.csv"), index=False, float_format="%.4f")

# ---------- 3. Đánh giá tổng hợp: thời gian tương đối (so với best của từng nhóm) ----------
summ["rel_to_best"] = summ.groupby(["dataset", "n"])["mean"].transform(lambda s: s / s.min())
agg_all = summ.groupby("cutoff").rel_to_best.mean()
agg_big = summ[summ.n >= 100_000].groupby("cutoff").rel_to_best.mean()
agg_rand = summ[(summ.dataset == "random") & (summ.n >= 100_000)].groupby("cutoff").rel_to_best.mean()

# ---------- 4. Đồ thị ----------
plt.rcParams.update({"figure.dpi": 130, "axes.grid": True, "grid.alpha": 0.3})

# 4a. Thời gian tuyệt đối theo cutoff, mỗi N một đồ thị, mỗi dataset một đường (có CI 95%)
fig, axes = plt.subplots(1, len(sizes), figsize=(5.2 * len(sizes), 4.2))
for ax, n in zip(np.atleast_1d(axes), sizes):
    for d in datasets:
        s = summ[(summ.dataset == d) & (summ.n == n)]
        ax.errorbar(s.cutoff, s["mean"], yerr=s.ci95, marker="o", ms=3, capsize=2, label=d)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.axvline(7, color="gray", ls=":", lw=1); ax.axvline(10, color="k", ls=":", lw=1)
    ax.set_title(f"N = {n:,}"); ax.set_xlabel("CUTOFF"); ax.set_ylabel("Thời gian trung bình (ms)")
np.atleast_1d(axes)[0].legend(fontsize=8)
fig.suptitle("Thời gian mergesort theo CUTOFF (đường chấm: 7 và 10; thanh lỗi: CI 95%)")
fig.tight_layout(); fig.savefig(os.path.join(CH, "time_vs_cutoff.png")); plt.close(fig)

# 4b. Thời gian tương đối so với mergesort thuần (cutoff=1), cho thấy lợi ích của cutoff
fig, axes = plt.subplots(1, len(sizes), figsize=(5.2 * len(sizes), 4.2), sharey=True)
for ax, n in zip(np.atleast_1d(axes), sizes):
    for d in datasets:
        s = summ[(summ.dataset == d) & (summ.n == n)]
        ax.plot(s.cutoff, s.rel_to_c1, marker="o", ms=3, label=d)
    ax.axhline(1, color="gray", lw=1)
    ax.axvline(7, color="gray", ls=":", lw=1); ax.axvline(10, color="k", ls=":", lw=1)
    ax.set_xscale("log"); ax.set_title(f"N = {n:,}"); ax.set_xlabel("CUTOFF")
np.atleast_1d(axes)[0].set_ylabel("Thời gian / thời gian cutoff=1")
np.atleast_1d(axes)[0].legend(fontsize=8)
fig.suptitle("Tỉ lệ thời gian so với mergesort thuần (<1 nghĩa là nhanh hơn)")
fig.tight_layout(); fig.savefig(os.path.join(CH, "relative_to_pure.png")); plt.close(fig)

# 4c. Phóng to vùng 1..32 cho dữ liệu random, N lớn nhất + boxplot phân bố
nbig = sizes[-1]
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
s = summ[(summ.dataset == "random") & (summ.n == nbig)]
ax[0].errorbar(s.cutoff, s["mean"], yerr=s.ci95, marker="o", capsize=3)
ax[0].plot(s.cutoff, s["median"], "s--", ms=3, label="median")
ax[0].set_xlim(0, 35); ax[0].set_xlabel("CUTOFF"); ax[0].set_ylabel("ms")
ax[0].set_title(f"random, N={nbig:,}: mean ± CI95 (đường đứt: median)")
sub = df[(df.dataset == "random") & (df.n == nbig) & (df.cutoff <= 32)]
data = [sub[sub.cutoff == c].time_ms.values for c in sorted(sub.cutoff.unique())]
ax[1].boxplot(data, tick_labels=sorted(sub.cutoff.unique()), showfliers=False)
ax[1].set_xlabel("CUTOFF"); ax[1].set_ylabel("ms"); ax[1].set_title("Phân bố thời gian giữa các lần lặp")
fig.tight_layout(); fig.savefig(os.path.join(CH, "random_largest_zoom.png")); plt.close(fig)

# 4d. Mức tổng hợp: thời gian tương đối so với best trung bình theo cutoff
fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(agg_all.index, agg_all.values, "o-", ms=3, label="mọi (dataset, N)")
ax.plot(agg_big.index, agg_big.values, "s-", ms=3, label="N ≥ 10^5")
ax.plot(agg_rand.index, agg_rand.values, "^-", ms=3, label="random, N ≥ 10^5")
ax.set_xscale("log"); ax.set_xlabel("CUTOFF"); ax.set_ylabel("Thời gian / thời gian của cutoff tốt nhất (trung bình)")
ax.axvline(7, color="gray", ls=":", lw=1); ax.axvline(10, color="k", ls=":", lw=1)
ax.legend(fontsize=8); ax.set_title("Độ chậm tương đối trung bình theo CUTOFF")
fig.tight_layout(); fig.savefig(os.path.join(CH, "aggregate_relative.png")); plt.close(fig)

# 4e. Heatmap rel_to_best cho random
fig, ax = plt.subplots(figsize=(8, 3.2))
hm = summ[summ.dataset == "random"].pivot(index="n", columns="cutoff", values="rel_to_best")
im = ax.imshow(hm.values, aspect="auto", cmap="viridis_r", vmin=1, vmax=min(1.5, hm.values.max()))
ax.set_xticks(range(len(hm.columns))); ax.set_xticklabels(hm.columns, fontsize=7)
ax.set_yticks(range(len(hm.index))); ax.set_yticklabels([f"{n:,}" for n in hm.index])
ax.set_xlabel("CUTOFF"); ax.set_ylabel("N"); ax.set_title("random: thời gian / thời gian tốt nhất")
fig.colorbar(im); fig.tight_layout(); fig.savefig(os.path.join(CH, "heatmap_random.png")); plt.close(fig)

# ---------- 5. Ghi summary.md ----------
def md_table(d):
    return d.to_markdown(index=False, floatfmt=".3f")

with open(os.path.join(OUT, "summary.md"), "w", encoding="utf-8") as f:
    f.write("## Cutoff tốt nhất theo từng (dataset, N)\n\n")
    f.write(md_table(best_df.rename(columns={
        "best_mean_ms": "best (ms)", "pure_mean_ms": "cutoff=1 (ms)", "mean_c7_ms": "cutoff=7 (ms)",
        "mean_c10_ms": "cutoff=10 (ms)", "p_7_vs_10": "p(7 vs 10)",
        "statistically_tied_with_best": "cutoff không khác best (p>=0.05)"})))
    f.write("\n\n## Độ chậm tương đối trung bình so với cutoff tốt nhất (1.000 = tốt nhất)\n\n")
    t = pd.DataFrame({"mọi nhóm": agg_all, "N>=1e5": agg_big, "random N>=1e5": agg_rand}).reset_index()
    f.write(md_table(t))
    f.write("\n\n## Thống kê chi tiết: random\n\n")
    for n in sizes:
        s = summ[(summ.dataset == "random") & (summ.n == n)][
            ["cutoff", "reps", "mean", "median", "std", "ci95", "rel_to_c1"]]
        f.write(f"### N = {n:,}\n\n{md_table(s)}\n\n")

print(best_df.to_string(index=False))
print("\nAggregate relative slowdown (random, N>=1e5), top 6:")
print(agg_rand.sort_values().head(6).to_string())
print("\nAggregate (all groups), top 6:")
print(agg_all.sort_values().head(6).to_string())
