"""DCL (Data Control Language) — equivalente a sql/mariadb/commands/05_DCL.sql.

CREATE USER / GRANT / REVOKE / FLUSH PRIVILEGES / SHOW GRANTS. Requiere una cuenta
administrativa (por defecto root de XAMPP). Es repetible: CREATE USER usa IF NOT EXISTS.

Las contraseñas de las cuentas de ejemplo se pueden cambiar con las variables de
entorno GLOB_GUSTERS_PASS_REPORTES y GLOB_GUSTERS_PASS_MOSTRADOR; los valores por
defecto son los mismos del .sql.
"""

import os

from conexion import conexion, consultar, ejecutar

BD = "glob_gusters"
USUARIOS = {
    "glob_gusters_reportes": (os.getenv("GLOB_GUSTERS_PASS_REPORTES", "Reportes#2024"), "SELECT"),
    "glob_gusters_mostrador": (os.getenv("GLOB_GUSTERS_PASS_MOSTRADOR", "Mostrador#2024"), "SELECT, INSERT, UPDATE"),
}


def main():
    with conexion() as con:
        for usuario, (clave, privilegios) in USUARIOS.items():
            cuenta = f"'{usuario}'@'localhost'"
            # La contraseña va como parámetro; el resto son nombres fijos definidos arriba.
            ejecutar(con, f"CREATE USER IF NOT EXISTS {cuenta} IDENTIFIED BY %s", (clave,))
            ejecutar(con, f"GRANT {privilegios} ON `{BD}`.* TO {cuenta}")
            print(f"Usuario {cuenta}: GRANT {privilegios}")

        # El personal de mostrador no puede borrar historial de rentas.
        ejecutar(con, f"REVOKE DELETE ON `{BD}`.* FROM 'glob_gusters_mostrador'@'localhost'")
        ejecutar(con, "FLUSH PRIVILEGES")

        for usuario in USUARIOS:
            print(f"\n== Privilegios de {usuario} ==")
            for fila in consultar(con, f"SHOW GRANTS FOR '{usuario}'@'localhost'"):
                print(next(iter(fila.values())))


if __name__ == "__main__":
    main()
