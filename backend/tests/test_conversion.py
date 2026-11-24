import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_convert_individual_document():
    payload = {
        'files': [
            {
                'name': 'report.md',
                'relative_path': 'QA/report.md',
                'content': '# Proyecto\n\n- Ítem 1\n- Ítem 2\n\n```python\nprint("hola")\n```',
                'size': 100,
            }
        ],
        'mode': 'individual',
        'document_name': 'reporte',
        'include_cover': True,
        'include_toc': False,
        'page_breaks': True,
    }

    response = client.post('/api/convert', json=payload)
    assert response.status_code == 200
    results = response.json()['results']
    assert results[0]['name'].endswith('.docx')
    assert '/api/download' in results[0]['download_url']

    download = client.get(results[0]['download_url'])
    assert download.status_code == 200
    assert download.headers['content-type'].startswith('application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    assert len(download.content) > 0


def test_convert_individual_document_creates_zip():
    payload = {
        'files': [
            {'name': 'one.md', 'relative_path': 'A/one.md', 'content': '# Primero\n\n- a', 'size': 10},
            {'name': 'two.md', 'relative_path': 'B/two.md', 'content': '# Segundo\n\n- b', 'size': 20},
        ],
        'mode': 'individual',
        'document_name': 'bundle',
        'include_cover': True,
        'include_toc': False,
        'page_breaks': True,
    }

    response = client.post('/api/convert', json=payload)
    assert response.status_code == 200
    data = response.json()
    zip_result = next(item for item in data['results'] if item['name'].endswith('.zip'))
    assert zip_result['download_url'].startswith('/api/download?file_name=')

    zip_download = client.get(zip_result['download_url'])
    assert zip_download.status_code == 200
    assert zip_download.headers['content-type'].startswith('application/zip')
    assert len(zip_download.content) > 0


def test_convert_document_preserves_table_structure():
    import io
    from docx import Document

    table_md = """# Reporte con Tabla

## Sección de prueba

| Campo | Valor |
| --- | --- |
| ID | CP-001 |
| Nombre | test_login |
| Estado | Exitoso |
"""
    payload = {
        'files': [
            {'name': 'table_test.md', 'relative_path': 'table_test.md', 'content': table_md, 'size': len(table_md)},
        ],
        'mode': 'individual',
        'document_name': 'test_table',
        'include_cover': False,
        'include_toc': False,
        'page_breaks': False,
    }

    response = client.post('/api/convert', json=payload)
    assert response.status_code == 200
    results = response.json()['results']
    download_url = results[0]['download_url']

    download = client.get(download_url)
    assert download.status_code == 200

    doc = Document(io.BytesIO(download.content))
    assert len(doc.tables) >= 1
    table = doc.tables[0]
    # Check that table has 4 rows (1 header + 3 body rows), NOT 1 row!
    assert len(table.rows) == 4
    assert len(table.columns) == 2
    assert table.cell(0, 0).text.strip() == 'Campo'
    assert table.cell(1, 0).text.strip() == 'ID'
    assert table.cell(1, 1).text.strip() == 'CP-001'
    assert table.cell(3, 0).text.strip() == 'Estado'
    assert table.cell(3, 1).text.strip() == 'Exitoso'

