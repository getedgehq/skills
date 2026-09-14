import assert from "node:assert/strict";
import { mkdtemp, mkdir, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";

const script = new URL("../scripts/check-project.mjs", import.meta.url).pathname;
const root = await mkdtemp(path.join(tmpdir(), "launch-video-skill-"));

let result = spawnSync(process.execPath, [script, root], { encoding: "utf8" });
assert.notEqual(result.status, 0);
assert.match(result.stderr, /missing STORYBOARD\.md/);

await mkdir(path.join(root, "compositions"));
await mkdir(path.join(root, "renders"));
await writeFile(path.join(root, "design.md"), "# Design\n");
await writeFile(
  path.join(root, "STORYBOARD.md"),
  "# Storyboard\nStart: 0\nEnd: 4\nClaim: faster\nSource: benchmark\nTransition: cut\n",
);
await writeFile(path.join(root, "renders", "launch.mp4"), "rendered fixture");

result = spawnSync(process.execPath, [script, root], { encoding: "utf8" });
assert.equal(result.status, 0, result.stderr);
assert.match(result.stdout, /gate passed/);

console.log("check-project tests passed");

