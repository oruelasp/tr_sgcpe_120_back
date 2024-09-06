# SISTEMA SCALVIR (BACKEND)


## Descripción:
#### Aplicativo para el Servicio de Conciliación Administrativa Laboral Virtual

---
## Requerimientos y dependencias:
<p align="left">
   <a href="https://www.w3schools.com/css/" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original-wordmark.svg" alt="css3" width="40" height="40"/>
   </a>
   <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer">
      <img src="https://cdn.worldvectorlogo.com/logos/django.svg" alt="django" width="40" height="40"/>
   </a>
   <a href="https://www.docker.com/" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original-wordmark.svg" alt="docker" width="40" height="40"/>
   </a>
   <a href="https://git-scm.com/" target="_blank" rel="noreferrer">
      <img src="https://www.vectorlogo.zone/logos/git-scm/git-scm-icon.svg" alt="git" width="40" height="40"/>
   </a>
   <a href="https://www.w3.org/html/" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original-wordmark.svg" alt="html5" width="40" height="40"/>
   </a>
   <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" alt="javascript" width="40" height="40"/>
   </a>
   <a href="https://www.linux.org/" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/linux/linux-original.svg" alt="linux" width="40" height="40"/>
   </a>
   <a href="https://www.nginx.com" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/nginx/nginx-original.svg" alt="nginx" width="40" height="40"/>
   </a>
   <a href="https://www.python.org" target="_blank" rel="noreferrer">
      <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/>
   </a>
   <a href="https://vuejs.org/" target="_blank" rel="noreferrer">
   <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/vuejs/vuejs-original-wordmark.svg" alt="vuejs" width="40" height="40"/>
   </a>
</p>

---
## Configuración e Instalación:

#### Configuración en Django:
```
settings/base.py
```
---

#### Instalación de entorno y dependencias:
1. Instalar pip y virtualenv:
   ```
   sudo apt-get install python-pip python-virtualenv
   ```
2. Crear entorno virtual:
   ```
   virtualenv --no-site-package --distribute
   ```
3. Activar el entorno virtual:
   ```
   source bin/activate
   ```
4. Instalar dependencias:
   1. Desarrollo:
   ```
   pip install -r requirements/local.txt
   ```
   2. Producción:
   ```
   pip install -r requirements/production.txt
   ```
---

#### Variables de entorno:

| Variable               | Descripción                                              | Requerido | Ejemplo                                           |
|------------------------|----------------------------------------------------------|-----------|---------------------------------------------------|
| DB_NAME_URL            | Url base datos                                           | Sí      | `db:1521/XEPDB1`                                  |
| DB_USER                | Usuario base datos                                       | Sí      | `ATCOADLASYS`                                     |
| DB_PASS                | Password base datos                                      | Sí      | `ATCOADLASYS`                                     |
| DJANGO_SETTINGS_MODULE | Configuración del Django                                 | Sí      | `config.settings.base`                            |
| DJANGO_SECRET_KEY      | Key del server                                           | Sí      | `secret-key`                                      |
| DJANGO_ALLOWED_HOSTS   | Hosts con acceso                                         | Sí      | `localhost, localhost2`                           |
| LDR_HOST_API           | Host de Línea Dedicada a Reniec                          | Sí      | `http://10.100.206.200:8080`                      |
| LDR_PATH_API           | Ruta endpoint de Línea Dedicada a Reniec                 | Sí      | `reniecld-rest/consulta/datos`                    |
| WSM_HOST_API           | Host de Web Service Sunat/Migraciones                    | Sí      | `https://ws.trabajo.gob.pe`                       |
| WSM_PATH_API           | Ruta endpoint de Web Service Sunat/Migraciones           | Sí      | `migraciones-rest/consulta/cpp`                   |
| CODIGO_SISTEMA         | Código del sistema en el Sistema de Seguridad - SIMINTRA | Sí      | `123`                                             |
| CODIGO_SISTEMA_WS      | Código del sistema para el uso de Webservices del MINTRA | Sí      | `126`                                             |
| CORS_ALLOWED_HOSTS     | Hosts del front end para tener acceso backend            | Sí      | `http://localhost:8080,http://192.168.41.23`      |
| WSR_PATH_API           | Ruta endpoint de Web Service de Reniec                   | Sí      | `siscoweb/client/api/sunat/pide/datosPrincipales` |
| WSR_USERNAME_API       | Username del Web Service de Sunat/Migraciones            | Sí      | `MTPEWS`                                          |
| WSR_PASSWORD_API       | Password del Web Service de Sunat/Migraciones            | Sí      | `*****`                                           |


## Configuración de Datos del Sistema
* Configuración del Sistema y Perfiles (En Coordinación con el área encargada)
  * Realizar la creación del Sistema SCALVIR en el SIMINTRA1
  * Realizar la creación de los siguientes Perfiles en el SIMINTRA1:
    * (001) ADMINISTRADOR
    * (002) PROGRAMADOR
    * (003) CONCILIADOR
* Configuración del Token Confidencial
  * Realizar la inserción del Token Confidencial en SCALVIR:
    * Ejecutar el query de INSERT de Token-Confidencial que se encuentra en /database/6.Inserciones.sql
    
* Configuración de Grupos
  * Realizar la ejecución del siguiente API para la asignación de Grupos en SCALVIR:
    ``https://scalvir.trabajo.gob.pe/seguridad/api/grupo/ ``
  * Ingresar en el Body del request el contenido especificado en /seguridad/fixtures/grupos.json
  
* Configuración de Menúes
  * Realizar la ejecución del siguiente API para la creación de Menués en SCALVIR:
    ``https://scalvir.trabajo.gob.pe/seguridad/api/menu/ ``
  *  Ingresar en el Body del request el contenido especificado en /seguridad/fixtures/menues.json

* Configuración de Grupo-Menués
  * Realizar la ejecución del siguiente API para la relación de Grupos por Menués en SCALVIR:
    ``https://scalvir.trabajo.gob.pe/seguridad/api/grupo-menu/ ``
  *  Ingresar en el Body del request el contenido especificado en /seguridad/fixtures/grupo-menues.json

* Configuración de Token Público
  * Realizar la ejecución del siguiente API para la relación de Grupos por Menués en SCALVIR:
    ``https://scalvir.trabajo.gob.pe/seguridad/api/parametro/ ``
  *  Ingresar en el Body del request el contenido especificado en /seguridad/fixtures/parametros.json
  
* Configuración de Grupo Usuario
  * Realizar la ejecución del siguiente API para la relación de Grupos Especiales por Usuarios en SCALVIR:
    ``https://scalvir.trabajo.gob.pe/seguridad/api/grupo-usuario/ ``
  *  Ingresar en el Body del request el contenido especificado en /seguridad/fixtures/grupo-usuarios.json

## Manual de Despliegue
  * A fin de conocer el detalle de la arquitectura del sistema y otras variables destacadas, consultar el manual de despliegue.



## Créditos y Licencia:
* Oficina General de Tecnologías de la Información y Comunicaciones (OGTIC)
* Ministerio del Trabajo y la Promoción del Empleo (MTPE) © 2023
