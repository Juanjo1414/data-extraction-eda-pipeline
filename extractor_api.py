# Se importan las librerías necesarias.
# pip install requests pandas pyarrow python-dotenv
import os
import json
from datetime import datetime

import requests
import pandas as pd
from dotenv import load_dotenv

# Se lee la API Key desde el archivo .env
load_dotenv()
API_KEY = os.getenv("API_SPORTS_KEY")

if not API_KEY:
    raise ValueError("No se encontró API_SPORTS_KEY. Verifica tu archivo .env")

# Se configuran los datos generales de la conexión y de la consulta.
url_base = "https://v3.football.api-sports.io"
headers = {"x-apisports-key": API_KEY}

liga = 1          # Competición: Copa Mundial
temporada = 2022
extraido_por = "Juan Jose Jaramillo Mora y Sebastian Giraldo Franco"

# Se define una función para consultar cualquier endpoint de la API.
# Recorre todas las páginas de resultados y guarda una copia local en JSON,
# para no volver a consultar la API si el script se corre varias veces.
def consultar_endpoint(endpoint, parametros, archivo_cache):
    if os.path.exists(archivo_cache):
        print(f"Leyendo {endpoint} desde caché local: {archivo_cache}")
        with open(archivo_cache, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"Consultando {endpoint} en la API...")
    resultados_totales = []
    pagina_actual = 1
    total_paginas = 1

    while pagina_actual <= total_paginas:
        parametros_pagina = dict(parametros)
        if pagina_actual > 1:
            parametros_pagina["page"] = pagina_actual

        respuesta = requests.get(url_base + endpoint, headers=headers, params=parametros_pagina)

        if respuesta.status_code != 200:
            raise RuntimeError(
                f"Error al consultar {endpoint}: status {respuesta.status_code} - {respuesta.text}"
            )

        data = respuesta.json()

        if data.get("errors"):
            raise RuntimeError(f"La API devolvió errores en {endpoint}: {data['errors']}")

        resultados_totales.extend(data["response"])

        total_paginas = data.get("paging", {}).get("total", 1)
        print(f"  Página {pagina_actual} de {total_paginas} - {len(data['response'])} registros")
        pagina_actual += 1

    with open(archivo_cache, "w", encoding="utf-8") as f:
        json.dump(resultados_totales, f, ensure_ascii=False, indent=2)

    return resultados_totales

# Se consultan los equipos participantes.
datos_equipos = consultar_endpoint(
    "/teams", {"league": liga, "season": temporada}, f"raw_teams_{temporada}.json"
)

# Se normalizan los datos de equipos
equipos_data = []
for item in datos_equipos:
    equipo = item["team"]
    equipos_data.append({
        "equipo_id": equipo["id"],
        "nombre_equipo": equipo["name"],
        "codigo_equipo": equipo["code"],
        "pais": equipo["country"],
        "anio_fundacion": equipo["founded"],
        "es_seleccion_nacional": equipo["national"],
        "logo_url": equipo["logo"],
        "competencia_id": liga,
        "temporada": temporada,
        "fecha_extraccion": datetime.now().isoformat(),
        "extraido_por": extraido_por,
        "endpoint_origen": "/teams",
    })

df_equipos = pd.DataFrame(equipos_data)
df_equipos = df_equipos.drop_duplicates(subset=["equipo_id"])

# Se convierte cada columna al tipo de dato apropiado.
df_equipos["equipo_id"] = df_equipos["equipo_id"].astype("Int64")
df_equipos["anio_fundacion"] = df_equipos["anio_fundacion"].astype("Int64")
df_equipos["es_seleccion_nacional"] = df_equipos["es_seleccion_nacional"].astype(bool)
df_equipos["competencia_id"] = df_equipos["competencia_id"].astype("Int64")
df_equipos["temporada"] = df_equipos["temporada"].astype("Int64")

print(f"\nequipos: {len(df_equipos)} registros únicos")

# Se consultan todos los partidos de la competición.
datos_fixtures = consultar_endpoint(
    "/fixtures", {"league": liga, "season": temporada}, f"raw_fixtures_{temporada}.json"
)

# Se normalizan los datos de partidos.
partidos_data = []
for item in datos_fixtures:
    fixture = item["fixture"]
    league = item["league"]
    teams = item["teams"]
    goals = item["goals"]
    score = item["score"]

    partidos_data.append({
        "partido_id": fixture["id"],
        "competencia_id": league["id"],
        "competencia_nombre": league["name"],
        "temporada": league["season"],
        "ronda": league["round"],
        "fecha_partido": fixture["date"],
        "zona_horaria": fixture["timezone"],
        "estado_partido": fixture["status"]["long"],
        "minuto_transcurrido": fixture["status"]["elapsed"],
        "arbitro": fixture["referee"],
        "estadio_id": fixture["venue"]["id"],
        "estadio_nombre": fixture["venue"]["name"],
        "estadio_ciudad": fixture["venue"]["city"],
        "equipo_local_id": teams["home"]["id"],
        "equipo_local_nombre": teams["home"]["name"],
        "equipo_visitante_id": teams["away"]["id"],
        "equipo_visitante_nombre": teams["away"]["name"],
        "gano_local": teams["home"]["winner"],
        "gano_visitante": teams["away"]["winner"],
        "goles_local": goals["home"],
        "goles_visitante": goals["away"],
        "penales_local": score["penalty"]["home"],
        "penales_visitante": score["penalty"]["away"],
        "fecha_extraccion": datetime.now().isoformat(),
        "extraido_por": extraido_por,
        "endpoint_origen": "/fixtures",
    })

