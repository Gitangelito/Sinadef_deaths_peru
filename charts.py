# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# -------------------------
# LOAD
# -------------------------
df = pd.read_csv("dashboard_data.csv")
df = df[df['CATEGORY'] == 'BY_AGE'].copy()
df['GROUP'] = df['GROUP'].astype(str)

# Clean cause names to title case
df['CAUSE'] = df['CAUSE'].str.strip().str.title()

years = sorted(df['YEAR'].unique())
age_groups = ['0-10','11-20','21-30','31-40','41-50','51-60','61-70','71-80','81-90','90+']

palette = sns.color_palette("Set2", 5)

pdf_path = "deaths_report.pdf"
with pdf_backend.PdfPages(pdf_path) as pdf:

    # -------------------------
    # COVER PAGE
    # -------------------------
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    fig.patch.set_facecolor('#1a1a2e')
    ax.text(0.5, 0.65, 'Peru Deaths Report', fontsize=36, fontweight='bold',
            ha='center', va='center', color='white', transform=ax.transAxes)
    ax.text(0.5, 0.52, 'Top 5 Causes of Death by Age Group', fontsize=18,
            ha='center', va='center', color='#a0a0c0', transform=ax.transAxes)
    ax.text(0.5, 0.42, str(min(years)) + ' - ' + str(max(years)), fontsize=14,
            ha='center', va='center', color='#a0a0c0', transform=ax.transAxes)
    ax.text(0.5, 0.20, 'Source: SINADEF', fontsize=11,
            ha='center', va='center', color='#606080', transform=ax.transAxes)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # -------------------------
    # ONE PAGE PER YEAR
    # -------------------------
    for year in years:
        yr_data = df[df['YEAR'] == year]

        fig, axes = plt.subplots(2, 5, figsize=(22, 10))
        fig.suptitle('Top 5 Causes of Death by Age Group - ' + str(year),
                     fontsize=16, fontweight='bold', y=1.01)
        fig.patch.set_facecolor('#f8f9fa')
        axes = axes.flatten()

        for i, age in enumerate(age_groups):
            ax = axes[i]
            data = yr_data[yr_data['GROUP'] == age].sort_values('TOTAL_DEATHS')

            if data.empty:
                ax.axis('off')
                ax.set_title(age, fontsize=11, fontweight='bold')
                continue

            bars = ax.barh(data['CAUSE'], data['TOTAL_DEATHS'],
                           color=palette, edgecolor='white', linewidth=0.5)

            # Add value labels
            for bar in bars:
                w = bar.get_width()
                ax.text(w + w * 0.02, bar.get_y() + bar.get_height() / 2,
                        '{:,}'.format(int(w)), va='center', fontsize=8)

            ax.set_title('Age ' + age, fontsize=11, fontweight='bold', pad=8)
            ax.set_xlabel('Total Deaths', fontsize=8)
            ax.tick_params(axis='y', labelsize=7)
            ax.tick_params(axis='x', labelsize=7)
            ax.set_facecolor('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.xaxis.set_major_formatter(
                matplotlib.ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x))
            )

        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

    # -------------------------
    # TREND PAGE: total deaths per year per age group
    # -------------------------
    trend = df[df['RANK'] == 1].groupby(['YEAR', 'GROUP'])['TOTAL_DEATHS'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('white')

    palette2 = sns.color_palette("tab10", len(age_groups))
    for idx, age in enumerate(age_groups):
        sub = trend[trend['GROUP'] == age]
        if not sub.empty:
            ax.plot(sub['YEAR'], sub['TOTAL_DEATHS'], marker='o',
                    label='Age ' + age, color=palette2[idx], linewidth=2)

    ax.set_title('#1 Cause Total Deaths Trend by Age Group', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Total Deaths', fontsize=11)
    ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=9)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x))
    )
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

print("DONE - deaths_report.pdf created")
