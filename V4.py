import csv
from datetime import datetime
import os
import pandas as pd
import plotly.express as px

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
                evenement['Description'] = nettoyer_description(ligne.split(':', 1)[1].strip())

    # Ajouter une description par défaut si elle est manquante
    for evt in evenements:
        if 'Description' not in evt or not evt['Description']:
            evt['Description'] = 'Aucune description disponible.'

    return evenements

def formater_date(date_ics):
    """
    Convertit une date au format ICS (YYYYMMDDTHHMMSSZ) en format lisible (YYYY-MM-DD HH:MM).
    """
    try:
        date_obj = datetime.strptime(date_ics, '%Y%m%dT%H%M%SZ')
        return date_obj
    except ValueError:
        return date_ics  # Retourner la date brute si le format ne correspond pas

def nettoyer_description(description):
    """
    Nettoie la description en supprimant les sauts de ligne et les mentions de date d'exportation.
    """
    description = description.replace('\n', ' ').strip()
    if 'Date d\'exportation' in description:
        description = description.split('Date d\'exportation')[0].strip()
    return description

def filtrer_evenements(evenements):
    """
    Filtre les événements pour ne conserver que ceux de type "TP" et "A1" et appartenant aux mois de septembre,
    octobre, novembre et décembre 2023.
    """
    evenements_filtrés = []
    for evenement in evenements:
        if 'TP' in evenement.get('Résumé', '') and 'A1' in evenement.get('Description', ''):
            date_debut = evenement.get('Début')
            if isinstance(date_debut, datetime):
                if date_debut.year == 2023 and date_debut.month in [9, 10, 11, 12]:
                    evenements_filtrés.append(evenement)
    return evenements_filtrés

def compter_seances_par_mois(evenements):
    """
    Compte le nombre de séances de TP pour chaque mois (septembre, octobre, novembre, décembre 2023).
    """
    mois = {9: 0, 10: 0, 11: 0, 12: 0}
    for evenement in evenements:
        date_debut = evenement.get('Début')
        if isinstance(date_debut, datetime):
            mois[date_debut.month] += 1
    return mois

def afficher_graphe(seances_par_mois):
    """
    Affiche un graphique des séances de TP par mois en utilisant Plotly.
    """
    mois = ['Septembre', 'Octobre', 'Novembre', 'Décembre']
    seances = [seances_par_mois[9], seances_par_mois[10], seances_par_mois[11], seances_par_mois[12]]

    # Créer un DataFrame Pandas
    df = pd.DataFrame({
        'Mois': mois,
        'Séances de TP': seances
    })

    # Créer un graphique avec Plotly
    fig = px.bar(df, x='Mois', y='Séances de TP', title="Nombre de séances de TP du groupe A1 (Septembre - Décembre 2023)", labels={'Séances de TP': 'Nombre de séances'})
    
    # Sauvegarder le graphique en PNG
    fig.write_image("seances_tp_A1.png")
    fig.show()

def main():
    """
    Fonction principale pour exécuter le programme.
    """
    # Demander le nom du fichier ICS à lire
    nom_fichier_ics = input("Entrez le nom du fichier ICS à analyser (sans extension) : ").strip()
    if not nom_fichier_ics.endswith('.ics'):
        nom_fichier_ics += '.ics'

    if not os.path.exists(nom_fichier_ics):
        print(f"Erreur : Le fichier '{nom_fichier_ics}' n'existe pas.")
        return

    # Lire et extraire les données du fichier ICS
    evenements = lire_fichier_ics(nom_fichier_ics)

    # Filtrer les événements (TP pour le groupe A1 en 2023)
    evenements_filtrés = filtrer_evenements(evenements)

    # Compter les séances par mois
    seances_par_mois = compter_seances_par_mois(evenements_filtrés)

    # Afficher le graphique
    afficher_graphe(seances_par_mois)

if __name__ == "__main__":
    main()
