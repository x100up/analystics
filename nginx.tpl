server{
    listen {host}:{port};
    server_name

    location ~* \.(jpg|jpeg|gif|png|ico|css|zip|js|swf)$ {
            root $root/static/;
            expires 7d;
    }

    location / {
             proxy_pass http://127.0.0.1:8001/;
             proxy_redirect off;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

}