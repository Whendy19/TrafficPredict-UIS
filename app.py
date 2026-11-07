import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="TrafficPredict UIS", page_icon="📊", layout="wide")

DATA_PATH = Path(__file__).parent / "datos" / "TrafficPredict_base_aforos_carrera27_sur_norte.csv"

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
    elif DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
    else:
        return None
    df["x_minutos"] = pd.to_datetime(df["hora_inicio"], format="%H:%M").dt.hour * 60 + pd.to_datetime(df["hora_inicio"], format="%H:%M").dt.minute
    return df.sort_values("x_minutos").reset_index(drop=True)

def lagrange_eval(x_nodes, y_nodes, x):
    total = 0.0
    for i in range(len(x_nodes)):
        term = y_nodes[i]
        for j in range(len(x_nodes)):
            if i != j:
                denominator = x_nodes[i] - x_nodes[j]
                if denominator == 0:
                    raise ValueError("Los valores de x deben ser diferentes.")
                term *= (x - x_nodes[j]) / denominator
        total += term
    return total

def newton_coefficients(x_nodes, y_nodes):
    n = len(x_nodes)
    table = np.zeros((n, n), dtype=float)
    table[:, 0] = y_nodes
    for j in range(1, n):
        for i in range(n - j):
            table[i, j] = (table[i + 1, j - 1] - table[i, j - 1]) / (x_nodes[i + j] - x_nodes[i])
    return table[0, :], table

def newton_eval(x_nodes, coefficients, x):
    result = coefficients[0]
    product = 1.0
    for i in range(1, len(coefficients)):
        product *= (x - x_nodes[i - 1])
        result += coefficients[i] * product
    return result

def clock_label(minutes):
    h, m = divmod(int(minutes), 60)
    return f"{h:02d}:{m:02d}"

st.title("TrafficPredict UIS")
st.caption("Análisis del flujo vehicular · Carrera 27 entre Avenida La Rosita y Calle 36 · Sentido sur–norte")

uploaded = st.sidebar.file_uploader("Cargar otra base CSV (opcional)", type=["csv"])
df = load_data(uploaded)

if df is None:
    st.error("No se encontró la base de datos. Coloca el CSV en la carpeta datos o cárgalo desde el menú lateral.")
    st.stop()

st.sidebar.header("Configuración")
periods = {
    "Mañana (06:00–09:00)": (360, 540),
    "Mediodía (11:30–14:30)": (690, 870),
    "Tarde (17:00–20:00)": (1020, 1200),
}
period = st.sidebar.selectbox("Franja horaria", list(periods.keys()))
lo, hi = periods[period]
data = df[(df["x_minutos"] >= lo) & (df["x_minutos"] < hi)].copy()

if data.empty:
    st.warning("No hay datos en la franja seleccionada.")
    st.stop()

# Indicadores
c1, c2, c3 = st.columns(3)
c1.metric("Intervalos disponibles", len(data))
c2.metric("Vehículos registrados", f"{int(data['total_vehiculos'].sum()):,}".replace(",", "."))
max_row = data.loc[data["total_vehiculos"].idxmax()]
c3.metric("Mayor aforo en 15 min", f"{int(max_row['total_vehiculos']):,}".replace(",", "."), max_row["hora_inicio"])

tab_data, tab_interp, tab_fit, tab_about = st.tabs(["Datos", "Interpolación", "Mínimos cuadrados", "Acerca del proyecto"])

