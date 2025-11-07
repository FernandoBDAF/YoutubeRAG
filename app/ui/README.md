# GraphRAG Pipeline Visualization UI

**Achievement 8.3: User Guide**

Comprehensive UI suite for the GraphRAG Pipeline Visualization system.

---

## 📋 Overview

This directory contains 13 interactive web-based user interfaces for monitoring, controlling, and exploring the GraphRAG pipeline and knowledge graph.

### What's Inside

| Dashboard                          | Purpose                    | Key Features                                    |
| ---------------------------------- | -------------------------- | ----------------------------------------------- |
| **pipeline_control.html**          | Control pipeline execution | Start/stop/resume pipelines, configure settings |
| **pipeline_monitor.html**          | Real-time progress         | Live stage progress, SSE streaming              |
| **pipeline_history.html**          | Pipeline execution history | Browse past runs, filter, export CSV            |
| **stage_flow.html**                | Stage contribution viz     | Data flow visualization, stage stats            |
| **entity_browser.html**            | Entity exploration         | Search, filter, view entity details             |
| **relationship_viewer.html**       | Relationship exploration   | Browse triples, filter by predicate             |
| **community_explorer.html**        | Community exploration      | Browse clusters, multi-resolution               |
| **graph_viewer.html**              | Interactive graph          | D3.js visualization, ego networks, export       |
| **experiment_comparison.html**     | Compare experiments        | Side-by-side metrics, charts                    |
| **experiment_visualization.html**  | Experiment charts          | Histograms, scatter plots, trends               |
| **quality_metrics_dashboard.html** | Quality metrics            | Per-stage quality, trends                       |
| **graph_statistics.html**          | Graph analytics            | Degree distribution, type stats                 |
| **performance_dashboard.html**     | Performance metrics        | Duration, throughput, trends                    |

---

## 🚀 Quick Start

### Prerequisites

1. **MongoDB** running with GraphRAG data
2. **API servers** running:

   ```bash
   # Start API servers (each in separate terminal)
   python app/api/pipeline_control.py 8000
   python app/api/entities.py 8001
   python app/api/communities.py 8002
   python app/api/export.py 8003
   ```

3. **Web server** (optional but recommended):
   ```bash
   cd app/ui
   python -m http.server 8080
   ```

### Access the UIs

**Via Web Server:**

- http://localhost:8080/pipeline_control.html
- http://localhost:8080/entity_browser.html
- http://localhost:8080/graph_viewer.html
- (etc.)

**Via File System:**

- Open HTML files directly in browser (works but may have CORS issues with API calls)

---

## 📊 Dashboard Guide

### 1. Pipeline Control (`pipeline_control.html`)

**Purpose:** Remote control of pipeline execution

**Key Features:**

- **Start New Pipeline**: Configure and launch pipeline runs
- **Real-Time Status**: View current pipeline state with auto-refresh
- **Cancel/Resume**: Stop or resume pipeline execution
- **Log Viewer**: Monitor pipeline logs in real-time
- **JSON Config Editor**: Advanced configuration with syntax validation

**Usage:**

```
1. Enter database name (e.g., "mongo_hack")
2. Optionally set experiment ID
3. Configure stages (leave empty for all)
4. Edit JSON config if needed
5. Click "Start Pipeline"
6. Monitor status and logs
```

**API Endpoint:** `:8000/api/pipeline/*`

---

### 2. Pipeline Monitor (`pipeline_monitor.html`)

**Purpose:** Real-time pipeline progress visualization

**Key Features:**

- **Live Progress Bars**: Per-stage progress with percentage
- **Status Indicators**: Visual status (idle, running, completed, failed)
- **Message Stream**: Real-time log messages
- **Error Alerts**: Immediate error notifications

**Usage:**

```
1. Open the page (auto-connects to SSE stream)
2. Watch real-time updates as pipeline executes
3. Monitor stage progress and completion
4. View errors as they occur
```

**Technology:** Server-Sent Events (SSE) for streaming

---

### 3. Pipeline History (`pipeline_history.html`)

**Purpose:** Browse past pipeline executions

**Key Features:**

- **History Table**: All pipeline runs with timestamps
- **Filtering**: By status, experiment_id
- **Pagination**: Navigate large result sets
- **Export**: Download history as CSV
- **Links**: Jump to pipeline control or experiment comparison

