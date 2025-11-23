import connexion
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os
from datetime import datetime

# ==============================================================================
#  CONFIGURACIÓN
# ==============================================================================
# URL del servicio de Contenidos 
CONTENT_SERVICE_URL = os.getenv("CONTENT_SERVICE_URL", "http://localhost:8081")

# Parámetros de conexión a la base de datos PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5435") # Puerto externo del docker
DB_NAME = os.getenv("DB_NAME", "recomendaciones_db")
DB_USER = os.getenv("DB_USER", "usuario")
DB_PASS = os.getenv("DB_PASS", "123454321")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        return conn
    except Exception as e:
        print(f"--> [ERROR CRÍTICO] DB Connection: {e}")
        return None

# ==============================================================================
#  HELPER: COMUNICACIÓN
# ==============================================================================
def _fetch_from_content(endpoint):
    """Pide datos a Contenidos (Síncrono)"""
    try:
        url = f"{CONTENT_SERVICE_URL}{endpoint}"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"--> [ERROR HTTP] Fallo comunicación Contenidos ({endpoint}): {e}")
    return None

# ==============================================================================
#  BLOQUE 1: INGESTIÓN DE DATOS (WRITES)
# ==============================================================================

def add_play(body):  
    """Registra una reproducción usando la secuencia de PostgreSQL."""
    if connexion.request.is_json:
        play = body 
        conn = get_db_connection()
        if not conn: return "DB Connection Error", 500
        
        cur = conn.cursor()
        try:
            # SQL: Usamos nextval('plays_id_seq') para generar el ID de forma segura y atómica
            # Si tu tabla se llama 'plays' y la secuencia 'plays_id_seq' (estándar en tu init.sql)
            cur.execute("""
                INSERT INTO plays (id, user_id, track_id, timestamp)
                VALUES (nextval('public.plays_id_seq'), %s, %s, %s)
            """, (play['user_id'], play['track_id'], datetime.now()))
            
            conn.commit()
            print(f"--> [DB] Play guardado: User {play['user_id']} -> Track {play['track_id']}")
        except Exception as e:
            conn.rollback()
            print(f"--> [ERROR SQL] {e}")
            return "Error saving play", 500
        finally:
            cur.close()
            conn.close()
        
    return "Play registered", 201


def add_like(body): 
    """Registra un like usando la secuencia de PostgreSQL."""
    if connexion.request.is_json:
        like = body
        conn = get_db_connection()
        if not conn: return "DB Connection Error", 500
        
        cur = conn.cursor()
        try:
            # SQL: Usamos nextval('likes_id_seq')
            cur.execute("""
                INSERT INTO likes (id, user_id, track_id, timestamp)
                VALUES (nextval('public.likes_id_seq'), %s, %s, %s)
                ON CONFLICT (user_id, track_id) DO NOTHING
            """, (like['user_id'], like['track_id'], datetime.now()))
            
            conn.commit()
            print(f"--> [DB] Like guardado: User {like['user_id']} -> Track {like['track_id']}")
        except Exception as e:
            conn.rollback()
            print(f"--> [ERROR SQL] {e}")
            return "Error saving like", 500
        finally:
            cur.close()
            conn.close()

    return "Like registered", 201


# ==============================================================================
#  BLOQUE 2: MÉTRICAS Y RECOMENDACIONES (READS)
# ==============================================================================

