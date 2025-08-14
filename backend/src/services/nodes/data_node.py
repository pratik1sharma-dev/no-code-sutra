from typing import Dict, Any
from datetime import datetime


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        input_source = state.get('input_source', '')
        output_name = state.get('output_name', 'post_data')
        operation = state.get('operation', 'pass_through')

        print(f"Data node processing - input_source: {input_source}, output_name: {output_name}")
        print(f"Available state keys: {list(state.keys())}")

        input_data = None
        if input_source:
            if input_source in state:
                input_data = state[input_source]
                print(f"Found input data from specified source '{input_source}': {type(input_data)}")
            else:
                print(f"Warning: Specified input source '{input_source}' not found in state")

        if input_data is None:
            for key in ['result', 'output', 'content', 'text', 'data']:
                if key in state and state[key]:
                    input_data = state[key]
                    print(f"Using content from '{key}': {type(input_data)}")
                    break

        if input_data is None and 'input_data' in state:
            input_data = state['input_data']
            print(f"Using input_data from state: {type(input_data)}")

        if input_data is None:
            input_data = "No input data available"
            print("Warning: No input data found")

        if operation == 'pass_through':
            transformed_data = input_data
        elif operation == 'transform':
            transformed_data = _transform_data(input_data)
        elif operation == 'filter':
            transformed_data = _filter_data(input_data, state.get('filter_criteria', {}))
        elif operation == 'aggregate':
            transformed_data = _aggregate_data(input_data, state.get('aggregation_type', 'sum'))
        else:
            transformed_data = input_data

        state[output_name] = transformed_data
        state['output_data'] = transformed_data
        state['content'] = transformed_data
        state['post_data'] = transformed_data
        state['operation'] = operation
        state['input_source'] = input_source
        state['output_name'] = output_name
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        print(f"Error in data node: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state


def _transform_data(data: Dict[str, Any]) -> Dict[str, Any]:
    transformed: Dict[str, Any] = {}
    for key, value in data.items() if isinstance(data, dict) else []:
        if isinstance(value, str):
            transformed[key] = value.upper()
        elif isinstance(value, (int, float)):
            transformed[key] = value * 2
        else:
            transformed[key] = value
    return transformed


def _filter_data(data: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
    filtered: Dict[str, Any] = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if key in criteria:
                if isinstance(value, str) and str(criteria[key]).lower() in value.lower():
                    filtered[key] = value
                elif value == criteria[key]:
                    filtered[key] = value
    return filtered


def _aggregate_data(data: Dict[str, Any], agg_type: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    if isinstance(data, dict):
        numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
        if agg_type == 'sum':
            result['sum'] = sum(numeric_values) if numeric_values else 0
        elif agg_type == 'count':
            result['count'] = len(numeric_values)
        else:
            result['sum'] = sum(numeric_values) if numeric_values else 0
            result['count'] = len(numeric_values)
    return result