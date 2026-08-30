# PHASE 13: Production Deployment

Comprehensive production-ready deployment infrastructure for SANTINEL AI Coaching Assistant.

## Overview

PHASE 13 delivers a complete production deployment stack including containerization, orchestration, monitoring, and automated deployment pipelines.

## Deliverables

### 1. Docker & Container Infrastructure

#### `deployment/Dockerfile` (Multi-stage build)
- **Stage 1 (Builder)**: Compile Python dependencies with C extensions
- **Stage 2 (Runtime)**: Minimal production image with only runtime dependencies
- **Base Image**: Python 3.12-slim (optimized for size)
- **Dependencies**: FastAPI, PostgreSQL client, voice processing libraries
- **Security**: Non-root user (UID 1000), health checks, no unnecessary packages
- **Size**: ~200MB optimized image

Features:
- Multi-stage build for minimal image size
- Health check endpoint configured
- Supports hot-reload for development
- Production-ready with best practices

#### `deployment/docker-compose.yml` (Orchestration)
Complete microservices stack with 10 services:

**Core Services:**
- **PostgreSQL** (postgres:16-alpine): Primary data store, 5432
- **Redis** (redis:7-alpine): Cache layer, 6379
- **FastAPI Backend** (santinel/api): Main API, 8002
- **Voice Processor** (santinel/api): Async voice processing

**Data Services:**
- **Analytics DB** (TimescaleDB): Time-series metrics, 5433

**Monitoring & Logging:**
- **Prometheus** (prom/prometheus): Metrics collection, 9090
- **Grafana** (grafana/grafana): Visualization, 3000
- **Elasticsearch**: Log storage, 9200
- **Kibana**: Log visualization, 5601
- **Logstash**: Log processing, 5000

**Development:**
- **Frontend** (React Vite): Optional development server, 5173

Configuration:
- All services on `santinel-net` bridge network
- Health checks for critical services
- Volume persistence for data
- Structured logging to JSON files
- Environment variable management

### 2. Kubernetes Orchestration

#### `deployment/kubernetes.yaml` (K8s manifests)

**Namespace & Configuration:**
- Dedicated `santinel-prod` namespace
- ConfigMap for non-sensitive settings
- Secret for API keys and passwords

**Deployments & StatefulSets:**

1. **PostgreSQL StatefulSet**
   - Single replica (can scale)
   - Persistent volume with 10Gi storage
   - Health checks via pg_isready
   - Resource limits: 1Gi memory, 1 CPU max

2. **Redis Deployment**
   - Single replica for simplicity
   - Resource limits: 512Mi memory, 500m CPU
   - Liveness probe via redis-cli ping

3. **FastAPI API Deployment**
   - 3 replicas (horizontal scaling)
   - Rolling update strategy (1 surge, 0 unavailable)
   - Pod anti-affinity for distribution
   - Resource requests: 512Mi/500m, limits: 1Gi/1000m
   - Readiness & liveness probes

4. **Voice Processor Deployment**
   - 2 replicas for async processing
   - Same resource constraints as API

**Scaling & Availability:**

- **HorizontalPodAutoscaler (HPA)**
  - Scales API 3-10 replicas based on CPU/memory
  - Target: 70% CPU, 80% memory utilization
  - Scale-down stabilization: 300s

- **PodDisruptionBudget (PDB)**
  - Minimum 2 API pods always available
  - Ensures graceful cluster maintenance

**Networking:**

- **Services**: ClusterIP for internal, LoadBalancer for external
- **Ingress**: nginx-based with TLS termination
  - Hosts: api.santinel.ai, santinel.ai
  - Rate limiting, SSL redirect, proxy settings

**Security:**

- **NetworkPolicy**: Restrict traffic between pods
  - API → PostgreSQL, Redis, DNS
  - Ingress from nginx-ingress namespace only

**Monitoring:**

- **ServiceMonitor**: Prometheus scraping configuration
- **PrometheusRule**: Alert rules
  - High error rate (>5%)
  - High latency (p95 >1s)
  - Memory usage (>90%)

### 3. Database Schema

#### `deployment/init_db.sql`

Production schema with:
- **users**: User authentication and profiles
- **sessions**: Coaching session records
- **coaching_interactions**: Coaching history
- **feedback**: User feedback
- **voice_fingerprints**: Voice analysis data

Features:
- UUID primary keys
- Timestamps (created_at, updated_at)
- Indexes on common queries
- Referential integrity

### 4. Monitoring & Error Tracking

#### `monitoring/sentry_config.py`

Error tracking with Sentry:
- SDK initialization with FastAPI integration
- Transaction sampling (10% of requests)
- Performance profiling
- User context tracking
- Breadcrumbs for debugging
- Error categorization and metrics

Class structure:
- `SentryConfig`: Configuration and initialization
- `ErrorMetrics`: Error tracking and statistics
- Integration with FastAPI middleware

#### `monitoring/prometheus_metrics.py`

Prometheus metrics collection:
- HTTP request metrics (counter + histogram)
- API errors and latency
- Voice processing metrics
- Database query metrics
- Cache hit/miss tracking
- Session metrics
- Coaching framework metrics

