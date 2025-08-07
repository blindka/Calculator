import discord
from discord.ext import commands
from discord.ui import Select, View

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Print when the bot is connected
@bot.event
async def on_ready():
    print(f"{bot.user} is connected")
    bot.add_view(PersistentOperationView())

# Menu to choose a base for number operations
class BaseSelect(Select):
    def __init__(self, placeholder):
        options = [
            discord.SelectOption(label="Binary (2)", value="2"),
            discord.SelectOption(label="Octal (8)", value="8"),
            discord.SelectOption(label="Decimal (10)", value="10"),
            discord.SelectOption(label="Hexadecimal (16)", value="16"),
        ]
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options,
            custom_id="base_select",
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_base = int(self.values[0])
        await interaction.response.defer()
        self.view.stop()

# Shows the base-selection menu and returns the chosen base
async def select_base(ctx, text):
    view = View(timeout=60)
    select = BaseSelect(placeholder=text)
    view.add_item(select)
    msg = await ctx.send(text, view=view)
    await view.wait()
    if not hasattr(view, "selected_base"):
        await msg.edit(content="No selection made, please try again.", view=None)
        raise Exception("No base selected")
    return view.selected_base

class OperationSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Convert number between bases", value="convert"),
            discord.SelectOption(label="Add two numbers", value="add"),
            discord.SelectOption(label="Subtract two numbers", value="sub"),
            discord.SelectOption(label="Multiply two numbers", value="mul"),
        ]
        super().__init__(
            placeholder="Choose an operation",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="operation_select",
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_operation = self.values[0]
        await interaction.response.defer()
        self.view.stop()

class PersistentOperationView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OperationSelect())

async def prompt_number_chat(ctx, text):
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    await ctx.send(text)
    msg = await bot.wait_for("message", timeout=30.0, check=check)
    return msg.content

@bot.command()
async def operation(ctx):
    view = View(timeout=60)
    select = OperationSelect()
    view.add_item(select)
    msg = await ctx.send("Choose an operation:", view=view)
    await view.wait()

    if not hasattr(view, "selected_operation"):
        await msg.edit(content="No selection made, please try again.", view=None)
        return

    op = view.selected_operation

    if op == "convert":
        try:
            from_base = await select_base(ctx, "From which base do you want to convert?")
            to_base = await select_base(ctx, "To which base do you want to convert?")
        except:
            return

        while True:
            try:
                number = await prompt_number_chat(ctx, "Enter the number you want to convert:")
                if not all(c in "0123456789abcdef"[:from_base] for c in number.lower()):
                    await ctx.send("Input does not match the selected base. Please try again.")
                    continue
                dec = int(number, from_base)
                break
            except:
                await ctx.send("Input does not match the selected base. Please try again.")

        if to_base == 2:
            result_text = bin(dec)[2:]
        elif to_base == 8:
            result_text = oct(dec)[2:]
        elif to_base == 10:
            result_text = str(dec)
        elif to_base == 16:
            result_text = hex(dec)[2:]

        await ctx.send(f"**Result in base {to_base}:**\n`{result_text}`")

    else:
        while True:
            try:
                num1 = await prompt_number_chat(ctx, "Enter the first number:")
                base1 = await select_base(ctx, "Choose the base of the first number:")

                num2 = await prompt_number_chat(ctx, "Enter the second number:")
                base2 = await select_base(ctx, "Choose the base of the second number:")

                result_base = await select_base(ctx, "Choose the base for the result:")

                if not all(c in "0123456789abcdef"[:base1] for c in num1.lower()) or \
                   not all(c in "0123456789abcdef"[:base2] for c in num2.lower()):
                    await ctx.send("Input does not match the chosen bases. Please try again.")
                    continue

                n1 = int(num1, base1)
                n2 = int(num2, base2)

                if op == "add":
                    result = n1 + n2
                elif op == "sub":
                    result = n1 - n2
                elif op == "mul":
                    result = n1 * n2

                if result_base == 2:
                    result_text = bin(result)[2:]
                elif result_base == 8:
                    result_text = oct(result)[2:]
                elif result_base == 10:
                    result_text = str(result)
                elif result_base == 16:
                    result_text = hex(result)[2:]

                break
            except:
                await ctx.send("Invalid input. Make sure numbers match their bases and try again.")

        op_display = {
            "add": "addition",
            "sub": "subtraction",
            "mul": "multiplication",
        }[op]

        await ctx.send(f"**Result of {op_display} in base {result_base}:**\n`{result_text}`")

@bot.command(name="commands")
async def send_commands_list(ctx):
    try:
        commands_message = (
            "**Available bot commands:**\n\n"
            "**!commands** – Get the full command list in DM\n"
            "**!operation** – Open a menu to choose an operation (convert, add, subtract, multiply) between numbers in same/different bases\n\n"
            "Supported bases: Binary (2), Octal (8), Decimal (10), Hexadecimal (16).\n"
        )
        await ctx.author.send(commands_message)
    except discord.Forbidden:
        await ctx.send("I couldn't DM you. Please allow direct messages from this server.")
