"""
src/eda.py
─────────────────────────────────────────────
Exploratory Data Analysis (EDA) for the
Disease Prediction System.

Generates:
  • Summary statistics
  • Disease distribution plot
  • Correlation heatmap
  • Top symptom frequency chart
  • Symptom co-occurrence heatmap
  • Insights report (text)
─────────────────────────────────────────────
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")           # non-interactive backend for servers
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

from src.logger import get_logger

warnings.filterwarnings("ignore")
logger = get_logger(__name__)

# ── Aesthetic palette ──────────────────────────────────────────────────────────
PALETTE = {
    "primary":   "#1A73E8",
    "secondary": "#34A853",
    "accent":    "#EA4335",
    "warn":      "#FBBC04",
    "bg":        "#F8F9FA",
    "text":      "#202124",
}
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)


class EDAAnalyzer:
    """
    Runs all EDA steps and saves plots to disk.

    Usage:
        eda = EDAAnalyzer(df, output_dir="notebooks/eda_plots")
        eda.run_all()
    """

    def __init__(self, df: pd.DataFrame, target_col: str = "Disease",
                 output_dir: str = "notebooks/eda_plots"):
        self.df = df.copy()
        self.target_col = target_col
        self.output_dir = output_dir
        self.symptom_cols = [c for c in df.columns if c != target_col]
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"EDAAnalyzer initialized | output → {output_dir}")

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _save(self, fig: plt.Figure, filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        logger.info(f"Plot saved: {path}")
        return path

    # ── 1. Summary Statistics ──────────────────────────────────────────────────

    def summary_statistics(self) -> dict:
        """
        Computes and logs dataset summary statistics.

        Returns:
            dict with keys: shape, n_classes, class_counts,
                            n_features, missing_pct, symptom_prevalence
        """
        logger.info("── Summary Statistics ──")

        stats = {
            "shape":         self.df.shape,
            "n_classes":     self.df[self.target_col].nunique(),
            "class_counts":  self.df[self.target_col].value_counts().to_dict(),
            "n_features":    len(self.symptom_cols),
            "missing_pct":   self.df.isnull().mean().mean() * 100,
            "symptom_prevalence": self.df[self.symptom_cols].mean().sort_values(ascending=False),
        }

        logger.info(f"Dataset shape      : {stats['shape']}")
        logger.info(f"Number of diseases : {stats['n_classes']}")
        logger.info(f"Number of symptoms : {stats['n_features']}")
        logger.info(f"Missing values %   : {stats['missing_pct']:.2f}%")
        logger.info(f"Avg symptom prevalence: "
                    f"{stats['symptom_prevalence'].mean() * 100:.1f}%")

        return stats

    # ── 2. Disease Distribution ────────────────────────────────────────────────

    def plot_disease_distribution(self) -> str:
        """Bar chart of sample counts per disease."""
        logger.info("Plotting disease distribution …")

        counts = self.df[self.target_col].value_counts()
        n = len(counts)
        cmap = plt.cm.get_cmap("tab20", n)
        colors = [cmap(i) for i in range(n)]

        fig, ax = plt.subplots(figsize=(14, max(6, n * 0.35)))
        bars = ax.barh(counts.index, counts.values, color=colors, edgecolor="white")

        for bar, val in zip(bars, counts.values):
            ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
                    str(val), va="center", fontsize=9, color=PALETTE["text"])

        ax.set_title("Disease Distribution", fontsize=16, fontweight="bold",
                     color=PALETTE["text"], pad=15)
        ax.set_xlabel("Number of Samples", fontsize=12)
        ax.set_ylabel("Disease", fontsize=12)
        ax.invert_yaxis()
        fig.tight_layout()

        return self._save(fig, "01_disease_distribution.png")

    # ── 3. Top Symptom Frequency ───────────────────────────────────────────────

    def plot_symptom_frequency(self, top_n: int = 25) -> str:
        """Bar chart of the most frequent symptoms across all patients."""
        logger.info(f"Plotting top {top_n} symptom frequencies …")

        freq = self.df[self.symptom_cols].sum().sort_values(ascending=False).head(top_n)

        fig, ax = plt.subplots(figsize=(13, 6))
        bars = ax.bar(range(top_n), freq.values,
                      color=PALETTE["primary"], alpha=0.85, edgecolor="white")

        ax.set_xticks(range(top_n))
        ax.set_xticklabels(freq.index, rotation=45, ha="right", fontsize=9)
        ax.set_title(f"Top {top_n} Most Frequent Symptoms",
                     fontsize=15, fontweight="bold", color=PALETTE["text"])
        ax.set_ylabel("Frequency (# patients)", fontsize=11)

        # Annotate bars
        for bar, val in zip(bars, freq.values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                    str(int(val)), ha="center", va="bottom", fontsize=8)

        fig.tight_layout()
        return self._save(fig, "02_symptom_frequency.png")

    # ── 4. Correlation Heatmap (top symptoms) ─────────────────────────────────

    def plot_correlation_heatmap(self, top_n: int = 30) -> str:
        """Heatmap of symptom–symptom correlations for top-N frequent symptoms."""
        logger.info(f"Plotting correlation heatmap (top {top_n} symptoms) …")

        top_symptoms = (
            self.df[self.symptom_cols]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .index
        )
        corr = self.df[top_symptoms].corr()

        fig, ax = plt.subplots(figsize=(14, 11))
        mask = np.triu(np.ones_like(corr, dtype=bool))  # upper triangle
        cmap = sns.diverging_palette(220, 20, as_cmap=True)

        sns.heatmap(
            corr, mask=mask, cmap=cmap,
            center=0, vmin=-1, vmax=1,
            square=True, linewidths=0.4,
            annot=False, ax=ax,
            cbar_kws={"shrink": 0.8, "label": "Pearson Correlation"},
        )
        ax.set_title(f"Symptom Correlation Heatmap (Top {top_n})",
                     fontsize=15, fontweight="bold", pad=12)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
        fig.tight_layout()
        return self._save(fig, "03_correlation_heatmap.png")

    # ── 5. Symptoms per Disease (heatmap) ─────────────────────────────────────

    def plot_disease_symptom_heatmap(self, top_symptoms: int = 20) -> str:
        """
        Heatmap showing mean symptom activation per disease.
        Rows = diseases, Columns = top symptoms.
        """
        logger.info("Plotting disease–symptom profile heatmap …")

        # Pick top symptoms by overall frequency
        top_cols = (
            self.df[self.symptom_cols]
            .sum()
            .sort_values(ascending=False)
            .head(top_symptoms)
            .index
        )
        pivot = self.df.groupby(self.target_col)[top_cols].mean()

        fig, ax = plt.subplots(figsize=(16, max(8, len(pivot) * 0.35)))
        sns.heatmap(
            pivot, cmap="YlOrRd",
            linewidths=0.3, linecolor="white",
            annot=False, ax=ax,
            cbar_kws={"shrink": 0.6, "label": "Mean Symptom Presence"},
        )
        ax.set_title("Disease–Symptom Profile Heatmap",
                     fontsize=15, fontweight="bold", pad=12)
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=9)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9)
        fig.tight_layout()
        return self._save(fig, "04_disease_symptom_heatmap.png")

    # ── 6. Class Balance ──────────────────────────────────────────────────────

    def plot_class_balance(self) -> str:
        """Pie / donut chart of class balance."""
        logger.info("Plotting class balance …")

        counts = self.df[self.target_col].value_counts()
        is_balanced = counts.std() / counts.mean() < 0.15

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # ── Left: donut ──
        pie_result = ax1.pie(
            counts.values,
            labels=None,
            autopct="%1.1f%%" if len(counts) <= 10 else None,
            startangle=140,
            pctdistance=0.82,
            wedgeprops=dict(width=0.5, edgecolor="white"),
        )
        wedges = pie_result[0]
        ax1.set_title("Class Distribution (Donut)", fontweight="bold")
        balance_label = "✓ Balanced" if is_balanced else "⚠ Imbalanced"
        ax1.text(0, -1.3, balance_label, ha="center", fontsize=12,
                 color=PALETTE["secondary"] if is_balanced else PALETTE["accent"])

        # ── Right: sorted bar ──
        colors2 = plt.cm.tab20(np.linspace(0, 1, len(counts)))
        ax2.bar(range(len(counts)), sorted(counts.values, reverse=True),
                color=colors2, edgecolor="white")
        ax2.axhline(counts.mean(), color=PALETTE["accent"], linestyle="--",
                    linewidth=1.5, label=f"Mean ({int(counts.mean())})")
        ax2.set_title("Samples per Disease (sorted)", fontweight="bold")
        ax2.set_xlabel("Disease (sorted by count)")
        ax2.set_ylabel("Count")
        ax2.legend()

        fig.suptitle("Class Balance Analysis", fontsize=16, fontweight="bold", y=1.01)
        fig.tight_layout()
        return self._save(fig, "05_class_balance.png")

    # ── 7. Symptom Co-occurrence ───────────────────────────────────────────────

    def plot_symptom_cooccurrence(self, top_n: int = 20) -> str:
        """
        Heatmap of symptom co-occurrence counts (how often
        two symptoms appear together in the same patient).
        """
        logger.info("Plotting symptom co-occurrence …")

        top_cols = (
            self.df[self.symptom_cols]
            .sum()
            .sort_values(ascending=False)
            .head(top_n)
            .index
        )
        sub = self.df[top_cols].values
        cooc = sub.T @ sub  # shape (top_n, top_n)
        cooc_arr = cooc.copy()
        np.fill_diagonal(cooc_arr, 0)          # remove self-cooccurrence
        cooc_df = pd.DataFrame(cooc_arr, index=top_cols, columns=top_cols)

        fig, ax = plt.subplots(figsize=(13, 10))
        sns.heatmap(cooc_df, cmap="Blues", ax=ax, linewidths=0.3,
                    cbar_kws={"label": "Co-occurrence Count"})
        ax.set_title(f"Symptom Co-occurrence (Top {top_n})",
                     fontsize=14, fontweight="bold")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
        fig.tight_layout()
        return self._save(fig, "06_symptom_cooccurrence.png")

    # ── 8. EDA Insights ──────────────────────────────────────────────────────

    def generate_insights(self, stats: dict) -> list[str]:
        """
        Derives human-readable insights from computed statistics.

        Args:
            stats (dict): Output of summary_statistics().

        Returns:
            list[str]: List of insight strings.
        """
        insights = []
        prevalence = stats["symptom_prevalence"]
        class_counts = pd.Series(stats["class_counts"])

        # 1. Dataset balance
        cv = class_counts.std() / class_counts.mean()
        if cv < 0.15:
            insights.append(
                "✅ Dataset is well-balanced across disease classes "
                f"(CV={cv:.2f}), which should prevent class-bias in models."
            )
        else:
            insights.append(
                f"⚠️  Dataset shows class imbalance (CV={cv:.2f}). "
                "Consider oversampling (SMOTE) or class-weight adjustments."
            )

        # 2. Most common symptom
        top_sym = prevalence.index[0]
        top_pct = prevalence.iloc[0] * 100
        insights.append(
            f"🔥 The most prevalent symptom is '{top_sym}' "
            f"appearing in {top_pct:.1f}% of all patients."
        )

        # 3. Rare symptoms
        rare = (prevalence < 0.03).sum()
        insights.append(
            f"📉 {rare} symptoms appear in <3% of patients — "
            "they may have limited predictive value and could be candidates for removal."
        )

        # 4. Disease complexity
        insights.append(
            f"📊 The dataset contains {stats['n_classes']} unique diseases "
            f"and {stats['n_features']} binary symptom features — "
            "a moderate-complexity multi-class classification problem."
        )

        # 5. Missing values
        if stats["missing_pct"] < 0.5:
            insights.append(
                f"✅ Missing value rate is very low ({stats['missing_pct']:.2f}%), "
                "requiring minimal imputation effort."
            )

        # 6. Feature type
        insights.append(
            "💡 All features are binary (0/1 symptom indicators). "
            "Tree-based models (Random Forest, XGBoost) often excel on binary feature spaces."
        )

        for i, ins in enumerate(insights, 1):
            logger.info(f"Insight {i}: {ins}")

        return insights

    # ── Master runner ─────────────────────────────────────────────────────────

    def run_all(self) -> dict:
        """
        Runs the full EDA pipeline and returns all artefacts.

        Returns:
            dict with keys: stats, insights, plot_paths
        """
        logger.info("═" * 50)
        logger.info("Starting full EDA pipeline …")
        logger.info("═" * 50)

        stats    = self.summary_statistics()
        insights = self.generate_insights(stats)

        plot_paths = {
            "disease_distribution":   self.plot_disease_distribution(),
            "symptom_frequency":      self.plot_symptom_frequency(),
            "correlation_heatmap":    self.plot_correlation_heatmap(),
            "disease_symptom_heatmap":self.plot_disease_symptom_heatmap(),
            "class_balance":          self.plot_class_balance(),
            "symptom_cooccurrence":   self.plot_symptom_cooccurrence(),
        }

        logger.info("✅ EDA pipeline complete — all plots saved")
        return {"stats": stats, "insights": insights, "plot_paths": plot_paths}


# ── Standalone run ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    from src.data_generator import generate_dataset

    raw_path = "data/raw/disease_dataset.csv"
    if not os.path.exists(raw_path):
        generate_dataset(save_path=raw_path)

    df = pd.read_csv(raw_path)
    eda = EDAAnalyzer(df, output_dir="notebooks/eda_plots")
    results = eda.run_all()

    print("\n── EDA Insights ──")
    for insight in results["insights"]:
        print(insight)
