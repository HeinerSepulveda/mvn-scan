from jinja2 import Template
from colorama import Fore
from datetime import datetime

class template_html_helper:

    #Plantilla HTML
    def generate_report(self, componentes, componentes_filtrados, salida_archivo):

        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Maven vulnerability report</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
            <style>
                body { background-color: #f8f9fa; font-family: 'Inter', sans-serif; font-size: 0.9rem; }
                .table { background-color: white; border-radius: 8px; overflow: hidden; font-size: 0.85rem; }
                .clickable { cursor: pointer; }
                .details-row { background-color: #f1f1f1; }
                .cve-link { margin-right: 5px; }
            </style>
        </head>
        <body>
        <div class="container mt-4">
            <h3>Maven vulnerability report</h3><br>
            <small class="text-muted">Report date: {{ fecha_reporte }}</small><br><br>
            <table class="table">
                
                <thead>
                    <tr>
                        <th></th>
                        <th>Component</th>
                        <th>Direct vulnerabilities</th>
                        <th>Maven link</th>
                    </tr>
                </thead>
                <tbody>
                    {% for id_componente, datos in componentes.items() %}
                    <tr class="clickable">
                        <td data-bs-toggle="collapse" data-bs-target="#detail{{ id_componente }}">
                            {% if datos.dependencias %}
                                <span class="toggle-icon">+</span>
                            {% endif %}
                        </td>
                        <td data-bs-toggle="collapse" data-bs-target="#detail{{ id_componente }}"><strong>{{ datos.nombre }}-{{ datos.version }}</strong></td>
                        <td>
                            {% if datos.vulnerabilidades %}
                                {% for cve, score in datos.vulnerabilidades %}
                                    {% set score_num = score | float %}
                                    {% if score_num >= 7 %}
                                        {% set clase = "text-danger" %}
                                    {% elif score_num >= 4 %}
                                        {% set clase = "text-warning" %}
                                    {% else %}
                                        {% set clase = "text-success" %}
                                    {% endif %}
                                    <a href="https://nvd.nist.gov/vuln/detail/{{ cve }}" class="cve-link {{ clase }}" target="_blank">
                                        {{ cve }} ({{ score }})
                                    </a>
                                {% endfor %}
                            {% else %}
                                --
                            {% endif %}
                        </td>
                        <td>
                            {% if datos.vulnerabilidades %}
                                <a href="https://central.sonatype.com/artifact/{{ datos.fabricante }}/{{ datos.nombre }}/{{ datos.version | replace('@', '')}}" target="_blank">Ver detalle</a>
                            {% else %}
                                <a href="https://central.sonatype.com/artifact/{{ datos.fabricante }}/{{ datos.nombre }}/{{ datos.version | replace('@', '')}}/dependencies" target="_blank">Ver detalle</a>
                            {% endif %}
                        </td>
                    </tr>
                    {% for id_dep, dep in datos.dependencias.items() %}
                    <tr id="detail{{ id_componente }}" class="collapse details-row">
                        <td colspan="5">
                            Dependence: {{ dep.nombre }}-{{ dep.version }}<br>
                            Vulnerabilities of dependency:<br>
                            {% if dep.vulnerabilidades %}
                                {% for cve, score in dep.vulnerabilidades %}
                                    {% set score_num = score | float %}
                                    {% if score_num >= 7 %}
                                        {% set clase = "text-danger" %}
                                    {% elif score_num >= 4 %}
                                        {% set clase = "text-warning" %}
                                    {% else %}
                                        {% set clase = "text-success" %}
                                    {% endif %}
                                    <a href="https://nvd.nist.gov/vuln/detail/{{ cve }}" class="cve-link {{ clase }}" target="_blank">
                                        {{ cve }} ({{ score }})
                                    </a>
                                {% endfor %}
                            {% else %}
                                --
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
        </body>
        </html>
        """
        fecha_reporte = datetime.now().strftime("%d-%m-%Y %H:%M")
        template = Template(html_template)
        html_output = template.render(componentes=componentes_filtrados, fecha_reporte=fecha_reporte)

        # Guardar en un archivo
        with open(salida_archivo, "w", encoding="utf-8") as f:
            f.write(html_output)

        
        print(f"{Fore.GREEN}\nReport successfully generated: {salida_archivo}{Fore.WHITE}")