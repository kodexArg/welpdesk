# DJ5-HelpDesk

Sistema de ticketing para mesa de ayuda basado en Django 5. Altamente configurable y fácil de personalizar para adaptarse a las necesidades específicas de cualquier organización.

⚠️ **Proyecto en construcción** ⚠️

## Características

- Sistema completo de gestión de tickets de soporte
- Múltiples niveles organizacionales (UDNs, Sectores)
- Categorización jerárquica de incidencias
- Sistema de permisos granular basado en grupos
- Frontend minimalista utilizando Django Templates y HTMX (sin JavaScript adicional)
- Containerizado con Docker para fácil despliegue

## Tecnologías

- Django 5
- PostgreSQL
- HTMX
- Docker & Docker Compose
- Gunicorn
- Nginx

## Configuración y personalización

El sistema es genérico y puede adaptarse a cualquier estructura organizacional. Los modelos principales incluyen:

- **UDN**: Unidades de Negocio (sucursales, departamentos, etc.)
- **Sector**: Áreas dentro de cada unidad
- **IssueCategory**: Categorías de problemas
- **IssueType**: Tipos específicos de problemas dentro de cada categoría

### Datos de ejemplo

El proyecto incluye un archivo `initialize-db.yaml` que contiene datos de ejemplo para poblar los modelos iniciales. Este archivo es completamente personalizable y puede adaptarse a la estructura de su organización.

Para más información sobre cómo personalizar este archivo, consulte la documentación en `configs/initialize-db/initialize-db.md`.

## Instalación en servidor

Asumiendo que ya tiene Docker y Docker Compose instalados:

1. Clone el repositorio:
   ```bash
   git clone https://github.com/kodexArg/dj5-helpdesk.git
   cd dj5-helpdesk
