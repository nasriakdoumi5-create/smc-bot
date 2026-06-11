import { PrismaClient } from '@prisma/client';
import fs from 'fs';
import path from 'path';

const globalForPrisma = globalThis;

function getDbUrl() {
  // On Vercel (serverless), copy seed DB to /tmp which is writable
  if (process.env.VERCEL) {
    const tmpDb  = '/tmp/store.db';
    const seedDb = path.join(process.cwd(), 'prisma/seed.db');
    if (!fs.existsSync(tmpDb) && fs.existsSync(seedDb)) {
      fs.copyFileSync(seedDb, tmpDb);
    }
    return `file:${tmpDb}`;
  }
  return process.env.DATABASE_URL || 'file:./prisma/dev.db';
}

function createClient() {
  return new PrismaClient({
    datasources: { db: { url: getDbUrl() } },
  });
}

export const db = globalForPrisma.prisma ?? createClient();
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db;