**Usage:**

```
1. Enter database name
2. Apply filters (optional)
3. Click "Load History"
4. Browse paginated results
5. Click "View" for details or "Compare" for analysis
```

**Columns:** Pipeline ID, Status, Started At, Completed At, Duration, Exit Code

---

### 4. Stage Flow (`stage_flow.html`)

**Purpose:** Visualize how data flows through pipeline stages

**Key Features:**

- **Flow Chart**: chunks → entities → relationships → communities
- **Counts**: Input/output counts per stage
- **Color Coding**: Status-based colors (green=completed, blue=running, red=failed)
- **Details**: Click stage for detailed statistics
- **Auto-Refresh**: Updates every 5 seconds

**Usage:**

```
1. Enter database name
2. Click "Load Stats"
3. View data flow visualization
4. Click stages for details
5. Enable auto-refresh for live updates
```

**Best For:** Understanding pipeline behavior, debugging data flow issues

---

### 5. Entity Browser (`entity_browser.html`)

**Purpose:** Search and explore entities in knowledge graph

**Key Features:**

- **Search**: Find entities by name
- **Filters**: Type, confidence, source_count
- **Pagination**: Browse large entity sets
- **Detail View**: Aliases, relationships, metadata
- **Links**: Navigate to related entities

**Usage:**

```
1. Enter database name
2. Search by name (optional)
3. Apply filters (type, confidence, etc.)
4. Click "Search Entities"
5. Click entity for details
6. Click "View Relationships" to explore connections
```

**Typical Workflow:** Search → Filter → View Details → Explore Relationships → Navigate to Graph

---

### 6. Relationship Viewer (`relationship_viewer.html`)

**Purpose:** Browse and filter relationship triples

**Key Features:**

- **Triple Display**: subject → predicate → object
- **Filters**: Predicate, entity type, confidence
- **Pagination**: Browse large relationship sets
- **Detail View**: Source chunks, confidence, metadata
- **Links**: Navigate to subject/object entities

**Usage:**

```
1. Enter database name
2. Filter by predicate (optional)
3. Click "Search Relationships"
4. Browse subject → predicate → object triples
5. Click entity names to view entity details
```

**Best For:** Understanding relationship patterns, exploring predicates

---

### 7. Community Explorer (`community_explorer.html`)

**Purpose:** Browse and explore detected communities

**Key Features:**

- **Level Navigation**: Navigate between resolution levels (macro → micro)
- **Filtering**: Level, size, coherence score
- **Sorting**: By entity count, coherence, level
- **Detail View**: Entities, relationships, summary
- **Graph Link**: Visualize community as subgraph
- **Level Stats**: Count, avg size, avg coherence per level

**Usage:**

```
1. Enter database name
2. Click "Load Communities"
3. Navigate levels (buttons at top)
4. Filter by size/coherence
5. Click community for details
6. Click "View Graph" to visualize
```

**Multi-Resolution:**

- **Level 1**: Macro themes (broad topics)
- **Level 2-3**: Mid-level topics
- **Level 4+**: Micro topics (specific subjects)

---

### 8. Graph Viewer (`graph_viewer.html`)

**Purpose:** Interactive graph visualization with D3.js

**Key Features:**

- **Multiple Views**:
  - Sample graph (top entities)
  - Ego network (N-hop neighborhoods)
  - Community subgraph
- **Interactions**: Zoom, pan, drag nodes, click for details
- **Filtering**: Filter by predicate type
- **Export**: JSON, CSV, GraphML, GEXF formats
- **Hop Control**: Configurable depth (1-5 hops) for ego networks

**Usage:**

**Sample Graph:**

```
1. Enter database name
2. Set max nodes (50-500)
3. Click "Load Graph"
```

**Ego Network:**

```
1. Enter database name
2. Enter entity ID
3. Set max hops (1-5)
4. Set max nodes
5. Click "Load Graph"
```

**Community Graph:**

```
1. Enter community ID (or link from community explorer)
2. Click "Load Graph"
```

**Predicate Filtering:**

```
1. Load any graph first
2. Select predicate from dropdown
3. Graph filters automatically
```

**Export Graph:**

