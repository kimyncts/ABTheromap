#########################################################################################################################
#####################################   SCRIPT 2 - RUN BLAST   ####################################################
#####################################      31/03/25 - Python utf8     ####################################################
###########################################################################################################
"""
Ce script utilise BLAST pour analyser des séquences NGS. 
- create_blast_db : Crée une base de données BLAST à partir d'un fichier FASTA.
- run_blast : Exécute BLASTN pour comparer des séquences de requête (VH, VL) 
à la base NGS et formate les résultats en TSV.
"""

# Importation des librairies
import subprocess
import pandas as pd

# Création de la base de données
def create_blast_db(fasta_file, db_name):
    """Crée une base de données BLAST à partir d'un fichier FASTA"""
    print(f"On rentre dans la fonction create blast {fasta_file}, {db_name}")
    cmd = [
        "makeblastdb", "-in", fasta_file, "-dbtype", "nucl", "-out", db_name
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Base de données BLAST créée : {db_name}")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de la création de la base de données BLAST: {e}")
        raise

# Execution du BLAST
def run_blast(query_file, db_name, output_file, evalue=0.001, perc_id=85.0, min_coverage=0, max_gaps=1000, min_length=0):
    """Exécute BLASTN avec un fichier de requête contre une base de données BLAST."""
    cmd = [
        "blastn", "-query", query_file, "-db", db_name, "-out", output_file,
        "-evalue", str(evalue), "-perc_identity", str(perc_id),
        "-outfmt", "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qcovs","-max_target_seqs", "10000"
    ]
    subprocess.run(cmd, check=True)
    print(f"BLAST terminé. Résultats enregistrés dans {output_file}")

    columns = [
        "qseqid", "sseqid", "pident", "length", "mismatch", "gapopen",
        "qstart", "qend", "sstart", "send", "evalue", "bitscore", "qcovs"
    ]
    df = pd.read_csv(output_file, sep="\t", header=None, names=columns)
    
    # Forçage explicite des types pour éviter les erreurs lors de l'enregistrement en base
    df = df.astype({
        "pident": float,
        "length": int,
        "mismatch": int,
        "gapopen": int,
        "qstart": int,
        "qend": int,
        "sstart": int,
        "send": int,
        "evalue": float,
        "bitscore": float,
        "qcovs": float
    })
    
    
    # Etape de filtration selon les paramètres du formulaire
    df = df[
        (df["qcovs"] >= min_coverage) &
        (df["gapopen"] <= max_gaps) &
        (df["length"] >= min_length)
    ]
    
    # Sauvegarde des données dans un fichier csv
    df.to_csv(output_file, sep="\t", index=False)
    
    return df
