import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables from token.env file test
load_dotenv('token.env')

# Bot settings - Use only basic intents (no privileged intents needed)
intents = discord.Intents.default()
intents.message_content = True  # This is needed for slash commands
bot = commands.Bot(command_prefix="!", intents=intents)

# Simple test command
@bot.tree.command(name="ping", description="Test if bot is working")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Bot is working!", ephemeral=True)
    print(f"Ping command used by {interaction.user}")

# Check if the number is valid for the given base
def is_valid_number(num: str, base: int) -> bool:
    valid_chars = "0123456789abcdef"[:base]
    num = num.lower().strip()
    return all(c in valid_chars for c in num)

# Convert number from one base to another
def convert_base(num_str: str, from_base: int, to_base: int) -> str:
    decimal_value = int(num_str, from_base)
    if to_base == 2:
        return bin(decimal_value)[2:]
    elif to_base == 8:
        return oct(decimal_value)[2:]
    elif to_base == 10:
        return str(decimal_value)
    elif to_base == 16:
        return hex(decimal_value)[2:]
    else:
        raise ValueError("Invalid base")

# Perform the selected operation
def perform_operation(op: str, n1: int, n2: int):
    if op == "add":
        return n1 + n2
    elif op == "sub":
        return n1 - n2
    elif op == "mul":
        return n1 * n2
    elif op == "div":
        quotient = n1 // n2
        remainder = n1 % n2
        return f"Quotient: {quotient}, Remainder: {remainder}"
    elif op == "and":
        return n1 & n2
    elif op == "or":
        return n1 | n2
    elif op == "xor":
        return n1 ^ n2
    else:
        raise ValueError("Invalid operation")