```
1. Load graph
2. Click "Export Graph"
3. Choose format (json, csv, graphml, gexf)
4. File downloads
```

**Best For:** Visual exploration, entity-centric analysis, community inspection

---

### 9. Experiment Comparison (`experiment_comparison.html`)

**Purpose:** Compare multiple pipeline runs side-by-side

**Key Features:**

- **Experiment Selection**: Choose multiple runs to compare
- **Comprehensive Metrics**:
  - Quality: modularity, graph density, clustering
  - Cost: tokens, estimated USD, cost per entity
  - Performance: runtime, throughput
  - Coverage: chunks processed, entities/chunk
- **Charts**: Trends, comparisons, distributions
- **Export**: Comparison report as JSON

**Usage:**

```
1. Enter database name
2. Select experiments to compare
3. Click "Load Comparison"
4. View metric tables and charts
5. Export comparison report
```

**Best For:** A/B testing, parameter optimization, cost analysis

---

### 10. Experiment Visualization (`experiment_visualization.html`)

**Purpose:** Visual analysis of experiment results

**Key Features:**

- **Charts**:
  - Community size distributions (histograms)
  - Cost vs quality (scatter plots)
  - Performance over time (line charts)
  - Modularity comparisons (bar charts)
  - Resolution effects (line charts)
- **Interactive**: Click, zoom, filter
- **Export**: Charts as images, data as JSON

**Usage:**

```
1. Enter database name
2. Select experiments
3. Click "Load Experiments"
4. View charts
5. Export as needed
```

**Best For:** Visual experiment analysis, identifying trends, presentations

---

### 11. Quality Metrics Dashboard (`quality_metrics_dashboard.html`)

**Purpose:** Monitor per-stage quality metrics

**Key Features:**

- **Per-Stage Metrics**:
  - Extraction: completion rate, canonical ratio
  - Resolution: merge rate, duplicate reduction
  - Construction: graph density, relationship types
  - Detection: modularity, coverage, community sizes
- **Auto-Refresh**: Updates every 10 seconds
- **Stage Selection**: View specific stage or all

**Usage:**

```
1. Enter database name
2. Select stage (or "All Stages")
3. Click "Load Metrics"
4. View quality metrics
5. Enable auto-refresh for live updates
```

**Best For:** Quality monitoring, regression detection, improvement tracking

---

### 12. Graph Statistics Dashboard (`graph_statistics.html`)

**Purpose:** Analyze graph-level statistics

**Key Features:**

- **Statistics**:
  - Node/edge counts
  - Graph density
  - Degree distribution
  - Type distribution (entity types)
  - Predicate distribution (relationship types)
- **Charts**: Bar charts for distributions
- **Tables**: Detailed distribution tables
- **Auto-Refresh**: Updates every 10 seconds

**Usage:**

```
1. Enter database name
2. Click "Load Statistics"
3. View overview stats
4. Analyze distribution charts
5. Browse distribution tables
```

**Best For:** Graph analysis, understanding structure, identifying patterns

---

### 13. Performance Dashboard (`performance_dashboard.html`)

**Purpose:** Monitor pipeline performance

**Key Features:**

- **Metrics**:
  - Pipeline duration
  - Throughput (chunks/sec, chunks/min)
  - Performance trends over time
- **Charts**: Duration and throughput line charts
- **Auto-Refresh**: Updates every 10 seconds

**Usage:**

```
1. Enter database name
2. Optionally enter pipeline ID
3. Click "Load Metrics"
4. View performance metrics
5. Analyze trends
```

**Best For:** Performance optimization, bottleneck identification, capacity planning

---

## 🔧 Configuration

### API Endpoints

All dashboards connect to API endpoints. Update `API_BASE` in JavaScript if needed:

```javascript
const API_BASE = "http://localhost:8000"; // Default
```

### Database Name

Default database is `mongo_hack`. Change via UI controls or URL parameters:

```
?db_name=my_custom_db
```

### URL Parameters

Many dashboards support URL parameters for direct access:

**graph_viewer.html:**

```
?community_id=community_123&db_name=mongo_hack
```

**pipeline_history.html:**

```
?pipeline_id=pipeline_123
```

---

## 🎨 UI Architecture

### Technology Stack

