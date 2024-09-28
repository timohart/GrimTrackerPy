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
            # Fetch all players
            cursor.execute('SELECT * FROM Players')
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
        player_name = request.form.get('player_name', '').strip()
        email = request.form.get('email', '').strip()
        password_hash = request.form.get('password_hash', '').strip()  # Ideally, hash the password

        if not player_name or not email or not password_hash:
            flash("All fields are required!", "error")
            return redirect(url_for('add_player'))

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                insert_query = '''
                    INSERT INTO Players (username, email, password_hash)
                    VALUES (%s, %s, %s)
                '''
                cursor.execute(insert_query, (player_name, email, password_hash))
                conn.commit()
                flash(f"Player '{player_name}' added successfully!", "success")
            except Error as e:
                flash(f"Error adding player: {e}", "error")
            finally:
                cursor.close()
                conn.close()
            return redirect(url_for('index'))
        else:
            flash("Failed to connect to the database.", "error")
            return redirect(url_for('index'))
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
        character_name = request.form.get('character_name', '').strip()
        character_class = request.form.get('class', '').strip()
        gold = request.form.get('gold', '0').strip()
        silver = request.form.get('silver', '0').strip()
        copper = request.form.get('copper', '0').strip()

        if not player_id or not character_name or not character_class:
            flash("Player, Character Name, and Class are required!", "error")
            return redirect(url_for('add_character'))

        try:
            gold = int(gold)
            silver = int(silver)
            copper = int(copper)
        except ValueError:
            flash("Gold, Silver, and Copper must be integers.", "error")
            return redirect(url_for('add_character'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO Characters (player_id, character_name, class, gold, silver, copper)
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (player_id, character_name, character_class, gold, silver, copper))
            conn.commit()
            flash(f"Character '{character_name}' added successfully!", "success")
        except Error as e:
            flash(f"Error adding character: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    # GET request: Fetch all players to select from
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT player_id, username FROM Players')
        players = cursor.fetchall()
        return render_template('add_character.html', players=players)
    except Error as e:
        flash(f"Error fetching players: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

# 2. Add Item
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    conn = get_db_connection()
    if not conn:
        flash("Failed to connect to the database.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        character_id = request.form.get('character_id')
        item_name = request.form.get('item_name', '').strip()
        quantity = request.form.get('quantity', '1').strip()
        description = request.form.get('description', '').strip()

        if not character_id or not item_name:
            flash("Character and Item Name are required!", "error")
            return redirect(url_for('add_item'))

        try:
            quantity = int(quantity)
            if quantity < 1:
                raise ValueError
        except ValueError:
            flash("Quantity must be a positive integer.", "error")
            return redirect(url_for('add_item'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO Items (character_id, item_name, quantity, description)
                VALUES (%s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (character_id, item_name, quantity, description))
            conn.commit()
            flash(f"Item '{item_name}' added successfully!", "success")
        except Error as e:
            flash(f"Error adding item: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    # GET request: Fetch all characters to select from
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT character_id, character_name FROM Characters')
        characters = cursor.fetchall()
        return render_template('add_item.html', characters=characters)
    except Error as e:
        flash(f"Error fetching characters: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

# 3. Add Event
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        event_name = request.form.get('event_name', '').strip()
        description = request.form.get('description', '').strip()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        location = request.form.get('location', '').strip()

        if not event_name or not start_date or not end_date:
            flash("Event Name, Start Date, and End Date are required!", "error")
            return redirect(url_for('add_event'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO Events (event_name, description, start_date, end_date, location)
                VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(insert_query, (event_name, description, start_date, end_date, location))
            conn.commit()
            flash(f"Event '{event_name}' added successfully!", "success")
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
        ap_id = request.form.get('ap_id')
        character_id = request.form.get('character_id')
        assigned_ap = request.form.get('assigned_ap', '1').strip()

        if not ap_id or not character_id:
            flash("AP Earned Record and Character are required!", "error")
            return redirect(url_for('assign_ap'))

        try:
            assigned_ap = int(assigned_ap)
            if assigned_ap < 1:
                raise ValueError
        except ValueError:
            flash("Assigned AP must be a positive integer.", "error")
            return redirect(url_for('assign_ap'))

        try:
            cursor = conn.cursor()
            insert_query = '''
                INSERT INTO APAssignment (ap_id, character_id, assigned_ap)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(insert_query, (ap_id, character_id, assigned_ap))
            conn.commit()
            flash("AP assigned to character successfully!", "success")
        except Error as e:
            flash(f"Error assigning AP: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('index'))

    # GET request: Fetch all APEarned records and Characters to select from
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT ap_id, ap_date, ap_amount, player_id FROM APEarned')
        ap_records = cursor.fetchall()

        cursor.execute('SELECT character_id, character_name FROM Characters')
        characters = cursor.fetchall()

        return render_template('assign_ap.html', ap_records=ap_records, characters=characters)
    except Error as e:
        flash(f"Error fetching data: {e}", "error")
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()

# ------------------- Existing Routes -------------------
# (Check-in, Check-out, Delete Player)
# ... (as previously provided)

if __name__ == '__main__':
    app.run(debug=True)
