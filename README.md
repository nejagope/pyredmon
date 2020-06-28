pyredmon
=======
Python + Redis + Mongo

Ejecutar el contenedor
---------------------
Antes de la ejecución, deben configurarse las variables de entorno en el archivo .env

```console
sudo docker run -d -v /home/nelson/Escritorio/so1p2/pyredmon:/app -p 5000:5000 --env-file .env --name pyredmon  pyredmon
```

sudo docker run -it -v /home/nelson/Escritorio/so1p2/pyredmon:/app --env-file .env --name pyredmon  pyredmon