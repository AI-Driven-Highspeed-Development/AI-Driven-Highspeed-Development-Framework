"""Utilities for discovering modules exposed by public/private listing repositories."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from .framework_commons.yaml_util import YamlUtil, YamlFile


class ModuleListing:
    """Fetch and render module listings defined in listing_public/private.yaml."""

    LISTING_FILENAME = "listing.yaml"

    def __init__(self, framework_dir: Path):
        self.framework_dir = framework_dir
        self.public_listing_path = framework_dir / "listing_public.yaml"
        self.private_listing_path = framework_dir / "listing_private.yaml"
        self.clone_tmp_root = framework_dir / ".adhd_clone_tmp"

    def list_available_modules(self) -> bool:
        """Print all available modules from configured listing sources."""
        sources = self._collect_listing_sources()
        if not sources:
            print(
                "⚠️  No listing sources found. Configure listing_public.yaml or listing_private.yaml."
            )
            return False

        print(f"\n{'=' * 60}")
        print("📚 AVAILABLE MODULES")
        print(f"{'=' * 60}")

        discovered_any = False
        for group_name, repo_url in sources.items():
            modules = self._fetch_group_modules(group_name, repo_url)
            if not modules:
                print(f"⚠️  No modules discovered for listing group '{group_name}'.")
                continue

            discovered_any = True
            self._print_group(group_name, modules)

        if not discovered_any:
            print("⚠️  Module listings were located, but no modules were returned.")
            return False

        return True

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _collect_listing_sources(self) -> Dict[str, str]:
        sources: Dict[str, str] = {}
        sources.update(self._read_listing_file(self.public_listing_path, "public"))
        sources.update(self._read_listing_file(self.private_listing_path, "private"))
        return sources

    def _read_listing_file(self, listing_path: Path, label: str) -> Dict[str, str]:
        if not listing_path.exists():
            return {}

        try:
            yaml_file = YamlUtil.read_yaml(listing_path)
        except FileNotFoundError:
            print(f"⚠️  Listing file '{listing_path}' is missing or invalid; skipping {label} sources.")
            return {}

        if not yaml_file:
            print(f"⚠️  Listing file '{listing_path}' is empty; skipping {label} sources.")
            return {}

        data = yaml_file.to_dict()
        if not isinstance(data, dict):
            print(f"⚠️  Listing file '{listing_path}' does not contain a mapping; skipping {label} sources.")
            return {}

        listings: Dict[str, str] = {}
        for group, repo in data.items():
            if isinstance(repo, str) and repo.strip():
                listings[str(group)] = repo.strip()
            else:
                print(f"⚠️  Skipping malformed entry '{group}' in {listing_path}.")
        return listings

    def _fetch_group_modules(self, group_name: str, repo_url: str) -> List[Dict[str, str]]:
        listing_yaml = self._load_listing_yaml(repo_url)
        if not listing_yaml:
            print(f"⚠️  Unable to load listing.yaml for group '{group_name}'.")
            return []

        listing_data = listing_yaml.to_dict()
        if not isinstance(listing_data, dict):
            print(f"⚠️  Listing for group '{group_name}' is not a mapping; skipping.")
            return []

        modules: List[Dict[str, str]] = []
        for module_name, module_meta in listing_data.items():
            if not isinstance(module_meta, dict):
                continue
            modules.append(
                {
                    "name": str(module_name),
                    "type": str(module_meta.get("type", "unknown")),
                    "description": str(
                        module_meta.get("description", "No description provided.")
                    ),
                }
            )

        modules.sort(key=lambda item: item["name"].lower())
        return modules

    def _load_listing_yaml(self, repo_url: str) -> Optional[YamlFile]:
        if not repo_url:
            return None

        listing_filename = self.LISTING_FILENAME

        if YamlUtil.is_url(repo_url):
            if repo_url.endswith((".yaml", ".yml")):
                yaml_file = YamlUtil.read_yaml_from_url_direct(repo_url, "")
                if yaml_file:
                    return yaml_file

            yaml_file = YamlUtil.read_yaml_from_url(
                repo_url,
                listing_filename,
                allow_clone_fallback=False,
            )
            if yaml_file:
                return yaml_file

        return self._load_listing_via_clone(repo_url, listing_filename)

    def _load_listing_via_clone(self, repo_url: str, listing_filename: str) -> Optional[YamlFile]:
        yaml_file = YamlUtil.read_yaml_from_url_via_clone(
            repo_url,
            listing_filename,
            clone_root=self.clone_tmp_root,
        )

        if not yaml_file:
            print(f"⚠️  Failed to retrieve '{listing_filename}' from repository '{repo_url}'.")

        return yaml_file

    def _print_group(self, group_name: str, modules: List[Dict[str, str]]) -> None:
        header = f"📦 {group_name} ({len(modules)} module{'s' if len(modules) != 1 else ''})"
        print(f"\n{header}")
        for module in modules:
            description = module["description"].strip() or "No description provided."
            print(f"  • {module['name']} ({module['type']}): {description}")

