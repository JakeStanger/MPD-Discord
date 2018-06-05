# MPD Discord
A discord bot to control and view your MPD server, as well as stream output through voice.

# Setup
Install the requirements in `requirements.txt`.

All features require an MPD server.

For some features, you will need to configure a web server (or two)
with a directory containing your music library, and another
where album art will be placed.

Change the settings in `settings.json` to match your setup and requirements.

Launch the bot from `main.py`.

## Settings
### Token
The token for the Discord bot account you wish to run it through.

### Prefix
The command prefix i.e what a message must start with for the bot to interpret it as a command.

### MPD
#### Server
The MPD server host address.

#### Port
The MPD server port number.


#### Timeout
The server connection timeout. In most cases you won't need to ever touch this.
In some rare circumstances, increasing this may help connection issues.

#### FIFO
The full path to MPD's FIFO file. This is required to stream audio through discord.
You must configure MPD itself to output to a FIFO file.

#### Art Grabber
##### Save Directory
The location in which album art should be saved to.
If you want this to actually do anything, this should be a web server directory
since Discord can only fetch images via HTTP(S).

##### Library Directory
The location of your music library. Used to search for album art
in album directories. 

### Download Servers
#### Art URL
The URL to where album art can be fetched from.
Used to display album art along-side songs in embeds.

#### Music URL
The URL to where music files can be fetched from.
Used for the download button in song embeds.

## Commands
To add new commands or configure existing commands to the bot, all you have to do
is add an entry to `settings.json`.

The parent key is the name of the command. This is both used
in order to use the command from Discord, and internally - 
**a function of the same name must exist in `commands.py`**.

The aliases are a list of alternate words which can be used
in order to run the command.

The description is displayed when the `help` command is used.