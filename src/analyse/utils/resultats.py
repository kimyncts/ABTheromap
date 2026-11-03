from matplotlib_venn import venn2
import matplotlib.pyplot as plt
from Bio import SeqIO
import io
import base64

def generate_venn_image(vh_set, vl_set, as_base64=True):
    """
    Génère un diagramme de Venn à partir de deux ensembles et retourne l'image encodée en base64.
    """
    plt.figure(figsize=(5, 5))
    venn = venn2([vh_set, vl_set], set_labels=('VH', 'VL'))
    
    # Couleurs du diagramme 
    if venn.get_patch_by_id('10'):
        venn.get_patch_by_id('10').set_color('#f9d6de')  # VH seul
    if venn.get_patch_by_id('01'):
        venn.get_patch_by_id('01').set_color('#c9d9f8')  # VL seul
    if venn.get_patch_by_id('11'):
        venn.get_patch_by_id('11').set_color('#d2b1f4')  # Intersection
    
    # Uniformiser la transparence 
    for subset in ('10', '01', '11'):
        patch = venn.get_patch_by_id(subset)
        if patch:
            patch.set_alpha(0.8)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    
    if as_base64:
        return base64.b64encode(buf.read()).decode('utf-8')
    else:
        return buf

def get_sequence_from_fasta(fasta_path, clone_id):
    """
    Récupère la séquence dont l'id commence par clone_id + '_H', '_L' ou '_K' dans le fichier fasta_path.
    """
    for record in SeqIO.parse(fasta_path, "fasta"):
        if record.id.startswith(f"{clone_id}_"):
            return str(record.seq)
    return None