- **HTML5/CSS3**: Layout and styling
- **Vanilla JavaScript**: Interactivity (no framework dependencies)
- **D3.js v7**: Graph visualization (via CDN)
- **Chart.js v4**: Charts and graphs (via CDN)

### Design Principles

1. **Dark Theme**: Optimized for long viewing sessions
2. **Responsive**: Works on desktop and tablet (mobile partially supported)
3. **Real-Time**: Auto-refresh capabilities for live monitoring
4. **Self-Contained**: Each dashboard is independent
5. **No Build Step**: Pure HTML/CSS/JS (no compilation needed)

### Color Scheme

```
Background: #1e1e1e
Secondary: #2d2d2d
Accent: #4a9eff (blue)
Success: #4caf50 (green)
Warning: #ff9800 (orange)
Error: #f44336 (red)
Text: #e0e0e0 (light gray)
```

### Entity Type Colors

```
PERSON: #4a9eff (blue)
ORGANIZATION: #4caf50 (green)
TECHNOLOGY: #ff9800 (orange)
CONCEPT: #9c27b0 (purple)
LOCATION: #00bcd4 (cyan)
EVENT: #ff5722 (red-orange)
OTHER: #f44336 (red)
```

---

## 🔗 Integration with APIs

### Required API Servers

The UIs require these API servers to be running:

1. **Pipeline Control API** (`:8000`):

   - `app/api/pipeline_control.py`
   - Used by: pipeline_control.html, pipeline_history.html

2. **Pipeline Progress API** (`:8000`):

   - `app/api/pipeline_progress.py`
   - Used by: pipeline_monitor.html

3. **Pipeline Stats API** (`:8000`):

   - `app/api/pipeline_stats.py`
   - Used by: stage_flow.html

4. **Entity API** (`:8001` or `:8000`):

   - `app/api/entities.py`
   - Used by: entity_browser.html, graph_viewer.html

5. **Relationship API** (`:8000`):

   - `app/api/relationships.py`
   - Used by: relationship_viewer.html, graph_viewer.html

6. **Community API** (`:8002` or `:8000`):

   - `app/api/communities.py`
   - Used by: community_explorer.html, graph_viewer.html

7. **Ego Network API** (`:8000`):

   - `app/api/ego_network.py`
   - Used by: graph_viewer.html

8. **Export API** (`:8003` or `:8000`):

   - `app/api/export.py`
   - Used by: graph_viewer.html (server-side export)

9. **Quality Metrics API** (`:8000`):

   - `app/api/quality_metrics.py`
   - Used by: quality_metrics_dashboard.html

10. **Graph Statistics API** (`:8000`):

    - `app/api/graph_statistics.py`
    - Used by: graph_statistics.html

11. **Performance Metrics API** (`:8000`):
    - `app/api/performance_metrics.py`
    - Used by: performance_dashboard.html

### Starting All APIs

```bash
# Option 1: Manual (separate terminals)
python app/api/pipeline_control.py 8000 &
python app/api/entities.py 8001 &
python app/api/communities.py 8002 &
python app/api/export.py 8003 &

# Option 2: Use process manager (supervisord, pm2, etc.)
# See documentation/guides/GRAPHRAG-VISUALIZATION-GUIDE.md
```

---

## 📖 Typical Workflows

### Workflow 1: Run and Monitor a Pipeline

```
1. Open pipeline_control.html
2. Configure and start pipeline
3. Open pipeline_monitor.html in new tab
4. Watch real-time progress
5. When complete, check pipeline_history.html
```

### Workflow 2: Explore the Knowledge Graph

```
1. Open entity_browser.html
2. Search for entity of interest
3. Click entity for details
4. Note entity ID
5. Open graph_viewer.html
6. Enter entity ID, set max hops to 2
7. Load ego network
8. Explore connected entities
9. Filter by predicate if needed
10. Export graph for external analysis
```

### Workflow 3: Analyze Communities

```
1. Open community_explorer.html
2. Load communities
3. Navigate levels (macro → micro)
4. Click interesting community
5. View details (entities, relationships, summary)
6. Click "View Graph"
7. Explore community subgraph
8. Export if needed
```

### Workflow 4: Compare Experiments

