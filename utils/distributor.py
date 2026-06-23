import math


def calculate_total_weight(products):

    total = 0

    for product in products:

        total += (
            product["weight"]
            * product["quantity"]
        )

    return round(total, 3)


def get_box_type(gross_weight):

    if gross_weight < 5:
        return "CUSTOM BOX"

    elif gross_weight < 9:
        return "STANDARD BOX 1"

    elif gross_weight < 13:
        return "STANDARD BOX 2"

    else:
        return "STANDARD BOX 3"


def distribute_products(
    products,
    max_weight=15,
    packaging_weight=1
):

    total_product_weight = (
        calculate_total_weight(products)
    )

    usable_weight_per_box = (
        max_weight
        - packaging_weight
    )

    if usable_weight_per_box <= 0:

        raise Exception(
            "El peso de embalaje no puede ser mayor al peso máximo."
        )

    num_boxes = math.ceil(
        total_product_weight
        / usable_weight_per_box
    )

    if num_boxes < 1:
        num_boxes = 1

    boxes = []

    for i in range(num_boxes):

        boxes.append({
            "box_number": i + 1,
            "products": [],
            "net_weight": 0,
            "gross_weight": 0,
            "box_type": ""
        })

    # ----------------------------
    # EXPLOTA cantidades
    # ----------------------------

    units = []

    for product in products:

        for _ in range(product["quantity"]):

            units.append({
                "name": product["name"],
                "weight": product["weight"],
                "price": product["price"]
            })

    # ----------------------------
    # Ordenar por peso descendente
    # ----------------------------

    units.sort(
        key=lambda x: x["weight"],
        reverse=True
    )

    # ----------------------------
    # Balanceo por peso
    # ----------------------------

    for unit in units:

        lightest_box = min(
            boxes,
            key=lambda b: b["net_weight"]
        )

        lightest_box["products"].append({
            "name": unit["name"],
            "quantity": 1,
            "weight": unit["weight"],
            "price": unit["price"]
        })

        lightest_box["net_weight"] += (
            unit["weight"]
        )

    # ----------------------------
    # Consolidar cantidades
    # ----------------------------

    for box in boxes:

        grouped = {}

        for item in box["products"]:

            name = item["name"]

            if name not in grouped:

                grouped[name] = {
                    "name": item["name"],
                    "quantity": 0,
                    "weight": item["weight"],
                    "price": item["price"]
                }

            grouped[name]["quantity"] += 1

        box["products"] = list(
            grouped.values()
        )

        box["net_weight"] = round(
            box["net_weight"],
            2
        )

        box["gross_weight"] = round(
            box["net_weight"]
            + packaging_weight,
            2
        )

        box["box_type"] = get_box_type(
            box["gross_weight"]
        )

    return boxes