import asyncio

import duckdb


def create_db(json_dir: str | None = None, db_path: str | None = None) -> duckdb.DuckDBPyConnection:
    json_dir = json_dir or "data/gml"
    db_path = db_path or "data/geo.db"
    conn = duckdb.connect(db_path)
    conn.install_extension("spatial")
    conn.install_extension("postgres")
    conn.load_extension("spatial")

    conn.sql("""
             DROP TABLE IF EXISTS borders
             """)

    conn.sql("""
    CREATE TABLE borders (
        ID VARCHAR PRIMARY KEY,
        shape GEOMETRY,
        type VARCHAR,
        name VARCHAR,
        parent_id VARCHAR NULL,
        ancestors VARCHAR[]
    )""")

    communes_json = f"{json_dir}/A03_Granice_gmin.json"
    conn.sql(
        f"""INSERT INTO borders
        SELECT 
            CONCAT('PL', LPAD(CAST(JPT_KOD_JE AS VARCHAR), 7, '0')) as ID,
            geom AS shape, 
            JPT_SJR_KO as type,
            JPT_NAZWA_ as name,
            CONCAT('PL', LPAD(CAST(JPT_KOD_JE AS VARCHAR), 4, '0')) as parent_id,
            ['PL', CONCAT('PL', LPAD(CAST(JPT_KOD_JE AS VARCHAR), 2, '0')), CONCAT('PL', LPAD(CAST(JPT_KOD_JE AS VARCHAR), 4, '0'))] as ancestors
        FROM ST_Read('{communes_json}')"""
    )

    counties_json = f"{json_dir}/A02_Granice_powiatow.json"
    conn.sql(
        f"""INSERT INTO borders
        SELECT 
            CONCAT('PL', LPAD(CAST(JPT_KOD_JE AS VARCHAR), 4, '0')) as ID,
            geom AS shape,
            JPT_SJR_KO as type,
            JPT_NAZWA_ as name,
            CONCAT('PL', LPAD(CAST(JPT_KOD_JE AS VARCHAR), 2, '0')) as parent_id,
            ['PL', CONCAT('PL', LPAD(CAST(JPT_KOD_JE AS VARCHAR), 2, '0'))] as ancestors
        FROM ST_Read('{counties_json}')"""
    )

    voivodeships_json = f"{json_dir}/A01_Granice_wojewodztw.json"
    conn.sql(
        f"""INSERT INTO borders
        SELECT 
            CONCAT('PL', LPAD(CAST(JPT_KOD_JE AS VARCHAR), 2, '0')) as ID,
            geom AS shape,
            JPT_SJR_KO as type,
            JPT_NAZWA_ as name,
            'PL' as parent_id,
            ['PL'] as ancestors
        FROM ST_Read('{voivodeships_json}')"""
    )

    country_json = f"{json_dir}/A00_Granice_panstwa.json"
    conn.sql(
        f"""INSERT INTO borders
        SELECT 
            'PL' as ID,
            geom AS shape,
            JPT_SJR_KO as type,
            JPT_NAZWA_ as name,
            NULL as parent_id,
            [] as ancestors
        FROM ST_Read('{country_json}')"""
    )

    return conn


async def aio_create_db(json_dir: str | None = None) -> duckdb.DuckDBPyConnection:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, create_db, json_dir)


if __name__ == "__main__":
    create_db()
