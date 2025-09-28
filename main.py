from flask import (
    Flask,
    make_response,
    request,
    session,
    redirect,
    render_template_string,
    jsonify,
    abort,
    send_file
)
from flask import send_file
from werkzeug.utils import secure_filename
import os
import time
import threading
import discord
import random
import io
from discord.ext import commands
import base64
from discord import app_commands
import string
import asyncio
import secrets
import requests
from discord.ui import Modal, TextInput
from datetime import datetime

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


XOR_KEY = b"8b64b53738b7e0f3f55dce35f598c4c37d3d0b670fcc6db313fe90c4be45e747"  # jack never share this shit dead ass like never even copy it to your clipboard
BYPASS_THUMBNAIL_URL = "https://raw.githubusercontent.com/prototbh/TEMP/refs/heads/main/Screenshot%202025-09-19%20210530.png"
SECURITY_ALERT_CHANNEL_ID = 1419756627162304622


def get_ip_geolocation(ip_address):
    try:
        if (
            ip_address == "127.0.0.1"
        ):
            return "Local/Private Network"
        response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            location_parts = []
            if data.get("city"):
                location_parts.append(data["city"])
            if data.get("region"):
                location_parts.append(data["region"])
            if data.get("country_name"):
                location_parts.append(data["country_name"])
            return (
                ", ".join(location_parts) if location_parts else "Location unavailable"
            )
        return "API request failed"
    except Exception as e:
        print(f"Geolocation error for IP {ip_address}: {e}")
        return "Geolocation service unavailable"


async def send_security_alert(ip_address, user_agent, referer):
    try:
        location_info = get_ip_geolocation(ip_address)

        embed_data = {
            "title": "Security Alert: Bypass Attempt Detected",
            "description": f"**Bypass attempt detected from the following source:**\n\n"
            f"**Geolocation:** `{location_info}`\n"
            f"**User Agent:** `{user_agent[:100]}...`\n"
            f"**Referer:** `{referer[:100] if referer else 'None'}...`\n\n"
            f"**Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "color": 0x000001,
            "thumbnail": {"url": BYPASS_THUMBNAIL_URL},
            "footer": {"text": "Vertex Z Security System - Automated Monitoring"},
        }
        channel = bot.get_channel(SECURITY_ALERT_CHANNEL_ID)
        if channel:
            await channel.send(embed=discord.Embed.from_dict(embed_data))
    except Exception as e:
        print(f"Error sending security alert: {e}")


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="ping", description="Replies with Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


class PaymentSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🤖PayPal", description="Pay with PayPal"),
            discord.SelectOption(
                label="🤑Crypto (LTC,BTC)", description="Pay with Cryptocurrency"
            ),
            discord.SelectOption(label="📈Robux - TOP OPTION", description="Pay with Robux"),
        ]
        super().__init__(
            placeholder="Buy perm key...", min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        ticket_number = random.randint(1, 1000)
        category = bot.get_channel(1397640585527169095)
        if category is None:
            await interaction.response.send_message(
                "❌ Could not find the ticket category.", ephemeral=True
            )
            return
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
        }
        support_role = interaction.guild.get_role(1397384666419433541)
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True,
                manage_channels=True,
            )
        try:
            channel = await category.create_text_channel(
                name=f"Buyer-Ticket-{ticket_number}",
                overwrites=overwrites,
                topic=f"Payment ticket for {interaction.user.name} - {self.values[0]}",
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to create ticket channel: {e}", ephemeral=True
            )
            return
        embed = discord.Embed(
            title="Buyer Info",
            description=f"Payment method selected: {self.values[0]}",
            color=discord.Color.from_str("#000000"),
        )
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/prototbh/TEMP/refs/heads/main/Screenshot%202025-09-19%20210530.png"
        )
        embed.add_field(
            name="User",
            value=f"{interaction.user.mention} ({interaction.user.name})",
            inline=True,
        )
        embed.add_field(name="User ID", value=interaction.user.id, inline=True)
        embed.add_field(
            name="Account Created",
            value=interaction.user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=False,
        )
        embed.set_footer(text="Vertex Z", icon_url=None)
        view = CloseTicketView()
        await channel.send(
            content=f"{interaction.user.mention} {support_role.mention if support_role else ''}",
            embed=embed,
            view=view,
        )

        await interaction.response.send_message(
            f"✅ Ticket created! Check {channel.mention}", ephemeral=True
        )


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket"
    )
    async def close_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not any(role.id == 1397384666419433541 for role in interaction.user.roles):
            await interaction.response.send_message(
                "❌ You don't have permission to close tickets.", ephemeral=True
            )
            return
        await interaction.channel.delete()


class GetKeyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Get Key", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        # Create the embed
        embed = discord.Embed(
            title="AD Lock",
            description="To proceed with obtaining your key, please complete the verification process by clicking [this link](https://lootdest.org/s?og5sV6mJ). This helps us maintain security and prevent unauthorized access to our services.",
            color=0x000001,
        )
        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/prototbh/TEMP/refs/heads/main/Screenshot%202025-09-19%20210530.png"
        )
        embed.set_footer(text="Vertex Z - Key Locked")

        try:
            # Send the embed to the user's DMs
            await interaction.user.send(embed=embed)
            await interaction.response.send_message(
                "Done ✅ Check your DMs.", ephemeral=True
            )
        except discord.Forbidden:
            # If the user has DMs disabled
            await interaction.response.send_message(
                "❌ I couldn't send you a DM. Please enable DMs from server members and try again.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {str(e)}", ephemeral=True
            )


class RedeemKeyButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="Redeem Key for Script", style=discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        modal = KeyRedeemModal()
        await interaction.response.send_modal(modal)


class KeyRedeemModal(discord.ui.Modal, title="Key Redemption"):
    def __init__(self):
        super().__init__()
        self.key_input = discord.ui.TextInput(
            label="Please input your key below",
            placeholder="Enter your Vertex Z key here...",
            style=discord.TextStyle.short,
            required=True,
            max_length=50,
        )
        self.add_item(self.key_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        user_key = self.key_input.value.strip()
        lua_content = read_keys_file()
        if lua_content is None:
            await interaction.followup.send(
                "❌ Error reading keys database. Please try again later.",
                ephemeral=True,
            )
            return
        perm_keys = extract_keys_from_lua(lua_content)
        temp_keys = extract_temp_keys_from_lua(lua_content)
        key_type = None
        expiry_time = None
        if user_key in perm_keys:
            key_type = "perm"
        elif user_key in temp_keys:
            key_type = "temp"
            expiry_time = temp_keys[user_key]
        if not key_type:
            await interaction.followup.send(
                "❌ Invalid key. Please check your key and try again.", ephemeral=True
            )
            return
        embed = discord.Embed(
            title="Key Redeemed 🔓",
            description="Thank You For Using Vertex Z",
            color=0x000001,
        )

        lua_code = f"""local key = "{user_key}"
local loadScript = loadstring(game:HttpGet("https://vertex-z.onrender.com/error?key=skidder"))()
loadScript(key)"""

        embed.add_field(
            name="Script Code", value=f"``\n{lua_code}\n``", inline=False
        )
        if key_type == "perm":
            embed.add_field(
                name="⏳ Key Validity", value="**Permanent** 🔄", inline=True
            )
        else:
            try:
                from datetime import datetime
                import pytz

                est = pytz.timezone("US/Eastern")
                expiry_datetime = datetime.strptime(
                    expiry_time, "%Y-%m-%d %H:%M:%S EST"
                )
                expiry_datetime = est.localize(expiry_datetime)
                current_time = datetime.now(est)

                time_diff = expiry_datetime - current_time
                total_seconds = int(time_diff.total_seconds())

                if total_seconds <= 0:
                    embed.add_field(
                        name="⏳ Key Validity", value="**EXPIRED** ❌", inline=True
                    )
                else:
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    expiry_timestamp = int(expiry_datetime.timestamp())
                    time_display = f"Expires <t:{expiry_timestamp}:R>"

                    embed.add_field(
                        name="⏳ Key Validity", value=f"**{time_display}**", inline=True
                    )

            except Exception as e:
                embed.add_field(
                    name="⏳ Key Validity", value="**Valid** ✅", inline=True
                )

        embed.set_thumbnail(
            url="https://raw.githubusercontent.com/prototbh/TEMP/refs/heads/main/Screenshot%202025-09-19%20210530.png"
        )
        embed.set_footer(text="Use this code inside your executor.")

        try:
            await interaction.user.send(embed=embed)
            await interaction.followup.send(
                "✅ Key redeemed! Check your DMs for the script.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ I couldn't send you a DM. Please enable DMs from server members.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}", ephemeral=True
            )


def extract_temp_keys_from_lua(lua_content):
    temp_keys = {}
    try:
        start_idx = lua_content.find("tempKeys = {")
        if start_idx == -1:
            return temp_keys

        start_bracket = lua_content.find("{", start_idx) + 1
        end_bracket = lua_content.find("}", start_bracket)
        temp_keys_section = lua_content[start_bracket:end_bracket]

        lines = temp_keys_section.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith('["') and '"] = "' in line:
                try:
                    key_end = line.find('"] = "')
                    key = line[2:key_end]
                    expiry_str = line[key_end + 6 : -2]
                    temp_keys[key] = expiry_str
                except Exception:
                    continue

    except Exception as e:
        print(f"Error extracting temp keys: {e}")

    return temp_keys


class ControlPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PaymentSelect())
        self.add_item(GetKeyButton())
        self.add_item(RedeemKeyButton())


@bot.tree.command(name="ctrlpan", description="Sends control panel")
@app_commands.checks.has_permissions(administrator=True)
async def ctrlpan(interaction: discord.Interaction):
    channel = bot.get_channel(CONTROL_PANEL_CHANNEL_ID)
    if channel is None:
        await interaction.response.send_message(
            "❌ Could not find the control panel channel.", ephemeral=True
        )
        return

    embed = discord.Embed(
        title="Vertex Z Control Panel",
        description="This control panel is made to make getting Vertex Z as simple and easy as possible to use.",
        color=discord.Color.from_str("#ace9ff"),
    )
    embed.set_thumbnail(
        url="https://raw.githubusercontent.com/prototbh/TEMP/refs/heads/main/Screenshot%202025-09-19%20210530.png"
    )
    embed.set_footer(text="Vertex Z", icon_url=None)

    await channel.send(embed=embed, view=ControlPanelView())
    await interaction.response.send_message("✅ Control panel sent.", ephemeral=True)


