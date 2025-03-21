# DJ5-HelpDesk

Sistema de ticketing para mesa de ayuda basado en Django 5. Altamente configurable y fácil de personalizar para adaptarse a las necesidades específicas de cualquier organización.

## Características

- Sistema completo de gestión de tickets de soporte
- Múltiples niveles organizacionales (UDNs, Sectores)
- Categorización jerárquica de incidencias
- Sistema de permisos granular basado en grupos
- Frontend minimalista utilizando Django Templates y HTMX
- Containerizado con Docker para fácil despliegue
- Soporte para múltiples mensajes por ticket
- Adjuntos de archivos en los mensajes
- Integración con Vite para el frontend

## Tecnologías

- Django 5
- PostgreSQL
- HTMX
- Vite
- Tailwind CSS
- Docker & Docker Compose
- Gunicorn
- Nginx

## Estructura del modelo de datos

El sistema ofrece una estructura robusta y flexible:

- **UDN**: Unidades de Negocio (sucursales, departamentos, etc.)
- **Sector**: Áreas dentro de cada unidad, vinculadas a UDNs
- **IssueCategory**: Categorías de problemas, vinculadas a sectores
- **Issue**: Tipos específicos de problemas dentro de cada categoría
- **Ticket**: Registro principal de incidencias, vinculado a UDN, Sector, Categoría e Issue
- **Message**: Mensajes relacionados con cada ticket, con seguimiento de estado
- **Attachment**: Archivos adjuntos a los mensajes

Cada modelo incluye relaciones con grupos de permisos para un control de acceso granular.

## Sistema de tickets y mensajes

El sistema soporta:
- Seguimiento completo del ciclo de vida del ticket
- Estados configurables (abierto, solucionado, cerrado, comentado)
- Múltiples mensajes por ticket
- Adjuntos de archivos en cada mensaje
- Registro temporal de reportes y creación

## Entorno de desarrollo

El proyecto utiliza Vite para el desarrollo frontend, configurado para integrarse perfectamente con Django:

```
DJANGO_VITE_DEV_MODE = DEBUG
DJANGO_VITE_ASSETS_PATH = BASE_DIR / 'assets'
DJANGO_VITE_DEV_SERVER_PORT = 3000
```

## Instalación y despliegue

### Requisitos
- Docker y Docker Compose

### Pasos para instalación

1. Clone el repositorio:
   ```bash
   git clone https://github.com/kodexArg/dj5-helpdesk.git
   cd dj5-helpdesk
   ```

2. Configure las variables de entorno (o utilice las predeterminadas):
   ```bash
   cp .env.example .env
   ```

3. Inicie los servicios con Docker Compose:
   ```bash
   docker-compose up -d
   ```

El sistema estará disponible en http://localhost:8080

## Configuración

El sistema utiliza un archivo `.env` para la configuración principal:
- Credenciales de base de datos
- Configuración de Debug
- Hosts permitidos
- Configuración regional

## Personalización

El sistema puede adaptarse completamente a cualquier estructura organizativa modificando los modelos UDN, Sector, IssueCategory e Issue.

## Estructura del proyecto

```
dj5-helpdesk/
├── core/               # Aplicación principal
│   ├── components/     # Componentes de Django
│   ├── models.py       # Modelos de datos
│   ├── static/         # Archivos estáticos
│   └── templates/      # Plantillas HTML
├── project/            # Configuración del proyecto
│   ├── settings.py     # Configuración de Django
│   └── urls.py         # Rutas URL
├── configs/            # Archivos de configuración
├── assets/             # Archivos generados por Vite
├── docker-compose.yaml # Configuración de Docker
├── Dockerfile          # Definición de imagen Docker
├── requirements.txt    # Dependencias de Python
└── vite.config.mjs     # Configuración de Vite
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, siga los siguientes pasos:

1. Haga un fork del repositorio
2. Cree una rama para su funcionalidad (`git checkout -b feature/amazing-feature`)
3. Confirme sus cambios (`git commit -m 'Añadir funcionalidad increíble'`)
4. Empuje la rama (`git push origin feature/amazing-feature`)
5. Abra un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - vea el archivo LICENSE.md para más detalles.
