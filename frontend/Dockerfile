FROM node:20-alpine AS base
WORKDIR /app

COPY package.json package-lock.json ./

FROM base AS prod-deps
RUN npm install --production

FROM base AS build-deps
RUN npm install --production=false

FROM build-deps AS build
###
# COPY . .
###
COPY ./public/ ./public/
COPY ./src/ ./src/
COPY ./astro.config.mjs tsconfig.json .env.local .env.production ./
###
RUN npm run build

FROM base AS runtime
COPY --from=prod-deps /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist

ENV HOST=0.0.0.0
ENV PORT=80

EXPOSE 80

CMD node ./dist/server/entry.mjs
