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

## 2. Desplegar en Render (Opción A: Automática con Blueprint)

Como he añadido un archivo `render.yaml` al proyecto, esto es lo más fácil:

1.  En [Render Dashboard](https://dashboard.render.com/), haz clic en **New +** > **Blueprint**.
2.  Conecta tu repositorio `embroidery-converter`.
3.  Render detectará la configuración automáticamente.
4.  Haz clic en **Apply**. ¡Y listo!

## 3. Desplegar en Render (Opción B: Manual)

Si prefieres hacerlo a mano:

1.  Haz clic en **New +** > **Web Service**.
2.  Conecta tu repositorio.
3.  Configuración:
    *   **Name**: `embroidery-app`
    *   **Environment**: `Docker`
    *   **Region**: Oregon o Frankfurt.
    *   **Plan**: Free.
4.  Haz clic en **Create Web Service**.

## 4. ¡Listo!

Render empezará a construir tu aplicación (puede tardar unos minutos la primera vez).
Cuando termine, verás un mensaje de "Live" y una URL tipo:
`https://embroidery-app-xyz.onrender.com`

¡Comparte esa URL y cualquiera podrá usar tu convertidor!