```
1. Run multiple experiments with different configs
2. Open experiment_comparison.html
3. Select experiments to compare
4. Load comparison
5. Analyze metrics (quality, cost, performance)
6. View charts and trends
7. Export comparison report
8. Document findings in experiment journal
```

### Workflow 5: Monitor Quality

```
1. Open quality_metrics_dashboard.html
2. Enable auto-refresh
3. Monitor completion rates
4. Check for failures
5. Track quality trends
6. Switch between stages
7. Open graph_statistics.html for deeper analysis
```

---

## 🎯 Use Cases by Role

### Data Scientist

**Primary Dashboards:**

- experiment_comparison.html
- experiment_visualization.html
- quality_metrics_dashboard.html

**Typical Tasks:**

- Compare experiment results
- Analyze quality metrics
- Optimize pipeline parameters
- Track improvements

### Platform Engineer

**Primary Dashboards:**

- pipeline_control.html
- pipeline_monitor.html
- performance_dashboard.html

**Typical Tasks:**

- Monitor pipeline execution
- Troubleshoot failures
- Optimize performance
- Track resource usage

### Domain Expert

**Primary Dashboards:**

- entity_browser.html
- relationship_viewer.html
- community_explorer.html
- graph_viewer.html

**Typical Tasks:**

- Explore knowledge graph
- Validate entity extraction
- Review communities
- Export data for analysis

---

## 🔍 Advanced Features

### 1. Ego Network Exploration

**N-Hop Neighborhoods:**

- **1-hop**: Direct neighbors only
- **2-hop**: Neighbors + neighbors of neighbors
- **3+ hops**: Extended neighborhood (can get large)

**Use Cases:**

- Entity-centric analysis
- Local graph structure
- Relationship patterns around key entities

**Tips:**

- Start with 1-hop, expand as needed
- Use max_nodes to limit size
- Export for detailed analysis in external tools

### 2. Predicate Filtering

**Filter Graph by Relationship Type:**

**Use Cases:**

- Focus on specific relationship types
- Analyze relationship patterns
- Simplify complex graphs

**Example:**

- Filter by "works_for" to see employment relationships
- Filter by "located_in" to see geographic connections

### 3. Multi-Format Export

**Formats:**

- **JSON**: Programmatic access, NetworkX integration
- **CSV**: Spreadsheet analysis, data inspection
- **GraphML**: Gephi, yEd, graph analysis tools
- **GEXF**: Gephi (recommended for Gephi)

**Use Cases:**

- External analysis in specialized tools
- Sharing graphs with collaborators
- Integration with other systems

**Gephi Integration:**

```
1. Export graph as GEXF
2. Open Gephi
3. File → Open → Select .gexf file
4. Apply layout (Force Atlas 2, Fruchterman Reingold)
5. Color nodes by type
6. Analyze communities, centrality, etc.
```

### 4. Multi-Resolution Community Navigation

**Hierarchical Exploration:**

- Drill down from broad themes to specific topics
- Understand topic hierarchy
- Find right granularity for your use case

**Tips:**

- Start at level 1 for overview
- Drill down to level 2-3 for specifics
- Compare coherence scores across levels
- Use level stats to understand distribution

---

## 🐛 Troubleshooting

### Dashboard Won't Load

**Symptoms:** Blank page, "Failed to load" error

**Solutions:**

1. Check browser console (F12) for errors
2. Verify API servers are running
3. Check API_BASE URL in JavaScript
4. Try accessing API directly (curl)
5. Check CORS headers

### Graph Rendering Issues

**Symptoms:** Graph doesn't appear, nodes overlap, performance issues

**Solutions:**

1. Reduce max_nodes (try 50-100)
2. Use filters to limit data
3. Check that entities exist in database
4. Try different browser (Chrome recommended)
5. Clear browser cache

### Slow Performance

**Symptoms:** Dashboards load slowly, lag when interacting

**Solutions:**