@ctrlpan.error
async def ctrlpan_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.", ephemeral=True
        )


def xor_encrypt_decrypt(data, key):
    if isinstance(data, str):
        data = data.encode("utf-8")
    if isinstance(key, str):
        key = key.encode("utf-8")
    extended_key = (key * (len(data) // len(key) + 1))[: len(data)]
    result = bytes(a ^ b for a, b in zip(data, extended_key))

    return result


def generate_random_key(length=20):
    characters = string.ascii_letters + string.digits + "!@#$%^&*()_-+="
    return "".join(random.choice(characters) for _ in range(length))


def ensure_keys_file():
    keys_content = """local keysModule = {}

keysModule.permKeys = {
    "g7%Nw4Qz-Rk9!Ty2@Lp",
    "Vx3#Jm8Zp-Cq1^Rd5*K",
    "s2!Ht6Wv-Qn8&Lk4%Xr",
    "B9^Pf1Yq-Mz7$Rt5!Lc",
    "Au4!Kz3Vr-Np8^Xy6%G",
    "d8@Rq5Lm-Vz2!Kt7^Xp",
    "C3%Wy9Gh-Rn1$Tk6!Zb",
    "Y6!Tq2Lp-Vm8@Kr4%Nj",
    "P1^Ks7Xc-Qz5$Rd9!Hf",
    "K5!Dr3Mn-Vz8@Lp2%Xc",
    "J8%Vy4Qt-Rn1!Kz7^Lp",
    "L2@Fp6Xk-Mz9$Rt3!Qh",
    "R7!Kq5Yn-Vx2^Lp8%Mc",
    "A4%Xz1Nd-Qv9$Rt6!Kp",
    "F9!Mt2Rp-Kx7^Lq4%Vz",
    "G6^Pz3Wr-Qn8!Kt1@Ly",
    "Z3!Tv9Bn-Mx4$Kr6%Qp",
    "U7%Vq1Fz-Dn8!Rk5@Lp",
    "E2!Kx8Rn-Vz3^Lp6%Qy",
    "S9%Lr4Mp-Kt1!Rz7@Vn",
    "O1!Fg6Yt-Nz8^Kr5%Xp",
    "M8%Rk2Qv-Hz7!Lt3@Pn",
    "N5!Vz3Kq-Xp9^Lr1%Tm",
    "H4^Gt7Wn-Qp2!Kx8@Ly",
    "Q7!Rp5Mn-Lk2^Vx9%Td",
    "T4%Wn8Xy-Kr1!Gp6@Zc",
    "V9@Lf3Qp-Mx7$Rt2!Kh",
    "K6^Dt1Zb-Qn4!Vy8@Rp",
    "Z5!Hq2Nm-Lx9^Kt3%Vg",
    "F8%Xr4Lj-Mz1$Tp7!Kw",
    "C2!Mv6Rg-Kn8^Yp5@Xq",
    "Y1@Tp9Wd-Qm3!Vk7^Lf",
    "P3^Ls5Xv-Nz8!Kr4@Gw",
    "R8!Ky1Bt-Mx6^Hp2%Vn",
    "A9%Gn3Qw-Lk5$Vz7!Rt",
    "E7!Zw4Lp-Kt2^Ry9@Mh",
    "G4^Xc8Dv-Qp1!Ln5@Kr",
    "N2!Vr7Tb-Mz3^Kp6%Wx",
    "U6@Qf1Hy-Ln9!Rt4^Kv",
    "D5!Ks8Xm-Vz2^Qp7%Gr",
    "J3%Lp4Wr-Nx6!Kv1@Ht",
    "B8@Yt2Mf-Qz5!Rk9^Vx",
    "M7^Rz3Gw-Lp8!Kt4@Yn",
    "S1!Hp5Xn-Vm2^Lq9%Zr"
}

keysModule.tempKeys = {}

return keysModule"""

    keys_file_path = "keys.lua"
    if not os.path.exists(keys_file_path):
        encrypted_content = xor_encrypt_decrypt(keys_content, XOR_KEY)
        with open(keys_file_path, "wb") as f:
            f.write(encrypted_content)
        print("Created keys.lua with encrypted content")

    return keys_file_path


def read_keys_file():
    keys_file_path = ensure_keys_file()

    try:
        with open(keys_file_path, "rb") as f:
            encrypted_content = f.read()
        decrypted_content = xor_encrypt_decrypt(encrypted_content, XOR_KEY).decode(
            "utf-8"
        )
        return decrypted_content
    except Exception as e:
        print(f"Error reading keys file: {str(e)}")
        return None


def extract_keys_from_lua(lua_content):
    try:
        start_idx = lua_content.find("permKeys = {")
        if start_idx == -1:
            return []

        start_idx = lua_content.find("{", start_idx) + 1
        end_idx = lua_content.find("}", start_idx)

        keys_section = lua_content[start_idx:end_idx]
        keys = []
        for line in keys_section.split("\n"):
            line = line.strip()
            if line.startswith('"') and line.endswith('",'):
                key = line[1:-2]
                keys.append(key)

        return keys
    except Exception as e:
        print(f"Error extracting keys: {str(e)}")
        return []


def update_keys_in_lua(lua_content, keys):
    try:
        start_idx = lua_content.find("permKeys = {")
        if start_idx == -1:
            return lua_content

        start_bracket = lua_content.find("{", start_idx) + 1
        end_bracket = lua_content.find("}", start_bracket)
        new_keys_section = "\n"
        for key in keys:
            new_keys_section += f'    "{key}",\n'
        updated_content = (
            lua_content[:start_bracket] + new_keys_section + lua_content[end_bracket:]
        )
        return updated_content
    except Exception as e:
        print(f"Error updating keys: {str(e)}")
        return lua_content


def write_keys_file(lua_content):
    keys_file_path = "keys.lua"

    try:
        encrypted_content = xor_encrypt_decrypt(lua_content, XOR_KEY)

        with open(keys_file_path, "wb") as f:
            f.write(encrypted_content)

        return True
    except Exception as e:
        print(f"Error writing keys file: {str(e)}")
        return False


ensure_keys_file()


class KeySelect(discord.ui.Select):
    def __init__(self, keys):
        options = [
            discord.SelectOption(
                label=f"Key #{i+1}",
                description=key[:30] + "..." if len(key) > 30 else key,
                value=str(i),
            )
            for i, key in enumerate(keys)
        ]
        options.append(
            discord.SelectOption(
                label="➕ Add New Key",
                description="Generate a new permanent key",
                value="add",
            )
        )

        super().__init__(
            placeholder="Select a key to manage...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.keys = keys

    async def callback(self, interaction: discord.Interaction):
        selected_value = self.values[0]

        if selected_value == "add":
            new_key = generate_random_key()
            lua_content = read_keys_file()
            if lua_content is None:
                await interaction.response.send_message(
                    "❌ Error reading keys file.", ephemeral=True
                )
                return
            current_keys = extract_keys_from_lua(lua_content)
            current_keys.append(new_key)
            updated_content = update_keys_in_lua(lua_content, current_keys)
            if write_keys_file(updated_content):
                await interaction.response.send_message(
                    f"✅ New key generated and added:\n`{new_key}`\n\nThis key has been saved to the keys file.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "❌ Error saving new key to file.", ephemeral=True
                )
        else:
            key_index = int(selected_value)
            if 0 <= key_index < len(self.keys):
                key_to_remove = self.keys[key_index]
                lua_content = read_keys_file()
                if lua_content is None:
                    await interaction.response.send_message(
                        "❌ Error reading keys file.", ephemeral=True
                    )
                    return
                current_keys = extract_keys_from_lua(lua_content)
                if key_index < len(current_keys):
                    removed_key = current_keys.pop(key_index)
                    updated_content = update_keys_in_lua(lua_content, current_keys)
                    if write_keys_file(updated_content):
                        await interaction.response.send_message(
                            f"✅ Key removed:\n`{removed_key}`\n\nThis key has been removed from the keys file.",
                            ephemeral=True,
                        )
                    else:
                        await interaction.response.send_message(
                            "❌ Error updating keys file.", ephemeral=True
                        )
                else:
                    await interaction.response.send_message(
                        "❌ Key index out of range.", ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    "❌ Invalid key selection.", ephemeral=True
                )


class KeyManageView(discord.ui.View):
    def __init__(self, keys):
        super().__init__(timeout=120)
        self.add_item(KeySelect(keys))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


@bot.tree.command(name="manage_keys", description="Manage the key system")
@app_commands.checks.has_permissions(administrator=True)
async def manage_keys(interaction: discord.Interaction):
    lua_content = read_keys_file()
    if lua_content is None:
        await interaction.response.send_message(
            "❌ Error reading keys file.", ephemeral=True
        )
        return
    keys = extract_keys_from_lua(lua_content)

    if not keys:
        await interaction.response.send_message(
            "❌ No keys found in the keys file.", ephemeral=True
        )
        return
    embed = discord.Embed(
        title="🔑 Key Management System",
        description="Select a key to remove it or choose 'Add New Key' to generate a new one.",
        color=discord.Color(0x000000),
    )
    key_list = "\n".join([f"**{i+1}.** `{key}`" for i, key in enumerate(keys)])
    embed.add_field(
        name=f"Current Permanent Keys ({len(keys)})",
        value=key_list if len(key_list) < 1024 else "Too many keys to display",
        inline=False,
    )

    embed.set_footer(text="This interface will timeout after 2 minutes.")
    await interaction.response.send_message(
        embed=embed, view=KeyManageView(keys), ephemeral=True
    )


@manage_keys.error
async def manage_keys_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(error)}", ephemeral=True
        )


@bot.tree.command(
    name="tk-dump", description="Display all temporary keys and their expiration dates"
)
@app_commands.checks.has_permissions(administrator=True)
async def tk_dump(interaction: discord.Interaction):
    """Display all temporary keys and their expiration dates in an embed"""
    try:
        lua_content = read_keys_file()
        if lua_content is None:
            await interaction.response.send_message(
                "❌ Error reading keys file.", ephemeral=True
            )
            return

        # Extract temp keys section
        start_idx = lua_content.find("tempKeys = {")
        if start_idx == -1:
            await interaction.response.send_message(
                "❌ No temporary keys section found.", ephemeral=True
            )
            return

        start_bracket = lua_content.find("{", start_idx) + 1
        end_bracket = lua_content.find("}", start_bracket)
        temp_keys_section = lua_content[start_bracket:end_bracket]

        # Parse temp keys
        temp_keys = []
        lines = temp_keys_section.split("\n")

        for line in lines:
            line = line.strip()
            if line.startswith('["') and '"] = "' in line:
                try:
                    key_end = line.find('"] = "')
                    key = line[2:key_end]
                    expiry_str = line[key_end + 6 : -2]
                    temp_keys.append((key, expiry_str))
                except Exception as e:
                    print(f"Error parsing temp key line: {e}")
                    continue

        if not temp_keys:
            await interaction.response.send_message(
                "❌ No temporary keys found.", ephemeral=True
            )
            return

        # Create embed
        embed = discord.Embed(
            title="🔑 Temporary Keys Dump",
            description=f"Found **{len(temp_keys)}** temporary key(s)",
            color=discord.Color.gold(),
            timestamp=discord.utils.utcnow(),
        )

        # Add keys to embed (split into fields if too many)
        key_list = ""
        for i, (key, expiry) in enumerate(temp_keys, 1):
            key_entry = f"**{i}. `{key}`**\n   📅 Expires: `{expiry}`\n"

            # If adding this entry would exceed field limit, create a new field
            if len(key_list) + len(key_entry) > 1024:
                embed.add_field(
                    name=f"Temporary Keys (Part {len(embed.fields) + 1})",
                    value=key_list,
                    inline=False,
                )
                key_list = key_entry
            else:
                key_list += key_entry

        # Add remaining keys
        if key_list:
            embed.add_field(
                name=f"Temporary Keys (Part {len(embed.fields) + 1})",
                value=key_list,
                inline=False,
            )

        embed.set_footer(text=f"Total keys: {len(temp_keys)}")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        print(f"Error in tk-dump command: {e}")
        await interaction.response.send_message(
            f"❌ An error occurred while retrieving temporary keys: {str(e)}",
            ephemeral=True,
        )


@tk_dump.error
async def tk_dump_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(error)}", ephemeral=True
        )


