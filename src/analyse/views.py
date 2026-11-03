# Importation des librairies nécessaires
from io import BytesIO
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
import pandas as pd
from analyse.models import Analysis, BlastResult
from .forms import AnalysisForm
from django.utils import timezone
from django.db import transaction
from .tasks import traiter_analyse_async
from .utils.resultats import generate_venn_image, get_sequence_from_fasta
import re
import os


@login_required
##### Vérification des données du formulaire 
def nouvelle_analyse(request):
    """ Si le formulaire est valide, on crée une analyse (class Analysis), on initialise le processig à True et on stock la date et l'heure du début de l'analyse
    puis on redirige la page html vers la vue chargement. 
    Si le formulaire n'est pas valide, on renvoie un formulaire vide et on affiche à nouveau la page html du formulaire.  
    """
    if request.method == 'POST':
        # On crée une instance appartenant à la classe AnalysisForm qui contient les données textuelles et les fichiers
        form = AnalysisForm(request.POST, request.FILES) 
        
        if form.is_valid(): # Verifie que les données du formulaire sont valide (=conforme au model dans models.py)
            # Création de l'analyse
            analysis = form.save(commit=False) #crée l'objet analyse mais enregistre pas tout de suite dans la base de données car commit = False
            #Ajoute et modification des champs qui ne sont pas demandé dans le formulaire
            analysis.start_time = timezone.now()
            analysis.is_processing = True
            analysis.user = request.user
            # Sauvegarde dans la base de données
            analysis.save()
            
            # Traitement en arrière plan (asynchrone) 
            transaction.on_commit(lambda: traiter_analyse_async.delay(analysis.pk))
            print("c'est lancé !")
            # Redirection immédiate vers la page de chargement
            #return render (request, 'analyse/chargement.html', {'analysis': analysis}) 
            return redirect('afficher_chargement', pk=analysis.pk)
            
    else:
        # Formulaire vide
        form = AnalysisForm()
    
    return render(request, 'analyse/index.html', {'form': form})



###### Page de chargement
def afficher_chargement(request, pk):
    """Page de chargement avec rafraîchissement automatique de la page"""
    # Récupération de l'object Analysis correspondant à la clé primaire (pk), sinon renvoie une page d'erreur 404
    analysis = get_object_or_404(Analysis, pk=pk)
    return render(request, 'analyse/chargement.html', {'analysis': analysis})



# Vue d'affichage des résultats dans la page HTML
def resultats_analyse(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk)
    top_n = int(request.GET.get('top', 10))  # valeur par défaut = 10

    # On filtre les résultats associés à cette analyse
    vh_results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VH")
    vl_results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VL")

    # Création d'un dictionnaire {clone_id: count}
    clone_match = {}
    clone_identical_match = {}
    
    for row in vh_results:
        clone_id = re.sub(r'_[HhLlKk]$', '', row.qseqid)
        if clone_id in clone_match:
            clone_match[clone_id] += 1
        else:
            clone_match[clone_id] = 1
        
        if row.pident == 100.0:
            if clone_id in clone_identical_match:
                clone_identical_match[clone_id] += 1
            else:
                clone_identical_match[clone_id] = 1

    for row in vl_results:
        clone_id = re.sub(r'_[HhLlKk]$', '', row.qseqid)
        if clone_id in clone_match:
            clone_match[clone_id] += 1
        else:
            clone_match[clone_id] = 1
        
        if row.pident == 100.0:
            if clone_id in clone_identical_match:
                clone_identical_match[clone_id] += 1
            else:
                clone_identical_match[clone_id] = 1

     # Fusion des données et tri
    combined_data = []
    for clone_id, count in clone_match.items():
        identical = clone_identical_match.get(clone_id, 0)
        combined_data.append((clone_id, count, identical))
        
    # Tri des clones par nombre de match
    sorted_clones = sorted(combined_data, key=lambda x: x[1], reverse=True)
    top_clones = sorted_clones[:top_n]

    context = {
        "analysis": analysis,
        "top_clones": top_clones,
        "top_n": top_n,
    }

    return render(request, 'analyse/resultats.html', context)



def detail_clone(request, pk, clone_id):
    analysis = get_object_or_404(Analysis, pk=pk)

    # On filtre les résultats associés à ce clone
    vh_results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VH", qseqid__istartswith=clone_id)
    vl_results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VL", qseqid__istartswith=clone_id)

    # Diagramme de Venn
    vh_set = set(vh_results.values_list('sseqid', flat=True))
    vl_set = set(vl_results.values_list('sseqid', flat=True))
    
    venn_data = {
        "vh_only": list(vh_set - vl_set),      # Uniquement VH
        "vl_only": list(vl_set - vh_set),      # Uniquement VL
        "both": list(vh_set & vl_set),         # Intersection VH et VL
        "vh_only_count": len(vh_set - vl_set),
        "vl_only_count": len(vl_set - vh_set),
        "both_count": len(vh_set & vl_set),
    }
    
    venn_image = generate_venn_image(vh_set, vl_set, as_base64=True)
    
    # Séquence des clones 
    vh_seq_file =os.path.join(settings.MEDIA_ROOT, f"analysis_{analysis.id}/split-VH_VL/VH_sequences_{analysis.id}.fasta") 
    vl_seq_file = os.path.join(settings.MEDIA_ROOT, f"analysis_{analysis.id}/split-VH_VL/VL_sequences_{analysis.id}.fasta")

    vh_sequence = get_sequence_from_fasta(vh_seq_file, clone_id)
    vl_sequence = get_sequence_from_fasta(vl_seq_file, clone_id)
    
    context = {
        "analysis": analysis,
        "clone_id": clone_id,
        "vh_results": vh_results,
        "vl_results": vl_results,
        "venn_data": venn_data,
        "venn_image": venn_image,
        "vh_sequence": vh_sequence,
        "vl_sequence": vl_sequence,
    }
    return render(request, "analyse/detail_clone.html", context)



