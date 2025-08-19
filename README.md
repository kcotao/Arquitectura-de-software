Flavio Oyarce González
202173617-4

Esta mini app corre 2 micro servicios

Libros-service:
Puedes cargar libros a la página solo utilizando los autores de autores-service,
también puedes visualizar los libros que ya creaste.

Autores-service:
Puedes ver la lista de autores ya existentes,
puedes crear nuevos autores con su respectiva ID.

Utiliza una comunicación mediante logs de Promtail, Loki y visualización mediante Grafana.

Para ejecutar:
docker compose up -d --build
