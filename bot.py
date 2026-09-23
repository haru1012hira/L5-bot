import os
import random

import discord
from discord.ext import commands
from discord import app_commands


TOKEN = os.environ["DISCORD_TOKEN"]


# Discordの権限設定
intents = discord.Intents.default()
intents.members = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ========================================
# メンバー取得
# ========================================

async def get_channel_members(channel):
    """
    テキストチャンネル：
        そのチャンネルを見ることができるメンバー

    スレッド：
        そのスレッドに参加しているメンバー

    Botは除外する
    """

    members = []

    # ------------------------------------
    # 通常のテキストチャンネル
    # ------------------------------------

    if isinstance(channel, discord.TextChannel):

        for member in channel.guild.members:

            # Botを除外
            if member.bot:
                continue

            # チャンネルを見る権限があるか確認
            permissions = channel.permissions_for(member)

            if permissions.view_channel:
                members.append(member)

    # ------------------------------------
    # スレッド
    # ------------------------------------

    elif isinstance(channel, discord.Thread):

        try:
            # Discordからスレッド参加者を取得
            thread_members = await channel.fetch_members()

        except discord.HTTPException:
            return []

        for thread_member in thread_members:

            # ThreadMemberからGuild Memberを取得
            member = channel.guild.get_member(thread_member.id)

            if member is None:
                try:
                    member = await channel.guild.fetch_member(
                        thread_member.id
                    )
                except discord.HTTPException:
                    continue

            # Botを除外
            if member.bot:
                continue

            members.append(member)

    return members


# ========================================
# ランダムチーム分け
# ========================================

def split_members(members, team_size):
    """
    メンバーをランダムにシャッフルして
    指定人数ずつチームに分ける
    """

    members = list(members)

    random.shuffle(members)

    return [
        members[i:i + team_size]
        for i in range(0, len(members), team_size)
    ]


# ========================================
# Tag名
# ========================================

def tag_name(number):
    """
    1 → A
    2 → B
    3 → C
    ...
    26 → Z
    27 → AA
    28 → AB
    """

    result = ""

    while number > 0:
        number -= 1
        result = chr(65 + (number % 26)) + result
        number //= 26

    return result


# ========================================
# Bot起動
# ========================================

@bot.event
async def on_ready():

    print(f"ログインしました: {bot.user}")


# ========================================
# スラッシュコマンド同期
# ========================================

@bot.event
async def setup_hook():

    await bot.tree.sync()

    print("スラッシュコマンドを同期しました")


# ========================================
# /team
# ========================================

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

    # ------------------------------------
    # 使用できる場所を確認
    # ------------------------------------

    if not isinstance(
        interaction.channel,
        (discord.TextChannel, discord.Thread)
    ):

        await interaction.response.send_message(
            "❌ このコマンドはテキストチャンネルまたはスレッドで使用してください。",
            ephemeral=True
        )

        return


    # ------------------------------------
    # チーム数チェック
    # ------------------------------------

    if number < 1:

        await interaction.response.send_message(
            "❌ チーム数は1以上にしてください。",
            ephemeral=True
        )

        return


    # ------------------------------------
    # メンバー取得
    # ------------------------------------

    members = await get_channel_members(
        interaction.channel
    )


    # ------------------------------------
    # メンバーがいない
    # ------------------------------------

    if len(members) == 0:

        await interaction.response.send_message(
            "❌ 対象となるメンバーがいません。",
            ephemeral=True
        )

        return


    # ------------------------------------
    # 均等に分けられるか確認
    # ------------------------------------

    if len(members) % number != 0:

        await interaction.response.send_message(
            f"❌ {len(members)}人を{number}チームに均等に分けられません。",
            ephemeral=True
        )

        return


    # ------------------------------------
    # チーム作成
    # ------------------------------------

    team_size = len(members) // number

    teams = split_members(
        members,
        team_size
    )


    # ------------------------------------
    # 結果作成
    # ------------------------------------

    message = (
        f"🎲 **{number}チームにランダム分け！**\n\n"
    )


    for i, team_members in enumerate(
        teams,
        1
    ):

        message += (
            f"**Tag {tag_name(i)}**\n"
        )

        for member in team_members:

            message += (
                f"{member.mention}\n"
            )

        message += "\n"


    # ------------------------------------
    # Discordに送信
    # ------------------------------------

    await interaction.response.send_message(
        message
    )


# ========================================
# /teammember
# ========================================

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

    # ------------------------------------
    # 使用できる場所を確認
    # ------------------------------------

    if not isinstance(
        interaction.channel,
        (discord.TextChannel, discord.Thread)
    ):

        await interaction.response.send_message(
            "❌ このコマンドはテキストチャンネルまたはスレッドで使用してください。",
            ephemeral=True
        )

        return


    # ------------------------------------
    # 人数チェック
    # ------------------------------------

    if number < 1:

        await interaction.response.send_message(
            "❌ 1チームの人数は1以上にしてください。",
            ephemeral=True
        )

        return


    # ------------------------------------
    # メンバー取得
    # ------------------------------------

    members = await get_channel_members(
        interaction.channel
    )


    # ------------------------------------
    # メンバーがいない
    # ------------------------------------

    if len(members) == 0:

        await interaction.response.send_message(
            "❌ 対象となるメンバーがいません。",
            ephemeral=True
        )

        return


    # ------------------------------------
    # 均等に分けられるか確認
    # ------------------------------------

    if len(members) % number != 0:

        await interaction.response.send_message(
            f"❌ {len(members)}人では、1チーム{number}人に均等に分けられません。",
            ephemeral=True
        )

        return


    # ------------------------------------
    # チーム作成
    # ------------------------------------

    teams = split_members(
        members,
        number
    )


    # ------------------------------------
    # 結果作成
    # ------------------------------------

    message = (
        f"🎲 **1チーム{number}人でランダム分け！**\n\n"
    )


    for i, team_members in enumerate(
        teams,
        1
    ):

        message += (
            f"**Tag {tag_name(i)}**\n"
        )

        for member in team_members:

            message += (
                f"{member.mention}\n"
            )

        message += "\n"


    # ------------------------------------
    # Discordに送信
    # ------------------------------------

    await interaction.response.send_message(
        message
    )


# ========================================
# Bot起動
# ========================================

bot.run(TOKEN)