#### VUE DE TELECHARGEMENT 
# Vue de téléchargement des diagramme de Venn
def telecharger_image(request, pk, clone_id):
    analysis = get_object_or_404(Analysis, pk=pk)

    # Récupérer les résultats VH et VL pour le clone
    vh_results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VH", qseqid__istartswith=clone_id)
    vl_results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VL", qseqid__istartswith=clone_id)

    # Créer les ensembles pour le diagramme de Venn
    vh_set = set(vh_results.values_list('sseqid', flat=True))
    vl_set = set(vl_results.values_list('sseqid', flat=True))

    # Génération de l'image du diagramme de Venn
    venn_image = generate_venn_image(vh_set, vl_set, as_base64=False)  # Fonction à adapter si nécessaire
    
    # Réponse HTTP pour l'image
    response = HttpResponse(venn_image, content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename={clone_id}_venn.png'

    return response

# Vue de téléchargement des tableaux
def telecharger_excel(request, pk):
    format = request.GET.get('format', 'excel').lower()  # format par défaut : excel
    analysis = get_object_or_404(Analysis, pk=pk)
    top_n = int(request.GET.get('top', 10))

    vh_results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VH")
    vl_results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VL")

    clone_match = {}
    clone_identical_match = {}
    
    def extract_clone_id(qseqid):
        return re.sub(r'_[HhLlKk]$', '', qseqid)

    for row in vh_results:
        clone_id = extract_clone_id(row.qseqid)
        clone_match[clone_id] = clone_match.get(clone_id, 0) + 1
        if row.pident == 100.0:
            clone_identical_match[clone_id] = clone_identical_match.get(clone_id, 0) + 1

    # Comptage pour VL
    for row in vl_results:
        clone_id = extract_clone_id(row.qseqid)
        clone_match[clone_id] = clone_match.get(clone_id, 0) + 1
        if row.pident == 100.0:
            clone_identical_match[clone_id] = clone_identical_match.get(clone_id, 0) + 1

    # Fusion et tri
    combined_data = []
    for clone_id, count in clone_match.items():
        identical = clone_identical_match.get(clone_id, 0)
        combined_data.append((clone_id, count, identical))

    sorted_clones = sorted(combined_data, key=lambda x: x[1], reverse=True)
    top_clones = sorted_clones[:top_n]

    df = pd.DataFrame(top_clones, columns=["Clone ID", "Nombre de matchs","Matchs à 100%"])

    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=blast_resultats_{analysis.id}.csv'
        df.to_csv(path_or_buf=response, index=False, sep=';')
    else:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=blast_resultats_{analysis.id}.xlsx'
        df.to_excel(response, index=False)
        
        
    return response


# Vue telecherger les tableaux VH, VL
def telecharger_excel_clone(request, pk, type_clone, clone_id):
    format = request.GET.get('format', 'excel').lower()  # par défaut 'excel'
    # On récupère l'analyse
    analysis = get_object_or_404(Analysis, pk=pk)

    # On récupère les résultats VH ou VL selon le type
    if type_clone == "VH":
        results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VH", qseqid__istartswith=clone_id)
        clone_label = "VH"
    elif type_clone == "VL":
        results = BlastResult.objects.filter(analysis=analysis, vh_or_vl="VL", qseqid__istartswith=clone_id)
        clone_label = "VL"
    else:
        return HttpResponse("Type de clone invalide", status=400)
    
    
    # Création d'un dictionnaire pour les données de chaque clone
    data = []
    for r in results:
        data.append({
            "qseqid": r.qseqid,
            "sseqid": r.sseqid,
            "Identité (%)": r.pident,
            "Longueur": r.length,
            "Mismatch": r.mismatch,
            "Gap open": r.gapopen,
            "qstart": r.qstart,
            "qend": r.qend,
            "sstart": r.sstart,
            "send": r.send,
            "e-value": r.evalue,
            "Bitscore": r.bitscore,
            "qcovs (%)": r.qcovs,
        })

    # Crée un DataFrame avec les résultats
    df = pd.DataFrame(data)

    # Prépare la réponse pour le téléchargement
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=blast_resultats_{analysis.id}_{clone_label}_{clone_id}.csv'
        df.to_csv(path_or_buf=response, index=False, sep=';')
    else:
        # format excel par défaut
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=blast_resultats_{analysis.id}_{clone_label}_{clone_id}.xlsx'
        df.to_excel(response, index=False)
    
    
    return response


@require_POST
def supprimer_analyse(request, analyse_id):
    analyse = get_object_or_404(Analysis, id=analyse_id, user=request.user)
    analyse.delete()
    return redirect('accounts-historique') 
