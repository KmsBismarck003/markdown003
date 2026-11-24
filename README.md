# Markdown to Word local converter

Aplicación web local para importar archivos Markdown, revisarlos en una vista previa y convertirlos a documentos Microsoft Word (.docx) sin depender de servicios externos.

## Características principales

- Importación de archivos `.md` y carpetas completas
- Vista previa renderizada y fuente original del Markdown
- Conversión individual, consolidada y agrupada por carpetas
- Generación local de documentos Word con formato profesional
- Descarga individual o en lote mediante acceso directo al navegador
- Arquitectura modular basada en capas para facilidad de mantenimiento

## Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + Pydantic
- Document processing: python-docx
- Markdown parsing: markdown-it-py (integrado con apoyo visual en el frontend)

## Estructura del proyecto

- `frontend/` – interfaz de usuario web
- `backend/` – API local y lógica de conversión
- `docs/` – documentación del proyecto
- `scripts/` – scripts de ejecución y empaquetado

## Requisitos

- Python 3.11+
- Node.js 18+
- npm
- Windows 10/11 recomendado

## Instalación

1. Clona o descarga el proyecto.
2. Abre una terminal en la raíz del proyecto.
3. Instala las dependencias del frontend:

```powershell
cd frontend
npm install
```

4. Instala las dependencias del backend:

```powershell
cd ..\backend
python -m pip install -r requirements.txt
```

## Ejecución local

### Opción manual

Backend:

```powershell
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

Frontend:

```powershell
cd frontend
npm run dev -- --host 0.0.0.0
```

Después, abre:

- http://localhost:5173
- API en http://127.0.0.1:8001/api/health

### Opción con script de Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

## Proceso de conversión

1. Importa archivos Markdown o carpetas.
2. Revisa la vista previa.
3. Elige la modalidad de salida.
4. Configura el nombre del documento y la portada/opciones visuales.
5. Ejecuta la conversión.
6. Descarga el documento generado o guarda el archivo en una carpeta seleccionada.

## Validación

```powershell
cd frontend
npm run build
cd ..\backend
pytest -q
```

## Nota de seguridad

La conversión se realiza localmente en la máquina del usuario; no se envían archivos a servicios externos. La API está vinculada a localhost y se validan rutas de salida para evitar accesos no autorizados.
