"""
Vibes TCG Tracker v2 - With Card Tracking & Archetype Detection
Flask backend with SQLite database
"""

from flask import Flask, render_template, request, jsonify, send_file
import psycopg
from psycopg.rows import dict_row
import json
import os
import csv
import io
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# Configuration - PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")

# ─────────────────────────────────────────────────────────────────────────────
# Card Database - All Vibes TCG Cards (from official card data)
# ─────────────────────────────────────────────────────────────────────────────

CARD_LIST = [
    "A Drop in Attention", "Absent-Minded Penguin", "Abstract Penguin", "Adventure Squad",
    "Again, Again", "Aha Penguin", "Amazing Penguin", "Ambitious Penguin",
    "An Offer You Can't Refuse", "Arches", "Ascending Penguin", "Balanced Penguin",
    "Bamboo Penguin", "Band Together", "Bashful Swordsman Penguin", "Be Big and Goofy",
    "Be Merry and Go", "Be Weird and Silly", "Be a Lil Evil", "Bearish Sentiment",
    "Becky Breaker", "Bedtime Story", "Best Seats in the House", "Binkus, Who Eats the Stars",
    "Bizmo, PhD Candidate", "Blizzby the Swift", "Blossoming Penguin", "Blue Mega Penguin",
    "Blue Wizard Penguin", "Boat-Tying Penguin", "Bottle Penguin", "Bounce House Rod",
    "Brainy Penguin", "Bridge With Layer Zero", "Bubbles, the Great and Powerful",
    "Buddy Up", "Build a Burrito", "Bunkus, Who Is the Stars", "Calligraphy Rod",
    "Cannonball Penguin", "Capture the Moment", "Carnival Penguin",
    "Chalice of Everflowing Pudge", "Change Perspective", "Charming Swordsman Penguin",
    "Chase Your Dreams", "Check the Yellow Pages", "Cheeky Sidequest", "Chef Penguin",
    "Chisel from Stone", "Chub, Who Lives for Action", "Chubopolis Unleashed",
    "Clean Up Good", "Colosseum", "Contemplation Penguin", "Cookies of Truth",
    "Cooking Penguin", "Cool Story Bro!", "Cross the River", "Curious Penguin",
    "Dashing Swordsman Penguin", "Daydreaming Penguin", "Demolition Penguin",
    "Dima the Destroyer", "Distract", "Do a Lil Math", "Don't Trust, Verify",
    "Dragonrider Penguin", "Dummy Thicc Disco Ball", "Dunk a Donut", "Easter Island",
    "Eiffel Tower", "Enter the Bounce House Dimension", "Escape in Time",
    "Everybody Stay Clam", "Extrovert Penguin", "Fact-Finding Penguin", "Feather Forecast",
    "Fishing Trip", "Flip a Flapjack", "Flop, Drop, and Roll", "Flower-Arranging Penguin",
    "Flying Penguin", "Force of Lil", "Four of a Kind", "Freezing Rod", "Frolic",
    "Frosterous the Great", "Frosty the Penguin", "Galaxy Penguin", "Gardenkeeper Penguin",
    "Gather Together", "Glass Act", "Glow and Behold", "Go With the Flow",
    "Goodnight, Pengs", "Got 'Em!", "Great Wall", "Green Mega Penguin",
    "Green Wizard Penguin", "Grow Together", "Half Past Chill",
    "Have a Philosophical Debate", "Have an Encore", "Heads I Win, Tails You Lose",
    "Here's Pengy", "Hit the High Note", "Honey, I Shrunk the Pengs", "Hot Rod",
    "Hungry Penguin", "Hyper Penguin", "Inconceivable!", "Ingenious Idea",
    "Inquisitive Penguin", "Insomniac Penguin", "Inspiring Story", "Into the Night",
    "Introvert Penguin", "Is This a Rod", "Jealous Penguin", "Jeepers!", "Join the Trend",
    "Josephine, Party Queen", "Jubilant Penguin", "Juggling Penguin", "Karate Penguin",
    "Keep Digging", "Keyturning Penguin", "Koi Penguin", "Layer Two Technology",
    "Layer a Lasagna", "Leaning Tower", "Lil Baker", "Lil Bamboo", "Lil Bellyacher",
    "Lil Chef", "Lil Comic", "Lil Contemplator", "Lil Daydreamer", "Lil Detective",
    "Lil Dragonrider", "Lil Drippy", "Lil Extrovert", "Lil Frosty", "Lil Gardenkeeper",
    "Lil Insomniac", "Lil Introvert", "Lil Jelly", "Lil Juggler", "Lil Leafrider",
    "Lil Lifeguard", "Lil Lodger", "Lil Lookout", "Lil Lucky", "Lil Milkmaid",
    "Lil Moonlight", "Lil Painter", "Lil Paper", "Lil Quaker", "Lil Raker", "Lil Rock",
    "Lil Scissors", "Lil Shaker", "Lil Singer", "Lil Skydiver", "Lil Solo Adventurer",
    "Lil Space Cadet", "Lil Stargazer", "Lil Surprised", "Lil Waker", "Lil Who Blooms",
    "Lil Who Breaks Free", "Lil Who Can't Stop Eating", "Lil Who Hoops", "Lil Who Scoops",
    "Lil Who Slides", "Lil Who's Down Bad", "Lil Window Washer", "Lil With Balloon",
    "Lil Zoomer", "Look Inside", "Lost in the Sauce", "Luca Saves the Penguins",
    "Lucky Penguin", "Marilyl", "Melt a Marshmallow", "Miss Chief, Keeper of Keys",
    "Miss Place, Forgetter of Things", "Miss Tweeny", "Moonlit Penguin", "Mount Fuji",
    "Mukbang Penguin", "Mysterious Penguin", "Mystery of the Everlasting Fish",
    "Napengulon, Legendary Host", "No Way!", "Not Today!", "Not Your Keys",
    "Not a Rod Anymore!", "Nyan Cat", "One With History", "Ooo, Shiny", "Opera House",
    "Orb of Hopium", "Ornate Swordsman Penguin", "Overwhelm With Fish",
    "Overwhelm With Knowledge", "Pack Attack", "Painter Penguin", "Paper Penguin",
    "Parasol Rod", "Peace Out Penguin", "Pebblington the Brave",
    "Penguin Caught in Fishing Line", "Penguin That Doesn't Mind Goodbyes",
    "Penguin Who Bakes", "Penguin Who Breaks the Fourth Wall",
    "Penguin Who Carries the Berg", "Penguin Who Explores the Reef",
    "Penguin Who Is the Garden", "Penguin Who Might Bring a Plus One",
    "Penguin Who Quakes", "Penguin Who Rakes", "Penguin Who Runs the Lift",
    "Penguin Who Shakes", "Penguin Who Spills the Tea", "Penguin Who Wakes",
    "Penguin Who Zooms", "Penguin Who's Late to the Party", "Penguin Who's OK",
    "Penguin Whose Belly Aches", "Penguin Whose Garden Grows",
    "Penguin With Great Mystique", "Penguin With Hoops", "Penguin With Lil Mystique",
    "Penguin With a Flag", "Penguin With a Rod of His Own", "Penguin in Color",
    "Penguin of the Falling Leaves", "Peppy Penguin", "Petite Pourer", "Phone Home",
    "Pleepem, Who Stands Alone", "Pointsrich Penguin", "Pongo", "Popcorn Penguin",
    "Poppin' Pete", "Porthole Penguin", "Pot-Stirring Penguin", "Potion Commotion",
    "Prepare for a Wild Night", "Primo Wizard Penguin", "Prosperous Penguin",
    "Pudgticate", "Pudgy Man Rod", "Purple Mega Penguin", "Purple Wizard Penguin",
    "Put Your Flippers in the Air", "Put on a Show", "Questionable Methods",
    "Rad Chill, Who's Super Cool", "Raid the Snacks", "Red Mega Penguin",
    "Red Wizard Penguin", "Ribbon-Dancing Penguin", "Ride the Train",
    "Risk-Taking Penguin", "Rock Penguin", "Rod of Camaraderie",
    "Rod of Charming Melodies", "Rod of Cheesy Slices", "Romulus Who Roams",
    "Run-It-Back Penguin", "Samantha Feathers, Pop Idol", "Scissors Penguin",
    "Screaming Penguin", "See the Berg", "Send It Too Hard", "Send Off",
    "Serene Penguin", "Shapenguzad", "Sheeeesh!", "Shocking Penguin", "Shy Penguin",
    "Sick Pull!", "Silent Snow Globe", "Simon Smasher", "Sir Vibesalil", "Sir Vibesalot",
    "Sir Waddlesworth", "Sketching Penguin", "Skydiving Penguin", "Sliding Penguin",
    "Sneaky Penguin", "Son of Lil", "Space Cadet Penguin", "Sphinx", "Spring Break",
    "Spring a Leak", "Squibblestone the Wise", "Stand in the Rain", "Stargazing Penguin",
    "Statue of Liberty", "Striking Swordsman Penguin", "Study All Night",
    "Success Penguin", "Sunburn a Penguin", "Supportive Friend", "Teleporter Penguin",
    "Thawing Penguin", "The Champion of Clouds", "The End of the Rainbow",
    "The Herald of Horizons", "The Lord of Lightning", "The Savior of Skies",
    "The Warden of Wind", "They're Twins", "Three Wise Penguins", "Throw Some Snow",
    "Tidal Penguin", "Tie Game", "Tina Who Tears", "Too Cool for School",
    "Too Much Caffeine", "Toss Up", "Trampoline Rod", "Trust Fall", "Tubbins the Bold",
    "Turn to Rod", "Umbrella Rod", "Unlikely Friends", "Unmasked Penguin",
    "Use Whoopee Cushion", "Walk the Runway", "Waterfall Penguin", "Wen?",
    "What a Twist!", "Win the Race", "Window-Washing Penguin", "Wizard Cap",
    "Wizard of Balloons", "Wizard of Dreams", "Wizard of Feathers", "Wizard of the Deep",
    "Wizard of the Void", "Wut?", "Yellow Mega Penguin", "Yellow Wizard Penguin",
    "You Dropped This", "Yum Yum", "liL mOCkeR"
]

