import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import markdown

def lire_fichier_ics(nom_fichier):
    """
    Lit le contenu du fichier .ics et extrait les données de tous les événements.
    """
    with open(nom_fichier, 'r', encoding='utf-8') as fichier:
        lignes = fichier.readlines()

    evenements = []
    evenement = {}
    dans_evenement = False

    for ligne in lignes:
        ligne = ligne.strip()
        if ligne == 'BEGIN:VEVENT':
            dans_evenement = True
            evenement = {}
        elif ligne == 'END:VEVENT':
            dans_evenement = False
            evenements.append(evenement)
        elif dans_evenement:
            if ligne.startswith('SUMMARY:'):
                evenement['Résumé'] = ligne.split(':', 1)[1].strip()
            elif ligne.startswith('DTSTART:'):
                evenement['Début'] = formater_date(ligne.split(':', 1)[1].strip())
            elif ligne.startswith('DTEND:'):
                evenement['Fin'] = formater_date(ligne.split(':', 1)[1].strip())
            elif ligne.startswith('LOCATION:'):
                evenement['Lieu'] = ligne.split(':', 1)[1].strip()
            elif ligne.startswith('DESCRIPTION:'):
                evenement['Description'] = ligne.split(':', 1)[1].strip()

    return evenements

def formater_date(date_ics):
    """
    Convertit une date au format ICS (YYYYMMDDTHHMMSSZ) en objet datetime.
    """
    try:
        return datetime.strptime(date_ics, '%Y%m%dT%H%M%SZ')
    except ValueError:
        return None

def convertir_en_csv_matiere_7_b1(evenements, nom_fichier_csv):
    """
    Convertit les événements pour la matière 7 et le groupe B1 en un fichier CSV.
    """
    with open(nom_fichier_csv, 'w', newline='', encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv)
        writer.writerow(['Résumé', 'Début', 'Fin', 'Lieu', 'Description'])
        for evenement in evenements:
            if '7' in evenement.get('Résumé', '') and 'B1' in evenement.get('Description', ''):
                writer.writerow([
                    evenement.get('Résumé', ''),
                    evenement.get('Début', '').strftime('%Y-%m-%d %H:%M') if evenement.get('Début') else '',
                    evenement.get('Fin', '').strftime('%Y-%m-%d %H:%M') if evenement.get('Fin') else '',
                    evenement.get('Lieu', ''),
                    evenement.get('Description', '')
                ])

def creer_graphe_repartition_tous_mois(evenements, groupe, nom_fichier_png):
    """
    Crée un diagramme circulaire montrant la répartition des événements par mois
    pour le groupe spécifié (présent dans la description).
    """
    mois_noms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
    mois_counts = [0] * 12

    for evenement in evenements:
        if groupe in evenement.get('Description', ''):
            date = evenement.get('Début')
            if date:
                mois_counts[date.month - 1] += 1

    mois_utilises = [mois_noms[i] for i in range(12) if mois_counts[i] > 0]
    valeurs_utilisees = [mois_counts[i] for i in range(12) if mois_counts[i] > 0]

    # Créer le diagramme avec une taille réduite
    plt.figure(figsize=(6, 6))  # Taille réduite : 6x6 pouces
    plt.pie(valeurs_utilisees, labels=mois_utilises, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20.colors)
    plt.title(f"Répartition des séances par mois (Groupe {groupe})")
    plt.savefig(nom_fichier_png, dpi=300, bbox_inches='tight')
    plt.close()

def generer_html(tableau_csv, image_diagramme, fichier_html):
    """
    Génère un fichier HTML contenant un tableau et une image de diagramme circulaire.
    """
    contenu_tableau = ""
    if os.path.exists(tableau_csv):
        with open(tableau_csv, 'r', encoding='utf-8') as f:
            lignes = f.readlines()
            contenu_tableau += "<table border='1'>\n"
            for i, ligne in enumerate(lignes):
                colonnes = ligne.strip().split(',')
                if i == 0:
                    contenu_tableau += "<thead><tr>" + "".join(f"<th>{col}</th>" for col in colonnes) + "</tr></thead>\n"
                else:
                    contenu_tableau += "<tr>" + "".join(f"<td>{col}</td>" for col in colonnes) + "</tr>\n"
            contenu_tableau += "</table>\n"

    contenu_markdown = f"""
# Résultats des Travaux :

## Tableau des Séances (Matière 7, Groupe B1) :
{contenu_tableau}

## Diagramme Circulaire (Répartition par mois pour le groupe A1) :

![Diagramme Circulaire](./{os.path.basename(image_diagramme)})
"""

    html = markdown.markdown(contenu_markdown, extensions=['extra'])

    html_complet = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travaux Python</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    {html}
</body>
</html>
"""

    with open(fichier_html, 'w', encoding='utf-8') as f:
        f.write(html_complet)

    print(f"Fichier HTML généré : {fichier_html}")

def main():
    nom_fichier_ics = input("Entrez le nom du fichier ICS (avec extension) : ").strip()
    if not os.path.exists(nom_fichier_ics):
        print(f"Erreur : Le fichier '{nom_fichier_ics}' n'existe pas.")
        return

    tableau_csv = "evenements_matiere7_b1.csv"
    image_diagramme = "evenements_a1.png"
    fichier_html = "resultats.html"

    evenements = lire_fichier_ics(nom_fichier_ics)
    convertir_en_csv_matiere_7_b1(evenements, tableau_csv)
    creer_graphe_repartition_tous_mois(evenements, "A1", image_diagramme)
    generer_html(tableau_csv, image_diagramme, fichier_html)

    os.startfile(fichier_html)

if __name__ == "__main__":
    main()
