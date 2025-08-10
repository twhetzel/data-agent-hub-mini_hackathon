import { Hono } from "hono";
import { cors } from "hono/cors";
import OpenAI from "openai";
import { buildPrompt } from "./prompt.js";

const app = new Hono();

app.get("/health", c => c.json({ ok: true, model: MODEL }));

app.use("*", cors());

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY! });
const MODEL = process.env.OPENAI_MODEL || "gpt-4o-mini";

app.get("/", c => c.json({ ok: true, model: MODEL }));

app.post("/agent", async c => {
    const body = await c.req.json<{ schema_description: string; sample_rows: string }>();

    const prompt = await buildPrompt(body.schema_description, body.sample_rows);

    const completion = await client.chat.completions.create({
        model: MODEL,
        temperature: 0.1,
        messages: [
            { role: "system", content: "You are a data visualization agent." },
            { role: "user", content: prompt }
        ]
    });

    const text = completion.choices[0]?.message?.content ?? "{}";

    // Best-effort JSON extraction: first { ... } block
    const match = text.match(/\{[\s\S]*\}$/);
    const json = JSON.parse(match ? match[0] : "{}");

    return c.json(json);
});

import { serve } from "@hono/node-server";
const PORT = Number(process.env.PORT || 3000);
console.log(`[agent-service] listening on http://localhost:${PORT}`);
console.log("Freestyle env PORT:", process.env.PORT);
serve({ fetch: app.fetch, port: PORT });