# ─────────────────────────────────────────────────────────────────────────────
# Archetype Detection - Signature Cards for Each Deck Type
# ─────────────────────────────────────────────────────────────────────────────

ARCHETYPES = {
    "GMP Caffeine Colo": {
        "signature": ["Green Mega Penguin", "Too Much Caffeine", "Colosseum"],
        "supporting": ["Lil Bellyacher", "Lil Extrovert", "Mount Fuji", "Popcorn Penguin"],
        "weight": 3
    },
    "GMP Colo": {
        "signature": ["Green Mega Penguin", "Colosseum"],
        "supporting": ["Lil Bellyacher", "Lil Extrovert", "Lil Lookout", "Popcorn Penguin"],
        "weight": 2
    },
    "Red Removal": {
        "signature": ["Potion Commotion", "Not a Rod Anymore!", "Layer a Lasagna"],
        "supporting": ["Not Today!", "Lil Singer", "Silent Snow Globe", "Mount Fuji"],
        "weight": 3
    },
    "Red Control": {
        "signature": ["Potion Commotion", "Layer a Lasagna"],
        "supporting": ["Lil Moonlight", "Mount Fuji", "Inspiring Story", "Lil Singer"],
        "weight": 2
    },
    "Yellow Control": {
        "signature": ["Silent Snow Globe", "Bashful Swordsman Penguin"],
        "supporting": ["Serene Penguin", "Prosperous Penguin", "What a Twist!", "Heads I Win, Tails You Lose"],
        "weight": 2
    },
    "Bash Globe": {
        "signature": ["Bashful Swordsman Penguin", "Silent Snow Globe"],
        "supporting": ["Simon Smasher", "Lil Extrovert", "Toss Up"],
        "weight": 3
    },
    "Colo Bash Globe": {
        "signature": ["Colosseum", "Bashful Swordsman Penguin", "Silent Snow Globe"],
        "supporting": ["Green Mega Penguin", "Lil Bellyacher", "Simon Smasher"],
        "weight": 3
    },
    "Belly Colo": {
        "signature": ["Lil Bellyacher", "Colosseum", "Penguin Whose Belly Aches"],
        "supporting": ["Lil Extrovert", "Popcorn Penguin"],
        "weight": 3
    },
    "Yum Yum": {
        "signature": ["Yum Yum"],
        "supporting": ["Penguin Who Bakes", "Lil Baker", "Cooking Penguin"],
        "weight": 2
    },
    "Green Control": {
        "signature": ["Green Mega Penguin", "Inspiring Story"],
        "supporting": ["Mount Fuji", "Lil Moonlight", "Serene Penguin"],
        "weight": 2
    },
    "Green Aggro": {
        "signature": ["Green Mega Penguin", "Lil Zoomer", "Lil Extrovert"],
        "supporting": ["Too Much Caffeine", "Bounce House Rod"],
        "weight": 2
    },
    "GMP Aggro": {
        "signature": ["Green Mega Penguin", "Lil Zoomer"],
        "supporting": ["Too Much Caffeine", "Lil Extrovert", "Bounce House Rod"],
        "weight": 2
    },
    "Blue Mill": {
        "signature": ["Blue Mega Penguin", "Galaxy Penguin"],
        "supporting": ["Wizard of the Deep", "Blue Wizard Penguin"],
        "weight": 2
    },
    "Bizbunk": {
        "signature": ["Bizmo, PhD Candidate"],
        "supporting": ["Brainy Penguin", "Do a Lil Math"],
        "weight": 2
    },
    "Swordsman": {
        "signature": ["Bashful Swordsman Penguin", "Charming Swordsman Penguin", "Dashing Swordsman Penguin"],
        "supporting": ["Striking Swordsman Penguin", "Ornate Swordsman Penguin"],
        "weight": 3
    },
    "Purple Control": {
        "signature": ["Purple Mega Penguin", "Potion Commotion"],
        "supporting": ["Layer a Lasagna", "Wizard of the Void"],
        "weight": 2
    },
    "Wizard": {
        "signature": ["Wizard Cap", "Green Wizard Penguin"],
        "supporting": ["Blue Wizard Penguin", "Red Wizard Penguin", "Yellow Wizard Penguin", "Purple Wizard Penguin"],
        "weight": 2
    }
}

