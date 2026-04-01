# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.backends.backend_pdf as pdf_backend
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# -------------------------
# LOAD & CLEAN
# -------------------------
df = pd.read_csv("dashboard_data.csv")
df['CAUSE'] = df['CAUSE'].str.strip().str.title()

# Merge duplicate heart attack entries
df['CAUSE'] = df['CAUSE'].replace(
    'Infarto Agudo Del Miocardio', 'Infarto Agudo De Miocardio'
)

age_order = ['0-10','11-20','21-30','31-40','41-50','51-60','61-70','71-80','81-90','90+']
years = sorted(df['YEAR'].unique())

# Color palette
main_color = '#2E86AB'
accent = '#E84855'
bg = '#F8F9FA'

fmt = ticker.FuncFormatter(lambda x, _: '{:,.0f}'.format(x))

with pdf_backend.PdfPages("deaths_report.pdf") as pdf:

    # -------------------------
    # COVER
    # -------------------------
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    fig.patch.set_facecolor('#1a1a2e')
    ax.text(0.5, 0.62, 'Peru Mortality Report', fontsize=40, fontweight='bold',
            ha='center', color='white', transform=ax.transAxes)
    ax.text(0.5, 0.50, 'Causes of Death Analysis', fontsize=20,
            ha='center', color='#a0a0c0', transform=ax.transAxes)
    ax.text(0.5, 0.40, '2017 - 2024', fontsize=15,
            ha='center', color='#a0a0c0', transform=ax.transAxes)
    ax.text(0.5, 0.18, 'Source: SINADEF - Sistema Nacional de Defunciones', fontsize=10,
            ha='center', color='#606080', transform=ax.transAxes)
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # -------------------------
    # PAGE 1: TOTAL DEATHS TREND PER YEAR
    # -------------------------
    age_df = df[df['CATEGORY'] == 'BY_AGE'].copy()
    trend = age_df.groupby('YEAR')['TOTAL_DEATHS'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor('white')

    ax.fill_between(trend['YEAR'], trend['TOTAL_DEATHS'], alpha=0.15, color=main_color)
    ax.plot(trend['YEAR'], trend['TOTAL_DEATHS'], marker='o', color=main_color,
            linewidth=2.5, markersize=8)

    for _, row in trend.iterrows():
        ax.annotate('{:,.0f}'.format(row['TOTAL_DEATHS']),
                    (row['YEAR'], row['TOTAL_DEATHS']),
                    textcoords="offset points", xytext=(0, 10),
                    ha='center', fontsize=9, color='#333333')

    ax.set_title('Total Deaths per Year (All Age Groups)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Total Deaths', fontsize=11)
    ax.set_xticks(years)
    ax.yaxis.set_major_formatter(fmt)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_facecolor('white')

    note = 'Note: spike in 2020-2021 reflects COVID-19 pandemic impact'
    fig.text(0.5, -0.02, note, ha='center', fontsize=9, color='gray', style='italic')

    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # -------------------------
    # PAGE 2: HEATMAP - TOP CAUSE PER AGE GROUP ACROSS YEARS
    # -------------------------
    top1 = age_df[age_df['RANK'] == 1].copy()
    top1['GROUP'] = pd.Categorical(top1['GROUP'], categories=age_order, ordered=True)
    pivot = top1.pivot_table(index='GROUP', columns='YEAR', values='TOTAL_DEATHS', aggfunc='sum')
    pivot = pivot.reindex(age_order)

    fig, ax = plt.subplots(figsize=(13, 7))
    fig.patch.set_facecolor(bg)

    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd',
                linewidths=0.5, linecolor='white',
                annot_kws={'size': 9}, ax=ax,
                cbar_kws={'label': 'Total Deaths'})

    ax.set_title('Deaths from #1 Cause by Age Group & Year', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Year', fontsize=11)
    ax.set_ylabel('Age Group', fontsize=11)
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # -------------------------
    # PAGE 3: TOP 5 CAUSES OVERALL (ALL YEARS COMBINED)
    # -------------------------
    overall = (
        age_df.groupby('CAUSE')['TOTAL_DEATHS'].sum()
        .reset_index()
        .sort_values('TOTAL_DEATHS', ascending=False)
        .head(10)
        .sort_values('TOTAL_DEATHS')
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(bg)
    ax.set_facecolor('white')

    colors = [accent if i >= len(overall) - 5 else '#b0c4de' for i in range(len(overall))]
    bars = ax.barh(overall['CAUSE'], overall['TOTAL_DEATHS'], color=colors, edgecolor='white')

    for bar in bars:
        w = bar.get_width()
        ax.text(w + w * 0.01, bar.get_y() + bar.get_height() / 2,
                '{:,.0f}'.format(int(w)), va='center', fontsize=9)

    ax.set_title('Top 10 Causes of Death - All Years Combined', fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Total Deaths', fontsize=11)
    ax.xaxis.set_major_formatter(fmt)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='y', labelsize=9)

    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

    # -------------------------
    # PAGE 4: TOP 5 CAUSES BY SEX (ALL YEARS COMBINED)
    # -------------------------
    sex_df = df[df['CATEGORY'] == 'BY_SEX'].copy()
    sex_df = sex_df[sex_df['GROUP'].isin(['MASCULINO', 'FEMENINO'])]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor(bg)
    fig.suptitle('Top 5 Causes of Death by Sex - All Years Combined',
                 fontsize=14, fontweight='bold')

    for ax, (sex, label, color) in zip(axes, [
        ('MASCULINO', 'Men', '#2E86AB'),
        ('FEMENINO',  'Women', '#E84855')
    ]):
        data = (
            sex_df[sex_df['GROUP'] == sex]
            .groupby('CAUSE')['TOTAL_DEATHS'].sum()
            .reset_index()
            .sort_values('TOTAL_DEATHS', ascending=False)
            .head(5)
            .sort_values('TOTAL_DEATHS')
        )
        ax.set_facecolor('white')
        bars = ax.barh(data['CAUSE'], data['TOTAL_DEATHS'], color=color, edgecolor='white')
        for bar in bars:
            w = bar.get_width()
            ax.text(w + w * 0.01, bar.get_y() + bar.get_height() / 2,
                    '{:,.0f}'.format(int(w)), va='center', fontsize=9)
        ax.set_title(label, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel('Total Deaths', fontsize=10)
        ax.xaxis.set_major_formatter(fmt)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='y', labelsize=9)

    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()

print("DONE - deaths_report.pdf created (4 pages + cover)")
