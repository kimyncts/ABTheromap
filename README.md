# ABTheroMap - scfv-analysis-interface

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

### Full Demo

[<img width="1679" height="877" alt="ABTheroMap" src="https://github.com/user-attachments/assets/f52b370f-514b-4ed3-8889-170238aa99c9" />](https://github.com/kimyncts/ABTheromap/raw/refs/heads/main/src/aide/static/images/aide/ABTM.mp4)

### User Registration

[<img width="1914" height="973" alt="User Registration" src="https://github.com/user-attachments/assets/3efab123-a899-4ddf-9aad-993b33cb2c08" />](https://github.com/kimyncts/ABTheromap/raw/refs/heads/main/src/aide/static/images/aide/inscription_ABTheroMap.mp4)

### Sequence Analysis

[<img width="1846" height="808" alt="Sequence Analysis" src="https://github.com/user-attachments/assets/9cabb315-bf48-4cf7-bbae-c700eca7e472" />](https://github.com/kimyncts/ABTheromap/raw/refs/heads/main/src/aide/static/images/aide/analyse_outil.mp4)

### User Logout

[<img width="1882" height="807" alt="User Logout" src="https://github.com/user-attachments/assets/bfc96ced-22e6-403c-bff6-fd4d592400bb" />](https://github.com/kimyncts/ABTheromap/raw/refs/heads/main/src/aide/static/images/aide/Deconnexion_ABTheroMap.mp4)

Equipe : Emma Eveilleau, Kimsay Nacitas, Marion Turgault et Sarah Toubal 

