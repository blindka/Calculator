import discord
from discord.ext import commands
from discord.ui import Select, View

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} is connected")
    bot.add_view(PersistentOperationView())

class BaseSelect(Select):
    def __init__(self, placeholder):
        options = [
            discord.SelectOption(label="בסיס בינארי (2)", value="2"),
            discord.SelectOption(label="בסיס אוקטלי (8)", value="8"),
            discord.SelectOption(label="בסיס עשרוני (10)", value="10"),
            discord.SelectOption(label="בסיס הקסדצימלי (16)", value="16")
        ]
        super().__init__(placeholder=placeholder, min_values=1, max_values=1, options=options, custom_id="base_select")

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_base = int(self.values[0])
        await interaction.response.defer()
        self.view.stop()

async def בחר_בסיס(ctx, טקסט):
    view = View(timeout=60)
    select = BaseSelect(placeholder=טקסט)
    view.add_item(select)
    msg = await ctx.send(טקסט, view=view)
    await view.wait()
    if not hasattr(view, "selected_base"):
        await msg.edit(content="לא בוצעה בחירה, אנא נסה שוב", view=None)
        raise Exception("No base selected")
    return view.selected_base

class OperationSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="המרת מספר בין בסיסים", value="convert"),
            discord.SelectOption(label="חיבור בין שני מספרים", value="add"),
            discord.SelectOption(label="חיסור בין שני מספרים", value="sub"),
            discord.SelectOption(label="כפל בין שני מספרים", value="mul")
        ]
        super().__init__(placeholder="בחר פעולה לביצוע", min_values=1, max_values=1, options=options, custom_id="operation_select")

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_operation = self.values[0]
        await interaction.response.defer()
        self.view.stop()

class PersistentOperationView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OperationSelect())

async def שאל_מספר_צאט(ctx, טקסט):
    def check(m): return m.author == ctx.author and m.channel == ctx.channel
    await ctx.send(טקסט)
    msg = await bot.wait_for('message', timeout=30.0, check=check)
    return msg.content

@bot.command()
async def פעולה(ctx):
    view = View(timeout=60)
    select = OperationSelect()
    view.add_item(select)
    msg = await ctx.send("בחר פעולה לביצוע:", view=view)
    await view.wait()

    if not hasattr(view, "selected_operation"):
        await msg.edit(content="לא בוצעה בחירה, אנא נסה שוב", view=None)
        return

    פעולה = view.selected_operation

    def check(m): return m.author == ctx.author and m.channel == ctx.channel

    if פעולה == "convert":
        try:
            מבסיס = await בחר_בסיס(ctx, "מאיזה בסיס תרצה לבצע את ההמרה?")
            לבסיס = await בחר_בסיס(ctx, "לאיזה בסיס תרצה להמיר?")
        except:
            return

        while True:
            try:
                מספר = await שאל_מספר_צאט(ctx, "מה המספר שתרצה לבצע לו המרה?")
                if not all(c in "0123456789abcdef"[:מבסיס] for c in מספר.lower()):
                    await ctx.send("קלט אינו תואם את הבסיס שנבחר, אנא נסה שנית")
                    continue
                dec = int(מספר, מבסיס)
                break
            except:
                await ctx.send("קלט אינו תואם את הבסיס שנבחר, אנא נסה שנית")

        if לבסיס == 2:
            תוצאה = bin(dec)[2:]
        elif לבסיס == 8:
            תוצאה = oct(dec)[2:]
        elif לבסיס == 10:
            תוצאה = str(dec)
        elif לבסיס == 16:
            תוצאה = hex(dec)[2:]

        await ctx.send(f"**התוצאה בבסיס {לבסיס}:**\n`{תוצאה}`")

    else:
        while True:
            try:
                num1 = await שאל_מספר_צאט(ctx, "הכנס את המספר הראשון:")
                base1 = await בחר_בסיס(ctx, "בחר את הבסיס של המספר הראשון:")

                num2 = await שאל_מספר_צאט(ctx, "הכנס את המספר השני:")
                base2 = await בחר_בסיס(ctx, "בחר את הבסיס של המספר השני:")

                result_base = await בחר_בסיס(ctx, "בחר את הבסיס שבו תרצה לראות את התוצאה:")

                if not all(c in "0123456789abcdef"[:base1] for c in num1.lower()) or \
                   not all(c in "0123456789abcdef"[:base2] for c in num2.lower()):
                    await ctx.send("קלט אינו תואם את הבסיסים שנבחרו, אנא נסה שוב")
                    continue

                n1 = int(num1, base1)
                n2 = int(num2, base2)

                if פעולה == "add":
                    result = n1 + n2
                elif פעולה == "sub":
                    result = n1 - n2
                elif פעולה == "mul":
                    result = n1 * n2

                if result_base == 2:
                    תוצאה = bin(result)[2:]
                elif result_base == 8:
                    תוצאה = oct(result)[2:]
                elif result_base == 10:
                    תוצאה = str(result)
                elif result_base == 16:
                    תוצאה = hex(result)[2:]

                break
            except:
                await ctx.send("קלט שגוי, אנא ודא שהמספרים תואמים לבסיסים שהוזנו ונסה שוב")

        פלט = {
            "add": "חיבור",
            "sub": "חיסור",
            "mul": "כפל"
        }[פעולה]

        await ctx.send(f"**התוצאה ב{פלט} בבסיס {result_base}:**\n`{תוצאה}`")
    