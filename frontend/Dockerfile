# Use Nginx to serve the app
FROM nginx:alpine

# COPY THE STATIC FILES
COPY src/ /usr/share/nginx/html

# --- ADD THIS LINE ---
# Overwrite default config with our custom proxy config
COPY nginx.conf /etc/nginx/conf.d/default.conf
# ---------------------

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]