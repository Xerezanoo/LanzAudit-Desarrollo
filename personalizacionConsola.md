https://dev.to/raulmar/personaliza-tu-terminal-de-0-a-pro-3map

 Personaliza tu terminal de 0 a PRO 😎
#tutorial
#bash
#beginners
#linux

Ten por seguro que personalizar la terminal no te hará un hacker ni mejor desarrollador pero te prometo que vas a sentirte como uno.

A todo desarrolladores nos gusta la personalización de nuestras herramientas y que mejor que empezar con la que probablemente más interactuamos, la terminal.

Esta guía puede servir para Linux, MacOS y WSL (Windows Subsystem for Linux) por lo tanto pueden usar cualquier terminal que tengan, ya sea la terminal por defecto de MacOS, iterm 2.0, GNOME terminal, Terminator, la nueva terminal de Windows etc.

Visita mi sitio raulmar.com para más información
Comparación visual 👀
Antes

1

2
Después

new3

new4

new5

new6



Lo que haremos 🧰

    Cambiaremos la shell por defecto (BASH) por ZSH
    Instalaremos GIT para clonar repositorios desde la nube
    Instalaremos Oh My ZSH que es un administrador de configuración para ZSH el cual nos hará la vida más fácil
    Instalaremos algunos plugins sobre Oh My ZSH
    Instalaremos el tema powerlevel10k con Oh My ZSH que permite una gran cantidad de combinaciones gracias a su configuration wizard
    Agregaremos algunos alias que es como configurar comando personalizados
    Cambiaremos el prompt por defecto de nuestra terminal



Cambiar BASH por ZSH 💱

ZSH es una mejor alternativa al shell por defecto que es BASH, principalmente por sus addons que nos facilitan todo, desde plugins hasta un framework para temas.

    Instalamos ZSH

    sudo apt install zsh

    Seleccionamos ZSH como shell por defecto

    chsh -s $(which zsh)

    #Otra alternativa es:
    #chsh -s `which zsh`

    Reiniciamos la consola

    Revisamos que estemos usando ZSH, si nos sale un error hay que verficar la instalación

    echo $SHELL

    #nos debe responder con
    #/usr/bin/zsh

    Si nos sale el siguiente menú seleccionamos (2) para desktop y (0) para conexiones SSH

    5

Instalamos git 💻

Además de ser una excelente herramienta para desarrollo también la usaremos para que OhMyZSH se pueda instalar correctamente

    Instalamos los paquetes de git

    sudo apt-get install git

    Comprobamos la instalación

    git --version



Instalamos Oh My ZSH 🔧

Este framework creado por la comunidad nos ayuda a configurar nuestro ZSH.
No confundir ZSH y OhMyZSH, OhMyZSH actúa sobre el archivo de configuración de ZSH (.zshrc)

    Instalamos Oh My ZSH

    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

    Oh My ZSH nos modifica el archivo .zshrc y nos crea la carpeta .oh-my-zsh donde encontraremos los plugins, temas, plantillas etc.

    nano ~/.zshrc
    #para ver la configuración de ZSH

    Por defecto nos selecciona el tema robbyrussell

    6

Instalamos plugins 🔨

    Los paquetes que vamos a instalar son:

        zsh-syntax-highlighting: Si estas escribiendo los comando correctos en la terminal, les pone colores

7

git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting

zsh-autosuggestions: Para obtener sugerencias basadas en tu historial

8

git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions

fzf: Con "ctrl + t" te da un explorador de carpeta, con "ctrl + r" te da un explorador de historial de comandos y con "ctrl + c" salimos

        9

        git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install

        Aceptamos todo lo que nos pida

    Vamos a nuestro archivo de configuración ZSH

    nano ~/.zshrc

    Aquí nos vamos a la parte de abajo del archivo hasta donde veamos plugins (por defecto viene con el plugin de git) y agregamos lo siguiente

    plugins=(
    git
    zsh-syntax-highlighting
    zsh-autosuggestions
    )

    Reiniciamos la consola y listo 😉



Power level 10k 🖌️
Fuente

Fuente regular
10

Fuente nerd
11

    Descargar una fuente con soporte para iconos.
        Mi recomendación es descargar la fuente de https://www.nerdfonts.com/font-downloads
        La fuente que uso es la de JetBrainsMono Nerd Font

    Descomprimir el zip a la carpeta .fonts (~/.fonts o ~/.local/share/fonts) y movernos a ella

    # En caso de no tener la carpeta fonts
    # mkdir ~/.fonts && cd ~/.fonts
    unzip ~/Descargas/[fuente_descargada].zip

    Cambiar la fuente de la terminal, normalmente es click derecho sobre el área de comandos > Preferencias > Apariencia/Perfiles > Fuente
        Aquí elegimos la fuente que hayamos descargado

    12

Powerlevel10k

Nos da muchas opciones de personalización visual como las siguientes

13

    Descargamos powelevel10k

    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k

    Declaramos el tema en el archivo de configuración de zsh

    ZSH_THEME="powerleve10k/powerlevel10k"
    POWERLEVEL10K_MODE="nerdfont-complete"

    14

    Reiniciamos la terminal para que aparezca el configurador o en su defecto teclear p10k configure

    15

    Terminando el instalador tendremos nuestra terminal totalmente personalizada

Colores

    Para cambiar los colores damos click derecho sobre el área de comandos > Preferencias > Apariencia/Perfiles > colores

    16

    Para paletas de colores random puedes visitar coolors.co

    Mis colores principales son:

    Fondo: #302F4D

    Texto: #FFFFFF

    Morado de prompt: #B816B8

    Blanco de prompt: #FFFFFF



Aliases 🕵️‍♂️

Los aliases son una herramienta para crear atajos para los comando que más usamos o para los que más nos equivocamos

    Abrimos la configuración zsh y nos movemos a la parte de abajo

    17

    Aquí en la configuración nos da unos ejemplos

    La sintaxis para agregar alias es:

    alias atajo="comando regular para el atajo"

    Los atajos que tengo configurados son

    alias zshconfig="nano ~/.zshrc"
    alias ohmyzsh="cd ~/.oh-my-zsh"
    alias sl="ls" #por si lo escribo al revés XD



Cambiando el prompt 👩‍💻

Personalmente prefiero que solo me muestre el directorio actual en lugar de todo el path. Queremos pasar de esto

18

A esto, con ayuda de una configuración del tema powerlevel10k

19

    Primero tendremos que abrír el archivo de configuración con nuestro editor favorito, en mi caso utilizaré nano

    nano ~/.p10k.zsh

    Después buscamos el parámetro (en nano podemos usar "Ctrl + w" para buscar)

    POWERLEVEL9K_SHORTEN_STRATEGY=truncate_to_unique

    Sustituimos el valor por defecto

    POWERLEVEL9K_SHORTEN_STRATEGY=truncate_to_last

    Reiniciar la terminal 😃



Gracias por leer!

No olvides compartir esta guía para que mas gente tenga terminales de otro mundo y compartir el conocimiento.
No dudes en mandarme un screenshot de tu terminal por twitter como @__raulmar


Recursos 📔

Instalación de Terminator terminal

Utilidades Terminator terminal

Your terminal can be much more productive

OhMyZSH official repo

ZSH installation guide

Power level 10k & OhMyZSH

OhMyZSH plugins

OhMyZSH website
