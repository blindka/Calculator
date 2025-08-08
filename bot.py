import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv

# Try to load environment variables from tokev.env file
try:
    load_dotenv('tokev.env')
    print("📁 Loaded tokev.env file")
except Exception as e:
    print(f"⚠️ Could not load tokev.env: {e}")
    
# Check if the file exists
if os.path.exists('tokev.env'):
    print("✅ tokev.env file found")
    with open('tokev.env', 'r') as f:
        content = f.read()
        if 'DISCORD_BOT_TOKEN' in content:
            print("✅ DISCORD_BOT_TOKEN found in file")
        else:
            print("❌ DISCORD_BOT_TOKEN not found in file")
else:
    print("❌ tokev.env file not found in current directory")

# Bot settings
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

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

# On bot ready - Enhanced with better error handling and debugging
@bot.event
async def on_ready():
    print(f"{bot.user} is connecting...")
    try:
        # Clear existing commands (optional - uncomment if needed)
        # bot.tree.clear_commands(guild=None)
        
        # Sync commands
        synced = await bot.tree.sync()
        print(f"✅ Successfully synced {len(synced)} command(s)")
        
        # List synced commands for debugging
        for command in synced:
            print(f"   - /{command.name}: {command.description}")
            
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
        print(f"Error type: {type(e).__name__}")
    
    print(f"🤖 {bot.user} is now online and ready!")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"🔧 Bot is in {len(bot.guilds)} guild(s)")

# Error handler for command errors
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    else:
        print(f"Command error: {error}")
        await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

# Test command to verify bot is working
@bot.tree.command(name="test", description="Test if the bot is working properly")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("✅ הבוט עובד בצורה תקינה! (Bot is working properly!)", ephemeral=True)

# Slash Command - Convert between bases
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