def detect_archetype(cards_seen):
    """
    Score each archetype based on cards seen.
    Returns list of (archetype, score, confidence) sorted by score.
    """
    if not cards_seen:
        return []
    
    cards_set = set(cards_seen)
    scores = []
    
    for archetype, data in ARCHETYPES.items():
        score = 0
        signature_hits = 0
        supporting_hits = 0
        
        # Signature cards are worth more
        for card in data["signature"]:
            if card in cards_set:
                score += 10
                signature_hits += 1
        
        # Supporting cards add smaller bonus
        for card in data["supporting"]:
            if card in cards_set:
                score += 3
                supporting_hits += 1
        
        # Apply archetype weight
        score *= data["weight"]
        
        # Calculate confidence based on signature card coverage
        if len(data["signature"]) > 0:
            confidence = (signature_hits / len(data["signature"])) * 100
        else:
            confidence = 0
        
        if score > 0:
            scores.append({
                "archetype": archetype,
                "score": score,
                "confidence": round(confidence),
                "signature_hits": signature_hits,
                "supporting_hits": supporting_hits
            })
    
    # Sort by score descending
    scores.sort(key=lambda x: x["score"], reverse=True)
    return scores

# ─────────────────────────────────────────────────────────────────────────────
# Database Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_db():
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    
    # Main matches table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS matches(
            id SERIAL PRIMARY KEY,
            date_time TEXT,
            my_deck TEXT,
            opp_name TEXT,
            opp_deck TEXT,
            result_match INTEGER,
            on_play_start INTEGER,
            notes TEXT
        );
    """)
    
    # Cards seen per match
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cards_seen(
            id SERIAL PRIMARY KEY,
            match_id INTEGER REFERENCES matches(id) ON DELETE CASCADE,
            card_name TEXT
        );
    """)
    
    # User's decklists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS decklists(
            id SERIAL PRIMARY KEY,
            name TEXT,
            cards TEXT,
            created_at TEXT,
            is_public INTEGER DEFAULT 0
        );
    """)
    
    # Create indexes if they don't exist
    cur.execute("CREATE INDEX IF NOT EXISTS idx_dt ON matches(date_time);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_my ON matches(my_deck);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_cards_match ON cards_seen(match_id);")
    
    conn.commit()
    cur.close()
    conn.close()

def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# ─────────────────────────────────────────────────────────────────────────────
# Routes - Pages
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

# ─────────────────────────────────────────────────────────────────────────────
# Routes - Card List & Archetype Detection
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/cards")
def get_cards():
    """Return all card names for autocomplete"""
    return jsonify(sorted(CARD_LIST))

@app.route("/api/archetypes")
def get_archetypes():
    """Return all archetype names"""
    return jsonify(sorted(ARCHETYPES.keys()))

@app.route("/api/detect-archetype", methods=["POST"])
def detect_archetype_api():
    """Detect archetype from list of cards seen"""
    cards = request.json.get("cards", [])
    results = detect_archetype(cards)
    return jsonify(results)

# ─────────────────────────────────────────────────────────────────────────────
# Routes - Matches API
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/matches", methods=["GET"])
def get_matches():
    conn = get_db()
    cur = conn.cursor()
    
    query = """
        SELECT id, date_time, my_deck, opp_name, opp_deck, 
               result_match, on_play_start, notes 
        FROM matches WHERE 1=1
    """
    params = []
    
    if request.args.get("date_from"):
        query += " AND date_time >= %s"
        params.append(request.args.get("date_from") + " 00:00")
    if request.args.get("date_to"):
        query += " AND date_time <= %s"
        params.append(request.args.get("date_to") + " 23:59")
    if request.args.get("my_deck"):
        query += " AND my_deck LIKE %s"
        params.append("%" + request.args.get("my_deck") + "%")
    if request.args.get("opp_deck"):
        query += " AND opp_deck LIKE %s"
        params.append("%" + request.args.get("opp_deck") + "%")
    if request.args.get("result") == "win":
        query += " AND result_match = 1"
    elif request.args.get("result") == "loss":
        query += " AND result_match = 0"
    
    query += " ORDER BY date_time DESC, id DESC"
    
    cur.execute(query, params)
    matches = [dict(row) for row in cur.fetchall()]
    
    # Get cards seen for each match
    for match in matches:
        cur.execute(
            "SELECT card_name FROM cards_seen WHERE match_id = %s",
            (match["id"],)
        )
        cards = cur.fetchall()
        match["cards_seen"] = [c["card_name"] for c in cards]
    
    cur.close()
    conn.close()
    return jsonify(matches)

@app.route("/api/matches", methods=["POST"])
def add_match():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO matches (date_time, my_deck, opp_name, opp_deck, result_match, on_play_start, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        now_iso(),
        data.get("my_deck", ""),
        data.get("opp_name", ""),
        data.get("opp_deck", ""),
        1 if data.get("result") == "win" else 0,
        data.get("on_play"),
        data.get("notes", "")
    ))
    
    match_id = cur.fetchone()["id"]
    
    # Insert cards seen
    cards_seen = data.get("cards_seen", [])
    for card in cards_seen:
        cur.execute(
            "INSERT INTO cards_seen (match_id, card_name) VALUES (%s, %s)",
            (match_id, card)
        )
    
    conn.commit()
    cur.close()
    conn.close()
    
    return jsonify({"success": True, "id": match_id})

@app.route("/api/matches/<int:match_id>", methods=["DELETE"])
def delete_match(match_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM cards_seen WHERE match_id = %s", (match_id,))
    cur.execute("DELETE FROM matches WHERE id = %s", (match_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/matches/<int:match_id>/cards", methods=["POST"])
def add_card_to_match(match_id):
    """Add a card to an existing match"""
    card_name = request.json.get("card_name")
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO cards_seen (match_id, card_name) VALUES (%s, %s)",
        (match_id, card_name)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/matches/<int:match_id>/cards/<card_name>", methods=["DELETE"])
def remove_card_from_match(match_id, card_name):
    """Remove a card from a match"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM cards_seen WHERE id = (SELECT id FROM cards_seen WHERE match_id = %s AND card_name = %s LIMIT 1)",
        (match_id, card_name)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

