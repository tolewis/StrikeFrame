const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const projectRoot = path.resolve(__dirname, '..');
const smokeOutputDir = path.join(projectRoot, 'output', 'smoke');

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: projectRoot,
    encoding: 'utf8',
    ...options,
  });
  return result;
}

function requireFile(filePath, label) {
  if (!fs.existsSync(filePath)) {
    throw new Error(`${label} missing: ${filePath}`);
  }
}

function makeSmokeConfig(configPath) {
  const absolute = path.join(projectRoot, configPath);
  const data = JSON.parse(fs.readFileSync(absolute, 'utf8'));
  fs.mkdirSync(smokeOutputDir, { recursive: true });

  const baseName = path.basename(configPath, '.json');
  const outputName = `${baseName}.jpg`;
  data.output = path.join(smokeOutputDir, outputName);

  const tempPath = path.join(os.tmpdir(), `strikeframe-smoke-${baseName}-${process.pid}.json`);
  fs.writeFileSync(tempPath, JSON.stringify(data, null, 2));
  return tempPath;
}

function runRender(configPath) {
  const tempConfig = makeSmokeConfig(configPath);
  const result = run('node', ['scripts/render.js', tempConfig]);
  if (result.status !== 0) {
    throw new Error(`render failed for ${configPath}\n${result.stdout}\n${result.stderr}`);
  }

  let payload;
  try {
    payload = JSON.parse(result.stdout.trim());
  } catch (error) {
    throw new Error(`render output was not valid JSON for ${configPath}: ${error.message}\n${result.stdout}`);
  }

  requireFile(payload.output, `render output for ${configPath}`);
  requireFile(payload.reviewPath, `review output for ${configPath}`);

  if (payload.reviewStatus === 'fail') {
    throw new Error(`review failed for ${configPath}: ${payload.reviewPath}`);
  }

  console.log(`✔ render ${configPath} -> ${payload.reviewStatus}`);
}

function runQaqc(configPath, reportPath) {
  const result = run('python3', ['scripts/qaqc.py', configPath]);
  if (![0, 1].includes(result.status)) {
    throw new Error(`qaqc crashed for ${configPath}\n${result.stdout}\n${result.stderr}`);
  }

  const absoluteReport = path.join(projectRoot, reportPath);
  requireFile(absoluteReport, `qaqc report for ${configPath}`);

  const report = JSON.parse(fs.readFileSync(absoluteReport, 'utf8'));
  const failed = (report.renders || []).filter((item) => item.final_status === 'fail');
  if (failed.length) {
    throw new Error(`qaqc reported fail for ${configPath}: ${failed.map((x) => x.output).join(', ')}`);
  }

  const summary = (report.renders || []).map((item) => item.final_status).join(', ');
  console.log(`✔ qaqc ${configPath} -> ${summary || 'no-renders'}`);
}

try {
  console.log('StrikeFrame smoke tests');
  console.log('-----------------------');
  runRender('configs/sample-banner.json');
  runRender('configs/sample-social-square.json');
  runRender('configs/sample-linkedin-landscape.json');
  runRender('configs/sample-product-composite.json');
  runQaqc('configs/sample-batch.json', 'configs/sample-batch.qaqc-report.json');
  console.log('\nAll smoke tests passed.');
} catch (error) {
  console.error(`\nSmoke test failure: ${error.message}`);
  process.exit(1);
}
