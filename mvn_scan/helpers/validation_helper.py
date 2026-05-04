import sys
from bs4 import BeautifulSoup
from colorama import Fore,Style
from xml.etree import ElementTree
from zipfile import BadZipfile,ZipFile

class validation_helper:

    def procesar_archivo_txt(self, archivo):

        data = []
        ext_archivo = archivo.split('.')[-1]

        if ext_archivo == 'txt':

            try:
                with open(archivo, "r", encoding="utf-8", errors='ignore') as archivo:
                    for linea_archivo in archivo:
                        version_archivo = linea_archivo.split('-')[-1].replace('\n', '')
                        posicion_linea = linea_archivo.find(version_archivo)-1
                        group_id = ''
                        componente = linea_archivo[0:posicion_linea]
                        version = version_archivo[0:-4]

                        if version_archivo.split('.')[-1] == 'jar': 

                            if componente and version != '':
                                data.append((group_id, componente, version))
                            else:
                                print(Fore.RED + 'Invalid txt file; it must not have empty line breaks, components without an extension, or components other than .jar' + Style.RESET_ALL)
                                sys.exit(1)
                        else:
                            print(Fore.RED + 'Invalid txt file; it must not have empty line breaks, components without an extension, or components other than .jar' + Style.RESET_ALL)
                            sys.exit(1)      
            except FileNotFoundError:
                print(Fore.RED + 'Text file not found in the specified path' + Style.RESET_ALL)
                sys.exit(1)
        else:
            print(Fore.RED + 'Invalid txt file, must be a .txt file' + Style.RESET_ALL)
            sys.exit(1)

        return data

    def procesar_archivo_war(self, archivoWar):

        carpeta_busqueda = "WEB-INF/lib/"
        data = []
        archivos_jar = []
        encontro_carpeta_libs = False
        ext_archivo = archivoWar.split('.')[-1]
        
        if ext_archivo == 'war':

            try:
                with ZipFile(archivoWar, 'r') as archivoZip:
                    archivos_en_war = archivoZip.namelist()

                    for archivo in archivos_en_war:
                        if archivo.startswith(carpeta_busqueda):
                            encontro_carpeta_libs = True

                    if encontro_carpeta_libs:
                        for archivo in archivos_en_war:
                            if archivo.startswith(carpeta_busqueda):
                                nombre_jar = archivo[len(carpeta_busqueda):]
                                archivos_jar.append(nombre_jar)

                        for linea_archivo in archivos_jar:
                            
                            if(linea_archivo != ''):
                                version_archivo = linea_archivo.split('-')[-1]
                                posicion_linea = linea_archivo.find(version_archivo)-1
                                group_id = ''
                                componente = linea_archivo[0:posicion_linea]
                                version = version_archivo[0:-4]
                                data.append((group_id, componente, version))
                    else:
                        print(Fore.RED + 'Invalid war file, make sure it has the correct structure' + Style.RESET_ALL)
                        sys.exit(1)
            except BadZipfile:
                print(Fore.RED + 'Invalid war file' + Style.RESET_ALL)
                sys.exit(1)
            except FileNotFoundError:
                print(Fore.RED + 'War file not found, in the specified path' + Style.RESET_ALL)
                sys.exit(1)
        else:
            print(Fore.RED + 'Invalid war file, must be a .war file' + Style.RESET_ALL)
            sys.exit(1)

        return data

    def procesar_archivo_xml(self, archivo_xml):

        data = []
        ext_archivo = archivo_xml.split('.')[-1]

        if ext_archivo == 'xml':

            try:
                data_xml = ElementTree.parse(archivo_xml)
                namespaces = {
                    'xmlns': 'http://maven.apache.org/POM/4.0.0'
                }

                project = data_xml.getroot()
                dependencies = project.findall('.//xmlns:dependency', namespaces)

                for dependency in dependencies:
                    group_id = dependency.find('xmlns:groupId', namespaces).text
                    componente = dependency.find('xmlns:artifactId', namespaces).text
                    version = dependency.find('xmlns:version', namespaces)

                    if version != None:
                        data.append((group_id, componente, version.text))

            except ElementTree.ParseError:
                print(Fore.RED + 'Invalid xml file, please verify that it is a valid Maven xml file' + Style.RESET_ALL)
                sys.exit(1)
            except FileNotFoundError:
                print(Fore.RED + 'XML file not found in the specified path' + Style.RESET_ALL)
                sys.exit(1)

        else:
            print(Fore.RED + 'Invalid xml file, must be an .xml file' + Style.RESET_ALL)
            sys.exit(1)

        return data

    def generarArchivoHTML(self, dataHTML, salidaArchivo):

        try:
            with open(salidaArchivo, "w", encoding="utf8") as archivoHTML:
                archivoHTML.write('<html>\n')
                archivoHTML.write('<body style="font-family:Calibri; font-size:16px;">\n')
                archivoHTML.write('<ul id="vulnerabilities">\n')
            
                for componente, urlMaven, vulnerabilitiesMaven, __, urlSnyk, vulnerabilitiesSnyk in dataHTML:
                    if vulnerabilitiesMaven != '' or vulnerabilitiesSnyk != '':
                        if vulnerabilitiesMaven != '':
                            urlMaven = f"\n{urlMaven}"
                        else:
                            urlMaven = ""

                        if vulnerabilitiesSnyk != '':
                            urlSnyk = f"\n{urlSnyk}"
                        else:
                            urlSnyk = ""
                            
                        archivoHTML.write(f"""<li>
                                                <b>{componente}</b>
                                                <br>
                                                <a href='{urlMaven}' target='_blank'>{urlMaven}<a><br>
                                                {vulnerabilitiesMaven}
                                                <br><br>
                                                <a href='{urlSnyk}' target='_blank'>{urlSnyk}<a><br>
                                                {vulnerabilitiesSnyk}
                                                <br><br>
                                            </li>""")
                        
                archivoHTML.write('</ul><hr>\n')
                archivoHTML.write('<ul id="checkManual">\n')

                for __, __, __, chequeoManualMaven, __, __ in dataHTML:
                    if chequeoManualMaven != '':
                        archivoHTML.write(f"""<li>
                                                {chequeoManualMaven}<br><br>
                                            </li>
                                            """)

                archivoHTML.write('</ul>\n')

                archivoHTML.write('</body>\n')
                archivoHTML.write('<html>\n')

        except FileNotFoundError:
            print(Fore.RED + 'Error, output file not found' + Style.RESET_ALL)
            sys.exit(1)

        try:
            with open(salidaArchivo, "r", encoding="utf8") as archivoHTML:
                contenidoHtml = archivoHTML.read()

            soup = BeautifulSoup(contenidoHtml, "html.parser")
            elementoVulnerabilities = soup.find("ul", id="vulnerabilities")
            elementoCheckManual = soup.find("ul", id="checkManual")
            
            if not elementoVulnerabilities.find_all():

                nuevoElemento = soup.new_tag("li")
                nuevoElemento.string = "No vulnerabilities were found."
                elementoVulnerabilities.append(nuevoElemento)

                with open(salidaArchivo, "w", encoding="utf8") as archivoHTML:
                    archivoHTML.write(str(soup))

            if not elementoCheckManual.find_all():

                nuevoElemento = soup.new_tag("li")
                nuevoElemento.string = "No components were found to review manually."
                elementoCheckManual.append(nuevoElemento)

                with open(salidaArchivo, "w", encoding="utf8") as archivoHTML:
                    archivoHTML.write(str(soup))

        except FileNotFoundError:
            print(Fore.RED + 'Error, output file not found' + Style.RESET_ALL)
            sys.exit(1)

            