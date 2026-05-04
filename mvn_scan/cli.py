import sys
import argparse
from colorama import Fore, Style

from mvn_scan.helpers.general_helper import general_helper
from mvn_scan.helpers.config_helper import config_helper
from mvn_scan.helpers.validation_helper import validation_helper
from mvn_scan.core.scan_vulnerabilities import scan_vulnerabilities

class ScanMvn:

    def __init__(self):
        self.salida_archivo = 'vulnerability_report_mvn.html'

    def run(self, parametros, api_token):

        file = validation_helper()
        scan = scan_vulnerabilities()

        if parametros.out:
            self.salida_archivo = parametros.out

        if parametros.txt:
            archivo = parametros.txt
            data = file.procesar_archivo_txt(archivo)

        elif parametros.war:
            archivo = parametros.war
            data = file.procesar_archivo_war(archivo)

        elif parametros.xml:
            archivo = parametros.xml
            data = file.procesar_archivo_xml(archivo)

        else:
            raise ValueError("You must specify an input file")

        scan.scan_vulnerabilities_mvn(data, archivo, api_token)
        scan.generate_report_vulnerabilities(self.salida_archivo)


def main():

    helper = general_helper()
    config = config_helper()

    try:
        parser = argparse.ArgumentParser(
            description=helper.banner(),
            usage=helper.banner(),
            add_help=True,
            allow_abbrev=False,
            formatter_class=argparse.RawTextHelpFormatter
        )

        group = parser.add_mutually_exclusive_group()

        group.add_argument('-txt', type=str, help=".txt file to scan") 
        group.add_argument('-war', type=str, help=".war file to scan") 
        group.add_argument('-xml', type=str, help=".xml file to scan") 

        parser.add_argument('-out', type=str, help="Optional output .html file") 
        parser.add_argument('--api-token', type=str, help="OSS Index API Token") 
        parser.add_argument('--set-api-token', type=str, help="Save API Token to configuration")

        parametros = parser.parse_args()

        if parametros.set_api_token:
            config.update_config({"api_token": parametros.set_api_token})
            print(Fore.GREEN + "API Token saved successfully" + Style.RESET_ALL)
            sys.exit(0)

        if not any([parametros.txt, parametros.war, parametros.xml]):
            parser.error("You must specify one of the arguments: -txt, -war or -xml")

        api_token = config.get_api_token(parametros.api_token)
        scanner = ScanMvn()
        scanner.run(parametros, api_token)

    except KeyboardInterrupt:
        print(Fore.RED + 'Execution cancelled by the user' + Style.RESET_ALL)
        sys.exit(1)

    except Exception as e:
        print(Fore.RED + str(e) + Style.RESET_ALL)
        sys.exit(1)


if __name__ == "__main__":
    main()