from celery import shared_task
from .models import Analysis, BlastResult
from .utils.sanger_processing import process_sanger_file
from .utils.run_blast import create_blast_db, run_blast
from django.conf import settings
import os

@shared_task
def traiter_analyse_async(analysis_id):
    print(f"Tâche Celery lancée pour analysis_id={analysis_id}")
    
    #### Verifie que l'analyse existe dans la base de donnée (données du formulaire) - obligatoire en asynchrone
    try:
        analysis = Analysis.objects.get(pk=analysis_id)
        print(f"Analysis trouvée !")
    except Analysis.DoesNotExist:
        print(f"Analysis avec pk={analysis_id} introuvable !")
        raise
    
    #### Lancement de l'analyse des séquences (séparation VH_VL et alignement Blast)
    try:
        # Créer un dossier de travail pour cette analyse
        print("Début du bloc traitement")
        working_dir = os.path.join(settings.MEDIA_ROOT, f"analysis_{analysis.id}")
        os.makedirs(working_dir, exist_ok=True)

        ## ETAPE 1 : Généré 2 fichiers fasta VH et VL à partir des données du Séquençage Sanger
        vh_path, vl_path = process_sanger_file(analysis.seq_file.path, working_dir, analysis.id)
        print(f"Fichiers VH et VL générés : {vh_path}, {vl_path}")

        ### Définir les dossiers et chemin d'accès pour les résultats du BLAST
        db_name = os.path.join(working_dir, "ngs_db")
        ngs_fasta = analysis.ngs_file.path  # récupérer le fichier NGS uploadé
        vh_blast_result = os.path.join(working_dir, "VH_blast_results.tsv")
        vl_blast_result = os.path.join(working_dir, "VL_blast_results.tsv")
        print("dossier BLAST crées")
        # ETAPE 2 : Créer la base de donnée BLAST
        create_blast_db(ngs_fasta, db_name)
        print("Base de données crées")
        # ETAPE 3 : Lancer le blast pour le vichier VH.fasta et VL.fasta issue de l'étape 1
        # Pour VH
        print("Blast lancé pour VH")
        df_vh = run_blast(vh_path, db_name, vh_blast_result, 
                          evalue = analysis.e_value, 
                          perc_id = analysis.perc_identity,
                          min_coverage = analysis.coverage,
                          max_gaps = analysis.gaps,
                          min_length = analysis.alignment_length)
        
        # Ajout des données d'alignement des domaines VH dans la base de données
        vh_results = [
            BlastResult(
                analysis=analysis,
                vh_or_vl="VH",
                qseqid=row.qseqid,
                sseqid=row.sseqid,
                pident=row.pident,
                length=row.length,
                mismatch=row.mismatch,
                gapopen=row.gapopen,
                qstart=row.qstart,
                qend=row.qend,
                sstart=row.sstart,
                send=row.send,
                evalue=row.evalue,
                bitscore=row.bitscore,
                qcovs=row.qcovs,
            )
            for _, row in df_vh.iterrows()
        ]
        BlastResult.objects.bulk_create(vh_results, batch_size=1000)
        print("Fin de l'enregistrement VH dans la base de données")
        
        # Pour VL
        print("BLAST lancé pour vl")
        df_vl = run_blast(vl_path, db_name, vl_blast_result,
                          evalue = analysis.e_value, 
                          perc_id = analysis.perc_identity,
                          min_coverage = analysis.coverage,
                          max_gaps = analysis.gaps,
                          min_length = analysis.alignment_length)
        
        # Ajout des données d'alignement des domaines VL dans la base de données
        vl_results = [
            BlastResult(
                analysis=analysis,
                vh_or_vl="VL",
                qseqid=row.qseqid,
                sseqid=row.sseqid,
                pident=row.pident,
                length=row.length,
                mismatch=row.mismatch,
                gapopen=row.gapopen,
                qstart=row.qstart,
                qend=row.qend,
                sstart=row.sstart,
                send=row.send,
                evalue=row.evalue,
                bitscore=row.bitscore,
                qcovs=row.qcovs,
            )
            for _, row in df_vl.iterrows()
        ]
        BlastResult.objects.bulk_create(vl_results, batch_size=1000)
        print("Fin de l'enregistrement VL dans la base de données")
        # Résumé de l'analyse dans résult
        analysis.result = (
            f"Fichiers générés :\n"
            f"VH : {vh_path}\n"
            f"VL : {vl_path}\n"
            f"Résultats BLAST VH : {vh_blast_result}\n"
            f"Résultats BLAST VL : {vl_blast_result}"
        )
        print("Résumé de l'analyse fait")
        
    except Exception as e:
        analysis.result = f"Erreur durant le traitement : {str(e)}"
    
    # Annoncer que l'analyse est fini et sauvegarder l'analyse
    analysis.is_processing = False
    analysis.save()
