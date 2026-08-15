# Import des librairies
import os
from pathlib import Path
from supabase import create_client

# On renseigne les variables d'environnement
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

# On crée le client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# On définit les tables à exporter
tables = ["jugadores","tm_achievements","tm_clubs_roster","tm_injuries","tm_profiles","tm_transfers","entity_resolution","fotmob_internationals","silver_analyst",
"silver_fotmob","silver_sofascore","silver_understat","sofascore_valuations","valuations","capology_payrolls","capology_salaries","salarysport_salaries"]

output_dir = Path("data")
output_dir.mkdir(exist_ok=True)

for table in tables:
    print(f"Export de {table}...")

    response = (
        supabase
        .table(table)
        .select("*")
        .csv()
        .execute()
    )

    output_file = output_dir / f"{table}.csv"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(response.data)

    print(f"{table} exportée vers {output_file}")