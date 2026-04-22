# 1 Introducción

La tarea consiste en el desarrollo de un sistema de correo electrónico que integra un servidor y cliente SMTP y un servidor POP3 junto con protocolos y capas de seguridad y notificación mediante xmpp.
El servidor SMTP será responsable de enviar y recibir correos, implementado en Python con la biblioteca Twisted, incorporando comunicación segura mediante TLS y validación de dominios para aceptar o rechazar mensajes, además de soportar archivos adjuntos a través del estándar MIME.
Por otro lado, el cliente permitirá a los usuarios gestionar el envío de correos, incluyendo la lectura de destinatarios desde archivos CSV.
El servidor POP3 actuará como un buzón recibiendo los correos enviados por el SMTP. Los usuarios puedan autenticarse y consultar, descargar y eliminar correos, todo bajo una capa de cifrado segura.

# 2 Ambiente de desarrollo

- SO: Ubuntu
- IDE: PyCharm
- Bibliotecas: Twisted
- IA: ChatGPT (GPT-5.3)
- VC: Git/GitHub

# 3 Estructura de datos usadas y funciones

## `userservices.py` – Funciones de usuarios

- **`loadUsers()`:** lee el archivo `.env` (formato `usuario=contraseña` por línea) y retorna un diccionario `{username: password}`
- **Clase `UserValidator`: verifica credenciales de tipo `IUsernamePassword`
  - `requestAvatarId(credentials)`: extrae el nombre de usuario (parte local del email) y la contraseña y si coinciden con los datos cargados retorna el `username`, si no coinciden falla con `UnauthorizedLogin`

## `pop3server.py`

- **Clase `MailRealm`** 
  - `requestAvatar(avatarId, mind, *interfaces)`: crea un buzón de correos para el usuario autenticado
- **Clase `Mailbox`:** gestiona el buzón de un usuario
  - `_load()`: lista y ordena los archivos `.eml` en el directorio del usuario
  - `listMessages(index)`: retorna los mensajes listados con sus respectivos tamaños (bytes)
  - `getMessage(index)`: abre y retorna un mensaje
  - `getMessageCount()`: cantidad de mensajes
  - `deleteMessage(index)`: marca un mensaje para borrar
  - `undelete(index)`: desmarca un mensaje que estaba para borrar
  - `sync()`: elimina físicamente del servidor los mensajes marcados
  - `getUidl(index)`: retorna el nombre base del archivo como identificador único
- **Clase `PortalFactory`**
  - `buildProtocol(addr)`: crea un protocolo `pop3.POP3` y le asigna el portal de autenticación

## `smtpserver.py`
- **Clase `PostOffice`**
  - `receivedHeader()`: genera la cabecera `Received:` con el `helo` y la IP del remitente
  - `validateFrom()`: valida el origen
  - `validateTo(user)`: verifica que el dominio del destinatario esté en la lista de permitidos y crea el directorio del usuario si no existe
- **Clase `Message`**
  - `lineReceived(strLine)`: acumula las líneas del mensaje
  - `eomReceived()`: guarda el mensaje en un archivo con nombre `email-<timestamp>.eml` dentro del directorio del usuario
- **Clase `ProtocolFactory`**
  - `buildProtocol(addr)`: crea un protocolo `SMTP` para que lo use la instacia `PostOffice`
- **`loadAllowedDomains(domainsCSV)`:** lee un CSV con columna `Domain` y retorna la lista de dominios permitidos

## `smtpclient.py`
- **`personalizeMessage(recipient, messageFile)`:** lee una plantilla de mensaje y reemplaza `{name}` con el nombre del destinatario
- **`sendEmail(smtpServer, csvEmailsFile, messageFile)`**  
  - Abre el CSV (columnas esperadas: `Name`, `Email`)
  - Conecta al servidor SMTP en el puerto `2525`
  - Para cada destinatario crea un correo y asigna remitente, destinatario, asunto y contenido personalizado
  - Envía el mensaje con `server.send_message()`. Si falla, imprime un rechazo.

# 4 Instrucciones para ejecutar el programa

## SMTP Server

```bash
python3 smtpserver.py -d <domains> -s <mail-storage> -p <port>
```

- **`<domains>`:** debe ser un CSV con mínimo la columna `Domain`
- **`<mail-storage>`:** es la ruta donde se guardaran los mensajes
- **`<port>`:** el puerto a usar por el servidor SMTP

## SMTP Client

```bash
python3 smtpclient.py -h <mail-server> -c <csv-file> -m <message-file>
```

