import csv
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict
import networkx as nx
from collections import defaultdict
import os
import argparse
import pandas as pd
import re
import yaml
from typing import List, Dict, Any
from pathlib import Path


class SigmaMatcher:
    """
    Handles parsing Sigma rules from YAML files and evaluating them 
    against normalized log entries.

    This class processes Sigma rule detection logic, logsource requirements, 
    and metadata. It provides an evaluation engine that determines if a 
    specific log entry matches the rule's criteria, supporting field 
    modifiers and complex boolean conditions.
    """
    def __init__(self, rule_file: str, flexible_mode: bool = True):
        with open(rule_file, 'r', encoding='utf-8') as f:
            self.rule_data = yaml.safe_load(f)

        self.title = self.rule_data.get('title', 'Unknown')
        self.description = self.rule_data.get('description', '')
        self.level = self.rule_data.get('level', 'medium')
        self.tags = self.rule_data.get('tags', [])
        self.detection = self.rule_data.get('detection', {})
        self.logsource = self.rule_data.get('logsource', {})
        self.flexible_mode = flexible_mode

    def match(self, log_entry: Dict[str, Any]) -> bool:
        """
        Check if log entry matches rule.

        This function checks if a given log entry matches the Sigma rule's detection logic.
        It evaluates the conditions defined in the rule against the fields in the log entry.
        """
        if not log_entry:
            return False
            
        if not self.flexible_mode and self.logsource:
            if not self._check_logsource(log_entry):
                return False    
    
        condition = self.detection.get('condition', '').lower().strip()
    
        selections = {}
        for key, value in self.detection.items():
            if key == 'condition':
                continue
            selections[key.lower()] = self._match_selection(value, log_entry)
    
        return self._evaluate_condition(condition, selections)

    def _check_logsource(self, log_entry: Dict[str, Any]) -> bool:
        """
        Check if log_entry match with the rule's expected logsource.

        This function validates whether the log entry originates from the log source 
        specified in the Sigma rule (category, product, service).
        """
        expected_category = self.logsource.get("category", "").lower()
        expected_product = self.logsource.get("product", "").lower()
        expected_service = self.logsource.get("service", "").lower()
        
        log_types = log_entry.get("log_type", [])
        if isinstance(log_types, str):
            log_types = [log_types]
        
        log_types_lower = [lt.lower() for lt in log_types]

        if expected_category and not any(expected_category in lt for lt in log_types_lower):
            return False
            
        if expected_product:
            if expected_service:
                if not any(expected_service in lt for lt in log_types_lower):
                    if not any(expected_product in lt for lt in log_types_lower):
                        return False
        return True

    def _match_selection(self, selection, log_entry: Dict) -> bool:
        """
        Match selection with log entry.

        This function iterates through the selection criteria (strings, lists, or dictionaries)
        and checks if the log entry satisfies them. in flexible mode, it searches broadly.
        """
        search_fields = self._get_search_fields(log_entry)
        
        if isinstance(selection, list):
            for pattern in selection:
                pattern_lower = str(pattern).lower()
                if self._match_simple_pattern(pattern_lower, search_fields):
                    return True
            return False 

        if isinstance(selection, str):
            pattern_lower = str(selection).lower()
            return self._match_simple_pattern(pattern_lower, search_fields)

        if not isinstance(selection, dict):
            return False

        for field, patterns in selection.items():
            if field == '|all':
                patterns = patterns if isinstance(patterns, list) else [patterns]
                for pattern in patterns:
                    pattern_lower = str(pattern).lower()
                    if not self._match_simple_pattern(pattern_lower, search_fields):
                        return False
                return True
            
            if field == '|any':
                patterns = patterns if isinstance(patterns, list) else [patterns]
                for pattern in patterns:
                    pattern_lower = str(pattern).lower()
                    if self._match_simple_pattern(pattern_lower, search_fields):
                        return True
                return False

            field_name, modifier = self._parse_field(field)
            patterns = patterns if isinstance(patterns, list) else [patterns]
            
            log_value = self._get_field_value(log_entry, field_name)

            null_check_needed = any(str(p).lower() == "null" for p in patterns)
            if not log_value and not null_check_needed:
                return False
                
            null_match_found = False
            for p in patterns:
                if str(p).lower() == "null":
                    if log_value == "":
                        null_match_found = True
                    else:
                        return False
                
            if null_match_found:
                 return True

            pattern_matched = False
            for p in patterns:
                if str(p).lower() == "null": continue
                if self._match_value(log_value, str(p).lower(), modifier):
                    pattern_matched = True
                    break
            
            if not pattern_matched:
                return False

        return True

    def _match_simple_pattern(self, pattern: str, search_fields: List[str]) -> bool:
        """
        Matches a simple pattern string against a list of search fields.

        This function checks if the pattern exists as a substring in any of the provided search fields.
        """
        return any(pattern in field for field in search_fields)

    def _get_search_fields(self, log_entry: Dict) -> List[str]:
        """
        Get all searchable fields from log entry.

        This function gathers values from various fields in the log entry to form a list
        of text strings to search against. In flexible mode, it includes almost all values.
        """
        search_fields = []
        if 'desc' in log_entry:
            search_fields.append(str(log_entry.get('desc', '')).lower())
        
        if self.flexible_mode:
             for k, v in log_entry.items():
                 if k not in ['log_type'] and v:
                     search_fields.append(str(v).lower())
        else:
            http_fields = ['c-uri', 'cs-uri-query', 'cs-user-agent', 'cs-referer', 'cs-method']
            for field in http_fields:
                if field in log_entry and log_entry[field]:
                    search_fields.append(str(log_entry[field]).lower())
            
            extra_fields =  ['command', 'commandline', 'process', 'image', 'parentimage']
            for field in extra_fields:
                if field in log_entry and log_entry[field]:
                    search_fields.append(str(log_entry[field]).lower())
        
        return search_fields if search_fields else ['']

    def _get_field_value(self, log_entry: Dict, field_name: str) -> str:
        """
        Get the value of a field from the log entry.

        This function retrieves the value of a specific field from the log entry,
        handling field mapping (e.g., 'uri' -> 'c-uri') and normalizing to lowercase.
        """
        if field_name in log_entry:
            return str(log_entry[field_name]).lower()
        
        field_mappings = {
            'uri': 'c-uri',
            'url': 'c-uri',
            'query': 'cs-uri-query',
            'useragent': 'cs-user-agent',
            'user_agent': 'cs-user-agent',
            'method': 'cs-method',
            'status': 'sc-status',
            'message': 'desc',
            'msg': 'desc',
            'commandline': 'desc',
            'command': 'desc',
        }

        mapped_field = field_mappings.get(field_name.lower())
        if mapped_field and mapped_field in log_entry:
            return str(log_entry[mapped_field]).lower()
        
        if self.flexible_mode and 'desc' in log_entry:
            return str(log_entry['desc']).lower()
        
        return ''

    def _parse_field(self, field: str):
        """
        Parse a field string into a tuple of (field_name, modifier).

        This function splits a field string like 'fieldname|modifier' into its components.
        """
        if "|" not in field:
            return (field, None)
        parts = field.split("|")
        return parts[0], parts[-1]

    def _match_value(self, value: str, pattern: str, modifier: str = None):
        """
        Match a pattern against a value based on the modifier.

        This function applies the specified modifier (e.g., 'contains', 'startswith')
        to match the pattern against the value.
        """
        if modifier == "contains": return pattern in value
        if modifier == "startswith": return value.startswith(pattern)
        if modifier == "endswith": return value.endswith(pattern)
        if modifier == "re": return bool(re.search(pattern, value))
        return value == pattern

    def _evaluate_condition(self, condition: str, selections: Dict[str, bool]) -> bool:
        """
        Evaluate a condition based on the selections.

        This function evaluates the logical condition string (e.g., 'selection1 and not selection2')
        using the results of the selection matching.
        """
        if not condition:
            return any(selections.values())
    
        condition = condition.lower().strip()
        
        def replace_x_of(match):
            count_str = match.group(1) 
            prefix = match.group(2)
            
            matching_vals = [v for k, v in selections.items() if k.startswith(prefix)]
            if not matching_vals: return "False"

            if "not" in count_str:
                 target = int(count_str.replace("not", "").strip())
                 return str(not (sum(matching_vals) >= target))
            elif "all" in count_str:
                 return str(all(matching_vals))
            else:
                 target = int(count_str)
                 return str(sum(matching_vals) >= target)

        condition = re.sub(r'((?:not\s+)?\d+|all)\s+of\s+(\w+)\*?', replace_x_of, condition)

        if "all of them" in condition: condition = condition.replace("all of them", str(all(selections.values())))
        if "1 of them" in condition: condition = condition.replace("1 of them", str(any(selections.values())))
        if "any of them" in condition: condition = condition.replace("any of them", str(any(selections.values())))
        
        for key, result in selections.items():
            condition = re.sub(rf"\\b{re.escape(key)}\\b", str(result), condition)
        
        try:
            return bool(eval(condition))
        except Exception:
            return any(selections.values())


