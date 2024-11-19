import matplotlib.pyplot as plt
from tabulate import tabulate
import csv
import os

def folder_creator(results_type):
    """
    Esta función permite la creación de carpetas para organizar los resultados generados en la ejecución.
    La función se asegura que el nombre de la carpeta sea válido y que no contenga caracteres restringidos.
    La función permite crear carpetas específicas para diferentes tipos de resultados (por ejemplo, archivos CSV, gráficos, etc.).

    Args:
        results_type (str): Descripción del tipo de resultados a almacenar en el folder a crear. Esta info
        se usa como guía cuando se le indica al usuario asignar el nombre del folder.

    Raises:
        ValueError: Cuando el nombre de la carpeta es vacío
        ValueError: Cuando el nombre contiene caracteres restringidos tales como: \/:*?"<>|

    Returns:
        str: Nombre del folder recién creado, el cual será usado como referencia para escribir los resultados
    """
    while True:
        try:
            invalid_chr = set(r'\/:*?"<>|')
            folder_name_input = input(f"Enter the folder name to save the '{results_type}' files: ").strip()
            if folder_name_input.lower() == "q":
                return None
            if not folder_name_input:
                raise ValueError("You entered an empty name. Try it again or type 'q' to cancel.")
            if any(chr in folder_name_input for chr in invalid_chr):
                raise ValueError(f"Invalid character for folder name was detected. Avoid {invalid_chr}")
            if not os.path.exists(folder_name_input):
                os.makedirs(folder_name_input)
            return folder_name_input
        except ValueError as e:
            print(f"Error: {e}")
def log_analyzer():
    """
    Analiza un registro de correos y extrae la información de correos enviados por remitentes y sellos de tiempo.

    Esta función solicita al usuario el nombre del archivo y luego analiza linea por linea, extrayendo información relevanta como
    remitente individual, dominio del correo del remitente, la hora, dia, mes y año en el que se enviaron los correos. La informacion extraida
    se almacena en un diccionario estructurado que lasifica los datos extraidos en diferentes categorias para analisis posteriores.


    Returns:
        dict: Un diccionario con la siguiente estructura:
        -"individual_sender": Diccinario que contiene el correo del remitente individual y el número de correos que ha enviado
        -"institutional_sender": Diccionario que contiene los dominios de los correos y el número de correos enviados por dominio
        -"timestamp": que contiene:
            -"hour": Diccionario con cada hora del día y el número de correos enviados por cada hora
            -"week_day": Diccionario con cada día de la semana y el número de correos enviado por cada día
            -"month": Diccionario que contiene los meses del año y el número de correos enviado por mes
            -"year": Diccionario que contiene los años en los que enviaron los correos y el número de correos por año.
    """
    extracted_info = {"individual_sender": {},
                      "institutional_sender": {},
                      "timestamp": {
                          "hour": {},
                          "week_day":{},
                          "month": {},
                          "year": {}
                      }
                      }
    while True:
        try:
            fname = input("Enter the file name: ")
            #Permitir salir al usuario salir del programa
            if fname.lower() == "q":
                print("Closing the program...")
                return None
            with open(fname, "r") as file:
                for line in file:
                    line = line.rstrip()
                    #Ignorar lineas que no son relevantes
                    if len(line) == 0 or not line.startswith("From "): continue
                    line = line.split()
                    #Extraer informacion con base a composicion de la linea
                    email_split = line[1].split("@")
                    hour_extract = line[5].split(":")[0]
                    ind_email = email_split[0]
                    inst_email = email_split[1]
                    weekday_extract = line[2]
                    month_extract = line[3]
                    year_extract = line[-1]
                    #Actualizar el diccionario, añadiendo los datos en la categoria correspondiente
                    extracted_info["individual_sender"][ind_email] = extracted_info["individual_sender"].get(ind_email, 0) + 1
                    extracted_info["institutional_sender"][inst_email] = extracted_info["institutional_sender"].get(inst_email, 0) + 1
                    extracted_info["timestamp"]["hour"][hour_extract] = extracted_info["timestamp"]["hour"].get(hour_extract, 0) + 1
                    extracted_info["timestamp"]["week_day"][weekday_extract] = extracted_info["timestamp"]["week_day"].get(weekday_extract, 0) +1
                    extracted_info["timestamp"]["month"][month_extract] = extracted_info["timestamp"]["month"].get(month_extract, 0) + 1
                    extracted_info["timestamp"]["year"][year_extract] = extracted_info["timestamp"]["year"].get(year_extract, 0) + 1
                return extracted_info
        except FileNotFoundError:
            print(f"The file '{fname}' doesn't exist. Try it again. Or type 'q' to exit.")
