FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Add our custom config
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Copy static frontend
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80