df_partidos = pd.DataFrame(partidos_data)
df_partidos = df_partidos.drop_duplicates(subset=["partido_id"])

# Se convierte cada columna al tipo de dato apropiado.
df_partidos["partido_id"] = df_partidos["partido_id"].astype("Int64")
df_partidos["competencia_id"] = df_partidos["competencia_id"].astype("Int64")
df_partidos["temporada"] = df_partidos["temporada"].astype("Int64")
df_partidos["fecha_partido"] = pd.to_datetime(df_partidos["fecha_partido"], errors="coerce")
df_partidos["minuto_transcurrido"] = df_partidos["minuto_transcurrido"].astype("Int64")
df_partidos["estadio_id"] = df_partidos["estadio_id"].astype("Int64")
df_partidos["equipo_local_id"] = df_partidos["equipo_local_id"].astype("Int64")
df_partidos["equipo_visitante_id"] = df_partidos["equipo_visitante_id"].astype("Int64")
df_partidos["gano_local"] = df_partidos["gano_local"].astype("boolean")
df_partidos["gano_visitante"] = df_partidos["gano_visitante"].astype("boolean")
df_partidos["goles_local"] = df_partidos["goles_local"].astype("Int64")
df_partidos["goles_visitante"] = df_partidos["goles_visitante"].astype("Int64")
df_partidos["penales_local"] = df_partidos["penales_local"].astype("Int64")
df_partidos["penales_visitante"] = df_partidos["penales_visitante"].astype("Int64")

print(f"partidos: {len(df_partidos)} registros únicos")

# Se consulta la clasificación de los grupos.
datos_standings = consultar_endpoint(
    "/standings", {"league": liga, "season": temporada}, f"raw_standings_{temporada}.json"
)

# Se normalizan los datos de clasificación (por competición, por grupo y por equipo).
clasificacion_data = []
for item in datos_standings:
    league = item["league"]
    competencia_id = league["id"]
    temporada_actual = league["season"]

    for grupo in league["standings"]:
        for posicion_equipo in grupo:
            equipo = posicion_equipo["team"]
            todos = posicion_equipo["all"]

            clasificacion_data.append({
                "grupo": posicion_equipo["group"],
                "posicion": posicion_equipo["rank"],
                "equipo_id": equipo["id"],
                "nombre_equipo": equipo["name"],
                "puntos": posicion_equipo["points"],
                "partidos_jugados": todos["played"],
                "partidos_ganados": todos["win"],
                "partidos_empatados": todos["draw"],
                "partidos_perdidos": todos["lose"],
                "goles_favor": todos["goals"]["for"],
                "goles_contra": todos["goals"]["against"],
                "diferencia_gol": posicion_equipo["goalsDiff"],
                "forma_reciente": posicion_equipo["form"],
                "estado_clasificacion": posicion_equipo["status"],
                "descripcion_clasificacion": posicion_equipo["description"],
                "fecha_actualizacion": posicion_equipo["update"],
                "competencia_id": competencia_id,
                "temporada": temporada_actual,
                "fecha_extraccion": datetime.now().isoformat(),
                "extraido_por": extraido_por,
                "endpoint_origen": "/standings",
            })

df_clasificacion = pd.DataFrame(clasificacion_data)
df_clasificacion = df_clasificacion.drop_duplicates(subset=["grupo", "equipo_id"])

# Se convierte cada columna al tipo de dato apropiado.
df_clasificacion["posicion"] = df_clasificacion["posicion"].astype("Int64")
df_clasificacion["equipo_id"] = df_clasificacion["equipo_id"].astype("Int64")
df_clasificacion["puntos"] = df_clasificacion["puntos"].astype("Int64")
df_clasificacion["partidos_jugados"] = df_clasificacion["partidos_jugados"].astype("Int64")
df_clasificacion["partidos_ganados"] = df_clasificacion["partidos_ganados"].astype("Int64")
df_clasificacion["partidos_empatados"] = df_clasificacion["partidos_empatados"].astype("Int64")
df_clasificacion["partidos_perdidos"] = df_clasificacion["partidos_perdidos"].astype("Int64")
df_clasificacion["goles_favor"] = df_clasificacion["goles_favor"].astype("Int64")
df_clasificacion["goles_contra"] = df_clasificacion["goles_contra"].astype("Int64")
df_clasificacion["diferencia_gol"] = df_clasificacion["diferencia_gol"].astype("Int64")
df_clasificacion["fecha_actualizacion"] = pd.to_datetime(
    df_clasificacion["fecha_actualizacion"], errors="coerce"
)
df_clasificacion["competencia_id"] = df_clasificacion["competencia_id"].astype("Int64")
df_clasificacion["temporada"] = df_clasificacion["temporada"].astype("Int64")

print(f"clasificacion: {len(df_clasificacion)} registros únicos")

# Se guardan los resultados en archivos Parquet.
df_equipos.to_parquet("equipos.parquet", index=False)
df_partidos.to_parquet("partidos.parquet", index=False)
df_clasificacion.to_parquet("clasificacion.parquet", index=False)

print("\nExtracción completada")
print("equipos.parquet, partidos.parquet y clasificacion.parquet guardados correctamente.")