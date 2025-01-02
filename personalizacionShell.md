https://dev.to/raulmar/personaliza-tu-terminal-de-0-a-pro-3map
## 1. Cambiar la shell por defecto (BASH) por ZSH
ZSH es una mejor alternativa al shell por defecto que es BASH, principalmente por sus addons que nos facilitan todo, desde plugins hasta un framework para temas.
1. Instalamos ZSH
```bash
sudo apt install zsh
```

2. Seleccionamos ZSH como shell por defecto
```bash
chsh -s $(which zsh)
```
Otra alternativa es:
```bash
chsh -s `which zsh`
```
 
 3. Reiniciamos la consola

4. Revisamos que estemos usando ZSH, si nos sale un error hay que verficar la instalación
```bash
 echo $SHELL
```
--> Nos debe responder con `/usr/bin/zsh`

5. Si nos sale un menú seleccionamos (2) para desktop y (0) para conexiones SSH

## 2. Instalar GIT
Para clonar repositorios desde la nube.
Además de ser una excelente herramienta para desarrollo también la usaremos para que OhMyZSH se pueda instalar correctamente
1. Instalamos los paquetes de git
```bash
sudo apt-get install git
```

2. Comprobamos la instalación
```bash
git --version
```

## 3. Instalar Oh My ZSH
Oh My ZSH es un administrador de configuración para ZSH el cual nos hará la vida más fácil.
Este framework creado por la comunidad nos ayuda a configurar nuestro ZSH.
No confundir ZSH y OhMyZSH, OhMyZSH actúa sobre el archivo de configuración de ZSH (.zshrc)
1. Instalamos Oh My ZSH
```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```
Oh My ZSH nos modifica el archivo `.zshrc` y nos crea la carpeta `.oh-my-zsh` donde encontraremos los plugins, temas, plantillas etc.

Podemos hacer `nano ~/.zshrc` para ver la configuración de ZSH. Por defecto nos selecciona el tema de `robbyrussell`

## 4. Instalar algunos plugins sobre Oh My ZSH
 Los paquetes que vamos a instalar son:
`zsh-syntax-highlighting`: Si estas escribiendo los comando correctos en la terminal, les pone colores:
```bash
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
```

`zsh-autosuggestions`: Para obtener sugerencias basadas en tu historial:
```bash
git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
```

`fzf`: Con `Ctrl + T` te da un explorador de carpeta, con `Ctrl + R` te da un explorador de historial de comandos y con `Ctrl + C` salimos:
```bash
git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf && ~/.fzf/install
```
Aceptamos todo lo que nos pida

Ahora vamos a nuestro archivo de configuración ZSH con `nano ~/.zshrc`.
    Aquí nos vamos a la parte de abajo del archivo hasta donde veamos plugins (por defecto viene con el plugin de git) y agregamos lo siguiente:
```
plugins=(
git
zsh-syntax-highlighting
zsh-autosuggestions
)
```
Reiniciamos la consola y listo.

## 5.  Instalar el tema `powerlevel10k` con Oh My ZSH
Permite una gran cantidad de combinaciones gracias a su configuration wizard.
Si queremos cambiar la fuente:
1. Descargar una fuente con soporte para iconos.
Mi recomendación es descargar la fuente de https://www.nerdfonts.com/font-downloads
La fuente que uso es la de `JetBrainsMono Nerd Font`.

2. Descomprimir el zip a la carpeta `.fonts` (`~/.fonts` o `~/.local/share/fonts`) y movernos a ella.
En caso de no tener la carpeta fonts, la creamos:
```bash
mkdir ~/.fonts && cd ~/.fonts
unzip ~/Descargas/[fuente_descargada].zip
```

3. Cambiar la fuente de la terminal, normalmente es click derecho sobre el área de comandos > Preferencias > Apariencia/Perfiles > Fuente
Aquí elegimos la fuente que hayamos descargado

Ahora, vamos a instalar `powerlevel10k`:
1. Descargamos powelevel10k
```bash
git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
```

2. Declaramos el tema en el archivo de configuración de zsh (`nano ~/.zshrc`):
```bash
ZSH_THEME="powerlevel10k/powerlevel10k"
POWERLEVEL10K_MODE="nerdfont-complete"
```

3. Reiniciamos la terminal para que aparezca el configurador o en su defecto teclear p10k configure.

4. Configuramos la terminal a nuestro gusto y listo

## 6. Agregar algunos alias
Los aliases son una herramienta para crear atajos para los comando que más usamos o para los que más nos equivocamos:
1. Abrimos la configuración zsh (`nano ~/.zshrc`) y nos movemos a la parte de abajo
Aquí en la configuración nos da unos ejemplos. La sintaxis para agregar alias es: `alias atajo="comando regular para el atajo"`

Los atajos que tengo configurados son
```
alias zshconfig="nano ~/.zshrc"
alias ohmyzsh="cd ~/.oh-my-zsh"
alias sl="ls" # Por si lo sueles escribes al revés por ejemplo
```

## 7. Cambiar el prompt por defecto de nuestra terminal
Si prefieres por ejemplo que solo me muestre el directorio actual en lugar de todo el path en el que estás:
1. Abrimos el archivo de configuración con nuestro editor favorito, en mi caso utilizaré `nano`
```bash
    nano ~/.p10k.zsh
```

2. Después buscamos el parámetro (en nano podemos usar "Ctrl + W" o "Ctrl + F" para buscar)
```
POWERLEVEL9K_SHORTEN_STRATEGY=truncate_to_unique
```

3. Sustituimos el valor por defecto
```
POWERLEVEL9K_SHORTEN_STRATEGY=truncate_to_last
```

4. Reiniciamos la terminal para que se apliquen los cambios y listo

