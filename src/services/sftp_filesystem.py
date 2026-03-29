"""
SFTP Filesystem Service for remote project access.

Allows p9i to access projects on remote machines via SFTP/SSH.
Supports full read/write operations with connection pooling.
"""

import os
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, BinaryIO

import paramiko
from paramiko import SSHClient, AutoAddPolicy, SFTPClient


@dataclass
class SFTPConfig:
    """SFTP connection configuration."""
    host: str
    port: int = 22
    username: str = "root"
    password: Optional[str] = None
    key_file: Optional[str] = None
    timeout: int = 30
    # Connection pool settings
    max_connections: int = 5
    connection_timeout: int = 60


class SFTPFilesystem:
    """
    Remote filesystem access via SFTP.

    Supports:
    - Password authentication
    - SSH key authentication
    - Read/write files remotely
    - Directory operations
    - Connection pooling
    """

    def __init__(self, config: SFTPConfig):
        self.config = config
        self._client: Optional[SSHClient] = None
        self._sftp: Optional[SFTPClient] = None

    def _connect(self) -> SFTPClient:
        """Establish SFTP connection."""
        if self._sftp is not None:
            return self._sftp

        self._client = SSHClient()
        self._client.set_missing_host_key_policy(AutoAddPolicy())

        connect_kwargs = {
            "hostname": self.config.host,
            "port": self.config.port,
            "username": self.config.username,
            "timeout": self.config.timeout,
        }

        if self.config.password:
            connect_kwargs["password"] = self.config.password
        elif self.config.key_file:
            connect_kwargs["key_filename"] = self.config.key_file

        self._client.connect(**connect_kwargs)
        self._sftp = self._client.open_sftp()
        return self._sftp

    def connect(self) -> None:
        """Establish SFTP connection (alias for _connect)."""
        self._connect()

    def close(self) -> None:
        """Close SFTP connection."""
        if self._sftp:
            self._sftp.close()
        if self._client:
            self._client.close()
        self._sftp = None
        self._client = None

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ==================== Read Operations ====================

    def exists(self, path: str) -> bool:
        """Check if remote path exists."""
        if not self._sftp:
            self._connect()
        try:
            self._sftp.stat(path)
            return True
        except FileNotFoundError:
            return False
        except OSError:
            return False

    def is_dir(self, path: str) -> bool:
        """Check if remote path is a directory."""
        if not self._sftp:
            self._connect()
        try:
            stat = self._sftp.stat(path)
            return paramiko.SFTP_IS_DIR(stat.st_mode)
        except (FileNotFoundError, OSError):
            return False

    def is_file(self, path: str) -> bool:
        """Check if remote path is a file."""
        if not self._sftp:
            self._connect()
        try:
            stat = self._sftp.stat(path)
            return paramiko.SFTP_IS_REG(stat.st_mode)
        except (FileNotFoundError, OSError):
            return False

    def read_file(self, path: str) -> bytes:
        """Read file content from remote path."""
        if not self._sftp:
            self._connect()
        with self._sftp.file(path, "rb") as f:
            return f.read()

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        """Read text file content from remote path."""
        return self.read_file(path).decode(encoding)

    def list_dir(self, path: str) -> list[str]:
        """List directory contents."""
        if not self._sftp:
            self._connect()
        return self._sftp.listdir(path)

    def stat(self, path: str) -> paramiko.SFTPAttributes:
        """Get file/directory attributes."""
        if not self._sftp:
            self._connect()
        return self._sftp.stat(path)

    def get_file_size(self, path: str) -> int:
        """Get file size in bytes."""
        stat = self.stat(path)
        return stat.st_size

    # ==================== Write Operations ====================

    def write_file(self, path: str, content: Union[bytes, BinaryIO]) -> None:
        """
        Write bytes content to remote file.

        Creates parent directories if they don't exist.

        Args:
            path: Remote file path.
            content: Bytes content or file-like object to write.
        """
        if not self._sftp:
            self._connect()

        # Create parent directories if needed
        parent = os.path.dirname(path)
        if parent and not self.exists(parent):
            self.mkdir(parent, parents=True)

        mode = "wb"
        if hasattr(content, "read"):
            mode = "rb"

        with self._sftp.open(path, mode) as f:
            if hasattr(content, "read"):
                # Read from file-like object in chunks
                while True:
                    chunk = content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
            else:
                f.write(content)

    def write_text(
        self,
        path: str,
        text: str,
        encoding: str = "utf-8",
    ) -> None:
        """
        Write text content to remote file.

        Creates parent directories if they don't exist.

        Args:
            path: Remote file path.
            text: Text string to write.
            encoding: Text encoding (default: utf-8).
        """
        content = text.encode(encoding)
        self.write_file(path, content)

    def mkdir(
        self,
        path: str,
        mode: int = 0o755,
        parents: bool = False,
    ) -> None:
        """
        Create directory on remote filesystem.

        Args:
            path: Remote directory path to create.
            mode: Directory permissions (default: 0o755).
            parents: Create parent directories if they don't exist.
        """
        if not self._sftp:
            self._connect()

        if parents:
            # Split path into components and create each
            parts = Path(path).parts
            current = ""
            for part in parts:
                current = os.path.join(current, part) if current else part
                try:
                    self._sftp.mkdir(current, mode=mode)
                except IOError:
                    # Directory might already exist
                    if not self.exists(current):
                        raise
        else:
            self._sftp.mkdir(path, mode=mode)

    def remove(self, path: str) -> None:
        """
        Remove (delete) file from remote filesystem.

        Args:
            path: Remote file path to remove.
        """
        if not self._sftp:
            self._connect()
        self._sftp.remove(path)

    def rmdir(self, path: str) -> None:
        """
        Remove (delete) empty directory from remote filesystem.

        Args:
            path: Remote directory path to remove.
        """
        if not self._sftp:
            self._connect()
        self._sftp.rmdir(path)

    def rename(self, old: str, new: str) -> None:
        """
        Rename/move file or directory on remote filesystem.

        Args:
            old: Current path.
            new: New path.
        """
        if not self._sftp:
            self._connect()

        # Create parent directory of destination if needed
        new_parent = os.path.dirname(new)
        if new_parent and not self.exists(new_parent):
            self.mkdir(new_parent, parents=True)

        self._sftp.rename(old, new)

    # ==================== Utility Methods ====================

    def walk(self, path: str):
        """
        Walk directory tree recursively.

        Yields:
            Tuples of (dirpath, dirnames, filenames).
        """
        if not self._sftp:
            self._connect()

        try:
            entries = self._sftp.listdir_attr(path)
        except IOError:
            return

        dirs = []
        files = []

        for entry in entries:
            name = entry.filename
            # S_IFDIR = 0o40000
            if entry.st_mode & 0o170000 == 0o40000:
                dirs.append(name)
            else:
                files.append(name)

        yield (path, dirs, files)

        for dirname in dirs:
            new_path = os.path.join(path, dirname)
            yield from self.walk(new_path)


# Global SFTP connection pool (per host)
_sftp_pools: dict[str, SFTPFilesystem] = {}


def get_sftp_connection(
    host: str,
    port: int = 22,
    username: str = "root",
    password: Optional[str] = None,
    key_file: Optional[str] = None,
    timeout: int = 30,
) -> SFTPFilesystem:
    """
    Get or create SFTP connection.

    Connection is cached per host to avoid reconnecting.
    """
    cache_key = f"{username}@{host}:{port}"

    if cache_key not in _sftp_pools:
        config = SFTPConfig(
            host=host,
            port=port,
            username=username,
            password=password,
            key_file=key_file,
            timeout=timeout,
        )
        _sftp_pools[cache_key] = SFTPFilesystem(config)

    sftp = _sftp_pools[cache_key]
    if not sftp._client:
        sftp.connect()

    return sftp


def close_all_sftp() -> None:
    """Close all SFTP connections."""
    for sftp in _sftp_pools.values():
        sftp.close()
    _sftp_pools.clear()
