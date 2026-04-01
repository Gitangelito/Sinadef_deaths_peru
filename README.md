# Peru Mortality Analysis (SINADEF)

Analysis of death records from Peru's SINADEF database (2017–2024).

## Files

- `analyze_deaths.py` — cleans the raw SINADEF CSV and outputs `dashboard_data.csv`
- `charts.py` — reads `dashboard_data.csv` and generates `deaths_report.pdf`

## How to Run

1. Download the raw data from [SINADEF](https://sinadef.minsa.gob.pe)
2. URL [https://www.datosabiertos.gob.pe/dataset/informaci%C3%B3n-de-fallecidos-del-sistema-inform%C3%A1tico-nacional-de-defunciones-sinadef-1] and name it `fallecidos_sinadef.csv`
3. Place it in the same folder as the scripts
4. Run:

```bash
pip install pandas matplotlib seaborn
python analyze_deaths.py
python charts.py
```

## Output

- `dashboard_data.csv` — top 5 causes of death grouped by age, sex, and ethnicity per year
- `deaths_report.pdf` — visual report with trend line, heatmap, and top causes by sex

## Data Source

SINADEF — Sistema Nacional de Defunciones, Ministerio de Salud del Peru
