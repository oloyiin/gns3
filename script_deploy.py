import json
import os
import tempfile
import requests

def generate_config(router_name, router_data):
    # Appeler le script python pour générer la configuration
    script_path = 'scriptFin.py'
    config_generation_command = f"python {script_path} {router_name}"
    generated_config = os.popen(config_generation_command).read()
    return generated_config

def save_temp_config(router_name, router_data):
    temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.cfg', prefix=router_name)
    temp_file.write(generate_config(router_name, router_data))
    temp_file.close()
    return temp_file.name


def import_configuration(router_name, config_file_path):
    # Informations d'authentification pour l'API GNS3
    api_url = 'http://localhost:3080/v2/projects'
    auth = ('votre_nom_utilisateur', 'votre_mot_de_passe')

    # Créer un nouveau projet dans GNS3
    project_data = {'name': f"Projet_{router_name}"}
    response = requests.post(api_url, auth=auth, json=project_data)

    try:
        # Vérifier si la création du projet a réussi (statut HTTP 200)
        response.raise_for_status()
        project_id = response.json()['project_id']
    except requests.exceptions.HTTPError as e:
        print(f"Erreur lors de la création du projet pour {router_name}: {e}")
        return

    # Ajouter un routeur au projet
    router_data = {'name': router_name, 'template': 'c7200', 'project_id': project_id}
    response = requests.post(f"{api_url}/{project_id}/nodes", auth=auth, json=router_data)
    node_id = response.json()['node_id']

    # Importer la configuration dans le routeur
    with open(config_file_path, 'r') as config_file:
        config_data = {'format': 'text', 'path': config_file_path, 'project_id': project_id, 'node_id': node_id}
        requests.post(f"{api_url}/{project_id}/nodes/{node_id}/configs", auth=auth, json=config_data)

if __name__ == "__main__":
    # Chemin vers le dossier contenant les fichiers de configuration
    configs_folder = '/chemin/vers/le/dossier/configs/'

    # Liste des routeurs et de leurs fichiers de configuration
    routers_configs = {'R1': 'R1_startup-config.cfg', 'R2': 'R2_startup-config.cfg', 'R3': 'R3_startup-config.cfg'}

    for router_name, config_file in routers_configs.items():
        config_file_path = os.path.join(configs_folder, config_file)
        import_configuration(router_name, config_file_path)
