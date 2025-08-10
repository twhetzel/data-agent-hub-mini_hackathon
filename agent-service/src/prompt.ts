import fs from "node:fs/promises";
import YAML from "yaml";

export async function buildPrompt(schemaDescription: string, sampleRows: string) {
    const raw = await fs.readFile("freestyle/data_ui_agent.yaml", "utf-8");
    const y = YAML.parse(raw);
    const instructions = (y.instructions ?? "").trim();
    const tmpl = (y.prompt ?? "").trim()
        .replace("{{schema_description}}", schemaDescription)
        .replace("{{sample_rows}}", sampleRows);

    const strict =
        `Return ONLY a single JSON object with keys "summary","suggested_visuals","chart_specs". ` +
        `No markdown fences or extra text.`;

    return `${instructions}\n\n${strict}\n\n${tmpl}`;
}
