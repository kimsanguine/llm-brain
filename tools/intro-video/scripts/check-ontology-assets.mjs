import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const names = ['information-field', 'reuse-field', 'ontology-atlas'];
const missing = names.filter((name) => !existsSync(fileURLToPath(new URL(`../public/ontology/${name}.webp`, import.meta.url))));
if (missing.length) {
  console.error(`Ontology artwork is required before rendering:\n${missing.map((name) => `  public/ontology/${name}.webp`).join('\n')}`);
  process.exitCode = 1;
} else {
  console.log('All three ontology artwork dependencies are present.');
}
