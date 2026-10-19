"""DQL (Data Query Language) — equivalente a sql/mariadb/commands/03_DQL.sql.

Consultas de solo lectura: SELECT con condición, JOIN y GROUP BY.
Sin argumentos ejecuta todas; con un nombre ejecuta una sola:
    python py/dql.py disponibles
"""

import sys

from conexion import conexion, consultar, imprimir

CONSULTAS = {
    "disponibles": (
        "Ejemplares disponibles para alquilar",
        """SELECT e.`Ejemplar_ID`, e.`Numero`, p.`Titulo`
           FROM `ejemplar` e
           INNER JOIN `pelicula` p ON p.`Pelicula_ID` = e.`Pelicula_ID`
           WHERE e.`Ejemplar_ID` NOT IN (
               SELECT er.`Ejemplar_ID` FROM `ejemplar_renta` er WHERE er.`Entrega` IS NULL
           )""",
    ),
    "rentas_activas": (
        "Rentas activas (sin fecha de devolución)",
        """SELECT c.`Nombre` AS Cliente, r.`Renta_ID`, r.`Inicia`,
                  pe.`Titulo` AS Pelicula, ej.`Numero` AS Numero_Ejemplar
           FROM `renta` r
           INNER JOIN `cliente` c         ON c.`Cliente_ID` = r.`Cliente_ID`
           INNER JOIN `ejemplar_renta` er ON er.`Renta_ID` = r.`Renta_ID`
           INNER JOIN `ejemplar` ej       ON ej.`Ejemplar_ID` = er.`Ejemplar_ID`
           INNER JOIN `pelicula` pe       ON pe.`Pelicula_ID` = ej.`Pelicula_ID`
           WHERE r.`Termina` IS NULL
           ORDER BY r.`Inicia`""",
    ),
    "peliculas_por_nacionalidad": (
        "Películas por nacionalidad",
        """SELECT n.`Nombre` AS Nacionalidad, COUNT(*) AS Total_Peliculas
           FROM `pelicula` p
           INNER JOIN `nacionalidad` n ON n.`Nacionalidad_ID` = p.`Nacionalidad_ID`
           GROUP BY n.`Nombre`
           ORDER BY Total_Peliculas DESC""",
    ),
    "ejemplares_por_estado": (
        "Ejemplares por estado de conservación",
        """SELECT es.`Nombre` AS Estado, COUNT(*) AS Total_Ejemplares
           FROM `ejemplar` e
           INNER JOIN `estado` es ON es.`Estado_ID` = e.`Estado_ID`
           GROUP BY es.`Nombre`""",
    ),
}


def main(argv):
    nombres = argv or list(CONSULTAS)
    desconocidas = [n for n in nombres if n not in CONSULTAS]
    if desconocidas:
        sys.exit(f"Consulta desconocida: {', '.join(desconocidas)}. Opciones: {', '.join(CONSULTAS)}")
    with conexion() as con:
        for nombre in nombres:
            titulo, sql = CONSULTAS[nombre]
            imprimir(titulo, consultar(con, sql))


if __name__ == "__main__":
    main(sys.argv[1:])
