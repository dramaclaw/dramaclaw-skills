from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from build_catalog import CatalogValidationError, build_catalog, validate_repository  # noqa: E402


def skill_payload(item_id: str = "community-video", **overrides) -> dict:
    payload = {
        "schema_version": "dramaclaw.workflow-skill.v1",
        "id": item_id,
        "name": "社区视频",
        "version": "1.0.0",
        "description": "把用户素材规划成视频工作流。",
        "category": "video",
        "triggers": {"keywords": ["社区视频"], "node_scopes": ["textGeneration"]},
        "allowed_recipe_ids": ["community-brief"],
        "input_parameters": [
            {
                "id": "aspect_ratio",
                "label": "画幅",
                "type": "single_select",
                "required": True,
                "default": "16:9",
                "options": ["16:9", "1:1"],
            }
        ],
        "planning": {
            "planning_notes": "根据用户输入动态规划。",
            "prompt_guide": "保持中文输出。",
            "conduct_rules": ["生成前确认。"],
        },
        "evaluation": {
            "rating_bands": [{"score": 5, "description": "可用"}],
            "quality_threshold": 4,
            "domain_constraints": ["不得虚构用户素材事实"],
        },
    }
    payload.update(overrides)
    return payload


def recipe_payload(item_id: str = "community-brief", **overrides) -> dict:
    payload = {
        "schema_version": "dramaclaw.recipe.v1",
        "id": item_id,
        "name": "社区简报",
        "version": "1.0.0",
        "output_kind": "text",
        "action_keys": ["community-brief"],
        "system_prompt": "把用户输入整理成视频简报。",
        "must_have_items": ["主题", "画幅"],
        "planning_prompt": "生成视频简报。",
        "result_summary": "视频简报。",
    }
    payload.update(overrides)
    return payload


def bundle_payload(**overrides) -> dict:
    payload = {
        "schema_version": "dramaclaw.skill-bundle.v1",
        "id": "community-video",
        "name": "社区视频",
        "version": "1.0.0",
        "description": "社区视频动态工作流。",
        "author": "DramaClaw",
        "license": "CC-BY-4.0",
        "min_dramaclaw_version": "2.0.0",
        "tags": ["video", "community"],
        "skill": skill_payload(),
        "recipes": [recipe_payload()],
    }
    payload.update(overrides)
    return payload


def write_bundle(root: Path, bundle: dict, *, path_id: str | None = None) -> None:
    bundle_dir = root / "skills" / (path_id or str(bundle["id"]))
    bundle_dir.mkdir(parents=True)
    (bundle_dir / "bundle.json").write_text(
        json.dumps(bundle, ensure_ascii=False),
        encoding="utf-8",
    )


class CatalogCiTest(unittest.TestCase):
    def test_official_freezone_bundles_include_their_referenced_recipes(self) -> None:
        expected_bundle_ids = {
            "japanese-anime-drama-video",
            "lego-minifigure-animation-video",
            "ling-cage-cinematic-video",
            "outdoor-stage-duel-video",
            "retro-hong-kong-kungfu-comedy-video",
        }

        records = validate_repository(REPO_ROOT)

        record_ids = {record.bundle_id for record in records}
        self.assertTrue(expected_bundle_ids <= record_ids)
        for record in records:
            if record.bundle_id not in expected_bundle_ids:
                continue
            recipe_ids = {recipe["id"] for recipe in record.bundle["recipes"]}
            self.assertEqual(set(record.bundle["skill"]["allowed_recipe_ids"]), recipe_ids)

            legal = record.bundle["legal"]
            self.assertEqual("2026 SuperTale contributors", legal["copyright"])
            self.assertEqual("Elastic-2.0", legal["license"]["id"])
            self.assertIn("Elastic License 2.0", legal["license"]["text"])
            self.assertIn("DramaClaw", legal["notice"])

    def test_validate_repository_accepts_skills_directory_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_bundle(root, bundle_payload())

            records = validate_repository(root)

            self.assertEqual([record.bundle_id for record in records], ["community-video"])

    def test_build_catalog_uses_bundle_metadata_and_urls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_bundle(root, bundle_payload())
            (root / "skills" / "community-video" / "cover.webp").write_bytes(b"cover")

            catalog = build_catalog(
                root,
                raw_base_url="https://raw.githubusercontent.com/dramaclaw/dramaclaw-skills/main",
            )

            self.assertEqual(
                catalog,
                {
                    "schema_version": "dramaclaw.community-catalog.v1",
                    "items": [
                        {
                            "id": "community-video",
                            "name": "社区视频",
                            "version": "1.0.0",
                            "description": "社区视频动态工作流。",
                            "author": "DramaClaw",
                            "license": "CC-BY-4.0",
                            "min_dramaclaw_version": "2.0.0",
                            "tags": ["video", "community"],
                            "bundle_url": "https://raw.githubusercontent.com/dramaclaw/dramaclaw-skills/main/skills/community-video/bundle.json",
                            "cover_url": "https://raw.githubusercontent.com/dramaclaw/dramaclaw-skills/main/skills/community-video/cover.webp",
                        }
                    ],
                },
            )

    def test_validate_repository_rejects_path_id_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_bundle(root, bundle_payload(), path_id="wrong-path")

            with self.assertRaisesRegex(CatalogValidationError, "path must match bundle id"):
                validate_repository(root)

    def test_validate_repository_rejects_missing_recipe_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_bundle(root, bundle_payload(recipes=[]))

            with self.assertRaisesRegex(CatalogValidationError, "missing referenced Recipes"):
                validate_repository(root)

    def test_validate_repository_rejects_scripts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_bundle(
                root,
                bundle_payload(recipes=[recipe_payload(script="echo bad")]),
            )

            with self.assertRaisesRegex(CatalogValidationError, "dangerous field"):
                validate_repository(root)

    def test_validate_repository_rejects_model_pinning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_bundle(
                root,
                bundle_payload(recipes=[recipe_payload(system_prompt="固定使用 gpt-image-2 生成。")]),
            )

            with self.assertRaisesRegex(CatalogValidationError, "supplier model name"):
                validate_repository(root)

    def test_empty_repository_can_be_allowed_for_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertEqual(validate_repository(Path(temp_dir), allow_empty=True), [])

    def test_empty_repository_fails_without_bootstrap_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(CatalogValidationError, "No skill bundles found"):
                validate_repository(Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
