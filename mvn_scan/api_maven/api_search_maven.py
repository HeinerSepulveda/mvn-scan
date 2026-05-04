import sys
import requests
from colorama import Fore
from mvn_scan.helpers.general_helper import general_helper
from mvn_scan.config.constants import (API_SEARCH_MAVEN, URL_MAVEN_CENTRAL_REPO)

class api_search_maven:
    
    def __init__(self,archivo_escanear):
        self.archivo_escanear = archivo_escanear

    """ Utiliza la api de search maven para obtener el fabricante,componente y version exacta de un componente para generar 
    el paguete a escanear """
    
    def get_search_api_maven(self, group_id, componente, version):

        if group_id != '':
            payload = f'g:{group_id} a:{componente} v:{version}'
        else:
            payload= f'a:{componente} v:{version}'

        search = {
            "size": 10,
            "searchTerm": payload,
            "filter": []
        }

        pkg_componente = {
            'fabricante_mvn':'',
            'componente_mvn':'',
            'version_mvn':''
        }
        
        url_maven = ''
        fabricante_mvn = ''
        componente_mvn = ''
        version_mvn = ''
        check_manual = ''
        ext_archivo = self.archivo_escanear.split('.')[-1]


        try:
            response = requests.post(API_SEARCH_MAVEN, json=search, headers={"Content-Type": "application/json"})
            if response.status_code == 200:

                json_data = response.json()
                found_component = json_data['components']

                if len(found_component) > 0:  

                    fabricante_mvn = json_data.get('components')[0]['namespace']
                    componente_mvn = json_data.get('components')[0]['name']
                    version_mvn = json_data.get('components')[0]['version']

                    if json_data.get('totalResultCount') == 1:
                        url_maven = f'{URL_MAVEN_CENTRAL_REPO}{fabricante_mvn}/{componente_mvn}/{version_mvn}'
                        print(f'Component URL: {Fore.GREEN + url_maven + Fore.WHITE}')

                    if json_data.get('totalResultCount') > 1 and ext_archivo == 'war':

                        obj_functions = general_helper()

                        jar = f'{componente}-{version}.jar'
                        extrajo_jar = obj_functions.extraer_war(self.archivo_escanear, jar)

                        if extrajo_jar:
                            hash = obj_functions.calcular_hash_sha(jar)
                            data_maven_hash = self.get_search_hash_api_maven(hash, componente, version)
                            url_maven = data_maven_hash[0]
                            fabricante_mvn = data_maven_hash[1]
                            check_manual = data_maven_hash[2]         

                    elif json_data.get('totalResultCount') > 1:
                        check_manual += f'<b style="color:red">Manual checking required:</b> <b>{componente} » {version}</b><br><br>'
                        print(f'The component: {Fore.RED + componente} » {version + Fore.WHITE} it must be checked manually, as it has several manufacturers')
                        for data_url in json_data['components']:
                            artefacto_dinamico = data_url['namespace']
                            componente_dinamico = data_url['name']
                            version_dinamica = data_url['version']
                            url_dinamica = f'{URL_MAVEN_CENTRAL_REPO}{artefacto_dinamico}/{componente_dinamico}/{version_dinamica}'
                            print(f'URL for manual verification: {Fore.GREEN + url_dinamica + Fore.WHITE}')
                            check_manual += f'<a href="{url_dinamica}" target="_blank">{url_dinamica}</a><br>'

                        url_maven = ''
                        fabricante_mvn = ''

                else:
                    print(f'Component not found in Maven: {Fore.RED + componente} » {version + Fore.WHITE}')
            else:
                print(f'{Fore.RED} Error sending request, Search API Maven: {response.status_code}') 
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print (f'{Fore.RED} Check the connection: {e}' + Fore.WHITE)
            sys.exit(1)



        pkg_componente['fabricante_mvn']=fabricante_mvn
        pkg_componente['componente_mvn']=componente_mvn
        pkg_componente['version_mvn']=version_mvn
        pkg_componente['url_maven']=url_maven

        return pkg_componente
    
    """ Utiliza la api de search maven para obtener el fabricante,componente y version exacta por hash de un componente y generar 
    el paguete a escanear """

    def get_search_hash_api_maven(self, hash, componente, version):
        
        if hash != '':
            payload = f'1:{hash}'

        search = {
            "size": 10,
            "searchTerm": payload,
            "filter": []
        }

        url_mvn = ''
        fabricante_mvn = ''
        check_manual = ''

        try:
            response = requests.post(API_SEARCH_MAVEN, json=search)
            if response.status_code == 200:
                json_data = response.json()

                found_component = json_data['components']

                if len(found_component) > 0:

                    fabricante_mvn = json_data.get('components')[0]['namespace']
                    componente_mvn = json_data.get('components')[0]['name']
                    version_mvn = json_data.get('components')[0]['version']

                    if json_data.get('totalResultCount') == 1: 
                        url_mvn = f'{URL_MAVEN_CENTRAL_REPO}{fabricante_mvn}/{componente_mvn}/{version_mvn}'
                        print(f'Component URL: {Fore.GREEN + url_mvn + Fore.WHITE}')

                    elif json_data.get('totalResultCount') > 1:
                        check_manual += f'<b style="color:red">Manual checking required:</b> <b>{componente} » {version}</b><br><br>'
                        print(f'The component: {Fore.RED + componente} » {version + Fore.WHITE} it must be checked manually, as it has several manufacturers')
                        for data_url in json_data['components']:
                            artefacto_dinamico = data_url['namespace']
                            componente_dinamico = data_url['name']
                            version_dinamica = data_url['version']
                            url_dinamica = f'{URL_MAVEN_CENTRAL_REPO}{artefacto_dinamico}/{componente_dinamico}/{version_dinamica}'
                            print(f'URL for manual verification: {Fore.GREEN + url_dinamica + Fore.WHITE}')
                            check_manual += f'<a href="{url_dinamica}" target="_blank">{url_dinamica}</a><br>'

                        url_mvn = ''
                        fabricante_mvn = ''
                else:
                    print(f'Component not found in Maven: {Fore.RED + componente} » {version + Fore.WHITE}')
            else:
                print(f'{Fore.RED} Error sending request, Search API Maven: {response.status_code}') 
                sys.exit(1)
        except requests.exceptions.RequestException as e:
            print (f'{Fore.RED} Check the connection: {e}' + Fore.WHITE)
            sys.exit(1)

        return [url_mvn, fabricante_mvn, check_manual]
    
    
    