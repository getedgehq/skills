#!/usr/bin/env node
import { access, readFile, stat } from "node:fs/promises";
import { constants } from "node:fs";
import path from "node:path";

const root = path.resolve(process.argv[2] || ".");
const failures = [];

async function required(relative, label = relative) {
  const absolute = path.join(root, relative);
  try {
    await access(absolute, constants.R_OK);
    return absolute;
  } catch {
    failures.push(`missing ${label}: ${relative}`);
    return null;
  }
}

const storyboard = await required("STORYBOARD.md");
await required("design.md");
await required("compositions", "editable compositions directory");
const render = await required("renders/launch.mp4", "final MP4");

if (storyboard) {
  const text = await readFile(storyboard, "utf8");
  for (const term of ["start", "end", "claim", "source", "transition"]) {
    if (!text.toLowerCase().includes(term)) {
      failures.push(`STORYBOARD.md does not expose ${term} information`);
    }
  }
}

if (render && (await stat(render)).size === 0) {
  failures.push("final MP4 is empty");
}

if (failures.length) {
  console.error("Product launch video project gate failed:\n- " + failures.join("\n- "));
  process.exit(1);
}

console.log("Product launch video project gate passed.");

