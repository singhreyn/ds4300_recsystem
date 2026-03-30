from neo4j import GraphDatabase
import pandas as pd

# Connection
URI = "neo4j+s://627fa261.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "t3sQw5j1eL4gXttJyzR0XFeuWrlXqtccX3tBz6s0Iv8"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

# Load nodes 
nodes_df = pd.read_csv("neo4j_nodes.csv")

def load_nodes(tx, batch):
    tx.run("""
        UNWIND $batch AS row
        CREATE (:Song {
            track_id: row.track_id,
            track_name: row.track_name,
            artists: row.artists,
            album_name: row.album_name,
            popularity: toInteger(row.popularity),
            danceability: toFloat(row.danceability),
            energy: toFloat(row.energy),
            loudness: toFloat(row.loudness),
            speechiness: toFloat(row.speechiness),
            acousticness: toFloat(row.acousticness),
            instrumentalness: toFloat(row.instrumentalness),
            liveness: toFloat(row.liveness),
            valence: toFloat(row.valence),
            tempo: toFloat(row.tempo),
            track_genre: row.track_genre
        })
    """, batch=batch)

batch = nodes_df.to_dict(orient="records")
with driver.session() as session:
    session.execute_write(load_nodes, batch)

print(f"Loaded {len(nodes_df)} nodes into Neo4j.")

# Load relationships
edges_df = pd.read_csv("neo4j_relationships.csv")

def load_edges(tx, batch):
    tx.run("""
        UNWIND $batch AS row
        MATCH (a:Song {track_id: row.src_id})
        MATCH (b:Song {track_id: row.dst_id})
        CREATE (a)-[:SIMILAR_TO {distance: toFloat(row.distance)}]->(b)
    """, batch=batch)

# Load in batches of 500
batch_size = 500
total = len(edges_df)
for i in range(0, total, batch_size):
    batch = edges_df.iloc[i:i+batch_size].to_dict(orient="records")
    with driver.session() as session:
        session.execute_write(load_edges, batch)
    print(f"Loaded edges {i} to {min(i+batch_size, total)}...")

print(f"Loaded {total} edges total.")