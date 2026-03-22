const fs = require('fs');
const path = require('path');

const projectRoot = path.resolve(__dirname, '..');
const configsRoot = path.join(projectRoot, 'configs');

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.isFile() && entry.name.endsWith('.json')) out.push(full);
  }
  return out.sort();
}

function loadJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function exists(p) {
  try {
    fs.accessSync(p, fs.constants.R_OK);
    return true;
  } catch {
    return false;
  }
}

function isInsideRepo(absPath) {
  const rel = path.relative(projectRoot, absPath);
  return rel && !rel.startsWith('..') && !path.isAbsolute(rel);
}

function classifyReference(ownerPath, key, refPath, bucket) {
  if (!refPath || typeof refPath !== 'string') return;

  const absolute = path.isAbsolute(refPath)
    ? refPath
    : path.resolve(path.dirname(ownerPath), refPath);

  if (exists(absolute)) return;

  const row = {
    config: path.relative(projectRoot, ownerPath),
    key,
    ref: refPath,
    resolved: absolute,
  };

  if (isInsideRepo(absolute)) bucket.repoMissing.push(row);
  else bucket.externalMissing.push(row);
}

function collectReferences(ownerPath, cfg, bucket) {
  if (!cfg || typeof cfg !== 'object') return;

  classifyReference(ownerPath, 'backgroundPath', cfg.backgroundPath, bucket);

  if (cfg.productImage && typeof cfg.productImage === 'object') {
    classifyReference(ownerPath, 'productImage.path', cfg.productImage.path, bucket);
  }

  if (cfg.productComposite && typeof cfg.productComposite === 'object') {
    classifyReference(ownerPath, 'productComposite.path', cfg.productComposite.path, bucket);
  }

  if (Array.isArray(cfg.logos)) {
    cfg.logos.forEach((logo, idx) => {
      if (logo && typeof logo === 'object') {
        classifyReference(ownerPath, `logos[${idx}].path`, logo.path, bucket);
      }
    });
  }
}

const files = walk(configsRoot);
const bucket = {
  parsed: 0,
  jsonErrors: [],
  repoMissing: [],
  externalMissing: [],
};

for (const file of files) {
  let data;
  try {
    data = loadJson(file);
    bucket.parsed += 1;
  } catch (error) {
    bucket.jsonErrors.push({
      config: path.relative(projectRoot, file),
      error: error.message,
    });
    continue;
  }

  if (data && typeof data === 'object' && Array.isArray(data.renders)) {
    collectReferences(file, data.defaults || {}, bucket);
    for (const render of data.renders) collectReferences(file, render, bucket);
  } else {
    collectReferences(file, data, bucket);
  }
}

console.log(`Validated ${bucket.parsed}/${files.length} config JSON files.`);

if (bucket.jsonErrors.length) {
  console.log(`\nJSON parse failures (${bucket.jsonErrors.length}):`);
  for (const item of bucket.jsonErrors.slice(0, 20)) {
    console.log(`- ${item.config}: ${item.error}`);
  }
}

if (bucket.repoMissing.length) {
  console.log(`\nMissing repo-local asset refs (${bucket.repoMissing.length}):`);
  for (const item of bucket.repoMissing.slice(0, 20)) {
    console.log(`- ${item.config} :: ${item.key} -> ${item.ref}`);
  }
}

if (bucket.externalMissing.length) {
  console.log(`\nMissing external asset refs (${bucket.externalMissing.length}) — warning only:`);
  for (const item of bucket.externalMissing.slice(0, 20)) {
    console.log(`- ${item.config} :: ${item.key} -> ${item.ref}`);
  }
  if (bucket.externalMissing.length > 20) {
    console.log(`- ... ${bucket.externalMissing.length - 20} more`);
  }
}

if (bucket.jsonErrors.length || bucket.repoMissing.length) {
  process.exit(1);
}