class SigmaRulesLoader:
    """
    Manages the lifecycle of Sigma rules within a specified directory.

    This class handles searching for, loading, and initializing Sigma rules into 
    executable matchers. It provides a high-level interface for checking log 
    entries against the entire rule set and managing rule-specific metadata.
    """
    def __init__(self, rules_dir: str, flexible_mode: bool = True):
        self.rules_dir = rules_dir
        self.flexible_mode = flexible_mode
        self.matchers = []
        self._load_rules()

    def _load_rules(self):
        """
        Loads all rules from desired directory.

        This function scans the specified rules directory for YAML files,
        creates a SigmaMatcher for each, and stores them in the matchers list.
        """
        if not self.rules_dir:
            print("No rules directory specified. Skipping rule loading.")
            return

        rules_path = Path(self.rules_dir)
        if not rules_path.exists():
            print(f"Rules directory {rules_path} does not exist")
            return
        
        mode_str = "FLEXIBLE" if self.flexible_mode else "STRICT"
        print(f"- Loading Sigma Rules from: {self.rules_dir} (Mode: {mode_str})")
        
        loaded_count = 0
        for rule_file in rules_path.glob('**/*.yml'):
            try:
                matcher = SigmaMatcher(str(rule_file), flexible_mode=self.flexible_mode)
                self.matchers.append({
                    'matcher': matcher,
                    'title': matcher.title,
                    'level': matcher.level,
                })
                loaded_count += 1
            except Exception:
                pass
        
        print(f"- Total rules loaded: {loaded_count} rules")

    def check_row(self, parsed_row: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Check if a row matches any of the loaded rules.

        This function iterates through all loaded rules and checks if the given
        parsed log row matches any of them. Returns a list of matching rules.
        """
        matches = []
        for rule_info in self.matchers:
            matcher = rule_info['matcher']
            if matcher.match(parsed_row):
                matches.append({
                    'rule_title': matcher.title,
                    'rule_level': matcher.level,
                })
        return matches

    def extract_sigma_priority(self, sigma_value: str) -> str:
        """
        Select top priority rule based on severity.

        This function parses a string of matched Sigma rules (formatted as 
        'Title[Severity] | Title[Severity]') and determines the highest priority
        match based on severity level.
        """
        if not sigma_value or not sigma_value.strip():
            return ""

        items = [s.strip() for s in sigma_value.split("|")]
        priority = {"critical": 5, "high": 4, "medium": 3, "low": 2, "informational": 1}

        best_item = None
        best_score = 0

        for item in items:
            if "[" in item and "]" in item:
                severity = item[item.rfind("[")+1 : item.rfind("]")].lower().strip()
                score = priority.get(severity, 0)
                if score > best_score:
                    best_score = score
                    best_item = item
        
        return best_item or ""


class SigmaLabel(object):
    """
    Orchestrates the log labeling process using Sigma rules.

    This class is responsible for reading input log files (CSV or TXT), 
    identifying the appropriate log type and source, and applying the loaded 
    Sigma rules to each entry to generate a labeled dataset.
    """
    def __init__(self, input_file, rules_dir=None, flexible_mode=True):
        self.input_file = input_file
        self.rules_dir = rules_dir
        self.flexible_mode = flexible_mode
    
    def count_lines(self):
        """
        Counts the number of lines in the input file.

        This function reads the input file to count the total number of lines,
        which is useful for progress tracking.
        """
        cnt = 0
        try:
            with open(self.input_file, 'r', encoding='utf-8', errors='replace') as f:
                for _ in f: cnt += 1
        except:
             pass
        return cnt

    def detect_log_type(self, desc: str, filename: str) -> Dict[str, Any]:
        """
        Detects the type of log entry based on its description and filename.

        This function analyzes the log description and filename to categorize the log
        (e.g., 'webserver', 'linux', 'windows') and extracts relevant fields like
        HTTP methods or status codes.
        """
        parsed = {}
        log_types = []
        lower_desc = desc.lower()
        
        if 'access.log' in filename:
            log_types.extend(['webserver', 'proxy', 'nginx', 'apache'])
            self._extract_http_fields(desc, parsed)
            
        if 'auth.log' in filename:
            log_types.extend(['linux', 'sshd'])
            if 'pam' in lower_desc: log_types.append('pam')
        if 'syslog' in filename:
            log_types.extend(['syslog', 'linux'])
            if 'systemd' in lower_desc: log_types.append('systemd')
            if 'kernel' in lower_desc: log_types.append('kernel')
            if 'audit' in lower_desc: log_types.append('auditd')

        if 'windows' in filename.lower() or '.evtx' in filename.lower():
            log_types.append('windows')
            if 'sysmon' in filename.lower(): log_types.append('sysmon')
            if 'security' in filename.lower(): log_types.append('security')
            if 'system' in filename.lower(): log_types.append('system')

        if self._looks_like_http_log(desc):
             if 'webserver' not in log_types: log_types.extend(['webserver', 'generic_http'])
             if 'cs-method' not in parsed: self._extract_http_fields(desc, parsed)
             
        if not log_types:
            log_types.append('unknown')

        parsed['log_type'] = log_types
        return parsed

    def _looks_like_http_log(self, desc: str)-> bool:
        """
        Detects if a log entry looks like an HTTP log entry.

        This function uses regular expressions to check for common HTTP log patterns,
        such as HTTP methods, status codes, or user-agent strings.
        """
        http_indicators = [
            r'\b(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\b',
            r'HTTP/\d\.\d',
            r'\b(200|301|302|400|401|403|404|500)\b',
            r'user[_-]?agent',
            r'referer',
        ]
        for pattern in http_indicators:
            if re.search(pattern, desc, re.IGNORECASE):
                return True
        return False

    def _extract_http_fields(self, desc: str, parsed: Dict[str, Any]):
        """
        Extracts HTTP fields from a log entry description.

        This function parses the log description to extract HTTP Method, URI, 
        Status Code, and User Agent, populating the 'parsed' dictionary.
        """
        method_match = re.search(r'\b(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\b', desc)
        if method_match: parsed['cs-method'] = method_match.group(1)
        
        uri_match = re.search(r'(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+([^\s]+)\s+HTTP', desc)
        if uri_match:
            parsed['c-uri'] = uri_match.group(2)
        else:
            uri_match = re.search(r'(GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+([^\s\"]+)', desc)
            if uri_match: parsed['c-uri'] = uri_match.group(2)

        status_match = re.search(r'code:\s*(\d{3})', desc)
        if status_match: parsed['sc-status'] = status_match.group(1)
        
        ua_match = re.search(r'user_agent:\s*(.+?)(?:\s+\w+:|$)', desc)
        if ua_match: parsed['cs-user-agent'] = ua_match.group(1).strip()

    def run(self):
        """
        Processes the input file and returns a labeled DataFrame.

        This function orchestrates the loading of data, detection of log types,
        matching against Sigma rules, and generation of a labeled DataFrame.
        """
        rules_loader = SigmaRulesLoader(self.rules_dir, flexible_mode=self.flexible_mode)
        
        if not rules_loader.matchers:
             print("No rules loaded! Continuing without matching...")

        is_csv = self.input_file.endswith('.csv')
        df = pd.DataFrame() 

        if is_csv:
            try:
                df = pd.read_csv(self.input_file, dtype=str)
            except:
                df = pd.read_csv(self.input_file, header=None, dtype=str)
                df.columns = [f'col_{i}' for i in range(len(df.columns))]
        else:
            try:
                with open(self.input_file, 'r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
                df = pd.DataFrame({'description': lines})
                df['filename'] = self.input_file
            except Exception as e:
                print(f"Error reading file: {e}")
                return df

        processed_rows = []
        total_rows = len(df)
        print(f"- Labeling {total_rows} rows...")
        
        count = 0 
        for _, row in df.iterrows():
            count += 1
            if count % 1000 == 0:
                print(f"- Processed {count}/{total_rows} lines...")

            desc = ""
            if 'message' in row: desc = str(row['message'])
            elif 'desc' in row: desc = str(row['desc'])
            elif 'description' in row: desc = str(row['description']) 
            elif len(row) > 4 and isinstance(row.values[4], str) : desc = row.values[4]
            else: desc = str(row.values[0])

            fname = self.input_file
            if 'filename' in row: fname = str(row['filename'])
            elif 'source_short' in row: fname = str(row['source_short'])
            elif 'display_name' in row: fname = str(row['display_name'])
            elif 'source' in row: fname = str(row['source'])
            elif len(row) > 6 and isinstance(row.values[6], str): fname = row.values[6]

            features = self.detect_log_type(str(desc), str(fname))
            
            log_entry = {
                "desc": desc,
                "log_type": features["log_type"], 
                "cs-method": features.get("cs-method", ""),
                "c-uri": features.get("c-uri", ""),
                "sc-status": features.get("sc-status", ""),
                "cs-user-agent": features.get("cs-user-agent", ""),
                "service": features.get("service", ""), 
            }

            matches = rules_loader.check_row(log_entry)
            
            if matches:
                detection_str = " | ".join([f"{m['rule_title']}[{m['rule_level']}]" for m in matches])
            else:
                detection_str = ""

            new_row = row.to_dict()
            new_row['logsource'] = str(features['log_type'])
            new_row['sigma'] = rules_loader.extract_sigma_priority(detection_str)
            processed_rows.append(new_row)

        return pd.DataFrame(processed_rows)


class EdgeGraph(object):
    """
    Constructs a directed graph from sigma-labeled logs to visualize system behavior.

    This class transforms a sequential list of security events into a 
    MultiDiGraph where nodes represent unique event types and edges represent 
    temporal transitions between them. It captures event frequency and 
    associated log metadata to facilitate forensic analysis.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
        if 'message' not in self.df.columns:
            if 'desc' in self.df.columns:
                self.df.rename(columns={'desc': 'message'}, inplace=True)
            elif 'description' in self.df.columns:
                self.df.rename(columns={'description': 'message'}, inplace=True)
            else:
                 self.df['message'] = ""

        if 'datetime' not in self.df.columns:
            if 'timestamp' in self.df.columns:
                 self.df.rename(columns={'timestamp': 'datetime'}, inplace=True)
            else:
                 self.df['datetime'] = ""

        self.events_dict = {}
        self.node_labels = {}
        self.node_events = []
        self.G = nx.MultiDiGraph()
        
        self.log_event_id = []
        self.node_members = defaultdict(list)
        self.event_logs = defaultdict(list)
        self.event_timestamps = defaultdict(list)
        
        self.edges_list = []
        self.edges_weight = defaultdict(int)
        self.edges_weight_list = []

    def define_events(self):
        """
        Identify unique security events from the labeled dataset.

        This function iterates through the 'sigma' column to find all unique rule matches. 
        These matches define the nodes of the graph. Each unique Sigma label 
        becomes a distinct node in the resulting behavioral map.
        """
        lines = self.df['message'].tolist()
        
        if 'sigma' in self.df.columns:
             events = self.df[self.df['sigma'].notna() & (self.df['sigma'] != '')]['sigma'].unique().tolist()
        else:
             events = []

        self.events_dict = {}
        for index, event in enumerate(events):
            self.events_dict[event] = index
        self.node_labels = {}
        for index, event in enumerate(events):
            self.node_labels[index] = event

        self.node_events = []
        for index, event in enumerate(events):
            self.node_events.append((index, {'event': f"{str(index)}. {event}"}))

    def create_graph(self):
        """
        Initialize the graph with nodes.

        This function creates a new networkx MultiDiGraph and adds the identified events
        as nodes.
        """
        self.G = nx.MultiDiGraph()
        self.G.add_nodes_from(self.node_events)
        print(f"Graph nodes added: {self.G.number_of_nodes()}")

    def get_list_event_id(self):
        """
        Map log entries to event IDs.

        This function processes the DataFrame rows, identifying which event ID corresponds
        to each log entry based on its Sigma label, and stores this mapping.
        """
        self.log_event_id = []
        self.node_members = defaultdict(list)
        self.event_logs = defaultdict(list)        
        self.event_timestamps = defaultdict(list)  

        for line_id, row in self.df.iterrows():
            sigma_value = row.get('sigma')
            desc_value = row.get('message')            
            timestamp_value = row.get('datetime')  
            
            if pd.notna(sigma_value) and sigma_value != '':
                if sigma_value in self.events_dict:
                    event_id = self.events_dict[sigma_value]
                    self.log_event_id.append(event_id)
                    self.node_members[event_id].append(line_id)
                    self.event_logs[event_id].append(desc_value)            
                    self.event_timestamps[event_id].append(timestamp_value) 

    def add_node_attributes(self):
        """
        Enrich nodes with attributes.

        This function adds metadata to each node in the graph, such as the first log snippet,
        timestamp, and the count of logs associated with that event.
        """
        for event_id in self.event_logs.keys():
            logs = self.event_logs[event_id]
            timestamps = self.event_timestamps[event_id]
            
            
            if logs:
                first_log = logs[0]
            else:
                first_log = ""
            
            if timestamps:
                first_timestamp = timestamps[0]
            else:
                first_timestamp = ""
            
            
            if self.G.has_node(event_id):
                self.G.nodes[event_id]['message'] = first_log
                self.G.nodes[event_id]['timestamp'] = first_timestamp
                self.G.nodes[event_id]['log_count'] = len(logs)

    def create_edges(self):
        """
        Calculate edges based on event transitions.

        This function iterates through the sequence of event IDs and creates edges
        between consecutive events, counting their occurrences to determine weights.
        """
        self.edges_list = []
        self.edges_weight = defaultdict(int)
        log_event_id_len = len(self.log_event_id)

        for index, event_id in enumerate(self.log_event_id):
            if (index + 1) < log_event_id_len:
                self.edges_list.append((event_id, self.log_event_id[index + 1]))
                self.edges_weight[(event_id, self.log_event_id[index + 1])] += 1

    def create_weighted_edges(self):
        """
        Format edges with weights for the graph.

        This function prepares the list of weighted edges to be added to the networkx graph.
        """
        self.edges_weight_list = []
        for edge, weight in self.edges_weight.items():
            self.edges_weight_list.append((edge[0], edge[1], {'weight': weight}))

    def add_edges_to_graph(self):
        """
        Add weighted edges to the graph.

        This function incorporates the calculated weighted edges into the graph structure.
        """
        self.G.add_edges_from(self.edges_weight_list)

    def write_to_graphml(self, output_filename="reconstruction_edge_graph.graphml"):
        """
        Save the graph to a GraphML file.

        This function exports the constructed graph to a file in GraphML format.
        """
        filename_graph_output = output_filename 
        nx.write_graphml_lxml(self.G, filename_graph_output)
        print(f"[!] Graph saved to {filename_graph_output}")
        print(f"[!] Graph contains {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges.")

    def export_event_logs(self, output_filename="reconstruction_event_logs.csv"):
        """
        Exports detailed event logs to a separate CSV file.

        This function creates a detailed CSV report containing every log entry that 
        contributed to the identified events.
        """
        csv_export_data = []
        for event_id in self.event_logs.keys():
            logs = self.event_logs[event_id]
            timestamps = self.event_timestamps[event_id]
            
            for ts, log in zip(timestamps, logs):
                csv_export_data.append({
                    'event_id': event_id,
                    'event_name': self.node_labels[event_id],
                    'timestamp': ts,
                    'log': log
                })

        if csv_export_data:
            csv_export_df = pd.DataFrame(csv_export_data)
            csv_filename = output_filename
            csv_export_df.to_csv(csv_filename, index=False)
            print(f"[+] Event logs also saved to: {csv_filename}")
        else:
             print("[!] No event logs to export.")

    def run_all(self, graph_output="reconstruction_edge_graph.graphml", csv_output=None):
        """
        Execute the full graph construction pipeline.
        
        This function will run the full graph construction pipeline which consists of 6 phases:
        1. Defining Events
        2. Creating Graph Nodes
        3. Processing Log Events
        4. Adding Node Attributes
        5. Creating Edges
        6. Writing Output
        """
        if self.df.empty:
            print("[!] DataFrame is empty. Cannot build graph.")
            return

        print("[+] Defining Events")
        self.define_events()
        
        if not self.events_dict:
            print("[!] No Sigma events found. Graph will be empty.")
            return

        print("[+] Creating Graph Nodes")
        self.create_graph()
        
        print("[+] Processing Log Events")
        self.get_list_event_id()
        
        print("[+] Adding Node Attributes")
        self.add_node_attributes()
        
        print("[+] Creating Edges")
        self.create_edges()
        self.create_weighted_edges()
        self.add_edges_to_graph()
        
        print("[+] Writing Output")
        self.write_to_graphml(graph_output)

        if csv_output:
            print("[+] Exporting Event Logs")
            self.export_event_logs(csv_output)

class ReconGraph(object):
    """
    Unified facade for the complete forensic reconstruction pipeline.

    This class serves as the main entry point for the ReconGraph library, 
    coordinating the transition from raw logs to labeled data and finally 
    to a behavioral graph. It simplifies complex operations into a 
    single automated workflow.
    """
    def __init__(self, input_file, rules_dir=None, flexible_mode=True):
        self.input_file = input_file
        self.rules_dir = rules_dir
        self.flexible_mode = flexible_mode
        
    def run_all(self, graph_output="reconstruction_edge_graph.graphml", 
                csv_output=None, sigma_output=None):
        """
        Executes the full pipeline.
        
        This function will run the full execution pipeline which consists of 3 phases:
        1. Sigma Labeling
        2. Edge Graph Construction
        3. Export
        """
        print(f"[+] Starting ReconGraph Pipeline for {self.input_file}")
        
        print("[Phase 1] Sigma Labeling")
        labeler = SigmaLabel(self.input_file, self.rules_dir, flexible_mode=self.flexible_mode)
        df_labeled = labeler.run()
        
        if sigma_output:
            if sigma_output == 'AUTO':
                base_name = os.path.splitext(os.path.basename(self.input_file))[0]
                final_sigma_output = f"{base_name}_sigma_labeled.csv"
            else:
                final_sigma_output = sigma_output
                
            df_labeled.to_csv(final_sigma_output, index=False)
            print(f"Sigma-labeled data exported to: {final_sigma_output}")
            
        print("\n[Phase 2] Edge Graph Construction")
        reconstruction = EdgeGraph(df_labeled)
        reconstruction.run_all(graph_output=graph_output, csv_output=csv_output)
        print("\n[✓] Pipeline Completed Successfully")


def main():
    """
    Main execution entry point.
    Uses the ReconGraph facade to run the full pipeline.
    """
    parser = argparse.ArgumentParser(description='Reconstruct a graph from forensic timeline.')
    parser.add_argument('-f', '--file', required=True, help='Path to the input file (CSV or TXT)')
    parser.add_argument('-o', '--output', help='Output filename for the GraphML file', default='reconstruction_edge_graph.graphml')
    parser.add_argument('-r', '--rules', help='Path to the rules directory', default=None)
    parser.add_argument('--export-csv', nargs='?', const='reconstruction_event_logs.csv', default=None, help='Export detailed event logs to a separate CSV file')
    parser.add_argument('--export-sigma', nargs='?', const='AUTO', default=None, help='Export the sigma-labeled DataFrame to a CSV file')
    parser.add_argument('--strict', action='store_true', help='Disable flexible matching mode (strict validation)')
    
    args = parser.parse_args()
    
    if os.path.exists(args.file):
        pipeline = ReconGraph(
            input_file=args.file, 
            rules_dir=getattr(args, 'rules', None),
            flexible_mode=not args.strict
        )
        
        pipeline.run_all(
            graph_output=args.output,
            csv_output=args.export_csv,
            sigma_output=args.export_sigma
        )
            
    else:
        print(f"[!] File {args.file} not found. Please ensure the input file is present.")

if __name__ == '__main__':
    main()
