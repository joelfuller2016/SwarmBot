"""
Cost Tracking Dashboard Page for SwarmBot
Provides comprehensive visualization and reporting of LLM API costs
"""

import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


def create_cost_dashboard_layout():
    """Create the cost tracking dashboard layout"""
    return html.Div([
        html.Div([
            html.H2("LLM API Cost Tracking", className="dashboard-title"),
            html.P("Monitor and analyze your AI spending across all providers", 
                   className="dashboard-subtitle")
        ], className="page-header"),
        
        # Summary Cards Row
        html.Div([
            # Today's Cost Card
            html.Div([
                html.Div([
                    html.H4("Today's Cost", className="metric-label"),
                    html.H2(id="today-cost", children="$0.00", className="metric-value"),
                    html.P(id="today-requests", children="0 requests", className="metric-subtitle")
                ], className="metric-card-content")
            ], className="metric-card col-3"),
            
            # Monthly Cost Card
            html.Div([
                html.Div([
                    html.H4("This Month", className="metric-label"),
                    html.H2(id="month-cost", children="$0.00", className="metric-value"),
                    html.P(id="month-progress", children="0% of budget", className="metric-subtitle")
                ], className="metric-card-content")
            ], className="metric-card col-3"),
            
            # Average Cost Card
            html.Div([
                html.Div([
                    html.H4("Avg Cost/Request", className="metric-label"),
                    html.H2(id="avg-cost", children="$0.00", className="metric-value"),
                    html.P(id="total-requests", children="0 total requests", className="metric-subtitle")
                ], className="metric-card-content")
            ], className="metric-card col-3"),
            
            # Budget Alert Card
            html.Div([
                html.Div([
                    html.H4("Budget Status", className="metric-label"),
                    html.H2(id="budget-status", children="OK", className="metric-value budget-ok"),
                    html.P(id="budget-remaining", children="$0.00 remaining", className="metric-subtitle")
                ], className="metric-card-content")
            ], className="metric-card col-3")
        ], className="row metrics-row"),
        
        # Charts Row
        html.Div([
            # Daily Cost Trend Chart
            html.Div([
                html.H3("Daily Cost Trend"),
                dcc.Graph(id="daily-cost-chart")
            ], className="chart-container col-6"),
            
            # Model Usage Pie Chart
            html.Div([
                html.H3("Cost by Model"),
                dcc.Graph(id="model-cost-chart")
            ], className="chart-container col-6")
        ], className="row"),
        
        # Provider Comparison Chart
        html.Div([
            html.Div([
                html.H3("Provider Cost Comparison"),
                dcc.Graph(id="provider-comparison-chart")
            ], className="chart-container col-12")
        ], className="row"),
        
        # Top Conversations Table
        html.Div([
            html.H3("Top Cost Sessions"),
            html.Div([
                dash_table.DataTable(
                    id="top-sessions-table",
                    columns=[
                        {"name": "Session ID", "id": "session_id", "type": "text"},
                        {"name": "Total Cost", "id": "total_cost", "type": "numeric", "format": {"specifier": "$.2f"}},
                        {"name": "Requests", "id": "request_count", "type": "numeric"},
                        {"name": "Avg Cost", "id": "avg_cost_per_request", "type": "numeric", "format": {"specifier": "$.4f"}},
                        {"name": "Duration (hrs)", "id": "duration_hours", "type": "numeric"},
                        {"name": "Started", "id": "start_time", "type": "datetime"}
                    ],
                    data=[],
                    sort_action="native",
                    style_cell={'textAlign': 'left'},
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    page_size=10
                )
            ], className="table-container")
        ], className="row"),
        
        # Export Section
        html.Div([
            html.H3("Export Cost Data"),
            html.Div([
                html.Label("Date Range:"),
                dcc.DatePickerRange(
                    id="export-date-range",
                    start_date=(datetime.now() - timedelta(days=30)).date(),
                    end_date=datetime.now().date(),
                    display_format='YYYY-MM-DD',
                    style={'marginLeft': '10px', 'marginRight': '20px'}
                ),
                html.Button("Export CSV", id="export-csv-button", className="btn btn-primary"),
                html.Button("Export JSON", id="export-json-button", className="btn btn-secondary"),
                dcc.Download(id="download-cost-data")
            ], className="export-controls")
        ], className="row export-section"),
        
        # Auto-refresh interval
        dcc.Interval(
            id='cost-interval-component',
            interval=5*1000,  # Update every 5 seconds
            n_intervals=0
        )
    ])


