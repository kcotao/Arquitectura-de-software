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

class Autor(BaseModel):
    id: int
    nombre: str

# Autores por defecto
autores: List[Autor] = [
    Autor(id=1, nombre="Gabriel García Márquez"),
    Autor(id=2, nombre="J.K. Rowling"),
    Autor(id=3, nombre="George Orwell"),
    Autor(id=4, nombre="Jane Austen"),
    Autor(id=5, nombre="J.R.R. Tolkien")
]

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    logger.info("Acceso a página principal de autores")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/autores")
def listar_autores():
    logger.info("Listando todos los autores")
    return autores

@app.get("/autores/{id}")
def obtener_autor(id: int):
    logger.info(f"Buscando autor ID: {id}")
    autor = next((a for a in autores if a.id == id), None)
    if not autor:
        logger.warning(f"Autor no encontrado (ID: {id})")
        raise HTTPException(404, detail="Autor no encontrado")
    logger.debug(f"Autor encontrado: {autor.nombre}")
    return autor

@app.post("/autores")
def crear_autor(autor: Autor):
    try:
        logger.info(f"Intentando crear autor: {autor.nombre} (ID: {autor.id})")
        
        if any(a.id == autor.id for a in autores):
            error_msg = f"ID de autor ya existe: {autor.id}"
            logger.error(error_msg)
            raise HTTPException(400, detail=error_msg)
            
        autores.append(autor)
        logger.info(f"Autor creado exitosamente: {autor.nombre}")
        return {"message": f"Autor {autor.nombre} creado"}
        
    except Exception as e:
        logger.error(f"Error al crear autor: {str(e)}", exc_info=True)
        raise