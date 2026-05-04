    
from colorama import Fore, Style
from mvn_scan.helpers.template_html_helper import template_html_helper
from mvn_scan.process_db.operations_db import operations_db
from mvn_scan.api_maven.api_search_maven import api_search_maven
from mvn_scan.api_maven.api_scan_maven import api_scan_maven

URL_NIST = "https://web.nvd.nist.gov/view/vuln/detail?vulnId"

class scan_vulnerabilities:
    
    """
        Este metodo se encarga de ejecutar varios metodos para preparar el escaneo
        - Utiliza la api de search maven para buscar el componente a escanear e inserta el componente en base de datos
        - Utiliza la api de dependencias maven, para buscar las dependencias vulnerables del componente e inserta las dependencias en base de datos
        - Consulta el paquete de componente + dependencias para luego ser escaneados.     
    """

    def scan_vulnerabilities_mvn(self, data_componente, archivo_escanear, api_token):

        api_search = api_search_maven(archivo_escanear)
        obj_db = operations_db()
        obj_db.create_db()

        dependencias_componentes = []
        
        for group_id, componente, version in data_componente:
            print(f"\n• Vulnerability scanning of: {Fore.BLUE + componente} » {version + Fore.WHITE}")
            respuesta_api_mvn = api_search.get_search_api_maven(group_id, componente, version)

            if respuesta_api_mvn['fabricante_mvn'] != '':
                last_insert_id = obj_db.insertar_componente('maven', respuesta_api_mvn['fabricante_mvn'], respuesta_api_mvn['componente_mvn'], f"@{respuesta_api_mvn['version_mvn']}")
                pkg_componente = f"pkg:maven/{respuesta_api_mvn['fabricante_mvn']}/{respuesta_api_mvn['componente_mvn']}@{respuesta_api_mvn['version_mvn']}"

                obj_db.insertar_dependencias_vulnerables(pkg_componente,last_insert_id)
                dependencias_componentes = obj_db.consultar_dependencias_componentes(last_insert_id)

                self.execute_scan_mvn(dependencias_componentes, last_insert_id, api_token)
  

    """ Este metodo se encarga de ejecutar la api para escanear vulnerabilidades de maven """

    def execute_scan_mvn(self,dependencias_componentes, id_componente, api_token):

        api_scan = api_scan_maven()
        obj_db = operations_db()

        coordinates =  {"coordinates": [item[1] for item in dependencias_componentes]}
        data_vulnerabilities = api_scan.scan_components_maven(coordinates, dependencias_componentes, api_token)

        for data_vulns in data_vulnerabilities:
            vulnerabilities = data_vulns.get('vulnerabilities')
            tipo_vuln = data_vulns['tipo_vuln']
            componente = data_vulns['componente']
            id_componente = data_vulns['id_componente']
            
            estado = "Direct vulnerabilities" if tipo_vuln == "directa" else f"\nVulnerabilities of dependencies in {componente}"
        
            if len(vulnerabilities) > 0:
                print(f"{Fore.RED}{estado}{Style.RESET_ALL}")
                for vuln in vulnerabilities:
                    print(f"{Fore.RED}{vuln['cve']}: {URL_NIST}={vuln['cve']}{Style.RESET_ALL}")
                    obj_db.insertar_vulnerabilidad(id_componente,tipo_vuln,vuln['title'],vuln['description'],vuln['cve'],vuln['cvssScore'])
            else:
                print(f"{Fore.GREEN}Were not found {estado}{Style.RESET_ALL}")
                
    
    def generate_report_vulnerabilities(self,salida_archivo):

        obj_db = operations_db()
        componentes = {}

        # Vulnerabilidades directas
        for id_comp, fabricante, nombre, version, cve, score in obj_db.consultar_vulnerabilidades_directas():
            if id_comp not in componentes:
                componentes[id_comp] = {
                    "fabricante": fabricante,
                    "nombre": nombre,
                    "version": version,
                    "vulnerabilidades": [],
                    "dependencias": {}
                }
            componentes[id_comp]["vulnerabilidades"].append((cve, score))

        # Vulnerabilidades de dependencias
        for id_comp, fabricante_padre, nombre_padre, version_padre, id_dep, nombre_dep, version_dep, cve, score in obj_db.consultar_vulnerabilidades_dependencias():
            if id_comp not in componentes:
                componentes[id_comp] = {
                    "fabricante": fabricante_padre,
                    "nombre": nombre_padre,
                    "version": version_padre,
                    "vulnerabilidades": [],
                    "dependencias": {}
                }
            if id_dep not in componentes[id_comp]["dependencias"]:
                componentes[id_comp]["dependencias"][id_dep] = {
                    "nombre": nombre_dep,
                    "version": version_dep,
                    "vulnerabilidades": []
                }
            componentes[id_comp]["dependencias"][id_dep]["vulnerabilidades"].append((cve, score))

        # Filtrar componentes sin ninguna vulnerabilidad
        componentes_filtrados = {
            k: v for k, v in componentes.items()
            if v["vulnerabilidades"] or any(dep["vulnerabilidades"] for dep in v["dependencias"].values())
        }

        helper = template_html_helper()
        helper.generate_report(componentes,componentes_filtrados,salida_archivo) 