def csv_counts_export(dic):
    """
    Esta función exporta los resultados del análisis por categoria de manera separada en formato .csv,
    y los guarda en una carpeta o ruta asignada por el usuario

    Args:
        dic (dict): Toma como entrada el diccionario producido por la función log_analyzer()
    Returns:
        None: Escribe los resultados en archivos .csv separados por nombre de categoria dentro de la carpeta asignada por el usuario
    """
    # Crear el folder si no existe
    results_folder = folder_creator("CSV")
    for category, data in dic.items():
        try:
            if category == "timestamp":
                for sublabel, subdata in data.items():
                    filename = os.path.join(results_folder, f"{sublabel}_results.csv")
                    with open(filename, "w", newline="") as outputfile:
                        writer = csv.writer(outputfile)
                        writer.writerow([sublabel, "Email counts"])
                        writer.writerows(subdata.items())
            else:
                filename = os.path.join(results_folder, f"{category}_results.csv")
                with open(filename, "w", newline="") as outputfile:
                    writer = csv.writer(outputfile)
                    writer.writerow([category, "Email counts"])
                    writer.writerows(data.items())
        except Exception as e:
            print(f"Ocurrió un error al guardar '{category}': {e}")
def email_stats(dic):
    """
    Calcula las estadisticas de los datos extraidos del email log almacenados en un diccionario que recibe como entrada

    Args:
        dic (dict): Diccionario que almacena los datos extraídos del email log, con claves como 'individual_sender',
                    'institutional_sender', y 'timestamp' que contiene las horas, días de la semana y meses.

   Returns:
        dict: Diccionario con las estadísticas que incluyen el total de correos, promedio de correos por día,
              remitente con más correos, dominio con más correos, y distribuciones de correo por hora, día y mes
              organizados de manera cronológica.
    """
    days_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    months_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    total_emails = sum(dic["individual_sender"].values())
    max_sender = max(dic["individual_sender"].items(), key = lambda item: item[1])
    max_domain = max(dic["institutional_sender"].items(), key = lambda item: item[1])
    avg_day = f"{(sum(dic["individual_sender"].values()) / 7):.2f}"
    stats = {
        "Total correos": total_emails,
        "Promedio de correos por día": avg_day,
        "Remitente con más correos": f"{max_sender[0]}: {max_sender[1]}",
        "Dominio con más correos": f"{max_domain[0]}: {max_domain[1]}",
        "Distribución de correos por día de semana": [(day, dic["timestamp"]["week_day"].get(day, 0)) for day in days_order],
        "Distribución de correos por mes": [(month, dic["timestamp"]["month"].get(month, 0)) for month in months_order],
        "Distribución de correos por hora": sorted(dic["timestamp"]["hour"].items(), key= lambda item: item[0]),
        "Distribución de correos por año": sorted(dic["timestamp"]["year"].items(), key= lambda item: item[0])
    }
    return stats
def display_stats(dic):
    """
    Esta función muestra las estadisticas de un registro de correos en una tabla formateada

    Args:
        dic (dict): Diccionario que contiene las estadisticas del registro de correos con llaves para estadisticas generales y distribuciones
                    de correo por hora, día, mes y año
    Returns:
        None: Imprime las tablas directamente en la consola.
    """
    dic_tuple = list(dic.items())
    #Mostrar stats generales
    print("\nEstadisticas generales")
    print(tabulate(dic_tuple[0:4], headers=["Descriptor", "Resultado"], tablefmt="simple_grid"))
    #Mostrar estadisticas de distribuciones en tablas separadas
    for category, data in dic_tuple[4:]:
        if "día" in category:
            header = ["Día", "Conteo"]
        elif "mes" in category:
            header = ["Mes", "Conteo"]
        elif "hora" in category:
            header = ["Hora", "Conteo"]
        elif "año" in category:
            header = ["Año", "Conteo"]
        #imprime el nombre de la categoria de la distribucion y la tabla correspondiente
        print(category)
        print(tabulate(data, headers=header, tablefmt="simple_grid"))
        print() #linea extra para legibilidad
