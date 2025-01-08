import os
from datetime import datetime
import matplotlib.pyplot as plt


def lire_fichier_ics(nom_fichier):
    """
    Lit le fichier ICS et extrait les événements.
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
            elif ligne.startswith('DESCRIPTION:'):
                evenement['Description'] = ligne.split(':', 1)[1].strip()

    return evenements


def formater_date(date_ics):
    """
    Convertit une date ICS (YYYYMMDDTHHMMSSZ) en objet datetime.
    """
    try:
        return datetime.strptime(date_ics, '%Y%m%dT%H%M%SZ')
    except ValueError:
        return None


def compter_seances_par_mois(evenements):
    """
    Compte le nombre de séances de TP du groupe A1 par mois.
    """
    mois_noms = ['Septembre', 'Octobre', 'Novembre', 'Décembre']
    mois_indices = {9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'}
    mois_counts = {mois: 0 for mois in mois_noms}

    for evt in evenements:
        if 'TP' in evt.get('Résumé', '') and 'A1' in evt.get('Description', ''):
            date = evt.get('Début')
            if date and date.month in mois_indices:
                mois = mois_indices[date.month]
                mois_counts[mois] += 1

    return mois_counts


def creer_graphe(mois_counts, nom_fichier_png):
    """
    Crée et exporte un graphique montrant les séances de TP par mois.
    """
    mois = list(mois_counts.keys())
    valeurs = list(mois_counts.values())

    plt.figure(figsize=(10, 6))
    plt.bar(mois, valeurs, color='skyblue', edgecolor='black')
    plt.title("Séances de TP du groupe A1 (2023)", fontsize=16)
    plt.xlabel("Mois", fontsize=14)
    plt.ylabel("Nombre de séances", fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Exportation du graphique
    plt.savefig(nom_fichier_png, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Graphe exporté avec succès : {nom_fichier_png}")


def main():
    """
    Fonction principale du programme.
    """
    # Demander le nom du fichier ICS
    nom_fichier_ics = input("Entrez le nom du fichier ICS (avec extension) : ").strip()
    if not os.path.exists(nom_fichier_ics):
        print(f"Erreur : Le fichier '{nom_fichier_ics}' n'existe pas.")
        return

    # Lire les événements du fichier ICS
    evenements = lire_fichier_ics(nom_fichier_ics)

    # Compter les séances par mois
    mois_counts = compter_seances_par_mois(evenements)

    # Afficher les résultats
    print("\nNombre de séances par mois :")
    for mois, count in mois_counts.items():
        print(f"{mois} : {count} séances")

    # Générer et exporter le graphique
    nom_fichier_png = nom_fichier_ics.replace('.ics', '_graphe.png')
    creer_graphe(mois_counts, nom_fichier_png)


if __name__ == "__main__":
    main()
