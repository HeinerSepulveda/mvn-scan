import sys
import requests
from mvn_scan.config.constants import (API_URL_COMPONENT)
from mvn_scan.helpers.config_helper import config_helper

class api_scan_maven:

    """ Este metodo escanea componentes y retorna las vulnerabilidades encontradas """
    
    def scan_components_maven(self, components, dependencias_componentes, api_token):

        config = config_helper()
        token = config.get_api_token(api_token)

        try:
            response = requests.post(
                API_URL_COMPONENT,
                json=components,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
            )

            if response.status_code == 200:
                results = response.json()
                
                tipo_vuln = {item[1]: item[2] for item in dependencias_componentes}
                id_componente = {item[1]: item[0] for item in dependencias_componentes}
                
                resultado = []
                for item in results:
                    
                    coordenada = item['coordinates']
                    vulnerabilities = [
                        {
                            "title": vuln.get("title", ""),
                            "description": vuln.get("description", ""),
                            "cve": vuln.get("cve", ""), 
                            "cvssScore": vuln.get("cvssScore", "")
                        }
                        for vuln in item.get("vulnerabilities", [])
                    ]

                    resultado.append({
                        "vulnerabilities": vulnerabilities,
                        "tipo_vuln": tipo_vuln.get(coordenada, ''),
                        "componente": coordenada.split("/")[-1],
                        "id_componente": id_componente.get(coordenada, '')
                    })

                return resultado
            else:
                print(f'Error scanning components, validate the network or your API token') 
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print ('Connection error: ', e)
        return []
