import discord
import asyncio
import json
import commands as bot_commands

client = discord.Client()

commands = {}
aliases = {}


def generate_help(*args):
    return ''.join(commands[command].get_help() for command in commands)


class Command:
    def __init__(self, name: str, command_aliases: list, description: str):
        self._name = name
        self._aliases = command_aliases
        self._description = description

        if command != 'help':
            self._function = getattr(bot_commands, self.get_name())
        else:
            self._function = generate_help

    def get_name(self):
        return self._name

    def get_aliases(self):
        return self._aliases

    def get_description(self):
        return self._description

    def get_help(self):
        return "\n\n**%s** - %s\n__Aliases:__ *%s*" % (self.get_name(), self.get_description(),
                                                       '*, *'.join(alias for alias in self.get_aliases()))

    def run(self, *args) -> dict:
        return self._function(*args)


def register_command(command: Command):
    if command.get_name() in commands:
        raise ValueError("A command with this name is already registered.")

    commands[command.get_name()] = command

    for alias in command.get_aliases():
        aliases[alias] = command.get_name()


with open('settings.json', 'r') as f:
    settings = json.loads(f.read())
    TOKEN = settings['token']
    PREFIX = settings['prefix']

    for command in settings['commands']:
        c = settings['commands'][command]
        register_command(Command(command, c['aliases'], c['description']))


def get_settings():
    return settings


def get_command_by_name(name: str) -> Command:
    name = name.split(' ')[0]
    if name in commands:
        return commands[name]
    elif name in aliases:
        return commands[aliases[name]]
    else:
        return None


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.content.startswith(PREFIX):
        command_input = message.content.split(PREFIX)[1]
        command = get_command_by_name(command_input)
        arguments = command_input.split(' ')[1:]

        if command:
            return_message = command.run(arguments)
            print(*return_message)
            await client.send_message(message.channel,
                                      content=return_message['message'] if 'message' in return_message else None,
                                      embed=return_message['embed'] if 'embed' in return_message else None)


if __name__ == '__main__':
    client.run(TOKEN)