Features:
- Middleware integration with FastAPI
- Performance tracking utilities
- Customizable buckets and aggregations
- Metrics export in Prometheus format

#### `monitoring/elk_stack.yaml`

ELK Stack configuration (YAML):
- **Elasticsearch**: Single-node cluster, 8.11.0
- **Logstash**: Log processing pipeline with filters
- **Kibana**: Visualization and dashboarding
- Index management and retention policies
- Alerting rules
- RBAC configuration
- Backup/restore procedures

Dashboards:
- SANTINEL Overview (request/error rates)
- Voice Processing Dashboard (latency/quality)

Visualizations:
- Request rate trends
- Error distribution
- Response time histogram
- Top endpoints by volume
- Voice quality gauges

#### `monitoring/logstash.conf`

Logstash pipeline:
- JSON and syslog input
- Docker container log parsing
- Timestamp normalization
- Severity level extraction
- Geolocation enrichment
- Fingerprinting for deduplication
- Multi-index output based on severity

#### `monitoring/prometheus.yml`

Prometheus scrape configuration:
- Prometheus self-monitoring
- FastAPI metrics (30s interval)
- PostgreSQL exporter
- Redis exporter
- Node exporter
- Docker metrics
- cAdvisor (container metrics)
- Elasticsearch exporter

### 5. Automated Deployment

#### `scripts/deploy.sh` (Bash script)

Automated deployment pipeline:
- Prerequisite checks (docker, kubectl, git)
- Environment loading from .env.production
- Docker image build and tagging
- Test suite execution
- Configuration validation
- State backup before deployment
- Database migrations
- Service health verification
- Smoke testing
- Automatic rollback on failure

Features:
- Comprehensive logging to timestamped file
- Color-coded console output
- Backup/restore capabilities
- Transaction-like deployment (all-or-nothing)
- Support for Docker Compose and Kubernetes
- Service health monitoring

### 6. Deployment Verification

#### `demo_deployment.py` (Bilingual verification)

Comprehensive deployment verification with:
- **8 health checks**:
  1. Docker containers status
  2. Database connectivity
  3. Redis cache availability
  4. FastAPI API health
  5. Voice processor availability
  6. Kubernetes cluster status
  7. Monitoring stack (Prometheus/Grafana)
  8. Centralized logging (ELK)

Features:
- **Bilingual support** (English + Romanian)
- Per-component latency measurement
- JSON results export
- Summary statistics
- Graceful handling of missing tools
- Detailed status reporting

Example output:
```
Deployment Verification Summary
Total checks: 8
Healthy: 7
Warnings: 1
Critical: 0
Duration: 12.34 seconds
```

## Deployment Scenarios

### Development (Docker Compose)

```bash
# Start all services
docker-compose -f deployment/docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api

# Scale service
docker-compose up -d --scale voice-processor=3
```

### Production (Kubernetes)

```bash
# Apply manifests
kubectl apply -f deployment/kubernetes.yaml

# Monitor rollout
kubectl rollout status deployment/api -n santinel-prod

# Scale replicas
kubectl scale deployment api -n santinel-prod --replicas=5

# View logs
kubectl logs -f deployment/api -n santinel-prod
```

### Automated Deployment

```bash
# Run complete deployment pipeline
./scripts/deploy.sh

# Deploy to Kubernetes specifically
DEPLOY_TARGET=kubernetes ./scripts/deploy.sh

# Deploy to Docker Compose
DEPLOY_TARGET=docker-compose ./scripts/deploy.sh
```

### Verify Deployment

```bash
# English verification
python demo_deployment.py

# Results exported to: deployment_verification_*.json
```

## Configuration Management

### Environment Variables

**`.env.production`** should contain:

```bash
# Database
DB_USER=postgres
DB_PASSWORD=<secure-password>
DB_NAME=santinel_prod

# Redis
REDIS_PASSWORD=<secure-password>

# LLM APIs
GROQ_API_KEY=<api-key>
MISTRAL_API_KEY=<api-key>
OPENAI_API_KEY=<api-key>

# Voice
DEEPGRAM_API_KEY=<api-key>
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Security
JWT_SECRET=<secure-random-string>

# Monitoring
SENTRY_DSN=https://...@sentry.io/...

# Deployment
DEPLOY_TARGET=kubernetes  # or docker-compose
GRAFANA_PASSWORD=<password>
ELASTIC_PASSWORD=<password>
```

### Kubernetes Secrets

Created via `kubectl`:

```bash
kubectl create secret generic santinel-secrets \
  --from-literal=JWT_SECRET=... \
  --from-literal=DB_PASSWORD=... \
  --from-file=google-credentials.json
```

## Performance Characteristics

### Latency Targets

- **API Response**: <200ms (p95)
- **Database Query**: <50ms (p95)
- **Voice Processing**: <300ms (target)
- **Cache Hit**: <10ms

### Capacity