@bot.tree.command(
    name="download_keys", description="Download the encrypted keys file (Admin only)"
)
@app_commands.checks.has_permissions(administrator=True)
async def download_keys(interaction: discord.Interaction):
    """Download the encrypted keys.lua file"""
    try:
        # Ensure the keys file exists and get its path
        keys_file_path = ensure_keys_file()

        # Read the encrypted content
        with open(keys_file_path, "rb") as f:
            encrypted_content = f.read()

        # Create a Discord file object
        file = discord.File(
            io.BytesIO(encrypted_content),
            filename="keys.lua",
            description="Encrypted keys file",
        )

        # Send the file to the user
        await interaction.response.send_message(
            "🔑 **Encrypted Keys File**\nHere is the current keys.lua file:",
            file=file,
            ephemeral=True,
        )

    except Exception as e:
        print(f"Error in download_keys command: {e}")
        await interaction.response.send_message(
            f"❌ An error occurred while retrieving the keys file: {str(e)}",
            ephemeral=True,
        )


@download_keys.error
async def download_keys_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You need administrator permissions to use this command.", ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(error)}", ephemeral=True
        )


app = Flask(__name__)
app.secret_key = "93578vbh65748hnty6v47859tynv64578vyn478yn6458"
app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
CONTROL_PANEL_CHANNEL_ID = 1419356040071348377
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_bot_token():
    try:
        response = requests.get(
            "https://voidy-script.neocities.org/nigherhub", timeout=10
        )
        response.raise_for_status()
        token = response.text.strip()
        if token and len(token) > 10:
            return token
        else:
            raise ValueError("Invalid token received from server")

    except Exception as e:
        print(f"Error fetching token: {e}")


niggerbottoken = get_bot_token()

