#!/usr/bin/env python3
"""
p9i CLI - Build, run, and deploy commands for p9i AI Prompt System

Usage:
    # Docker build and run
    python -m cli.main build          # Build image with keys from .env
    python -m cli.main run           # Run in stdio mode (no auth, Claude Code compatible)
    python -m cli.main start         # Build + run stdio

    # JWT token management (for HTTP mode)
    python -m cli.main jwt generate --subject my-project --role developer
    python -m cli.main jwt validate <token>

    # Kubernetes/MicroK8s deployment
    python -m cli.main deploy status                   # Check deployment status
    python -m cli.main deploy apply                   # Deploy to MicroK8s via Helm
    python -m cli.main deploy logs                     # View deployment logs
    python -m cli.main deploy restart                 # Restart deployment
    python -m cli.main deploy backup                  # Backup PostgreSQL/Redis
    python -m cli.main deploy restore --file backup.sql  # Restore from backup
    python -m cli.main deploy cleanup                 # Remove deployment

For HTTP access, use JWT with:
    {"url": "https://<DOMAIN>/mcp", "headers": {"Authorization": "Bearer <token>"}}
"""

import argparse
import os
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
HELM_CHART_PATH = PROJECT_ROOT / "helm" / "p9i"
K8S_NAMESPACE = "p9i"


def load_env_file():
    """Load .env file and return dict of API keys."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        print(f"Warning: .env file not found at {env_path}")
        return {}

    env_vars = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    return env_vars


def run_cmd(cmd, check=True, capture=True):
    """Run shell command and return output."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if capture and result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result


def build_image(args):
    """Build Docker image with API keys from .env."""
    env_vars = load_env_file()

    build_args = [
        "docker", "build",
        "-f", str(PROJECT_ROOT / "docker" / "Dockerfile"),
        "-t", args.tag or "p9i:latest",
    ]

    api_keys = [
        "MINIMAX_API_KEY", "ZAI_API_KEY", "OPENROUTER_API_KEY",
        "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY", "P9I_API_KEY",
    ]

    for key in api_keys:
        value = env_vars.get(key, "")
        if value:
            build_args.extend(["--build-arg", f"{key}={value}"])

    if env_vars.get("JWT_SECRET"):
        build_args.extend(["--build-arg", f"JWT_SECRET={env_vars['JWT_SECRET']}"])

    jwt_enabled = env_vars.get("JWT_ENABLED", "false")
    build_args.extend(["--build-arg", f"JWT_ENABLED={jwt_enabled}"])

    if args.no_cache:
        build_args.append("--no-cache")

    build_args.append(str(PROJECT_ROOT))

    print(f"Building p9i image...")
    result = subprocess.run(build_args)
    sys.exit(result.returncode)


def run_container(args):
    """Run p9i container in stdio mode."""
    print("Starting p9i in stdio mode...")

    cmd = [
        "docker", "run", "--rm", "-i",
        "-v", f"{PROJECT_ROOT}/.env:/app/.env:ro",
        "-v", f"{PROJECT_ROOT}:/project:ro",
        "-v", f"{PROJECT_ROOT}/memory:/app/memory:rw",
        "--network", "host" if args.network else "none",
        "p9i:latest"
    ]

    if args.interactive:
        cmd.insert(2, "-it")

    subprocess.run(cmd)


