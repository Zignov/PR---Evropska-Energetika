import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
import os

st.set_page_config(page_title="OVE Analiza Evropa", layout="wide")

POT_DATOTEKE = os.path.join("data", "estat_nrg_ind_ren.tsv")
POT_GDP = os.path.join("data", "sdg_08_10_tabular.tsv")
LETA = [str(leto) for leto in range(2014, 2025)]
CILJ_EU_2030 = 42.5

PREVODI_DRZAV = {
    'IS': 'Islandija',      'NO': 'Norveška',             'SE': 'Švedska',
    'FI': 'Finska',         'BA': 'Bosna in Hercegovina', 'AL': 'Albanija',
    'DK': 'Danska',         'LV': 'Latvija',              'AT': 'Avstrija',
    'EE': 'Estonija',       'ME': 'Črna Gora',            'PT': 'Portugalska',
    'LT': 'Litva',          'HR': 'Hrvaška',              'RS': 'Srbija',
    'ES': 'Španija',        'RO': 'Romunija',             'GR': 'Grčija',
    'SI': 'Slovenija',      'FR': 'Francija',             'BG': 'Bolgarija',
    'DE': 'Nemčija',        'MK': 'Severna Makedonija',   'CY': 'Ciper',
    'MD': 'Moldavija',      'NL': 'Nizozemska',           'GE': 'Gruzija',
    'IT': 'Italija',        'CZ': 'Češka',                'HU': 'Madžarska',
    'SK': 'Slovaška',       'XK': 'Kosovo',               'PL': 'Poljska',
    'MT': 'Malta',          'IE': 'Irska',                'LU': 'Luksemburg',
    'BE': 'Belgija',
}


@st.cache_data
def nalozi_ove(pot):
    surovi = pd.read_csv(pot, sep="\t")
    prvi_stolpec = surovi.columns[0]
    kode_drzav = set(PREVODI_DRZAV)
    vrstice = {}

    for _, vrstica in surovi.iterrows():
        deli_meta = [d.strip() for d in str(vrstica[prvi_stolpec]).split(',')]
        ujemanje = kode_drzav.intersection(deli_meta)
        
        if not ujemanje:
            continue
        
        ime_drzave = PREVODI_DRZAV[ujemanje.pop()]
        vrednosti = []

        for leto in LETA:
            stolpci = [s for s in surovi.columns if s.strip() == leto]
            if stolpci:
                surova_vrednost = str(vrstica[stolpci[0]]).strip().split()[0]
                try:
                    vrednosti.append(float(surova_vrednost))
                
                except ValueError:
                    vrednosti.append(float('nan'))
            else:
                vrednosti.append(float('nan'))
        vrstice[ime_drzave] = vrednosti

    df = pd.DataFrame.from_dict(vrstice, orient='index', columns=LETA)
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.interpolate(method='linear', axis=1).dropna(how='all')
    return df


@st.cache_data
def nalozi_gdp(pot):
    surovi = pd.read_csv(pot, sep="\t")
    prvi_stolpec = surovi.columns[0]
    head_split = prvi_stolpec.split('\\')[0].split(',')
    surovi[head_split] = surovi[prvi_stolpec].str.split(',', expand=True)
    surovi = surovi.drop(columns=[prvi_stolpec])
    df = surovi.melt(id_vars=head_split, var_name='year', value_name='value')


    df['value'] = df['value'].replace(r'[:\s]+', 'NaN', regex=True)
    df['value'] = df['value'].str.replace(r'[a-zA-Z\s]+', '', regex=True)
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'].str.strip(), errors='coerce')
    df['drzava'] = df['geo'].map(PREVODI_DRZAV).fillna(df['geo'])
    return df


