# ABTheroMap

**ABTheroMap** est une interface web développée dans le cadre de leur projet de fin d’année pour le programme européen **ABCardionostics**, porté par l’équipe Théranostic de l’Athérosclérose du CRMSB (Centre de Résonance Magnétique des Systèmes Biologiques).

## Description

ABTheroMap facilite la comparaison entre des séquences issues de la plateforme **IMGT/HighV-QUEST** et des banques de données expérimentales.

### Fonctionnalités principales :

- Upload de deux fichiers :
  - **Un fichier `.txt`** issu de l’outil IMGT/HighV-QUEST contenant les séquences requêtes.
  - **Un fichier `.fasta`** constituant la base de données de recherche BLAST.
- Extraction automatique des séquences **VH** et **VL**, correctement annotées, dans deux fichiers séparés.
- Alignement local de ces séquences via **BLAST+**, avec interface graphique pour configurer les paramètres d’alignement (e.g. e-value, identity, coverage...).
- Affichage des résultats avec options de tri, filtrage, export Excel et visualisation (ex : diagrammes de Venn interactifs).

### Prérequis :

- Python 3.10+
- [Podman](https://podman.io/) ou Docker
- Docker Compose ou Podman Compose
- ncbi-blast+ [Télécharger ici](https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.16.0+-x64-linux.tar.gz)

## Gallery / Demo

### 1. User Registration

[![ABTheroMap Registration](docs/images/inscription.png)](https://github.com/kimyncts/ABTheromap/raw/refs/heads/main/src/aide/static/images/aide/inscription_ABTheroMap.mp4)

### 2. Sequence Analysis

[![ABTheroMap Sequence Analysis](docs/images/connexion.png)](https://github.com/kimyncts/ABTheromap/raw/refs/heads/main/src/aide/static/images/aide/analyse_ABTheroMap.mp4)
Equipe : Emma Eveilleau, Kimsay Nacitas, Marion Turgault et Sarah Toubal 

