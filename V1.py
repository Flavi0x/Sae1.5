import csv

def lire_fichier_ics(nom_fichier):
    """
    Lit le contenu du fichier .ics et extrait les données de l'activité.
    """
    with open(nom_fichier, 'r', encoding='utf-8') as fichier:
        lignes = fichier.readlines()
    
    evenement = {}
    for ligne in lignes:
        if ligne.startswith('SUMMARY:'):
            evenement['Résumé'] = ligne.split(':', 1)[1].strip()
        elif ligne.startswith('DTSTART:'):
            evenement['Début'] = ligne.split(':', 1)[1].strip()
        elif ligne.startswith('DTEND:'):
            evenement['Fin'] = ligne.split(':', 1)[1].strip()
        elif ligne.startswith('LOCATION:'):
            evenement['Lieu'] = ligne.split(':', 1)[1].strip()
        elif ligne.startswith('DESCRIPTION:'):
            evenement['Description'] = ligne.split(':', 1)[1].strip()
    
    return evenement

def convertir_en_csv(evenement, nom_fichier_csv):
    """
    Convertit les données extraites en pseudo-code CSV.
    """
    with open(nom_fichier_csv, 'w', newline='', encoding='utf-8') as fichier_csv:
        writer = csv.writer(fichier_csv)
        # Écrire l'en-tête
        writer.writerow(['Résumé', 'Début', 'Fin', 'Lieu', 'Description'])
        # Écrire les données
        writer.writerow([
            evenement.get('Résumé', ''),
            evenement.get('Début', ''),
            evenement.get('Fin', ''),
            evenement.get('Lieu', ''),
            evenement.get('Description', '')
        ])

def main():
    """
    Fonction principale pour exécuter le programme.
    """
    # Nom du fichier ICS à lire
    nom_fichier_ics = 'ADE_RT1_Septembre2023_Decembre2023.ics'
    # Nom du fichier CSV de sortie
    nom_fichier_csv = 'ADE_RT1_Septembre2023_Decembre2023.csv'

    # Lire et extraire les données du fichier ICS
    evenement = lire_fichier_ics(nom_fichier_ics)

    # Convertir les données en format CSV
    convertir_en_csv(evenement, nom_fichier_csv)

    print(f"Les données ont été converties et enregistrées dans {nom_fichier_csv}")

if __name__ == "__main__":
    main()
