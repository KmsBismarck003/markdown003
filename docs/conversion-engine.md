# Documentación del motor de conversión

## Objetivo

Transformar Markdown a documentos DOCX sin perder la intención estructural del original.

## Elementos soportados

- encabezados H1 a H6
- párrafos normales
- listas ordenadas y sin ordenar
- citas
- tablas básicas
- bloques de código
- código en línea
- enlaces
- imágenes con referencia local
- delimitadores horizontales
- texto en negrita, cursiva y tachado

## Proceso

1. El contenido Markdown se recibe desde el frontend.
2. El servicio de conversión analiza líneas y patrones relevantes.
3. Se construye un documento Word con estilos básicos y jerarquías.
4. Se guarda el archivo final en la carpeta de salida local.

## Limitaciones conocidas

- El soporte visual de imágenes depende de rutas accesibles en el sistema local.
- Tablas complejas con decoraciones avanzadas pueden necesitar ajustes manuales.
- La conversión está optimizada para reportes técnicos y documentos de texto con estructura clara.
