import { type ChangeEvent, type DragEvent, useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import './App.css'

type ConversionMode = 'individual' | 'consolidated' | 'grouped'
type PreviewTab = 'rendered' | 'source' | 'editor'

type ImportedFile = {
  id: string
  name: string
  relativePath: string
  size: number
  content: string
}

type ConversionResult = {
  name: string
  download_url: string
}

function formatBytes(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

// Crisp Minimal SVG Icons (No Emojis)
function IconDownload({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  )
}

function IconFolder({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
    </svg>
  )
}

function IconFileText({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
      <line x1="16" y1="13" x2="8" y2="13" />
      <line x1="16" y1="17" x2="8" y2="17" />
      <polyline points="10 9 9 9 8 9" />
    </svg>
  )
}

function IconUpload({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  )
}

function IconCheck({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

function IconClose({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  )
}

function IconTrash({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="3 6 5 6 21 6" />
      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
    </svg>
  )
}

function IconCopy({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  )
}

function IconSettings({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  )
}

function IconConvert({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="16 3 21 3 21 8" />
      <line x1="4" y1="20" x2="21" y2="3" />
      <polyline points="21 16 21 21 16 21" />
      <line x1="15" y1="15" x2="21" y2="21" />
      <line x1="4" y1="4" x2="9" y2="9" />
    </svg>
  )
}

function IconLayers({ className = 'icon' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 2 7 12 12 22 7 12 2" />
      <polyline points="2 17 12 22 22 17" />
      <polyline points="2 12 12 17 22 12" />
    </svg>
  )
}

function App() {
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const folderInputRef = useRef<HTMLInputElement | null>(null)
  const resultsRef = useRef<HTMLDivElement | null>(null)
  const savedDirectoryHandleRef = useRef<FileSystemDirectoryHandle | null>(null)

  const [files, setFiles] = useState<ImportedFile[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [editorMarkdown, setEditorMarkdown] = useState('# Pega aquí tu Markdown\n\n- prueba\n- tabla\n\n| Columna | Valor |\n| --- | --- |\n| A | 1 |')
  const [mode, setMode] = useState<ConversionMode>('consolidated')
  const [documentName, setDocumentName] = useState('reporte-convertido')
  const [includeCover, setIncludeCover] = useState(true)
  const [includeToc, setIncludeToc] = useState(false)
  const [pageBreaks, setPageBreaks] = useState(true)
  const [autoDownload, setAutoDownload] = useState(true)
  const [outputDirectory, setOutputDirectory] = useState('Carpeta local de salida')
  const [results, setResults] = useState<ConversionResult[]>([])
  const [previewTab, setPreviewTab] = useState<PreviewTab>('rendered')
  const [dragging, setDragging] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)

  const selectedFile = files.find((file) => file.id === selectedId) ?? files[0] ?? null

  useEffect(() => {
    if (selectedFile) {
      setEditorMarkdown(selectedFile.content)
    }
  }, [selectedFile])

  const currentMarkdown = selectedFile ? selectedFile.content : editorMarkdown

  const importFiles = async (fileList: FileList | File[]) => {
    const newItems: ImportedFile[] = []

    for (const file of Array.from(fileList)) {
      const lowerName = file.name.toLowerCase()
      if (!lowerName.endsWith('.md') && !lowerName.endsWith('.markdown')) continue

      const content = await file.text()
      const relativePath = (file as File & { webkitRelativePath?: string }).webkitRelativePath || file.name
      newItems.push({
        id: `${file.name}-${relativePath}-${file.size}-${Math.random().toString(36).slice(2)}`,
        name: file.name,
        relativePath,
        size: file.size,
        content,
      })
    }

    setFiles((current) => {
      const combined = new Map(current.map((item) => [item.id, item]))
      for (const item of newItems) combined.set(item.id, item)
      const next = Array.from(combined.values())
      if (next.length > 0) setSelectedId(next[0].id)
      return next
    })
    setError(null)
  }

  const handleInputFiles = async (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      await importFiles(event.target.files)
      event.target.value = ''
    }
  }

  const handleFolderFiles = async (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      await importFiles(event.target.files)
      event.target.value = ''
    }
  }

  const handleDrop = async (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragging(false)
    const fileList = event.dataTransfer.files
    if (fileList.length > 0) {
      await importFiles(fileList)
    }
  }

  const downloadResult = async (url: string, filename: string) => {
    try {
      const res = await fetch(url)
      if (!res.ok) throw new Error('Error al descargar el archivo')
      const blob = await res.blob()
      const blobUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
      setTimeout(() => URL.revokeObjectURL(blobUrl), 1000)
    } catch {
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      a.remove()
    }
  }

  const handleConvert = async () => {
    const payloadFiles = files.length
      ? files.map((file) => ({
          name: file.name,
          relative_path: file.relativePath,
          content: file.content,
          size: file.size,
        }))
      : editorMarkdown.trim()
        ? [{
            name: `${(documentName || 'markdown').trim() || 'markdown'}.md`,
            relative_path: `${(documentName || 'markdown').trim() || 'markdown'}.md`,
            content: editorMarkdown,
            size: editorMarkdown.length,
          }]
        : []

    if (payloadFiles.length === 0) {
      setError('Pega Markdown en el editor o importa al menos un archivo para convertir.')
      return
    }

    setProcessing(true)
    setError(null)
    setSuccessMessage(null)

    try {
      const response = await fetch('/api/convert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          files: payloadFiles,
          mode,
          document_name: documentName,
          include_cover: includeCover,
          include_toc: includeToc,
          page_breaks: pageBreaks,
        }),
      })

      const data = await response.json()
      if (!response.ok) {
        throw new Error(data.detail || 'La conversión falló.')
      }

      const generatedResults: ConversionResult[] = data.results || []
      setResults(generatedResults)

      const count = generatedResults.length
      setSuccessMessage(`Conversión finalizada con éxito. Se generaron ${count} documento(s).`)

      if (autoDownload && generatedResults.length > 0) {
        const zipResult = generatedResults.find((r) => r.name.endsWith('.zip'))
        const target = zipResult || generatedResults[0]
        await downloadResult(target.download_url, target.name)
      }

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 150)
    } catch (conversionError) {
      setError(
        conversionError instanceof Error
          ? conversionError.message
          : 'No se pudo completar la conversión.',
      )
    } finally {
      setProcessing(false)
    }
  }

  const clearSelection = () => {
    setFiles([])
    setSelectedId(null)
    setResults([])
    setError(null)
    setSuccessMessage(null)
  }

  const removeFile = (fileId: string) => {
    const nextFiles = files.filter((item) => item.id !== fileId)
    setFiles(nextFiles)
    if (selectedId === fileId) {
      setSelectedId(nextFiles[0]?.id ?? null)
    }
  }

  const copyMarkdown = async () => {
    try {
      await navigator.clipboard.writeText(currentMarkdown)
      setSuccessMessage('Contenido copiado al portapapeles.')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch {
      setError('No se pudo copiar el contenido al portapapeles.')
    }
  }

  const downloadMarkdown = () => {
    const blob = new Blob([currentMarkdown], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `${(documentName || 'markdown').trim() || 'markdown'}.md`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  const selectOutputFolder = async () => {
    if (!('showDirectoryPicker' in window)) {
      setOutputDirectory('Sin selector de directorio nativo en este navegador.')
      return
    }

    try {
      const handle = await (window as typeof window & { showDirectoryPicker: () => Promise<FileSystemDirectoryHandle> }).showDirectoryPicker()
      savedDirectoryHandleRef.current = handle
      setOutputDirectory(handle.name)
    } catch {
      setOutputDirectory('Selección cancelada')
    }
  }

  const saveResultToFolder = async (result: ConversionResult) => {
    let handle = savedDirectoryHandleRef.current
    if (!handle) {
      if (!('showDirectoryPicker' in window)) {
        await downloadResult(result.download_url, result.name)
        return
      }
      try {
        handle = await (window as typeof window & { showDirectoryPicker: () => Promise<FileSystemDirectoryHandle> }).showDirectoryPicker()
        savedDirectoryHandleRef.current = handle
        setOutputDirectory(handle.name)
      } catch {
        await downloadResult(result.download_url, result.name)
        return
      }
    }

    try {
      const fileHandle = await handle.getFileHandle(result.name, { create: true })
      const writable = await fileHandle.createWritable()
      const fileResponse = await fetch(result.download_url)
      const blob = await fileResponse.blob()
      await writable.write(blob)
      await writable.close()
      setSuccessMessage(`Documento guardado en carpeta: ${handle.name}/${result.name}`)
    } catch {
      await downloadResult(result.download_url, result.name)
    }
  }

  return (
    <div className="bento-app">
      {/* Top Header Navigation */}
      <header className="bento-header">
        <div className="header-brand">
          <div className="brand-badge">
            <span className="brand-dot" />
            <span>LOCAL ENGINE</span>
          </div>
          <div className="brand-titles">
            <h1>Markdown to Word</h1>
            <p className="brand-subtitle">Conversión profesional y privada a documentos .docx</p>
          </div>
        </div>

        <div className="header-actions">
          <button
            className="bento-btn bento-btn-primary convert-btn"
            type="button"
            onClick={handleConvert}
            disabled={processing || (!files.length && !editorMarkdown.trim())}
          >
            <IconConvert className="btn-icon" />
            <span>{processing ? 'Generando documento...' : 'Convertir a Word'}</span>
          </button>
        </div>
      </header>

      {/* Status Notifications */}
      {successMessage && (
        <div className="bento-banner banner-success">
          <div className="banner-body">
            <span className="banner-icon-badge">
              <IconCheck className="icon-sm" />
            </span>
            <span className="banner-text">{successMessage}</span>
          </div>
          <div className="banner-actions">
            {results.length > 0 && (
              <button
                type="button"
                className="banner-cta-btn"
                onClick={() => {
                  const zipResult = results.find((r) => r.name.endsWith('.zip'))
                  const primary = zipResult || results[0]
                  downloadResult(primary.download_url, primary.name)
                }}
              >
                <IconDownload className="icon-xs" />
                <span>Descargar {results.find((r) => r.name.endsWith('.zip')) ? 'paquete ZIP' : results[0]?.name}</span>
              </button>
            )}
            <button
              type="button"
              className="banner-close-btn"
              onClick={() => setSuccessMessage(null)}
              aria-label="Cerrar notificación"
            >
              <IconClose className="icon-xs" />
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="bento-banner banner-error">
          <div className="banner-body">
            <span className="banner-icon-badge error">
              <IconClose className="icon-sm" />
            </span>
            <span className="banner-text">{error}</span>
          </div>
          <button
            type="button"
            className="banner-close-btn"
            onClick={() => setError(null)}
            aria-label="Cerrar error"
          >
            <IconClose className="icon-xs" />
          </button>
        </div>
      )}

      {/* Main Bento Grid */}
      <main className="bento-grid">
        {/* Bento Tile 1: File Manager */}
        <section className="bento-tile tile-files">
          <div className="tile-header">
            <div className="tile-title-group">
              <IconFileText className="tile-icon" />
              <h2>Archivos</h2>
              <span className="tile-counter">{files.length}</span>
            </div>
            <div className="tile-actions">
              <button
                type="button"
                className="bento-btn bento-btn-subtle"
                onClick={() => fileInputRef.current?.click()}
                title="Cargar archivos Markdown sueltos"
              >
                <IconUpload className="btn-icon-xs" />
                <span>Archivo</span>
              </button>
              <button
                type="button"
                className="bento-btn bento-btn-subtle"
                onClick={() => folderInputRef.current?.click()}
                title="Cargar una carpeta completa con Markdown"
              >
                <IconFolder className="btn-icon-xs" />
                <span>Carpeta</span>
              </button>
              {files.length > 0 && (
                <button
                  type="button"
                  className="bento-btn bento-btn-ghost danger"
                  onClick={clearSelection}
                  title="Limpiar todos los archivos"
                >
                  <IconTrash className="btn-icon-xs" />
                </button>
              )}
            </div>
          </div>

          <div
            className={`bento-dropzone ${dragging ? 'drag-active' : ''}`}
            onDragOver={(event) => {
              event.preventDefault()
              setDragging(true)
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={handleDrop}
          >
            <IconUpload className="dropzone-icon" />
            <p className="dropzone-title">Arrastra archivos Markdown aquí</p>
            <span className="dropzone-hint">Soporta carpetas y lotes múltiples (.md)</span>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept=".md,.markdown"
            multiple
            hidden
            onChange={handleInputFiles}
          />
          <input
            ref={folderInputRef}
            type="file"
            multiple
            hidden
            {...({ webkitdirectory: '', directory: '' } as Record<string, string>)}
            onChange={handleFolderFiles}
          />

          <div className="bento-scroll-container file-list-scroll">
            {files.length === 0 ? (
              <div className="bento-empty-state">
                <p>No hay archivos importados.</p>
                <small>Puedes redactar en tiempo real en la pestaña Editor.</small>
              </div>
            ) : (
              <div className="file-items-stack">
                {files.map((file) => (
                  <div
                    key={file.id}
                    className={`file-item-card ${file.id === selectedId ? 'is-selected' : ''}`}
                    onClick={() => setSelectedId(file.id)}
                  >
                    <div className="file-info">
                      <strong className="file-name" title={file.name}>{file.name}</strong>
                      <span className="file-subinfo">{file.relativePath} • {formatBytes(file.size)}</span>
                    </div>
                    <button
                      type="button"
                      className="file-remove-btn"
                      onClick={(event) => {
                        event.stopPropagation()
                        removeFile(file.id)
                      }}
                      title="Quitar archivo"
                    >
                      <IconClose className="icon-xs" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        {/* Bento Tile 2: Document Preview & Editor (With Self-Contained Internal Scroll) */}
        <section className="bento-tile tile-preview">
          <div className="tile-header">
            <div className="tile-title-group">
              <IconLayers className="tile-icon" />
              <h2>Vista previa</h2>
              {selectedFile && (
                <span className="tile-tag" title={selectedFile.name}>
                  {selectedFile.name}
                </span>
              )}
            </div>

            <div className="bento-segmented-control">
              <button
                type="button"
                className={`segment-btn ${previewTab === 'rendered' ? 'active' : ''}`}
                onClick={() => setPreviewTab('rendered')}
              >
                Renderizado
              </button>
              <button
                type="button"
                className={`segment-btn ${previewTab === 'source' ? 'active' : ''}`}
                onClick={() => setPreviewTab('source')}
              >
                Original
              </button>
              <button
                type="button"
                className={`segment-btn ${previewTab === 'editor' ? 'active' : ''}`}
                onClick={() => setPreviewTab('editor')}
              >
                Editor
              </button>
            </div>
          </div>

          {/* Self-contained internal scroll container */}
          <div className="bento-preview-viewport">
            {previewTab === 'rendered' && (
              <div className="bento-markdown-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {currentMarkdown}
                </ReactMarkdown>
              </div>
            )}

            {previewTab === 'source' && (
              <pre className="bento-source-code">
                <code>{currentMarkdown}</code>
              </pre>
            )}

            {previewTab === 'editor' && (
              <div className="bento-editor-layout">
                <textarea
                  className="bento-textarea"
                  value={editorMarkdown}
                  placeholder="Escribe o pega contenido Markdown..."
                  onChange={(event) => {
                    setEditorMarkdown(event.target.value)
                    if (selectedFile) {
                      setFiles((current) =>
                        current.map((file) =>
                          file.id === selectedFile.id ? { ...file, content: event.target.value, size: event.target.value.length } : file,
                        ),
                      )
                    }
                  }}
                />
                <div className="editor-toolbar">
                  <button type="button" className="bento-btn bento-btn-subtle" onClick={copyMarkdown}>
                    <IconCopy className="btn-icon-xs" />
                    <span>Copiar texto</span>
                  </button>
                  <button type="button" className="bento-btn bento-btn-subtle" onClick={downloadMarkdown}>
                    <IconDownload className="btn-icon-xs" />
                    <span>Descargar .md</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Bento Tile 3: Configuration */}
        <section className="bento-tile tile-config">
          <div className="tile-header">
            <div className="tile-title-group">
              <IconSettings className="tile-icon" />
              <h2>Configuración</h2>
            </div>
          </div>

          <div className="config-form">
            <div className="form-group">
              <label htmlFor="conversion-mode" className="form-label">Modalidad de salida</label>
              <select
                id="conversion-mode"
                className="bento-select"
                value={mode}
                onChange={(event) => setMode(event.target.value as ConversionMode)}
              >
                <option value="consolidated">Consolidado (1 solo archivo)</option>
                <option value="individual">Individual (1 documento por .md)</option>
                <option value="grouped">Agrupado por carpetas</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="doc-name" className="form-label">Nombre del documento</label>
              <input
                id="doc-name"
                className="bento-input"
                value={documentName}
                placeholder="Nombre de archivo de salida"
                onChange={(event) => setDocumentName(event.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="output-dir" className="form-label">Carpeta local de guardado</label>
              <div className="input-with-action" onClick={selectOutputFolder}>
                <input
                  id="output-dir"
                  className="bento-input clickable"
                  value={outputDirectory}
                  readOnly
                />
                <button type="button" className="input-addon-btn" title="Seleccionar carpeta de salida">
                  <IconFolder className="icon-sm" />
                </button>
              </div>
            </div>

            <div className="config-toggles-card">
              <span className="toggles-header">Opciones de formato Word</span>

              <label className="bento-toggle-row">
                <input
                  type="checkbox"
                  checked={includeCover}
                  onChange={(event) => setIncludeCover(event.target.checked)}
                />
                <div className="toggle-text">
                  <span className="toggle-title">Portada formal</span>
                  <span className="toggle-desc">Incluye carátula técnica inicial</span>
                </div>
              </label>

              <label className="bento-toggle-row">
                <input
                  type="checkbox"
                  checked={includeToc}
                  onChange={(event) => setIncludeToc(event.target.checked)}
                />
                <div className="toggle-text">
                  <span className="toggle-title">Tabla de contenido</span>
                  <span className="toggle-desc">Índice automático de secciones</span>
                </div>
              </label>

              <label className="bento-toggle-row">
                <input
                  type="checkbox"
                  checked={pageBreaks}
                  onChange={(event) => setPageBreaks(event.target.checked)}
                />
                <div className="toggle-text">
                  <span className="toggle-title">Salto de página</span>
                  <span className="toggle-desc">Separar documentos en nueva página</span>
                </div>
              </label>

              <label className="bento-toggle-row highlight">
                <input
                  type="checkbox"
                  checked={autoDownload}
                  onChange={(event) => setAutoDownload(event.target.checked)}
                />
                <div className="toggle-text">
                  <span className="toggle-title">Descarga automática</span>
                  <span className="toggle-desc">Descarga al terminar de convertir</span>
                </div>
              </label>
            </div>
          </div>
        </section>

        {/* Bento Tile 4: Conversion Results (Full Width Bento Row) */}
        <section className="bento-tile tile-results" ref={resultsRef}>
          <div className="tile-header">
            <div className="tile-title-group">
              <IconDownload className="tile-icon" />
              <h2>Documentos generados</h2>
              <span className="tile-counter">{results.length}</span>
            </div>

            {results.length > 1 && (
              <button
                type="button"
                className="bento-btn bento-btn-primary"
                onClick={() => {
                  const zipResult = results.find((r) => r.name.endsWith('.zip'))
                  if (zipResult) {
                    downloadResult(zipResult.download_url, zipResult.name)
                  } else {
                    results.forEach((r) => downloadResult(r.download_url, r.name))
                  }
                }}
              >
                <IconDownload className="btn-icon-xs" />
                <span>Descargar lote completo (.ZIP)</span>
              </button>
            )}
          </div>

          {results.length === 0 ? (
            <div className="results-empty-bento">
              <IconFileText className="empty-icon" />
              <p>Todavía no hay documentos procesados.</p>
              <small>Presiona "Convertir a Word" para generar tus archivos .docx.</small>
            </div>
          ) : (
            <div className="bento-results-grid">
              {results.map((result) => (
                <div key={result.name} className="bento-result-card">
                  <div className="result-card-header">
                    <span className="result-card-format">
                      {result.name.endsWith('.zip') ? 'ZIP' : 'DOCX'}
                    </span>
                    <strong className="result-card-name" title={result.name}>{result.name}</strong>
                  </div>

                  <div className="result-card-actions">
                    <button
                      type="button"
                      className="bento-btn bento-btn-primary full-width"
                      onClick={() => downloadResult(result.download_url, result.name)}
                    >
                      <IconDownload className="btn-icon-xs" />
                      <span>Descargar</span>
                    </button>
                    <button
                      type="button"
                      className="bento-btn bento-btn-subtle"
                      onClick={() => saveResultToFolder(result)}
                      title="Guardar en carpeta local"
                    >
                      <IconFolder className="btn-icon-xs" />
                      <span>Guardar</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Modern Bento Footer */}
      <footer className="bento-footer">
        <div className="footer-content">
          <div className="footer-meta">
            <span className="footer-title">Markdown to Word Local Converter</span>
            <span className="footer-dot">•</span>
            <span className="footer-desc">Procesamiento 100% privado y local sin envío de datos externos</span>
          </div>

          <div className="footer-attribution">
            <p>
              &copy; 2026 Desarrollado por <strong>Redja</strong>. Todos los derechos reservados.
              <span className="license-tag">Licencia abierta para uso libre y distribución</span>
            </p>
          </div>

          <div className="footer-tech-stack">
            <span className="tech-pill">FastAPI</span>
            <span className="tech-pill">React 19</span>
            <span className="tech-pill">TypeScript</span>
            <span className="tech-pill">Vite</span>
            <span className="tech-pill">python-docx</span>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
