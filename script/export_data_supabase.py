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
    "stats": ["entity_resolution","fotmob_internationals","silver_analyst","silver_fotmob","silver_sofascore","silver_understat",
        "sofascore_valuations","valuations","fotmob_v2","sofascore_v2"],
    "wages": ["capology_payrolls","capology_salaries","salarysport_salaries"]
}

# Colonnes spécifiques à récupérer pour certaines tables
selected_columns = {
    "fotmob_v2": ["player_id","name","team","league","position", "positions_all","birth_date","is_international","national_team","clean_sheets_val","clean_sheets_pct90",
    "error_led_to_goal_val","error_led_to_goal_per90", "xa_val","xa_per90","yellow_cards_val","yellow_cards_per90","red_cards_val","red_cards_per90",
    "penalty_saves_val", "penalty_saves_pct","penalties_conceded_val","high_claims_val","high_claims_per90","high_claims_pct","xg_excl_penalty_val",
    "xg_excl_penalty_per90","assists_val","assists_per90","big_chances_created_val", "big_chances_created_per90","touches_in_opposition_box_val",
    "touches_in_opposition_bo_per90","dispossessed_val", "dispossessed_per90","fouls_won_val","fouls_won_per90","fouls_committed_val","fouls_committed_per90",
    "minutes_played","successful_crosses_val","successful_crosses_per90","cross_accuracy_val","dribbles_val","dribbles_per90","dribbles_success_rate_val",
    "possession_won_final_3rd_val","possession_won_final_3rd_val_per90","dribbled_past_val", "dribbled_past_per90","penalties_awarded_val", "penalties_awarded_per90",
    "top_speed_val","running_per90","sprinting_per90","penalty_goals_val","season"]
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

        # Si la table possède une sélection spécifique de colonnes,
        # on utilise cette liste. Sinon, on récupère toutes les colonnes.
        columns = ",".join(selected_columns.get(table, ["*"]))

        while True:
            response = (
                supabase
                .schema(schema)
                .table(table)
                .select(columns)
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