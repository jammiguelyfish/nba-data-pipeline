from nba_api.stats.endpoints import leaguedashteamstats, leagueleaders
import duckdb


def run_nba_etl():
    print("Starting NBA ETL pipeline...")

    # Extract
    stats = leaguedashteamstats.LeagueDashTeamStats(season='2025-26')
    df = stats.get_data_frames()[0]
    print(f"Extracted {len(df)} rows from NBA API...")

    # Load
    con = duckdb.connect('nba_warehouse.db')
    con.execute("DROP TABLE IF EXISTS staging_team_stats")
    con.execute("CREATE TABLE staging_team_stats AS SELECT * FROM df")
    print("Loaded data into staging...")

    # Extract player leaders
    leaders = leagueleaders.LeagueLeaders(season='2025-26', stat_category_abbreviation='PTS')
    df_leaders = leaders.get_data_frames()[0]
    print(f"Extracted {len(df_leaders)} player rows from NBA API...")

    con.execute("DROP TABLE IF EXISTS staging_player_stats")
    con.execute("CREATE TABLE staging_player_stats AS SELECT * FROM df_leaders")
    print("Loaded player stats into staging...")

    # Transform team standings
    con.execute("""
        CREATE OR REPLACE TABLE analytics_team_standings AS
        SELECT
            TEAM_NAME,
            GP,
            W,
            L,
            W_PCT,
            PTS,
            AST,
            (PTS + AST) / GP AS OFFENSIVE_EFFICIENCY
        FROM staging_team_stats
        ORDER BY W_PCT DESC
    """)
    print("Transformed data loaded into analytics_team_standings...")

    # Transform league leaders
    con.execute("""
        CREATE OR REPLACE TABLE analytics_league_leaders AS
        SELECT
            PLAYER,
            TEAM,
            GP,
            PTS,
            AST,
            REB,
            STL,
            BLK,
            EFF
        FROM staging_player_stats
        ORDER BY PTS DESC
    """)
    print("Transformed data loaded into analytics_league_leaders...")

    con.close()
    print("NBA ETL pipeline complete.")


if __name__ == "__main__":
    run_nba_etl()