# ─────────────────────────────────────────────────────────────────────────────
# Routes - Stats & Analytics
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/stats")
def get_stats():
    conn = get_db()
    cur = conn.cursor()
    
    my_deck = request.args.get("my_deck")
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    
    where_clauses = []
    params = []
    
    if my_deck:
        where_clauses.append("my_deck = %s")
        params.append(my_deck)
    if date_from:
        where_clauses.append("date_time >= %s")
        params.append(date_from + " 00:00")
    if date_to:
        where_clauses.append("date_time <= %s")
        params.append(date_to + " 23:59")
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Overall stats
    cur.execute(f"SELECT COUNT(*) as count FROM matches WHERE {where_sql}", params)
    total = cur.fetchone()["count"]
    
    cur.execute(f"SELECT COUNT(*) as count FROM matches WHERE {where_sql} AND result_match = 1", params)
    wins = cur.fetchone()["count"]
    
    # Play/Draw stats
    cur.execute(f"SELECT COUNT(*) as count FROM matches WHERE {where_sql} AND on_play_start = 1", params)
    otp_total = cur.fetchone()["count"]
    
    cur.execute(f"SELECT COUNT(*) as count FROM matches WHERE {where_sql} AND on_play_start = 1 AND result_match = 1", params)
    otp_wins = cur.fetchone()["count"]
    
    cur.execute(f"SELECT COUNT(*) as count FROM matches WHERE {where_sql} AND on_play_start = 0", params)
    otd_total = cur.fetchone()["count"]
    
    cur.execute(f"SELECT COUNT(*) as count FROM matches WHERE {where_sql} AND on_play_start = 0 AND result_match = 1", params)
    otd_wins = cur.fetchone()["count"]
    
    # Matchup breakdown
    matchups_query = f"""
        SELECT opp_deck, 
               COUNT(*) as total,
               SUM(CASE WHEN result_match = 1 THEN 1 ELSE 0 END) as wins
        FROM matches 
        WHERE {where_sql} AND opp_deck != ''
        GROUP BY opp_deck
        ORDER BY total DESC
    """
    cur.execute(matchups_query, params)
    matchup_rows = cur.fetchall()
    matchups = []
    for row in matchup_rows:
        matchups.append({
            "opp_deck": row["opp_deck"],
            "total": row["total"],
            "wins": row["wins"],
            "losses": row["total"] - row["wins"],
            "win_rate": round(row["wins"] / row["total"] * 100, 1) if row["total"] > 0 else 0
        })
    
    cur.close()
    conn.close()
    
    return jsonify({
        "total": total,
        "wins": wins,
        "losses": total - wins,
        "win_rate": round(wins / total * 100, 1) if total > 0 else 0,
        "otp_total": otp_total,
        "otp_wins": otp_wins,
        "otp_win_rate": round(otp_wins / otp_total * 100, 1) if otp_total > 0 else 0,
        "otd_total": otd_total,
        "otd_wins": otd_wins,
        "otd_win_rate": round(otd_wins / otd_total * 100, 1) if otd_total > 0 else 0,
        "matchups": matchups
    })

