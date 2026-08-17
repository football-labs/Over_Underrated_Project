# Import des librairies
import os
from pathlib import Path
import pandas as pd
from supabase import create_client

# On renseigne les variables d'environnement
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

# On crée le client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# On définit les tables à exporter avec leur schéma
tables = {
    "maestros": ["jugadores"],
    "profiles": ["tm_achievements","tm_clubs_roster","tm_injuries","tm_profiles","tm_transfers"],
    "stats": ["entity_resolution","fotmob_internationals","silver_analyst","silver_fotmob","silver_sofascore","silver_understat","sofascore_valuations",
        "valuations"],
    "wages": ["capology_payrolls","capology_salaries","salarysport_salaries"]
}

# Dossier de sortie
output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

# Taille des lots
batch_size = 1000

# Export de toutes les tables
for schema, schema_tables in tables.items():

    for table in schema_tables:
        print(f"\nExport de {schema}.{table}...")

        all_rows = []
        start = 0

        while True:
            response = (
                supabase
                .schema(schema)
                .table(table)
                .select("*")
                .range(start, start + batch_size - 1)
                .execute()
            )

            rows = response.data

            if not rows:
                break

            all_rows.extend(rows)

            # Si moins de 1000 lignes sont retournées, on sait qu'on a atteint la fin
            if len(rows) < batch_size:
                break

            start += batch_size

        # Conversion en DataFrame
        df = pd.DataFrame(all_rows)

        # Export CSV
        output_file = output_dir / f"{table}.csv"
        df.to_csv(output_file, index=False)

        print(
            f"{schema}.{table} exportée vers {output_file} "
            f"({len(df)} lignes)"
        )