import pytest
import pandas as pd
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from recongraph.recongraph import SigmaMatcher, SigmaLabel, EdgeGraph, ReconGraph

# --- TEST CASES ---

def test_log_type_detection():
    """Tests if SigmaLabel correctly identifies log types."""
    labeler = SigmaLabel(input_file="access.log")
    features = labeler.detect_log_type("GET /index.php HTTP/1.1", "access.log")
    assert 'webserver' in features['log_type']
    assert features['cs-method'] == "GET"

@pytest.fixture
def dummy_df():
    return pd.DataFrame({
        'datetime': ["2023-01-01 10:00:00", "2023-01-01 10:01:00"],
        'message': ["Log A", "Log B"],
        'sigma': ["Critical Event[critical]", "Low Event[low]"]
    })

def test_graph_nodes(dummy_df):
    """Tests if EdgeGraph creates the correct number of nodes."""
    builder = EdgeGraph(dummy_df)
    builder.define_events()
    builder.create_graph()
    # There are two unique sigma events in dummy_df
    assert builder.G.number_of_nodes() == 2

def test_sigma_matcher_logic():
    """Tests if the SigmaMatcher correctly evaluates logic conditions."""
    # Create a dummy matcher manually
    from recongraph.recongraph import SigmaMatcher
    import yaml
    import tempfile
    import os

    rule_content = {
        'title': 'Test Rule',
        'logsource': {'category': 'webserver'},
        'detection': {
            'selection': {'c-uri': '/etc/passwd'},
            'condition': 'selection'
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tf:
        yaml.dump(rule_content, tf)
        temp_name = tf.name

    try:
        matcher = SigmaMatcher(temp_name)
        
        # Positive match
        assert matcher.match({'c-uri': '/etc/passwd', 'log_type': ['webserver']}) is True
        # Negative match (wrong URI)
        assert matcher.match({'c-uri': '/index.php', 'log_type': ['webserver']}) is False
    finally:
        os.remove(temp_name)

def test_edge_weight_calculation():
    """Tests if transitions between events are counted correctly as weights."""
    from recongraph.recongraph import EdgeGraph
    import pandas as pd

    # Sequence: A -> B -> A -> B -> C
    data = {
        'datetime': ["10:00", "10:01", "10:02", "10:03", "10:04"],
        'message': ["m1", "m2", "m3", "m4", "m5"],
        'sigma': ["Event_A", "Event_B", "Event_A", "Event_B", "Event_C"]
    }
    df = pd.DataFrame(data)
    builder = EdgeGraph(df)
    builder.run_all()

    # The transition (Event_A -> Event_B) happened twice
    # Find the edge in the MultiDiGraph
    u = builder.events_dict["Event_A"]
    v = builder.events_dict["Event_B"]
    
    # Check weights in edges_weight dictionary
    assert builder.edges_weight[(u, v)] == 2

def test_graphml_export(tmp_path, dummy_df):
    """Verifies that the GraphML file is created and contains node data."""
    from recongraph.recongraph import EdgeGraph
    import os

    output_file = tmp_path / "test_graph.graphml"
    builder = EdgeGraph(dummy_df)
    builder.run_all(graph_output=str(output_file))

    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 0