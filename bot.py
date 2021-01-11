import itertools
import os
from datetime import datetime

import discord
from discord.ext import commands


def sg(it, func):
    return{k: list(g) for k, g in itertools.groupby(sorted(it, key=func), key=func)}


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
        count_members = guild.member_count
        count_users = len(members[True])
        count_bots = len(members[False])
        status_users = sg_count(members[True], lambda m: m.status)
        status_bots = sg_count(members[False], lambda m: m.status)

        e = discord.Embed(title=f"{guild} の情報", timestamp=datetime.now())
        e.set_thumbnail(url=guild.icon_url)
        e.add_field(
            name='メンバー',
            value=f'{count_members} 人 (:busts_in_silhouette: {count_users} ユーザー、:robot: {count_bots} ボット)',
            inline=False
        )
        e.add_field(
            name='状態',
            value='\n'.join([f':green_circle: オンライン (:busts_in_silhouette: {status_users.get(discord.Status.online,0)} ユーザー、:robot: {status_bots.get(discord.Status.online,0)} ボット)',
                             f':crescent_moon: 退席中 (:busts_in_silhouette: {status_users.get(discord.Status.idle,0)} ユーザー、:robot: {status_bots.get(discord.Status.idle,0)} ボット)',
                             f':no_entry: 取り込み中 (:busts_in_silhouette: {status_users.get(discord.Status.dnd,0)} ユーザー、:robot: {status_bots.get(discord.Status.dnd,0)} ボット)',
                             f':black_circle: オフライン (:busts_in_silhouette: {status_users.get(discord.Status.offline,0)} ユーザー、:robot: {status_bots.get(discord.Status.offline,0)} ボット)']),
            inline=False)
        e.add_field(
            name='チャンネル',
            value='\n'.join([f':speech_balloon: テキスト ({len(guild.text_channels)} チャンネル)',
                             f':sound: ボイス ({len(guild.voice_channels)} チャンネル)']),
            inline=False
        )

        message = await channel.history().get(author=self.bot.user) or await channel.send('初期化中')
        await message.edit(content='', embed=e)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            print(f'{self.bot.user} でログイン完了')
            await self.update()
            print(f'更新完了、ログアウトします')
        finally:
            await self.bot.logout()


if __name__ == '__main__':
    token = os.environ['TOKEN']
    guild_id = int(os.environ['GUILD_ID'])
    channel_id = int(os.environ['CHANNEL_ID'])

    bot = commands.Bot('$', intents=discord.Intents.all())
    bot.add_cog(A(bot, guild_id, channel_id))
    bot.run(token)
