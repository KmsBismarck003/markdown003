# Arquitectura del proyecto

## Objetivo

La aplicación está pensada para importar Markdown desde la máquina local, visualizarlo antes de convertirlo y generar informes en Word compatibles con Microsoft Office.

## Capas

### Presentation Layer
- Interfaz React + TypeScript con Vite
- Importación de archivos y carpetas
- Vista previa de Markdown en formato renderizado y fuente
- Configuración de salida y resultados

### Application Layer
- API FastAPI con endpoints de salud, importación y conversión
- Validación del contenido de entrada
- Orquestación de las conversiones
- Generación y entrega de archivos DOCX

### Domain Layer
- Entidades básicas del documento y la configuración
- Reglas de conversión por modo (individual, consolidado, agrupado)
- Validación de requisitos para cada documento

### Infrastructure Layer
- Lectura local de archivos Markdown
- Escritura de documentos DOCX en la carpeta local de salida
- Manejo seguro de rutas y nombres de archivos

## Flujo principal

1. El usuario importa archivos o una carpeta.
2. El frontend almacena el contenido Markdown y muestra la vista previa.
3. Se selecciona una modalidad de salida.
4. La API recibe la configuración y genera el documento Word.
5. El usuario descarga el resultado o lo guarda en una carpeta local.

## Consideraciones

- Todo el procesamiento ocurre localmente.
- El sistema no requiere autenticación ni servicios externos.
- El backend atiende solo en localhost.
- La salida se mantiene en una carpeta controlada del proyecto y se entrega al usuario para descarga segura.
