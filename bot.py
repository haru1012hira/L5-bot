import os
import random

import discord
from discord.ext import commands
from discord import app_commands


TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


def get_channel_members(channel):
    """そのテキストチャンネルを見られるメンバーを取得"""
    members = []

    for member in channel.guild.members:
        if member.bot:
            continue

        permissions = channel.permissions_for(member)

        if permissions.view_channel:
            members.append(member)

    return members


def split_members(members, team_size):
    """メンバーを指定人数ずつランダムに分ける"""
    members = list(members)
    random.shuffle(members)

    return [
        members[i:i + team_size]
        for i in range(0, len(members), team_size)
    ]


@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")


@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("スラッシュコマンドを同期しました")


@bot.tree.command(
    name="team",
    description="指定したチーム数にランダム分けします"
)
@app_commands.describe(
    number="作りたいチーム数"
)
async def team(
    interaction: discord.Interaction,
    number: int
):
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "❌ このコマンドはテキストチャンネルで使用してください。",
            ephemeral=True
        )
        return

    if number < 1:
        await interaction.response.send_message(
            "❌ チーム数は1以上にしてください。",
            ephemeral=True
        )
        return

    members = get_channel_members(interaction.channel)

    if len(members) == 0:
        await interaction.response.send_message(
            "❌ 対象となるメンバーがいません。",
            ephemeral=True
        )
        return

    if len(members) % number != 0:
        await interaction.response.send_message(
            f"❌ {len(members)}人を{number}チームに均等に分けられません。",
            ephemeral=True
        )
        return

    team_size = len(members) // number
    teams = split_members(members, team_size)

    message = f"🎲 **{number}チームにランダム分け！**\n\n"

    for i, team_members in enumerate(teams, 1):
        message += f"**Team {i}**\n"

        for member in team_members:
            message += f"{member.mention}\n"

        message += "\n"

    await interaction.response.send_message(message)


@bot.tree.command(
    name="teammember",
    description="指定した人数ごとにランダム分けします"
)
@app_commands.describe(
    number="1チームあたりの人数"
)
async def teammember(
    interaction: discord.Interaction,
    number: int
):
    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "❌ このコマンドはテキストチャンネルで使用してください。",
            ephemeral=True
        )
        return

    if number < 1:
        await interaction.response.send_message(
            "❌ 1チームの人数は1以上にしてください。",
            ephemeral=True
        )
        return

    members = get_channel_members(interaction.channel)

    if len(members) == 0:
        await interaction.response.send_message(
            "❌ 対象となるメンバーがいません。",
            ephemeral=True
        )
        return

    if len(members) % number != 0:
        await interaction.response.send_message(
            f"❌ {len(members)}人では、1チーム{number}人に均等に分けられません。",
            ephemeral=True
        )
        return

    teams = split_members(members, number)

    message = f"🎲 **1チーム{number}人でランダム分け！**\n\n"

    for i, team_members in enumerate(teams, 1):
        message += f"**Team {i}**\n"

        for member in team_members:
            message += f"{member.mention}\n"

        message += "\n"

    await interaction.response.send_message(message)


bot.run(TOKEN)
