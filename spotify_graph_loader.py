# DS4300 HW5 — Spotify Song Recommendation Graph
# Team Members: Benoit Schiermeier, Reyna Singh, and Talal Fakhoury
# Samples 114k Spotify songs, builds a similarity graph, and exports CSVs for Neo4j.
# Graph model: (:Song)-[:SIMILAR_TO {distance}]->(:Song)
# Similarity metric: Euclidean distance < 0.35 across 9 normalised audio features

# Imports
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import euclidean_distances

# Load the data
df = pd.read_csv("spotify.csv")
print(f"Total songs loaded: {len(df)}")
print(df.columns.tolist())

# Find seed songs (The Strokes + Regina Spektor) 
strokes = df[df["artists"].str.contains("The Strokes", na=False)].drop_duplicates("track_id")
regina  = df[df["artists"].str.contains("Regina Spektor", na=False)].drop_duplicates("track_id")
seed    = pd.concat([strokes, regina]).drop_duplicates("track_id")

print(f"The Strokes songs: {len(strokes)}")
print(f"Regina Spektor songs: {len(regina)}")
print(f"Total seed songs: {len(seed)}")

# Sample 1000 diverse non-seed songs
non_seed   = df[~df["track_id"].isin(seed["track_id"])].drop_duplicates("track_id")
top_genres = non_seed["track_genre"].value_counts().head(30).index

parts = []
for g in top_genres:
    gdf = non_seed[non_seed["track_genre"] == g]
    parts.append(gdf.sample(min(30, len(gdf)), random_state=42))

remainder = non_seed[~non_seed["track_genre"].isin(top_genres)]
parts.append(remainder.sample(min(100, len(remainder)), random_state=42))

sample = pd.concat(parts).drop_duplicates("track_id").head(1000)
print(f"Sampled non-seed songs: {len(sample)}")
print(f"Genres represented: {sample['track_genre'].nunique()}")

# Combine seed + sample into full graph 
graph_df = pd.concat([seed, sample]).drop_duplicates("track_id").reset_index(drop=True)
print(f"Total graph nodes: {len(graph_df)}")

# Normalize audio features
FEATURES = ["danceability", "energy", "loudness", "speechiness",
            "acousticness", "instrumentalness", "liveness", "valence", "tempo"]

scaler      = MinMaxScaler()
feat_matrix = scaler.fit_transform(graph_df[FEATURES].fillna(0))
print(f"Feature matrix shape: {feat_matrix.shape}")

#  Compute pairwise distances and create edges
THRESHOLD = 0.35
GOOD_GENRES = {'alt-rock', 'alternative', 'indie', 'pop', 'rock', 'acoustic',
               'singer-songwriter', 'indie-pop', 'power-pop', 'garage', 'punk',
               'emo', 'piano', 'folk', 'sad', 'new-wave', 'grunge', 'post-punk'}

dist_matrix = euclidean_distances(feat_matrix)

edges = []
n = len(graph_df)
for i in range(n):
    for j in range(i + 1, n):
        d = dist_matrix[i, j]
        if d < THRESHOLD:
            edges.append({
                "src_id": graph_df.iloc[i]["track_id"],
                "dst_id": graph_df.iloc[j]["track_id"],
                "distance": round(float(d), 4)
            })

print(f"Total edges created: {len(edges)}")

print(f"Total edges created: {len(edges)}")

# Generate recommendations based on proximity to seed songs
seed_ids = set(seed["track_id"])
id_to_idx = {row["track_id"]: i for i, row in graph_df.iterrows()}

neighbor_scores = {}
for tid in seed_ids:
    if tid not in id_to_idx:
        continue
    i = id_to_idx[tid]
    for j in range(n):
        other = graph_df.iloc[j]
        other_id = other["track_id"]
        if other_id in seed_ids:
            continue
        if other["track_genre"] not in GOOD_GENRES:
            continue
        if not other["track_name"].isascii():
            continue
        d = dist_matrix[i, j]
        if d < THRESHOLD:
            if other_id not in neighbor_scores:
                neighbor_scores[other_id] = []
            neighbor_scores[other_id].append(d)

ranked = sorted(neighbor_scores.items(),
                key=lambda x: (len(x[1]), -np.mean(x[1])), reverse=True)

print("\nTop 5 Recommendations for Prof. Rachlin")
for i, (tid, dists) in enumerate(ranked[:5], 1):
    row = graph_df[graph_df["track_id"] == tid].iloc[0]
    print(f"{i}. {row['track_name']}, {row['artists']}, {row['album_name']}, {row['track_genre']}")

# Export CSVs for Neo4j import
import pandas as pd

node_cols = ["track_id", "track_name", "artists", "album_name", "popularity",
             "duration_ms", "explicit", "danceability", "energy", "key", "loudness",
             "mode", "speechiness", "acousticness", "instrumentalness", "liveness",
             "valence", "tempo", "time_signature", "track_genre"]

graph_df[node_cols].to_csv("neo4j_nodes.csv", index=False)
pd.DataFrame(edges).to_csv("neo4j_relationships.csv", index=False)