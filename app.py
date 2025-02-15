import streamlit as st
import sqlite3
from pyvis.network import Network
import pandas as pd

# Fetch data from database
def fetch_data(query):
    conn = sqlite3.connect("knowledge_graph.db")
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Generate knowledge graph
def generate_graph(filtered_tags=None):
    nodes = fetch_data("SELECT * FROM Nodes")
    edges = fetch_data("SELECT * FROM Edges")
    tags = fetch_data("SELECT * FROM Tags")
    
    if filtered_tags:
        tagged_nodes = tags[tags['tag'].isin(filtered_tags)]['node_id'].unique()
        nodes = nodes[nodes['id'].isin(tagged_nodes)]
        edges = edges[(edges['source'].isin(nodes['id'])) & (edges['target'].isin(nodes['id']))]
    
    net = Network(height="750px", width="100%", bgcolor="white", font_color="black")
    
    # Use a set to track added nodes
    added_nodes = set()

    # Add nodes to the graph
    for _, node in nodes.iterrows():
        if node['id'] not in added_nodes:
            net.add_node(node['id'], label=node['name'], title=node['description'], group=node['type'])
            added_nodes.add(node['id'])

    # Add edges with relation text (queried from the database)
    for _, edge in edges.iterrows():
        net.add_edge(edge['source'], edge['target'], title=edge['relationship'], label=edge['relationship'])

    return net

# Streamlit UI
st.title("AMLTRIX Knowledge Graph")
selected_tags = st.multiselect("Filter by Tags", fetch_data("SELECT DISTINCT tag FROM Tags")['tag'].tolist())
graph = generate_graph(selected_tags)

# Render graph
graph.save_graph("graph.html")
st.components.v1.html(open("graph.html", "r").read(), height=800)
