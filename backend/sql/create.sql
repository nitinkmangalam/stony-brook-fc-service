-- Players table - stores player information and statistics
CREATE TABLE players (
    player_id SERIAL PRIMARY KEY,
    player_name VARCHAR(100) NOT NULL,
    -- matches_played INT DEFAULT 0,
    -- wins INT DEFAULT 0,
    -- draws INT DEFAULT 0,
    -- losses INT DEFAULT 0,
    -- goals_scored INT DEFAULT 0,
    -- goals_against INT DEFAULT 0,
    -- goal_difference INT GENERATED ALWAYS AS (goals_scored - goals_against) STORED,
    -- clean_sheets INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matches table - stores both scheduled and completed matches
CREATE TABLE matches (
    id SERIAL PRIMARY KEY,
    round VARCHAR(50) NOT NULL,
    match_type VARCHAR(10) CHECK (match_type IN ('1v1', '2v2')),
    team1_player1_id INT REFERENCES players(player_id),
    team1_player2_id INT REFERENCES players(player_id), -- NULL for 1v1
    team2_player1_id INT REFERENCES players(player_id),
    team2_player2_id INT REFERENCES players(player_id), -- NULL for 1v1
    match_date TIMESTAMP NOT NULL,
    scheduled_date TIMESTAMP NOT NULL,
    team1_goals INT, -- NULL for scheduled matches
    team2_goals INT, -- NULL for scheduled matches
    result VARCHAR(50), -- 'Team1', 'Team2', or 'Draw', NULL for scheduled matches
    status VARCHAR(20) DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'COMPLETED', 'CANCELLED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Match statistics table - for detailed match statistics
CREATE TABLE match_stats (
    id SERIAL PRIMARY KEY,
    match_id INT REFERENCES matches(id) ON DELETE CASCADE,
    player_id INT REFERENCES players(player_id),
    goals INT DEFAULT 0,
    clean_sheet BOOLEAN DEFAULT FALSE,
    points INT DEFAULT 0, -- Points earned in this match
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_round ON matches(round);
CREATE INDEX idx_match_stats_player ON match_stats(player_id);

-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to maintain updated_at
CREATE TRIGGER update_players_timestamp
    BEFORE UPDATE ON players
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_matches_timestamp
    BEFORE UPDATE ON matches
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Function to update player statistics when a match is completed
CREATE OR REPLACE FUNCTION update_player_stats()
RETURNS TRIGGER AS $func$
BEGIN
    IF NEW.status = 'COMPLETED' AND OLD.status = 'SCHEDULED' THEN
        -- Team 1 player 1
        INSERT INTO match_stats (match_id, player_id, goals, clean_sheet, points)
        VALUES (
            NEW.id, 
            NEW.team1_player1_id, 
            NEW.team1_goals,
            CASE WHEN NEW.team2_goals = 0 THEN TRUE ELSE FALSE END,
            CASE 
                WHEN NEW.team1_goals > NEW.team2_goals THEN 6 
                WHEN NEW.team1_goals = NEW.team2_goals THEN 2
                ELSE 0 
            END
        );

        -- Team 2 player 1
        INSERT INTO match_stats (match_id, player_id, goals, clean_sheet, points)
        VALUES (
            NEW.id, 
            NEW.team2_player1_id, 
            NEW.team2_goals,
            CASE WHEN NEW.team1_goals = 0 THEN TRUE ELSE FALSE END,
            CASE 
                WHEN NEW.team2_goals > NEW.team1_goals THEN 6
                WHEN NEW.team2_goals = NEW.team1_goals THEN 2
                ELSE 0 
            END
        );
    END IF;
    RETURN NEW;
END;
$func$ LANGUAGE plpgsql;

-- Trigger for updating player stats when match is completed
CREATE TRIGGER update_match_stats
    AFTER UPDATE ON matches
    FOR EACH ROW
    EXECUTE FUNCTION update_player_stats();