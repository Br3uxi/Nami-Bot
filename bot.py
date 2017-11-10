import asyncio
import configparser
import os
import random
import re
import sys

import discord
import pendulum

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError

__author__ = 'Breuxi'

"""
Markdown Link - [Name](URL)
"""

client = discord.Client()

token = ''

keks_gifs = [
    'https://media.giphy.com/media/RWeGuRoDTtIli/giphy.gif',
    'https://media.giphy.com/media/AMiH2CuUvzk1q/giphy.gif'
]

regexp = re.compile(r'(\bn+?[a, e, o]+?i+?(([n,]+?)|e+?n+?)\b)|(\bn+?[o, u]+?p+?e+?\b)|(n(ö+|ö+?h+?ö+?))|ne+',
                    re.IGNORECASE)

keks_re = re.compile(r'(k+?e+?k+?s+?)', re.IGNORECASE)

if os.path.exists('config.ini'):
    config = configparser.ConfigParser()
    config.read("config.ini")
    if config.has_section("Discord") and config.has_section("Animexx") and config.has_option("Discord", "token") and config.has_option("Animexx", "client_id") and config.has_option("Animexx", "client_secret"):
        token = config.get('Discord', 'token')
        animexx_client_id = config.get('Animexx', 'client_id')
    else:
        print("Config unvollständig! Bitte Discord Token und Animexx Client hinzufügen")
        sys.exit(1)
else:
    print("Die config.ini Datei existiert nicht, bitte erstellen die eine nach dem Beispiel in config.ini.example")
    sys.exit(1)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    for server in client.servers:
        print('- Name: {} | Id: {}'.format(server.name, server.id))
    print('------')
    await client.change_presence(game=discord.Game(name="§help | Karma ist toll!"))


def get_animexx_json(endpoint):
    try:
        oauth_client = OAuth2Session(animexx_client_id, token={'access_token': token, 'token_type': 'Bearer'})
        r = oauth_client.get(endpoint)
    except TokenExpiredError as e:
        print("Token expired")
        config.set('Animexx', 'access_token', token)
        with open('config.cfg', 'wb') as configfile:
            config.write(configfile)
        oauth_client = OAuth2Session(animexx_client_id, token=token)
        r = oauth_client.get(endpoint)
    return r.json()


@client.event
async def on_message(message):
    if message.content.startswith('§help'):
        await client.send_typing(message.channel)
        msg = await client.send_message(message.channel,
                                        'Cringiger Bot - Erschaffen durch Karma und Breuxi\n'
                                        '\n'
                                        '\n'
                                        '**Commands:**\n'
                                        '    §keks => <User>\n'
                                        '\n'
                                        '§help - Diese Seite\n'
                                        'Invite Link: https://discordapp.com/api/oauth2/authorize?client_id=' + client.user.id + '&scope=bot&permissions=1')
        await asyncio.sleep(20)
        try:
            await client.delete_message(message)
        except discord.Forbidden:
            pass
        await client.delete_message(msg)
    elif "(╯°□°）╯︵ ┻━┻" in message.content:
        await client.send_typing(message.channel)
        await client.send_message(message.channel,
                                  'So geht das aber nicht! ┬─┬﻿ ノ( ゜-゜ノ)')
    elif "alice" in message.content.lower():
        await client.send_typing(message.channel)
        em = discord.Embed(colour=0xf7acd7)
        em.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        em.set_image(url="https://media.giphy.com/media/LZH5vHlbUVL8Y/giphy.gif")
        await client.send_message(message.channel, embed=em)
    elif message.content.startswith('§keks'):
        args = message.content.split(' ')
        if args[1] == '=>' and not message.author.id == client.user.id:
            await client.send_typing(message.channel)
            em = discord.Embed(colour=0xf7acd7)
            em.set_author(name=client.user.name, icon_url=client.user.avatar_url)
            em.set_image(url=random.choice(keks_gifs))
            await client.send_message(message.channel,
                                      args[2] + " " + " bekommt einen Keks von " + message.author.mention)
            await client.send_message(message.channel, embed=em)
    elif 'sob' in message.content or 'miep' in message.content.lower() or '😭' in message.content or ':(' in message.content or keks_re.search(
            message.content):
        if message.author.name != client.user.name:
            await client.send_message(message.channel, ':cookie:')

    elif message.content.startswith('§cons'):
        if len(message.content) > 5:
            # Future Parameters for Con Details and Search
            pass
        else:
            con_json = get_animexx_json(
                "https://ws.animexx.de/json/events/event/suche_details?api=2&krits={\"datum_zukunft\":true}")
            if con_json["success"]:
                em = discord.Embed(colour=0xf7acd7)
                em.set_author(name="Conventions", icon_url=client.user.avatar_url)
                i = 0
                await client.send_typing(message.channel)
                for con in con_json["return"]["events"]:
                    if i == 5:
                        break
                    if con["groesse"] >= 5:
                        em.add_field(name=con["name"],
                                     value='{ort} | {von} - {bis} ({verbleibend})'.format(ort=con["ort"],
                                                                                          von=pendulum.parse(
                                                                                              con["datum_von"]).format(
                                                                                              '%A %d %B %Y',
                                                                                              locale='de'),
                                                                                          bis=pendulum.parse(
                                                                                              con["datum_bis"]).format(
                                                                                              '%A %d %B %Y',
                                                                                              locale='de'),
                                                                                          verbleibend=(pendulum.parse(
                                                                                              con[
                                                                                                  "datum_von"]) - pendulum.now(
                                                                                              'Europe/Paris')).in_words(
                                                                                              locale='de')))
                        i += 1
                em.set_footer(text="Powered by Animexx", icon_url="http://animexx.onlinewelten.com/pics/logov2.png")
                await client.send_message(message.channel, embed=em)
            else:
                await client.send_typing(message.channel)
                await client.send_message(message.channel, "Fehler beim Request, bitte als [Github Issue](https://github.com/Breuxi/Nami-Bot/issues) melden")
    elif "gurkenglas" in message.content.lower() and re.compile(r'(öffne)[n,t,]?', re.IGNORECASE).search(
            message.content):
        await client.send_typing(message.channel)
        em = discord.Embed(colour=0xf7acd7)
        em.set_author(name=client.user.name, icon_url=client.user.avatar_url)
        em.set_image(url="https://media.giphy.com/media/l1AsAhTU3dWw3NZL2/giphy.gif")
        await client.send_message(message.channel, embed=em)


client.run(token)
