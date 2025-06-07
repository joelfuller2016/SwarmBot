# SwarmBot Control Center - Complete UI Manual

## Table of Contents
1. [Overview](#overview)
2. [Dashboard Pages](#dashboard-pages)
3. [Settings Page](#settings-page)
4. [Agents Page](#agents-page)
5. [Tasks Page](#tasks-page)
6. [Performance Analytics](#performance-analytics)
7. [Quick Actions](#quick-actions)
8. [System Status](#system-status)
9. [UI Elements Reference](#ui-elements-reference)
10. [Testing Guide](#testing-guide)

## Overview

The SwarmBot Control Center is a sophisticated web-based interface for managing and monitoring AI agent swarms. Built with Dash and Plotly, it provides real-time visualization and control over multi-agent systems running on the MCP protocol.

### Access Methods
- **Primary**: `python swarmbot.py --ui`
- **Alternative**: `python launch_dashboard.py`
- **URL**: `http://localhost:8050`
- **Default Port**: 8050

### Design Theme
- **Color Scheme**: Dark mode with purple accent colors
- **Primary Background**: #0d1117 (GitHub dark)
- **Card Background**: #161b22
- **Accent Colors**: Purple gradient (#667eea to #764ba2)
- **Status Colors**:
  - Idle: #58a6ff (blue)
  - Busy: #f97316 (orange)
  - Processing: #8b5cf6 (purple)
  - Error: #ef4444 (red)
  - Offline: #6b7280 (gray)

## Dashboard Pages

### Navigation Bar
Located at the top of the interface with the following elements:
- **Logo**: SwarmBot icon and branding
- **Page Links**: Dashboard, Agents, Tasks, Performance, Settings
- **System Status**: "System Online" indicator with green status light

## Settings Page

The Settings page is the control hub for configuring agent behavior and system parameters.

### Agent Creation Panel
**Purpose**: Create new AI agents with specific configurations

**Fields**:
1. **Agent Type** (Dropdown)
   - Options loaded from agent templates
   - Default: General purpose agent
   
2. **Agent Name** (Text Input)
   - Placeholder: "Enter agent name"
   - Validation: Unique names required
   
3. **Create Agent** (Button)
   - Primary action button
   - Creates and initializes new agent instance

### Task Submission Panel
**Purpose**: Submit new tasks to the agent swarm

**Fields**:
1. **Task Type** (Text Input)
   - Free-form task categorization
   - Used for routing to appropriate agents
   
2. **Description** (Text Area)
   - Multi-line task description
   - Supports markdown formatting
   
3. **Priority** (Dropdown)
   - Options: High, Medium, Low
   - Affects task scheduling order
   
4. **Submit Task** (Button)
   - Adds task to the global queue
   - Triggers agent assignment logic

### Swarm Configuration Panel
**Purpose**: Configure system-wide behavior and limits

**Settings**:
1. **Load Balancing** (Toggle Switch)
   - When ON: Distributes tasks evenly across agents
   - When OFF: Tasks assigned to first available agent
   
2. **Auto Scaling** (Toggle Switch)
   - When ON: Automatically creates/destroys agents based on load
   - When OFF: Manual agent management only
   
3. **Max Retries** (Number Input)
   - Default: 3
   - Range: 0-10
   - Number of times to retry failed tasks
   
4. **Task Timeout (s)** (Number Input)
   - Default: 300 seconds (5 minutes)
   - Range: 30-3600 seconds
   - Maximum time for task execution

## Agents Page

The Agents page provides comprehensive monitoring of all active agents in the swarm.

### Agent Monitor Cards
Four metric cards displaying real-time statistics:

1. **Total Agents Card**
   - Icon: Group of people
   - Shows total registered agents
   - Background: Purple gradient
   
2. **Active Card**
   - Icon: Green activity indicator
   - Shows agents currently processing tasks
   - Updates in real-time
   
3. **Idle Card**
   - Icon: Pause symbol
   - Shows agents waiting for tasks
   - Click to view idle agent list
   
4. **Errors Card**
   - Icon: Warning triangle
   - Shows agents in error state
   - Click for error details

### Active Agents Section
**Display Format**: List or grid view
- Agent cards showing:
  - Agent ID and name
  - Current status (color-coded)
  - Assigned task (if any)
  - Performance metrics
  - Last activity timestamp

### Agent Communication Network
**Visualization**: Interactive network graph
- **Nodes**: Represent individual agents
- **Edges**: Show communication channels
- **Colors**: Indicate agent status
- **Interactions**:
  - Hover: Show agent details
  - Click: Focus on agent connections
  - Drag: Rearrange network layout

## Tasks Page

The Tasks page manages and monitors all tasks in the system.

### Task Management Cards
Four summary cards showing:

1. **Total Tasks**
   - Icon: List
   - All tasks in the system
   - Includes completed and pending
   
2. **Completed**
   - Icon: Checkmark
   - Successfully finished tasks
   - Success rate percentage
   
3. **In Progress**
   - Icon: Spinning gear
   - Currently executing tasks
   - Shows assigned agents
   
4. **Failed**
   - Icon: X mark
   - Tasks that encountered errors
   - Click for failure details

### Task Queue
**Purpose**: Display pending tasks awaiting assignment

**Information Shown**:
- Task ID
- Type and priority (color-coded borders)
- Description preview
- Submission timestamp
- Estimated wait time

**Priority Indicators**:
- High: Red left border (#ef4444)
- Medium: Orange left border (#f59e0b)
- Low: Green left border (#10b981)

### Task Timeline
**Visualization**: Gantt-style chart showing:
- Task execution over time
- Agent assignments
- Task dependencies
- Completion status
- Interactive hover details

## Performance Analytics

The Performance page provides system-wide metrics and analytics.

### CPU Usage Chart
**Type**: Real-time line graph
- **X-axis**: Time (last 5 minutes)
- **Y-axis**: CPU percentage (0-100%)
- **Features**:
  - Auto-scrolling timeline
  - Hover for exact values
  - System vs. SwarmBot usage

### Memory Usage Chart
**Type**: Real-time line graph
- **X-axis**: Time (last 5 minutes)
- **Y-axis**: Memory in MB
- **Features**:
  - Peak memory indicators
  - Memory leak detection
  - Per-agent breakdown available

### Task Distribution
**Type**: Pie or donut chart
- Shows task allocation by:
  - Task type
  - Priority level
  - Agent assignment
  - Completion status

### Agent Utilization
**Type**: Bar chart
- **X-axis**: Individual agents
- **Y-axis**: Utilization percentage
- **Colors**: 
  - Green: Optimal (50-80%)
  - Yellow: Low (<50%)
  - Red: Overloaded (>80%)

## Quick Actions

Located in the left sidebar on all pages:

### Buttons
1. **New Agent**
   - Quick access to agent creation
   - Opens modal with creation form
   
2. **New Task**
   - Quick task submission
   - Pre-fills with default values
   
3. **Stop All**
   - Emergency stop for all agents
   - Requires confirmation
   - Saves current state

## System Status

Displayed in the left sidebar below Quick Actions:

### Metrics
1. **Active Agents**: Current count
2. **Running Tasks**: In-progress count
3. **CPU Usage**: System percentage
4. **Memory**: Used/Total in MB/GB

### Recent Activity
- Scrollable log of recent events
- Includes:
  - Agent status changes
  - Task completions
  - System events
  - Error notifications

## UI Elements Reference

### Color Coding
- **Success**: #10b981 (green)
- **Warning**: #f59e0b (orange)
- **Error**: #ef4444 (red)
- **Info**: #3b82f6 (blue)
- **Processing**: #8b5cf6 (purple)

### Interactive Elements
1. **Cards**: Hover effect with elevation change
2. **Buttons**: Ripple effect on click
3. **Toggles**: Smooth transition animations
4. **Charts**: Interactive tooltips and zoom

### Responsive Design
- Breakpoints:
  - Desktop: > 1200px
  - Tablet: 768px - 1200px
  - Mobile: < 768px (limited functionality)

## Testing Guide

### Functional Tests

1. **Agent Creation Test**
   ```
   1. Navigate to Settings page
   2. Select agent type from dropdown
   3. Enter unique agent name
   4. Click "Create Agent"
   5. Verify agent appears in Agents page
   6. Check system status updates
   ```

2. **Task Submission Test**
   ```
   1. Navigate to Settings page
   2. Enter task type
   3. Add task description
   4. Select priority
   5. Click "Submit Task"
   6. Verify task appears in queue
   7. Monitor task assignment
   ```

3. **Real-time Update Test**
   ```
   1. Open dashboard in multiple browsers
   2. Create agent in one browser
   3. Verify update appears in all browsers
   4. Submit task and monitor distribution
   ```

4. **Performance Monitoring Test**
   ```
   1. Navigate to Performance page
   2. Create multiple agents
   3. Submit batch of tasks
   4. Monitor CPU/Memory graphs
   5. Verify metrics accuracy
   ```

5. **Error Handling Test**
   ```
   1. Submit invalid task data
   2. Create duplicate agent names
   3. Exceed system limits
   4. Verify error messages display
   5. Check error recovery
   ```

### UI Element Tests

1. **Navigation Test**
   - Click all navigation links
   - Verify correct page loads
   - Check active page highlighting
   
2. **Responsive Test**
   - Resize browser window
   - Test on different devices
   - Verify layout adaptability
   
3. **Interactive Element Test**
   - Test all buttons
   - Verify dropdowns populate
   - Check toggle switches
   - Validate form inputs

### Performance Tests

1. **Load Test**
   - Create 50+ agents
   - Submit 100+ tasks
   - Monitor UI responsiveness
   
2. **Real-time Data Test**
   - Enable auto-refresh
   - Monitor update frequency
   - Check data consistency
   
3. **Memory Leak Test**
   - Run dashboard for extended period
   - Monitor browser memory usage
   - Verify cleanup on page changes

## Troubleshooting

### Common Issues

1. **Dashboard Won't Start**
   - Check dependencies: `pip install dash plotly dash-bootstrap-components`
   - Verify port 8050 is available
   - Check for Python errors in console

2. **No Data Displayed**
   - Verify SwarmBot core is running
   - Check agent infrastructure exists
   - Confirm WebSocket connection

3. **Slow Updates**
   - Adjust update interval in settings
   - Check system resources
   - Reduce number of active agents

4. **Chart Rendering Issues**
   - Clear browser cache
   - Update Plotly version
   - Check browser compatibility

### Debug Mode
Enable debug mode for detailed logging:
```bash
python swarmbot.py --ui --debug
```

## Future Enhancements

1. **Planned Features**
   - Agent templates marketplace
   - Task dependency visualization
   - Historical data export
   - Custom dashboard layouts
   - Mobile app companion

2. **Performance Improvements**
   - WebSocket implementation
   - Data caching layer
   - Lazy loading for large datasets
   - GPU acceleration for graphs

3. **Integration Expansions**
   - REST API endpoints
   - Webhook notifications
   - Third-party monitoring tools
   - Cloud deployment options

## Conclusion

The SwarmBot Control Center provides a comprehensive interface for managing AI agent swarms. While currently displaying simulated data, the UI framework is fully functional and ready for integration with real agent systems. Regular testing and monitoring ensure optimal performance and user experience.

For technical implementation details, see `UI_IMPLEMENTATION_REQUIREMENTS.md`.
For development roadmap, see `UI_IMPLEMENTATION_ROADMAP.md`.