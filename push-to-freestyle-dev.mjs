// push-to-freestyle-dev.mjs
import { FreestyleSandboxes } from "freestyle-sandboxes";
import fsp from "node:fs/promises";
import path from "node:path";

// 1) Create Freestyle client
const freestyle = new FreestyleSandboxes({
    apiKey: process.env.FREESTYLE_API_KEY,
});

// 2) Create a Freestyle Git repo
const { repoId } = await freestyle.createGitRepository({
    name: "data-agent-hub-agent-service",
    public: true,
    source: { type: "git", url: "https://github.com/freestyle-sh/freestyle-next" },
});
console.log("Repo:", repoId);

// 3) Start a Dev Server for that repo
const dev = await freestyle.requestDevServer({ repoId });
console.log("Dev server:", dev.ephemeralUrl);

// 4) Upload local files, skipping node_modules and junk
const root = path.resolve("./agent-service");
const ignoreDirs = new Set(["node_modules", ".git"]);
const ignoreFiles = new Set([".DS_Store"]);

async function uploadDir(localDir, remoteDir = ".") {
    const entries = await fsp.readdir(localDir, { withFileTypes: true });

    for (const e of entries) {
        if (e.isDirectory()) {
            if (ignoreDirs.has(e.name)) {
                console.log("Skipping dir:", e.name);
                continue;
            }
            await uploadDir(path.join(localDir, e.name), path.posix.join(remoteDir, e.name));
        } else {
            if (ignoreFiles.has(e.name)) {
                console.log("Skipping file:", e.name);
                continue;
            }
            const src = path.join(localDir, e.name);
            const dst = path.posix.join(remoteDir, e.name);

            const content = await fsp.readFile(src);
            await dev.fs.writeFile(dst, content.toString("utf-8"));
            console.log("Wrote", dst);
        }
    }
}

await uploadDir(root);

// 5) Install deps & start server on Dev Server
console.log("Installing… (this can take ~1–2 min)");
await dev.process.exec("npm install", true);

console.log("Starting dev server…");
await dev.process.exec("npm run dev", true);

// 6) Done — print live URLs
console.log("\nLIVE URL:", dev.ephemeralUrl);
console.log("Health:", dev.ephemeralUrl + "/");
console.log("POST     ", dev.ephemeralUrl + "/agent");
