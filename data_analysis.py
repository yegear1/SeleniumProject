import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import re
import logging

df = pd.read_csv('dados_tratados.csv', header=None, names=['Nome', 'Marca', 'Preco', 'Data', 'Fonte'])

print(df.head())

df = pd.read_csv('dados_tratados.csv', header=None, names=['Modelo', 'Marca', 'Preco', 'Data', 'Fonte'])

df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
df['Preco'] = pd.to_numeric(df['Preco'], errors='coerce')

print(df.head())

modelo_desejado = 'RTX 3060'
df_modelo = df[df['Modelo'] == modelo_desejado]

plt.figure(figsize=(10, 6))
sns.lineplot(data=df_modelo, x='Data', y='Preco', hue='Marca', marker='o')
plt.title(f'Evolução de Preço - {modelo_desejado}')
plt.xlabel('Data')
plt.ylabel('Preço (R$)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()