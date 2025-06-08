# WebSocket Troubleshooting Guide

## Common Issues and Solutions

### 1. Connection Issues

#### Issue: WebSocket Connection Fails Immediately
**Symptoms:**
- Status indicator shows red (disconnected)
- Browser console shows "WebSocket connection failed"
- Fallback to polling mode activates

**Solutions:**
1. **Check if the dashboard is running:**
   ```bash
   ps aux | grep swarmbot
   netstat -an | grep 8050
   ```

2. **Verify WebSocket is enabled:**
   ```python
   # Check .env file
   WEBSOCKET_ENABLED=true
   ```

3. **Test direct connection:**
   ```javascript
   // In browser console
   const testSocket = new WebSocket('ws://localhost:8050/socket.io/?EIO=4&transport=websocket');
   testSocket.onopen = () => console.log('Direct WebSocket works!');
   testSocket.onerror = (e) => console.error('WebSocket error:', e);
   ```

4. **Check firewall/antivirus:**
   - Temporarily disable firewall
   - Add exception for port 8050
   - Check antivirus WebSocket scanning settings

#### Issue: WebSocket Connects but Immediately Disconnects
**Symptoms:**
- Brief green status, then red
- Rapid reconnection attempts
- Console shows "disconnect" events

**Solutions:**
1. **Check server logs:**
   ```bash
   tail -f swarmbot_dashboard.log | grep -i websocket
   ```

2. **Verify eventlet is installed:**
   ```bash
   pip show eventlet
   # If missing:
   pip install eventlet>=0.33.0
   ```

3. **Check for port conflicts:**
   ```bash
   lsof -i :8050
   ```

### 2. Performance Issues

#### Issue: High Latency Despite WebSocket Connection
**Symptoms:**
- Updates take > 100ms
- Connection quality score < 70
- UI feels sluggish

**Solutions:**
1. **Check event batching configuration:**
   ```python
   # In websocket_events.py
   BATCH_INTERVAL = 0.1  # Reduce for lower latency
   MAX_BATCH_SIZE = 50   # Reduce for more frequent updates
   ```

2. **Monitor server resources:**
   ```bash
   htop  # Check CPU and memory
   iotop # Check disk I/O
   ```

3. **Optimize event emission:**
   ```python
   # Avoid emitting large payloads
   # Compress data if > 1KB
   ```

#### Issue: Memory Usage Increases Over Time
**Symptoms:**
- Browser memory grows continuously
- Dashboard becomes slow after hours
- Page crashes eventually

**Solutions:**
1. **Check for event listener leaks:**
   ```javascript
   // Ensure cleanup on component unmount
   componentWillUnmount() {
       socket.off('event_name');
   }
   ```

2. **Limit event history:**
   ```python
   # Clear old events periodically
   if len(self.event_history) > 1000:
       self.event_history = self.event_history[-500:]
   ```

### 3. Browser-Specific Issues

#### Issue: WebSocket Works in Chrome but Not Firefox
**Solutions:**
1. **Check browser console for errors**
2. **Verify CORS settings:**
   ```python
   socketio = SocketIO(
       cors_allowed_origins="*"  # Or specific origins
   )
   ```
3. **Test with different Firefox versions**
4. **Disable Firefox enhanced tracking protection**

#### Issue: Safari WebSocket Disconnects Frequently
**Solutions:**
1. **Increase ping interval:**
   ```python
   socketio = SocketIO(
       ping_interval=10,  # More frequent pings
       ping_timeout=5
   )
   ```
2. **Enable WebSocket in Safari Developer menu**

### 4. Proxy and Network Issues

#### Issue: WebSocket Fails Behind Corporate Proxy
**Symptoms:**
- Works on direct connection
- Fails on corporate network
- Falls back to polling

**Solutions:**
1. **Configure proxy WebSocket support**
2. **Use WSS (WebSocket Secure):**
   ```nginx
   location /socket.io {
       proxy_pass https://localhost:8050/socket.io;
       proxy_ssl_verify off;
   }
   ```
3. **Contact IT for WebSocket whitelist**

#### Issue: WebSocket Blocked by Firewall
**Solutions:**
1. **Use standard HTTPS port (443)**
2. **Enable WebSocket over HTTP/2**
3. **Configure fallback to long-polling**

### 5. Development Issues

#### Issue: WebSocket Tests Failing
**Error:** `AttributeError: 'SocketIOTestClient' object has no attribute 'on'`

