import sqlite3
import os
from mvn_scan.helpers.general_helper import general_helper
from mvn_scan.api_maven.api_component_maven import api_component_maven
from mvn_scan.config.constants import (NAME_DB)

class operations_db:

    def conection_db(self):

        helper = general_helper()
        path_user = helper.check_directory()
        path_db = os.path.join(path_user,NAME_DB)

        return sqlite3.connect(path_db)

    def create_db(self):
        conexion = self.conection_db()
        conexion.execute("PRAGMA foreign_keys = 1")
        cursor=conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS componentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                software TEXT NOT NULL,
                fabricante TEXT NOT NULL,
                componente TEXT NOT NULL,
                version TEXT NOT NULL
            )  
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deps_componentes_vuln (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_componente INTEGER NOT NULL,
                software TEXT NOT NULL,
                fabricante TEXT NOT NULL,
                componente TEXT NOT NULL,
                version TEXT NOT NULL,
                FOREIGN KEY (id_componente) REFERENCES componentes (id) ON DELETE CASCADE
            )  
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_componente INTEGER NULL,
                id_dependencia INTEGER NULL,
                tipo_vuln TEXT NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                cve TEXT NOT NULL,
                cvss_score TEXT NOT NULL,
                FOREIGN KEY (id_componente) REFERENCES componentes (id) ON DELETE CASCADE,
                FOREIGN KEY (id_dependencia) REFERENCES deps_componentes_vuln (id) ON DELETE CASCADE
            )  
        """)

        cursor.execute("DELETE FROM componentes")
        cursor.execute("DELETE FROM deps_componentes_vuln")
        cursor.execute("DELETE FROM vulnerabilidades")
        conexion.commit()
        conexion.close()


    def insertar_componente(self,software,fabricante,componente,version):

        conexion = self.conection_db()
        cursor=conexion.cursor()
        cursor.execute("INSERT INTO componentes (software,fabricante,componente,version) VALUES (?,?,?,?)", (software, fabricante, componente, version))
        last_insert_id = cursor.lastrowid
        conexion.commit()
        conexion.close()
        
        return last_insert_id
        
    def insertar_dependencias_vulnerables(self,pkg_componente,last_insert_id):

        api_component = api_component_maven()
        conexion = self.conection_db()
        cursor=conexion.cursor()
        
        dependencias = api_component.check_dependencies_vulnerabilities(pkg_componente)

        for dependencia in dependencias:
            dependencia_split = dependencia.split("/")
            id_componente = last_insert_id
            software = dependencia_split[0][4:9]
            fabricante = dependencia_split[1]
            componente = dependencia_split[2]
            posicion_arroba = dependencia.find('@')
            posicion_arroba2 = componente.find('@')

            if posicion_arroba != -1:
                version = dependencia[posicion_arroba:]

            if posicion_arroba2 != -1:
                componente = componente[:posicion_arroba2]

            cursor.execute("INSERT INTO deps_componentes_vuln (id_componente,software,fabricante,componente,version) VALUES (?,?,?,?,?)", (id_componente,software,fabricante,componente,version)) 

        conexion.commit() 
        conexion.close()


    def consultar_dependencias_componentes(self,id_componente):

        conexion = self.conection_db()
        cursor=conexion.cursor()
        dependencias_componentes = []
        
        cursor.execute( """
            SELECT id,software,fabricante,componente,version,'directa' AS tipo_vuln FROM componentes WHERE id = ? UNION ALL 
            SELECT id,software,fabricante,componente,version,'dependencia' AS tipo_vuln FROM deps_componentes_vuln WHERE id_componente = ?
        """, (id_componente,id_componente))
        componentes_dependencias = cursor.fetchall()

        for id_componente,software,fabricante,componente,version,tipo_vuln in componentes_dependencias:
            dependencias_componentes.append((id_componente, f'pkg:{software}/{fabricante}/{componente}{version}', tipo_vuln))

        return dependencias_componentes
        
    def insertar_vulnerabilidad(self,id_componente,tipo_vuln,titulo,descripcion,cve,cvss_score):

        conexion = self.conection_db()
        cursor = conexion.cursor()

        if tipo_vuln == "directa":
            cursor.execute("INSERT INTO vulnerabilidades (id_componente,tipo_vuln,titulo,descripcion,cve,cvss_score) VALUES (?,?,?,?,?,?)", (id_componente,tipo_vuln,titulo,descripcion,cve,cvss_score))

        elif tipo_vuln == "dependencia":
            cursor.execute("INSERT INTO vulnerabilidades (id_dependencia,tipo_vuln,titulo,descripcion,cve,cvss_score) VALUES (?,?,?,?,?,?)", (id_componente,tipo_vuln,titulo,descripcion,cve,cvss_score))

        conexion.commit()
        conexion.close()
        

    def consultar_vulnerabilidades_directas(self):

        conexion = self.conection_db()
        cursor = conexion.cursor()

        query = """
            SELECT 
                c.id AS id_componente,
                c.fabricante,
                c.componente,
                c.version,
                v.cve,
                v.cvss_score
            FROM componentes c
            JOIN vulnerabilidades v ON v.id_componente = c.id
            WHERE v.id_dependencia IS NULL;
        """

        cursor.execute(query)
        return cursor.fetchall()
    
    def consultar_vulnerabilidades_dependencias(self):

        conexion = self.conection_db()
        cursor = conexion.cursor()

        query = """
            SELECT 
                c.id AS id_componente,
                c.fabricante AS fabricante_padre,
                c.componente AS componente_padre,
                c.version AS version_padre,
                d.id AS id_dependencia,
                d.componente AS componente_dependencia,
                d.version AS version_dependencia,
                v.cve,
                v.cvss_score
            FROM componentes c
            JOIN deps_componentes_vuln d ON d.id_componente = c.id
            JOIN vulnerabilidades v ON v.id_dependencia = d.id;
        """

        cursor.execute(query)
        return cursor.fetchall()