def plot_data_organizer(dic1, dic2):
    """
    Esta función extrae, organiza y retorna una lista de tuplas que contiene los datos de los conteos individuales e institucionales junto con
    las distribuciones de los conteos por hora, dia mes y año en una lista de tuplas formateada
    para la generación de gráficos que se usa como entrada en la funcion bar_plot()

    Args:
        dic1 (dict): Diccionario obtenido con la funcion log_analyzer() para extraer y organizar las listas conteos por individuo y dominio
        dic2 (dict): Diccionari obtenido con al funcion email_stats() para extraer las listas que contienen la distribución de correos por hora, dia, mes y año
    
    Returns:
        list: Lista de tuplas formatada de la forma [(category, data)]
    """
    #extracción de los conteos de correos de individuos y dominios a partir del diccionario que tiene todos los conteos
    sender_data = list(dic1.items())
    dic1_labeled = [(category, list(data.items())) for category, data in sender_data]
    dic1_chopped = dic1_labeled[:2]
    #organizar los conteos de manera ascendente
    for category, data in dic1_chopped:
        data.sort(key=lambda item: item[1])
    #extraccion de las distribuciones de los conteos por hora, día, mes y año del diccionario de las estadisticas
    distribution_data = list(dic2.items())
    dic2_labeled = [(category, data) for category, data in distribution_data]
    dic2_chopped = dic2_labeled[4:]
    #concatenación de listas para graficar
    organized_plot_data = dic1_chopped + dic2_chopped
    return organized_plot_data
def bar_plot(plot_data):
    """
    Genera gráficos de barras que permiten la visualizacion de los resultados del análisis del email log.

    Args:
        plot_data (list): Lista de tuplas generada por la función data_plot_organizer()

    Returns:
        None: Genera los gráficos de barra y los guarda individualmente.
    """
    plot_format = {"individual_sender": {
        "title": "Emails sent by individual",
        "xlabel": "Individuals",
        "filename": "ind_sender_bar_plot.png"
    },
    "institutional_sender": {
        "title": "Emails sent by institutional domain",
        "xlabel": "Email domains",
        "filename": "domain_sender_bar_plot.png"
    },
    "Distribución de correos por día de semana": {
        "title": "Mails distribution by day",
        "xlabel": "Day",
        "filename": "day_distribution_bar_plot.png"
    },
    "Distribución de correos por mes": {
        "title": "Mails distribution by month",
        "xlabel": "Month",
        "filename": "month_distribution_bar_plot.png"
    },
    "Distribución de correos por hora": {
        "title": "Mails distribution by hour",
        "xlabel": "Hour",
        "filename": "hour_distribution_bar_plot.png"
    },
    "Distribución de correos por año": {
        "title": "Mails distribution by year",
        "xlabel": "Year",
        "filename": "year_distribution_bar_plot.png"
    }
    }
    plots_folder = folder_creator("Plot")
    for category, data in plot_data:
        label, datos = zip(*data)
        plt.bar(label, datos)
        plt.title(plot_format[category]["title"])
        plt.xlabel(plot_format[category]["xlabel"])
        plt.ylabel("Email counts")
        plt.xticks(rotation=90)
        plt.tight_layout()
        full_path = os.path.join(plots_folder, plot_format[category]["filename"])
        plt.savefig(full_path, format = "png", dpi = 300)
        plt.clf()


results = log_analyzer()
if results:
    csv_counts_export(results)
    stats = email_stats(results)
    display_stats(stats)
    data_to_plot = plot_data_organizer(results, stats)
    bar_plot(data_to_plot)