def izracun_napovedi_2030(pivot_df, nacin):
    rezultati = []
    
    for drzava in pivot_df.index:
        serija = pivot_df.loc[drzava].dropna()
        if len(serija) < 2:
            continue
        y = serija.values
        zacetek = int(serija.index[0])
        X_raw = np.array([int(l) for l in serija.index])
        
        if nacin == "Linearna":
            model = LinearRegression()
            model.fit(X_raw.reshape(-1, 1), y)
            napoved = model.predict([[2030]])[0]

        else:
            X = (X_raw - zacetek).reshape(-1, 1)
            pol = PolynomialFeatures(degree=2)
            X_pol = pol.fit_transform(X)
            model = Ridge(alpha=1.0)
            model.fit(X_pol, y)
            napoved = float(np.clip(model.predict(pol.transform([[2030 - zacetek]]))[0], 0, 100))

        rezultati.append({'drzava': drzava, 'zadnje_leto': y[-1], 'napoved_2030': napoved})
    
    df_pred = pd.DataFrame(rezultati)
    df_pred['dosega_cilj'] = df_pred['napoved_2030'] >= CILJ_EU_2030
    return df_pred


def izracun_cagr(pivot_df):
    prvo = pivot_df.columns[0]

    zadnje = pivot_df.columns[-1]
    n_let = int(zadnje) - int(prvo)
    return ((pivot_df[zadnje] / pivot_df[prvo]) ** (1 / n_let) - 1) * 100


def fig_size(sirina, visina):
    return sirina * 0.7, visina * 0.7


if not os.path.exists(POT_DATOTEKE):
    st.error(f"Datoteka `{POT_DATOTEKE}` ni bila najdena.")
    st.stop()

df = nalozi_ove(POT_DATOTEKE)

st.sidebar.header("Izbira analize")
izbrano_orodje = st.sidebar.radio(
    "Izberite funkcionalnost:",
    ["Primerjava po OVE", "Največji napredek OVE", "Napoved 2030", "BDP vs OVE korelacija"]
)

#----
#1) primerjava drzav - linijski graf za izbrane drzave skozi cas
#----
if izbrano_orodje == "Primerjava po OVE":
    st.header("Primerjava po OVE")

    izbrane_drzave = st.multiselect(
        "Izberite države za primerjavo:",
        options=sorted(df.index),
        default=["Slovenija", "Hrvaška", "Avstrija"],
    )

    int_leta = [int(l) for l in LETA]
    zacetno_leto, koncno_leto = st.slider(
        "Izberite časovno obdobje:",
        min_value=min(int_leta), max_value=max(int_leta), value=(2014, 2024),
    )

    if not izbrane_drzave:
        st.warning("Prosim, izberite vsaj eno državo.")
        st.stop()

    izbrana_leta = [str(l) for l in range(zacetno_leto, koncno_leto + 1)]
    filtrirani_df = df.loc[izbrane_drzave, izbrana_leta]

    st.subheader("Primerjalni graf")
    slika, os_grafa = plt.subplots(figsize=fig_size(14, 5))
    for drzava in izbrane_drzave:
        os_grafa.plot(filtrirani_df.columns, filtrirani_df.loc[drzava], marker='o', label=drzava, linewidth=2)
    
    y_min = max(0, filtrirani_df.min().min() - 5)
    y_max = min(100, filtrirani_df.max().max() + 5)

    os_grafa.set(xlabel="Leto", ylabel="Delež OVE (%)", ylim=(y_min, y_max))
    os_grafa.legend()
    os_grafa.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(slika, use_container_width=True)

    st.subheader("Povprečni delež OVE v izbranem obdobju")
    povprecja = filtrirani_df.mean(axis=1).rename("Povprečje (%)").to_frame()
    st.dataframe(povprecja, use_container_width=True)