with tab_data:
    st.subheader("Registros de aforo")
    display_cols = ["hora_inicio", "hora_fin", "motos", "taxis", "particulares", "busetas", "camiones", "volquetas", "buses", "total_vehiculos"]
    st.dataframe(data[display_cols], use_container_width=True, hide_index=True)
    fig, ax = plt.subplots()
    ax.plot(data["hora_inicio"], data["total_vehiculos"], marker="o")
    ax.set_title("Flujo vehicular por intervalo de 15 minutos")
    ax.set_xlabel("Hora de inicio")
    ax.set_ylabel("Vehículos")
    ax.grid(True, alpha=.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Fuente de los datos: trabajo de grado UIS (2020). Los registros corresponden a una jornada de medición, no a tráfico actual.")

with tab_interp:
    st.subheader("Interpolación polinómica")
    st.write("Selecciona puntos de una misma franja. La variable x representa los minutos transcurridos desde las 00:00 y y representa vehículos por cada 15 minutos.")
    method = st.radio("Método numérico", ["Lagrange", "Newton"], horizontal=True)
    max_nodes = min(6, len(data))
    default_nodes = min(4, max_nodes)
    node_count = st.slider("Cantidad de puntos", min_value=2, max_value=max_nodes, value=default_nodes)
    selected_positions = np.linspace(0, len(data)-1, node_count, dtype=int)
    nodes = data.iloc[selected_positions]
    x_nodes = nodes["x_minutos"].to_numpy(dtype=float)
    y_nodes = nodes["total_vehiculos"].to_numpy(dtype=float)

    st.write("Puntos utilizados:")
    st.dataframe(nodes[["hora_inicio", "total_vehiculos"]].rename(columns={"hora_inicio":"Hora", "total_vehiculos":"Vehículos"}), hide_index=True, use_container_width=True)

    x_min = float(x_nodes.min())
    x_max = float(x_nodes.max())
    query_clock = st.slider("Hora para interpolar", min_value=int(x_min), max_value=int(x_max), value=int((x_min+x_max)/2), step=1, format="%d") 
    x_query = float(query_clock)
    if method == "Lagrange":
        y_query = lagrange_eval(x_nodes, y_nodes, x_query)
        st.latex(r"P(x)=\sum_{i=0}^{n} y_i\prod_{j\\ne i}\frac{x-x_j}{x_i-x_j}")
    else:
        coeffs, table = newton_coefficients(x_nodes, y_nodes)
        y_query = newton_eval(x_nodes, coeffs, x_query)
        st.latex(r"P(x)=a_0+a_1(x-x_0)+a_2(x-x_0)(x-x_1)+\cdots")
        st.write("Tabla de diferencias divididas:")
        st.dataframe(pd.DataFrame(table), use_container_width=True)
        st.write("Coeficientes de Newton:", np.round(coeffs, 6))

    m1, m2 = st.columns(2)
    m1.metric("Hora consultada", clock_label(query_clock))
    m2.metric("Valor interpolado", f"{y_query:,.2f} vehículos".replace(",", "."))
    if y_query < 0:
        st.warning("El polinomio produce un valor negativo. Esto muestra una limitación del modelo; no debe interpretarse como un conteo físico.")
    st.caption("La interpolación estima valores entre los puntos seleccionados. No constituye por sí sola una predicción del tráfico futuro.")

    x_curve = np.linspace(x_min, x_max, 250)
    if method == "Lagrange":
        y_curve = [lagrange_eval(x_nodes, y_nodes, xx) for xx in x_curve]
    else:
        y_curve = [newton_eval(x_nodes, coeffs, xx) for xx in x_curve]
    fig, ax = plt.subplots()
    ax.scatter(x_nodes, y_nodes, label="Puntos seleccionados")
    ax.plot(x_curve, y_curve, label=f"Polinomio de {method}")
    ax.scatter([x_query], [y_query], marker="x", s=80, label="Consulta")
    ax.set_xlabel("Minutos desde las 00:00")
    ax.set_ylabel("Vehículos por 15 minutos")
    ax.set_title(f"Interpolación por {method}")
    ax.grid(True, alpha=.3)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)

with tab_fit:
    st.subheader("Ajuste por mínimos cuadrados")
    st.write("Este ajuste aproxima la tendencia de los datos; no interpola necesariamente cada punto.")
    degree = st.selectbox("Grado del polinomio de ajuste", [1, 2, 3], index=1)
    x = data["x_minutos"].to_numpy(dtype=float)
    y = data["total_vehiculos"].to_numpy(dtype=float)
    coeff = np.polyfit(x, y, degree)
    pred = np.polyval(coeff, x)
    mae = np.mean(np.abs(y-pred))
    rmse = np.sqrt(np.mean((y-pred)**2))
    a, b, c = st.columns(3)
    a.metric("MAE", f"{mae:.2f} vehículos")
    b.metric("RMSE", f"{rmse:.2f} vehículos")
    c.metric("Grado", degree)
    st.write("Coeficientes (de mayor a menor potencia):")
    st.code(np.array2string(coeff, precision=6))
    fig, ax = plt.subplots()
    ax.scatter(x, y, label="Datos observados")
    xx = np.linspace(x.min(), x.max(), 250)
    ax.plot(xx, np.polyval(coeff, xx), label="Ajuste por mínimos cuadrados")
    ax.set_xlabel("Minutos desde las 00:00")
    ax.set_ylabel("Vehículos por 15 minutos")
    ax.set_title("Ajuste polinómico")
    ax.grid(True, alpha=.3)
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("MAE y RMSE se calculan sobre los mismos datos usados para ajustar el polinomio; son errores de ajuste, no una validación independiente.")

with tab_about:
    st.subheader("Objetivo")
    st.write("Desarrollar una herramienta académica para analizar el flujo vehicular de un tramo de la Carrera 27 de Bucaramanga mediante interpolación de Lagrange, Newton y ajuste por mínimos cuadrados.")
    st.markdown("""
    **Fuente:** Marino Hernández, P. A. y Rodríguez Silva, E. F. (2020), trabajo de grado, Universidad Industrial de Santander.

    **Alcance de la base:** 36 intervalos de 15 minutos correspondientes a tres franjas horarias de una jornada de medición. No representa un monitoreo en tiempo real.
    """)
    st.markdown("[Consultar el documento en el repositorio UIS](https://noesis.uis.edu.co/handle/20.500.14071/39901)")
    st.info("Para hacer predicciones aplicables a otros días será necesario incorporar aforos de varias jornadas y separar datos de entrenamiento y validación.")
