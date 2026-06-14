FROM node:20-alpine

WORKDIR /app

# Install deps
COPY package.json package-lock.json* ./
RUN npm ci --legacy-peer-deps || npm install

COPY . .

# Dev mode: command overridden by compose to npm run dev
# For prod build would be: npm run build && npm start
EXPOSE 3000
CMD ["npm", "run", "dev"]