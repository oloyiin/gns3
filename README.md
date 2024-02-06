# gns3
Protocole de routage automatique

## Description

This script generates router configurations based on input data provided in JSON format. The configuration includes settings for IPv4 and IPv6 addresses, interfaces, BGP neighbors (both iBGP and eBGP), and routing protocols (OSPF and RIP v2).
Requirements

    Python 3
    JSON file containing network configuration (e.g., intent.json)

## Fonctionnalité du programme 
Le programme permet de créer des fichiers de configuration pour tous les routeurs des AS décrits dans un intent file au format JSON avec les fonctionalités suivantes :

    -Allocation automatisée des sous-réseaux et adresses IP sur chaque lien interne à une AS, ainsi que des adresses IP de loopback
    -Paramétrage du coût OSPF d'un lien
    -Tagging de communautés BGP et mise en place de route-map correspondants
    -Les configurations générées pour chaque routeur seront sauvegardées dans des fichiers distincts dans le répertoire de destination spécifié.
 
## Routing bgp communities 
Les communities pour chaque client en utilsant une route map sont mis en place sous cette fome 

  
  ip community-list expanded ALLOW_Client permit {as_number}:10 
  route-map sendCustCom_{neighbor['name']} permit 40
  match community ALLOW_Client


# Génération Automatique de Configurations de Routeurs

Ce script Python facilite la création automatique de configurations de routeurs réseau en se basant sur les informations fournies dans un fichier JSON. Les configurations générées ciblent principalement les routeurs Cisco utilisant les protocoles BGP, OSPF et RIP v2.

## Fonctions Principales

### `generate_config`

Cette fonction prend le nom du routeur et les données associées en entrée, puis génère une configuration complète pour ce routeur. La configuration inclut des sections pour les interfaces, les protocoles de routage (OSPF et RIP v2), les voisins BGP (iBGP et eBGP), ainsi que d'autres paramètres réseau.

### `write_config_to_file`

Cette fonction prend le nom du routeur, le chemin du fichier de destination et la configuration générée en entrée. Elle crée le dossier de destination s'il n'existe pas, puis écrit la configuration dans un fichier spécifique au routeur.

### `main`

La fonction principale du script. Elle lit les données du fichier JSON d'entrée, génère les configurations pour chaque routeur, et écrit ces configurations dans des fichiers distincts en utilisant la fonction `write_config_to_file`.

### `generate_route_map`

Cette fonction génère une partie de la configuration BGP liée aux filtres de route en fonction du type de voisin BGP (client, peer, provider).

### `generate_route_map_filter`

Cette fonction génère une partie de la configuration BGP liée aux filtres de route basés sur les valeurs de la communauté BGP.

## Utilisation

1. Assurez-vous d'avoir le fichier de données au format JSON (par exemple, `intent.json`) spécifiant les détails des routeurs et de leur configuration.

2. Exécutez le script en utilisant la commande suivante :
   ```bash
   python3 scriptFin.py


## Utilisation du proogramme 

## Structure du JSON
Le JSON est sous la forme suivante 
{
  "AS1": {
    "routers": {
      "Router1": {
        "ASnumber": 65001,
        "routerId": "1.1.1.1",
        "interfaces": {
          "GigabitEthernet0/0": {
            "ipAddress": "2001:DB8::1/64"
          },
          ...
        },
        "ibgpNeighbors": [...],
        "ebgpNeighbors": [...],
        "ipv6Prefix": [...],
        "routingProtocols": [...],
        "filepath": ""
      },
      ...
    }
  },
  ...
}





