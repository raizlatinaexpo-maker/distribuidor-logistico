import pandas as pd

from rapidfuzz import process


def load_products(excel_file):

    df = pd.read_excel(excel_file)

    required_columns = [
        "PRODUCTO",
        "PESO_KG",
        "PRECIO_COP"
    ]

    for col in required_columns:

        if col not in df.columns:

            raise Exception(
                f"Falta columna: {col}"
            )

    df["PRODUCTO"] = (
        df["PRODUCTO"]
        .astype(str)
        .str.strip()
    )

    return df


def find_product(
        product_name,
        df):

    product_name = (
        str(product_name)
        .strip()
    )

    choices = (
        df["PRODUCTO"]
        .tolist()
    )

    match = process.extractOne(
        product_name,
        choices,
        score_cutoff=70
    )

    if not match:

        raise Exception(
            f"No encontrado: {product_name}"
        )

    best_name = match[0]

    row = df[
        df["PRODUCTO"]
        == best_name
    ].iloc[0]

    return {

        "name":
        row["PRODUCTO"],

        "weight":
        float(
            row["PESO_KG"]
        ),

        "price":
        float(
            row["PRECIO_COP"]
        )
    }