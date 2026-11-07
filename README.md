# TrafficPredict UIS

Aplicación académica en Python + Streamlit para analizar aforos vehiculares de la Carrera 27 de Bucaramanga, sentido sur–norte.

## Ejecutar localmente en Windows

Requisitos: Python 3.10 o superior y Visual Studio Code (opcional, recomendado).

1. Descomprime el proyecto y abre la carpeta `TrafficPredict_UIS` en VS Code.
2. Abre **Terminal → New Terminal**.
3. Ejecuta:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`.

## Publicar en GitHub y obtener un enlace público

### 1. Crear el repositorio
1. Entra a [GitHub](https://github.com/) e inicia sesión.
2. Pulsa **New repository** y escribe `TrafficPredict-UIS`.
3. Para facilitar la publicación gratuita en Streamlit Community Cloud, puedes dejarlo **Public**.
4. Crea el repositorio sin agregar README ni `.gitignore`; este proyecto ya los incluye.

### 2. Subir el proyecto desde VS Code
Abre la terminal en la carpeta raíz `TrafficPredict_UIS` y ejecuta, reemplazando `TU-USUARIO` por tu usuario de GitHub:

```bash
git init
git add .
git commit -m "Primera version de TrafficPredict UIS"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TrafficPredict-UIS.git
git push -u origin main
```

Si Git solicita identificación, sigue el inicio de sesión que ofrece VS Code o Git Credential Manager. No compartas contraseñas ni tokens.

### 3. Publicar en Streamlit Community Cloud
1. Entra a [Streamlit Community Cloud](https://share.streamlit.io/).
2. Inicia sesión con GitHub y autoriza la conexión.
3. Selecciona **Create app**.
4. Elige el repositorio `TU-USUARIO/TrafficPredict-UIS`, la rama `main` y el archivo principal `app.py`.
5. Pulsa **Deploy**.

Al terminar, Streamlit asignará el enlace público de la aplicación. Tendrá una forma similar a `https://trafficpredict-uis.streamlit.app`, pero la dirección exacta depende de la disponibilidad del nombre y de la asignación de la plataforma.

### Actualizar la aplicación
Después de modificar y guardar el código, ejecuta:

```bash
git add .
git commit -m "Actualizacion de la aplicacion"
git push
```

Streamlit Community Cloud detectará el cambio en GitHub y volverá a desplegar la aplicación.

## Funcionalidades incluidas

- Consulta de aforos por franja horaria.
- Gráfica del flujo vehicular por intervalos de 15 minutos.
- Interpolación de Lagrange.
- Interpolación de Newton y tabla de diferencias divididas.
- Ajuste por mínimos cuadrados.
- Métricas MAE y RMSE.

## Fuente y alcance de los datos

La base contiene 36 intervalos de 15 minutos de tres franjas horarias de una jornada de medición. Fuente: trabajo de grado de la Universidad Industrial de Santander (2020), disponible en el [repositorio UIS](https://noesis.uis.edu.co/handle/20.500.14071/39901).

**Limitación importante:** los datos corresponden a una jornada de 2020. La aplicación permite el análisis académico e interpolación de esos registros; no representa tráfico en tiempo real ni demuestra por sí sola capacidad de predecir el flujo de otros días.
