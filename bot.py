import os
from datetime import datetime
from itertools import groupby

import discord
from discord.ext import commands


def sg(it, func):
    return{k: list(g) for k, g in groupby(sorted(it, key=func), key=func)}


def sg_count(it, func):
    return {k: len(l) for k, l in sg(it, func).items()}


class A(commands.Cog):

    def __init__(self, bot, guild_id, channel_id):
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id

    async def update(self):
        guild = self.bot.get_guild(self.guild_id)
        channel = self.bot.get_channel(self.channel_id)
        print(f'{guild} の情報を {channel} に送信します')

        members = sg(guild.members, lambda m: not m.bot)
        users = members[True]
        bots = members[False]
        status_users = sg_count(users, lambda m: m.status)
        status_bots = sg_count(bots, lambda m: m.status)

        e = discord.Embed(title=f"{guild} の情報", timestamp=datetime.now())
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(
            name='メンバー',
            value='\n'.join([f'{guild.member_count} 人',
                             f'├ :busts_in_silhouette: {len(users)} ユーザー',
                             f'└ :robot: {len(bots)} ボット']),
        )
        e.add_field(
            name='状態',
            value='\n'.join([':green_circle: オンライン',
                             f'├ :busts_in_silhouette: {status_users.get(discord.Status.online,0)} ユーザー',
                             f'└ :robot: {status_bots.get(discord.Status.online,0)} ボット',
                             ':crescent_moon: 退席中',
                             f'├ :busts_in_silhouette: {status_users.get(discord.Status.idle,0)} ユーザー',
                             f'└ :robot: {status_bots.get(discord.Status.idle,0)} ボット',
                             ':no_entry: 取り込み中',
                             f'├ :busts_in_silhouette: {status_users.get(discord.Status.dnd,0)} ユーザー',
                             f'└ :robot: {status_bots.get(discord.Status.dnd,0)} ボット',
                             ':white_circle: オフライン',
                             f'├ :busts_in_silhouette: {status_users.get(discord.Status.offline,0)} ユーザー',
                             f'└ :robot: {status_bots.get(discord.Status.offline,0)} ボット']),
        )
        e.add_field(
            name='チャンネル',
            value='\n'.join([':speech_balloon: テキスト',
                             f'└ {len(guild.text_channels)} チャンネル',
                             ':sound: ボイス',
                             f'└ {len(guild.voice_channels)} チャンネル']),
        )

        message = await channel.history().get(author=self.bot.user) or await channel.send('初期化中')
        await message.edit(content='', embed=e)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            print(f'{self.bot.user} でログイン完了')
            await self.update()
            print('更新完了、ログアウトします')
        finally:
            await self.bot.logout()


if __name__ == '__main__':
    token = os.environ['TOKEN']
    guild_id = int(os.environ['GUILD_ID'])
    channel_id = int(os.environ['CHANNEL_ID'])

    bot = commands.Bot('$', intents=discord.Intents.all())
    bot.add_cog(A(bot, guild_id, channel_id))
    bot.run(token)