@app.route("/api/analytics/cards-in-losses")
def cards_in_losses():
    """Cards most commonly seen in losses"""
    conn = get_db()
    cur = conn.cursor()
    my_deck = request.args.get("my_deck")
    
    query = """
        SELECT cs.card_name, COUNT(*) as count
        FROM cards_seen cs
        JOIN matches m ON cs.match_id = m.id
        WHERE m.result_match = 0
    """
    params = []
    
    if my_deck:
        query += " AND m.my_deck = %s"
        params.append(my_deck)
    
    query += " GROUP BY cs.card_name ORDER BY count DESC LIMIT 20"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{"card": r["card_name"], "count": r["count"]} for r in rows])

@app.route("/api/analytics/cards-in-wins")
def cards_in_wins():
    """Cards most commonly seen in wins"""
    conn = get_db()
    cur = conn.cursor()
    my_deck = request.args.get("my_deck")
    
    query = """
        SELECT cs.card_name, COUNT(*) as count
        FROM cards_seen cs
        JOIN matches m ON cs.match_id = m.id
        WHERE m.result_match = 1
    """
    params = []
    
    if my_deck:
        query += " AND m.my_deck = %s"
        params.append(my_deck)
    
    query += " GROUP BY cs.card_name ORDER BY count DESC LIMIT 20"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify([{"card": r["card_name"], "count": r["count"]} for r in rows])

