FROM node:20-bookworm-slim AS deps

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

FROM node:20-bookworm-slim AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .
COPY audio ./public/audio/

ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ARG NEXT_PUBLIC_APP_ENV=production
ARG NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN=false

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_PUBLIC_APP_ENV=$NEXT_PUBLIC_APP_ENV \
    NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN=$NEXT_PUBLIC_ENABLE_CUSTOM_CHARGEN \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run prepare:dice \
    && test -f public/assets/dice-box/assets/ammo/ammo.wasm.wasm \
    || (echo "ERROR: ammo.wasm.wasm missing after prepare:dice" && exit 1)
RUN test -f "public/audio/Solo RPG Theme.mp3" \
    && test -f "public/audio/SoloRPG - Combat.mp3" \
    || (echo "ERROR: audio assets missing — ensure audio/ exists at project root" && exit 1)
RUN npm run build

FROM node:20-bookworm-slim AS runner

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs \
    && adduser --system --uid 1001 --ingroup nodejs nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]
