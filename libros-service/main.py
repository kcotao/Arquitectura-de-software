from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import httpx, logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

class Libro(BaseModel):
    id: int
    titulo: str
    autor_id: int
    año: Optional[int] = None

libros: List[Libro] = []

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

async def obtener_nombre_autor(autor_id: int):
    try:
        logger.debug(f"Iniciando consulta de autor ID: {autor_id}")
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://autores-service:8001/autores/{autor_id}")
            if response.status_code == 404:
                logger.warning(f"Autor no encontrado (ID: {autor_id})")
                return "Autor desconocido"
            nombre_autor = response.json()["nombre"]
            logger.debug(f"Autor obtenido: {nombre_autor}")
            return nombre_autor
    except httpx.HTTPStatusError as e:
        logger.error(f"Error de conexión con servicio de autores: {str(e)}")
        return "Autor desconocido"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Acceso a la página principal")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/libros")
async def listar_libros():
    try:
        logger.info("Listando todos los libros")
        libros_con_autor = []
        for libro in libros:
            logger.debug(f"Procesando libro ID: {libro.id}")
            autor_nombre = await obtener_nombre_autor(libro.autor_id)
            libros_con_autor.append({
                **libro.dict(),
                "autor_nombre": autor_nombre
            })
        logger.info(f"Total de libros listados: {len(libros_con_autor)}")
        return libros_con_autor
    except Exception as e:
        logger.error(f"Error al listar libros: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Error interno al listar libros")

@app.post("/libros")
def crear_libro(libro: Libro):
    try:
        logger.info(f"Intentando crear libro: {libro.titulo} (ID: {libro.id})")
        
        if any(l.id == libro.id for l in libros):
            error_msg = f"ID de libro duplicado: {libro.id}"
            logger.error(error_msg)
            raise HTTPException(400, detail=error_msg)
            
        libros.append(libro)
        logger.info(f"Libro creado exitosamente: {libro.titulo}")
        return {"message": f"Libro {libro.titulo} creado"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al crear libro: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Error interno al crear libro")

@app.get("/libros/{id}")
async def obtener_libro(id: int):
    try:
        logger.info(f"Buscando libro ID: {id}")
        libro = next((l for l in libros if l.id == id), None)
        
        if not libro:
            logger.warning(f"Libro no encontrado (ID: {id})")
            raise HTTPException(404, detail="Libro no encontrado")
        
        autor_nombre = await obtener_nombre_autor(libro.autor_id)
        logger.debug(f"Libro encontrado: {libro.titulo}")
        
        return {
            **libro.dict(),
            "autor_nombre": autor_nombre
        }
    
    except Exception as e:
        logger.error(f"Error al obtener libro: {str(e)}", exc_info=True)
        raise HTTPException(500, detail="Error interno al obtener libro")