@app.route("/api/analytics/winrate-vs-card")
def winrate_vs_card():
    """Win rate when opponent plays specific cards"""
    conn = get_db()
    cur = conn.cursor()
    my_deck = request.args.get("my_deck")
    
    query = """
        SELECT cs.card_name,
               COUNT(*) as total,
               SUM(CASE WHEN m.result_match = 1 THEN 1 ELSE 0 END) as wins
        FROM cards_seen cs
        JOIN matches m ON cs.match_id = m.id
    """
    params = []
    
    if my_deck:
        query += " WHERE m.my_deck = %s"
        params.append(my_deck)
    
    query += " GROUP BY cs.card_name HAVING COUNT(*) >= 3 ORDER BY COUNT(*) DESC"
    
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    results = []
    for r in rows:
        results.append({
            "card": r["card_name"],
            "total": r["total"],
            "wins": r["wins"],
            "losses": r["total"] - r["wins"],
            "win_rate": round(r["wins"] / r["total"] * 100, 1)
        })
    
    return jsonify(results)

# ─────────────────────────────────────────────────────────────────────────────
# Routes - Decklists
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/decklists", methods=["GET"])
def get_decklists():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM decklists ORDER BY created_at DESC")
    rows = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(rows)

@app.route("/api/decklists", methods=["POST"])
def add_decklist():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO decklists (name, cards, created_at, is_public)
        VALUES (%s, %s, %s, %s)
    """, (
        data.get("name", "Unnamed Deck"),
        json.dumps(data.get("cards", {})),
        now_iso(),
        1 if data.get("is_public") else 0
    ))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/decklists/<int:deck_id>", methods=["DELETE"])
def delete_decklist(deck_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM decklists WHERE id = %s", (deck_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/my-decks")
def get_my_deck_names():
    """Get list of deck names for dropdown"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name FROM decklists ORDER BY name")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([row["name"] for row in rows])

