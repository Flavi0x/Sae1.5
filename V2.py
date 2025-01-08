import csv
from datetime import datetime
import os

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
        return date_obj.strftime('%Y-%m-%d %H:%M')
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

def convertir_en_csv(evenements, nom_fichier_csv):
    """
    Convertit les données extraites en pseudo-code CSV.
    Remplit les cases vides avec "vide".
    """
    with open(nom_fichier_csv, 'w', newline='', encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv)
        # Écrire l'en-tête
        writer.writerow(['Résumé', 'Début', 'Fin', 'Lieu', 'Description'])
        # Écrire les données des événements
        for evenement in evenements:
            writer.writerow([
                evenement.get('Résumé', 'vide') or 'vide',
                evenement.get('Début', 'vide') or 'vide',
                evenement.get('Fin', 'vide') or 'vide',
                evenement.get('Lieu', 'vide') or 'vide',
                evenement.get('Description', 'vide') or 'vide'
            ])

def main():
    """
    Fonction principale pour exécuter le programme.
    """
    # Demander le nom du fichier ICS à lire
    nom_fichier_ics = input("Entrez le nom du fichier ICS à convertir (sans extension) : ").strip()
    if not nom_fichier_ics.endswith('.ics'):
        nom_fichier_ics += '.ics'

    if not os.path.exists(nom_fichier_ics):
        print(f"Erreur : Le fichier '{nom_fichier_ics}' n'existe pas.")
        return

    # Nom du fichier CSV de sortie
    nom_fichier_csv = nom_fichier_ics.replace('.ics', '.csv')

    # Lire et extraire les données du fichier ICS
    evenements = lire_fichier_ics(nom_fichier_ics)

    # Convertir les données en format CSV
    convertir_en_csv(evenements, nom_fichier_csv)

    print(f"Les données ont été converties et enregistrées dans {nom_fichier_csv}")

    # Ouvrir le fichier CSV après sa création
    os.startfile(nom_fichier_csv)

if __name__ == "__main__":
    main()