**Solution:**
```python
# Old (incorrect):
@client.on('event')
def handler(data):
    pass

# New (correct):
received = client.get_received()
events = [msg for msg in received if msg.get('name') == 'event']
```

#### Issue: Cannot Debug WebSocket Events
**Solutions:**
1. **Enable debug logging:**
   ```python
   import logging
   logging.getLogger('socketio').setLevel(logging.DEBUG)
   logging.getLogger('engineio').setLevel(logging.DEBUG)
   ```

2. **Use browser WebSocket inspector:**
   - Chrome: F12 → Network → WS → Select connection
   - Firefox: F12 → Network → Filter: WS

### 6. Production Issues

#### Issue: WebSocket Fails with SSL/HTTPS
**Solutions:**
1. **Update client connection:**
   ```javascript
   const socket = io('https://your-domain.com', {
       secure: true,
       rejectUnauthorized: false  // Only for self-signed certs
   });
   ```

2. **Verify proxy SSL configuration:**
   ```nginx
   location /socket.io {
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```

#### Issue: Load Balancer Drops WebSocket Connections
**Solutions:**
1. **Enable session affinity (sticky sessions)**
2. **Increase load balancer timeout:**
   ```yaml
   # AWS ALB example
   stickiness:
     enabled: true
     duration_seconds: 86400
   ```

### Diagnostic Commands

#### Check WebSocket Connection Status
```javascript
// Browser console
if (window.swarmSocket) {
    console.log('Connected:', window.swarmSocket.connected);
    console.log('Transport:', window.swarmSocket.io.engine.transport.name);
    console.log('Latency:', window.wsLatency + 'ms');
}
```

#### Monitor WebSocket Traffic
```bash
# Linux/Mac
sudo tcpdump -i any -s 0 -A 'tcp port 8050'

# Windows (with Wireshark)
# Filter: tcp.port == 8050
```

#### Test WebSocket Endpoint
```python
# test_websocket.py
import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('Connected!')

@sio.event
def disconnect():
    print('Disconnected!')

try:
    sio.connect('http://localhost:8050')
    sio.wait()
except Exception as e:
    print(f'Connection failed: {e}')
```

### Performance Metrics

#### Check Connection Quality
```javascript
// Browser console
function checkConnectionQuality() {
    const start = Date.now();
    window.swarmSocket.emit('ping', { timestamp: start });
    
    window.swarmSocket.once('pong', (data) => {
        const latency = Date.now() - start;
        console.log(`Latency: ${latency}ms`);
        
        if (latency < 50) {
            console.log('Connection: Excellent');
        } else if (latency < 150) {
            console.log('Connection: Good');
        } else if (latency < 300) {
            console.log('Connection: Fair');
        } else {
            console.log('Connection: Poor');
        }
    });
}
```

### Emergency Procedures

#### Force Fallback to Polling
```javascript
// Browser console
window.swarmSocket.io.opts.transports = ['polling'];
window.swarmSocket.disconnect();
window.swarmSocket.connect();
```

#### Clear WebSocket Event Queue
```javascript
// Browser console
window.wsQueuedEvents = [];
console.log('Event queue cleared');
```

#### Reset Connection
```javascript
// Browser console
window.swarmSocket.disconnect();
window.wsReconnectAttempts = 0;
setTimeout(() => {
    window.swarmSocket.connect();
}, 1000);
```

### Getting Help

If issues persist:

1. **Collect Diagnostics:**
   ```bash
   # System info
   python --version
   pip show flask-socketio
   
   # Logs
   tail -n 100 swarmbot_dashboard.log > debug_info.txt
   
   # Browser console
   # Right-click → Save as... → console_log.txt
   ```

2. **Check GitHub Issues:**
   - Search existing issues
   - Create new issue with diagnostics

3. **Community Support:**
   - SwarmBot Discord/Slack
   - Stack Overflow with tags: `swarmbot`, `flask-socketio`

### Prevention Tips

1. **Regular Monitoring:**
   - Set up alerts for connection failures
   - Monitor WebSocket metrics
   - Track client connection counts

2. **Gradual Rollout:**
   - Test with small user group first
   - Monitor performance metrics
   - Scale gradually

3. **Fallback Planning:**
   - Always maintain polling fallback
   - Test fallback regularly
   - Document fallback behavior

Remember: WebSocket issues often stem from network infrastructure rather than application code. Always test in the actual deployment environment.