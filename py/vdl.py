"""VDL (View Definition Language) — equivalente a sql/mariadb/commands/04_VDL.sql.

CREATE OR REPLACE VIEW de las dos vistas del proyecto y consulta de cada una.
El DROP VIEW queda detrás de la opción --drop, igual que está comentado en el .sql:
    python py/vdl.py --drop
"""

import sys

from conexion import conexion, consultar, ejecutar, imprimir

VISTAS = {
    "v_ejemplares_detalle": (
        """CREATE OR REPLACE VIEW `v_ejemplares_detalle` AS
           SELECT e.`Ejemplar_ID`, e.`Numero` AS Numero_Ejemplar, p.`Titulo` AS Pelicula,
                  p.`Anio`, es.`Nombre` AS Estado_Conservacion
           FROM `ejemplar` e
           INNER JOIN `pelicula` p ON p.`Pelicula_ID` = e.`Pelicula_ID`
           INNER JOIN `estado` es  ON es.`Estado_ID` = e.`Estado_ID`""",
        "SELECT * FROM `v_ejemplares_detalle` ORDER BY `Pelicula`, `Numero_Ejemplar`",
    ),
    "v_clientes_con_aval": (
        """CREATE OR REPLACE VIEW `v_clientes_con_aval` AS
           SELECT c.`Cliente_ID`, c.`Nombre` AS Cliente, c.`Dni`, aval.`Nombre` AS Avalado_Por
           FROM `cliente` c
           LEFT JOIN `cliente` aval ON aval.`Cliente_ID` = c.`Aval_Cliente_ID`""",
        "SELECT * FROM `v_clientes_con_aval` ORDER BY `Cliente`",
    ),
}


def main(argv):
    with conexion() as con:
        if "--drop" in argv:
            for nombre in VISTAS:
                ejecutar(con, f"DROP VIEW IF EXISTS `{nombre}`")
                print(f"Vista eliminada: {nombre}")
            con.commit()
            return
        for nombre, (crear, consulta) in VISTAS.items():
            ejecutar(con, crear)
            imprimir(nombre, consultar(con, consulta))
        con.commit()


if __name__ == "__main__":
    main(sys.argv[1:])
