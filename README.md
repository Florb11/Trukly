<div align="center">

# 🚛 Trukly

### Sistema de gestión de flota de camiones

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-MariaDB-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)

</div>

---

## 📋 Descripción

**Trukly** es una aplicación web para la gestión de flotas de camiones. Permite administrar viajes, choferes, mecánicos, operadores logísticos y el seguimiento de reportes de falla, todo desde una interfaz moderna con dashboards y roles diferenciados por tipo de usuario.

El sistema sigue una arquitectura **MVC (Modelo - Vista - Controlador)** con una **API REST** desarrollada en Flask que se comunica con el frontend en React mediante JSON.

---

## 🧱 Tecnologías utilizadas

| Capa | Tecnología |
|------|-----------|
| Frontend | React 19, React Router 7, Bootstrap 5 |
| Build tool | Vite 8 |
| Backend | Python, Flask 3.1 |
| ORM | SQLAlchemy 2.0 + Flask-SQLAlchemy |
| Base de datos | MySQL / MariaDB |
| Autenticación | JWT (Flask-JWT-Extended + PyJWT) |
| Hash de contraseñas | bcrypt (Flask-Bcrypt) |
| Variables de entorno | python-dotenv |

---

## 📁 Estructura general del proyecto

```
trukly/
├── backend/                        # API REST — arquitectura MVC
│   ├── app.py                      # Punto de entrada
│   ├── db_instance.py              # Singleton de SQLAlchemy
│   ├── database/                   # Script SQL
│   ├── models/                     # (M) Modelos — tablas de la BD
│   ├── controllers/                # (C) Controladores — coordinan, validan y delegan
│   ├── routes/                     # Blueprints — conectan endpoints con métodos de los controladores
│   ├── src/                        # Clases de dominio — acá vive la lógica de negocio
│   │   └── observer/               # Patrón Observer (eventos y notificaciones)
│   ├── utils/
│   │   ├── auth_decorators.py      # Decoradores de autorización por rol
│   │   ├── input_sanitizer.py      # Sanitizador de inputs
│   │   └── validation_composite.py # Patrón Composite de validaciones
│   └── logs/                       # Logs generados automáticamente
├── frontend/                       # (V) Vista — React
│   └── src/
│       ├── components/
│       ├── pages/                  # Dashboards por rol
│       ├── context/                # Estado global de sesión
│       └── utils/
│           └── fetchConToken.js    # Fetch con JWT 
└── README.md
```

---

## 🏗️ Patrones de diseño aplicados

| Patrón | Ubicación | Descripción |
|--------|-----------|-------------|
| **Singleton** | `db_instance.py` | Una única instancia de SQLAlchemy compartida en toda la app |
| **Composite** | `utils/validation_composite.py` | Validaciones anidadas y combinables (`ValidadorCompuesto`, `CampoObligatorio`, `ValorPermitido`, `ValidacionCondicional`, etc.) |
| **Observer** | `notificacion_routes` / `NotificacionesPage` | Las acciones del sistema generan notificaciones automáticas para los usuarios correspondientes |
| **MVC** | Estructura general | Separación clara entre modelos, controladores y vistas |

---

## 🔒 Seguridad

- **JWT** con expiración de 60 minutos. Al vencer, el frontend elimina el token y redirige al login automáticamente.
- **Decoradores de autorización por rol** en Flask (`@admin_required`, `@chofer_required`, `@operador_required`, `@mecanico_required`, `@usuario_required`, `@roles_required`). Cada endpoint protegido verifica que el token sea válido, que el usuario esté activo y que el rol del token coincida con el rol en la base de datos.
- **Sanitización de inputs** con `InputSanitizer`: limpieza de texto, emails, contraseñas, enteros y decimales antes de cualquier procesamiento. Usa `html.escape` para prevenir XSS.
- **Validación de contraseñas**: se aplican validacion al registrar o cambiar la contraseña.
- **Rutas protegidas en el frontend** con `ProtectedRoute`: si el usuario no tiene sesión o intenta acceder a una sección sin permiso, es redirigido automáticamente. Las páginas no encontradas y los accesos no autorizados tienen páginas dedicadas (`NotFoundPage`, `NoAutorizadoPage`).
- **CORS** configurado con Flask-CORS.

---

## 🗂️ Blueprints (rutas de la API)

Las rutas están organizadas en Blueprints de Flask, uno por módulo:

| Blueprint | Prefijo |
|-----------|---------|
| `auth_routes` | `/api/auth` |
| `administrador_routes` | `/api/administrador`, `/api/admin` |
| `chofer_routes` | `/api/chofer` |
| `operador_routes` | `/api/operador` |
| `mecanico_routes` | `/api/mecanico` |
| `camion_routes` | `/api/camion` |
| `viaje_routes` | `/api/viaje` |
| `reporte_routes` | `/api/reporte` |
| `perfil_routes` | `/api/perfil` |
| `notificacion_routes` | `/api/notificacion` |
| `registro_ingreso_salida_routes` | `/api/registro` |

---

## ⚙️ Instalación y configuración

### Requisitos previos

- Python 3.11 o superior
- Node.js 18 o superior
- MySQL 8 o MariaDB 10.4

---

### 🗄️ 1. Base de datos

Importá el script que está dentro de `backend/database/`:

```bash
mysql -u root -p < backend/database/Script.sql
```

> Esto crea la base de datos, las tablas y carga los datos de prueba automáticamente.

---

### 🐍 2. Backend (Flask)

```bash
# Entrar a la carpeta del backend
cd backend

# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar dependencias (se instalan todas automáticamente)
pip install -r requirements.txt

# Configurar las variables de entorno
# Crear un archivo .env con el siguiente contenido:
```

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=trukly
DB_PORT=3306
SECRET_KEY=clave_secreta_aqui
```

```bash
# Iniciar el servidor
python app.py
```

El backend queda corriendo en: `http://localhost:5000`

---

### ⚛️ 3. Frontend (React)

```bash
# Entrar a la carpeta del frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar la aplicación
npm run dev
```

El frontend queda corriendo en: `http://localhost:5173`

---

## 👥 Usuarios de prueba

> Todos los usuarios comparten la misma contraseña: **`12345678a`**

| Usuario | Rol |
|---------|-----|
| `admin1` | Administrador |
| `chofer1` | Chofer |
| `Operador1` | Operador Logístico |
| `Mecanico1` | Mecánico |

---

## 🔐 Roles del sistema

| Rol | Permisos principales |
|-----|---------------------|
| **Administrador** | Gestión total del sistema, usuarios, camiones, viajes, reportes y estadísticas |
| **Operador Logístico** | Crear y gestionar viajes, asignar choferes y camiones, ver reportes y estadísticas |
| **Chofer** | Ver sus viajes asignados, reportar fallas, ver sus estadísticas |
| **Mecánico** | Ver y gestionar reportes de falla asignados, registrar reparaciones |

Cada rol tiene su propio dashboard con las secciones correspondientes. Todos los usuarios pueden editar su perfil y ver sus notificaciones.

---

## 🚚 Datos de prueba incluidos

- **6 camiones** (4 disponibles, 2 en mantenimiento)
- **4 viajes** (pendientes, finalizado y cancelado)
- **2 reportes de falla** (pendiente y en revisión)
- **3 notificaciones**

---

<div align="center">
  <sub>Desarrollado por Juan Del Pozo y Florencia Bergman— Trukly </sub>
</div>