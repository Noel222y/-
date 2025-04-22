import os
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv  # ← เพิ่มตรงนี้

from myserver import server_on
import random

load_dotenv()  # ← โหลด .env ตรงนี้

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

# (คำสั่งทั้งหมดตามที่คุณมีอยู่)


 # ห้ามโชว์ token จริงนะครับ!

user_tickets = {}

def get_balance(user_id):
    return user_tickets.get(user_id, 100)

def update_balance(user_id, amount):
    user_tickets[user_id] = get_balance(user_id) + amount

@bot.event
async def on_ready():
    print(f"✅ Bot Online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"📡 Synced {len(synced)} command(s) with Discord")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# ใช้ app_commands เพื่อสร้าง Slash Command อย่างถูกต้อง
@bot.tree.command(name="ตกปลา", description="ใช้สำหรับตกปลา")
@app_commands.describe(bait="เลือกเหยื่อที่ใช้ตกปลา")
@app_commands.choices(bait=[
    app_commands.Choice(name="ไม่ใช้เหยื่อ", value="ไม่ใช้เหยื่อ"),
    app_commands.Choice(name="ไส้เดือน", value="ไส้เดือน"),
    app_commands.Choice(name="เหยื่อสูตรพี่ศักดิ์", value="เหยื่อสูตรพี่ศักดิ์"),
    app_commands.Choice(name="เหยื่อปลอม", value="เหยื่อปลอม"),
 
])
async def fish(interaction: discord.Interaction, bait: app_commands.Choice[str]):
    bait_value = bait.value

    if bait_value == "ไม่ใช้เหยื่อ":
        fish_types = ["ปลาเข็ง", "ปลาตะเพียน"]
        weights = [0.5, 0.5]
    elif bait_value == "ไส้เดือน":
        fish_types = ["ปลาเข็ง", "ปลาตะเพียน", "ปลานิล", "ปลาดุก"]
        weights = [0.1, 0.1, 0.4, 0.4]
    elif bait_value == "เหยื่อสูตรพี่ศักดิ์":
        fish_types = ["ปลานิล", "ปลาดุก", "ปลาช่อน"]
        weights = [0.1, 0.1, 0.8]
    elif bait_value == "เหยื่อปลอม":
        fish_types = ["ปลาเข็ง", "ปลาตะเพียน", "ปลานิล ", "ปลาดุก", "ปลาช่อน"]
        weights = [0.3, 0.3, 0.1, 0.1, 0.2]
     
   

    caught_fish = random.choices(fish_types, weights=weights, k=1)[0]
    await interaction.response.send_message(
        f"🎣 คุณใช้เหยื่อ **{bait_value}** และได้ **{caught_fish}** 🐟! ยินดีด้วย!"
    )

@bot.tree.command(name="เดิมพันลูกเต๋า", description="ทายหน้าเต๋าให้ถูก")
@app_commands.describe(bet="จำนวนเงินที่เดิมพัน", guess="เลขที่ทาย (1-6)")
async def dice_game(interaction: discord.Interaction, bet: int, guess: int):
    user_id = interaction.user.id
    balance = get_balance(user_id)

    if bet <= 4:
        await interaction.response.send_message("⚠️ ต้องเดิมพันมากกว่า 4")
        return

    if guess not in range(1, 7):
        await interaction.response.send_message("🎲 ต้องทายเลขระหว่าง 1 ถึง 6 เท่านั้น")
        return

    if bet > balance:
        await interaction.response.send_message("💸 คุณมีตั๋วไม่พอเดิมพัน (ถึงไม่โชว์ก็ยังจำกัดอยู่นะ!)")
        return

    dice = random.randint(1, 6)
    if guess == dice:
        win_amount = bet * 3
        update_balance(user_id, win_amount)
        await interaction.response.send_message(
            f"🎉 ลูกเต๋าออก **{dice}** ทายถูก! ได้รับเงิน +{win_amount} พลัน "
        )
    else:
        update_balance(user_id, -bet)
        await interaction.response.send_message(
            f"😢 ลูกเต๋าออก **{dice}** ทายผิด! เสียเงิน -{bet} พลัน"
        )

@bot.tree.command(name="เป่ายิงฉุบ", description="แข่งเป่ายิงฉุบกับกรณ์")
@app_commands.describe(bet="จำนวนเงินที่เดิมพัน", choice="เลือก ค้อน กรรไกร หรือ กระดาษ")
@app_commands.choices(choice=[
    app_commands.Choice(name="🪨 ค้อน", value="ค้อน"),
    app_commands.Choice(name="✂️ กรรไกร", value="กรรไกร"),
    app_commands.Choice(name="📄 กระดาษ", value="กระดาษ")
])
async def rps_game(interaction: discord.Interaction, bet: int, choice: app_commands.Choice[str]):
    user_id = interaction.user.id
    player_choice = choice.value
    bot_choice = random.choice(["ค้อน", "กรรไกร", "กระดาษ"])
    balance = get_balance(user_id)

    if bet <= 4:
        await interaction.response.send_message("⚠️ ต้องเดิมพันมากกว่า 4")
        return

    if bet > balance:
        await interaction.response.send_message("💸 คุณมีตั๋วไม่พอเดิมพัน")
        return

    result = None
    if player_choice == bot_choice:
        result = "draw"
    elif (
        (player_choice == "ค้อน" and bot_choice == "กรรไกร") or
        (player_choice == "กรรไกร" and bot_choice == "กระดาษ") or
        (player_choice == "กระดาษ" and bot_choice == "ค้อน")
    ):
        result = "win"
    else:
        result = "lose"

    if result == "win":
        update_balance(user_id, bet)
        message = f" คุณเลือก **{player_choice}** | กรณ์เลือก **{bot_choice}**\n✅ คุณชนะ! ได้รับเงิน +{bet} พลัน"
    elif result == "lose":
        update_balance(user_id, -bet)
        message = f" คุณเลือก **{player_choice}** | กรณ์เลือก **{bot_choice}**\n❌ คุณแพ้! เสียเงิน -{bet} พลัน"
    else:
        message = f" คุณเลือก **{player_choice}** | กรณ์เลือก **{bot_choice}**\n🔁 เสมอ! ได้เงินคืน"

    await interaction.response.send_message(message)

server_on()

print("Token Loaded:", os.getenv('TOKEN'))

bot.run(os.getenv('TOKEN'))