#----
#2) najvecji napredek - katere drzave so najbolj zrastle od 2014 do 2024
#----
elif izbrano_orodje == "Največji napredek OVE":
    st.header("Največji napredek OVE")

    stevilo_drzav = st.number_input(
        "Koliko vodilnih držav?", min_value=1, max_value=20, value=5,
    )

    df_napredek = df[['2014', '2024']].dropna().copy()
    df_napredek['Razlika'] = df_napredek['2024'] - df_napredek['2014']
    vodilne_drzave = df_napredek.nlargest(stevilo_drzav, 'Razlika')

    if vodilne_drzave.empty:
        st.warning("Ni podatkov za izračun napredka.")
        st.stop()

    st.subheader(f"Top {stevilo_drzav} držav z največjo rastjo (2014 → 2024)")
    slika2, os_grafa2 = plt.subplots(figsize=fig_size(14, max(3, stevilo_drzav * 0.65)))
    pozicije = range(len(vodilne_drzave))
    stolpci_grafa = os_grafa2.barh(pozicije, vodilne_drzave['Razlika'], color='teal')

    os_grafa2.set_yticks(pozicije)
    os_grafa2.set_yticklabels(vodilne_drzave.index)
    os_grafa2.set_xlabel("Povečanje deleža OVE (v odstotnih točkah)")
    os_grafa2.invert_yaxis()
    os_grafa2.grid(True, linestyle='--', alpha=0.4, axis='x')


    for stolpec in stolpci_grafa:
        sirina = stolpec.get_width()
        os_grafa2.text(sirina + 0.3, stolpec.get_y() + stolpec.get_height() / 2, f"+{sirina:.1f}%", va='center', ha='left', fontsize=10, weight='bold')
    
    st.pyplot(slika2, use_container_width=True)

    st.write("Podrobni podatki:")
    st.dataframe(vodilne_drzave.style.format("{:.2f}"), use_container_width=True)

#----
#3) napoved 2030 - bo drzava dosegla cilj EU 42.5%
#----
elif izbrano_orodje == "Napoved 2030":
    st.header("Napoved deleža OVE za leto 2030")
    st.caption("Zeleno = bo dosegla cilj EU (42,5 %), rdeče = ne bo.")

    nacin_regresije = st.radio(
        "Model napovedi:", ["Linearna", "Polinomska (2. stopnje, Ridge)"], horizontal=True,
    )
    nacin = "Linearna" if nacin_regresije == "Linearna" else "Polinomska"

    df_pred = izracun_napovedi_2030(df, nacin)
    df_viz = df_pred.sort_values(by='napoved_2030', ascending=True)
    barve = ['#2ca02c' if x else '#d62728' for x in df_viz['dosega_cilj']]

    slika4, os_grafa4 = plt.subplots(figsize=fig_size(14, 12))
    os_grafa4.barh(df_viz['drzava'], df_viz['napoved_2030'], color=barve, edgecolor='black', alpha=0.8)
    os_grafa4.axvline(x=CILJ_EU_2030, color='black', linestyle='--', linewidth=2)
    os_grafa4.set_title(f"Napoved deleža OVE za leto 2030 ({nacin} regresija)", fontsize=13, fontweight='bold')
    os_grafa4.set_xlabel("Napovedan delež OVE (%)")
    os_grafa4.set_ylabel("Država")
    os_grafa4.grid(axis='x', linestyle='-', alpha=0.3)
    
    zelena = mpatches.Patch(color='#2ca02c', label='Cilj BO dosežen')
    rdeca = mpatches.Patch(color='#d62728', label='Cilj NE bo dosežen')
    crta = plt.Line2D([0], [0], color='black', linestyle='--', label=f'EU Cilj ({CILJ_EU_2030} %)')

    os_grafa4.legend(handles=[zelena, rdeca, crta], loc='lower right', fontsize=10)
    slika4.tight_layout()
    st.pyplot(slika4, use_container_width=True)

    st.subheader("Podrobni podatki napovedi")
    
    prikaz_pred = df_pred.sort_values('napoved_2030', ascending=False).copy()
    prikaz_pred['dosega_cilj'] = prikaz_pred['dosega_cilj'].map({True: 'Da', False: 'Ne'})
    
    st.dataframe(prikaz_pred.rename(columns={'drzava': 'Država', 'zadnje_leto': 'OVE zdaj (%)','napoved_2030': 'Napoved 2030 (%)', 'dosega_cilj': 'Dosega cilj'}).set_index('Država').style.format({'OVE zdaj (%)': '{:.1f}', 'Napoved 2030 (%)': '{:.1f}'}),use_container_width=True,)

