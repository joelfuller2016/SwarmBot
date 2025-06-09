import dash
from dash import html, dcc

def create_layout():
    """Creates the layout for the testing dashboard page."""
    return html.Div([
        html.H1("Project Test Dashboard", style={'textAlign': 'center'}),
        html.Button('Run All Tests', id='run-tests-button', n_clicks=0, className='btn btn-primary mb-3'),
        html.Hr(),
        dcc.Loading(
            id="loading-test-results",
            type="circle",
            children=html.Div(id='test-results-container')
        ),
        # Add interval component for auto-refresh
        dcc.Interval(
            id='interval-component',
            interval=5000,  # Update every 5 seconds
            n_intervals=0
        )
    ])

def register_testing_callbacks(app):
    """Registers the callbacks for the testing dashboard page."""
    # Callbacks will be added here later to update the test results
    pass

# You can add a main block to run this page standalone for testing
if __name__ == '__main__':
    app = dash.Dash(__name__)
    app.layout = create_layout()
    register_testing_callbacks(app)
    app.run_server(debug=True)