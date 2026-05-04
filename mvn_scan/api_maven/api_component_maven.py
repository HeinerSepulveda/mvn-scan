import sys
import time
import requests
from tqdm import tqdm
from mvn_scan.config.constants import (API_COMPONENT_MAVEN, API_DEPENDENCIES_MAVEN, TIME)

class api_component_maven:

    """ Obtiene las dependencias de un componente y retorna las dependencias vulnerables del componente """
    
    def check_dependencies_vulnerabilities(self,component):
        
        page_count = self.check_pages_dependencies(component)
        array_vulns_dependencies = []

        for page in range(page_count):

            array_dependencies = []
            
            body_json = {
                "purl": component,
                "page": page,
                "size": 10,
                "searchTerm": "",
                "filter": [
                    "dependencyRef:DIRECT"
                ]
            }

            try:
                response = requests.post(
                    API_DEPENDENCIES_MAVEN,
                    json=body_json,
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    dependencies = response.json()

                    for dependencie in dependencies['components']:
                        if dependencie['scope'] == 'COMPILE':
                            array_dependencies.append(dependencie['dependencyPurl'])

                    try:
                        response = requests.post(
                            API_COMPONENT_MAVEN,
                            json=array_dependencies,
                            headers={"Content-Type": "application/json"}
                        )
                        if response.status_code == 200:
                            dependencies_vuln = response.json()
                            for desc_dependencie, number_vuln in dependencies_vuln.items():
                                if number_vuln != 0:
                                    array_vulns_dependencies.append(desc_dependencie)
                        else:
                            print(f'Error in the request: {response.status_code} - {response.text}') 
                            sys.exit(1)
                    except requests.exceptions.RequestException as e:
                        print('Connection error: ', e)
                elif response.status_code == 429:
                    for i in tqdm(range(TIME), desc="Too many requests, will resume in 3 minutes", colour='#44882a', ncols=100, bar_format="{l_bar}{bar}|"):
                        time.sleep(0.1)
                    self.check_dependencies_vulnerabilities(component)
                else:
                    print(f'Error in the request: {response.status_code} - {response.text}') 
                    sys.exit(1)
            except requests.exceptions.RequestException as e:
                print('Connection error: ', e)
            
        return array_vulns_dependencies


    """ Obtiene la cantidad de paginas de las dependencias del componente """
    
    def check_pages_dependencies(self,component):

        array_dependencies = {
            "purl": component,
            "page": 100,
            "size": 10,
            "filter": [
                "dependencyRef:DIRECT"
            ]
        }
            
        try:
            response = requests.post(
                API_DEPENDENCIES_MAVEN,
                json=array_dependencies,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                dependencies_vuln = response.json()
                return dependencies_vuln['pageCount']
            elif response.status_code == 429:
                for i in tqdm(range(TIME), desc="Too many requests, will resume in 3 minutes", colour='#44882a', ncols=100, bar_format="{l_bar}{bar}|"):
                    time.sleep(0.1)
                return self.check_pages_dependencies(component)
            else:
                print(f'Error in the request: {response.status_code} - {response.text}') 
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print('Connection error: ', e)