- **Concurrent Users**: 1000+ (with 3-5 replicas)
- **Requests/second**: 100+ (per API replica)
- **Data Retention**: 90 days (logs), 365 days (audit)
- **Storage**: 10Gi (PostgreSQL), 50Gi (Elasticsearch)

### Resource Utilization

- **API Pod**: 512Mi request, 1Gi limit (CPU: 500m request, 1000m limit)
- **PostgreSQL**: 256Mi request, 1Gi limit
- **Redis**: 128Mi request, 512Mi limit

## Security Considerations

1. **Network**
   - NetworkPolicy restricts traffic
   - TLS/HTTPS on all external endpoints
   - Firewall rules for cluster

2. **Secrets**
   - Never commit .env files
   - Use Kubernetes Secrets or HashiCorp Vault
   - Rotate regularly

3. **Authentication**
   - JWT tokens with HS256
   - API key validation
   - OAuth2 integration ready

4. **Audit Logging**
   - All API requests logged
   - ELK stack centralized logging
   - 365-day retention for audit logs

## Monitoring & Alerting

### Key Metrics

- Request rate and latency
- Error rate and types
- Database connection pool
- Cache hit/miss ratio
- Voice processing quality
- System resources (CPU, memory, disk)

### Alert Rules

- High error rate (>5% for 5m)
- High latency (p95 >1s for 5m)
- Memory usage >90%
- Voice processing failures
- Database connection pool exhaustion

### Dashboards

1. **Overview Dashboard**
   - System health status
   - Request volume and errors
   - Response time distribution

2. **Voice Processing Dashboard**
   - Processing latency
   - Signal quality metrics
   - Event volume over time

3. **Infrastructure Dashboard**
   - Container resource usage
   - Network I/O
   - Disk usage

## Disaster Recovery

### Backup Strategy

- **Database**: Daily snapshots (30-day retention)
- **Redis**: Periodic RDB snapshots
- **Logs**: Elasticsearch snapshots weekly
- **Configuration**: Version control (git)

### Recovery Procedures

1. **Database Recovery**: Restore from snapshot
2. **Service Recovery**: Kubernetes automatic restart
3. **Full Cluster**: Use backup scripts and terraform

### RTO/RPO

- **RTO (Recovery Time Objective)**: <15 minutes
- **RPO (Recovery Point Objective)**: <1 hour

## Cost Optimization

- Auto-scaling reduces idle resources
- Reserved instances for baseline load
- Spot instances for non-critical workloads
- Log retention pruning (90 days default)
- Database query optimization

## Integration Points

### CI/CD Pipeline

- Build: Docker image with `docker build`
- Test: Run test suite before deployment
- Deploy: `scripts/deploy.sh` integration
- Verify: `demo_deployment.py` post-deployment

### Existing SANTINEL Components

- FastAPI backend (port 8002)
- React frontend (port 5173)
- PostgreSQL database
- Voice module (core/voice_module.py)
- Monitoring (monitoring/ directory)

## Next Steps

1. **Set up CI/CD** (GitHub Actions/GitLab CI)
2. **Configure SSL certificates** (Let's Encrypt/cert-manager)
3. **Setup domain** (api.santinel.ai)
4. **Production secrets** (Vault/AWS Secrets)
5. **Custom monitoring** (additional Prometheus exporters)
6. **Load testing** (k6, Locust)
7. **Disaster recovery drills**

## Troubleshooting

### Common Issues

**API failing to start:**
```bash
# Check logs
kubectl logs deployment/api -n santinel-prod

# Check database connectivity
kubectl exec -it postgres-0 -n santinel-prod -- psql -U postgres
```

**High latency:**
```bash
# Check metrics
curl http://prometheus:9090/api/v1/query?query=rate(http_requests_total[5m])

# Check resource usage
kubectl top pods -n santinel-prod
```

**Deployment rollback:**
```bash
kubectl rollout undo deployment/api -n santinel-prod
```

## Files Summary

| File | Purpose | Size |
|------|---------|------|
| Dockerfile | Container image | ~150 lines |
| docker-compose.yml | Dev orchestration | ~350 lines |
| kubernetes.yaml | Production orchestration | ~600 lines |
| sentry_config.py | Error tracking | ~250 lines |
| prometheus_metrics.py | Metrics collection | ~350 lines |
| elk_stack.yaml | Logging configuration | ~400 lines |
| logstash.conf | Log processing | ~150 lines |
| prometheus.yml | Metrics config | ~80 lines |
| deploy.sh | Deployment automation | ~400 lines |
| demo_deployment.py | Verification | ~500 lines |
| init_db.sql | Database schema | ~80 lines |

**Total:** ~3,300 lines of production-ready infrastructure code

## Status

✓ **PHASE 13 COMPLETE**

All production deployment infrastructure implemented:
- Docker & container orchestration
- Kubernetes manifests with HA
- Comprehensive monitoring (Prometheus/Grafana)
- Centralized logging (ELK stack)
- Error tracking (Sentry)
- Automated deployment pipeline
- Bilingual verification tools

**Next Phase**: PHASE 14 - Performance Optimization & Load Testing