- **`<mail-server>`:** ddirección IP del servidor SMTP
- **`<csv-file>`:** el CSV con los destinatarios, debe tener como mínimo la columna `Name` y `Email`
- **`<message-file>`:** el `.txt` con el contenido del correo

## POP3 Server

```bash
python pop3server.py -s <mail-storage> -p <port>
```

- **`<mail-storage>`:** es la ruta donde el servidor SMTP guarda los mensajes
- **`<port>`:** el puerto a usar por el servidor POP3

# 5 Actividades realizadas por estudiante

```bash
commit 0f04974b86c1e71d94551da216e530260fbdcae5
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Tue Apr 21 22:06:25 2026 -0600

    implement loading of allowed domains from a CSV
    
    - Implement CSV parsing to load allowed domains
    - Validate recipient domains against loaded list in `validateTo()`
    - Save messages with `.eml` extension (previously `.txt`)

commit 378c328f343753e5970b089afd30f57cc2e35f27
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Tue Apr 21 21:55:46 2026 -0600

    implement POP3 server
    
    - Implement `deleted` set to track messages marked for deletion
    - Implement `deleteMessage()` and `undelete()` methods (DELE / RSET)
    - Implement `sync()` to physically remove deleted files on QUIT
    - Implement `getUidl()` to obtain unique identifier per message
    - Works on email clients like Thunderbird

commit 4feb8934c93a8dd827a96aafa60ebe22080c1107
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Tue Apr 21 13:20:22 2026 -0600

    implement user authentication using .env credentials
    
    Features:
    - Loads credentials from `.env` file (username=password format)
    - Implemented `ICredentialsChecker` to validate USER/PASS commands

commit 159077299c75c97f07b015f9ce07763a06664580
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Tue Apr 21 00:52:51 2026 -0600

    implement email saving to local mailbox storage
    
    Current status of the server:
    - Parse CLI arguments (Allowed Domains, Email Storage, Port)
    - Emails are stored per recipient mailbox

commit 03ad3ad65e15282eb86f3fa4650c520de80c1976
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Mon Apr 20 22:20:22 2026 -0600

    add initial SMTP server implementation
    
    Current status of the server:
    - Implements mail and internet modules from Twisted library

commit cef5ad7a49247f13c71a5c9660421a8bc8523339
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Mon Apr 20 19:46:40 2026 -0600

    add SMTP connection and email delivery
    
    Current status of the client:
    - Implements email sending via SMTP using smtplib
    - Builds MIME messages (text-only)

commit ee77cbc492f729d4b6a2d462fa280bcec59eb522
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Mon Apr 20 12:19:33 2026 -0600

    add initial SMTP client implementation (not sending)
    
    Current status of the client:
    - Parse CLI arguments (SMTP server, CSV file, message file)
    - Read and process recipients list from the CSV file
    - Support basic message templating using `{variable_name}` placeholders
    - Email sending logic still pending

commit 016edf879caa3e569130001bc232cd83b59ca8d6
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Mon Apr 20 09:54:04 2026 -0600

    ignore PGP signature files

commit c9ed663e441179eeb5b56457e5e8d185000d2dad
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Mon Apr 20 09:48:37 2026 -0600

    add project kick-off documentation

commit 119105f03f3835814e7420ed38eff8e5254cd998
Author: Sebas Quesada <167464285+Sebco27@users.noreply.github.com>
Date:   Fri Apr 17 20:54:45 2026 -0600

    add README and git config files
```

# 6 Autoevaluación

El programa al final no se pudo conectar con el dominio adquirido ya que por falta de tiempo quedó pendiente la configuración de los puertos de la computadora para poder recibir correos desde otra computadora.
Las notificaciones tampoco fueron implementadas por falta de tiempo.

| Nota |             Rubro              |
|:----:|:------------------------------:|
|  5   | Aprendizaje del protocolo SMTP |
|  4   | Aprendizaje del protocolo pop3 |
|  0   | Aprendizaje del protocolo xmpp |
|  3   | Aprendizaje de la capa SSL/TLS |
|  1   |     Organización de Tiempo     |

# 7 Lecciones Aprendidas

Administrar bien el tiempo es fundamental. La tarea estaba bastante accesible para realizarse en un fin de semana y las bibliotecas de python ayudan a que sea rápido avanzar.

# 8 Bibliografía

- [Twisted documentation](https://docs.twisted.org/en/stable/)
- [Cómo utilizar argparse](https://youtu.be/tirLko5urBo)