def register_cost_dashboard_callbacks(app, integration):
    """Register callbacks for cost tracking dashboard"""
    
    @app.callback(
        [Output('today-cost', 'children'),
         Output('today-requests', 'children'),
         Output('month-cost', 'children'),
         Output('month-progress', 'children'),
         Output('avg-cost', 'children'),
         Output('total-requests', 'children'),
         Output('budget-status', 'children'),
         Output('budget-status', 'className'),
         Output('budget-remaining', 'children')],
        [Input('cost-interval-component', 'n_intervals')]
    )
    def update_cost_metrics(n):
        """Update cost tracking metrics"""
        try:
            # Get cost tracking data from integration
            cost_data = integration.get_cost_tracking_data()
            
            # Today's metrics
            today_cost = f"${cost_data['today']['total_cost']:.2f}"
            today_requests = f"{cost_data['today']['request_count']} requests"
            
            # Monthly metrics
            month_cost = f"${cost_data['month']['total_cost']:.2f}"
            budget_threshold = cost_data['budget']['threshold']
            month_percentage = (cost_data['month']['total_cost'] / budget_threshold * 100) if budget_threshold > 0 else 0
            month_progress = f"{month_percentage:.1f}% of budget"
            
            # Average cost
            total_requests = cost_data['all_time']['request_count']
            avg_cost_value = cost_data['all_time']['avg_cost_per_request']
            avg_cost = f"${avg_cost_value:.4f}"
            total_requests_text = f"{total_requests} total requests"
            
            # Budget status
            if cost_data['budget']['exceeded']:
                budget_status = "EXCEEDED"
                budget_class = "metric-value budget-exceeded"
            elif month_percentage > 80:
                budget_status = "WARNING"
                budget_class = "metric-value budget-warning"
            else:
                budget_status = "OK"
                budget_class = "metric-value budget-ok"
            
            budget_remaining = f"${cost_data['budget']['remaining_budget']:.2f} remaining"
            
            return (today_cost, today_requests, month_cost, month_progress,
                   avg_cost, total_requests_text, budget_status, budget_class, budget_remaining)
                   
        except Exception as e:
            logger.error(f"Error updating cost metrics: {e}")
            return ("$0.00", "0 requests", "$0.00", "0% of budget", 
                   "$0.00", "0 total requests", "ERROR", "metric-value budget-error", "$0.00 remaining")
    
    @app.callback(
        Output('daily-cost-chart', 'figure'),
        [Input('cost-interval-component', 'n_intervals')]
    )
    def update_daily_cost_chart(n):
        """Update daily cost trend chart"""
        try:
            cost_data = integration.get_cost_tracking_data()
            daily_costs = cost_data.get('daily_costs', [])
            
            if not daily_costs:
                return create_empty_chart("No cost data available")
            
            # Convert to DataFrame for easier plotting
            df = pd.DataFrame(daily_costs)
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by date and sum costs
            daily_totals = df.groupby('date')['total_cost'].sum().reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_totals['date'],
                y=daily_totals['total_cost'],
                mode='lines+markers',
                name='Daily Cost',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=8)
            ))
            
            fig.update_layout(
                title="Daily Cost Trend (Last 30 Days)",
                xaxis_title="Date",
                yaxis_title="Cost ($)",
                hovermode='x unified',
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error updating daily cost chart: {e}")
            return create_empty_chart("Error loading chart")
    
    @app.callback(
        Output('model-cost-chart', 'figure'),
        [Input('cost-interval-component', 'n_intervals')]
    )
    def update_model_cost_chart(n):
        """Update model cost distribution chart"""
        try:
            cost_data = integration.get_cost_tracking_data()
            model_stats = cost_data.get('model_usage', [])
            
            if not model_stats:
                return create_empty_chart("No model usage data")
            
            df = pd.DataFrame(model_stats)
            
            fig = go.Figure(data=[go.Pie(
                labels=df['model'],
                values=df['total_cost'],
                hole=.3,
                textinfo='label+percent',
                textposition='auto'
            )])
            
            fig.update_layout(
                title="Cost Distribution by Model",
                template='plotly_white'
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error updating model cost chart: {e}")
            return create_empty_chart("Error loading chart")
    
    @app.callback(
        Output('provider-comparison-chart', 'figure'),
        [Input('cost-interval-component', 'n_intervals')]
    )
    def update_provider_comparison_chart(n):
        """Update provider comparison chart"""
        try:
            cost_data = integration.get_cost_tracking_data()
            model_stats = cost_data.get('model_usage', [])
            
            if not model_stats:
                return create_empty_chart("No provider data")
            
            # Group by provider
            df = pd.DataFrame(model_stats)
            
            # Extract provider from model names (assuming format like "gpt-4" for OpenAI)
            def get_provider(model):
                if 'gpt' in model.lower():
                    return 'OpenAI'
                elif 'claude' in model.lower():
                    return 'Anthropic'
                elif 'gemini' in model.lower():
                    return 'Google'
                elif 'llama' in model.lower() or 'mixtral' in model.lower():
                    return 'Groq'
                else:
                    return 'Other'
            
            df['provider'] = df['model'].apply(get_provider)
            
            provider_stats = df.groupby('provider').agg({
                'total_cost': 'sum',
                'total_requests': 'sum',
                'total_input_tokens': 'sum',
                'total_output_tokens': 'sum'
            }).reset_index()
            
            provider_stats['avg_cost_per_request'] = provider_stats['total_cost'] / provider_stats['total_requests']
            
            fig = go.Figure()
            
            # Add bars for total cost
            fig.add_trace(go.Bar(
                name='Total Cost',
                x=provider_stats['provider'],
                y=provider_stats['total_cost'],
                yaxis='y',
                offsetgroup=1
            ))
            
            # Add line for average cost per request
            fig.add_trace(go.Scatter(
                name='Avg Cost/Request',
                x=provider_stats['provider'],
                y=provider_stats['avg_cost_per_request'],
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='red', width=2),
                marker=dict(size=10)
            ))
            
            fig.update_layout(
                title="Provider Cost Comparison",
                xaxis_title="Provider",
                yaxis=dict(
                    title="Total Cost ($)",
                    side="left"
                ),
                yaxis2=dict(
                    title="Avg Cost per Request ($)",
                    overlaying="y",
                    side="right"
                ),
                hovermode='x',
                template='plotly_white',
                legend=dict(x=0.01, y=0.99)
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"Error updating provider comparison chart: {e}")
            return create_empty_chart("Error loading chart")
    
    @app.callback(
        Output('top-sessions-table', 'data'),
        [Input('cost-interval-component', 'n_intervals')]
    )
    def update_top_sessions_table(n):
        """Update top cost sessions table"""
        try:
            cost_data = integration.get_cost_tracking_data()
            top_conversations = cost_data.get('top_conversations', [])
            
            # Format data for table
            for conv in top_conversations:
                # Truncate session ID for display
                if len(conv.get('session_id', '')) > 12:
                    conv['session_id'] = conv['session_id'][:12] + '...'
                
                # Format datetime
                if 'start_time' in conv:
                    try:
                        dt = datetime.fromisoformat(conv['start_time'].replace('Z', '+00:00'))
                        conv['start_time'] = dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        pass
            
            return top_conversations[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Error updating top sessions table: {e}")
            return []
    
    @app.callback(
        Output('download-cost-data', 'data'),
        [Input('export-csv-button', 'n_clicks'),
         Input('export-json-button', 'n_clicks')],
        [State('export-date-range', 'start_date'),
         State('export-date-range', 'end_date')],
        prevent_initial_call=True
    )
    def export_cost_data(csv_clicks, json_clicks, start_date, end_date):
        """Handle cost data export"""
        try:
            ctx = dash.callback_context
            if not ctx.triggered:
                return None
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            
            if button_id == 'export-csv-button':
                # Export as CSV
                csv_data = integration.export_cost_data_csv(start_date, end_date)
                return dict(content=csv_data, filename=f"cost_data_{start_date}_to_{end_date}.csv")
            
            elif button_id == 'export-json-button':
                # Export as JSON
                json_data = integration.export_cost_data_json(start_date, end_date)
                return dict(content=json_data, filename=f"cost_data_{start_date}_to_{end_date}.json")
                
        except Exception as e:
            logger.error(f"Error exporting cost data: {e}")
            return None


def create_empty_chart(message):
    """Create an empty chart with a message"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        template='plotly_white'
    )
    return fig
