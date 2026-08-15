from time import sleep

from bs4 import BeautifulSoup

from selenium.webdriver.chrome.service import Service
from selenium import webdriver

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from datetime import datetime

from urllib.parse import urljoin

import pandas as pd


# =========================================================
# CONFIGURACIÓN
# =========================================================


service = Service("/usr/bin/chromedriver")

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=service, options=options)

url = "https://books.toscrape.com/index.html"

extraido_por = "Sebastián Giraldo Franco y Juan José Jaramillo Mora"


# =========================================================
# ABRIR PÁGINA PRINCIPAL
# =========================================================


driver.get(url)

main_page_soup = BeautifulSoup(driver.page_source, "html.parser")


# =========================================================
# EXTRAER CATEGORÍAS
# =========================================================


category_items = main_page_soup.select("ul.nav-list ul li a")
data_category = []

for item in category_items:

    category_name = item.get_text(strip = True)
    category_url = urljoin(url, item.get("href"))
    
    driver.get(category_url)

    category_soup = BeautifulSoup(driver.page_source, "html.parser")

    strong = category_soup.select_one("form.form-horizontal strong")
    category_total_books = int(strong.get_text(strip=True))

    data_category.append({
        "categoria":category_name,
        "url_categoria":category_url,
        "cantidad_libros":category_total_books,
        "fecha_extraccion":datetime.now(),
        "extraido_por":extraido_por
    })


# =========================================================
# GUARDAR CATEGORÍAS
# =========================================================


category_dataframe = pd.DataFrame(data_category)

category_dataframe.to_parquet("categorias.parquet", index = False)


# =========================================================
# EXTRAER LIBROS POR CATEGORÍA
# =========================================================


data_book = []

ratings = {

    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5

}


for category in data_category:

    category_name = category["categoria"]

    current_page_url = category["url_categoria"]

    print(
        f"\nProcesando categoría: {category_name}"
    )


    while current_page_url:

        driver.get(current_page_url)

        page_soup = BeautifulSoup(
            driver.page_source,
            "html.parser"
        )


        # ---------------------------------------------
        # LIBROS DE LA PÁGINA ACTUAL
        # ---------------------------------------------

        links_to_detail_pages = page_soup.select(
            "article.product_pod h3 a"
        )


        for link in links_to_detail_pages:

            detail_url = urljoin(
                current_page_url,
                link.get("href")
            )

            driver.get(detail_url)

            detail_soup = BeautifulSoup(
                driver.page_source,
                "html.parser"
            )


            # -----------------------------------------
            # INFORMACIÓN DEL PRODUCTO
            # -----------------------------------------

            product_info = detail_soup.select(
                "table.table-striped td"
            )

            upc = product_info[0].get_text(
                strip=True
            )

            product_type = product_info[1].get_text(
                strip=True
            )

            price_tax_free = float(
                product_info[2]
                .get_text(strip=True)
                .replace("£", "")
            )

            price_with_tax = float(
                product_info[3]
                .get_text(strip=True)
                .replace("£", "")
            )

            tax = float(
                product_info[4]
                .get_text(strip=True)
                .replace("£", "")
            )

            availability = product_info[5].get_text(
                strip=True
            )

            reviews = int(
                product_info[6].get_text(strip=True)
            )


            # -----------------------------------------
            # TÍTULO
            # -----------------------------------------

            title = detail_soup.select_one(
                "div.product_main h1"
            ).get_text(strip=True)


            # -----------------------------------------
            # CATEGORÍA
            # -----------------------------------------

            book_category = detail_soup.select(
                "ul.breadcrumb li"
            )[2].get_text(strip=True)


            # -----------------------------------------
            # DESCRIPCIÓN
            # -----------------------------------------

            description_element = detail_soup.select_one(
                "#product_description + p"
            )

            if description_element:

                description = description_element.get_text(
                    strip=True
                )

            else:

                description = ""


            # -----------------------------------------
            # STOCK
            # -----------------------------------------

            stock = int(
                "".join(
                    number
                    for number in availability
                    if number.isdigit()
                )
                or 0
            )


            # -----------------------------------------
            # CALIFICACIÓN
            # -----------------------------------------

            rating_element = detail_soup.find(
                "p",
                class_="star-rating"
            )

            rating = ratings[
                rating_element["class"][1]
            ]


            # -----------------------------------------
            # IMAGEN
            # -----------------------------------------

            img_element = detail_soup.select_one(
                "div.item.active img"
            )

            img_url = urljoin(
                detail_url,
                img_element.get("src")
            )


            # -----------------------------------------
            # GUARDAR LIBRO
            # -----------------------------------------

            data_book.append({

                "upc": upc,

                "titulo": title,

                "categoria": book_category,

                "descripcion": description,

                "tipo_producto": product_type,

                "precio_sin_impuesto": price_tax_free,

                "precio_con_impuesto": price_with_tax,

                "impuesto": tax,

                "moneda": "GBP",

                "disponibilidad": availability,

                "cantidad_stock": stock,

                "calificacion": rating,

                "cantidad_resenas": reviews,

                "url_libro": detail_url,

                "url_imagen": img_url,

                "fecha_extraccion": datetime.now(),

                "extraido_por": extraido_por

            })


            print(
                f"   Libro: {title}"
            )


        # ---------------------------------------------
        # BUSCAR SIGUIENTE PÁGINA DE LA CATEGORÍA
        # ---------------------------------------------

        next_page = page_soup.select_one(
            "li.next a"
        )

        if next_page:

            current_page_url = urljoin(
                current_page_url,
                next_page.get("href")
            )

        else:

            current_page_url = None


# =========================================================
# GUARDAR LIBROS
# =========================================================

book_dataframe = pd.DataFrame(
    data_book
)

book_dataframe.to_parquet(
    "libros.parquet",
    index=False
)


# =========================================================
# FINALIZAR
# =========================================================

driver.quit()
print("\nProceso terminado")
print(
    f"Categorías extraídas: {len(category_dataframe)}"
)
print(
    f"Libros extraídos: {len(book_dataframe)}"
)