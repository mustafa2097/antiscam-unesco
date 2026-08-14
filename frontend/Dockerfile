# Multi-stage: build Vite frontend, serve with nginx, proxy /api to backend URL at runtime via env.
# For simplest free hosting, prefer Cloudflare Pages / Netlify for the static frontend
# and point VITE_API_BASE_URL to the Render API. This Dockerfile is optional.

FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
