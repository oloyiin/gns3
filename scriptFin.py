import json
import os


def generate_config(router_name, router_data):
    as_number = router_data['ASnumber']
    config = f"!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n!\nhostname {router_name}\n!\nboot-start-marker\nboot-end-marker\n!\n!\n!\nno aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n!\n!\n!\n!\n!\n!\nno ip domain lookup\nipv6 unicast-routing\nipv6 cef\n!\n!\nmultilink bundle-name authenticated\n!\n!\n!\n!\n!\n!\n!\n!\n!\nip tcp synwait-time 5\n!\n!\n!\n!\n!\n!\n!\n!\n"

    for interface, data in router_data['interfaces'].items():
        config += f"interface {interface}\n no ip address\n negotiation auto\n"

        if 'ipAddress' in data:
            config += f" ipv6 address {data['ipAddress']}\n ipv6 enable\n"

            for protocol in router_data.get('routingProtocols', []):
                if protocol == 'Ospf':
                    config += f" ipv6 ospf 1 area 0\n"
                elif protocol == 'Rip v2':
                    config += f" ipv6 rip rip{as_number} enable\n"

        config += "!\n"
     
    for protocol in router_data.get('routingProtocols', []):
        if protocol == 'Ospf':
            config += "router ospf 1\n!\n"




    if 'ibgpNeighbors' in router_data or 'ebgpNeighbors' in router_data:
        config += f"router bgp {as_number}\n bgp router-id {router_data['routerId']}\n bgp log-neighbor-changes\n no bgp default ipv4-unicast\n"
        
        for neighbor in router_data.get('ibgpNeighbors', []):
            config += f" neighbor {neighbor['ipAddress']} remote-as {as_number}\n"
            
            if 'loopbackAddress' in neighbor:
                config += f" neighbor {neighbor['loopbackAddress']} remote-as {as_number}\n"
                config += f" neighbor {neighbor['loopbackAddress']} update-source loopback0\n"
            
            # Ajoute la local preference s'il est spécifié
            config += f" neighbor {neighbor['ipAddress']} local-preference {neighbor.get('localPreference')}\n"
        
        for neighbor in router_data.get('ebgpNeighbors', []):
            config += f" neighbor {neighbor['ipAddress']} remote-as {neighbor['remoteAs']}\n"
            
            # Ajoute la local preference s'il est spécifié
            config += f" neighbor {neighbor['ipAddress']} local-preference {neighbor.get('localPreference')}\n"

        config += " !\n address-family ipv4\n exit-address-family\n"
        config += " address-family ipv6\n"
        
        for neighbor in router_data.get('ibgpNeighbors', []):
            config += f"  neighbor {neighbor['ipAddress']} activate\n"
            
        for neighbor in router_data.get('ebgpNeighbors', []):
            config += f"  neighbor {neighbor['ipAddress']} activate\n"
            
        for prefix in router_data.get('ipv6Prefix', []):
            config += f"  network {prefix}\n"
        
        config += " exit-address-family\n!\n"




    config += "ip forward-protocol nd\n!\n!\nno ip http server\nno ip http secure-server\n!\n"
    
    for protocol in router_data.get('routingProtocols', []):
        if protocol == 'Ospf':
            config += "ipv6 router ospf 1\n"
            config += f"router-id {router_data['routerId']}\n!"
            config += "redistribute connected subnets\n"
        elif protocol == 'Rip v2':
            config += f"router rip rip{as_number}\n redistribute connected\n!\n"

    config+= "\n!\n!\ncontrol-plane\n!\n!\nline con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline vty 0 4\n login\n!\n!\nend"

    return config


def write_config_to_file(router_name, config):
    destination_folder = r'C:\Users\ilhem\GNS3\projects\projet GNS3\project-files\dynamips'
    router_folder = os.path.join(destination_folder, f'router_{router_name}\configs')

    # Crée le dossier du routeur s'il n'existe pas
    if not os.path.exists(router_folder):
        os.makedirs(router_folder)

    # Écrit la configuration dans le fichier
    file_path = os.path.join(router_folder, f'{router_name}_startup-config.cfg')
    with open(file_path, 'w') as output_file:
        output_file.write(config)

    print(f"Configuration for {router_name} saved to {file_path}")

def main():
    with open('intent.json', 'r') as file:
        data = json.load(file)

    for as_number, as_data in data.items():
        if 'routers' in as_data:
            for router_name, router_data in as_data['routers'].items():
                config = generate_config(router_name, router_data)
                with open(f'{router_name}_startup-config.cfg', 'w') as output_file:
                    output_file.write(config)
                print(f"Configuration for {router_name} in {as_number} saved to {router_name}_startup-config.cfg")
        else:
            print(f"No routers found for AS{as_number}")

    
    for as_number, as_data in data.items():
        for router_name, router_data in as_data['routers'].items():
            config = generate_config(router_name, router_data)
            #write_config_to_file(router_name, config)


if __name__ == "__main__":
    main()
