# Guía de Despliegue (Deployment) 🚀

Esta guía te llevará paso a paso para publicar tu aplicación en internet usando **GitHub** y **Render** (Gratis).

## 1. Preparar el Código (Git)

Primero necesitamos subir tu código a un repositorio de GitHub.

1.  **Inicializar Git** (si no lo has hecho):
    Abre tu terminal en la carpeta del proyecto y ejecuta:
    ```bash
    git init
    git add .
    git commit -m "Versión final lista para despliegue"
    ```

2.  **Crear Repositorio en GitHub**:
    *   Ve a [github.com/new](https://github.com/new).
    *   Nombre: `embroidery-converter` (o el que quieras).
    *   Público o Privado: Da igual.
    *   **NO** marques "Initialize with README" (ya tenemos uno).
    *   Dale a "Create repository".

3.  **Conectar y Subir**:
    Copia los comandos que te da GitHub (se verán parecidos a estos) y ejecútalos en tu terminal:
    ```bash
    git branch -M main
    git remote add origin https://github.com/TU_USUARIO/embroidery-converter.git
    git push -u origin main
    ```

## 2. Desplegar en Render (PaaS)

Render detectará automáticamente nuestro `Dockerfile` y se encargará de todo.

1.  Crea una cuenta en [render.com](https://render.com).
2.  En el Dashboard, haz clic en **New +** y selecciona **Web Service**.
3.  Selecciona **Build and deploy from a Git repository**.
4.  Conecta tu cuenta de GitHub y selecciona el repo `embroidery-converter` que acabas de subir.
5.  **Configuración**:
    *   **Name**: `embroidery-app` (será parte de tu URL).
    *   **Environment**: `Docker` (Render debería detectarlo solo).
    *   **Region**: La que prefieras (ej: Frankfurt o Oregon).
    *   **Branch**: `main`.
    *   **Plan**: Free (Gratis).

6.  Haz clic en **Create Web Service**.

## 3. ¡Listo!

Render empezará a construir tu aplicación (puede tardar unos minutos la primera vez).
Cuando termine, verás un mensaje de "Live" y una URL tipo:
`https://embroidery-app-xyz.onrender.com`

¡Comparte esa URL y cualquiera podrá usar tu convertidor!
