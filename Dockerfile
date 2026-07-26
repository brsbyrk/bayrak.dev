FROM nginx:alpine
COPY build/ /usr/share/nginx/html/
RUN echo 'server { listen 80; root /usr/share/nginx/html; index index.html; location / { try_files $uri $uri/ /404.html; } }' > /etc/nginx/conf.d/default.conf
