import os
import random
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib import enums
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)

LOGO_PATH = "utils/logo.png"


def create_output_folder(order_number, customer):

    safe_customer = "".join(
        c if c.isalnum() or c in " _-" else "_"
        for c in customer.upper()
    ).strip()

    folder = os.path.join(
        "output",
        f"{order_number}_{safe_customer}"
    )

    os.makedirs(folder, exist_ok=True)

    return folder


def generate_declared_value():
    return round(random.uniform(64, 65), 2)


def _styles():

    styles = getSampleStyleSheet()

    styles.add(
        ParagraphStyle(
            name="Small",
            fontSize=8,
            leading=10
        )
    )

    styles.add(
        ParagraphStyle(
            name="NormalWrap",
            fontSize=9,
            leading=11,
            alignment=enums.TA_LEFT
        )
    )

    return styles


def _logo():

    if os.path.exists(LOGO_PATH):

        return Image(
            LOGO_PATH,
            width=180,
            height=100
        )

    return Paragraph(
        "RAIZ LATINA",
        _styles()["Normal"]
    )


def generate_commercial_invoice(
    order,
    box,
    output_path
):

    styles = _styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=25,
        rightMargin=25,
        topMargin=20,
        bottomMargin=20
    )

    elements = []

    header = Table([[
        _logo(),
        Paragraph(
            f"<b>FACTURA COMERCIAL</b><br/>"
            f"Orden #{order['order_number']}<br/>"
            f"Caja {box['box_number']}",
            styles["Normal"]
        )
    ]], colWidths=[250, 250])

    elements.append(header)
    elements.append(Spacer(1, 10))

    company = Paragraph(
        "<b>RAÍZ LATINA BEAUTY SUPPLY</b><br/>"
        "Itagüí, Antioquia, Colombia<br/>"
        "+57 3242128894<br/>"
        "raizlatinaexpo@gmail.com",
        styles["NormalWrap"]
    )

    customer = Paragraph(
        f"<b>CLIENTE</b><br/>"
        f"{order['customer']}<br/>"
        f"{order['address']}<br/>"
        f"{order['city']}, {order['state']} {order['postal_code']}<br/>"
        f"{order['country']}<br/>"
        f"{order['phone']}",
        styles["NormalWrap"]
    )

    elements.append(
        Table([[company, customer]], colWidths=[260, 260])
    )

    elements.append(Spacer(1, 12))

    declared_value = generate_declared_value()

    total_weight = sum(
        p["weight"] * p["quantity"]
        for p in box["products"]
    )

    rows = [[
        Paragraph("<b>DESCRIPCIÓN PRODUCTO</b>", styles["Normal"]),
        Paragraph("<b>CANTIDAD</b>", styles["Normal"]),
        Paragraph("<b>VALOR UNITARIO USD</b>", styles["Normal"]),
        Paragraph("<b>VALOR TOTAL USD</b>", styles["Normal"])
    ]]

    for p in box["products"]:

        product_weight = p["weight"] * p["quantity"]

        proportion = (
            product_weight / total_weight
            if total_weight > 0 else 0
        )

        total_usd = round(
            declared_value * proportion,
            2
        )

        unit_usd = round(
            total_usd / p["quantity"],
            2
        )

        rows.append([
            Paragraph(p["name"], styles["NormalWrap"]),
            str(p["quantity"]),
            f"${unit_usd:.2f}",
            f"${total_usd:.2f}"
        ])

    table = Table(
        rows,
        colWidths=[290, 60, 90, 90]
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
    ]))

    elements.append(table)
    elements.append(Spacer(1, 12))

    total_units = sum(
        p["quantity"]
        for p in box["products"]
    )

    summary = Table([
        ["Valor Declarado", f"USD {declared_value:.2f}"],
        ["Total Unidades", str(total_units)]
    ], colWidths=[150, 150])

    summary.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black)
    ]))

    elements.append(summary)
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "Declaro que la información contenida en esta factura es correcta.",
            styles["Small"]
        )
    )

    elements.append(Spacer(1, 40))
    elements.append(Paragraph("__________________________", styles["Normal"]))
    elements.append(Paragraph("Firma Autorizada", styles["Normal"]))

    doc.build(elements)


def generate_packing_list(
    order,
    box,
    total_boxes,
    output_path
):

    styles = _styles()

    packing_title_style = ParagraphStyle(
        "PackingTitle",
        parent=styles["Normal"],
        fontSize=18,
        leading=22,
        alignment=2
    )

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=25,
        rightMargin=25,
        topMargin=20,
        bottomMargin=20
    )

    elements = []

    header = Table([[
        _logo(),
        Paragraph(
            f"<b>PACKING LIST</b><br/>"
            f"Orden #{order['order_number']}<br/>"
            f"Caja {box['box_number']} de {total_boxes}",
            packing_title_style
        )
    ]], colWidths=[250, 250])

    elements.append(header)
    elements.append(Spacer(1, 10))

    elements.append(
        Paragraph(
            f"<b>Cliente:</b> {order['customer']}<br/>"
            f"<b>País:</b> {order['country']}",
            styles["NormalWrap"]
        )
    )

    elements.append(Spacer(1, 10))

    rows = [[
        Paragraph("<b>PRODUCTO</b>", styles["Normal"]),
        Paragraph("<b>CANT</b>", styles["Normal"]),
        Paragraph("<b>REV 1</b>", styles["Normal"]),
        Paragraph("<b>REV 2</b>", styles["Normal"])
    ]]

    for p in box["products"]:

        rev1 = Table(
          [[""]],
          colWidths=[12],
          rowHeights=[12]
     )

        rev1.setStyle(TableStyle([
          ("GRID", (0, 0), (-1, -1), 0.8, colors.black)
     ]))

        rev2 = Table(
          [[""]],
          colWidths=[12],
          rowHeights=[12]
     )

        rev2.setStyle(TableStyle([
          ("GRID", (0, 0), (-1, -1), 0.8, colors.black)
     ]))

        rows.append([
          Paragraph(
           p["name"],
           styles["NormalWrap"]
     ),
         str(p["quantity"]),
           rev1,
           rev2
     ])

    table = Table(
        rows,
        colWidths=[350, 60, 50, 50]
    )

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 1), (3, -1), "CENTER")
    ]))

    elements.append(table)
    elements.append(Spacer(1, 25))

    total_units = sum(
        p["quantity"]
        for p in box["products"]
    )

    info_table = Table([
        ["Peso Neto", f"{box['net_weight']} kg"],
        ["Peso Bruto", f"{box['gross_weight']} kg"],
        ["Tipo Caja", box["box_type"]],
        ["Total Unidades", str(total_units)]
    ], colWidths=[170, 170])

    info_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black)
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 12))

    elements.append(
        Paragraph(
            "□ CAJA COMPLETADA",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 25))

    elements.append(Paragraph("Empacado por:", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("__________________________", styles["Normal"]))

    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Firma:", styles["Normal"]))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("__________________________", styles["Normal"]))

    doc.build(elements)
