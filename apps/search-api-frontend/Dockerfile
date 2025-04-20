# Dockerfile

FROM node:22.14.0

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy the rest of the files
COPY . .

# Expose the Vite dev server port
EXPOSE 5173

# Start Vite in dev mode
CMD ["npm", "run", "dev"]
