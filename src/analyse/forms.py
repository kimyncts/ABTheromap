from django import forms
from .models import Analysis

class AnalysisForm(forms.ModelForm):
    class Meta:
        model = Analysis
        fields = [
            'name', 'description', 'coverage', 'e_value',
            'gaps', 'alignment_length', 'perc_identity', 'seq_file', 'ngs_file'
        ]
        labels = {
            'name': 'Titre de l\'analyse',
            'coverage' : 'Couverture minimale',
            'e_value': 'Seuil de E-value',
            'gaps': 'Nombre de Gaps authorisé',
            'alignment_length' : 'Longueur minimale d\'alignement',
            'perc_identity' : 'Pourcentage d\'identité',
            'seq_file': 'Fichier "3-Nt-sequences.txt" issue de l\'outil IMGT (.txt)',
            'ngs_file': 'Fichier NGS (.fasta)'
        }
        help_texts = {
            'name': 'Entrez un titre clair pour identifier facilement votre analyse dans l’historique.',
            'description': 'Décrivez brièvement l’objectif ou le contexte de cette analyse.',
            'coverage': 'Nombre minimal de bases en pourcentage devant être alignées pour valider un résultat (ex: 85%).',
            'e_value': 'Seuil de significativité BLAST. Plus la valeur est petite, plus le résultat est fiable (ex: 1e-5).',
            'gaps': 'Nombre maximal de gaps (insertions ou délétions) autorisés dans l’alignement.',
            'alignment_length': 'Longueur minimale (en pb) pour qu’un alignement soit pris en compte.',
            'perc_identity': 'Pourcentage minimal d’identité entre les séquences alignées (ex: 95%).',
            'seq_file': 'Fichier de séquences exporté depuis l\'outil IMGT. Format requis : .txt.',
            'ngs_file': 'Fichier de séquences issues du séquençage NGS constituant la base de données. Format requis : .fasta.',
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nom de l'analyse"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Description..."}),
            "coverage": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100}),
            "e_value": forms.NumberInput(attrs={"class": "form-control", "step": "1e-6", "min": 0}),
            "gaps": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "alignment_length": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "perc_identity": forms.NumberInput(attrs={"class": "form-control", "step": 0.1, "min": 0, "max": 100}),
            "seq_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "ngs_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        seq_file = cleaned_data.get('seq_file')
        ngs_file = cleaned_data.get('ngs_file')

        valid_seq_extensions = ['.txt']
        valid_ngs_extensions = ['.fasta', '.fa', '.fna']

        if seq_file:
            # Vérification extension
            if not any(seq_file.name.lower().endswith(ext) for ext in valid_seq_extensions):
                self.add_error('seq_file', 'Le fichier "3-Nt-sequences.txt" IMGT doit être au format .txt')
            else:
                # Vérification contenu du fichier
                seq_file.seek(0)  # Revenir au début du fichier
                content = seq_file.read().decode('utf-8', errors='ignore')  # Lire le contenu en texte
                if 'V-REGION' not in content or 'V-DOMAIN ID' not in content:
                    self.add_error('seq_file', 'Le fichier .txt doit contenir les chaînes "V-REGION" et "V-DOMAIN ID".')

        if ngs_file:
            if not any(ngs_file.name.lower().endswith(ext) for ext in valid_ngs_extensions):
                self.add_error('ngs_file', "Le fichier NGS doit être au format .fasta, .fa ou .fna")

        return cleaned_data
