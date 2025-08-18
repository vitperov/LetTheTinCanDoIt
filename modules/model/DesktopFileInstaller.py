import os
import sys
import stat
from pathlib import Path

class DesktopFileInstaller:
    """
    Class for installing application .desktop file.
    """
    def install(self):
        """
        Install the .desktop file for the application on Linux by reading the
        template, replacing placeholders, and placing it in the user's
        application directory. Raises NotImplementedError on non-Linux platforms.
        """
        if not sys.platform.startswith("linux"):
            raise NotImplementedError("Desktop file installation is only supported on Linux.")

        base_dir = Path(__file__).resolve().parents[2]
        template_path = base_dir / "resources" / "LetTheTinCanDoIt.desktop"
        if not template_path.exists():
            raise FileNotFoundError(f"Desktop file template not found: {template_path}")

        content = template_path.read_text()
        python_exec = sys.executable
        script_path = Path(sys.argv[0]).resolve()
        icon_path = base_dir / "resources" / "tinCan.png"

        content = content.format(
            python_exec=python_exec,
            script_path=script_path,
            icon_path=icon_path,
        )

        xdg_data_home = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
        applications_dir = Path(xdg_data_home) / "applications"
        applications_dir.mkdir(parents=True, exist_ok=True)

        target_file = applications_dir / template_path.name
        target_file.write_text(content)

        mode = target_file.stat().st_mode
        target_file.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
