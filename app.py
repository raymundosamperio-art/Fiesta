import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# --- Funciones para manejar la base de datos ---
def conectar():
    return sqlite3.connect("invitados.db")

def crear_invitado(nombre, apellidos, telefono, correo, asistira, acompanantes):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        INSERT INTO invitados (nombre, apellidos, telefono, correo, asistira, acompanantes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nombre, apellidos, telefono, correo, asistira, acompanantes))
    conn.commit()
    conn.close()

def obtener_invitados():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM invitados", conn)
    conn.close()
    return df

def actualizar_invitado(id_, nombre, apellidos, telefono, correo, asistira, acompanantes):
    conn = conectar()
    c = conn.cursor()
    c.execute("""
        UPDATE invitados
        SET nombre=?, apellidos=?, telefono=?, correo=?, asistira=?, acompanantes=?
        WHERE id=?
    """, (nombre, apellidos, telefono, correo, asistira, acompanantes, id_))
    conn.commit()
    conn.close()

def eliminar_invitado(id_):
    conn = conectar()
    c = conn.cursor()
    c.execute("DELETE FROM invitados WHERE id=?", (id_,))
    conn.commit()
    conn.close()

# --- Funciones para exportar datos ---
def exportar_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Invitados")
    output.seek(0)
    return output

def exportar_pdf(df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    titulo = Paragraph("Lista de Invitados - Aniversario 🎉", estilos["Title"])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

    data = [list(df.columns)] + df.values.tolist()
    tabla = Table(data, repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    elementos.append(tabla)
    doc.build(elementos)
    buffer.seek(0)
    return buffer

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Lista de Invitados - Aniversario 🎉", layout="centered")
st.title("🎊 Lista de invitados - Aniversario")

menu = st.sidebar.selectbox("Menú", ["Agregar Invitado", "Ver Invitados", "Actualizar Invitado", "Eliminar Invitado"])

if menu == "Agregar Invitado":
    st.subheader("➕ Agregar nuevo invitado")
    nombre = st.text_input("Nombre")
    apellidos = st.text_input("Apellidos")
    telefono = st.text_input("Teléfono")
    correo = st.text_input("Correo electrónico")
    asistira = st.selectbox("¿Asistirá?", ["Sí", "No", "No ha confirmado"])
    acompanantes = st.number_input("Número de acompañantes", min_value=0, step=1)

    if st.button("Guardar"):
        if nombre and apellidos:
            crear_invitado(nombre, apellidos, telefono, correo, asistira, acompanantes)
            st.success(f"✅ Invitado {nombre} {apellidos} agregado correctamente.")
        else:
            st.warning("Por favor completa al menos nombre y apellidos.")

elif menu == "Ver Invitados":
    st.subheader("📋 Lista de invitados")
    df = obtener_invitados()
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        # --- Indicadores ---
        total = len(df)
        confirmados = len(df[df["asistira"] == "Sí"])
        no_confirmados = len(df[df["asistira"] == "No ha confirmado"])
        no_asistiran = len(df[df["asistira"] == "No"])
        total_personas = df["acompanantes"].sum() + confirmados

        st.markdown("### 📊 Resumen general")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Registrados", total)
        col2.metric("Confirmados", confirmados)
        col3.metric("No han confirmado", no_confirmados)
        col4.metric("No asistirán", no_asistiran)
        col5.metric("Personas esperadas", total_personas)

        # --- Exportar datos ---
        st.markdown("### 📤 Exportar lista")
        col_excel, col_pdf = st.columns(2)

        with col_excel:
            excel_data = exportar_excel(df)
            st.download_button(
                label="📗 Descargar Excel",
                data=excel_data,
                file_name="lista_invitados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col_pdf:
            pdf_data = exportar_pdf(df)
            st.download_button(
                label="📕 Descargar PDF",
                data=pdf_data,
                file_name="lista_invitados.pdf",
                mime="application/pdf"
            )

elif menu == "Actualizar Invitado":
    st.subheader("✏️ Actualizar datos de invitado")
    df = obtener_invitados()
    if not df.empty:
        id_seleccionado = st.selectbox("Selecciona invitado por ID", df["id"])
        invitado = df[df["id"] == id_seleccionado].iloc[0]

        nombre = st.text_input("Nombre", invitado["nombre"])
        apellidos = st.text_input("Apellidos", invitado["apellidos"])
        telefono = st.text_input("Teléfono", invitado["telefono"])
        correo = st.text_input("Correo electrónico", invitado["correo"])
        asistira = st.selectbox("¿Asistirá?", ["Sí", "No", "No ha confirmado"], index=["Sí", "No", "No ha confirmado"].index(invitado["asistira"]))
        acompanantes = st.number_input("Número de acompañantes", min_value=0, step=1, value=int(invitado["acompanantes"]))

        if st.button("Actualizar"):
            actualizar_invitado(id_seleccionado, nombre, apellidos, telefono, correo, asistira, acompanantes)
            st.success(f"✅ Invitado {nombre} {apellidos} actualizado correctamente.")
    else:
        st.info("No hay invitados registrados todavía.")

elif menu == "Eliminar Invitado":
    st.subheader("🗑️ Eliminar invitado")
    df = obtener_invitados()
    if not df.empty:
        id_eliminar = st.selectbox("Selecciona el ID del invitado a eliminar", df["id"])
        invitado = df[df["id"] == id_eliminar].iloc[0]
        st.write(f"Vas a eliminar a: **{invitado['nombre']} {invitado['apellidos']}**")

        if st.button("Eliminar"):
            eliminar_invitado(id_eliminar)
            st.success("✅ Invitado eliminado correctamente.")
    else:
        st.info("No hay invitados para eliminar.")
