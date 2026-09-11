import os
import random

import discord
from discord.ext import commands
from discord import app_commands


TOKEN = os.environ["DISCORD_TOKEN"]

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


def get_members(channel):
    """そのテキストチャンネルを見られる人を取得（Bot除外）"""
    members = [
        member
        for member in channel.members
        if not member.bot
    ]
    return members


def create_teams(members, team_count):
    """人数を指定したチーム数に均等分配"""
    if team_count < 1:
        return None

    if len(members) % team_count != 0:
        return None

    random.shuffle(members)

    team_size = len(members) // team_count

    return [
        members[i * team_size:(i + 1) * team_size]
        for i in range(team_count)
    ]


@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")


@bot.event
async def setup_hook():
    await bot.tree.sync()
    print("スラッシュコマンドを同期しました")


@bot.tree.command(name="team", description="指定したチーム数にランダム分けします")
@app_commands.describe(number="作りたいチーム数")
async def team(interaction: discord.Interaction, number: int):

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "このコマンドはテキストチャンネルで使用してください。",
            ephemeral=True
        )
        return

    members = get_members(interaction.channel)

    if number < 1:
        await interaction.response.send_message(
            "チーム数は1以上にしてください。",
            ephemeral=True
        )
        return

    if len(members) == 0:
        await interaction.response.send_message(
            "参加メンバーがいません。",
            ephemeral=True
        )
        return

    if len(members) % number != 0:
        await interaction.response.send_message(
            f"❌ {len(members)}人を{number}チームに均等に分けられません。",
            ephemeral=True
        )
        return

    teams = create_teams(members, number)

    text = f"🎲 **{number}チームにランダム分け！**\n\n"

    for i, team_members in enumerate(teams, 1):
        text += f"**Team {i}**\n"
        text += "\n".join(member.mention for member in team_members)
        text += "\n\n"

    await interaction.response.send_message(text)


@bot.tree.command(
    name="teammember",
    description="指定した人数ごとにランダム分けします"
)
@app_commands.describe(number="1チームあたりの人数")
async def teammember(interaction: discord.Interaction, number: int):

    if not isinstance(interaction.channel, discord.TextChannel):
        await interaction.response.send_message(
            "このコマンドはテキストチャンネルで使用してください。",
            ephemeral=True
        )
        return

    members = get_members(interaction.channel)

    if number < 1:
        await interaction.response.send_message(
            "1チームの人数は1以上にしてください。",
            ephemeral=True
        )
        return

    if len(members) == 0:
        await interaction.response.send_message(
            "参加メンバーがいません。",
            ephemeral=True
        )
        return

    if len(members) % number != 0:
        await interaction.response.send_message(
            f"❌ {len(members)}人では、1チーム{number}人に均等に分けられません。",
            ephemeral=True
        )
        return

    team_count = len(members) // number
    teams = create_teams(members, team_count)

    text = f"🎲 **1チーム{number}人でランダム分け！**\n\n"

    for i, team_members in enumerate(teams, 1):
        text += f"**Team {i}**\n"
        text += "\n".join(member.mention for member in team_members)
        text += "\n\n"

    await interaction.response.send_message(text)


bot.run(TOKEN)
