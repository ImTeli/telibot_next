from nextcord.ext import commands
from config import token
import nextcord
import asyncio
import datetime as dt
import os
import aiohttp
import aiofiles

description = """Telibot, a multi purpose bot."""

nextcord.Intents.members = True
nextcord.Intents.message_content = True
nextcord.Intents.voice_states = True

bot = commands.Bot(command_prefix='>>', description=description, intents=nextcord.Intents.all())


@bot.event
async def on_ready():
    print("#"+"".center(70,"_")+"#")
    print(f"| Logged in as {bot.user.name} with id {bot.user.id}\n| Bot presente nos seguintes servidores:")
    for g in bot.guilds:
        print(f"| {g} id: {g.id}")
        if not os.path.exists(f"guilds/{g.id}"):
            os.makedirs(f"guilds/{g.id}")
            os.makedirs(f"guilds/{g.id}/sounds")
            os.makedirs(f"guilds/{g.id}/log")
    print("#"+"".center(70,"_")+"#")

@bot.command()  # Force commands sync
async def sinc(ctx: commands.Context):
    await ctx.send("Sincronizando comandos \"/\"!")
    await bot.sync_application_commands()


class Audio(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Áudio de entrada na sala!", timeout=30)

        self.mp3 = nextcord.ui.TextInput(
            label="Insira a URL para um arquivo .mp3",
            placeholder="url",
            required=True
        )
        self.add_item(self.mp3)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        filepath = f"guilds/{interaction.guild.id}/sounds/{interaction.user.id}.mp3"
        try:
            if self.mp3.value[-4:] != ".mp3":
                raise Exception("URL não indica um arquivo mp3!")
            async with aiohttp.ClientSession() as session:
                url = self.mp3.value
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise Exception(f"Código de resposta diferente de 200! Código: {resp.status}")
                    elif resp.content_type != "audio/mpeg":
                        raise Exception(f"Arquivo em formato incorreto, formato esperado: audio/mpeg, formato recebido: {resp.content_type}")
                    elif resp.content_length > 3145728:
                        raise Exception(f"Arquivo muito grande, tamanho máximo: 3MB! Tamanho recebido: {resp.content_length/1000000:.2f}MB")
                    else:
                        try:
                            async with aiofiles.open(filepath, 'wb') as file:
                                async for data, _ in resp.content.iter_chunks():
                                    await file.write(data)
                                await interaction.send(
                                    f"{interaction.user.mention} seu arquivo foi salvo com sucesso, entre e saia da sala"
                                    f" para testar!")
                        except Exception as n:
                            await interaction.send(f"Erro durante a gravação do arquivo! Cód. Erro: {n}")

        except aiohttp.InvalidURL:
            await interaction.send("Não foi possível baixar o arquivo de áudio pelo link (URL Inválida).")
        except Exception as n:
            await interaction.send(f"Erro: {n}")


@bot.slash_command()
async def audio(interaction: nextcord.Interaction):
    modal = Audio()
    await interaction.response.send_modal(modal)


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and member.id != 1110960477514772630:
        nome, canal, guilda = member.global_name, member.voice.channel, member.guild
        print(f"{nome} entrou no canal de voz {canal} no servidor {guilda} em {dt.datetime.now()}.")

        if os.path.isfile(f"guilds/{member.guild.id}/sounds/{member.id}.mp3"):
            try:
                source = await nextcord.FFmpegOpusAudio.from_probe(f"guilds/{member.guild.id}/sounds/{member.id}.mp3",
                                                                   method="fallback")
                vc = await member.voice.channel.connect()
                vc.play(source)
            except:
                pass

        while True:
            await asyncio.sleep(0.001)

            try:
                if not vc.is_playing():
                    await vc.disconnect()
                    break
            except UnboundLocalError:
                pass

    elif (before.channel is not None and after.channel is None) and member.id != 1110960477514772630:
        nome, canal, guilda = member.global_name, before.channel, member.guild
        print(f"{nome} saiu do canal de voz {canal} no servidor {guilda} em {dt.datetime.now()}.")


bot.run(token)
