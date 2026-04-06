import pandas as pd
import matplotlib.pyplot as plt
import time

def clean_eurostat_df(df): # prva vrstica; prvi stoplec vsebuje več info, ki jih potem treba razdelit da je bolj pregledno; potem pa še tudi nadomesti vse vredonsti da pač piše ali je prazno ali pač številka; potem še pretvori v številke in odstrani morebitne presledke
    raw_col = df.columns[0]
    head_split = raw_col.split('\\')[0].split(',')
    df[head_split] = df[raw_col].str.split(',', expand=True)
    df = df.drop(columns=[raw_col])

    id_vars = head_split 
    df = df.melt(id_vars=id_vars, var_name='year', value_name='value')

    df['value'] = df['value'].replace(r'[:\s]+', 'NaN', regex=True)
    df['value'] = df['value'].str.replace(r'[a-zA-Z\s]+', '', regex=True)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'].str.strip(), errors='coerce')

    return df

def load_tsv(name, path): # simple load funkcija za vse tsv-je; vrne koliko vrstic naloži in koliko časa potrebuje (vsebuje tudi čiščenje podatkov)
    s_time = time.time()
    df = pd.read_csv(f'{path}/{name}.tsv', sep='\t')

    df = clean_eurostat_df(df)
    e_time = time.time()

    print(f"Loaded {name} in {e_time - s_time:.3f}s - {len(df)} rows")
    return df

# Funkcije za nalaganje posameznih datasetov, ki jih potem uporabimo v main.py; vsaka funkcija pokliče load_tsv z ustreznim imenom datoteke in potjo do nje

def energy_balance():
    return load_tsv('estat_nrg_bal_s', 'data')

def share_of_renewables():
    return load_tsv('estat_nrg_ind_ren', 'data')

def STC_of_renewables():
    return load_tsv('estat_nrg_cb_rw', 'data')

def production_of_electricity():
    return load_tsv('estat_nrg_ind_peh', 'data')

def get_country_mapping(): #Še za lažjo predstavitev držav namesto njihovih kratic.
    return {
        'AL': 'Albanija',
        'AT': 'Avstrija',
        'BE': 'Belgija',
        'BG': 'Bolgarija',
        'CY': 'Ciper',
        'CZ': 'Češka',
        'DE': 'Nemčija',
        'DK': 'Danska',
        'EE': 'Estonija',
        'EL': 'Grčija',
        'ES': 'Španija',
        'FI': 'Finska',
        'FR': 'Francija',
        'HR': 'Hrvaška',
        'HU': 'Madžarska',
        'IE': 'Irska',
        'IS': 'Islandija',
        'IT': 'Italija',
        'LT': 'Litva',
        'LU': 'Luksemburg',
        'LV': 'Latvija',
        'MT': 'Malta',
        'NL': 'Nizozemska',
        'NO': 'Norveška',
        'PL': 'Poljska',
        'PT': 'Portugalska',
        'RO': 'Romunija',
        'SE': 'Švedska',
        'SI': 'Slovenija',
        'SK': 'Slovaška',
        'EU27_2020': 'Evropska Unija (27)'
    }

def add_country_names(df):
    mapping = get_country_mapping()
    # Ustvari nov stolpec 'drzava' na podlagi kratice 'geo'
    df['drzava'] = df['geo'].map(mapping)
    # Če kratice ni v slovarju, obdrži originalno kratico
    df['drzava'] = df['drzava'].fillna(df['geo'])
    return df

#Po želji še dodaj druge pomožne funkcije, ki jih potrebuješ za čiščenje ali obdelavo podatkov.