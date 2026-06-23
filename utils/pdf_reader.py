import pdfplumber
import re


def extract_order_data(pdf_file):

    text = ""

    with pdfplumber.open(pdf_file) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
    print("\n\n========== TEXTO PDF ==========\n")
    print(text)
    print("\n========== FIN PDF ==========\n\n")

    return parse_order(text)


def parse_order(text):

    data = {
        "order_number": "",
        "customer": "",
        "phone": "",
        "address": "",
        "city": "",
        "state": "",
        "postal_code": "",
        "country": "",
        "products": []
    }

    # Eliminar duplicados si el PDF repite páginas

    first_order = text.find("Orden #")

    second_order = text.find(
        "Orden #",
        first_order + 1
    )

    if second_order != -1:
        text = text[:second_order]

    # Número de pedido

    order_match = re.search(
        r"Orden #(\d+)",
        text
    )

    if order_match:
        data["order_number"] = order_match.group(1)

    # Cliente

    customer_match = re.search(
        r"Enviar a:\s*\n(.*?)\nTeléfono:",
        text,
        re.DOTALL
    )

    if customer_match:

        data["customer"] = (
            customer_match.group(1)
            .strip()
        )

    # Teléfono

    phone_match = re.search(
        r"Teléfono:\s*(.*)",
        text
    )

    if phone_match:

        data["phone"] = (
            phone_match.group(1)
            .strip()
        )

    # Dirección

    lines = text.split("\n")

    shipping_index = None

    for i, line in enumerate(lines):

        if "Teléfono:" in line:
            shipping_index = i
            break

    if shipping_index is not None:

        address_lines = []

        for line in lines[
            shipping_index + 1:
            shipping_index + 5
        ]:

            address_lines.append(
                line.strip()
            )

        if len(address_lines) >= 2:

            data["address"] = (
                address_lines[0]
                + " "
                + address_lines[1]
            )

        if len(address_lines) >= 3:

            city_line = address_lines[2]

            city_match = re.match(
                r"(.*?),\s*(.*?),\s*(\d+)",
                city_line
            )

            if city_match:

                data["city"] = (
                    city_match.group(1)
                    .strip()
                )

                data["state"] = (
                    city_match.group(2)
                    .strip()
                )

                data["postal_code"] = (
                    city_match.group(3)
                    .strip()
                )

        if len(address_lines) >= 4:

            data["country"] = (
                address_lines[3]
                .strip()
            )

    # Productos

    data["products"] = (
        extract_products(text)
    )

    return data


def extract_products(text):

    lines = text.split("\n")

    products = []

    started = False

    current_name = []

    stop_words = [
        "Subtotal",
        "Costo de envío",
        "Total:",
        "Medio de pago",
        "Enviar a:"
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if "Producto Cant." in line:

            started = True
            continue

        if not started:
            continue

        if any(
            word in line
            for word in stop_words
        ):
            break

        # Producto en una sola línea:
        # Shampoo de Miel 300ml Click Hair 2

        match = re.match(
            r"^(.*?)\s+(\d+)$",
            line
        )

        if match:

            product_name = (
                " ".join(current_name)
                + " "
                + match.group(1)
            ).strip()

            quantity = int(
                match.group(2)
            )

            products.append({
                "name": product_name,
                "quantity": quantity
            })

            current_name = []

            continue

        # Parte de un nombre largo

        current_name.append(line)

    return products