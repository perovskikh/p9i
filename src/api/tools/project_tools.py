"""
Project MCP Tools - Project management and SFTP tools.

These tools provide multi-project SaaS functionality including
project CRUD operations and SFTP connection management.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Global references - will be set during registration
_project_service_func = None
_get_memory_func = None
_save_memory_func = None


def register_project_tools(
    mcp,
    get_project_service_func,
    get_memory_func,
    save_memory_func
):
    """
    Register project management tools with the MCP server.

    Args:
        mcp: FastMCP server instance
        get_project_service_func: Function that returns ProjectService instance
        get_memory_func: Function to get project memory
        save_memory_func: Function to save project memory
    """
    global _project_service_func, _get_memory_func, _save_memory_func

    _project_service_func = get_project_service_func
    _get_memory_func = get_memory_func
    _save_memory_func = save_memory_func

    @mcp.tool()
    def adapt_to_project(
        project_path: str,
        project_description: str = None,
        sftp_host: str = None,
        sftp_port: int = 22,
        sftp_username: str = "root",
        sftp_password: str = None,
        sftp_key_file: str = None,
    ) -> dict:
        """
        Auto-detect stack and adapt prompts.

        Args:
            project_path: Path to the project (optional if project_description provided)
            project_description: Description of project stack (optional)
            sftp_host: Remote SFTP host (for remote projects)
            sftp_port: SFTP port (default: 22)
            sftp_username: SFTP username (default: root)
            sftp_password: SFTP password (optional if using key)
            sftp_key_file: Path to SSH private key file

        Returns:
            dict: Detected stack and adaptations
        """
        import os
        from src.services.sftp_filesystem import get_sftp_connection

        stack = {"language": None, "framework": None, "database": None}
        remote_access = False
        sftp = None

        # Try path-based detection first
        path = Path(project_path) if project_path else None

        # If SFTP credentials provided, try remote access first
        if sftp_host and project_path:
            try:
                sftp = get_sftp_connection(
                    host=sftp_host,
                    port=sftp_port,
                    username=sftp_username,
                    password=sftp_password,
                    key_file=sftp_key_file,
                )
                if sftp.exists(project_path):
                    path = Path(project_path)
                    remote_access = True
                    logger.info(f"Accessed remote project via SFTP: {sftp_host}:{project_path}")
            except Exception as e:
                logger.warning(f"SFTP connection failed: {e}, falling back to local")

        # If not remote and path doesn't exist locally, try common mount mappings
        if not remote_access and path and not path.exists():
            # Common Docker mount patterns: /home/.../project → /project
            mount_mappings = [
                ("/home/", "/project/"),
                ("/workspace/", "/project/"),
                ("/app/", "/project/"),
                ("/root/", "/project/"),
            ]
            path_str = str(path)
            for host_prefix, container_prefix in mount_mappings:
                if path_str.startswith(host_prefix):
                    remaining = path_str[len(host_prefix):]
                    project_name = remaining.split('/')[-1] if remaining else ""
                    new_path = f"/project/{project_name}"
                    mapped_path = Path(new_path)
                    if mapped_path.exists():
                        path = mapped_path
                        break
            # If still not found, try scattered /app/ mount pattern
            if path and not path.exists():
                app_path = Path("/app")
                if app_path.exists():
                    if (app_path / "src").exists() or (app_path / "prompts").exists():
                        path = app_path

        # Now check if path exists
        if path and path.exists():
            # Detect language/framework via local or remote access
            if remote_access and sftp:
                try:
                    if sftp.exists(str(path / "requirements.txt")):
                        stack["language"] = "Python"
                        req_content = sftp.read_text(str(path / "requirements.txt"))
                    elif sftp.exists(str(path / "pyproject.toml")):
                        stack["language"] = "Python"
                        req_content = sftp.read_text(str(path / "pyproject.toml"))
                    else:
                        req_content = ""
                    if "fastapi" in req_content.lower():
                        stack["framework"] = "FastAPI"
                    elif "aiogram" in req_content.lower():
                        stack["framework"] = "aiogram"
                    elif "fastmcp" in req_content.lower():
                        stack["framework"] = "FastMCP"

                    if sftp.exists(str(path / "package.json")):
                        stack["language"] = "JavaScript/TypeScript"
                        pkg_content = sftp.read_text(str(path / "package.json"))
                        if "next" in pkg_content.lower():
                            stack["framework"] = "Next.js"

                    if sftp.exists(str(path / "docker-compose.yml")):
                        content = sftp.read_text(str(path / "docker-compose.yml"))
                        if "postgres" in content:
                            stack["database"] = "PostgreSQL"
                        elif "redis" in content:
                            stack["database"] = "Redis"
                except Exception as e:
                    logger.error(f"Error reading remote files: {e}")
            else:
                # Local file reading
                if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
                    stack["language"] = "Python"
                    req_content = (path / "requirements.txt").read_text() if (path / "requirements.txt").exists() else ""
                    if "fastapi" in req_content.lower():
                        stack["framework"] = "FastAPI"
                    elif "aiogram" in req_content.lower():
                        stack["framework"] = "aiogram"
                    elif "fastmcp" in req_content.lower():
                        stack["framework"] = "FastMCP"

                if (path / "package.json").exists():
                    stack["language"] = "JavaScript/TypeScript"
                    pkg_content = (path / "package.json").read_text()
                    if "next" in pkg_content.lower():
                        stack["framework"] = "Next.js"

                # Detect database
                if (path / "docker-compose.yml").exists():
                    content = (path / "docker-compose.yml").read_text()
                    if "postgres" in content:
                        stack["database"] = "PostgreSQL"
                    elif "redis" in content:
                        stack["database"] = "Redis"
        elif project_description:
            # Fallback to description-based detection
            desc = project_description.lower()
            if "python" in desc:
                stack["language"] = "Python"
                if "fastmcp" in desc or "fastapi" in desc:
                    stack["framework"] = "FastMCP" if "fastmcp" in desc else "FastAPI"
            if "javascript" in desc or "typescript" in desc:
                stack["language"] = "JavaScript/TypeScript"
                if "next" in desc:
                    stack["framework"] = "Next.js"
            if "postgresql" in desc or "postgres" in desc:
                stack["database"] = "PostgreSQL"
            if "redis" in desc:
                stack["database"] = "Redis"
        else:
            return {"status": "error", "error": "Project path does not exist and no description provided"}

        # Save detected stack to project memory
        try:
            from src.services.memory import get_memory_service
            memory = get_memory_service()
            project_id = str(path) if path else project_description
            memory_data = memory.get(project_id)
            memory_data["stack"] = stack
            memory_data["project_path"] = str(path) if path else None
            memory_data["remote_access"] = remote_access
            memory.save(project_id, memory_data)
            memory.save("current_project", memory_data)
        except Exception as e:
            logger.warning(f"Failed to save project memory: {e}")

        return {
            "status": "success",
            "stack": stack,
            "access_type": "remote_sftp" if remote_access else "local",
            "project_path": str(path) if path else None,
            "adaptations": [
                f"Selected prompts for {stack.get('language', 'unknown')} project",
                f"Framework: {stack.get('framework', 'not detected')}"
            ]
        }

    @mcp.tool()
    async def create_project(
        name: str,
        owner_id: str,
        description: str = "",
        sftp_host: str = None,
        sftp_port: int = 22,
        sftp_username: str = None,
        sftp_key_fingerprint: str = None,
        sftp_project_path: str = None,
        default_project_path: str = "/project",
    ) -> dict:
        """
        Create a new project for multi-project SaaS.

        Args:
            name: Project name (unique identifier)
            owner_id: Owner user/organization ID
            description: Project description
            sftp_host: Remote SFTP host (optional)
            sftp_port: SFTP port (default: 22)
            sftp_username: SFTP username (optional)
            sftp_key_fingerprint: SSH key fingerprint (optional)
            sftp_project_path: Remote path on SFTP server (optional)
            default_project_path: Default project path (default: /project)

        Returns:
            dict: Created project with ID and API key
        """
        try:
            from src.services.project_service import CreateProjectDTO

            service = _project_service_func()

            dto = CreateProjectDTO(
                name=name,
                owner_id=owner_id,
                description=description,
                sftp_host=sftp_host,
                sftp_port=sftp_port,
                sftp_username=sftp_username,
                sftp_key_fingerprint=sftp_key_fingerprint,
                sftp_project_path=sftp_project_path,
                default_project_path=default_project_path,
            )

            project = await service.create_project(dto)

            # Create initial API key for the project
            api_key_model, raw_key = await service.create_api_key(
                project_id=str(project.id),
                name=f"{name} Default Key",
                permissions=["read_prompts", "run_prompt"],
                rate_limit=100,
            )

            return {
                "status": "success",
                "project": {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "owner_id": project.owner_id,
                    "sftp_host": project.sftp_host,
                    "default_project_path": project.default_project_path,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                },
                "api_key": raw_key,
                "message": "Save the API key - it won't be shown again!",
            }

        except Exception as e:
            logger.error(f"create_project error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def get_project(project_id: str) -> dict:
        """
        Get project details by ID.

        Args:
            project_id: Project UUID

        Returns:
            dict: Project details including SFTP config
        """
        try:
            service = _project_service_func()
            project = await service.get_project(project_id)

            if not project:
                return {"status": "error", "error": "Project not found"}

            return {
                "status": "success",
                "project": {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "owner_id": project.owner_id,
                    "sftp_host": project.sftp_host,
                    "sftp_port": project.sftp_port,
                    "sftp_username": project.sftp_username,
                    "sftp_project_path": project.sftp_project_path,
                    "default_project_path": project.default_project_path,
                    "stack": project.stack or [],
                    "project_metadata": project.project_metadata or {},
                    "is_active": project.is_active,
                    "created_at": project.created_at.isoformat() if project.created_at else None,
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                },
            }

        except Exception as e:
            logger.error(f"get_project error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def list_projects(owner_id: str) -> dict:
        """
        List all projects for an owner.

        Args:
            owner_id: Owner user/organization ID

        Returns:
            dict: List of projects
        """
        try:
            service = _project_service_func()
            projects = await service.list_projects(owner_id)

            return {
                "status": "success",
                "projects": [
                    {
                        "id": str(p.id),
                        "name": p.name,
                        "description": p.description,
                        "owner_id": p.owner_id,
                        "sftp_host": p.sftp_host,
                        "is_active": p.is_active,
                        "created_at": p.created_at.isoformat() if p.created_at else None,
                    }
                    for p in projects
                ],
                "count": len(projects),
            }

        except Exception as e:
            logger.error(f"list_projects error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def update_project(
        project_id: str,
        name: str = None,
        description: str = None,
        sftp_host: str = None,
        sftp_port: int = None,
        sftp_username: str = None,
        sftp_project_path: str = None,
        default_project_path: str = None,
    ) -> dict:
        """
        Update project configuration.

        Args:
            project_id: Project UUID
            name: New project name (optional)
            description: New description (optional)
            sftp_host: New SFTP host (optional)
            sftp_port: New SFTP port (optional)
            sftp_username: New SFTP username (optional)
            sftp_project_path: New remote path (optional)
            default_project_path: New default path (optional)

        Returns:
            dict: Updated project
        """
        try:
            from src.services.project_service import UpdateProjectDTO

            service = _project_service_func()

            update_data = UpdateProjectDTO(
                name=name,
                description=description,
                sftp_host=sftp_host,
                sftp_port=sftp_port,
                sftp_username=sftp_username,
                sftp_project_path=sftp_project_path,
                default_project_path=default_project_path,
            )

            project = await service.update_project(project_id, update_data)

            if not project:
                return {"status": "error", "error": "Project not found"}

            return {
                "status": "success",
                "project": {
                    "id": str(project.id),
                    "name": project.name,
                    "description": project.description,
                    "sftp_host": project.sftp_host,
                    "updated_at": project.updated_at.isoformat() if project.updated_at else None,
                },
            }

        except Exception as e:
            logger.error(f"update_project error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def delete_project(project_id: str) -> dict:
        """
        Delete (deactivate) a project.

        Args:
            project_id: Project UUID

        Returns:
            dict: Deletion status
        """
        try:
            service = _project_service_func()
            result = await service.delete_project(project_id)

            if not result:
                return {"status": "error", "error": "Project not found"}

            return {
                "status": "success",
                "message": f"Project {project_id} deleted",
            }

        except Exception as e:
            logger.error(f"delete_project error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def create_project_api_key(
        project_id: str,
        name: str,
        permissions: list = None,
        rate_limit: int = 100,
    ) -> dict:
        """
        Create an API key for a project.

        Args:
            project_id: Project UUID
            name: API key name
            permissions: List of permissions (default: ["read_prompts", "run_prompt"])
            rate_limit: Requests per minute (default: 100)

        Returns:
            dict: Created API key (raw key shown only once!)
        """
        try:
            service = _project_service_func()

            if permissions is None:
                permissions = ["read_prompts", "run_prompt"]

            api_key_model, raw_key = await service.create_api_key(
                project_id=project_id,
                name=name,
                permissions=permissions,
                rate_limit=rate_limit,
            )

            return {
                "status": "success",
                "api_key": {
                    "id": str(api_key_model.id),
                    "name": api_key_model.name,
                    "permissions": api_key_model.permissions or [],
                    "rate_limit": api_key_model.rate_limit,
                    "created_at": api_key_model.created_at.isoformat() if api_key_model.created_at else None,
                },
                "raw_key": raw_key,
                "message": "Save the API key - it won't be shown again!",
            }

        except Exception as e:
            logger.error(f"create_project_api_key error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def list_project_api_keys(project_id: str) -> dict:
        """
        List all API keys for a project.

        Args:
            project_id: Project UUID

        Returns:
            dict: List of API keys (without raw keys)
        """
        try:
            service = _project_service_func()
            keys = await service.list_api_keys(project_id)

            return {
                "status": "success",
                "api_keys": [
                    {
                        "id": str(k.id),
                        "name": k.name,
                        "permissions": k.permissions or [],
                        "rate_limit": k.rate_limit,
                        "is_active": k.is_active,
                        "created_at": k.created_at.isoformat() if k.created_at else None,
                        "last_used_at": k.last_used_at.isoformat() if k.last_used_at else None,
                    }
                    for k in keys
                ],
                "count": len(keys),
            }

        except Exception as e:
            logger.error(f"list_project_api_keys error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def revoke_project_api_key(key_id: str) -> dict:
        """
        Revoke an API key.

        Args:
            key_id: API key UUID

        Returns:
            dict: Revocation status
        """
        try:
            service = _project_service_func()
            result = await service.revoke_api_key(key_id)

            if not result:
                return {"status": "error", "error": "API key not found"}

            return {
                "status": "success",
                "message": f"API key {key_id} revoked",
            }

        except Exception as e:
            logger.error(f"revoke_project_api_key error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def connect_project_sftp(project_id: str) -> dict:
        """
        Establish SFTP connection for a project.

        Args:
            project_id: Project UUID

        Returns:
            dict: Connection status
        """
        try:
            service = _project_service_func()
            sftp = await service.connect_sftp(project_id)

            if not sftp:
                return {
                    "status": "error",
                    "error": "SFTP not configured for this project or connection failed",
                }

            project = await service.get_project(project_id)

            return {
                "status": "success",
                "message": f"Connected to SFTP: {project.sftp_host}",
                "project_path": project.sftp_project_path or "/project",
                "host": project.sftp_host,
            }

        except Exception as e:
            logger.error(f"connect_project_sftp error: {e}")
            return {"status": "error", "error": str(e)}

    @mcp.tool()
    async def disconnect_project_sftp(project_id: str) -> dict:
        """
        Disconnect SFTP connection for a project.

        Args:
            project_id: Project UUID

        Returns:
            dict: Disconnection status
        """
        try:
            service = _project_service_func()
            await service.disconnect_sftp(project_id)

            return {
                "status": "success",
                "message": f"SFTP disconnected for project {project_id}",
            }

        except Exception as e:
            logger.error(f"disconnect_project_sftp error: {e}")
            return {"status": "error", "error": str(e)}

    return [
        adapt_to_project,
        create_project,
        get_project,
        list_projects,
        update_project,
        delete_project,
        create_project_api_key,
        list_project_api_keys,
        revoke_project_api_key,
        connect_project_sftp,
        disconnect_project_sftp,
    ]