def check_microk8s():
    """Check if MicroK8s is available."""
    result = subprocess.run(["which", "microk8s"], capture_output=True)
    if result.returncode != 0:
        print("Error: microk8s not found. Please install MicroK8s first.")
        print("See: https://microk8s.io/docs/install-alternative")
        sys.exit(1)

    result = subprocess.run(["microk8s", "status"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: MicroK8s is not running. Start it with: microk8s start")
        sys.exit(1)

    # Check required addons
    result = subprocess.run(["microk8s", "addons", "list"], capture_output=True, text=True)
    enabled = []
    for addon in ["storage", "dns", "ingress"]:
        if addon in result.stdout.lower() and "[enabled]" in result.stdout.lower():
            enabled.append(addon)
    print(f"Enabled addons: {enabled}")
    return enabled


def deploy_status(args):
    """Check deployment status."""
    print(f"\n=== p9i Deployment Status ({K8S_NAMESPACE}) ===\n")

    # Check namespace
    run_cmd(["kubectl", "get", "namespace", K8S_NAMESPACE], check=False)

    # Check pods
    print("\n--- Pods ---")
    run_cmd(["kubectl", "get", "pods", "-n", K8S_NAMESPACE, "-o", "wide"])

    # Check services
    print("\n--- Services ---")
    run_cmd(["kubectl", "get", "svc", "-n", K8S_NAMESPACE])

    # Check ingress
    print("\n--- Ingress ---")
    run_cmd(["kubectl", "get", "ingress", "-n", K8S_NAMESPACE])

    # Check helm release
    print("\n--- Helm Release ---")
    run_cmd(["helm", "list", "-n", K8S_NAMESPACE], check=False)

    # Check recent events
    print("\n--- Recent Events ---")
    run_cmd(["kubectl", "get", "events", "-n", K8S_NAMESPACE, "--sort-by=.lastTimestamp", "-A"], check=False)


def deploy_apply(args):
    """Deploy to MicroK8s via Helm."""
    print("\n=== Deploying p9i to MicroK8s ===\n")

    # Check MicroK8s
    check_microk8s()

    # Tag and push image
    print("\n--- Building and pushing Docker image ---")
    env_vars = load_env_file()

    # Build image
    run_cmd(["docker", "build", "-f", str(PROJECT_ROOT / "docker" / "Dockerfile"), "-t", "p9i:latest", str(PROJECT_ROOT)])

    # Tag for local registry
    run_cmd(["docker", "tag", "p9i:latest", "localhost:5000/p9i:k8s"])

    # Push to local registry
    run_cmd(["docker", "push", "localhost:5000/p9i:k8s"])

    # Create namespace if needed
    print("\n--- Creating namespace ---")
    run_cmd(["kubectl", "create", "namespace", K8S_NAMESPACE, "--dry-run=client", "-o", "yaml"], check=False)
    run_cmd(["kubectl", "get", "namespace", K8S_NAMESPACE], check=False)

    # Create TLS secret
    print("\n--- Creating TLS secret ---")
    run_cmd(["kubectl", "create", "secret", "tls", "p9i-tls",
             "--cert=certs/cert.pem", "--key=certs/key.pem",
             "-n", K8S_NAMESPACE, "--dry-run=client", "-o", "yaml"], check=False)

    # Deploy via Helm
    print("\n--- Deploying with Helm ---")
    cmd = [
        "helm", "upgrade", "--install", "p9i", str(HELM_CHART_PATH),
        "--namespace", K8S_NAMESPACE,
        "--create-namespace",
        "--values", str(HELM_CHART_PATH / "values.yaml"),
        "--wait", "--timeout", "10m",
    ]

    if args.atomic:
        cmd.append("--atomic")

    run_cmd(cmd)

    # Verify deployment
    print("\n--- Verifying deployment ---")
    run_cmd(["kubectl", "wait", "--for=condition=ready", "pod", "-l", "app=p9i", "-n", K8S_NAMESPACE, "--timeout=300s"])
    run_cmd(["kubectl", "rollout", "status", "deployment/p9i-p9i", "-n", K8S_NAMESPACE])

    # Show status
    print("\n=== Deployment Complete ===")
    deploy_status(args)


def deploy_logs(args):
    """View deployment logs."""
    tail = args.tail or 100
    follow = "-f" if args.follow else ""

    print(f"Showing logs (last {tail} lines)...")
    run_cmd(["kubectl", "logs", "-n", K8S_NAMESPACE, "deployment/p9i-p9i", "--tail", str(tail), follow])


def deploy_restart(args):
    """Restart deployment."""
    print("Restarting p9i deployment...")
    run_cmd(["kubectl", "rollout", "restart", "deployment/p9i-p9i", "-n", K8S_NAMESPACE])
    run_cmd(["kubectl", "wait", "--for=condition=ready", "pod", "-l", "app=p9i", "-n", K8S_NAMESPACE, "--timeout=300s"])
    print("Restart complete.")


def deploy_backup(args):
    """Backup PostgreSQL and Redis data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_ROOT / "backups"
    backup_dir.mkdir(exist_ok=True)

    print(f"\n=== Backing up p9i data ({timestamp}) ===\n")

    # Backup PostgreSQL
    print("--- PostgreSQL backup ---")
    pg_backup = f"p9i_postgres_{timestamp}.sql"
    run_cmd([
        "kubectl", "exec", "-n", K8S_NAMESPACE, "p9i-p9i-postgresql-0", "--",
        "pg_dump", "-U", "postgres", "ai_prompts", "-f", f"/tmp/{pg_backup}"
    ], check=False)
    run_cmd([
        "kubectl", "cp", f"{K8S_NAMESPACE}/p9i-p9i-postgresql-0:/tmp/{pg_backup}",
        str(backup_dir / pg_backup)
    ], check=False)

    # Backup Redis
    print("--- Redis backup ---")
    redis_backup = f"p9i_redis_{timestamp}.rdb"
    run_cmd([
        "kubectl", "exec", "-n", K8S_NAMESPACE, "p9i-p9i-redis-master-0", "--",
        "redis-cli", "SAVE"
    ], check=False)
    run_cmd([
        "kubectl", "cp", f"{K8S_NAMESPACE}/p9i-p9i-redis-master-0:/data/dump.rdb",
        str(backup_dir / redis_backup)
    ], check=False)

    print(f"\nBackup complete! Files saved to: {backup_dir}")


def deploy_restore(args):
    """Restore from backup."""
    if not args.file:
        print("Error: --file parameter required")
        sys.exit(1)

    backup_file = Path(args.file)
    if not backup_file.exists():
        print(f"Error: Backup file not found: {backup_file}")
        sys.exit(1)

    print(f"\n=== Restoring from {backup_file} ===\n")

    # Determine type and restore
    if backup_file.suffix == ".sql":
        print("Restoring PostgreSQL...")
        run_cmd(["kubectl", "cp", str(backup_file), f"{K8S_NAMESPACE}/p9i-p9i-postgresql-0:/tmp/restore.sql"])
        run_cmd([
            "kubectl", "exec", "-n", K8S_NAMESPACE, "p9i-p9i-postgresql-0", "--",
            "psql", "-U", "postgres", "-d", "ai_prompts", "-f", "/tmp/restore.sql"
        ])
    elif backup_file.suffix == ".rdb":
        print("Restoring Redis...")
        run_cmd(["kubectl", "cp", str(backup_file), f"{K8S_NAMESPACE}/p9i-p9i-redis-master-0:/tmp/restore.rdb"])
        run_cmd([
            "kubectl", "exec", "-n", K8S_NAMESPACE, "p9i-p9i-redis-master-0", "--",
            "redis-cli", "LOADRDB", "/tmp/restore.rdb"
        ])
    else:
        print("Error: Unknown backup file type. Use .sql for PostgreSQL or .rdb for Redis.")
        sys.exit(1)

    print("Restore complete!")


def deploy_cleanup(args):
    """Remove deployment."""
    print(f"\n=== Removing p9i deployment from {K8S_NAMESPACE} ===\n")

    confirm = input("Are you sure? This will delete all data! (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    run_cmd(["helm", "uninstall", "p9i", "-n", K8S_NAMESPACE], check=False)
    run_cmd(["kubectl", "delete", "namespace", K8S_NAMESPACE], check=False)
    print("Cleanup complete.")


def main():
    parser = argparse.ArgumentParser(
        prog="p9i",
        description="p9i CLI - Build, run, and deploy commands"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Docker commands
    build_parser = subparsers.add_parser("build", help="Build Docker image with API keys from .env")
    build_parser.add_argument("--tag", "-t", help="Image tag", default="p9i:latest")
    build_parser.add_argument("--no-cache", action="store_true", help="Build without cache")

    run_parser = subparsers.add_parser("run", help="Run in stdio mode")
    run_parser.add_argument("--network", action="store_true", help="Enable network access")
    run_parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")

    subparsers.add_parser("start", help="Build and run in stdio mode")

    # Deploy commands
    deploy_parser = subparsers.add_parser("deploy", help="Deploy to MicroK8s via Helm")
    deploy_subparsers = deploy_parser.add_subparsers(dest="deploy_command", help="Deploy subcommands")

    deploy_subparsers.add_parser("status", help="Check deployment status")

    apply_parser = deploy_subparsers.add_parser("apply", help="Deploy to MicroK8s")
    apply_parser.add_argument("--atomic", action="store_true", help="Atomic deployment (rollback on failure)")

    logs_parser = deploy_subparsers.add_parser("logs", help="View deployment logs")
    logs_parser.add_argument("--tail", type=int, help="Number of lines to show")
    logs_parser.add_argument("-f", "--follow", action="store_true", help="Follow logs")

    deploy_subparsers.add_parser("restart", help="Restart deployment")
    deploy_subparsers.add_parser("backup", help="Backup PostgreSQL/Redis data")

    restore_parser = deploy_subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("--file", required=True, help="Backup file to restore")

    deploy_subparsers.add_parser("cleanup", help="Remove deployment")

    args = parser.parse_args()

    if args.command == "build":
        build_image(args)
    elif args.command == "run":
        run_container(args)
    elif args.command == "start":
        build_image(argparse.Namespace(tag="p9i:latest", no_cache=False))
        run_container(argparse.Namespace(network=False, interactive=False))
    elif args.command == "deploy":
        if args.deploy_command == "status":
            deploy_status(args)
        elif args.deploy_command == "apply":
            deploy_apply(args)
        elif args.deploy_command == "logs":
            deploy_logs(args)
        elif args.deploy_command == "restart":
            deploy_restart(args)
        elif args.deploy_command == "backup":
            deploy_backup(args)
        elif args.deploy_command == "restore":
            deploy_restore(args)
        elif args.deploy_command == "cleanup":
            deploy_cleanup(args)
        else:
            deploy_parser.print_help()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()