home_page = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <link rel="icon" type="image/png" href="https://voidy-script.neocities.org/IMG_3803.jpeg">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
  <meta property="og:title" content="Vertex Z Script - #1 Roblox Script for Steal a Brainrot" />
  <meta property="og:description" content="Trusted, OP, and lightning-fast. Dominate in Steal a Brainrot with Vertex Z Script." />
  <meta property="og:image" content="https://voidy-script.neocities.org/IMG_3803.jpeg" />
  <meta property="og:url" content="https://vertex-z.onrender.com/" />
  <meta name="theme-color" content="#ace9ff">
  <title>Vertex Z Script</title>
  <meta name="robots" content="index, follow">
  <meta name="description" content="Vertex Z - #1 Roblox script for Steal a Brainrot. OP features, auto-hit, music, and more. Trusted and powerful.">
  <meta name="keywords" content="Vertex Z, Roblox script, Steal a Brainrot, Roblox executor, auto-hit, brainrot script, roblox cheats">
  <meta name="google-site-verification" content="aTXgP6WHLWMaIBkTMUiCuD2kXmdEH3gMxqeOsHQeXq0" />
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap" rel="stylesheet" />
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: 'Inter', sans-serif;
    }

    body {
      background: #000;
      color: #e0f6ff;
      min-height: 100vh;
      overflow-x: hidden;
      position: relative;
      -webkit-overflow-scrolling: touch;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      background:
        linear-gradient(45deg,
          transparent 0%,
          rgba(255, 255, 255, 0.02) 25%,
          rgba(255, 255, 255, 0.05) 50%,
          rgba(255, 255, 255, 0.02) 75%,
          transparent 100%),
        repeating-linear-gradient(0deg,
          rgba(0, 0, 0, 0.8) 0px,
          rgba(15, 15, 15, 0.9) 1px,
          rgba(25, 25, 25, 0.8) 2px,
          rgba(15, 15, 15, 0.9) 3px,
          rgba(0, 0, 0, 0.8) 4px),
        repeating-linear-gradient(90deg,
          rgba(0, 0, 0, 0.8) 0px,
          rgba(15, 15, 15, 0.9) 1px,
          rgba(25, 25, 25, 0.8) 2px,
          rgba(15, 15, 15, 0.9) 3px,
          rgba(0, 0, 0, 0.8) 4px),
        repeating-linear-gradient(45deg,
          transparent 0px,
          rgba(255, 255, 255, 0.08) 1px,
          rgba(255, 255, 255, 0.15) 2px,
          rgba(255, 255, 255, 0.08) 3px,
          transparent 4px,
          transparent 8px),
        repeating-linear-gradient(-45deg,
          transparent 0px,
          rgba(255, 255, 255, 0.08) 1px,
          rgba(255, 255, 255, 0.15) 2px,
          rgba(255, 255, 255, 0.08) 3px,
          transparent 4px,
          transparent 8px),
        radial-gradient(circle at 20% 30%, rgba(172, 233, 255, 0.03) 0%, transparent 50%),
        radial-gradient(circle at 80% 70%, rgba(172, 233, 255, 0.03) 0%, transparent 50%);
      background-size:
        100% 100%,
        4px 4px,
        4px 4px,
        8px 8px,
        8px 8px,
        400px 400px,
        300px 300px;
      animation: carbonWave 20s ease-in-out infinite;
      z-index: -1;
    }

    @keyframes carbonWave {
      0%, 100% {
        background-position: 0% 0%, 0px 0px, 0px 0px, 0px 0px, 0px 0px, 0% 50%, 100% 50%;
      }
      25% {
        background-position: 25% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 25% 75%, 75% 25%;
      }
      50% {
        background-position: 50% 50%, 4px 4px, 4px 4px, 8px 8px, 8px 8px, 50% 100%, 50% 0%;
      }
      75% {
        background-position: 75% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 75% 25%, 25% 75%;
      }
    }

    header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      padding: 15px 20px;
      background: rgba(15, 15, 15, 0.95);
      backdrop-filter: blur(15px);
      border-bottom: 1px solid rgba(172, 233, 255, 0.2);
      box-shadow: 
        0 2px 15px rgba(0, 0, 0, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      position: sticky;
      top: 0;
      z-index: 1000;
    }

    header::before {
      content: "";
      position: absolute;
      inset: 1px;
      background:
        repeating-linear-gradient(45deg,
          transparent 0px,
          rgba(255, 255, 255, 0.02) 1px,
          rgba(255, 255, 255, 0.05) 2px,
          rgba(255, 255, 255, 0.02) 3px,
          transparent 4px,
          transparent 6px);
      pointer-events: none;
      z-index: -1;
    }

    .logo {
      font-size: 24px;
      font-weight: 900;
      color: #ace9ff;
      text-shadow: 0 0 10px rgba(172, 233, 255, 0.5);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .logo span {
      color: #ffffff;
      filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.8));
    }

    nav {
      display: none;
      flex-direction: column;
      gap: 15px;
      width: 100%;
      padding: 10px 0;
    }

    nav.active {
      display: flex;
    }

    nav a {
      text-decoration: none;
      color: #e0f6ff;
      font-weight: 500;
      transition: all 0.3s ease;
      padding: 10px;
      border-radius: 8px;
      text-align: center;
      font-size: 16px;
    }

    nav a:hover {
      color: #ace9ff;
      background: rgba(172, 233, 255, 0.1);
      text-shadow: 0 0 10px rgba(172, 233, 255, 0.5);
    }

    .cta-btn {
      background: rgba(172, 233, 255, 0.1);
      color: #ace9ff;
      border: 1px solid rgba(255, 255, 255, 0.2);
      padding: 10px 20px;
      border-radius: 25px;
      cursor: pointer;
      font-weight: 600;
      font-size: 14px;
      transition: all 0.3s ease;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      touch-action: manipulation;
    }

    .cta-btn:hover {
      background: rgba(172, 233, 255, 0.2);
      transform: translateY(-2px);
      box-shadow:
        0 0 15px rgba(172, 233, 255, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
      border-color: rgba(255, 255, 255, 0.3);
    }

    .cta-btn.primary {
      background: rgba(172, 233, 255, 0.2);
      color: #ffffff;
      box-shadow: 
        0 0 15px rgba(172, 233, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
    }

    .cta-btn.primary:hover {
      background: rgba(172, 233, 255, 0.3);
      box-shadow: 
        0 0 25px rgba(172, 233, 255, 0.5),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
    }

    .cta-btn.secondary {
      background: rgba(0, 0, 0, 0.6);
      color: #ace9ff;
      border: 1px solid rgba(172, 233, 255, 0.3);
    }

    .theme-select {
      padding: 10px 16px;
      border-radius: 25px;
      border: 1px solid rgba(172, 233, 255, 0.2);
      background: rgba(0, 0, 0, 0.6);
      color: #ace9ff;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
      margin-left: 10px;
      font-size: 14px;
    }

    .theme-select:hover {
      background: rgba(172, 233, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.3);
    }

    .hamburger {
      display: none;
      font-size: 24px;
      color: #ace9ff;
      cursor: pointer;
      background: none;
      border: none;
      padding: 10px;
    }

    .hero {
      text-align: center;
      padding: 60px 15px;
      animation: fadeIn 1.2s ease;
      position: relative;
    }

    .hero::before {
      content: "";
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 100%;
      max-width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(172, 233, 255, 0.1) 0%, transparent 70%);
      border-radius: 50%;
      z-index: -1;
      animation: pulseGlow 4s ease-in-out infinite;
    }

    @keyframes pulseGlow {
      0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
      50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
    }

    .badge {
      background: rgba(172, 233, 255, 0.08);
      color: #ace9ff;
      padding: 8px 16px;
      border-radius: 25px;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      margin-bottom: 20px;
      animation: slideDown 0.8s ease;
      border: 1px solid rgba(255, 255, 255, 0.15);
      box-shadow: 
        inset 0 1px 0 rgba(255, 255, 255, 0.1),
        0 0 10px rgba(172, 233, 255, 0.2);
      font-size: 14px;
    }

    .hero h1 {
      font-size: 2.2em;
      font-weight: 900;
      margin: 15px 0;
      color: #ace9ff;
      text-shadow: 0 0 20px rgba(172, 233, 255, 0.6);
      line-height: 1.2;
    }

    .hero h1 span {
      color: #ffffff;
      filter: drop-shadow(0 0 12px rgba(255, 255, 255, 0.8));
    }

    .hero p {
      max-width: 90%;
      margin: 0 auto 30px;
      font-size: 16px;
      color: #a0d5eb;
      line-height: 1.5;
    }

    .button-group {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 15px;
      margin-top: 20px;
    }

    .features {
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding: 40px 15px;
      max-width: 100%;
      margin: 0 auto;
    }

    .feature-box {
      background: rgba(15, 15, 15, 0.95);
      backdrop-filter: blur(15px);
      padding: 20px;
      border-radius: 12px;
      text-align: center;
      animation: fadeInUp 1s ease;
      border: 1px solid rgba(172, 233, 255, 0.2);
      box-shadow:
        0 6px 20px rgba(0, 0, 0, 0.8),
        0 0 0 1px rgba(255, 255, 255, 0.1),
        inset 0 1px 0 rgba(255, 255, 255, 0.1);
      position: relative;
      transition: all 0.3s ease;
    }

    .feature-box::before {
      content: "";
      position: absolute;
      inset: 1px;
      background:
        repeating-linear-gradient(45deg,
          transparent 0px,
          rgba(255, 255, 255, 0.02) 1px,
          rgba(255, 255, 255, 0.05) 2px,
          rgba(255, 255, 255, 0.02) 3px,
          transparent 4px,
          transparent 6px);
      border-radius: 11px;
      pointer-events: none;
      z-index: -1;
    }

    .feature-box:hover {
      transform: translateY(-5px);
      box-shadow:
        0 10px 25px rgba(0, 0, 0, 0.9),
        0 0 20px rgba(172, 233, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.2);
      border-color: rgba(172, 233, 255, 0.4);
    }

    .feature-box h3 {
      margin-bottom: 10px;
      font-size: 1.2em;
      color: #ace9ff;
      text-shadow: 0 0 8px rgba(172, 233, 255, 0.3);
    }

    .feature-box p {
      color: #a0d5eb;
      line-height: 1.5;
      font-size: 14px;
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(-20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideDown {
      from { opacity: 0; transform: translateY(-10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    @media (max-width: 768px) {
      header {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        padding: 10px 15px;
      }

      .hamburger {
        display: block;
      }

      .header-actions {
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 8px;
      }

      .hero h1 {
        font-size: 1.8em;
      }

      .hero p {
        font-size: 14px;
        max-width: 95%;
      }

      .cta-btn {
        width: 100%;
        max-width: 300px;
        padding: 12px;
        font-size: 15px;
        text-align: center;
      }

      .theme-select {
        padding: 8px 12px;
        font-size: 13px;
      }

      .features {
        padding: 30px 10px;
      }

      .feature-box {
        padding: 15px;
      }
    }

    @media (max-width: 480px) {
      .logo {
        font-size: 20px;
      }

      .hero {
        padding: 40px 10px;
      }

      .hero h1 {
        font-size: 1.5em;
      }

      .hero p {
        font-size: 13px;
      }

      .badge {
        font-size: 12px;
        padding: 6px 12px;
      }

      .cta-btn {
        padding: 10px;
        font-size: 14px;
      }

      .theme-select {
        padding: 6px 10px;
        font-size: 12px;
      }

      .feature-box h3 {
        font-size: 1.1em;
      }

      .feature-box p {
        font-size: 13px;
      }
    }

    /* Loading animation */
    .loading-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: #000;
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
      transition: opacity 0.5s ease;
    }

    .loading-spinner {
      width: 40px;
      height: 40px;
      border: 3px solid rgba(172, 233, 255, 0.3);
      border-top: 3px solid #ace9ff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  </style>
</head>
<body>
  <div class="loading-overlay" id="loadingOverlay">
    <div class="loading-spinner"></div>
  </div>

  <header>
    <div class="logo">
      <i class="fas fa-bolt"></i>
      Vertex<span>Z</span>
    </div>
    <button class="hamburger" aria-label="Toggle Menu">
      <i class="fas fa-bars"></i>
    </button>
    <nav>
    </nav>
    <div class="header-actions">
      <button class="cta-btn" onclick="window.open('https://discord.com/invite/hCTCQwPKd3', '_blank')">
        <i class="fab fa-discord"></i>Join Discord
      </button>
      <select class="theme-select" id="themeSelect" aria-label="Select Theme">
        <option value="carbon">Carbon</option>
        <option value="system">System</option>
        <option value="light">Light</option>
        <option value="dark">Dark</option>
      </select>
    </div>
  </header>

  <section class="hero">
    <div class="badge">
      <i class="fas fa-bolt"></i>
      The Ultimate Brainrot Script
    </div>
    <h1>The #1 Script<br />For <span>Steal a Brainrot</span></h1>
    <p>Trusted by thousands. Lightning fast execution. Built for absolute domination. Experience 24/7 uptime with constant updates and premium features.</p>
    <div class="button-group">
      <button class="cta-btn primary" onclick="window.open('https://vertex-z.onrender.com/script', '_blank')">
        <i class="fas fa-download"></i>Get Script
      </button>
      <button class="cta-btn secondary" onclick="document.getElementById('features').scrollIntoView({behavior: 'smooth'})">
        <i class="fas fa-list"></i>View Features
      </button>
      <button class="cta-btn" onclick="window.open('https://discord.gg/hCTCQwPKd3', '_blank')">
        <i class="fab fa-discord"></i>Join Community
      </button>
    </div>
  </section>

  <section class="features" id="features">
    <div class="feature-box">
      <h3><i class="fas fa-sword"></i> OP Performance</h3>
      <p>Auto hit, music player, speed boost, and advanced combat features. Dominate every match with precision and power.</p>
    </div>
    <div class="feature-box">
      <h3><i class="fas fa-lightning-bolt"></i> Instant Execution</h3>
      <p>Lightning-fast script execution with zero delays. Run our optimized code and gain the advantage in seconds.</p>
    </div>
    <div class="feature-box">
      <h3><i class="fas fa-shield-check"></i> Trusted by Thousands</h3>
      <p>Community-approved with thousands of active users. Constantly updated and improved based on user feedback.</p>
    </div>
  </section>

  <script>
    window.addEventListener('load', () => {
      const loadingOverlay = document.getElementById('loadingOverlay');
      setTimeout(() => {
        loadingOverlay.style.opacity = '0';
        setTimeout(() => {
          loadingOverlay.style.display = 'none';
        }, 500);
      }, 800);
    });
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('nav');
    hamburger.addEventListener('click', () => {
      nav.classList.toggle('active');
      hamburger.querySelector('i').classList.toggle('fa-bars');
      hamburger.querySelector('i').classList.toggle('fa-times');
    });
    document.querySelectorAll('nav a').forEach(link => {
      link.addEventListener('click', () => {
        nav.classList.remove('active');
        hamburger.querySelector('i').classList.add('fa-bars');
        hamburger.querySelector('i').classList.remove('fa-times');
      });
    });
    const themeSelect = document.getElementById('themeSelect');

    function applyTheme(theme) {
      const body = document.body;

      body.classList.remove('light', 'dark', 'carbon');

      if (theme === 'light') {
        body.classList.add('light');
        body.style.background = 'linear-gradient(to right, #fff, #fff3f3)';
        body.style.color = '#0f0f0f';
        setMetaThemeColor('#ff4d4f');
      } else if (theme === 'dark') {
        body.classList.add('dark');
        body.style.background = 'linear-gradient(to right, #0f0f0f, #1a1a1a)';
        body.style.color = '#eee';
        setMetaThemeColor('#222222');
      } else if (theme === 'carbon') {
        body.style.background = '';
        body.style.color = '';
        setMetaThemeColor('#ace9ff');
      } else if (theme === 'system') {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (isDark) {
          body.classList.add('dark');
          body.style.background = 'linear-gradient(to right, #0f0f0f, #1a1a1a)';
          body.style.color = '#eee';
          setMetaThemeColor('#222222');
        } else {
          body.classList.add('light');
          body.style.background = 'linear-gradient(to right, #fff, #fff3f3)';
          body.style.color = '#0f0f0f';
          setMetaThemeColor('#ff4d4f');
        }
      }

      localStorage.setItem('themePreference', theme);
    }

    function setMetaThemeColor(color) {
      let meta = document.querySelector('meta[name="theme-color"]');
      if (!meta) {
        meta = document.createElement('meta');
        meta.name = "theme-color";
        document.head.appendChild(meta);
      }
      meta.content = color;
    }

    const savedTheme = localStorage.getItem('themePreference') || 'carbon';
    themeSelect.value = savedTheme;
    applyTheme(savedTheme);

    themeSelect.addEventListener('change', (e) => {
      applyTheme(e.target.value);
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
      if (themeSelect.value === 'system') {
        applyTheme('system');
      }
    });
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
    if (window.innerWidth > 768) {
      window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero');
        if (hero) {
          hero.style.transform = `translateY(${scrolled * 0.1}px)`;
        }
      });
    }
  </script>
</body>
</html>
"""

locked_page = """..."""

script_page = """<!DOCTYPE html>
<html lang="en">
<head>
    <title>Vertex Z Script</title>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
    <link rel="icon" type="image/png" href="favicon.png" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: #000;
            color: #e0f6ff;
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
            -webkit-overflow-scrolling: touch;
        }

        body::before {
            content: "";
            position: fixed;
            inset: 0;
            background:
                linear-gradient(45deg,
                    transparent 0%,
                    rgba(255, 255, 255, 0.02) 25%,
                    rgba(255, 255, 255, 0.05) 50%,
                    rgba(255, 255, 255, 0.02) 75%,
                    transparent 100%),
                repeating-linear-gradient(0deg,
                    rgba(0, 0, 0, 0.8) 0px,
                    rgba(15, 15, 15, 0.9) 1px,
                    rgba(25, 25, 25, 0.8) 2px,
                    rgba(15, 15, 15, 0.9) 3px,
                    rgba(0, 0, 0, 0.8) 4px),
                repeating-linear-gradient(90deg,
                    rgba(0, 0, 0, 0.8) 0px,
                    rgba(15, 15, 15, 0.9) 1px,
                    rgba(25, 25, 25, 0.8) 2px,
                    rgba(15, 15, 15, 0.9) 3px,
                    rgba(0, 0, 0, 0.8) 4px),
                repeating-linear-gradient(45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.08) 1px,
                    rgba(255, 255, 255, 0.15) 2px,
                    rgba(255, 255, 255, 0.08) 3px,
                    transparent 4px,
                    transparent 8px),
                repeating-linear-gradient(-45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.08) 1px,
                    rgba(255, 255, 255, 0.15) 2px,
                    rgba(255, 255, 255, 0.08) 3px,
                    transparent 4px,
                    transparent 8px),
                radial-gradient(circle at 20% 30%, rgba(172, 233, 255, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(172, 233, 255, 0.03) 0%, transparent 50%);
            background-size:
                100% 100%,
                4px 4px,
                4px 4px,
                8px 8px,
                8px 8px,
                400px 400px,
                300px 300px;
            animation: carbonWave 20s ease-in-out infinite;
            z-index: -1;
        }

        @keyframes carbonWave {
            0%, 100% {
                background-position: 0% 0%, 0px 0px, 0px 0px, 0px 0px, 0px 0px, 0% 50%, 100% 50%;
            }
            25% {
                background-position: 25% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 25% 75%, 75% 25%;
            }
            50% {
                background-position: 50% 50%, 4px 4px, 4px 4px, 8px 8px, 8px 8px, 50% 100%, 50% 0%;
            }
            75% {
                background-position: 75% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 75% 25%, 25% 75%;
            }
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(15px);
            border-bottom: 1px solid rgba(172, 233, 255, 0.2);
            box-shadow: 
                0 2px 15px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: sticky;
            top: 0;
            z-index: 1000;
            min-height: 50px;
        }

        .logo {
            font-size: 24px;
            font-weight: 900;
            color: #ace9ff;
            text-shadow: 0 0 10px rgba(172, 233, 255, 0.5);
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1001;
            flex-shrink: 0;
        }

        .logo span {
            color: #ffffff;
            filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.8));
        }

        .container {
            max-width: 900px;
            margin: 60px auto;
            padding: 20px;
            text-align: center;
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 16px;
            border: 1px solid rgba(172, 233, 255, 0.2);
            box-shadow:
                0 8px 25px rgba(0, 0, 0, 0.8),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            position: relative;
            animation: fadeInUp 1s ease;
        }

        .container::before {
            content: "";
            position: absolute;
            inset: 1px;
            background:
                repeating-linear-gradient(45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.02) 1px,
                    rgba(255, 255, 255, 0.05) 2px,
                    rgba(255, 255, 255, 0.02) 3px,
                    transparent 4px,
                    transparent 6px);
            border-radius: 15px;
            pointer-events: none;
            z-index: -1;
        }

        h1 {
            font-size: 2.5em;
            color: #ace9ff;
            margin-bottom: 0.4em;
            text-shadow: 0 0 15px rgba(172, 233, 255, 0.6);
            font-weight: 900;
            line-height: 1.2;
        }

        p {
            font-size: 1.2em;
            margin-bottom: 2em;
            color: #a0d5eb;
            line-height: 1.5;
            max-width: 90%;
            margin-left: auto;
            margin-right: auto;
        }

        .button {
            background: rgba(172, 233, 255, 0.15);
            color: #ace9ff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 12px 25px;
            margin: 10px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            touch-action: manipulation;
        }

        .button:hover {
            background: rgba(172, 233, 255, 0.25);
            transform: translateY(-3px);
            box-shadow:
                0 0 15px rgba(172, 233, 255, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }

        .button.primary {
            background: rgba(172, 233, 255, 0.25);
            color: #ffffff;
            box-shadow: 
                0 0 12px rgba(172, 233, 255, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
        }

        .button.primary:hover {
            background: rgba(172, 233, 255, 0.35);
            box-shadow: 
                0 0 20px rgba(172, 233, 255, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.3);
        }

        .top-right {
            position: fixed;
            top: 8px;
            right: 8px;
            z-index: 1002;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(172, 233, 255, 0.2);
            padding: 6px 12px;
            border-radius: 18px;
            font-size: 0.85em;
            line-height: 1.2;
            white-space: nowrap;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            max-width: 120px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .reviews-section {
            margin-top: 40px;
            text-align: left;
            max-width: 95%;
            margin-left: auto;
            margin-right: auto;
            animation: fadeInUp 1.2s ease;
        }

        .reviews-title {
            font-size: 1.8em;
            color: #ace9ff;
            margin-bottom: 25px;
            font-weight: 700;
            text-align: center;
            text-shadow: 0 0 12px rgba(172, 233, 255, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .review-item {
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.15);
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            position: relative;
            transition: all 0.3s ease;
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.1),
                0 2px 12px rgba(0, 0, 0, 0.5);
        }

        .review-item::before {
            content: "";
            position: absolute;
            inset: 1px;
            background:
                repeating-linear-gradient(90deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.03) 1px,
                    transparent 2px);
            border-radius: 11px;
            pointer-events: none;
        }

        .review-item:hover {
            transform: translateY(-2px);
            border-color: rgba(172, 233, 255, 0.3);
            box-shadow:
                0 0 12px rgba(172, 233, 255, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.15);
        }

        .review-user {
            font-weight: bold;
            color: #ace9ff;
            margin-bottom: 10px;
            font-size: 1em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .review-user::before {
            content: "👤";
            opacity: 0.7;
        }

        .review-text {
            font-size: 0.95em;
            color: #a0d5eb;
            line-height: 1.5;
            padding-left: 20px;
        }

        .glow-effect {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            max-width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(172, 233, 255, 0.08) 0%, transparent 70%);
            border-radius: 50%;
            z-index: -1;
            animation: pulseGlow 4s ease-in-out infinite;
        }

        @keyframes pulseGlow {
            0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 768px) {
            header {
                padding: 8px 12px;
                min-height: 40px;
            }

            .logo {
                font-size: 20px;
            }

            .container {
                margin: 30px 15px;
                padding: 15px;
            }

            h1 {
                font-size: 2em;
            }

            p {
                font-size: 1em;
                max-width: 95%;
            }

            .button {
                padding: 10px 20px;
                font-size: 0.95em;
                width: 100%;
                max-width: 300px;
                justify-content: center;
            }

            .top-right {
                top: 6px;
                right: 6px;
                padding: 5px 10px;
                font-size: 0.8em;
                border-radius: 16px;
                max-width: 100px;
            }

            .reviews-title {
                font-size: 1.5em;
            }

            .reviews-section {
                margin-top: 30px;
            }

            .review-item {
                padding: 12px;
                margin-bottom: 12px;
            }

            .review-user {
                font-size: 0.95em;
            }

            .review-text {
                font-size: 0.9em;
                padding-left: 15px;
            }

            .glow-effect {
                width: 100%;
                max-width: 400px;
                height: 400px;
            }
        }

        @media (max-width: 480px) {
            h1 {
                font-size: 1.8em;
            }

            p {
                font-size: 0.9em;
            }

            .button {
                padding: 8px 15px;
                font-size: 0.9em;
            }

            .top-right {
                padding: 4px 8px;
                font-size: 0.75em;
                border-radius: 14px;
                max-width: 90px;
            }

            .reviews-title {
                font-size: 1.3em;
            }

            .review-user {
                font-size: 0.9em;
            }

            .review-text {
                font-size: 0.85em;
            }
        }

        #maintenanceOverlay {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.95);
            color: #ace9ff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            font-size: 1.5em;
            text-align: center;
            padding: 15px;
            user-select: none;
            backdrop-filter: blur(10px);
        }

        body.no-scroll {
            overflow: hidden;
        }

        .success-message {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(172, 233, 255, 0.3);
            border-radius: 12px;
            padding: 20px;
            color: #ace9ff;
            font-size: 1.1em;
            z-index: 1000;
            box-shadow: 
                0 0 25px rgba(172, 233, 255, 0.3),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            animation: successPop 0.3s ease;
            max-width: 90%;
            text-align: center;
        }

        @keyframes successPop {
            0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
        }
    </style>
</head>
<body>
    <header>
        <div class="logo">
            <i class="fas fa-bolt"></i>
            Vertex<span>Z</span>
        </div>
    </header>

    <div class="glow-effect"></div>

    <a href="/" class="button top-right">
        <i class="fas fa-arrow-left"></i>
        Go Back
    </a>

    <div class="container">
        <h1><i class="fas fa-bolt"></i> Vertex Z Script</h1>
        <p>The #1 Roblox script for Steal a Brainrot. Trusted by thousands, powerful performance, and optimized for absolute domination. Experience premium features with zero compromises.</p>

        <button class="button primary" onclick="copyScript()">
            <i class="fas fa-download"></i>
            Get Script
        </button>

        <div class="reviews-section" id="reviews">
            <div class="reviews-title">
                <i class="fas fa-comments"></i>
                User Reviews
            </div>
            <div class="review-list" id="reviewContainer"></div>
        </div>
    </div>

    <script>
        const reviews = [
            { user: "Lilbabby87", text: "10/10 best script known to man and it get better and better every update" },
            { user: "manman01901", text: "1of the best script I ever used!" },
            { user: "elitelyex", text: "really recommend, i like to play music while playing." },
            { user: "thegrinch04616", text: "The script is insanely good in sab for a free script! THERES also other games that i have yet to try." },
        ];
        const container = document.getElementById("reviewContainer");
        reviews.forEach((review, index) => {
            const div = document.createElement("div");
            div.className = "review-item";
            div.style.animationDelay = `${index * 0.1}s`;

            const user = document.createElement("div");
            user.className = "review-user";
            user.innerText = review.user;

            const text = document.createElement("div");
            text.className = "review-text";
            text.innerText = review.text;

            div.appendChild(user);
            div.appendChild(text);
            container.appendChild(div);
        });
        function copyScript() {
            const scriptText = `loadstring(game:HttpGet("https://vertex-z.onrender.com/error?key=skidder"))()`;

            if (navigator.clipboard) {
                navigator.clipboard.writeText(scriptText).then(() => {
                    showSuccessMessage('Script copied to clipboard!');
                }).catch(err => {
                    showSuccessMessage('Failed to copy script', true);
                    console.error(err);
                });
            } else {
                const textArea = document.createElement('textarea');
                textArea.value = scriptText;
                textArea.style.position = 'fixed';
                textArea.style.left = '-999999px';
                textArea.style.top = '-999999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();

                try {
                    document.execCommand('copy');
                    showSuccessMessage('Script copied to clipboard!');
                } catch (err) {
                    showSuccessMessage('Failed to copy script', true);
                    console.error(err);
                }

                document.body.removeChild(textArea);
            }
        }

        function showSuccessMessage(message, isError = false) {
            const messageEl = document.createElement('div');
            messageEl.className = 'success-message';
            messageEl.innerHTML = `
                <i class="fas ${isError ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                <span style="margin-left: 8px;">${message}</span>
            `;

            if (isError) {
                messageEl.style.borderColor = 'rgba(255, 77, 79, 0.3)';
                messageEl.style.color = '#ff4d4f';
            }

            document.body.appendChild(messageEl);

            setTimeout(() => {
                messageEl.style.opacity = '0';
                messageEl.style.transform = 'translate(-50%, -50%) scale(0.8)';
                setTimeout(() => {
                    document.body.removeChild(messageEl);
                }, 300);
            }, 2000);
        }

        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        if (window.innerWidth <= 768) {
            document.querySelector('.glow-effect').style.animation = 'none';
            document.body.style.background = '#000';
            document.body.style.backgroundImage = 'none';
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.review-item').forEach(item => {
            observer.observe(item);
        });
    </script>
