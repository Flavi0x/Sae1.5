import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Fichiers d'entrée/sortie
tcpdump_file = "tcpdump.txt"  # Fichier contenant les logs réseau (capturé avec tcpdump)
csv_output_file = "network_traffic.csv"  # Fichier de sortie pour stocker les données analysées sous forme CSV
suspicious_report_file = "suspicious_activity_report.md"  # Rapport détaillé des activités suspectes
graph_output_file = "network_traffic_graphs.png"  # Graphiques pour visualiser les tendances du trafic réseau

# Étape 1 : Charger les données du fichier tcpdump
# Cette section lit les logs réseau et extrait les informations pertinentes.
print("Analyse du fichier tcpdump...")
with open(tcpdump_file, 'r', encoding="utf-8") as file:
    data = file.readlines()

# Regex pour extraire les données réseau (heure, IP source/destination, flags TCP et taille des paquets)
pattern = r"(\d{2}:\d{2}:\d{2}\.\d+)\s+IP\s+(\S+)\s>\s(\S+):\sFlags\s+\[(\S+)\],.*length\s+(\d+)"
records = []

# Boucle pour analyser chaque ligne du fichier tcpdump
for line in data:
    match = re.search(pattern, line)
    if match:
        time, src_ip, dest_ip, flags, length = match.groups()
        records.append({
            "Heure": time,  # Horodatage du paquet
            "IP Source": src_ip,  # Adresse IP source
            "IP Destination": dest_ip,  # Adresse IP destination
            "Flags": flags,  # Flags TCP (ex : SYN, ACK, FIN)
            "Longueur": int(length)  # Taille du paquet
        })

# Convertir les données extraites en DataFrame pour les manipuler facilement
df = pd.DataFrame(records)

# Sauvegarde des données dans un fichier CSV
print(f"Génération du fichier CSV : {csv_output_file}...")
df.to_csv(csv_output_file, index=False)

# Étape 2 : Détection de menaces
print("Détection de menaces potentielles...")
suspicious_activity = []

# 1. Détection DDoS : 
# Une attaque DDoS (Distributed Denial of Service) se caractérise par un grand nombre de connexions provenant d'une ou plusieurs IPs sources.
connections_per_source = df["IP Source"].value_counts()  # Nombre de connexions par IP source
threshold_ddos = 100  # Seuil pour identifier les IPs suspectes (exemple arbitraire)
suspicious_ips_ddos = connections_per_source[connections_per_source > threshold_ddos].index.tolist()

if suspicious_ips_ddos:
    suspicious_activity.append("**DDoS possible :** IP(s) source avec trop de connexions")
    for ip in suspicious_ips_ddos:
        suspicious_activity.append(f"- {ip} : {connections_per_source[ip]} connexions détectées")

# 2. Détection de flood : 
# Identifie les IPs qui envoient un grand nombre de paquets de petite taille (généralement utilisé dans les attaques par inondation).
short_packets = df[df["Longueur"] < 50]  # Filtrer les paquets courts
short_packet_counts = short_packets["IP Source"].value_counts()  # Comptage des paquets courts par IP source
threshold_flood = 50  # Seuil pour détecter un flood (exemple arbitraire)
suspicious_ips_flood = short_packet_counts[short_packet_counts > threshold_flood].index.tolist()

if suspicious_ips_flood:
    suspicious_activity.append("**Flood possible :** IP(s) envoyant beaucoup de paquets courts")
    for ip in suspicious_ips_flood:
        suspicious_activity.append(f"- {ip} : {short_packet_counts[ip]} paquets courts détectés")

# 3. Anomalies TCP : 
# Analyse des flags TCP pour identifier des comportements inhabituels (par exemple, un grand nombre de SYN ou de FIN sans réponse).
flag_counts = Counter(df["Flags"])  # Comptage des occurrences de chaque flag TCP
suspicious_activity.append("**Statistiques des flags TCP :**")
for flag, count in flag_counts.items():
    suspicious_activity.append(f"- {flag} : {count} occurrences")

# Étape 3 : Génération du rapport Markdown
# Génère un rapport des résultats détectés sous forme de fichier Markdown
print(f"Génération du rapport Markdown : {suspicious_report_file}...")
markdown_content = f"""
# Rapport de Détection de Menaces Réseau

## Résumé des Résultats
- Nombre total de paquets analysés : **{len(df)}**
- Nombre d'adresses IP sources uniques : **{df["IP Source"].nunique()}**
- Nombre d'adresses IP destinations uniques : **{df["IP Destination"].nunique()}**

## Menaces Potentielles Détectées
{''.join([f"<br>{item}" for item in suspicious_activity])}

## Statistiques Complètes
### Connexions par IP Source (Top 10)
{connections_per_source.head(10).to_markdown(index=False)}

### Paquets Courts par IP Source (Top 10)
{short_packet_counts.head(10).to_markdown(index=False)}
"""

# Sauvegarder le fichier Markdown
with open(suspicious_report_file, "w", encoding="utf-8") as file:
    file.write(markdown_content)

# Étape 4 : Génération des graphiques
# Crée des graphiques pour visualiser les connexions et paquets courts par IP source.
print(f"Génération des graphiques : {graph_output_file}...")
plt.figure(figsize=(12, 6))

# Graphique 1: Connexions par IP Source
plt.subplot(1, 2, 1)
connections_per_source.head(10).plot(kind="bar", color='skyblue', title="Top 10 des Connexions par IP Source", xlabel="IP Source", ylabel="Nombre de Connexions")
plt.xticks(rotation=45, ha='right')

# Graphique 2: Paquets Courts par IP Source
plt.subplot(1, 2, 2)
short_packet_counts.head(10).plot(kind="bar", color='orange', title="Top 10 des Paquets Courts par IP Source", xlabel="IP Source", ylabel="Nombre de Paquets Courts")
plt.xticks(rotation=45, ha='right')

plt.tight_layout()
plt.savefig(graph_output_file)