#----
#4) bdp vs ove - ali so bogatejse drzave boljse pri ove
#----
elif izbrano_orodje == "BDP vs OVE korelacija":
    st.header("Korelacija: BDP na prebivalca vs delež OVE")
    st.caption("Preverja ali imajo bogatejše države višji delež OVE in katera odstopajo od trenda.")

    if not os.path.exists(POT_GDP):
        st.error(f"Datoteka `{POT_GDP}` ni bila najdena.")
        st.stop()

    df_gdp_raw = nalozi_gdp(POT_GDP)
    zadnje_leto_int = int(LETA[-1])

    df_gdp_filter = df_gdp_raw[
        (df_gdp_raw['unit'].str.contains('CLV', na=False)) &
        (df_gdp_raw['unit'].str.contains('EUR_HAB', na=False)) &
        (df_gdp_raw['year'] == zadnje_leto_int) &
        (df_gdp_raw['value'] > 1000)
    ].copy()

    ove_zadnje = df[LETA[-1]].rename("OVE_delez")
    cagr_s = izracun_cagr(df).rename("CAGR")
    cagr_s = cagr_s[cagr_s.index != 'Gruzija']

    analiza_df = pd.DataFrame({'OVE_delez': ove_zadnje, 'CAGR': cagr_s}).merge(
        df_gdp_filter[['drzava', 'value']], left_index=True, right_on='drzava'
    ).rename(columns={'value': 'GDP_per_capita'})
    
    analiza_df['GDP_per_capita'] = pd.to_numeric(analiza_df['GDP_per_capita'], errors='coerce')
    analiza_df['OVE_delez'] = pd.to_numeric(analiza_df['OVE_delez'], errors='coerce')
    analiza_clean = analiza_df.dropna(subset=['GDP_per_capita', 'OVE_delez'])

    if analiza_clean.empty:
        st.warning("Ni dovolj podatkov. Preverite pot do GDP datoteke.")
        st.stop()

    X = analiza_clean[['GDP_per_capita']].values
    y = analiza_clean['OVE_delez'].values
    model = LinearRegression().fit(X, y)
    analiza_clean = analiza_clean.copy()
    analiza_clean['ostanek'] = y - model.predict(X)

    korelacija = analiza_clean['GDP_per_capita'].corr(analiza_clean['OVE_delez'])

    slika5, os_grafa5 = plt.subplots(figsize=fig_size(10, 6))
    sns.regplot(data=analiza_clean, x='GDP_per_capita', y='OVE_delez', ax=os_grafa5)
    os_grafa5.set_title(f"Korelacija: BDP vs delež OVE ({LETA[-1]})", fontsize=13)
    os_grafa5.set_xlabel("GDP na prebivalca (EUR)")

    os_grafa5.set_ylabel("Delež OVE (%)")
    slika5.tight_layout()
    st.pyplot(slika5, use_container_width=True)

    st.metric("Pearsonov korelacijski koeficient", f"{korelacija:.2f}",
              help="0 = ni povezave, 1 = popolna pozitivna povezava")

    st.subheader("Izstopajoče države glede na BDP")
    pozitivni_odkl = analiza_clean.nlargest(3, 'ostanek')[['drzava', 'OVE_delez', 'GDP_per_capita']]
    negativni_odkl = analiza_clean.nsmallest(3, 'ostanek')[['drzava', 'OVE_delez', 'GDP_per_capita']]

    levi, desni = st.columns(2)
    with levi:
        st.markdown("**Presegajo pričakovano glede na BDP**")
        st.dataframe(
            pozitivni_odkl.set_index('drzava').style.format({'OVE_delez': '{:.1f}', 'GDP_per_capita': '{:,.0f}'}),
            use_container_width=True,
        )
        
    with desni:
        st.markdown("**Zaostajajo glede na BDP**")
        st.dataframe(
            negativni_odkl.set_index('drzava').style.format({'OVE_delez': '{:.1f}', 'GDP_per_capita': '{:,.0f}'}),
            use_container_width=True,
        )