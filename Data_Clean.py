import pandas as pd
import numpy as np

# STEP 1: Load base CSV
df = pd.read_csv('consolidated_discharge.csv')

# STEP 2: Clean df
cols_to_drop = ['LAST_4', 'RANKGRADE', 'MIDDLE_NM', 'ASGLRS', 'DX', 'FOI', 'SUFFIX_NM']
df = df.drop(cols_to_drop, axis=1, errors='ignore')

# STEP 3: Create dummies for HOME_CIF
df_dummies = pd.get_dummies(df['HOME_CIF'], prefix='CIF')
df = pd.concat([df.drop('HOME_CIF', axis=1), df_dummies], axis=1)

# STEP 4: Load second CSV
df2 = pd.read_csv('consolidated_discharge2.csv')

# STEP 5: Clean df2 with same logic
df2 = df2.drop(cols_to_drop, axis=1, errors='ignore')
df2_dummies = pd.get_dummies(df2['HOME_CIF'], prefix='CIF')
df2 = pd.concat([df2.drop('HOME_CIF', axis=1), df2_dummies], axis=1)

# STEP 6: Align columns for concat (ensure all dummy columns match)
df2 = df2.reindex(columns=df.columns, fill_value=0)

# STEP 7: Append
df_combined = pd.concat([df, df2], ignore_index=True)

# STEP 8: Remove duplicates if needed
df_combined = df_combined.drop_duplicates()

# Final info
print(df_combined.head(5))
