# Inicialización de la Base de Datos

El archivo `initialize-db.yaml` es utilizado por el sistema para crear automáticamente las opciones por defecto durante el arranque inicial o la actualización del sistema. Este enfoque permite configurar rápidamente todas las opciones necesarias para el funcionamiento del sistema de helpdesk, sin necesidad de ingresarlas manualmente a través del panel de administración.

## Acerca del ejemplo incluido

El archivo de ejemplo proporcionado está basado en un caso real de dos estaciones de servicio pertenecientes a un mismo grupo empresarial: "Km 1151" y "Las Bóvedas". Estas estaciones utilizan el sistema de gestión DEBO y están afiliadas a la red de YPF Argentina.

Los datos incluidos representan:

* **UDNs**: Unidades de Negocio definidas (las dos estaciones mencionadas)
* **Sectores**: Áreas funcionales dentro de cada estación (Full, Playa, Administración, Parador)
* **Categorías de Incidencias**: Agrupaciones de tipos de problemas comunes (Sistema Debo, Sistema YPF, Solicitudes IT, etc.)
* **Tipos de Incidencias**: Problemas específicos que pueden ser reportados (Facturación, Despacho, Clover, etc.)

## Limitaciones importantes

**Nota**: Los nombres de las tablas/modelos del sistema (UDNs, Sectors, IssueCategories, IssueTypes) **no pueden ser modificados**. Solo es posible personalizar las opciones dentro de estos modelos.

Además, la relación entre `IssueType` e `IssueCategory` es de "muchos a uno", lo que significa que:
- Cada tipo de incidencia (IssueType) **solo puede pertenecer a una categoría** (IssueCategory)
- Una categoría puede contener múltiples tipos de incidencia
- No es posible asignar múltiples categorías a un mismo tipo de incidencia

## Personalización

Este archivo es solo un ejemplo y está diseñado para ser personalizado según las necesidades específicas de su organización. Reemplazarlo con sus propios datos antes de inicializar el sistema le ahorrará tiempo considerable en la configuración posterior.

Para personalizar el sistema para su organización:

1. Cree una copia del archivo `initialize-db.yaml`
2. Modifique las secciones para reflejar su estructura organizacional
3. Adapte las categorías y tipos de incidencias a los sistemas que utiliza su empresa
4. Asegúrese de mantener la estructura del archivo YAML

## Estructura del archivo YAML

El archivo sigue una estructura jerárquica con campos correspondientes a los modelos en el sistema:

```yaml
UDNs:
  - name: "Nombre de UDN 1"
  - name: "Nombre de UDN 2"
  # ...

Sectors:
  - name: "Nombre del Sector"
    udns:
      - "UDN relacionada 1"
      - "UDN relacionada 2"
  # ...

IssueCategories:
  - name: "Nombre de Categoría"
    sectors:
      - "Sector relacionado 1"
      - "Sector relacionado 2"
  # ...

IssueTypes:
  - name: "Nombre del Tipo de Incidencia"
    issue_category: "Categoría relacionada"  # Solo una categoría por tipo
    description: "Descripción detallada del tipo de incidencia"
  # ...
```

## Formatos de archivo disponibles

El sistema admite múltiples formatos para el archivo de inicialización:

* **YAML** (`initialize-db.yaml`): El formato principal y recomendado por su legibilidad
* **TOML** (`initialize-db.toml`): Alternativa que algunos usuarios pueden preferir
* **JSON** (`initialize-db.json`): Útil para integraciones con otros sistemas

## Recomendaciones

* Mantenga descripciones claras y específicas para cada tipo de incidencia
* Considere los flujos de trabajo de su organización al definir categorías
* Asegúrese de que las relaciones entre UDNs, sectores y categorías reflejen su estructura organizacional real
* Si necesita clasificar un tipo de problema en múltiples categorías, cree tipos de incidencia separados con nombres similares pero asignados a diferentes categorías
* Utilice descripciones que guíen al usuario sobre qué información incluir al reportar un problema
