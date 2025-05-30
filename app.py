from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",          # Replace with your MySQL user
            password="HellBorn",  # Replace with your MySQL password
            database="grim_db"    # Your database name
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# ------------------- Existing Routes -------------------

# Route to display all players and related data
@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Fetch all players with the correct column names
            cursor.execute('SELECT player_id, email, created_at, updated_at FROM Players')
            players = cursor.fetchall()
            return render_template('index.html', players=players)
        except Error as e:
            flash(f"Error fetching players: {e}", "error")
            return render_template('index.html', players=[])
        finally:
            cursor.close()
            conn.close()
    else:
        flash("Error connecting to the database.", "error")
        return render_template('index.html', players=[])

# Route to add a new player
@app.route('/add_player', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        emergency_name = request.form.get('emergency_name', '').strip()
        emergency_relationship = request.form.get('emergency_relationship', '').strip()
        emergency_phone = request.form.get('emergency_phone', '').strip()
        medical = request.form.get('medical', '').strip()

        if not first_name or not last_name or not email:
            flash("First Name, Last Name, and Email are required!", "error")
            return redirect(url_for('add_player'))

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                insert_query = '''
                    INSERT INTO Players (first_name, last_name, email, phone, emergency_name, emergency_relationship, emergency_phone, medical, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                '''
                now = datetime.now()
                cursor.execute(insert_query, (first_name, last_name, email, phone, emergency_name, emergency_relationship, emergency_phone, medical, now, now))
                conn.commit()
                flash(f"Player '{first_name} {last_name}' added successfully!", "success")
            except Error as e:
                flash(f"Error adding player: {e}", "error")
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('index'))
        else:
            flash("Error connecting to the database.", "error")
            return redirect(url_for('add_player'))
    return render_template('add_player.html')

# Existing routes: add_player, checkin_player, checkout_player, delete_player
# ... (as previously provided)

# ------------------- New Routes for Expansion -------------------

