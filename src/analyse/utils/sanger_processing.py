#########################################################################################################################
#####################################   SCRIPT 1 - Séparation VH/VL   ####################################################
#####################################      26/03/25 - Python utf8     ####################################################
#########################################################################################################################
"""
Ce script importe les séquences Sanger (fichier TSV)
Il récupère les séquences VH et VL, 
élimine les séquences pour lesquels il y a des valeurs NaN,
et génère des fichiers FASTA pour chaque type de séquence.
"""

# Importation des librairies
import pandas as pd
import os

# Définition des colonnes d'intérêt
SEQUENCE_COL = 'V-REGION'
ID_COL = 'V-DOMAIN ID'

def remove_nan_values(df):
    """Élimine les valeurs NaN de la colonne V-Region"""
    df = df.dropna(subset=[SEQUENCE_COL])
    return df

def filter_sequences(df):
    """Filtre les séquences VH et VL"""
    df_VH = df[df[ID_COL].str.endswith("H", na=False)]
    df_VL = df[df[ID_COL].str.endswith(("L","K"), na=False)]
    return df_VH, df_VL

def write_fasta(df, filename):
    """ Écrit un DataFrame en fichier FASTA """
    with open(filename, "w") as fasta_file:
        for _, row in df.iterrows():
            fasta_file.write(f">{row[ID_COL]}\n{row[SEQUENCE_COL]}\n")

### Fonctions pour le fichiers de statistiques
def compute_stats(df):
    """Calcule des statistiques de base sur les longueurs de séquences"""
    if df.empty:
        return {
            "nombre_de_sequences": 0,
            "taille_min": 0,
            "taille_max": 0,
            "taille_moyenne": 0,
            "taille_mediane": 0
        }

    lengths = df[SEQUENCE_COL].str.len()
    return {
        "nombre_de_sequences": len(lengths),
        "taille_min": lengths.min(),
        "taille_max": lengths.max(),
        "taille_moyenne": round(lengths.mean(), 2),
        "taille_mediane": lengths.median()
    }

def write_stats(stats_vh, stats_vl, output_path):
    """Écrit les statistiques VH et VL dans un fichier texte"""
    with open(output_path, "w") as f:
        f.write("STATISTIQUES DES SÉQUENCES\n")
        f.write("\n--- Séquences VH ---\n")
        for key, value in stats_vh.items():
            f.write(f"{key.replace('_', ' ').capitalize()} : {value}\n")

        f.write("\n--- Séquences VL ---\n")
        for key, value in stats_vl.items():
            f.write(f"{key.replace('_', ' ').capitalize()} : {value}\n")

#### Fonction principale
def process_sanger_file(filepath, output_dir,analysis_id):
    # Importer les séquences Sanger dans un dataframe
    print(f"début du process sanger {filepath}")
    df = pd.read_csv(filepath, sep="\t")
    print("Fichier téléchargé : df")
    # Vérifier la présence des colonnes ID et séquences
    if SEQUENCE_COL not in df.columns or ID_COL not in df.columns:
        raise ValueError("Colonnes manquantes dans le fichier TSV")

    
    # Eliminer les valeurs NaN si il y en a
    df = remove_nan_values(df)
    print("Elimination des NaN")
    # Séparer les séquences VH et VL dans deux dataframes distincts.
    df_VH, df_VL = filter_sequences(df)
    print("sequence filtré")
    print(f"Nombre de séquences VH : {df_VH.shape[0]}")
    print(f"Nombre de séquences VL : {df_VL.shape[0]}")

    # créer le dossier de sortie si il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    split_dir = os.path.join(output_dir, "split-VH_VL")
    os.makedirs(split_dir, exist_ok=True)
    
    # Définition des chemin des fichiers de sortie
    vh_path = os.path.join(split_dir, f"VH_sequences_{analysis_id}.fasta")
    vl_path = os.path.join(split_dir, f"VL_sequences_{analysis_id}.fasta")
    
    # Sauvegarder dans les fichiers FASTA
    write_fasta(df_VH, vh_path)
    write_fasta(df_VL, vl_path)
    print("sauvegarde des fichier validé")
    
    # Calcul et sauvegarde des statistiques
    stats_vh = compute_stats(df_VH)
    stats_vl = compute_stats(df_VL)
    stats_path = os.path.join(split_dir, f"stats_sequences_{analysis_id}.txt")
    write_stats(stats_vh, stats_vl, stats_path)
    print("Statistiques sauvegardées")
    
    return vh_path, vl_path

