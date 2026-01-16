import streamlit as st
import re
import uuid
from datetime import datetime, date
from sqlalchemy import create_engine, text

# =====================
# CONFIGURACIÓN STREAMLIT
# =====================
st.set_page_config(
    page_title="Coffee shop",
    page_icon="☕",
    layout="centered"
)

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# =====================
# CONEXIÓN A RDS (MySQL)
# =====================
engine = create_engine(
    st.secrets["db"]["url"],
    pool_pre_ping=True
)

# =====================
# FUNCIONES
# =====================
def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def generate_unique_id() -> str:
    return str(uuid.uuid4())

def save_contact(uid, nombre, email, fecha_nacimiento, timestamp):
    sql = """
    INSERT INTO contactos (id, nombre, email, fecha_nacimiento, created_at)
    VALUES (:id, :nombre, :email, :fecha_nacimiento, :created_at)
    ON DUPLICATE KEY UPDATE
        nombre = VALUES(nombre),
        fecha_nacimiento = VALUES(fecha_nacimiento);
    """
    with engine.begin() as conn:
        conn.execute(
            text(sql),
            {
                "id": uid,
                "nombre": nombre,
                "email": email,
                "fecha_nacimiento": fecha_nacimiento,
                "created_at": timestamp,
            }
        )

# =====================
# FRONT
# =====================
st.write("##")
st.title("¡Únete a la familia de cafeteros!")

c1, c2 = st.columns(2)

with c1:
    st.write("##")
    st.image("assets/logo.png")

with c2:
    st.write("##")
    nombre = st.text_input("Nombre*", placeholder="Tu nombre")
    email = st.text_input("Email*", placeholder="Tu mejor email")
    fecha_nacimiento = st.date_input(
        "Fecha de nacimiento",
        help="Tu cumpleaños es importante para nosotros, te enviaremos un regalo especial 😉",
        value=None
    )
    policy = st.checkbox("Acepto recibir emails por parte de la empresa")

    enviar = st.button("Enviar ☕")

    # =====================
    # BACK
    # =====================
    if enviar:
        if not nombre:
            st.error("Por favor, completa el campo del nombre")
        elif not email:
            st.error("Por favor, completa el campo del email")
        elif not validate_email(email):
            st.error("Por favor, ingresa un email válido")
        elif not policy:
            st.error("Por favor, acepta la política de privacidad")
        elif fecha_nacimiento is not None and fecha_nacimiento > date.today():
            st.error("Por favor, ingresa una fecha de nacimiento válida")
        else:
            try:
                with st.spinner("Guardando información..."):
                    uid = generate_unique_id()
                    timestamp = datetime.now()

                    save_contact(
                        uid=uid,
                        nombre=nombre.strip(),
                        email=email.strip().lower(),
                        fecha_nacimiento=fecha_nacimiento,
                        timestamp=timestamp
                    )

                st.success("¡Gracias por unirte a la familia de cafeteros! ☕")

            except Exception as e:
                st.exception(e)

st.write("##")
st.caption("© 2025 Coffee shop. Todos los derechos reservados")
