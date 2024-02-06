import json
import os

# Function to generate route map based on neighbor type
def generate_route_map(neighbor_name, neighbor_type,as_number):
    if neighbor_type == 'customer':
        return f"""
!
route-map SET_LOCAL_PREF_{neighbor_name} permit 10
 set local-preference 200
  set community {as_number}:10
!
"""
    elif neighbor_type == 'peer':
        return f"""
!
route-map SET_LOCAL_PREF_{neighbor_name} permit 20
 set local-preference 150
!
"""
    elif neighbor_type == 'provider':
        return f"""
!
route-map SET_LOCAL_PREF_{neighbor_name} permit 30
 set local-preference 50
!
"""
    else:
        return ""



# Function to generate route map for filtering based on community values
def generate_route_map_filter(config, neighbor,as_number):
    
    config += f"ip community-list expanded ALLOW_Client permit {as_number}:10 \n"
    config += f"route-map sendCustCom_{neighbor['name']} permit 40\n"
    config += f" match community ALLOW_Client\n"
    config += f"!\n"
    
    return config

# Function to generate the router configuration
def generate_config(router_name, router_data):
    as_number = router_data['ASnumber']
    config = f"!\nversion 15.2\nservice timestamps debug datetime msec\nservice timestamps log datetime msec\n!\nhostname {router_name}\n!\nboot-start-marker\nboot-end-marker\n!\n!\n!\nno aaa new-model\nno ip icmp rate-limit unreachable\nip cef\n!\n!\n!\n!\n!\n!\nno ip domain lookup\nipv6 unicast-routing\nipv6 cef\n!\n!\nmultilink bundle-name authenticated\n!\n!\n!\n!\n!\n!\n!\n!\n!\nip tcp synwait-time 5\n!\n!\n!\n!\n!\n!\n!\n!\n"

    # Interface configuration
    for interface, data in router_data['interfaces'].items():
        config += f"interface {interface}\n no ip address\n"

        # Vérifier si l'interface est un voisin eBGP
        is_ebgp_neighbor = any(neighbor['ipAddress'] == data['ipAddress'] for neighbor in router_data.get('ebgpNeighbors', []))
        
        if 'ipAddress' in data:
            config += f" ipv6 address {data['ipAddress']}\n ipv6 enable\n"
            if is_ebgp_neighbor:
                config += f" ipv6 ospf passive-interface {interface}\n"
            else:
                for protocol in router_data.get('routingProtocols', []):
                    if protocol == 'Ospf':
                        config += f" ipv6 ospf 1 area {router_data['area']}\n"
                    # Check if OSPF metric is specified and add the line
                        ospf_metric = router_data.get('OspfMetric')
                        if ospf_metric is not None:
                            config += f" ipv6 ospf cost {ospf_metric}\n"
                    
                        if 'mode' in data:
                            config += f" ipv6 ospf {data['mode']}-interface {interface}\n"
                        
                    elif protocol == 'Rip v2':
                        config += f" ipv6 rip as{as_number} enable\n"
        config += "!\n"



    # Routing protocol configuration
    for protocol in router_data.get('routingProtocols', []):
        if protocol == 'Ospf':
            config += "router ospf 1\n!\n"

    # BGP configuration
    if 'ibgpNeighbors' in router_data or 'ebgpNeighbors' in router_data:
        config += f"router bgp {as_number}\n bgp router-id {router_data['routerId']}\n bgp log-neighbor-changes\n no bgp default ipv4-unicast\n"
        
        # iBGP neighbors configuration
        for neighbor in router_data.get('ibgpNeighbors', []):
            config += f" neighbor {neighbor['ipAddress']} remote-as {as_number}\n"

            if 'loopbackAddress' in neighbor:
                config += f" neighbor {neighbor['loopbackAddress']} remote-as {as_number}\n"
                config += f" neighbor {neighbor['loopbackAddress']} update-source loopback0\n"
        
        # eBGP neighbors configuration
        for neighbor in router_data.get('ebgpNeighbors', []):
            config += f" neighbor {neighbor['ipAddress']} remote-as {neighbor['remoteAs']}\n"
            

            
        config += " !\n address-family ipv4\n exit-address-family\n"
        config += " address-family ipv6\n"
        
        # Activate iBGP neighbors
        for neighbor in router_data.get('ibgpNeighbors', []):
            config += f"  neighbor {neighbor['ipAddress']} activate\n"
            config += f" neighbor {neighbor['ipAddress']} send-community\n"

            
        # Activate eBGP neighbors and apply route maps
        for neighbor in router_data.get('ebgpNeighbors', []):
            config += f"  neighbor {neighbor['ipAddress']} activate\n"
            config += f" neighbor {neighbor['ipAddress']} send-community\n"
            config += f"  neighbor {neighbor['ipAddress']} route-map SET_LOCAL_PREF_{neighbor['name']} in\n"
            config += f"  neighbor {neighbor['ipAddress']} route-map sendCustCom_{neighbor['name']} out\n"
            
        # Network statements for IPv6 prefixes
        for prefix in router_data.get('ipv6Prefix', []):
            config += f"  network {prefix}\n"
        
        config += " exit-address-family\n!\n"

    # Miscellaneous configuration
    config += "ip forward-protocol nd\n!\n!\nno ip http server\nno ip http secure-server\n!\n!\n!"

    # eBGP specific configuration
    if 'ebgpNeighbors' in router_data:
        # Generate the configuration of the route map based on the eBGP neighbor type
        for neighbor in router_data.get('ebgpNeighbors', []):
            config += generate_route_map(neighbor.get('name'), neighbor.get('type'),as_number)
            # Generate route map for filtering based on community values
            config = generate_route_map_filter(config, neighbor,as_number)


    # Additional routing protocol configurations
    for protocol in router_data.get('routingProtocols', []):
        if protocol == 'Ospf':
            config += "ipv6 router ospf 1\n"
            config += f"router-id {router_data['routerId']}\n!"
        elif protocol == 'Rip v2':
            config += f"!\nrouter rip as{as_number}\n redistribute connected\n!"

    # Control plane and line configurations
    config += "\n!\n!\ncontrol-plane\n!\n!\nline con 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline aux 0\n exec-timeout 0 0\n privilege level 15\n logging synchronous\n stopbits 1\nline vty 0 4\n login\n!\n!\nend"

    return config

 
def write_config_to_file(router_name,filepath, config):
    destination_folder = r'C:\Users\ilhem\GNS3\projects\projet_Nap_test\project-files\dynamips'
    router_folder = os.path.join(destination_folder, f'{filepath}\configs')

    # Create the router folder if it doesn't exist
    if not os.path.exists(router_folder):
        os.makedirs(router_folder)

    # Write the configuration to the file
    if len(router_name) < 3:
        file_path = os.path.join(router_folder, f'i{router_name[1]}_startup-config.cfg')
    else:
        file_path = os.path.join(router_folder, f'i1{router_name[2]}_startup-config.cfg')


    with open(file_path, 'w') as output_file:
        output_file.write(config)

    print(f"Configuration for {router_name} saved to {file_path}")
    

# Main function to read JSON data and generate router configurations
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

 
# Write the configuration to the file
    for as_number, as_data in data.items():
        for router_name, router_data in as_data['routers'].items():
            config = generate_config(router_name, router_data)
            write_config_to_file(router_name,router_data['filepath'], config)


if __name__ == "__main__":
    main()
