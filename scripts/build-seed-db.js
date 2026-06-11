const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const projectRoot = process.cwd();
const seedDbPath = path.join(projectRoot, 'prisma', 'seed.db');

if (fs.existsSync(seedDbPath)) {
  fs.unlinkSync(seedDbPath);
}

const env = { ...process.env, DATABASE_URL: `file:${seedDbPath}` };

console.log('Creating database schema...');
execSync('npx prisma migrate deploy', { env, stdio: 'inherit' });

console.log('Seeding data...');
execSync('node prisma/seed.js', { env, stdio: 'inherit' });

console.log('Seed database ready at', seedDbPath);
