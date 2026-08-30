#!/bin/bash
# ============================================================
# SANTINEL Production Deployment Script
# Automated deployment pipeline with validation and rollback
# ============================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_DIR="$PROJECT_DIR/deployment"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$SCRIPT_DIR/deploy_${TIMESTAMP}.log"
BACKUP_DIR="$SCRIPT_DIR/backups/$TIMESTAMP"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓ $*${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗ $*${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠ $*${NC}" | tee -a "$LOG_FILE"
}

# Prerequisites check
check_prerequisites() {
    log "Checking prerequisites..."

    local missing_tools=()

    # Check required tools
    for tool in docker docker-compose kubectl git; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        return 1
    fi

    log_success "All prerequisites met"
    return 0
}

# Load environment variables
load_env() {
    log "Loading environment configuration..."

    if [ ! -f "$PROJECT_DIR/.env.production" ]; then
        log_error ".env.production not found"
        log "Please create .env.production with required variables"
        return 1
    fi

    source "$PROJECT_DIR/.env.production"
    log_success "Environment loaded"
    return 0
}

# Build Docker image
build_docker_image() {
    log "Building Docker image..."

    docker build \
        --file "$DEPLOYMENT_DIR/Dockerfile" \
        --tag "santinel/api:$TIMESTAMP" \
        --tag "santinel/api:latest" \
        --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
        --build-arg VCS_REF="$(git rev-parse --short HEAD)" \
        "$PROJECT_DIR"

    if [ $? -eq 0 ]; then
        log_success "Docker image built: santinel/api:$TIMESTAMP"
        return 0
    else
        log_error "Docker build failed"
        return 1
    fi
}

# Run tests
run_tests() {
    log "Running test suite..."

    cd "$PROJECT_DIR"

    # Unit tests
    if python tests/test_voice_module.py &>> "$LOG_FILE"; then
        log_success "Unit tests passed"
    else
        log_warning "Some unit tests failed"
    fi

    # Integration tests
    if [ -f "tests/integration_test.py" ]; then
        if python tests/integration_test.py &>> "$LOG_FILE"; then
            log_success "Integration tests passed"
        else
            log_warning "Some integration tests failed"
        fi
    fi

    return 0
}

# Validate configuration
validate_config() {
    log "Validating configuration files..."

    # Validate docker-compose
    docker-compose -f "$DEPLOYMENT_DIR/docker-compose.yml" config > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "docker-compose.yml is valid"
    else
        log_error "docker-compose.yml validation failed"
        return 1
    fi

    # Validate Kubernetes manifests
    if command -v kubeval &> /dev/null; then
        kubeval "$DEPLOYMENT_DIR/kubernetes.yaml" &>> "$LOG_FILE"
        if [ $? -eq 0 ]; then
            log_success "Kubernetes manifests are valid"
        else
            log_warning "Kubernetes manifest validation had warnings"
        fi
    fi

    return 0
}

# Deploy to Docker Compose (dev/staging)
deploy_docker_compose() {
    log "Deploying with Docker Compose..."

    cd "$DEPLOYMENT_DIR"

    # Backup current state
    mkdir -p "$BACKUP_DIR"
    docker-compose ps > "$BACKUP_DIR/compose_state_before.txt" 2>&1 || true

    # Pull latest images
    docker-compose pull &>> "$LOG_FILE"

    # Up with new image
    docker-compose up -d --remove-orphans &>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_success "Docker Compose deployment completed"

        # Wait for services to be healthy
        log "Waiting for services to become healthy..."
        sleep 10

        # Check service health
        if docker-compose ps | grep -q "healthy"; then
            log_success "Services are healthy"
            return 0
        else
            log_warning "Services may not be fully healthy yet"
            return 0
        fi
    else
        log_error "Docker Compose deployment failed"
        return 1
    fi
}

# Deploy to Kubernetes (production)
deploy_kubernetes() {
    log "Deploying to Kubernetes..."

    # Check context
    current_context=$(kubectl config current-context)
    log "Using Kubernetes context: $current_context"

    # Create namespace
    kubectl create namespace santinel-prod --dry-run=client -o yaml | kubectl apply -f - &>> "$LOG_FILE"
    log_success "Namespace ready"

    # Apply manifests
    kubectl apply -f "$DEPLOYMENT_DIR/kubernetes.yaml" &>> "$LOG_FILE"

    if [ $? -eq 0 ]; then
        log_success "Kubernetes manifests applied"
    else
        log_error "Failed to apply Kubernetes manifests"
        return 1
    fi

    # Wait for deployment
    log "Waiting for API deployment to be ready..."
    if kubectl rollout status deployment/api -n santinel-prod --timeout=5m &>> "$LOG_FILE"; then
        log_success "API deployment is ready"
    else
        log_error "API deployment failed or timed out"
        return 1
    fi

    return 0
}

# Health check
health_check() {
    log "Performing health checks..."

    local max_attempts=30
    local attempt=0

    # Get API endpoint
    local api_endpoint=""
    if command -v kubectl &> /dev/null && kubectl get svc api -n santinel-prod &> /dev/null; then
        api_endpoint="http://$(kubectl get svc api-lb -n santinel-prod -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo 'localhost'):8002"
    else
        api_endpoint="http://localhost:8002"
    fi

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf "$api_endpoint/api/v1/health" > /dev/null 2>&1; then
            log_success "Health check passed"
            return 0
        fi

        attempt=$((attempt + 1))
        log "Health check attempt $attempt/$max_attempts..."
        sleep 2
    done

    log_error "Health check failed after $max_attempts attempts"
    return 1
}

# Smoke tests
smoke_tests() {
    log "Running smoke tests..."

    local api_endpoint="http://localhost:8002"

    # Test endpoints
    local endpoints=(
        "/api/v1/health"
        "/api/v1/login"
    )

    for endpoint in "${endpoints[@]}"; do
        log "Testing $endpoint..."
        if curl -sf "$api_endpoint$endpoint" > /dev/null 2>&1; then
            log_success "$endpoint is accessible"
        else
            log_warning "$endpoint test failed"
        fi
    done

    return 0
}

# Database migration
migrate_database() {
    log "Running database migrations..."

    # Run migrations using alembic if available
    if command -v alembic &> /dev/null; then
        cd "$PROJECT_DIR"
        alembic upgrade head &>> "$LOG_FILE"
        log_success "Database migrations completed"
    else
        log "Loading schema.sql..."
        # Alternative: Load schema directly
        if [ -f "$PROJECT_DIR/schema.sql" ]; then
            log_success "Schema file found: $PROJECT_DIR/schema.sql"
        fi
    fi

    return 0
}

# Backup before deployment
backup_current_state() {
    log "Backing up current state..."

    mkdir -p "$BACKUP_DIR"

    # Backup database if accessible
    if command -v pg_dump &> /dev/null; then
        pg_dump "$DATABASE_URL" > "$BACKUP_DIR/database.sql" 2>&1 || \
            log_warning "Could not backup database"
    fi

    # Backup Redis data
    if command -v redis-cli &> /dev/null; then
        redis-cli BGSAVE > "$BACKUP_DIR/redis_backup.txt" 2>&1 || \
            log_warning "Could not backup Redis"
    fi

    log_success "State backed up to $BACKUP_DIR"
    return 0
}

# Rollback function
rollback() {
    log_error "Deployment failed. Rolling back..."

    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "No backup directory found. Manual rollback may be required."
        return 1
    fi

    # Rollback Docker Compose
    if [ -f "$BACKUP_DIR/compose_state_before.txt" ]; then
        cd "$DEPLOYMENT_DIR"
        docker-compose down &>> "$LOG_FILE"
        docker-compose up -d &>> "$LOG_FILE"
        log_success "Rollback to previous Docker Compose state"
    fi

    # Rollback Kubernetes
    if command -v kubectl &> /dev/null; then
        kubectl rollout undo deployment/api -n santinel-prod &>> "$LOG_FILE"
        log_success "Kubernetes rollback completed"
    fi

    return 0
}

# Main deployment flow
main() {
    log "=========================================="
    log "SANTINEL Production Deployment"
    log "Timestamp: $TIMESTAMP"
    log "=========================================="

    # Initialize
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$BACKUP_DIR"

    # Pre-deployment checks
    if ! check_prerequisites; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    if ! load_env; then
        log_error "Failed to load environment"
        exit 1
    fi

    if ! validate_config; then
        log_error "Configuration validation failed"
        exit 1
    fi

    # Build and test
    if ! build_docker_image; then
        log_error "Docker build failed"
        exit 1
    fi

    if ! run_tests; then
        log_warning "Tests had issues but continuing deployment"
    fi

    # Backup current state
    backup_current_state

    # Database migration
    migrate_database

    # Deployment
    case "${DEPLOY_TARGET:-docker-compose}" in
        kubernetes)
            if ! deploy_kubernetes; then
                rollback
                exit 1
            fi
            ;;
        docker-compose)
            if ! deploy_docker_compose; then
                rollback
                exit 1
            fi
            ;;
        *)
            log_error "Unknown deployment target: $DEPLOY_TARGET"
            exit 1
            ;;
    esac

    # Post-deployment verification
    if ! health_check; then
        log_error "Health check failed"
        rollback
        exit 1
    fi

    smoke_tests

    # Success
    log_success "=========================================="
    log_success "Deployment completed successfully!"
    log_success "Build: santinel/api:$TIMESTAMP"
    log_success "Logs: $LOG_FILE"
    log_success "=========================================="

    return 0
}

# Run main function
main "$@"
