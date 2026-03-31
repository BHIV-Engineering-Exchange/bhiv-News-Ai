# Prisma Configuration - Fixed

## Issue Resolved ✓

### Original Error
```
Error: The datasource property `url` is no longer supported in schema files.
  --> prisma/schema.prisma:10
   ...
error: Argument "url" is missing in data source block "db".
```

### Root Cause
- **Prisma npm audit** tried to install version 7.6.0
- **Project uses** Prisma 6.19.2 (from package.json)
- **Prisma 6.x requires** `url` in schema
- **Prisma 7.x removed** this requirement

### Solution ✓

**Use Prisma 6.x (current stable for this project)**:
- ✓ Schema includes: `url = env("DATABASE_URL")`
- ✓ Build script simplified for clarity
- ✓ Environment variable: DATABASE_URL configured
- ✓ All dependencies locked in package.json

---

## Setup (Prisma 6.19.2)

### 1. **Environment Variable**
```bash
# In .env.local or .env
DATABASE_URL="postgresql://user:password@host:5432/news_ai_db"
```

### 2. **Install Dependencies**
```bash
npm install --legacy-peer-deps
```

### 3. **Generate Client**
```bash
npx prisma generate
# ✓ Generated Prisma Client (v6.19.2)
```

### 4. **Run Migrations**
```bash
npx prisma migrate deploy
```

### 5. **Build**
```bash
npm run build
```

---

## Configuration Summary

| Item | Status | Details |
|------|--------|---------|
| **Schema** | ✓ Fixed | Has `url = env("DATABASE_URL")` |
| **Build Script** | ✓ Fixed | Uses `npx prisma generate` |
| **Prisma Version** | ✓ Locked | ^6.19.2 in package.json |
| **Client** | ✓ Simplified | Standard PrismaClient() init |

---

## Files Modified

```
blackhole-frontend/
├── prisma/
│   └── schema.prisma              ✓ Restored url property (Prisma 6 compatible)
├── lib/
│   └── prisma.ts                  ✓ Simplified client init
└── package.json                   ✓ Fixed build script
```

---

## Future: Upgrade to Prisma 7

When ready to upgrade to Prisma 7.x:
1. Update `package.json`: Change @prisma/client to ^7.0.0
2. Remove `url` from schema datasource
3. Create `prisma.config.ts` with datasource config
4. Update PrismaClient initialization if needed
5. Run `npm install` and test thoroughly

---

## Testing ✓

```bash
$ npx prisma generate
Prisma schema loaded from prisma\schema.prisma
✓ Generated Prisma Client (v6.19.2) to .\node_modules\@prisma\client in 398ms
```

---

**Current Setup**: Prisma 6.19.2 (Stable)  
**Status**: ✓ Working  
**Last Fixed**: March 31, 2026
