#!/usr/bin/env python3
import json
from pathlib import Path

path = Path(__file__).with_name("edge-database.json")
data = json.loads(path.read_text())

assert data["schema_version"] == 1
skills = data["skills"]
tasks = data["tasks"]
skill_ids = [item["id"] for item in skills]
task_ids = [item["id"] for item in tasks]
assert len(skill_ids) == len(set(skill_ids)) == data["counts"]["skills"]
assert len(task_ids) == len(set(task_ids)) == data["counts"]["tasks"]

known_skills = set(skill_ids)
known_tasks = set(task_ids)
for skill in skills:
    assert skill["title"] and skill["summary"] and skill["category"]
    assert skill["package"]["record_url"].endswith(f"/{skill['id']}.json")
    assert set(skill["task_ids"]) <= known_tasks
for task in tasks:
    assert task["skill"] in known_skills
    assert task["configurations"]
    for configuration in task["configurations"]:
        assert configuration["pairs"] > 0
        assert "overall" in configuration["metrics"]

print(f"valid: {len(skills)} skills, {len(tasks)} tasks")