# Slash Command - Perform operation between two numbers
@bot.tree.command(name="operation", description="Perform an operation between two numbers in given bases")
@app_commands.describe(
    op="Operation type: add, sub, mul, div, and, or, xor",
    num1="First number",
    base1="Base of first number",
    num2="Second number",
    base2="Base of second number",
    result_base="Base for the result (ignored for div)"
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

# View for interactive commands help (sends DM)
class CommandsHelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)  # 5 minute timeout

    async def on_timeout(self):
        # Disable buttons when view times out
        for item in self.children:
            item.disabled = True

    @discord.ui.button(label="Convert Command", style=discord.ButtonStyle.primary, emoji="🔄")
    async def convert_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = (
            "🔄 **/convert**\n"
            "**Usage:** `/convert number:<value> from_base:<2|8|10|16> to_base:<2|8|10|16>`\n"
            "**Example:** `/convert number:1011 from_base:2 to_base:10`\n"
            "**Description:** Converts a number from one base to another.\n"
            "**Supported bases:** Binary (2), Octal (8), Decimal (10), Hexadecimal (16).\n\n"
            "**Examples:**\n"
            "• Binary to Decimal: `/convert number:1011 from_base:2 to_base:10` → Result: `11`\n"
            "• Hex to Binary: `/convert number:ff from_base:16 to_base:2` → Result: `11111111`"
        )
        try:
            await interaction.user.send(msg)
            await interaction.response.send_message("📩 I sent you a DM with the Convert command details.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I couldn't send you a DM. Please enable DMs from this server.", ephemeral=True)

    @discord.ui.button(label="Operation Command", style=discord.ButtonStyle.primary, emoji="🧮")
    async def operation_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = (
            "🧮 **/operation**\n"
            "**Usage:** `/operation op:<add|sub|mul|div|and|or|xor> num1:<value> base1:<2|8|10|16> num2:<value> base2:<2|8|10|16> result_base:<2|8|10|16>`\n"
            "**Example:** `/operation op:add num1:101 base1:2 num2:7 base2:10 result_base:10`\n"
            "**Description:** Performs mathematical or binary operations between two numbers in given bases.\n\n"
            "**Operations:**\n"
            "• **Mathematical:** add, sub, mul, div\n"
            "• **Binary:** and, or, xor\n\n"
            "**Note:** For `div`, shows quotient and remainder. Logical operations work on integer values.\n\n"
            "**Examples:**\n"
            "• Add: `/operation op:add num1:101 base1:2 num2:3 base2:10 result_base:10` → Result: `8`\n"
            "• XOR: `/operation op:xor num1:ff base1:16 num2:aa base2:16 result_base:16` → Result: `55`"
        )
        try:
            await interaction.user.send(msg)
            await interaction.response.send_message("📩 I sent you a DM with the Operation command details.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I couldn't send you a DM. Please enable DMs from this server.", ephemeral=True)

    @discord.ui.button(label="Test Command", style=discord.ButtonStyle.success, emoji="✅")
    async def test_help(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = (
            "✅ **/test**\n"
            "**Usage:** `/test`\n"
            "**Description:** Simple command to test if the bot is working properly.\n"
            "**Use this:** To verify the bot is responding to slash commands correctly."
        )
        try:
            await interaction.user.send(msg)
            await interaction.response.send_message("📩 I sent you a DM with the Test command details.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ I couldn't send you a DM. Please enable DMs from this server.", ephemeral=True)

# Slash Command - Interactive commands help (Enhanced)
@bot.tree.command(name="commands", description="Interactive help for all available commands")
async def commands_help(interaction: discord.Interaction):
    print(f"Commands help requested by {interaction.user}")
    
    embed = discord.Embed(
        title="🤖 Bot Commands Help",
        description="Click the buttons below to receive detailed information about each command in your DMs:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Available Commands",
        value="• `/convert` - Convert numbers between bases\n• `/operation` - Perform calculations\n• `/test` - Test bot functionality",
        inline=False
    )
    embed.set_footer(text="💡 Make sure your DMs are open to receive help messages!")
    
    view = CommandsHelpView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Additional command for debugging server info
@bot.tree.command(name="botinfo", description="Show bot information and status")
async def bot_info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Bot Information",
        color=discord.Color.green()
    )
    embed.add_field(name="Bot Name", value=bot.user.display_name, inline=True)
    embed.add_field(name="Bot ID", value=bot.user.id, inline=True)
    embed.add_field(name="Servers", value=len(bot.guilds), inline=True)
    embed.add_field(name="Commands", value=len(bot.tree.get_commands()), inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Manual sync command (for debugging - only for bot owner)
@bot.tree.command(name="sync", description="Manually sync slash commands (Owner only)")
async def sync_commands(interaction: discord.Interaction):
    # Replace YOUR_USER_ID with your actual Discord user ID
    if interaction.user.id != 269890726840500224:  # Replace with your Discord ID
        await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
        return
    
    try:
        synced = await bot.tree.sync()
        await interaction.response.send_message(f"✅ Manually synced {len(synced)} commands!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to sync: {e}", ephemeral=True)

# Run the bot
if __name__ == "__main__":
    print("🔍 Current working directory:", os.getcwd())
    print("📁 Files in directory:", os.listdir('.'))
    
    # Try to get token from environment variable first
    token = os.getenv('DISCORD_BOT_TOKEN')
    print(f"🔑 Token loaded: {'Yes' if token else 'No'}")
    
    if not token:
        print("⚠️  No token found in environment variables!")
        print("📝 Please check your tokev.env file:")
        print("   1. Make sure it's in the same folder as bot.py")
        print("   2. Make sure it contains: DISCORD_BOT_TOKEN=your_actual_token")
        print("   3. No spaces around the = sign")
        print("   4. No quotes around the token")
        print("\n💡 Example tokev.env content:")
        print("DISCORD_BOT_TOKEN=MTQwMDk2MjkzOTc0NTMzNzM2NA.GWLRVm.your_actual_token_here")
        
        # Try to read the file manually for debugging
        if os.path.exists('tokev.env'):
            print("\n📄 Current tokev.env content:")
            with open('tokev.env', 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    print(f"   Line {i}: '{line.strip()}'")
        
        exit(1)
    
    try:
        print("🚀 Starting bot...")
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Invalid bot token! Please check your token.")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")