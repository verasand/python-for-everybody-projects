# Este programa analiza un registro de correos electrónicos almacenado en un archivo de texto.
# Extrae el número de correos enviados por día, así como el número de correos enviados por cada individuo e institución.
# Los resultados se visualizan en gráficos de barras, que son exportados junto con archivos .csv para análisis adicional.

import matplotlib.pyplot as plt
import csv
from tabulate import tabulate

def email_analyzer():
    """
    Analiza un archivo de registro de correos y cuenta los correos enviados por día, por remitente individual e institución.
    
    Solicita al usuario el nombre de un archivo, analiza su contenido y extrae la información relevante para actualizar
    los conteos. Permite salir del programa ingresando 'q'.
    
    Returns:
        dict: Diccionario con tres claves:
              - "day": Diccionario con el conteo de correos enviados por día de la semana.
              - "individual_senders": Diccionario con el conteo de correos enviados por cada remitente individual.
              - "institutional_senders": Diccionario con el conteo de correos enviados por cada dominio de correo.
    """
    analyzed_log = {
        "day": {},
        "individual_senders": {},
        "institutional_senders": {}
    }
    while True:
        try:
            # Solicita el nombre del archivo al usuario
            fname = input("Enter the file name: ")
            if fname.lower() == "q":  # Permitir al usuario salir del programa
                print("Closing the program...")
                return None
            
            # Abrir y leer el archivo línea por línea
            with open(fname) as file:
                for line in file:
                    line = line.rstrip()
                    # Ignorar líneas irrelevantes
                    if len(line) < 3 or not line.startswith("From "): 
                        continue
                    line_elements = line.split()
                    # Extraer información relevante: día, remitente y dominio
                    day = line_elements[2]
                    sender_email = line_elements[1]
                    institution_domain = sender_email[(sender_email.find("@") + 1):]
                    
                    # Actualizar el conteo en cada categoría
                    analyzed_log["day"][day] = analyzed_log["day"].get(day, 0) + 1
                    analyzed_log["individual_senders"][sender_email] = analyzed_log["individual_senders"].get(sender_email, 0) + 1
                    analyzed_log["institutional_senders"][institution_domain] = analyzed_log["institutional_senders"].get(institution_domain, 0) + 1

            return analyzed_log
        except FileNotFoundError:
            print(f"The file {fname} could not be found. Please try it again or type 'q' to exit.")

def generate_stats(dic):
    """
    Genera estadísticas del análisis de correos y las presenta en una tabla formateada.
    
    Calcula el total de correos, el día con más correos, el remitente individual con más correos,
    la institución con más correos y el promedio de correos por día.

    Args:
        dic (dict): Diccionario con los resultados del análisis de correos.

    Returns:
        None
    """
    stats = {
        "Total de correos": sum(dic["day"].values()),
        "Día con más correos": f"{max(dic['day'].items(), key=lambda item: item[1])[0]} : {max(dic['day'].items(), key=lambda item: item[1])[1]}",
        "Individuo con más correos": f"{max(dic['individual_senders'].items(), key=lambda item: item[1])[0]} : {max(dic['individual_senders'].items(), key=lambda item: item[1])[1]}",
        "Institución con más correos": f"{max(dic['institutional_senders'].items(), key=lambda item: item[1])[0]} : {max(dic['institutional_senders'].items(), key=lambda item: item[1])[1]}",
        "Promedio de correos por día": f"{(sum(dic['day'].values()) / len(dic['day'])):.2f}"
    }
    
    # Crear una tabla con las estadísticas generadas
    
    print(tabulate(stats.items(), headers=["Variable", "Resultado"], tablefmt="simple_grid"))

def bar_plots(dic):
    """
    Genera gráficos de barras para visualizar los resultados del análisis y los guarda como archivos de imagen.
    
    Args:
        dic (dict): Diccionario con los resultados del análisis de correos.
    
    Returns:
        None
    """
    # Diccionario para formatear cada gráfico de manera personalizada
    plot_format = {
        "day": {
            "title": "Emails Sent By Day",
            "xlabel": "Day of The Week",
            "file_name": "emails_by_day.png"
        },
        "individual_senders": {
            "title": "Emails Sent By Individual",
            "xlabel": "Individual sender",
            "file_name": "emails_by_individual_senders.png"
        },
        "institutional_senders": {
            "title": "Emails Sent by Institutional Domains",
            "xlabel": "Institutional Domains",
            "file_name": "emails_by_institutional_domains.png"
        }
    }
    
    # Ordenar y descomponer el diccionario en una lista de tuplas
    dic_decomposition = dic.items()
    dic_ordered = []
    for key, data in dic_decomposition:
        dic_ordered.append((key, sorted(data.items(), key=lambda item: item[1])))

    # Crear y guardar cada gráfico de barras
    for variable, data in dic_ordered:
        label, value = zip(*data)
        plt.bar(label, value, width=0.8)
        plt.title(plot_format[variable]["title"])
        plt.xlabel(plot_format[variable]["xlabel"])
        plt.ylabel("Email Counts")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(plot_format[variable]["file_name"], format="png", dpi=300)
        plt.clf()  # Limpia el gráfico para evitar superposición en la siguiente iteración

def export_results(dic):
    """Exporta los resultados del análisis del correo en archivos .csv
    Para cada clave en el diccionario (como 'day', 'individual_senders', 'institutional_senders'),
    crea un archivo CSV con el nombre de la clave y escribe los datos ordenados por el conteo.

    Args:
        dic (dict): Diccionario con los resultados del análisis de correos.
    """
    for key, dics in dic.items():
        fname = f"{key}" + ".csv"
        with open(fname, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([key, 'Counts']) #escribir el encabezado
            writer.writerows(sorted(dics.items(), key = lambda item: item[1])) #ordenar la salida de los datos en orden ascendente

# Ejecutar el análisis y visualizar los resultados
results = email_analyzer()
if results:
    bar_plots(results)
    export_results(results)
    generate_stats(results)
