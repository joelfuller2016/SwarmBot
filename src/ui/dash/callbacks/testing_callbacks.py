import dash
from dash import html, dcc, Dash
from dash.dependencies import Input, Output
import os

# Try to import TestRunnerService with fallback
try:
    from src.core.test_runner_service import TestRunnerService
except ImportError:
    TestRunnerService = None

def generate_results_table(test_results):
    """Generates an HTML table from the test results dictionary."""
    if not test_results:
        return html.P("No tests discovered or run yet.")

    header = [html.Thead(html.Tr([html.Th("Test File"), html.Th("Status"), html.Th("Duration (s)"), html.Th("Details")]))]
    
    rows = []
    for test_name, result in test_results.items():
        status = result.get('status', 'unknown')
        status_style = {'fontWeight': 'bold'}
        if status == 'passed':
            status_style['color'] = 'green'
        elif status == 'failed':
            status_style['color'] = 'red'

        details = html.Details([
            html.Summary('View Output'),
            html.Pre(html.Code(result.get('output', 'No output.')))
        ])

        rows.append(html.Tr([
            html.Td(test_name),
            html.Td(status.upper(), style=status_style),
            html.Td(result.get('duration', 'N/A')),
            html.Td(details)
        ]))

    body = [html.Tbody(rows)]
    
    return html.Table(header + body, style={'width': '100%', 'borderCollapse': 'collapse'})


def register_testing_page_callbacks(app: Dash):
    """Registers callbacks for the testing dashboard."""
    @app.callback(
        Output('test-results-container', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_test_results(n):
        # Access the service from the app context
        service = dash.get_app().test_runner_service
        
        # Handle case where TestRunnerService is not available
        if service is None:
            return html.Div([
                html.P("Test Runner Service is not available.", style={'color': 'red'}),
                html.P("Please ensure TestRunnerService is properly installed and configured.")
            ], style={'textAlign': 'center', 'marginTop': '50px'})
        
        if service.is_running:
            return html.Div([
                html.P("Tests are currently running..."),
                dcc.Loading(type="circle"),
            ], style={'textAlign': 'center', 'marginTop': '50px'})

        results = service.test_results
        
        if not results:
             return html.P("No test results available. The initial test run may still be in progress or no tests were found.", style={'textAlign': 'center', 'marginTop': '50px'})

        return generate_results_table(results)