import pandas as pd

def convert_to_number(key, df):
    df['Heures'] = pd.to_numeric(df['Heures'], errors='coerce').fillna(0).astype(int)
    df['Minutes'] = pd.to_numeric(df['Minutes'], errors='coerce').fillna(0).astype(int)
    df['Distance (km)'] = pd.to_numeric(df['Distance (km)'], errors='coerce').fillna(0).astype(float)
    df['Prix (€)'] = round(pd.to_numeric(df['Prix (€)'], errors='coerce').fillna(0).astype(float), 2)
    df['CO2 (kg)'] = round(pd.to_numeric(df['CO2 (kg)'], errors='coerce').fillna(0).astype(float), 2)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y')
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')        
    if key != 'Marche' :
        df['Année'] = pd.to_datetime(df['Date'], format='%d/%m/%Y').dt.year
        df["Prix horaire (€)"] =  round(pd.to_numeric(df["Prix (€)"] / (df["Heures"] + df["Minutes"] / 60)).fillna(0).astype(float), 2)
        df["Prix au km (km)"] =   round(pd.to_numeric(df["Prix (€)"] / df["Distance (km)"]).fillna(0).astype(float), 2)
        df["CO2 par km (g/km)"] = round(pd.to_numeric(df["CO2 (kg)"] / df["Distance (km)"]*1000).fillna(0).astype(float), 2)
    
    try :
        df['Classe'] = df["Classe"].astype(int)
    except Exception :
        pass
    
    return df

def calculate_fiesta(df) :
    v_moy = 35.0 #km/h
    nb_h_tot = 23280 #h
    temps_th_volant = 445 #h
    temps_vol_pourcent = 1.912 #%
    co2 = 0.105 #kg/km
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%d/%m/%Y')
    df.sort_values(by='Date', ascending=False)
    df['Kilométrage (km)'].astype(float)

    df['Quantité (L)'] = pd.to_numeric(df['Quantité (L)'], errors='coerce').fillna(0).astype(float)
    df['Prix (€)'] = pd.to_numeric(df['Prix (€)'], errors='coerce').fillna(0).astype(float)
    df['Kilométrage (km)'] = pd.to_numeric(df['Kilométrage (km)'], errors='coerce').fillna(0).astype(float)

    df['Distance (km)'] = (df['Kilométrage (km)'] - df['Kilométrage (km)'].shift(-1)).shift(1)
    
    df['Litre par 100km'] =  round(pd.to_numeric(df['Quantité (L)'] / df['Distance (km)']*100).fillna(0).astype(float), 2)
    df['Prix au litre'] = round(pd.to_numeric(df['Prix (€)'] / df['Quantité (L)']).fillna(0).astype(float), 4)

    df['km journalier moy'] = (round(pd.to_numeric(df['Distance (km)'].shift(-1) / (pd.to_datetime(df['Date']) - pd.to_datetime(df['Date'].shift(-1))).dt.days), 2)).shift(1)
    
    df['Heures'] = (round(df['Distance (km)'].shift(-1) / v_moy, 2)).shift(1)
    df['Minutes'] = (round((df['Distance (km)'].shift(-1) % v_moy)*100/60, 2)).shift(1)
    df['CO2 (kg)'] = co2 * df['Distance (km)']
    
    return df

def calculate_marche(df) :
    nb_pas_par_min = 100
    nb_trajet_quotidien = 4
    
    df['Pas par jour'] = pd.to_numeric(df['Pas par jour'], errors='coerce').fillna(0).astype(int)
    df['Calorie par jour'] = pd.to_numeric(df['Calorie par jour'], errors='coerce').fillna(0).astype(float)
    df['Distance par jour (km / jour)'] = pd.to_numeric(df['Distance par jour (km / jour)'], errors='coerce').fillna(0).astype(float)
    
    df['Pas par semaine'] = pd.to_numeric(df['Pas par jour']*7).fillna(0).astype(int)
    df['Distance (km)'] = round(pd.to_numeric(df['Distance par jour (km / jour)']*7, errors='coerce').fillna(0).astype(float), 2)
    df['Calories'] = pd.to_numeric(df['Calorie par jour']*7, errors='coerce').fillna(0).astype(float)
    
    df['Heures'] = pd.to_numeric(df['Pas par semaine']/nb_pas_par_min//60, errors='coerce').fillna(0).astype(int)
    df['Minutes'] = pd.to_numeric(df['Pas par semaine']/nb_pas_par_min%60, errors='coerce').fillna(0).astype(int)
    
    df['Date'] = df['Année'].astype(str) + " - " + df['Numéro semaine'].astype(str).str.zfill(2)
    df.sort_values(by='Date', ascending=False, inplace=True)
    
    df['Année'] = pd.to_numeric(df['Année'], errors='coerce').fillna(0).astype(int)
    
    df['Pas par kilomètre'] = pd.to_numeric(df['Pas par semaine']/df['Distance (km)'], errors='coerce').fillna(0).astype(int)
    df['Distance par trajet'] = round(pd.to_numeric(df['Distance (km)']/nb_trajet_quotidien, errors='coerce').fillna(0).astype(float), 2)
    df['Taille de pas'] = round(pd.to_numeric(100000/df['Pas par kilomètre'], errors='coerce').fillna(0).astype(float), 2)
    
    df['CO2 (kg)'] = 0
    df["Prix (€)"] = 0
    
    return df