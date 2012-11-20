server {

        listen 80;
       server_name analytics.topface.com;

        charset utf-8;


        location / {
            proxy_pass http://127.0.0.1:48888;
        }
}