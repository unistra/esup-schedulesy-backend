FROM nginx:latest

RUN rm /etc/nginx/conf.d/default.conf

COPY deploy/docker/nginx/nginx.conf /etc/nginx/nginx.conf
COPY deploy/docker/nginx/app.conf /etc/nginx/sites-available/

RUN mkdir -p /etc/nginx/sites-enabled/\
    && ln -s /etc/nginx/sites-available/app.conf /etc/nginx/sites-enabled/

# TODO: used to customized nginx config needed later
# Use the configuration script as the entrypoint
# COPY deploy/docker/nginx/entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh

# ENTRYPOINT ["/entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]