# 1. Add Character
@app.route('/add_character', methods=['GET', 'POST'])
def add_character():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        player_id = request.form.get('player_id')
        race_id = request.form.get('race_id')
        archetype_id = request.form.get('archetype_id')
        name = request.form.get('name')
        gold = request.form.get('gold')
        silver = request.form.get('silver')
        copper = request.form.get('copper')

        if not player_id or not race_id or not archetype_id or not name:
            flash("Player, Race, Archetype, and Character Name are required!", "error")
            return redirect(url_for('add_character'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO Characters (player_id, race_id, archetype_id, name, gold, silver, copper)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (player_id, race_id, archetype_id, name, gold, silver, copper))
            conn.commit()
            flash(f"Character '{name}' added successfully!", "success")
        except Error as e:
            flash(f"Error adding character: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT player_id, first_name, last_name FROM Players')
        players = cursor.fetchall()

        cursor.execute('SELECT race_id, name FROM Races')
        races = cursor.fetchall()

        cursor.execute('SELECT archetype_id, name FROM Archetypes')
        archetypes = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('add_character.html', players=players, races=races, archetypes=archetypes)

# 2. Add Item
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        character_id = request.form.get('character_id')
        item_type_id = request.form.get('item_type_id')
        name = request.form.get('name')
        description = request.form.get('description')
        quantity = request.form.get('quantity', 1)

        if not character_id or not item_type_id or not name:
            flash("Character, Item Type, and Item Name are required!", "error")
            return redirect(url_for('add_item'))

        try:
            cursor = conn.cursor()
            insert_item_query = '''
                INSERT INTO Items (item_type_id, name, description)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_item_query, (item_type_id, name, description))
            item_id = cursor.lastrowid

            insert_character_item_query = '''
                INSERT INTO Character_Items (character_id, item_id, quantity)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_character_item_query, (character_id, item_id, quantity))
            conn.commit()
            flash(f"Item '{name}' added successfully!", "success")
        except Error as e:
            flash(f"Error adding item: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT character_id, name AS character_name FROM Characters')
        characters = cursor.fetchall()

        cursor.execute('SELECT item_type_id, name FROM Item_Types')
        item_types = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('add_item.html', characters=characters, item_types=item_types)

# 3. Add Event
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name')
        start = request.form.get('start')
        end = request.form.get('end')

        # Debugging statements
        print(f"Name: {name}")
        print(f"Start: {start}")
        print(f"End: {end}")

        if not name or not start or not end:
            flash("All fields are required!", "error")
            return redirect(url_for('add_event'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO Events (name, start, end)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_query, (name, start, end))
            conn.commit()
            flash(f"Event '{name}' added successfully!", "success")
        except Error as e:
            flash(f"Error adding event: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    return render_template('add_event.html')

# 4. Add Attendance
@app.route('/add_attendance', methods=['GET', 'POST'])
def add_attendance():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        player_id = request.form.get('player_id')
        event_id = request.form.get('event_id')
        check_in_time = request.form.get('check_in_time')
        check_out_time = request.form.get('check_out_time')  # Optional

        if not player_id or not event_id or not check_in_time:
            flash("Player, Event, and Check-In Time are required!", "error")
            return redirect(url_for('add_attendance'))

        try:
            # Optional: Validate datetime formats
            if check_out_time:
                check_out_time = datetime.strptime(check_out_time, '%Y-%m-%d %H:%M:%S')
            else:
                check_out_time = None
        except ValueError:
            flash("Invalid datetime format. Use YYYY-MM-DD HH:MM:SS", "error")
            return redirect(url_for('add_attendance'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO Attendance (player_id, event_id, check_in_time, check_out_time)
                VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (player_id, event_id, check_in_time, check_out_time))
            conn.commit()
            flash("Attendance record added successfully!", "success")
        except Error as e:
            flash(f"Error adding attendance: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    # GET request: Fetch all players and events to select from
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT player_id, username FROM Players')
        players = cursor.fetchall()

        cursor.execute('SELECT event_id, event_name FROM Events')
        events = cursor.fetchall()

        return render_template('add_attendance.html', players=players, events=events)
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

# 5. Add AP Earned
@app.route('/add_apearned', methods=['GET', 'POST'])
def add_apearned():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        player_id = request.form.get('player_id')
        ap_date = request.form.get('ap_date')
        ap_amount = request.form.get('ap_amount', '1').strip()

        if not player_id or not ap_date:
            flash("Player and AP Date are required!", "error")
            return redirect(url_for('add_apearned'))

        try:
            ap_amount = int(ap_amount)
            if ap_amount < 1:
                raise ValueError
        except ValueError:
            flash("AP Amount must be a positive integer.", "error")
            return redirect(url_for('add_apearned'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO APEarned (player_id, ap_date, ap_amount)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_query, (player_id, ap_date, ap_amount))
            conn.commit()
            flash("AP earned record added successfully!", "success")
        except Error as e:
            flash(f"Error adding AP earned: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    # GET request: Fetch all players to select from
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT player_id, username FROM Players')
        players = cursor.fetchall()
        return render_template('add_apearned.html', players=players)
    except Error as e:
        flash(f"Error fetching players: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

# 6. Assign AP to Character
@app.route('/assign_ap', methods=['GET', 'POST'])
def assign_ap():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        player_id = request.form.get('player_id')
        character_id = request.form.get('character_id')
        quantity = request.form.get('quantity')
        reason = request.form.get('reason')

        if not player_id or not character_id or not quantity:
            flash("Player, Character, and Quantity are required!", "error")
            return redirect(url_for('assign_ap'))

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            flash("Quantity must be a positive integer.", "error")
            return redirect(url_for('assign_ap'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO ap_assignment (player_id, character_id, quantity, reason)
                VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (player_id, character_id, quantity, reason))
            conn.commit()
            flash("AP assigned successfully!", "success")
        except Error as e:
            flash(f"Error assigning AP: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT player_id, first_name, last_name FROM Players')
        players = cursor.fetchall()

        cursor.execute('SELECT character_id, name AS character_name FROM Characters')
        characters = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('assign_ap.html', players=players, characters=characters)

# 7. Add AP
@app.route('/add_ap', methods=['GET', 'POST'])
def add_ap():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        player_id = request.form.get('player_id')
        quantity = request.form.get('quantity')
        reason = request.form.get('reason')

        if not player_id or not quantity:
            flash("Player and Quantity are required!", "error")
            return redirect(url_for('add_ap'))

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            flash("Quantity must be a positive integer.", "error")
            return redirect(url_for('add_ap'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO ap_creation (player_id, quantity, reason)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_query, (player_id, quantity, reason))
            conn.commit()
            flash("AP added successfully!", "success")
        except Error as e:
            flash(f"Error adding AP: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT player_id, first_name, last_name FROM Players')
        players = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching players: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('add_ap.html', players=players)

# ------------------- Existing Routes -------------------
# (Check-in, Check-out, Delete Player)
# ... (as previously provided)

@app.route('/delete_player/<int:id>', methods=['POST'])
def delete_player(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM Players WHERE player_id = %s', (id,))
            conn.commit()
            flash('Player deleted successfully!', 'success')
        except Error as e:
            flash(f'Error deleting player: {e}', 'error')
        finally:
            cursor.close()
            conn.close()
    else:
        flash('Error connecting to the database.', 'error')
    return redirect(url_for('index'))

@app.route('/edit_player/<int:id>', methods=['GET', 'POST'])
def edit_player(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        emergency_name = request.form.get('emergency_name', '').strip()
        emergency_relationship = request.form.get('emergency_relationship', '').strip()
        emergency_phone = request.form.get('emergency_phone', '').strip()
        medical = request.form.get('medical', '').strip()

        if not first_name or not last_name or not email:
            flash("First Name, Last Name, and Email are required!", "error")
            return redirect(url_for('edit_player', id=id))

        try:
            cursor = conn.cursor()
            update_query = '''
                UPDATE Players
                SET first_name = %s, last_name = %s, email = %s, phone = %s, emergency_name = %s, emergency_relationship = %s, emergency_phone = %s, medical = %s, updated_at = %s
                WHERE player_id = %s
            '''
            now = datetime.now()
            cursor.execute(update_query, (first_name, last_name, email, phone, emergency_name, emergency_relationship, emergency_phone, medical, now, id))
            conn.commit()
            flash(f"Player '{first_name} {last_name}' updated successfully!", "success")
        except Error as e:
            flash(f"Error updating player: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Players WHERE player_id = %s', (id,))
        player = cursor.fetchone()
        if player is None:
            flash("Player not found.", "error")
            return redirect(url_for('index'))
    except Error as e:
        flash(f"Error fetching player: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_player.html', player=player)

@app.route('/view_player/<int:id>', methods=['GET'])
def view_player(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_players'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT player_id, first_name, last_name, email, phone, emergency_name, emergency_relationship, emergency_phone, medical, created_at, updated_at
            FROM Players
            WHERE player_id = %s
        ''', (id,))
        player = cursor.fetchone()
        if player is None:
            flash("Player not found.", "error")
            return redirect(url_for('view_players'))

        cursor.execute('''
            SELECT c.character_id, c.name AS character_name, r.name AS race_name, a.name AS archetype_name, c.gold, c.silver, c.copper
            FROM Characters c
            JOIN Races r ON c.race_id = r.race_id
            JOIN Archetypes a ON c.archetype_id = a.archetype_id
            WHERE c.player_id = %s
        ''', (id,))
        characters = cursor.fetchall()

        cursor.execute('''
            SELECT ap_c_id, quantity, reason, created_at
            FROM ap_creation
            WHERE player_id = %s
            ORDER BY created_at DESC
        ''', (id,))
        ap_log = cursor.fetchall()

        cursor.execute('''
            SELECT SUM(quantity) AS total_ap
            FROM ap_creation
            WHERE player_id = %s
        ''', (id,))
        total_ap = cursor.fetchone()['total_ap'] or 0

        cursor.execute('''
            SELECT SUM(aa.quantity) AS total_assigned_ap
            FROM ap_assignment aa
            JOIN Characters c ON aa.character_id = c.character_id
            WHERE c.player_id = %s
        ''', (id,))
        total_assigned_ap = cursor.fetchone()['total_assigned_ap'] or 0
    except Error as e:
        flash(f"Error fetching player data: {e}", "error")
        return redirect(url_for('view_players'))
    finally:
        cursor.close()
        conn.close()

    return render_template('view_player.html', player=player, characters=characters, ap_log=ap_log, total_ap=total_ap, total_assigned_ap=total_assigned_ap)

@app.route('/view_characters', methods=['GET'])
def view_characters():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT c.character_id, c.name AS character_name, p.first_name, p.last_name, r.name AS race_name, a.name AS archetype_name, c.gold, c.silver, c.copper
            FROM Characters c
            JOIN Players p ON c.player_id = p.player_id
            JOIN Races r ON c.race_id = r.race_id
            JOIN Archetypes a ON c.archetype_id = a.archetype_id
        ''')
        characters = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching characters: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('view_characters.html', characters=characters)

@app.route('/delete_character/<int:id>', methods=['POST'])
def delete_character(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_characters'))

    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Characters WHERE character_id = %s', (id,))
        conn.commit()
        flash('Character deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting character: {e}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_characters'))

@app.route('/view_character/<int:id>', methods=['GET'])
def view_character(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_characters'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT c.character_id, c.name AS character_name, p.first_name, p.last_name, r.name AS race_name, a.name AS archetype_name, c.gold, c.silver, c.copper, c.character_sheet
            FROM Characters c
            JOIN Players p ON c.player_id = p.player_id
            JOIN Races r ON c.race_id = r.race_id
            JOIN Archetypes a ON c.archetype_id = a.archetype_id
            WHERE c.character_id = %s
        ''', (id,))
        character = cursor.fetchone()
        if character is None:
            flash("Character not found.", "error")
            return redirect(url_for('view_characters'))

        cursor.execute('''
            SELECT ci.character_item_id, i.name AS item_name, i.description, ci.quantity
            FROM Character_Items ci
            JOIN Items i ON ci.item_id = i.item_id
            WHERE ci.character_id = %s
        ''', (id,))
        items = cursor.fetchall()

        cursor.execute('''
            SELECT ap_a_id, quantity, reason, assigned_at
            FROM ap_assignment
            WHERE character_id = %s
            ORDER BY assigned_at DESC
        ''', (id,))
        ap_log = cursor.fetchall()

        cursor.execute('''
            SELECT SUM(quantity) AS total_ap
            FROM ap_assignment
            WHERE character_id = %s
        ''', (id,))
        total_ap = cursor.fetchone()['total_ap'] or 0
    except Error as e:
        flash(f"Error fetching character data: {e}", "error")
        return redirect(url_for('view_characters'))
    finally:
        cursor.close()
        conn.close()

    return render_template('view_character.html', character=character, items=items, ap_log=ap_log, total_ap=total_ap)

@app.route('/edit_character/<int:id>', methods=['GET', 'POST'])
def edit_character(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_characters'))

    if request.method == 'POST':
        player_id = request.form.get('player_id')
        race_id = request.form.get('race_id')
        archetype_id = request.form.get('archetype_id')
        name = request.form.get('name')
        gold = request.form.get('gold')
        silver = request.form.get('silver')
        copper = request.form.get('copper')

        if not player_id or not race_id or not archetype_id or not name:
            flash("Player, Race, Archetype, and Character Name are required!", "error")
            return redirect(url_for('edit_character', id=id))

        try:
            cursor = conn.cursor()
            update_query = '''
                UPDATE Characters
                SET player_id = %s, race_id = %s, archetype_id = %s, name = %s, gold = %s, silver = %s, copper = %s
                WHERE character_id = %s
            '''
            cursor.execute(update_query, (player_id, race_id, archetype_id, name, gold, silver, copper, id))
            conn.commit()
            flash(f"Character '{name}' updated successfully!", "success")
        except Error as e:
            flash(f"Error updating character: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('view_characters'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Characters WHERE character_id = %s', (id,))
        character = cursor.fetchone()

        cursor.execute('SELECT player_id, first_name, last_name FROM Players')
        players = cursor.fetchall()

        cursor.execute('SELECT race_id, name FROM Races')
        races = cursor.fetchall()

        cursor.execute('SELECT archetype_id, name FROM Archetypes')
        archetypes = cursor.fetchall()

        if character is None:
            flash("Character not found.", "error")
            return redirect(url_for('view_characters'))
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('view_characters'))
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_character.html', character=character, players=players, races=races, archetypes=archetypes)

@app.route('/edit_character_item/<int:id>', methods=['GET', 'POST'])
def edit_character_item(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_characters'))

    if request.method == 'POST':
        quantity = request.form.get('quantity')

        if not quantity:
            flash("Quantity is required!", "error")
            return redirect(url_for('edit_character_item', id=id))

        try:
            cursor = conn.cursor()
            update_query = '''
                UPDATE Character_Items
                SET quantity = %s
                WHERE character_item_id = %s
            '''
            cursor.execute(update_query, (quantity, id))
            conn.commit()
            flash("Item updated successfully!", "success")
        except Error as e:
            flash(f"Error updating item: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('view_characters'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT ci.character_item_id, i.name AS item_name, ci.quantity
            FROM Character_Items ci
            JOIN Items i ON ci.item_id = i.item_id
            WHERE ci.character_item_id = %s
        ''', (id,))
        character_item = cursor.fetchone()
        if character_item is None:
            flash("Item not found.", "error")
            return redirect(url_for('view_characters'))
    except Error as e:
        flash(f"Error fetching item: {e}", "error")
        return redirect(url_for('view_characters'))
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_character_item.html', character_item=character_item)

@app.route('/delete_character_item/<int:id>', methods=['POST'])
def delete_character_item(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_characters'))

    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Character_Items WHERE character_item_id = %s', (id,))
        conn.commit()
        flash('Item deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting item: {e}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_characters'))

@app.route('/move_character_item/<int:id>', methods=['GET', 'POST'])
def move_character_item(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_characters'))

    if request.method == 'POST':
        target_character_id = request.form.get('target_character_id')

        if not target_character_id:
            flash("Target character is required!", "error")
            return redirect(url_for('move_character_item', id=id))

        try:
            cursor = conn.cursor()
            update_query = '''
                UPDATE Character_Items
                SET character_id = %s
                WHERE character_item_id = %s
            '''
            cursor.execute(update_query, (target_character_id, id))
            conn.commit()
            flash("Item moved successfully!", "success")
        except Error as e:
            flash(f"Error moving item: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('view_characters'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT character_item_id, character_id FROM Character_Items WHERE character_item_id = %s', (id,))
        character_item = cursor.fetchone()

        cursor.execute('SELECT character_id, name AS character_name FROM Characters')
        characters = cursor.fetchall()

        if character_item is None:
            flash("Item not found.", "error")
            return redirect(url_for('view_characters'))
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('view_characters'))
    finally:
        cursor.close()
        conn.close()

    return render_template('move_character_item.html', character_item=character_item, characters=characters)

@app.route('/view_events', methods=['GET'])
def view_events():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT event_id, name, start, end FROM Events')
        events = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching events: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('view_events.html', events=events)

@app.route('/view_event/<int:id>', methods=['GET'])
def view_event(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_events'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT event_id, name, start, end FROM Events WHERE event_id = %s', (id,))
        event = cursor.fetchone()
        if event is None:
            flash("Event not found.", "error")
            return redirect(url_for('view_events'))

        cursor.execute('''
            SELECT ci.checkins_id, ci.timestamp AS checkin_time, co.timestamp AS checkout_time, 
                   p.player_id, p.first_name, p.last_name, 
                   c.character_id, c.name AS character_name
            FROM Checkins ci
            LEFT JOIN Checkouts co ON ci.event_id = co.event_id AND ci.player_id = co.player_id AND ci.character_id = co.character_id
            JOIN Players p ON ci.player_id = p.player_id
            JOIN Characters c ON ci.character_id = c.character_id
            WHERE ci.event_id = %s
        ''', (id,))
        checkins = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching event or check-in data: {e}", "error")
        return redirect(url_for('view_events'))
    finally:
        cursor.close()
        conn.close()

    return render_template('view_event.html', event=event, checkins=checkins)

@app.route('/edit_event/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_events'))

    if request.method == 'POST':
        name = request.form.get('name')
        start = request.form.get('start')
        end = request.form.get('end')

        if not name or not start or not end:
            flash("All fields are required!", "error")
            return redirect(url_for('edit_event', id=id))

        try:
            cursor = conn.cursor()
            update_query = '''
                UPDATE Events
                SET name = %s, start = %s, end = %s
                WHERE event_id = %s
            '''
            cursor.execute(update_query, (name, start, end, id))
            conn.commit()
            flash(f"Event '{name}' updated successfully!", "success")
        except Error as e:
            flash(f"Error updating event: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('view_events'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM Events WHERE event_id = %s', (id,))
        event = cursor.fetchone()
        if event is None:
            flash("Event not found.", "error")
            return redirect(url_for('view_events'))
    except Error as e:
        flash(f"Error fetching event: {e}", "error")
        return redirect(url_for('view_events'))
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_event.html', event=event)

@app.route('/delete_event/<int:id>', methods=['POST'])
def delete_event(id):
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('view_events'))

    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Events WHERE event_id = %s', (id,))
        conn.commit()
        flash('Event deleted successfully!', 'success')
    except Error as e:
        flash(f'Error deleting event: {e}', 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('view_events'))

@app.route('/checkin', methods=['GET', 'POST'])
def checkin():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        event_id = request.form.get('event_id')
        player_id = request.form.get('player_id')
        character_id = request.form.get('character_id')
        copper = request.form.get('copper')
        silver = request.form.get('silver')
        gold = request.form.get('gold')
        timestamp = datetime.now()

        if not event_id or not player_id or not character_id:
            flash("Event, Player, and Character are required!", "error")
            return redirect(url_for('checkin'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO Checkins (event_id, player_id, character_id, copper, silver, gold, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (event_id, player_id, character_id, copper, silver, gold, timestamp))
            conn.commit()
            flash("Check-in recorded successfully!", "success")
        except Error as e:
            flash(f"Error recording check-in: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT event_id, name FROM Events')
        events = cursor.fetchall()

        cursor.execute('SELECT player_id, first_name, last_name FROM Players')
        players = cursor.fetchall()

        cursor.execute('SELECT character_id, name AS character_name FROM Characters')
        characters = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('checkin.html', events=events, players=players, characters=characters)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        event_id = request.form.get('event_id')
        player_id = request.form.get('player_id')
        character_id = request.form.get('character_id')
        copper = request.form.get('copper')
        silver = request.form.get('silver')
        gold = request.form.get('gold')
        timestamp = datetime.now()

        if not event_id or not player_id or not character_id:
            flash("Event, Player, and Character are required!", "error")
            return redirect(url_for('checkout'))

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute('SELECT name, start, end FROM Events WHERE event_id = %s', (event_id,))
            event = cursor.fetchone()
            if not event:
                flash("Event not found.", "error")
                return redirect(url_for('checkout'))

            # Calculate days attended
            start_date = event['start']
            end_date = event['end']
            days_attended = (end_date - start_date).days + 1
            ap_earned = days_attended

            # Insert checkout record
            insert_checkout_query = '''
                INSERT INTO Checkouts (event_id, player_id, character_id, copper, silver, gold, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_checkout_query, (event_id, player_id, character_id, copper, silver, gold, timestamp))

            # Insert AP earned record
            reason = f"{event['name']} - {days_attended} days attended"
            insert_ap_query = '''
                INSERT INTO ap_creation (player_id, quantity, reason)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_ap_query, (player_id, ap_earned, reason))

            conn.commit()
            flash("Check-out recorded successfully and AP earned!", "success")
        except Error as e:
            flash(f"Error recording check-out or AP: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT event_id, name FROM Events')
        events = cursor.fetchall()

        cursor.execute('SELECT player_id, first_name, last_name FROM Players')
        players = cursor.fetchall()

        cursor.execute('SELECT character_id, name AS character_name FROM Characters')
        characters = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

    return render_template('checkout.html', events=events, players=players, characters=characters)

if __name__ == '__main__':
    app.run(debug=True)
