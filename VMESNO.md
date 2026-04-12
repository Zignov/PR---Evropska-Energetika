# Napoved rasti obnovljivih virov energije v Evropi


Filip Mally, Žiga Novak, Matevž Skvarč, Mark Šincek, Simon Korošec

# 1. Opis problema
Glavni cilj raziskave je analizirati rast deleža obnovljivih virov energije v državah EU v obdobju zadnjega desetletja ter oceniti, kako uspešne so države pri uresničevanju cilja 42.5% do leta 2030.

Problem, ki ga preučujemo, je neenakomerna hitrost energetske rasti med državami, kar otežuje enotno načrtovanje evropske podnebne politike.

Z uporabo podatkovne analize in napovednih modelov želimo identificirati ključne razlike med državami ter oceniti prihodnje trende.


# 2. podatki
Uporabljamo uradne podatke statističnega urada Eurostat.

Glavni uporabljeni podatkovni viri so:
 - `estat_nrg_ind_ren`: delež OVE v končni porabi energije
 - `estat_nrg_bal_s`: energetske bilance držav
 - `estat_nrg_cb_rw`: podatki o posameznih vrstah obnovljivih virov
 - `sdg_08_10_tabular`: bruto domači proizvod na prebivalca (€ na prebivalca)

 Analiza se osredotočna na obdobje od leta 2014 do najnovejših razpoložljivih podatkov, kar omogoča vpogled v trende zadnjega desetletja.

 Podatki so bili v surovi obliki nepregledni in kompleksni, zato smo zgradili pomožno knjižnico `data_utils.py`, ki omogoča:
 - filtriranje relevantnih kazalnikov,
 - pretvorbo podatkov v numerične vrednosti,
 - preslikavo kratic držav v razumljiva imena,
 - čiščenje manjkajočih ali neveljavnih vrednosti

 Pri podatkih o GDP smo dodatno zapise filtrirali tako, da smo upoštevali le vrednosti v stalnih cenah CLV in na prebivalca (EUR_HAB). Odstranili smo prenizke vrednosti(manjše od 1000€), saj te najverjetneje predstavljajo manjkajoče ali nepravilno zabeležene podatke.

 Za potrebe analize smo podatke transformirali v pivotno obliko, kjer vrstice predstavljajo države, stolpci leta, vrednosti pa delež OVE. Manjkajoče vrednosti smo zapolnili z linearno interpolacijo.

 # 3. Izvedene analize
 Analizo smo izvajali v več zaporednih korakih, ki vključujejo pripravo podatkov, vizualizacijo in modeliranje vrednosti.

 
 ## 3.1 filtriranje in transformacija 
 Iz nabora podatkov smo izluščili podatke od leta 2014 naprej in ustvarili pivotno tabelo za primerjavo med državami
 S to obliko lahko enostavno primerjamo države skozi čas, ter služi kot osnova za nadaljne analize.

 ## 3.2 Vizualizacijo z toplotnim zemljevidom
Za pregled razvoja deleža OVE smo uporabili toplotni zemljevid. Omogoča nam hitro vizualno primerjavo med državami, saj so razlike zelo opazne zaradi barvne lestvice

 ## 3.3 Linearna regresija
 Za vsako državo posebej smo zgradili model linearne regresije, ki na temelji na obstoječih podatkih. Model napove delež OVE v letu 2030 na osnovi približno linearnih trendov rasti.

 ## 3.4 primerjava s cilji
države smo razdelili na 2 skupini, te ki bodo dosegle vsaj 42.5% obnovljivih virov energije do 2030 in te ki ne bodo.
Rezultate smo podali z stolpčnim diagramom kjer je zelo opazna razlika med uspešnimi in manj uspešnimi državami.

 ## 3.5 Analiza hitrosti rasti (CAGR)
Za bolj natančno oceno dinamike rasti smo izračunali sestavljeno letno stopnjo rasti ki upošteva učinek kumulativne rasti skozi čas
S to metriko lahko primerjamo države glede na hitrost napredka, ne glede na njihodo začetno stanje.

 ## 3.6 Povezava med gospodarsko razvitostjo in OVe
Analizirali smo tudi povezavo med BDP na prebivalca in deležem OVE. Uporabili smo linearno regresijo in Pearsonov koeificient za oceno jakosti povezave.
Namen je bil ugotoviti, ali imajo  bogatejše države prednost pri prehodu na obnovljive vire energije.

 ## 3.7 Analiza odstopanj
Na podlagi regresijskega modela smo našli države, ki odstopajo od pričakovanih vrednosti glede na njihov GDP.
Našli smo države katere imajo visok delež OVE glede na BDP in države ki imajo nizek delež OVE glede na BDP

 # 4. glavne ugotovitve in rezultati
 ## 4.1 Razlike med državami
  Razlike med posameznimi državami so zelo opazne, sploh med severnim in južnim delom evrope.
  Vodilne države ki že sedaj presegajo cilje so Skandinavske države. Na toplotnem zemljevidu lahko opazimo, da so te države konsistentno v zelenem območju skozi celotno desetletje.

 ## 4.2 Trenutni trendi in vizualizacija
    Toplotni zemljevid razkriva, da večina držav beleži postopno rast deleža OVE. Pri nekaterih državah je rest konsistentna, med tem ko druge kažejo stagnacijo oz. počasnejši napredek.

    Vizualizacija 1:
    Toplotni zemljevid deleža OVE(2014-danes) prikazuje stabilo rast v večini držav
    ![Toplotni zemljevid deleža OVE(2014-danes) prikazuje stabilo rast v večini držav](image.png)
 ## 4.3 Napoved za leto 2030
Na podalgi linearne regresije ugotavljamo, da precejšen delež držav ne bo dosegel cilja do leta 2030.
    Vizualizacija 2:
    ![Na paličnem grafikonu lahko vidimo napoved, katere države bodo do leta 2030 uresničile svoj cilj 42.5% deleža obnovljivih energij](image-1.png)

 ## 4.4 Hitrost rasti (CAGR)
Analiza sestavljene letne stopnje rasti pokaže, da nekatere države z nižjim začetnim deležem OVE dosegajo višje stopnje rasti.

 ## 4.5 Analiza ekonomskega vpliva (GDP vs OVE)
Želeli smo analizirati kako vpliva GDP na hitrost rasti OVE, za kar smo uporabili Pearsonov koeificient. Ta je po naših ugotovitvah znašal 0.21, kar kaže na šibko povezavo med BDP na prebivalca in deležem OVE.
To pomeni, da bogatejše države v povprečju malo pogosteje dosegajo višje deleže OVE, vendar povezava ni dovolj močna da bi bila edini pokazatelj tega.
Opažamo, da države z že visokim deležem OVE pogosto ohranjajo rast, kar nakazuje, da že obstoječa infrastruktura lahko močno prispeva k nadaljevanju ciljev.

    Vizualizacija 3:
    ![prikaz korelacije OVE z GDP](image-2.png)

 ## 4.5 Izstopajoče države
Prav tako smo ločili države ki najbolj odstopajo izven povprečja, tako najboljše kot najslabše. Ločili smo jih na podlagi nadpovprečnega/podpovprečnega deleža OVE glede na njihov GDP.
S tem smo dokazali da gospodarska razvitost ni edini dejavnik, vendar imajo vpliv tudi naravni viri (npr islandija).
