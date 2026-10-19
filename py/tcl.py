"""TCL (Transaction Control Language) — equivalente a sql/mariadb/commands/06_TCL.sql.

Ejemplo 1: START TRANSACTION + SAVEPOINT + COMMIT al registrar una renta con su detalle.
Ejemplo 2: transacción descartada con ROLLBACK.
Es repetible: si el cliente de ejemplo ya tiene ese ejemplar sin devolver, no inserta
nada (así no se acumulan préstamos hasta chocar con el trigger de máximo 4).
"""

import pymysql

from conexion import conexion, consultar, ejecutar, imprimir

DNI_CLIENTE = "1000000004"  # Andrés Torres
EJEMPLAR = ("Interstellar", 2014, 2)  # título, año, número de ejemplar


def main():
    with conexion() as con:
        cliente = consultar(con, "SELECT `Cliente_ID` FROM `cliente` WHERE `Dni` = %s", (DNI_CLIENTE,))
        ejemplar = consultar(
            con,
            """SELECT e.`Ejemplar_ID` FROM `ejemplar` e
               INNER JOIN `pelicula` p ON p.`Pelicula_ID` = e.`Pelicula_ID`
               WHERE p.`Titulo` = %s AND p.`Anio` = %s AND e.`Numero` = %s""",
            EJEMPLAR,
        )
        if not cliente or not ejemplar:
            raise SystemExit("Faltan datos de ejemplo: ejecuta glob_gusters_insert.sql primero.")
        id_cliente, id_ejemplar = cliente[0]["Cliente_ID"], ejemplar[0]["Ejemplar_ID"]

        ya_existe = consultar(
            con,
            """SELECT 1 AS existe FROM `ejemplar_renta` er
               INNER JOIN `renta` r ON r.`Renta_ID` = er.`Renta_ID`
               WHERE r.`Cliente_ID` = %s AND er.`Ejemplar_ID` = %s AND er.`Entrega` IS NULL""",
            (id_cliente, id_ejemplar),
        )

        # --- Ejemplo 1: renta + detalle de forma atómica -----------------------------
        con.begin()  # START TRANSACTION
        if ya_existe:
            print("La renta de ejemplo ya existe; no se inserta de nuevo.")
        else:
            try:
                with con.cursor() as cur:
                    cur.execute(
                        "INSERT INTO `renta` (`Cliente_ID`, `Inicia`, `Termina`) VALUES (%s, CURDATE(), NULL)",
                        (id_cliente,),
                    )
                    id_renta = cur.lastrowid
                    cur.execute("SAVEPOINT `sp_renta_creada`")
                    try:
                        cur.execute(
                            "INSERT INTO `ejemplar_renta` (`Renta_ID`, `Ejemplar_ID`, `Entrega`) VALUES (%s, %s, NULL)",
                            (id_renta, id_ejemplar),
                        )
                    except pymysql.err.OperationalError as error:
                        # Trigger de máximo 4 ejemplares: se conserva sólo el encabezado.
                        print("Detalle rechazado, ROLLBACK TO SAVEPOINT:", error.args[1])
                        cur.execute("ROLLBACK TO SAVEPOINT `sp_renta_creada`")
                    else:
                        print(f"Renta {id_renta} registrada con el ejemplar {id_ejemplar}.")
            except Exception:
                con.rollback()
                raise
        con.commit()

        # --- Ejemplo 2: cambio que se descarta ---------------------------------------
        con.begin()
        ejecutar(con, "UPDATE `cliente` SET `Direccion` = %s WHERE `Dni` = %s",
                 ("Dirección temporal de prueba", "1000000001"))
        dentro = consultar(con, "SELECT `Direccion` FROM `cliente` WHERE `Dni` = %s", ("1000000001",))
        con.rollback()
        fuera = consultar(con, "SELECT `Direccion` FROM `cliente` WHERE `Dni` = %s", ("1000000001",))
        imprimir("Dirección dentro de la transacción", dentro)
        imprimir("Dirección tras el ROLLBACK", fuera)


if __name__ == "__main__":
    main()
