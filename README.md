# Taller 1 - Ingeniería de Datos (2026-2)

Universidad EIA - Ingeniería de Datos

Este repositorio contiene las tres partes del Taller 1: extracción de datos mediante **web scraping**, extracción mediante **consumo de una API**, y un **análisis exploratorio de datos (EDA)** sobre un dataset libre de Kaggle.

## Estructura del repositorio

```
.
├── web_scraping/          # Parte 1: Web Scraping (Books to Scrape)
│   ├── scraper.py
│   ├── analisis.ipynb
│   ├── categorias.parquet
│   ├── libros.parquet
│   └── entorno_conda.txt
│
├── apis/                  # Parte 2: API-Football (Copa Mundial)
│   ├── extractor_api.py
│   ├── analisis.ipynb
│   ├── equipos.parquet
│   ├── partidos.parquet
│   ├── clasificacion.parquet
│   └── .env.template
│    
│
└── analisis_exploratorio_de_datos/   # Parte 3: EDA libre (Kaggle)
    └── analisis.ipynb
```

## Parte 1 — Web Scraping

**Fuente:** [Books to Scrape](https://books.toscrape.com/)

Un script en Python (`scraper.py`) recorre el catálogo completo del sitio con **Selenium**, extrae la información de categorías y libros con **BeautifulSoup**, y guarda los resultados en `categorias.parquet` y `libros.parquet` usando **pandas**. El notebook `analisis.ipynb` responde las preguntas de análisis planteadas en el taller.

➡️ Ver [`web_scraping/`](./web_scraping) para más detalle.

## Parte 2 — API-Football

**Fuente:** [API-Football](https://www.api-football.com/) (API-Sports) — Copa Mundial de Fútbol 2026

Un script en Python (`extractor_api.py`) consulta los endpoints `/teams`, `/fixtures` y `/standings`, normaliza los datos (aplanando los objetos JSON anidados y traduciendo los nombres de columna al español) y guarda los resultados en `equipos.parquet`, `partidos.parquet` y `clasificacion.parquet`.

⚠️ **Nota:** el plan gratuito de API-Sports solo da acceso a las temporadas 2022-2024; la temporada 2026 requiere plan de pago. El detalle de esta limitación y cómo se manejó está documentado en el README de esa carpeta.

➡️ Ver [`apis/`](./apis) para instrucciones de instalación, configuración de la API Key y más detalle.

## Parte 3 — Análisis Exploratorio de Datos (Kaggle)

**Dataset:** [Germany Cars Dataset](https://www.kaggle.com/datasets/ander289386/cars-germany) (AutoScout24), obtenido vía `kagglehub`.

Un notebook (`analisis.ipynb`) presenta la descripción general del dataset, análisis univariante y bivariante, y cinco preguntas de análisis propias con su código, resultados y conclusiones.

➡️ Ver [`analisis_exploratorio_de_datos/`](./analisis_exploratorio_de_datos).

## Requisitos generales

- Python 3.12
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- Google Chrome + ChromeDriver (para la Parte 1)
- Cuenta gratuita en API-Sports (para la Parte 2)
- Cuenta de Kaggle (para la Parte 3)

Cada carpeta puede reutilizar el mismo entorno virtual. Instalación general:

```bash
conda create -n taller1_eia python=3.12 -y
conda activate taller1_eia
pip install selenium beautifulsoup4 pandas pyarrow requests python-dotenv webdriver-manager kagglehub seaborn matplotlib jupyter
```

## Autores

Juan José Jaramillo Mora y Sebastián Giraldo Franco
Universidad EIA — Ingeniería de Datos, 2026-2