# ─────────────────────────────────────────────────────────────────────────────
# Routes - Session Stats
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/session")
def session_stats():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM matches 
        WHERE date_time >= %s
        ORDER BY date_time DESC, id DESC
    """, (today + " 00:00",))
    
    matches = [dict(row) for row in cur.fetchall()]
    cur.close()
    conn.close()
    
    wins = sum(1 for m in matches if m["result_match"] == 1)
    
    return jsonify({
        "matches": matches,
        "total": len(matches),
        "wins": wins,
        "losses": len(matches) - wins,
        "win_rate": round(wins / len(matches) * 100, 1) if matches else 0
    })

# ─────────────────────────────────────────────────────────────────────────────
# Routes - Export
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/export/csv")
def export_csv():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT date_time, my_deck, opp_name, opp_deck, result_match, on_play_start, notes
        FROM matches ORDER BY date_time DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "My Deck", "Opponent", "Their Deck", "Result", "On Play", "Notes"])
    
    for row in rows:
        writer.writerow([
            row["date_time"],
            row["my_deck"],
            row["opp_name"],
            row["opp_deck"],
            "Win" if row["result_match"] == 1 else "Loss",
            "Yes" if row["on_play_start"] == 1 else "No" if row["on_play_start"] == 0 else "Unknown",
            row["notes"]
        ])
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"vibes_matches_{datetime.now().strftime('%Y%m%d')}.csv"
    )

# ─────────────────────────────────────────────────────────────────────────────
# Initialize and Run
# ─────────────────────────────────────────────────────────────────────────────

# Always initialize DB (required for gunicorn on Railway)
init_db()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
