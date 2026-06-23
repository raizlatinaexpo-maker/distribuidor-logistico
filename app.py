import os
import zipfile
from io import BytesIO

import streamlit as st

from utils.pdf_reader import extract_order_data

from utils.product_matcher import (
load_products,
find_product
)

from utils.distributor import (
distribute_products,
calculate_total_weight
)

from utils.pdf_generator import (
create_output_folder,
generate_commercial_invoice,
generate_packing_list
)

st.set_page_config(
page_title="Raíz Latina Packing",
layout="wide"
)

st.title(
"RAÍZ LATINA BEAUTY SUPPLY"
)

st.write(
"Procesador de pedidos Tiendanube"
)

pdf_file = st.file_uploader(
"Subir PDF Tiendanube",
type=["pdf"]
)

max_weight = st.number_input(
"Peso máximo por caja (kg)",
value=15.0
)

packaging_weight = st.number_input(
"Peso de embalaje por caja (kg)",
value=1.0,
step=0.1
)

if st.button("Procesar Pedido"):

   try:

     if not pdf_file:

         st.error(
            "Debes subir el PDF"
        )

     else:

        order = extract_order_data(
            pdf_file
        )

        products_df = load_products(
            "productos.xlsx"
        )

        st.success(
            "Pedido leído correctamente"
        )

        st.subheader(
            "Información Cliente"
        )

        st.write(
            f"Cliente: {order['customer']}"
        )

        st.write(
            f"Teléfono: {order['phone']}"
        )

        st.write(
            f"Dirección: {order['address']}"
        )

        st.write(
            f"{order['city']}, "
            f"{order['state']} "
            f"{order['postal_code']}"
        )

        st.write(
            order["country"]
        )

        products_for_distribution = []

        for product in order["products"]:

            product_data = find_product(
                product["name"],
                products_df
            )

            products_for_distribution.append({

                "name":
                product_data["name"],

                "quantity":
                product["quantity"],

                "weight":
                float(
                    product_data["weight"]
                ),

                "price":
                float(
                    product_data["price"]
                )
            })

        total_weight = (
            calculate_total_weight(
                products_for_distribution
            )
        )

        st.subheader(
            "Resumen Pedido"
        )

        st.write(
            f"Peso total productos: "
            f"{total_weight} kg"
        )

        boxes = distribute_products(
            products_for_distribution,
            max_weight,
            packaging_weight
        )

        st.write(
            f"Cajas generadas: "
            f"{len(boxes)}"
        )

        for box in boxes:

            st.subheader(
                f"Box {box['box_number']}"
            )

            st.write(
                f"Net Weight: "
                f"{box['net_weight']} kg"
            )

            st.write(
                f"Gross Weight: "
                f"{box['gross_weight']} kg"
            )

            st.write(
                f"Recommended: "
                f"{box['box_type']}"
            )

            for product in box["products"]:

                st.write(
                    f"{product['name']} "
                    f"x "
                    f"{product['quantity']}"
                )

        # ---------------------------------
        # GENERAR PDFs
        # ---------------------------------

        output_folder = (
            create_output_folder(
                order["order_number"],
                order["customer"]
            )
        )

        for box in boxes:

            invoice_file = (
                f"{output_folder}/"
                f"Commercial_Invoice_Box_"
                f"{box['box_number']}.pdf"
            )

            packing_file = (
                f"{output_folder}/"
                f"Packing_List_Box_"
                f"{box['box_number']}.pdf"
            )

            generate_commercial_invoice(
                order,
                box,
                invoice_file
            )

            generate_packing_list(
                order,
                box,
                len(boxes),
                packing_file
            )

        st.success(
            "PDFs generados correctamente"
        )

        # ---------------------------------
        # CREAR ZIP PARA DESCARGA
        # ---------------------------------

        zip_buffer = BytesIO()

        with zipfile.ZipFile(
            zip_buffer,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zipf:

            for root, dirs, files in os.walk(
                output_folder
            ):

                for file in files:

                    file_path = os.path.join(
                        root,
                        file
                    )

                    arcname = os.path.relpath(
                        file_path,
                        os.path.dirname(
                            output_folder
                        )
                    )

                    zipf.write(
                        file_path,
                        arcname
                    )

        zip_buffer.seek(0)

        folder_name = os.path.basename(
            output_folder
        )

        st.download_button(
            label="📦 Descargar carpeta pedido",
            data=zip_buffer.getvalue(),
            file_name=f"{folder_name}.zip",
            mime="application/zip"
        )

      except Exception as e:

         st.error(
           str(e)
        )
