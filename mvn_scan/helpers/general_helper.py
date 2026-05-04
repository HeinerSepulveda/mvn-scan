import sys
import time
import hashlib
import os
import argparse
from tqdm import tqdm
from colorama import Fore,Style
from zipfile import BadZipfile,ZipFile
from mvn_scan.config.constants import (PATH_FOLDER)


class general_helper:

    def extraer_war(self, archivo_war, archivo_jar):
        extrajo_jar = False
        archivo_busqueda_jar = f"WEB-INF/lib/{archivo_jar}"
        carpeta_extraer_jar = os.path.join(os.path.expanduser('~'),PATH_FOLDER)

        try:
            with ZipFile(archivo_war, 'r') as archivoZip:
                archivoZip.extract(archivo_busqueda_jar, carpeta_extraer_jar)
                extrajo_jar = True

        except BadZipfile:
            print(Fore.RED + 'Invalid war file' + Style.RESET_ALL)
            sys.exit(1)
        except FileNotFoundError:
            print(Fore.RED + 'war file not found, in the specified path' + Style.RESET_ALL)
            sys.exit(1)
        
        return extrajo_jar


    def calcular_hash_sha(self, archivo_jar):

        hash_sha1 = ''
        carpeta_jar = os.path.join(os.path.expanduser('~'),PATH_FOLDER,"WEB-INF","lib")
        ruta_jar = os.path.join(carpeta_jar,archivo_jar)

        try:
            with open(ruta_jar, 'rb') as jar:
                contenido = jar.read()
                hash_sha1 = hashlib.sha1(contenido).hexdigest()

        except FileNotFoundError:
                print(Fore.RED + 'jar file not found in the specified path' + Style.RESET_ALL)
                sys.exit(1)
            
        return hash_sha1


    def check_directory(self):

        try:
            directory_user = os.path.expanduser('~')
            directory_create = PATH_FOLDER

            full_path = os.path.join(directory_user,directory_create)

            if not os.path.exists(full_path):
                os.makedirs(full_path)

            return full_path
        
        except:
            print(f'{Fore.RED} An error occurred while creating the installation folder' + Fore.WHITE)
            sys.exit()


    def barra_progreso(self):

        for i in tqdm(range(100), desc="Loading", colour='#44882a', ncols=75, bar_format="{l_bar}{bar}|"):
            time.sleep(0.01)
            

    def banner(self):

        return Fore.GREEN +"""                                       
     __  __                 _____                      
    |  \/  |               /  ___\                     
    | .  . |__   __ _ __   \ `--.   ___   __ _  _ __   
    | |\/| |\ \ / /| '_ \   `--. \ / __| / _` || '_ \  
    | |  | | \ V / | | | | /\__/ /| (__ | (_| || | | | 
    |_|  |_|  \_/  |_| |_| \____/  \___| \__,_||_| |_|  

    
    Usage:
    mvn-scan -txt <file.txt> [-out <output.html>]
    mvn-scan -war <file.war> [-out <output.html>]
    mvn-scan -xml <file.xml> [-out <output.html>]

    Options:
    -txt <file> Scans dependencies from a .txt file
    -war <file> Scans a .war file
    -xml <file> Scans an .xml file (pom.xml)
    -out <file> Output HTML file (optional)

    Configuration:
    --api-token <token> OSS Index API token (temporary)
    --set-api-token <token> Saves the API token to the local configuration

    Examples:
    mvn-scan -txt deps.txt
    mvn-scan -xml pom.xml -out report.html 
    mvn-scan --set-api-token API_TOKEN

    Author: Edwin Geinner Castro Sepulveda | Version: 1.8                                                      
        """