</body>
</html>
"""
html_panel = """<!DOCTYPE html>
<html>
<head>
    <title>Live Updates Admin</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        body {
            font-family: 'Inter', sans-serif;
            background: #121212;
            color: #fff;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 40px 20px;
            margin: 0;
            min-height: 100vh;
        }
        h1 {
            color: #00ffff;
            margin-bottom: 20px;
            font-size: 2.2rem;
            text-shadow: 0 0 8px #00ffff;
        }
        form {
            display: flex;
            flex-direction: column;
            width: 100%;
            max-width: 700px;
        }
        input[type="password"], textarea {
            padding: 15px 20px;
            margin-bottom: 15px;
            border-radius: 12px;
            border: none;
            font-size: 16px;
            outline: none;
            width: 100%;
            background: #1e1e1e;
            color: #fff;
            box-shadow: inset 0 0 8px #000;
        }
        textarea {
            min-height: 80px;
            resize: vertical;
        }
        button {
            padding: 15px;
            background: linear-gradient(90deg, #00ffff, #00cccc);
            border: none;
            border-radius: 12px;
            color: #000;
            font-weight: bold;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
        }
        button:hover {
            transform: scale(1.05);
            background: linear-gradient(90deg, #00cccc, #00aaaa);
        }
        #adminPanel {
            width: 100%;
            max-width: 700px;
            margin-top: 30px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        #updateForm {
            display: flex;
            flex-direction: column;
        }
        .section {
            background: #1f1f1f;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.1);
        }
        .section h2 {
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.5rem;
            color: #00ffff;
            text-shadow: 0 0 6px #00ffff;
        }
        #updates, #previousMessages {
            max-height: 250px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .update {
            background: #2a2a2a;
            padding: 12px 18px;
            border-radius: 12px;
            word-wrap: break-word;
            box-shadow: 0 0 8px rgba(0, 255, 255, 0.2);
        }
    </style>
</head>
<body>
    <h1>Live Updates Admin</h1>
    <form id="loginForm">
        <input type="password" id="password" placeholder="Enter password" required>
        <button type="submit">Login</button>
    </form>
    <div id="adminPanel" style="display:none;">
        <div class="section">
            <h2>Add New Update</h2>
            <form id="updateForm">
                <textarea id="newUpdate" placeholder="Enter update text..."></textarea>
                <textarea id="newNotification" placeholder="Enter notification text (optional)"></textarea>
                <button type="submit">Add Update</button>
            </form>
        </div>
        <div class="section">
            <h2>Recent Updates</h2>
            <div id="updates"></div>
        </div>
        <div class="section">
            <h2>Previous Messages</h2>
            <div id="previousMessages"></div>
        </div>
    </div>
    <script>
        const loginForm = document.getElementById("loginForm");
        const adminPanel = document.getElementById("adminPanel");
        loginForm.addEventListener("submit", function(e) {
            e.preventDefault();
            if(document.getElementById("password").value === "{{password}}") {
                loginForm.style.display = "none";
                adminPanel.style.display = "flex";
                fetchUpdates();
            } else {
                alert("Incorrect password!");
            }
        });
        async function fetchUpdates() {
            let res = await fetch("/updates.json");
            let data = await res.json();
            const container = document.getElementById("updates");
            const previousContainer = document.getElementById("previousMessages");
            container.innerHTML = "";
            previousContainer.innerHTML = "";
            if (Array.isArray(data) && data.length > 0) {
                data.forEach((u) => {
                    let div = document.createElement("div");
                    div.className = "update";
                    div.textContent = "Update: " + u.message + (u.notification ? " | Notification: " + u.notification : "");
                    container.appendChild(div);
                    let prevDiv = document.createElement("div");
                    prevDiv.className = "update";
                    prevDiv.textContent = "Update: " + u.message + (u.notification ? " | Notification: " + u.notification : "");
                    previousContainer.prepend(prevDiv);
                });
            } else {
                container.innerHTML = "<div class='update'>No updates yet.</div>";
            }
        }
        document.getElementById("updateForm").addEventListener("submit", async (e) => {
            e.preventDefault();
            let msg = document.getElementById("newUpdate").value;
            let notif = document.getElementById("newNotification").value;
            await fetch("/add", { 
                method: "POST", 
                headers: {"Content-Type": "application/json"}, 
                body: JSON.stringify({ message: msg, notification: notif }) 
            });
            document.getElementById("newUpdate").value = "";
            document.getElementById("newNotification").value = "";
            fetchUpdates();
        });
    </script>
</body>
</html>
"""

KEY_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VERTEX Z - Key Redemption</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: #000;
            color: #e0f6ff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 1.5rem;
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(45deg,
                    transparent 0%,
                    rgba(255, 255, 255, 0.02) 25%,
                    rgba(255, 255, 255, 0.05) 50%,
                    rgba(255, 255, 255, 0.02) 75%,
                    transparent 100%),
                repeating-linear-gradient(0deg,
                    rgba(0, 0, 0, 0.8) 0px,
                    rgba(15, 15, 15, 0.9) 1px,
                    rgba(25, 25, 25, 0.8) 2px,
                    rgba(15, 15, 15, 0.9) 3px,
                    rgba(0, 0, 0, 0.8) 4px),
                repeating-linear-gradient(90deg,
                    rgba(0, 0, 0, 0.8) 0px,
                    rgba(15, 15, 15, 0.9) 1px,
                    rgba(25, 25, 25, 0.8) 2px,
                    rgba(15, 15, 15, 0.9) 3px,
                    rgba(0, 0, 0, 0.8) 4px),
                repeating-linear-gradient(45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.08) 1px,
                    rgba(255, 255, 255, 0.15) 2px,
                    rgba(255, 255, 255, 0.08) 3px,
                    transparent 4px,
                    transparent 8px),
                repeating-linear-gradient(-45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.08) 1px,
                    rgba(255, 255, 255, 0.15) 2px,
                    rgba(255, 255, 255, 0.08) 3px,
                    transparent 4px,
                    transparent 8px),
                radial-gradient(circle at 20% 30%, rgba(172, 233, 255, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 70%, rgba(172, 233, 255, 0.03) 0%, transparent 50%);
            background-size:
                100% 100%,
                4px 4px,
                4px 4px,
                8px 8px,
                8px 8px,
                400px 400px,
                300px 300px;
            animation: carbonWave 20s ease-in-out infinite;
            z-index: -1;
        }

        @keyframes carbonWave {
            0%, 100% {
                background-position: 0% 0%, 0px 0px, 0px 0px, 0px 0px, 0px 0px, 0% 50%, 100% 50%;
            }
            25% {
                background-position: 25% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 25% 75%, 75% 25%;
            }
            50% {
                background-position: 50% 50%, 4px 4px, 4px 4px, 8px 8px, 8px 8px, 50% 100%, 50% 0%;
            }
            75% {
                background-position: 75% 25%, 2px 2px, 2px 2px, 4px 4px, 4px 4px, 75% 25%, 25% 75%;
            }
        }

        .container {
            max-width: 600px;
            width: 100%;
            background: rgba(15, 15, 15, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 16px;
            padding: 1.8rem;
            box-shadow:
                0 6px 25px rgba(0, 0, 0, 0.8),
                0 0 0 1px rgba(255, 255, 255, 0.1),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(172, 233, 255, 0.2);
            position: relative;
        }

        .container::before {
            content: "";
            position: absolute;
            inset: 1px;
            background:
                repeating-linear-gradient(45deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.02) 1px,
                    rgba(255, 255, 255, 0.05) 2px,
                    rgba(255, 255, 255, 0.02) 3px,
                    transparent 4px,
                    transparent 6px);
            border-radius: 15px;
            pointer-events: none;
            z-index: -1;
        }

        .header {
            text-align: center;
            margin-bottom: 1.5rem;
        }

        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 1rem;
        }

        .logo-icon {
            height: 70px;
            filter: drop-shadow(0 0 10px rgba(172, 233, 255, 0.3));
        }

        h1 {
            font-size: 1.8rem;
            color: #ace9ff;
            margin-bottom: 0.4rem;
            text-shadow: 0 0 15px rgba(172, 233, 255, 0.5);
        }

        .subtitle {
            font-size: 1rem;
            color: #88c9e0;
        }

        .badges {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            margin: 1.5rem 0;
        }

        .badge {
            background: rgba(172, 233, 255, 0.08);
            padding: 8px 15px;
            border-radius: 25px;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 6px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .badge i {
            color: #ace9ff;
        }

        .key-box {
            background: rgba(0, 0, 0, 0.6);
            padding: 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow:
                inset 0 1px 0 rgba(255, 255, 255, 0.1),
                0 2px 10px rgba(0, 0, 0, 0.5);
            position: relative;
        }

        .key-box::before {
            content: "";
            position: absolute;
            inset: 1px;
            background:
                repeating-linear-gradient(90deg,
                    transparent 0px,
                    rgba(255, 255, 255, 0.03) 1px,
                    transparent 2px);
            border-radius: 11px;
            pointer-events: none;
        }

        .key-label {
            font-size: 1rem;
            color: #88c9e0;
            margin-bottom: 0.8rem;
        }

        .key-value {
            font-family: 'Courier New', monospace;
            font-size: 1.1rem;
            letter-spacing: 1.5px;
            background: rgba(0, 0, 0, 0.8);
            padding: 0.8rem;
            border-radius: 8px;
            margin: 1rem 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #ace9ff;
            word-break: break-word;
            box-shadow:
                inset 0 2px 4px rgba(0, 0, 0, 0.5),
                inset 0 1px 0 rgba(255, 255, 255, 0.1);
            min-height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .copy-btn {
            background: rgba(172, 233, 255, 0.1);
            color: #ace9ff;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 10px 20px;
            border-radius: 25px;
            font-size: 0.9rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.3s ease;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .copy-btn:hover {
            background: rgba(172, 233, 255, 0.2);
            transform: translateY(-2px);
            box-shadow:
                0 0 15px rgba(172, 233, 255, 0.4),
                inset 0 1px 0 rgba(255, 255, 255, 0.2);
            border-color: rgba(255, 255, 255, 0.3);
        }

        .copy-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .copy-btn:disabled:hover {
            background: rgba(172, 233, 255, 0.1);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }

        .tips {
            background: rgba(172, 233, 255, 0.05);
            padding: 1rem;
            border-radius: 12px;
            margin-top: 1.5rem;
            border-left: 3px solid #ace9ff;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .tip-title {
            color: #ace9ff;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 1rem;
        }

        .tip-content {
            color: #a0d5eb;
            font-size: 0.9rem;
            line-height: 1.5;
        }

        .footer {
            margin-top: 2rem;
            text-align: center;
            color: #5f9db9;
            font-size: 0.8rem;
        }

        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-top: 10px;
        }

        .status-pending {
            background: rgba(255, 193, 7, 0.1);
            color: #ffc107;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }

        .status-success {
            background: rgba(40, 167, 69, 0.1);
            color: #28a745;
            border: 1px solid rgba(40, 167, 69, 0.3);
        }

        .status-error {
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
            border: 1px solid rgba(220, 53, 69, 0.3);
        }

        .expiry-info {
            margin-top: 10px;
            font-size: 0.8rem;
            color: #88c9e0;
        }

        /* Loading animation */
        .loading-dots {
            display: inline-block;
            position: relative;
            width: 80px;
            height: 20px;
        }

        .loading-dots div {
            position: absolute;
            top: 8px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #ace9ff;
            animation-timing-function: cubic-bezier(0, 1, 1, 0);
        }

        .loading-dots div:nth-child(1) {
            left: 8px;
            animation: loading-dots1 0.6s infinite;
        }

        .loading-dots div:nth-child(2) {
            left: 8px;
            animation: loading-dots2 0.6s infinite;
        }

        .loading-dots div:nth-child(3) {
            left: 32px;
            animation: loading-dots2 0.6s infinite;
        }

        .loading-dots div:nth-child(4) {
            left: 56px;
            animation: loading-dots3 0.6s infinite;
        }

        @keyframes loading-dots1 {
            0% { transform: scale(0); }
            100% { transform: scale(1); }
        }

        @keyframes loading-dots3 {
            0% { transform: scale(1); }
            100% { transform: scale(0); }
        }

        @keyframes loading-dots2 {
            0% { transform: translate(0, 0); }
            100% { transform: translate(24px, 0); }
        }

        /* Mobile tweaks */
        @media (max-width: 600px) {
            body {
                padding: 1rem;
            }

            .container {
                padding: 1.2rem;
                border-radius: 12px;
            }

            h1 {
                font-size: 1.5rem;
            }

            .subtitle {
                font-size: 0.9rem;
            }

            .badge {
                font-size: 0.8rem;
                padding: 6px 12px;
            }

            .key-value {
                font-size: 1rem;
                padding: 0.6rem;
            }
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="header">
            <div class="logo-container">
                <img src="https://raw.githubusercontent.com/prototbh/TEMP/refs/heads/main/image_2025-09-17_205022119-removebg-preview.png"
                    alt="VERTEX Z Logo" class="logo-icon">
            </div>
            <h1>Key Redemption</h1>
            <p class="subtitle">Your exclusive access key is ready</p>
        </div>

        <div class="badges">
            <div class="badge"><i class="fas fa-shield-alt"></i><span>100% Secure</span></div>
            <div class="badge"><i class="fas fa-key"></i><span id="keyStatus">Validating...</span></div>
            <div class="badge"><i class="fas fa-lock"></i><span>Encrypted Connection</span></div>
        </div>

        <div class="key-box">
            <div class="key-label">Your VERTEX Z Access Key</div>
            <div class="key-value" id="keyValue">
                <div class="loading-dots">
                    <div></div>
                    <div></div>
                    <div></div>
                    <div></div>
                </div>
            </div>
            <button class="copy-btn" id="copyButton" disabled><i class="far fa-copy"></i> <span id="copyText">Copy Key</span></button>
            <div class="expiry-info" id="expiryInfo" style="display: none;"></div>
            <div class="status-indicator status-pending" id="validationStatus">
                <i class="fas fa-sync-alt fa-spin"></i> Validating cookies...
            </div>
        </div>

        <div class="tips">
            <h3 class="tip-title"><i class="fas fa-exclamation-circle"></i> Security Tip</h3>
            <p class="tip-content">Never share your key publicly. Treat it like a password. Store it in a secure location and only use it on official VERTEX Z platforms.</p>
        </div>

        <div class="footer">
            <p>VERTEX Z &copy; 2025. All rights reserved. | Secure key redemption system</p>
        </div>
    </div>

    <script>
        async function validateAndGetKey() {
            try {
                document.getElementById('validationStatus').innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Checking cookies...';

                const response = await fetch('/rk');
                const data = await response.json();

                if (data.success) {
                    document.getElementById('keyValue').innerHTML = data.key;
                    document.getElementById('keyStatus').textContent = 'Key Generated';
                    document.getElementById('copyButton').disabled = false;
                    document.getElementById('validationStatus').className = 'status-indicator status-success';
                    document.getElementById('validationStatus').innerHTML = '<i class="fas fa-check-circle"></i> Validation successful!';
                    if (data.expiry) {
                        document.getElementById('expiryInfo').style.display = 'block';
                        document.getElementById('expiryInfo').textContent = `Expires: ${data.expiry}`;
                    }

                    setTimeout(() => {
                        document.cookie = "linkvt=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                        document.cookie = "linkvt12_ck=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
                        document.cookie = "linkvt6_ck=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

                        const statusEl = document.getElementById('validationStatus');
                        statusEl.className = 'status-indicator status-pending';
                        statusEl.innerHTML = '<i class="fas fa-info-circle"></i> Cookies cleared for security';
                    }, 60000); 

                } else {
                    document.getElementById('keyValue').innerHTML = 'Please complete key system';
                    document.getElementById('keyStatus').textContent = 'Validation Failed';
                    document.getElementById('validationStatus').className = 'status-indicator status-error';
                    document.getElementById('validationStatus').innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${data.error || 'Validation failed'}`;
                }
            } catch (error) {
                document.getElementById('keyValue').innerHTML = 'Please complete key system';
                document.getElementById('keyStatus').textContent = 'Connection Error';
                document.getElementById('validationStatus').className = 'status-indicator status-error';
                document.getElementById('validationStatus').innerHTML = '<i class="fas fa-exclamation-triangle"></i> Network error. Please try again.';
            }
        }

        document.getElementById('copyButton').addEventListener('click', function () {
            const keyText = document.getElementById('keyValue').textContent;
            const textarea = document.createElement('textarea');
            textarea.value = keyText;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);

            const copyTextEl = document.getElementById('copyText');
            const originalText = copyTextEl.textContent;
            copyTextEl.textContent = 'Copied!';
            this.innerHTML = '<i class="fas fa-check"></i> Copied!';

            setTimeout(() => {
                copyTextEl.textContent = originalText;
                this.innerHTML = '<i class="far fa-copy"></i> Copy Key';
            }, 2000);
        });

        document.addEventListener('DOMContentLoaded', validateAndGetKey);
    </script>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(home_page)

def is_executor():
    user_agent = request.headers.get("User-Agent", "").lower()
    executor_keywords = ["synapse", "roblox", "krnl", "fluxus", "executor", "delta"]
    return any(exec in user_agent for exec in executor_keywords)

@app.route("/script")
def execute():
    return render_template_string(script_page)

executed_keys = {}

@app.route("/track", methods=["POST"])
def track():
    key = request.form.get("key", "")
    executed_keys[key] = time.time()
    return "Tracked", 200

@app.route("/error")
def error():
    if request.args.get("key") == "skidder":
        return send_file(
            "script.txt",
            mimetype="text/plain",
            as_attachment=False
        )
    return "Error page has been deleted or moved", 403

ADMIN_PASSWORD = "admin21"


@app.route("/S-m-e")
def admin_panel():
    return render_template_string(html_panel, password=ADMIN_PASSWORD)


updates = []


@app.route("/updates.json", methods=["GET"])
def get_updates_json():
    if updates:
        return jsonify(updates[-1])
    return jsonify({"message": "", "notification": ""})


@app.route("/add", methods=["POST"])
def add_update():
    data = request.get_json()
    update = {"message": data.get("message", "")}
    notif = data.get("notification", "")
    if notif.strip():
        update["notification"] = notif
    updates.append(update)
    return jsonify({"success": True})


@app.route("/lvt12")
def linkvt12_redirect():
    referer = request.referrer or request.headers.get("Referer", "")
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    print(
        f"[REFERER LOG] /lvt12 - Referer: {referer if referer else 'None'} - IP: {ip_address}"
    )
    print(f"[DEBUG] Full headers: {dict(request.headers)}")
    print(f"[DEBUG] Is secure: {request.is_secure}")

    if referer and (
        "lootdest.org" in referer.lower()
        or "lootdest" in referer.lower()
        or "loot-link.com" in referer.lower()
    ):
        redirect_url = "https://loot-link.com/s?bFIfmm7X"

        resp = redirect(redirect_url, code=302)
        resp.set_cookie(
            "linkvt12_ck",
            secrets.token_hex(16),
            secure=request.is_secure,
            httponly=False,
            samesite="Lax",
            path="/",
        )
        return resp
    else:
        asyncio.run_coroutine_threadsafe(
            send_security_alert(ip_address, request.user_agent.string, referer),
            bot.loop,
        )
        abort(404)


@app.route("/lvt6")
def linkvt6_redirect():
    referer = request.referrer or request.headers.get("Referer", "")
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    print(
        f"[REFERER LOG] /lvt6 - Referer: {referer if referer else 'None'} - IP: {ip_address}"
    )
    print(f"[DEBUG] Full headers: {dict(request.headers)}")
    print(f"[DEBUG] Is secure: {request.is_secure}")

    if referer and (
        "lootdest.org" in referer.lower()
        or "lootdest" in referer.lower()
        or "loot-link.com" in referer.lower()
    ):
        redirect_url = "https://loot-link.com/s?A5LWQm6f"

        resp = redirect(redirect_url, code=302)
        resp.set_cookie(
            "linkvt6_ck",
            secrets.token_hex(16),
            secure=request.is_secure,
            httponly=False,
            samesite="Lax",
            path="/",
        )
        return resp
    else:
        asyncio.run_coroutine_threadsafe(
            send_security_alert(ip_address, request.user_agent.string, referer),
            bot.loop,
        )
        abort(404)


@app.route("/lvt")
def check_referrer_lvtfinal():
    referer = request.referrer or request.headers.get("Referer", "")
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.user_agent.string
    print(
        f"[REFERER LOG] /lvt - Referer: {referer if referer else 'None'} - IP: {ip_address}"
    )
    print(f"[DEBUG] Full headers: {dict(request.headers)}")
    print(f"[DEBUG] Is secure: {request.is_secure}")

    if referer and (
        "lootdest.org" in referer.lower()
        or "lootdest" in referer.lower()
        or "loot-link.com" in referer.lower()
    ):
        resp = make_response(KEY_PAGE)
        resp.set_cookie(
            "linkvt",
            "883uhdhjfdhdhsjkej3j400;'*(*(*$&#*@JHFGDS8JSHY1$",
            secure=request.is_secure,
            httponly=False,
            samesite="Lax",
            path="/",
        )
        return resp
    else:
        asyncio.run_coroutine_threadsafe(
            send_security_alert(ip_address, user_agent, referer), bot.loop
        )
        abort(404)


@app.route("/rk")
def validate_cookies_and_generate_key():
    cookies = request.cookies
    cookie_count = len(cookies)
    if cookie_count != 3:
        return jsonify({"success": False, "error": "Invalid cookie count"})
    linkvt12_cookie = cookies.get("linkvt12_ck")
    linkvt6_cookie = cookies.get("linkvt6_ck")

    if not linkvt12_cookie or not linkvt6_cookie:
        return jsonify({"success": False, "error": "Missing required cookies"})
    if len(linkvt12_cookie) != 32 or len(linkvt6_cookie) != 32:
        return jsonify({"success": False, "error": "Invalid cookie format"})

    try:
        int(linkvt12_cookie, 16)
        int(linkvt6_cookie, 16)
    except ValueError:
        return jsonify({"success": False, "error": "Invalid cookie content"})
    linkvt_cookie = cookies.get("linkvt")
    expected_linkvt_value = "883uhdhjfdhdhsjkej3j400;'*(*(*$&#*@JHFGDS8JSHY1$"

    if linkvt_cookie != expected_linkvt_value:
        return jsonify({"success": False, "error": "Invalid main cookie value"})
    new_key = generate_random_key()

    import pytz
    from datetime import datetime, timedelta

    est = pytz.timezone("US/Eastern")
    expiry_time = datetime.now(est) + timedelta(hours=24)
    expiry_timestamp = expiry_time.strftime("%Y-%m-%d %H:%M:%S EST")
    lua_content = read_keys_file()
    if lua_content is None:
        return jsonify({"success": False, "error": "Error reading keys file"})
    try:
        start_idx = lua_content.find("tempKeys = {")
        if start_idx == -1:
            return jsonify({"success": False, "error": "Temp keys section not found"})
        start_bracket = lua_content.find("{", start_idx) + 1
        end_bracket = lua_content.find("}", start_bracket)
        temp_keys_section = lua_content[start_bracket:end_bracket].strip()
        new_entry = f'\n    ["{new_key}"] = "{expiry_timestamp}",'

        if temp_keys_section and not temp_keys_section.isspace():
            updated_temp_keys = temp_keys_section + new_entry
        else:
            updated_temp_keys = new_entry.lstrip()
        updated_content = (
            lua_content[:start_bracket] + updated_temp_keys + lua_content[end_bracket:]
        )
        if write_keys_file(updated_content):
            return jsonify(
                {"success": True, "key": new_key, "expiry": expiry_timestamp}
            )
        else:
            return jsonify({"success": False, "error": "Error writing keys file"})

    except Exception as e:
        print(f"Error updating temp keys: {str(e)}")
        return jsonify({"success": False, "error": "Error updating keys"})


def check_expired_keys():
    while True:
        try:
            lua_content = read_keys_file()
            if lua_content is not None:
                start_idx = lua_content.find("tempKeys = {")
                if start_idx != -1:
                    start_bracket = lua_content.find("{", start_idx) + 1
                    end_bracket = lua_content.find("}", start_bracket)
                    temp_keys_section = lua_content[start_bracket:end_bracket]
                    lines = temp_keys_section.split("\n")
                    valid_entries = []

                    for line in lines:
                        line = line.strip()
                        if line.startswith('["') and '"] = "' in line:
                            try:
                                key_end = line.find('"] = "')
                                key = line[2:key_end]
                                expiry_str = line[key_end + 6 : -2]
                                from datetime import datetime
                                import pytz

                                est = pytz.timezone("US/Eastern")
                                expiry_time = datetime.strptime(
                                    expiry_str, "%Y-%m-%d %H:%M:%S EST"
                                )
                                expiry_time = est.localize(expiry_time)

                                current_time = datetime.now(est)
                                if current_time < expiry_time:
                                    valid_entries.append(line)

                            except Exception as e:
                                print(f"Error parsing key entry: {e}")
                                valid_entries.append(line)
                    new_temp_keys = (
                        "\n" + "\n".join(valid_entries) + "\n" if valid_entries else ""
                    )
                    if len(valid_entries) != len(lines) - (
                        2 if temp_keys_section.strip() else 0
                    ):
                        updated_content = (
                            lua_content[:start_bracket]
                            + new_temp_keys
                            + lua_content[end_bracket:]
                        )
                        write_keys_file(updated_content)
                        print(
                            f"Removed expired keys. {len(valid_entries)} keys remaining."
                        )

        except Exception as e:
            print(f"Error in expired keys check: {e}")

        time.sleep(5)


def start_key_checker():
    key_checker_thread = threading.Thread(target=check_expired_keys)
    key_checker_thread.daemon = True
    key_checker_thread.start()


@app.route("/43hfndsjdf74093oidjfgh7348wkeys.lua")
def serve_encrypted_keys():
    keys_file_path = ensure_keys_file()

    try:
        with open(keys_file_path, "rb") as f:
            encrypted_content = f.read()
        return (
            encrypted_content,
            200,
            {
                "Content-Type": "application/octet-stream",
                "Content-Disposition": "attachment; filename=keys.lua",
            },
        )
    except Exception as e:
        return f"Error reading keys file: {str(e)}", 500


def run_flask():
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    start_key_checker()
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    get_bot_token
    bot.run(niggerbottoken)
