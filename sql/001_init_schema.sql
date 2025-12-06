-- 001_init_schema.sql

-- Optional extension, handy later (UUIDs etc.)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-----------------------------
-- Dimension tables
-----------------------------

-- Seasons
CREATE TABLE IF NOT EXISTS dim_season (
    season_id      INTEGER PRIMARY KEY,   -- e.g. 20242025
    regular_start  DATE,
    regular_end    DATE,
    playoffs_start DATE,
    playoffs_end   DATE
);

-- Teams
CREATE TABLE IF NOT EXISTS dim_team (
    team_id        INTEGER PRIMARY KEY,       -- NHL numeric ID
    team_code      CHAR(3) NOT NULL UNIQUE,   -- e.g. "EDM"
    team_name      VARCHAR(100) NOT NULL,
    city           VARCHAR(100),
    conference     VARCHAR(50),
    division       VARCHAR(50),
    first_season   INTEGER,
    last_updated   TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Players
CREATE TABLE IF NOT EXISTS dim_player (
    player_id        INTEGER PRIMARY KEY,      -- NHL numeric ID
    full_name        VARCHAR(100) NOT NULL,
    first_name       VARCHAR(50),
    last_name        VARCHAR(50),
    shoots_catches   CHAR(1),                  -- 'L' or 'R'
    primary_position VARCHAR(5),               -- C, LW, RW, D, G
    birth_date       DATE,
    nationality      VARCHAR(3),
    last_updated     TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Games
CREATE TABLE IF NOT EXISTS dim_game (
    game_id        BIGINT PRIMARY KEY,        -- NHL gamePk
    season_id      INTEGER NOT NULL REFERENCES dim_season(season_id),
    game_date      DATE NOT NULL,
    game_type      CHAR(1) NOT NULL,          -- 'R', 'P', etc.
    home_team_id   INTEGER NOT NULL REFERENCES dim_team(team_id),
    away_team_id   INTEGER NOT NULL REFERENCES dim_team(team_id),
    venue          VARCHAR(100),
    status         VARCHAR(30),
    last_updated   TIMESTAMP NOT NULL DEFAULT NOW()
);

-----------------------------
-- Fact tables: game level
-----------------------------

-- Team-game stats
CREATE TABLE IF NOT EXISTS fact_team_game (
    game_id        BIGINT NOT NULL REFERENCES dim_game(game_id),
    team_id        INTEGER NOT NULL REFERENCES dim_team(team_id),
    is_home        BOOLEAN NOT NULL,
    goals_for      SMALLINT,
    goals_against  SMALLINT,
    shots_for      SMALLINT,
    shots_against  SMALLINT,
    corsi_for      SMALLINT,
    corsi_against  SMALLINT,
    fenwick_for    SMALLINT,
    fenwick_against SMALLINT,
    xg_for         REAL,
    xg_against     REAL,
    pp_goals_for   SMALLINT,
    pp_opportunities SMALLINT,
    pk_goals_against SMALLINT,
    pk_times_shorthanded SMALLINT,
    faceoff_win_pct REAL,
    hits           SMALLINT,
    blocks         SMALLINT,
    penalty_minutes SMALLINT,
    raw_stats      JSONB,
    PRIMARY KEY (game_id, team_id)
);

-- Player-game stats
CREATE TABLE IF NOT EXISTS fact_player_game (
    game_id        BIGINT NOT NULL REFERENCES dim_game(game_id),
    player_id      INTEGER NOT NULL REFERENCES dim_player(player_id),
    team_id        INTEGER NOT NULL REFERENCES dim_team(team_id),
    is_home        BOOLEAN NOT NULL,
    position       VARCHAR(5),
    toi_seconds    INTEGER,
    toi_ev_seconds INTEGER,
    toi_pp_seconds INTEGER,
    toi_sh_seconds INTEGER,
    goals          SMALLINT,
    assists        SMALLINT,
    points         SMALLINT,
    shots          SMALLINT,
    hits           SMALLINT,
    blocks         SMALLINT,
    pim            SMALLINT,
    plus_minus     SMALLINT,
    faceoff_wins   SMALLINT,
    faceoff_losses SMALLINT,
    expected_goals REAL,
    scoring_chances SMALLINT,
    high_danger_chances SMALLINT,
    -- Goalie fields
    saves          SMALLINT,
    shots_against  SMALLINT,
    goals_against  SMALLINT,
    save_pct       REAL,
    gsaa           REAL,
    raw_stats      JSONB,
    PRIMARY KEY (game_id, player_id)
);

-----------------------------
-- Fact tables: daily snapshots
-----------------------------

-- Team-day aggregates
CREATE TABLE IF NOT EXISTS fact_team_day (
    snapshot_date         DATE NOT NULL,
    team_id               INTEGER NOT NULL REFERENCES dim_team(team_id),
    season_id             INTEGER NOT NULL REFERENCES dim_season(season_id),

    games_played_season   SMALLINT,
    wins_season           SMALLINT,
    losses_season         SMALLINT,
    ot_losses_season      SMALLINT,
    points_season         SMALLINT,

    games_played_last10   SMALLINT,
    wins_last10           SMALLINT,
    goals_for_last10      SMALLINT,
    goals_against_last10  SMALLINT,
    xg_for_last10         REAL,
    xg_against_last10     REAL,

    win_streak            SMALLINT,   -- +ve = wins, -ve = losses
    goal_diff_streak      SMALLINT,   -- consecutive GF-GA > 0 games
    last_game_id          BIGINT,

    PRIMARY KEY (snapshot_date, team_id)
);

-- Player-day aggregates
CREATE TABLE IF NOT EXISTS fact_player_day (
    snapshot_date          DATE NOT NULL,
    player_id              INTEGER NOT NULL REFERENCES dim_player(player_id),
    team_id                INTEGER NOT NULL REFERENCES dim_team(team_id),
    season_id              INTEGER NOT NULL REFERENCES dim_season(season_id),

    games_played_season    SMALLINT,
    goals_season           SMALLINT,
    assists_season         SMALLINT,
    points_season          SMALLINT,
    toi_season_seconds     INTEGER,

    games_played_last5     SMALLINT,
    goals_last5            SMALLINT,
    assists_last5          SMALLINT,
    shots_last5            SMALLINT,
    xg_last5               REAL,
    toi_last5_seconds      INTEGER,

    point_streak           SMALLINT,
    goal_streak            SMALLINT,
    last_game_id           BIGINT,

    PRIMARY KEY (snapshot_date, player_id)
);