1. Use pagination (don't load all data)
2. Apply filters to reduce result sets
3. Check MongoDB indexes
4. Reduce auto-refresh frequency
5. Use smaller max_nodes in graph viewer

### API Connection Errors

**Symptoms:** "Failed to fetch", "Connection refused"

**Solutions:**

1. Verify API servers are running
2. Check port numbers match
3. Check firewall settings
4. Verify database name is correct
5. Check API logs for errors

### Export Not Working

**Symptoms:** Export button does nothing

**Solutions:**

1. Ensure graph is loaded first
2. Check browser allows downloads
3. Try different format
4. Check browser console for errors
5. Verify graph data is not empty

---

## 📦 Dependencies

### External Libraries (via CDN)

**D3.js v7:**

```html
<script src="https://d3js.org/d3.v7.min.js"></script>
```

**Chart.js v4:**

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

### No Build Required

All dashboards are self-contained HTML files with inline CSS and JavaScript. No compilation or build step required.

---

## 🚀 Deployment

### Local Development

```bash
cd app/ui
python -m http.server 8080
```

### Production Deployment

**Option 1: Nginx**

```nginx
server {
    listen 80;
    server_name graphrag.example.com;
    root /path/to/app/ui;
    index pipeline_control.html;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
    }
}
```

**Option 2: Docker**

```dockerfile
FROM nginx:alpine
COPY app/ui /usr/share/nginx/html
EXPOSE 80
```

---

## 🔐 Security Considerations

### Current State

- **No Authentication**: All dashboards are publicly accessible
- **No Authorization**: No access control on API endpoints
- **No Rate Limiting**: Unlimited API requests

### Production Recommendations

1. **Add Authentication**:

   - HTTP Basic Auth on Nginx
   - OAuth2 integration
   - API key authentication

2. **Add Rate Limiting**:

   - Nginx rate limiting
   - API-level throttling

3. **Secure API Endpoints**:

   - HTTPS only
   - CORS restrictions
   - Input validation

4. **Monitor Access**:
   - Access logs
   - Audit trails
   - Anomaly detection

---

## 📊 Performance Tips

### Graph Viewer

1. **Start Small**: Load 50-100 nodes first
2. **Use Filters**: Filter by type or predicate
3. **Ego Networks**: Use 1-2 hops for fast rendering
4. **Export Large Graphs**: For external tools (Gephi, Cytoscape)

### Auto-Refresh

1. **Adjust Interval**: Balance between freshness and load
2. **Disable When Not Needed**: Save resources
3. **Use Pipeline Monitor**: Purpose-built for real-time

### Pagination

1. **Use Reasonable Limits**: 50-100 results per page
2. **Apply Filters**: Reduce total result set
3. **Index MongoDB Fields**: Ensure performance

---

## 📝 Best Practices

### Pipeline Execution

1. Always set experiment_id for tracking
2. Use stage selection to run only needed stages
3. Monitor via pipeline_monitor.html
4. Check quality metrics after completion
5. Document experiments in journal

### Graph Exploration

1. Start with entity browser or community explorer
2. Use ego networks for entity-centric view
3. Use community graphs for cluster analysis
4. Apply predicate filters to focus
5. Export for deeper analysis

### Quality Monitoring

1. Enable auto-refresh during pipeline runs
2. Track trends over time
3. Compare across experiments
4. Document quality improvements
5. Use graph statistics for validation

---

## 🆘 Support

### Documentation

- **API Reference**: `documentation/api/GRAPHRAG-PIPELINE-API.md`
- **User Guide**: `documentation/guides/GRAPHRAG-VISUALIZATION-GUIDE.md`
- **Plan Document**: `PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md`

### Logs

- **Browser Console**: F12 → Console tab
- **API Logs**: Check console output of API servers
- **Pipeline Logs**: Available in pipeline_monitor.html

---

## 🎉 Summary

The GraphRAG Pipeline Visualization UI provides a comprehensive suite of dashboards for monitoring, controlling, and exploring the GraphRAG pipeline and knowledge graph. With 13 specialized interfaces, you can:

- ✅ Control pipeline execution remotely
- ✅ Monitor progress in real-time
- ✅ Explore entities, relationships, and communities
- ✅ Visualize graphs interactively
- ✅ Compare experiments and analyze quality
- ✅ Export data in multiple formats
- ✅ Track performance and identify bottlenecks

All dashboards are production-ready, self-contained, and require no build step. Simply open in a browser and start exploring!

---

**Version:** 1.0  
**Last Updated:** 2025-11-07  
**Achievement:** 8.3 - User Guide & Tutorials  
**Plan:** PLAN_GRAPHRAG-PIPELINE-VISUALIZATION.md
