import re
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Fichiers d'entrée/sortie
tcpdump_file = "tcpdump.txt"
csv_output_file = "network_traffic.csv"
suspicious_report_file = "suspicious_activity_report.md"
graph_output_file = "network_traffic_graphs.png"

# Étape 1 : Charger les données du fichier tcpdump
print("Analyse du fichier tcpdump...")
with open(tcpdump_file, 'r', encoding="utf-8") as file:
    data = file.readlines()

# Regex pour extraire les données
pattern = r"(\d{2}:\d{2}:\d{2}\.\d+)\s+IP\s+(\S+)\s>\s(\S+):\sFlags\s+\[(\S+)\],.*length\s+(\d+)"
records = []

for line in data:
    match = re.search(pattern, line)
    if match:
        time, src_ip, dest_ip, flags, length = match.groups()
        records.append({
            "Heure": time,
            "IP Source": src_ip,
            "IP Destination": dest_ip,
            "Flags": flags,
            "Longueur": int(length)
        })

# Convertir les données en DataFrame
df = pd.DataFrame(records)

# Sauvegarde des données dans un fichier CSV
print(f"Génération du fichier CSV : {csv_output_file}...")
df.to_csv(csv_output_file, index=False)

# Étape 2 : Détection de menaces
print("Détection de menaces potentielles...")
suspicious_activity = []

# 1. Détection DDoS : IPs avec beaucoup de connexions en peu de temps
connections_per_source = df["IP Source"].value_counts()
threshold_ddos = 100  # Seuil arbitraire pour détection
suspicious_ips_ddos = connections_per_source[connections_per_source > threshold_ddos].index.tolist()

if suspicious_ips_ddos:
    suspicious_activity.append("**DDoS possible :** IP(s) source avec trop de connexions")
    for ip in suspicious_ips_ddos:
        suspicious_activity.append(f"- {ip} : {connections_per_source[ip]} connexions détectées")

# 2. Détection de flood : Paquets courts provenant d'une même source
short_packets = df[df["Longueur"] < 50]
short_packet_counts = short_packets["IP Source"].value_counts()
threshold_flood = 50  # Seuil arbitraire pour flood
suspicious_ips_flood = short_packet_counts[short_packet_counts > threshold_flood].index.tolist()

if suspicious_ips_flood:
    suspicious_activity.append("**Flood possible :** IP(s) envoyant beaucoup de paquets courts")
    for ip in suspicious_ips_flood:
        suspicious_activity.append(f"- {ip} : {short_packet_counts[ip]} paquets courts détectés")

# 3. Anomalies TCP : Activité inhabituelle des flags
flag_counts = Counter(df["Flags"])
suspicious_activity.append("**Statistiques des flags TCP :**")
for flag, count in flag_counts.items():
    suspicious_activity.append(f"- {flag} : {count} occurrences")

# Étape 3 : Génération du rapport Markdown
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

# Étape 5 : Générer la page web avec le rapport Markdown et les graphiques
html_content = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport de Détection de Menaces Réseau</title>
</head>
<body>
    <h1>Rapport de Détection de Menaces Réseau</h1>
    <p><strong>Résumé des résultats :</strong></p>
    <ul>
        <li>Nombre total de paquets analysés : {len(df)}</li>
        <li>Nombre d'adresses IP sources uniques : {df["IP Source"].nunique()}</li>
        <li>Nombre d'adresses IP destinations uniques : {df["IP Destination"].nunique()}</li>
    </ul>
    <h2>Menaces Potentielles Détectées</h2>
    <p>{''.join([f"<br>{item}" for item in suspicious_activity])}</p>

    <h2>Graphiques :</h2>
    <img src="{graph_output_file}" alt="Graphiques de détection de menaces réseau">

    <h2>Tableaux des Connexions et Paquets Courts par IP Source</h2>
    <h3>Top 10 des Connexions par IP Source</h3>
    {connections_per_source.head(10).to_markdown(index=False)}

    <h3>Top 10 des Paquets Courts par IP Source</h3>
    {short_packet_counts.head(10).to_markdown(index=False)}
</body>
</html>
"""

# Sauvegarder le fichier HTML
html_report_file = "network_traffic_report.html"
with open(html_report_file, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"Page Web générée : {html_report_file}.")
print(f"Fichier Markdown sauvegardé dans {suspicious_report_file}.")
print(f"Fichier CSV sauvegardé dans {csv_output_file}.")
print(f"Graphiques sauvegardés dans {graph_output_file}.")
