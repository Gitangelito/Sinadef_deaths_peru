# -*- coding: utf-8 -*-
import pandas as pd

print("Loading CSV...")
df = pd.read_csv("fallecidos_sinadef.csv", sep="|", low_memory=False)
df.columns = df.columns.str.strip()
df = df.replace("SIN REGISTRO", pd.NA)

# Auto-detect year column
year_col = [c for c in df.columns if 'O' in c and 'A' in c and len(c) <= 4][0]

df = df[[year_col, 'SEXO', 'EDAD', 'ETNIA', 'DEPARTAMENTO DOMICILIO', 'DEBIDO A (CAUSA A)']].copy()
df = df.dropna(subset=[year_col, 'SEXO', 'EDAD', 'ETNIA', 'DEBIDO A (CAUSA A)'])

df['EDAD'] = pd.to_numeric(df['EDAD'], errors='coerce')
df[year_col] = pd.to_numeric(df[year_col], errors='coerce')
df = df.dropna(subset=['EDAD', year_col])

df['AGE_GROUP'] = pd.cut(
    df['EDAD'],
    bins=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 120],
    labels=['0-10','11-20','21-30','31-40','41-50','51-60','61-70','71-80','81-90','90+']
)
df = df.dropna(subset=['AGE_GROUP'])

df = df.rename(columns={
    year_col: 'YEAR',
    'SEXO': 'SEX',
    'ETNIA': 'ETHNICITY',
    'DEPARTAMENTO DOMICILIO': 'DEPARTMENT',
    'DEBIDO A (CAUSA A)': 'CAUSE'
})

def top5(group_cols):
    return (
        df.groupby(group_cols + ['CAUSE'], observed=True)
        .size().reset_index(name='TOTAL_DEATHS')
        .sort_values(group_cols + ['TOTAL_DEATHS'], ascending=[True]*len(group_cols) + [False])
        .groupby(group_cols, observed=True).head(5)
        .reset_index(drop=True)
    )

# TOP 5 BY YEAR + SEX
t_sex = top5(['YEAR', 'SEX'])
t_sex['RANK'] = t_sex.groupby(['YEAR', 'SEX']).cumcount() + 1
t_sex.insert(0, 'CATEGORY', 'BY_SEX')
t_sex = t_sex.rename(columns={'SEX': 'GROUP'})
t_sex['AGE_GROUP'] = ''
t_sex['ETHNICITY'] = ''

# TOP 5 BY YEAR + AGE GROUP
t_age = top5(['YEAR', 'AGE_GROUP'])
t_age['AGE_GROUP'] = t_age['AGE_GROUP'].astype(str)
t_age['RANK'] = t_age.groupby(['YEAR', 'AGE_GROUP']).cumcount() + 1
t_age.insert(0, 'CATEGORY', 'BY_AGE')
t_age = t_age.rename(columns={'AGE_GROUP': 'GROUP'})
t_age['SEX'] = ''
t_age['ETHNICITY'] = ''

# TOP 5 BY YEAR + ETHNICITY
t_eth = top5(['YEAR', 'ETHNICITY'])
t_eth['RANK'] = t_eth.groupby(['YEAR', 'ETHNICITY']).cumcount() + 1
t_eth.insert(0, 'CATEGORY', 'BY_ETHNICITY')
t_eth = t_eth.rename(columns={'ETHNICITY': 'GROUP'})
t_eth['SEX'] = ''
t_eth['AGE_GROUP'] = ''

# COMBINE
final = pd.concat(
    [t_sex, t_age, t_eth],
    ignore_index=True
)
final['YEAR'] = final['YEAR'].astype(int)
final = final[['CATEGORY', 'YEAR', 'GROUP', 'RANK', 'CAUSE', 'TOTAL_DEATHS']]
final = final.sort_values(['CATEGORY', 'YEAR', 'GROUP', 'RANK']).reset_index(drop=True)

final.to_csv("dashboard_data.csv", index=False)
print("DONE - dashboard_data.csv created")
print("Rows: " + str(len(final)))
print("\nPreview:")
print(final.head(30).to_string(index=False))
