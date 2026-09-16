# Pipeline de Extracción y Análisis de Datos

*Proyecto de curso — Ingeniería de Datos, Universidad EIA (2026-2)*

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-WebDriver-43B02A?logo=selenium&logoColor=white)
![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-HTML%20Parsing-yellow)
![Pandas](https://img.shields.io/badge/Pandas-Procesamiento%20de%20Datos-150458?logo=pandas&logoColor=white)
![Parquet](https://img.shields.io/badge/Almacenamiento-Apache%20Parquet-blue)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-F37626?logo=jupyter&logoColor=white)
![Requests](https://img.shields.io/badge/HTTP-Requests-lightgrey)

## Descripción general

Un pipeline de ingeniería de datos en tres etapas que cubre el ciclo completo de adquisición, integración y exploración de datos provenientes de fuentes heterogéneas: un scraper controlado por navegador, un cliente de API REST con normalización de JSON, y un notebook de análisis exploratorio de datos. Toda la información extraída se persiste en formato columnar Parquet para un análisis posterior eficiente.

Cada componente es independiente (con su propio script, dependencias y notebook), pero sigue un diseño consistente: esperas explícitas en lugar de tiempos fijos, normalización de esquemas a columnas tipadas, eliminación de duplicados, y extracción reproducible con metadatos de trazabilidad (fecha de extracción, endpoint de origen).

## Estructura del repositorio

```
.
├── web_scraping/              # Scraping controlado por navegador (Books to Scrape)
│   ├── scraper.py
│   ├── analisis.ipynb
│   ├── categorias.parquet
│   └── libros.parquet
│
├── apis/                       # Integración con API REST (API-Football)
│   ├── extractor_api.py
│   ├── analisis.ipynb
│   ├── equipos.parquet
│   ├── partidos.parquet
│   ├── clasificacion.parquet
│   └── .env.template
│
└── EDA_taller/                 # Análisis exploratorio de datos (dataset de Kaggle)
    └── analisis.ipynb
```

## Componentes

### 1. Web Scraping

Recorre de principio a fin un catálogo paginado, tipo e-commerce, usando **Selenium** para automatizar el navegador y **BeautifulSoup** para analizar el HTML. Recorre recursivamente cada categoría y cada página de paginación para recolectar información a nivel de producto, y luego normaliza y guarda los resultados con **pandas**.

- Esperas dinámicas (`WebDriverWait` + condiciones esperadas) en lugar de tiempos de espera fijos
- Ejecución en modo headless con carga de imágenes deshabilitada, para mayor rendimiento
- Lógica de deduplicación que maneja correctamente los registros que legítimamente pertenecen a más de una categoría

### 2. Integración con API REST

Consume una API externa de datos deportivos (**API-Football**), manejando paginación, autenticación mediante API key en encabezados (cargada desde variables de entorno, nunca escrita directamente en el código), y un caché local de las respuestas crudas para evitar solicitudes redundantes frente a un plan gratuito con límite de tasa.

- Aplana estructuras JSON profundamente anidadas en columnas tabulares normalizadas y tipadas
- Nombres de columna traducidos y estandarizados bajo una convención de nombrado consistente
- Caché de respuestas para evitar llamadas repetidas contra un plan gratuito con límite diario

### 3. Análisis Exploratorio de Datos

Un notebook de EDA estructurado sobre un dataset abierto (anuncios de autos usados en Alemania, obtenido vía `kagglehub`), que cubre perfilamiento del dataset, análisis univariante y bivariante, y un conjunto de preguntas analíticas propias respondidas con código, visualizaciones y conclusiones escritas.

- Análisis de distribución y detección de valores atípicos para variables numéricas
- Análisis de correlación y comparaciones de precio por categoría
- Preguntas de negocio propias, más allá de lo mínimo requerido

## Tecnologías utilizadas

| Categoría | Herramientas |
|---|---|
| Lenguaje | Python 3.12 |
| Automatización web | Selenium, webdriver-manager |
| Parsing | BeautifulSoup4 |
| Procesamiento de datos | pandas, NumPy |
| Almacenamiento | Apache Parquet (PyArrow) |
| HTTP / API | requests, python-dotenv |
| Análisis | Jupyter Notebook, seaborn, matplotlib |
| Entorno | Conda (Miniconda) |

## Instalación

```bash
conda create -n data-pipeline python=3.12 -y
conda activate data-pipeline
pip install selenium beautifulsoup4 pandas pyarrow requests python-dotenv \
            webdriver-manager kagglehub seaborn matplotlib jupyter
```

Cada subcarpeta puede ejecutarse de forma independiente. Ver las secciones siguientes para la configuración específica de cada componente.

### Credenciales de la API

La integración con la API requiere una API key gratuita de API-Football. Copia la plantilla y agrega tu propia clave — nunca se sube al control de versiones:

```bash
cd apis
cp .env.template .env
# edita .env y coloca API_SPORTS_KEY=tu_clave_aqui
```

## Uso

```bash
# Web scraping
cd web_scraping
python scraper.py

# Extracción de API
cd apis
python extractor_api.py

# Análisis exploratorio
jupyter notebook EDA_taller/analisis.ipynb
```

## Limitaciones conocidas

El plan gratuito del proveedor de API-Football restringe el acceso a datos históricos a un rango limitado de temporadas; consultar por fuera de ese rango requiere un plan de pago. El pipeline de extracción maneja esto de forma flexible parametrizando la temporada consultada, permitiendo validar el flujo completo contra una temporada disponible mientras se gestiona un acceso extendido.

## Contexto académico

Desarrollado como proyecto de curso para la asignatura de Ingeniería de Datos en la Universidad EIA (2026-2). El trabajo requería implementar tres estrategias independientes de adquisición de datos — scraping controlado por navegador, consumo de API REST, y exploración de un dataset abierto — evaluadas por la correcta extracción de datos, normalización de esquemas, y profundidad del análisis.

## Autores

Juan José Jaramillo Mora ([@Juanjo1414](https://github.com/Juanjo1414)) y Sebastián Giraldo Franco ([@sebasgiraldo69](https://github.com/sebasgiraldo69))