# Bot ready event - Fixed duplicate commands issue
@bot.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"🤖 BOT LOGIN SUCCESSFUL")
    print(f"Bot: {bot.user.name} (ID: {bot.user.id})")
    print(f"{'='*50}")
    
    # Check servers
    print(f"🏠 Bot is in {len(bot.guilds)} server(s):")
    for guild in bot.guilds:
        print(f"   • {guild.name} (ID: {guild.id}, Members: {guild.member_count})")
    
    # Check bot permissions in each guild
    for guild in bot.guilds:
        bot_member = guild.get_member(bot.user.id)
        if bot_member:
            perms = bot_member.guild_permissions
            print(f"\n🔐 Permissions in '{guild.name}':")
            print(f"   Administrator: {perms.administrator}")
            print(f"   Use Slash Commands: {perms.use_application_commands}")
            print(f"   Send Messages: {perms.send_messages}")
    
    # Show registered commands BEFORE syncing
    print(f"\n📝 Commands registered in code:")
    for cmd in bot.tree.get_commands():
        print(f"   • {cmd.name}: {cmd.description}")
    
    # Fixed: Simple sync - only global OR only specific servers
    print(f"\n🔄 Attempting to sync slash commands...")
    
    try:
        # Choose one of two options:
        
        # Option 1: Global sync (recommended - simpler, but takes up to 1 hour)
        synced = await bot.tree.sync()
        print(f"   🌐 Global sync successful: {len(synced)} commands")
        print(f"   ⏰ Commands will be available in ALL servers within 1 hour")
        
        # Option 2: Immediate sync to specific servers (uncomment to use)
        # total_synced = 0
        # for guild in bot.guilds:
        #     try:
        #         synced = await bot.tree.sync(guild=guild)
        #         total_synced += len(synced)
        #         print(f"   ✅ Synced {len(synced)} commands to '{guild.name}' (IMMEDIATE)")
        #         for cmd in synced:
        #             print(f"      - /{cmd.name}")
        #     except Exception as e:
        #         print(f"   ❌ Failed to sync to '{guild.name}': {e}")
        # print(f"   🎉 Commands available IMMEDIATELY in {len(bot.guilds)} server(s)!")
        
    except Exception as e:
        print(f"❌ SYNC FAILED: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"{'='*50}\n")

# Error handler
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print(f"Command error: {error}")
    if not interaction.response.is_done():
        await interaction.response.send_message("❌ An error occurred!", ephemeral=True)

# Convert command
@bot.tree.command(name="convert", description="Convert a number from one base to another")
@app_commands.describe(number="The number to convert", from_base="Base of the input number", to_base="Base of the result")
async def convert(interaction: discord.Interaction, number: str, from_base: int, to_base: int):
    print(f"Convert command used: {number} from base {from_base} to base {to_base}")
    
    if from_base not in [2, 8, 10, 16] or to_base not in [2, 8, 10, 16]:
        await interaction.response.send_message("Supported bases: 2, 8, 10, 16", ephemeral=True)
        return
    if not is_valid_number(number, from_base):
        await interaction.response.send_message(f"The number `{number}` is not valid in base {from_base}", ephemeral=True)
        return

    try:
        result = convert_base(number, from_base, to_base)
        await interaction.response.send_message(f"Result in base {to_base}: `{result}`", ephemeral=True)
    except Exception as e:
        print(f"Error in convert command: {e}")
        await interaction.response.send_message("An error occurred during conversion.", ephemeral=True)

# Operation command
@bot.tree.command(name="operation", description="Perform an operation between two numbers in given bases")
@app_commands.describe(
    op="Operation type: add, sub, mul, div, and, or, xor",
    num1="First number",
    base1="Base of first number", 
    num2="Second number",
    base2="Base of second number",
    result_base="Base for the result"
)
async def operation(interaction: discord.Interaction, op: str, num1: str, base1: int, num2: str, base2: int, result_base: int):
    print(f"Operation command used: {op} between {num1} (base {base1}) and {num2} (base {base2})")
    
    op = op.lower()
    if op not in ["add", "sub", "mul", "div", "and", "or", "xor"]:
        await interaction.response.send_message("Supported operations: add, sub, mul, div, and, or, xor", ephemeral=True)
        return

    for b in [base1, base2, result_base]:
        if b not in [2, 8, 10, 16]:
            await interaction.response.send_message("Supported bases: 2, 8, 10, 16", ephemeral=True)
            return

    if not is_valid_number(num1, base1):
        await interaction.response.send_message(f"The number `{num1}` is not valid in base {base1}", ephemeral=True)
        return
    if not is_valid_number(num2, base2):
        await interaction.response.send_message(f"The number `{num2}` is not valid in base {base2}", ephemeral=True)
        return

    n1 = int(num1, base1)
    n2 = int(num2, base2)

    try:
        result = perform_operation(op, n1, n2)
    except ZeroDivisionError:
        await interaction.response.send_message("Cannot divide by zero", ephemeral=True)
        return
    except Exception as e:
        print(f"Error in operation command: {e}")
        await interaction.response.send_message("An error occurred during the operation.", ephemeral=True)
        return

    try:
        if isinstance(result, int):
            result_str = convert_base(str(result), 10, result_base)
            await interaction.response.send_message(f"Result of {op} in base {result_base}: `{result_str}`", ephemeral=True)
        else:
            await interaction.response.send_message(f"Result of {op}: {result}", ephemeral=True)
    except Exception as e:
        print(f"Error formatting result: {e}")
        await interaction.response.send_message("An error occurred while formatting the result.", ephemeral=True)

# Help command
@bot.tree.command(name="help", description="Get help with bot commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Calculator Bot Commands",
        description="Available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="🏓 /ping", 
        value="Test if bot is working", 
        inline=False
    )
    embed.add_field(
        name="🔄 /convert", 
        value="Convert numbers between bases (2, 8, 10, 16)", 
        inline=False
    )
    embed.add_field(
        name="🧮 /operation", 
        value="Perform operations (add, sub, mul, div, and, or, xor)", 
        inline=False
    )
    embed.set_footer(text="💡 All responses are private (ephemeral)")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Force sync command for emergency
@bot.tree.command(name="forcesync", description="Emergency command sync")
async def force_sync(interaction: discord.Interaction):
    try:
        synced = await bot.tree.sync(guild=interaction.guild)
        await interaction.response.send_message(f"🔄 Force synced {len(synced)} commands to this server!", ephemeral=True)
        print(f"Force sync by {interaction.user}: {len(synced)} commands")
    except Exception as e:
        await interaction.response.send_message(f"❌ Force sync failed: {e}", ephemeral=True)
        print(f"Force sync error: {e}")



# Run the bot
if __name__ == "__main__":
    print("🚀 STARTING BOT...")
    print("📁 Current directory:", os.getcwd())
    print("📁 Files:", [f for f in os.listdir('.') if f.endswith('.env')])
    
    # Get token
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ NO TOKEN FOUND!")
        print("📝 Make sure token.env contains:")
        print("   DISCORD_BOT_TOKEN=your_actual_token")
        
        if os.path.exists('token.env'):
            print("\n📄 Current token.env content:")
            with open('token.env', 'r') as f:
                content = f.read()
                print(f"'{content}'")
                if 'DISCORD_BOT_TOKEN' not in content:
                    print("❌ Missing DISCORD_BOT_TOKEN in file!")
        else:
            print("❌ token.env file not found!")
        
        exit(1)
    
    print(f"✅ Token loaded: {token[:20]}...")
    
    try:
        print("🔌 Connecting to Discord...")
        bot.run(token)
    except discord.LoginFailure:
        print("❌ INVALID TOKEN! Please regenerate your bot token.")
    except Exception as e:
        print(f"❌ BOT ERROR: {e}")
        import traceback
        traceback.print_exc()