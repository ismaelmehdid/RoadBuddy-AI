FROM node:20-alpine

WORKDIR /app

COPY bot/package*.json ./
RUN npm install

COPY bot/ .

RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