def get_top_tracks():
    """Top 10 canciones más escuchadas."""
    conn = get_db_connection()
    if not conn: return []
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT track_id, COUNT(*) as total_plays
        FROM plays
        GROUP BY track_id
        ORDER BY total_plays DESC
        LIMIT 10
    """)
    top_ids = cur.fetchall()
    cur.close()
    conn.close()
    
    result = []
    for item in top_ids:
        track_info = _fetch_from_content(f"/tracks/{item['track_id']}")
        
        track_data = {
            "id": item['track_id'],
            "plays": item['total_plays'],
            "title": track_info['title'] if track_info else f"Track {item['track_id']}",
            "artist_id": track_info.get('artist_id') if track_info else None
        }
        result.append(track_data)
        
    return result

def get_recommended_tracks(id_user, type=None):
    """Recomendador Híbrido."""
    conn = get_db_connection()
    if not conn: return []
    cur = conn.cursor(cursor_factory=RealDictCursor)
    recommendations = []
    
    try:
        if type == 'genre':
            # 1. Sacar últimas canciones escuchadas (SQL)
            cur.execute("""
                SELECT track_id FROM plays 
                WHERE user_id = %s 
                ORDER BY timestamp DESC LIMIT 20
            """, (id_user,))
            recent_tracks = [row['track_id'] for row in cur.fetchall()]
            
            if not recent_tracks: return get_top_tracks()

            # 2. Buscar género favorito (HTTP a Contenidos)
            from collections import Counter
            genres = []
            for tid in recent_tracks:
                info = _fetch_from_content(f"/tracks/{tid}")
                if info and 'genre' in info:
                    genres.append(info['genre'])
            
            if not genres: return get_top_tracks()
            
            fav_genre = Counter(genres).most_common(1)[0][0]
            print(f"--> Usuario {id_user} prefiere: {fav_genre}")

            # 3. Pedir catálogo y filtrar (HTTP)
            all_tracks = _fetch_from_content("/tracks")
            if all_tracks:
                for t in all_tracks:
                    if t.get('genre') == fav_genre and t['id'] not in recent_tracks:
                        recommendations.append(t)
                        if len(recommendations) >= 5: break

        elif type == 'like':
             # SQL Colaborativo
             cur.execute("""
                SELECT l2.track_id, COUNT(*) as matches
                FROM likes l1
                JOIN likes l2 ON l1.user_id = l2.user_id
                WHERE l1.user_id = %s
                AND l2.track_id NOT IN (SELECT track_id FROM likes WHERE user_id = %s)
                GROUP BY l2.track_id
                ORDER BY matches DESC
                LIMIT 5
             """, (id_user, id_user))
             
             sim_ids = cur.fetchall()
             for item in sim_ids:
                 info = _fetch_from_content(f"/tracks/{item['track_id']}")
                 if info: recommendations.append(info)

        else:
            return get_top_tracks()
            
    except Exception as e:
        print(f"Error recomendando: {e}")
    finally:
        cur.close()
        conn.close()

    return recommendations

# ==============================================================================
#  STUBS REALES
# ==============================================================================
def get_user_plays(idUser): 
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT track_id, timestamp FROM plays WHERE user_id = %s ORDER BY timestamp DESC", (idUser,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_user_likes(idUser): 
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT track_id, timestamp FROM likes WHERE user_id = %s", (idUser,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def get_artist_plays(idArtist):
    tracks_data = _fetch_from_content(f"/artists/{idArtist}/tracks")
    if not tracks_data: return []
    track_ids = [t['id'] for t in tracks_data]
    if not track_ids: return [{"artist_id": idArtist, "total_plays": 0}]

    conn = get_db_connection()
    cur = conn.cursor()
    format_strings = ','.join(['%s'] * len(track_ids))
    cur.execute(f"SELECT COUNT(*) FROM plays WHERE track_id IN ({format_strings})", tuple(track_ids))
    total = cur.fetchone()[0]
    cur.close()
    conn.close()
    return [{"artist_id": idArtist, "total_plays": total}]

def get_track_plays(idTrack):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM plays WHERE track_id = %s", (idTrack,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return [{"track_id": idTrack, "plays": count}]

def get_track_likes(idTrack):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM likes WHERE track_id = %s", (idTrack,))
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return [{"track_id": idTrack, "likes": count}]

def get_artist_top_tracks(idArtist):
    tracks_data = _fetch_from_content(f"/artists/{idArtist}/tracks")
    if not tracks_data: return []
    track_ids = [t['id'] for t in tracks_data]
    if not track_ids: return []

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    format_strings = ','.join(['%s'] * len(track_ids))
    cur.execute(f"""
        SELECT track_id, COUNT(*) as plays
        FROM plays 
        WHERE track_id IN ({format_strings})
        GROUP BY track_id
        ORDER BY plays DESC
        LIMIT 5
    """, tuple(track_ids))
    ranking = cur.fetchall()
    cur.close()
    conn.close()
    
    result = []
    for item in ranking:
        original_track = next((t for t in tracks_data if t['id'] == item['track_id']), None)
        if original_track: result.append(original_track)
    return result