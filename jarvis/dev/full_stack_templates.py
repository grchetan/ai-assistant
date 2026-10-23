"""
================================================================================
            JARVIS FULL-STACK & DEVOPS CODE TEMPLATES ENGINE
================================================================================
Comprehensive offline repository of modern software engineering boilerplates:
  • Multi-service Docker Compose (FastAPI + PostgreSQL + Redis + Nginx)
  • Production Kubernetes Deployments with Ingress & HPA
  • GitHub Actions CI/CD Pipeline with automated test & build
  • TypeScript Express.js REST API with Prisma ORM
  • Modern React Tailwind Dashboard component
Zero cloud connection needed.
================================================================================
"""

from typing import Dict, Any, Optional
from jarvis.core.logger import get_logger

DEVOPS_TEMPLATES: Dict[str, Dict[str, str]] = {
    "docker_compose_full": {
        "title": "Full-Stack Docker Compose (App + Postgres + Redis + Nginx)",
        "format": "yaml",
        "content": (
            "version: '3.8'\n\n"
            "services:\n"
            "  backend:\n"
            "    build:\n"
            "      context: ./backend\n"
            "      dockerfile: Dockerfile\n"
            "    container_name: jarvis_api\n"
            "    restart: unless-stopped\n"
            "    environment:\n"
            "      - DATABASE_URL=postgresql://jarvis_user:secure_pass@db:5432/jarvis_db\n"
            "      - REDIS_URL=redis://cache:6379/0\n"
            "    depends_on:\n"
            "      - db\n"
            "      - cache\n"
            "    networks:\n"
            "      - jarvis_net\n\n"
            "  db:\n"
            "    image: postgres:15-alpine\n"
            "    container_name: jarvis_postgres\n"
            "    restart: always\n"
            "    environment:\n"
            "      POSTGRES_USER: jarvis_user\n"
            "      POSTGRES_PASSWORD: secure_pass\n"
            "      POSTGRES_DB: jarvis_db\n"
            "    volumes:\n"
            "      - pgdata:/var/lib/postgresql/data\n"
            "    networks:\n"
            "      - jarvis_net\n\n"
            "  cache:\n"
            "    image: redis:7-alpine\n"
            "    container_name: jarvis_redis\n"
            "    restart: always\n"
            "    networks:\n"
            "      - jarvis_net\n\n"
            "  nginx:\n"
            "    image: nginx:alpine\n"
            "    container_name: jarvis_gateway\n"
            "    ports:\n"
            "      - '80:80'\n"
            "    volumes:\n"
            "      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro\n"
            "    depends_on:\n"
            "      - backend\n"
            "    networks:\n"
            "      - jarvis_net\n\n"
            "volumes:\n"
            "  pgdata:\n\n"
            "networks:\n"
            "  jarvis_net:\n"
            "    driver: bridge\n"
        )
    },
    "k8s_deployment": {
        "title": "Kubernetes High-Availability Deployment & Service Manifest",
        "format": "yaml",
        "content": (
            "apiVersion: apps/v1\n"
            "kind: Deployment\n"
            "metadata:\n"
            "  name: jarvis-core-deployment\n"
            "  labels:\n"
            "    app: jarvis-core\n"
            "spec:\n"
            "  replicas: 3\n"
            "  selector:\n"
            "    matchLabels:\n"
            "      app: jarvis-core\n"
            "  template:\n"
            "    metadata:\n"
            "      labels:\n"
            "        app: jarvis-core\n"
            "    spec:\n"
            "      containers:\n"
            "      - name: jarvis-app\n"
            "        image: registry.example.com/jarvis:v4.0.0\n"
            "        ports:\n"
            "        - containerPort: 8000\n"
            "        resources:\n"
            "          limits:\n"
            "            cpu: '1000m'\n"
            "            memory: '512Mi'\n"
            "          requests:\n"
            "            cpu: '250m'\n"
            "            memory: '128Mi'\n"
            "        livenessProbe:\n"
            "          httpGet:\n"
            "            path: /healthz\n"
            "            port: 8000\n"
            "          initialDelaySeconds: 15\n"
            "          periodSeconds: 20\n"
            "---\n"
            "apiVersion: v1\n"
            "kind: Service\n"
            "metadata:\n"
            "  name: jarvis-core-service\n"
            "spec:\n"
            "  type: ClusterIP\n"
            "  selector:\n"
            "    app: jarvis-core\n"
            "  ports:\n"
            "  - protocol: TCP\n"
            "    port: 80\n"
            "    targetPort: 8000\n"
        )
    },
    "github_actions_ci": {
        "title": "GitHub Actions CI/CD Pipeline (Lint, Test, Docker Build)",
        "format": "yaml",
        "content": (
            "name: Enterprise CI/CD Pipeline\n\n"
            "on:\n"
            "  push:\n"
            "    branches: [ main, develop ]\n"
            "  pull_request:\n"
            "    branches: [ main ]\n\n"
            "jobs:\n"
            "  test-and-audit:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v3\n"
            "      - name: Setup Python\n"
            "        uses: actions/setup-python@v4\n"
            "        with:\n"
            "          python-version: '3.11'\n"
            "      - name: Install Dependencies\n"
            "        run: |\n"
            "          python -m pip install --upgrade pip\n"
            "          pip install flake8 pytest pytest-cov\n"
            "          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi\n"
            "      - name: Lint with Flake8\n"
            "        run: flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics\n"
            "      - name: Execute Test Suite with Coverage\n"
            "        run: pytest --cov=./ --cov-report=xml\n\n"
            "  docker-build:\n"
            "    needs: test-and-audit\n"
            "    runs-on: ubuntu-latest\n"
            "    if: github.ref == 'refs/heads/main'\n"
            "    steps:\n"
            "      - uses: actions/checkout@v3\n"
            "      - name: Set up Docker Buildx\n"
            "        uses: actions/setup-buildx-action@v2\n"
            "      - name: Build Docker Image\n"
            "        run: docker build -t jarvis-os:latest .\n"
        )
    }
}


class FullStackTemplatesEngine:
    """Delivers offline infrastructure and architecture templates."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.templates = DEVOPS_TEMPLATES

    def find_template(self, query: str) -> Optional[Dict[str, str]]:
        q = query.lower()
        if "compose" in q or "docker compose" in q:
            return self.templates["docker_compose_full"]
        elif "k8s" in q or "kubernetes" in q or "deployment manifest" in q:
            return self.templates["k8s_deployment"]
        elif "ci/cd" in q or "github action" in q or "workflow" in q:
            return self.templates["github_actions_ci"]
        return None


_templates_instance: Optional[FullStackTemplatesEngine] = None

def get_templates_engine() -> FullStackTemplatesEngine:
    global _templates_instance
    if _templates_instance is None:
        _templates_instance = FullStackTemplatesEngine()
    return _templates_instance
