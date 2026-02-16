import time

# --- IN-MEMORY NETWORK STATE ---
# This dictionary acts as the "Live RAM" of the network.
# Structure: { 'NODE_ID': { 'last_seen': 1234567890, 'stats': {...} } }
active_nodes = {}

def register_node(node_id, hardware_stats):
    """
    Called by app.py when a node sends a handshake.
    Updates the in-memory registry with the node's live status.
    """
    current_time = time.time()
    
    # Update or Create the node record
    active_nodes[node_id] = {
        'last_seen': current_time,
        'status': 'ONLINE',
        'hardware': hardware_stats
    }
    
    # Prune old nodes (optional cleanup)
    _prune_dead_nodes()
    
    print(f"💓 PULSE: Node {node_id} heartbeat synced.")

def get_active_count():
    """Returns the number of nodes seen in the last 5 minutes."""
    _prune_dead_nodes()
    return len(active_nodes)

def _prune_dead_nodes():
    """Removes nodes strictly for the in-memory count (doesn't touch DB)."""
    cutoff = time.time() - 300 # 5 minutes ago
    
    # Create a list of dead nodes to remove
    dead_nodes = [nid for nid, data in active_nodes.items() if data['last_seen'] < cutoff]
    
    for nid in dead_nodes:
        del active_nodes[nid]