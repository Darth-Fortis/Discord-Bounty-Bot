import discord
from discord.ext import commands
from discord.ext import tasks
import json

intents = discord.Intents.all()
intents.members = True

# Create a bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

# Dictionary to store XP levels of users
xp_levels = {}

# List to store bounties
bounties = []

# IDs for specific channels
command_team_channel_id = 1199141420221603862  
log_channel_id = 1216183031417536522  
general_channel_id = 1199121401706201208
status_channel_id = 1234556956602138758

# Function to save XP data to file
def save_xp_data():
    with open('xp_data.json', 'w') as file:
        json.dump(xp_data, file, indent=4, separators=(',', ': '))

# Function to save bounties data to file
def save_bounties_data():
    with open('bounties.json', 'w') as file:
        json.dump(bounties, file, indent=4, separators=(',', ': '))

# Function to update XP data with current server members who have the 'Clan Saxon' role
async def update_xp_data():
    global xp_data

    # Fetch all members of the server
    guild = bot.get_guild(1199105596956364900)
    members = guild.members
    
    # Role ID of the 'Clan Saxon' role
    clan_saxon_role_id = 1199106327474098226
    
    # Iterate through each member and add their ID to xp_data if not already present and they have the 'Clan Saxon' role
    for member in members:
        member_id = str(member.id)
        if member_id not in xp_data and discord.utils.get(member.roles, id = clan_saxon_role_id):
            xp_data[member_id] = {'display_name': member.display_name, 'xp': 0}  # Set initial XP level to 0 for new members    
    # Save updated XP data to file
    save_xp_data()

# Function to load bounties data from file
def load_bounties_data():
    global bounties
    try:
        with open('bounties.json', 'r') as file:
            bounties = json.load(file)
    except FileNotFoundError:
        bounties = []
    except json.decoder.JSONDecodeError:
        bounties = []

def load_xp_data():
    # Load XP data from file
    global xp_data

    try:
        with open('xp_data.json', 'r') as file:
            xp_data = json.load(file)
    except FileNotFoundError:
        xp_data = {}
    except json.decoder.JSONDecodeError:
        xp_data = {}

# Define a task to send a status update message every 15 minutes
@tasks.loop(minutes=15)
async def status_update_task():
    try:
        # Get the channel where the bot will send the message
        channel = bot.get_channel(status_channel_id)
        if channel:
            await channel.send("Test")
    except Exception as e:
        await channel.send(f'An error occurred: {str(e)}')

@bot.event
async def on_ready():
    print('\n[//] Bot is ready. [//]')

    # Load bounties data from file
    load_bounties_data()

    # Load XP data from file
    load_xp_data()

    # Update XP data with current server members
    await update_xp_data()
    print('\n[//] All members updated. [//]')

    # Start the status update task
    status_update_task.start()

    status_channel = bot.get_channel(status_channel_id)
    await status_channel.send('[//] Bot is online. [//]')

# Command to test if the bot receives commands
@bot.command()
async def test(ctx):
    print("\n\t[/] Test command received!")
    await ctx.send("Test command received!") 

#Help command
@bot.command()
async def helps(ctx):
    try:
        if ctx.channel.id != command_team_channel_id:
            await ctx.send('Here are the commands:\n\t /helps = Sends this message.\n\t /level @discord = Shows your XP amount.\n\t /levels = Shows Top 10 people with highest XP.\n')
        else:
            await ctx.send('Here are the commands:\n\t /helps = Sends this message.\n\t /level @discord = Shows your XP amount.\n\t /levels = Shows Top 10 people with highest XP.\n\t /addxp (temp-command) = Adds/removes XP for a user. eg. /addxp @discord 10 (or -10 if removing)\n\t /addbounty = Adds a bounty. eg. /addbounty discord @RR rank place xp \n\t /removebounty = Remove a bounty. eg. /removebounty discord ')
    
    except Exception as e:
        await ctx.send(f'An error occured while executing the commannd: {str(e)}')

# Command to check XP level
@bot.command()
async def level(ctx, user: discord.Member):
    try:
        if str(user.id) in xp_data:
            xp = xp_data[str(user.id)]['xp']
            await ctx.send(f"{user.display_name} has {xp} XP.")
        else:
            await ctx.send(f"{user.display_name} has not earned any XP yet.")
    except Exception as e:
        await ctx.send(f"An error occurred while executing the command: {str(e)}")

# Command to check top XP amounts
@bot.command()
async def levels(ctx):
    try:
        sorted_users = sorted(xp_data.items(), key=lambda x: x[1]['xp'], reverse=True)
        top_users = sorted_users[:10]

        if top_users:
            leaderboard = "\n\t".join(f"{user[1]['display_name']}: {user[1]['xp']} XP" for user in top_users)
            await ctx.send("Top 10 XP amounts:\n\t" + leaderboard)
        else:
            await ctx.send("No users have earned XP yet.")
    except Exception as e:
        await ctx.send(f"An error occurred while executing the command: {str(e)}")

# Command to add XP to a user (temporary command)
@bot.command()
async def addxp(ctx, member: discord.Member, amount: int):
    try:
        if ctx.channel.id != command_team_channel_id:
            return await ctx.send("This command can only be used in the Command Team channel.")

        member_id = str(member.id)
        xp_data[member_id]['xp'] += amount
        save_xp_data()

        await ctx.send(f"{amount} XP added to {member.display_name}. New total: {xp_data[member_id]['xp']} XP.")
    except Exception as e:
        await ctx.send(f"An error occurred while executing the command: {str(e)}")

# Command to add a bounty
@bot.command()
async def addbounty(ctx, person: str, rr: str, rank: str, place: str, xp: int):
    try:
        if ctx.channel.id != command_team_channel_id:
            return await ctx.send("This command can only be used in the Command Team channel.")

        general_channel = bot.get_channel(general_channel_id)
        clan_saxon_mention = f'<@&{1199106327474098226}>'
        
        # Add the bounty message with reactions to the general channel
        bounty_message = await general_channel.send(
            f"{clan_saxon_mention}\n\nBounty for {person} - \nRR: {rr}, \nRank: {rank}, \nPlace: {place}, \nXP: {xp}. \nReact with ✅ to claim, ❌ to cancel (HIGH COMMAND/LEADERS ONLY), ❎ to unclaim.")

        await bounty_message.add_reaction('✅')  # Claim
        await bounty_message.add_reaction('❌')  # Cancel
        await bounty_message.add_reaction('❎')  # Un-Claim

        # Add the bounty to the list
        bounty = {
            'person_id': person,
            'rr': rr,
            'rank': rank,
            'place': place,
            'xp': xp,
            'message_id': bounty_message.id,
            'thread_id': None,
            'claimer': None
        }
        bounties.append(bounty)

        # Save updated bounties data to file
        save_bounties_data()

        # Log the addition of the bounty
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"[+] Bounty added for {person} - RR: {rr}, Rank: {rank}, Place: {place}, XP: {xp}.")

        await ctx.send("Bounty added successfully!")  # Confirmation message
    
    except commands.MissingRequiredArgument:
        await ctx.send("Missing arguments. Please provide all required arguments.")
    except commands.MemberNotFound:
        await ctx.send("Member not found. Please provide a valid member.")
    except commands.BadArgument:
        await ctx.send("Invalid arguments. Please provide valid arguments.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to perform this action.")
    except Exception as e:
        await ctx.send(f"An error occurred while executing the command: {str(e)}")

# Command to remove a bounty
@bot.command()
async def removebounty(ctx, person: str):
    try:
        if ctx.channel.id != command_team_channel_id:
            return await ctx.send("This command can only be used in the Command Team channel.")

        removed_bounties = []
        for bounty in bounties[:]:
            if person == bounty['person_id']:
                removed_bounties.append(bounty)
                bounties.remove(bounty)

        if removed_bounties:
            for bounty in removed_bounties:
                try:
                    general_channel = bot.get_channel(general_channel_id)
                    message = await general_channel.fetch_message(bounty['message_id'])
                    await message.delete(delay=5)
                except discord.NotFound:
                    print(f"Message with ID {bounty['message_id']} not found or already deleted.")
            
            await ctx.send(f"{len(removed_bounties)} bounty/bounties removed for {person}.")

            # Save updated bounties data to file
            save_bounties_data()
            
            # Log the removal of the bounty
            log_channel = bot.get_channel(log_channel_id)
            for bounty in removed_bounties:
                await log_channel.send(f"[-] Bounty removed: {bounty['person_id']} - RR: {bounty['rr']}, Rank: {bounty['rank']}, Place: {bounty['place']}, XP: {bounty['xp']}.")
        else:
            await ctx.send("No bounties found for the specified person.")
    except Exception as e:
        await ctx.send(f"An error occurred while executing the command: {str(e)}")

# Event handler for reaction added
@bot.event
async def on_reaction_add(reaction, user):
    
    high_command_id = 1199105952733986949
    
    try:
        if user == bot.user:
            return

        if str(reaction.emoji) == '✅':
            for bounty in bounties:
                if reaction.message.id == bounty['message_id']:
                    # Set the claimer of the bounty
                    bounty['claimer'] = user.id
                    save_bounties_data()
                    
                    # Send a message confirming the bounty claim and creating a thread
                    thread = await reaction.message.create_thread(name=f"Bounty Claim - {bounty['person_id']}")
                    bounty['thread_id'] = thread.id
                    save_bounties_data()

                    await thread.send(f"Claimed by {user.mention}. Please send 'done' in this thread to verify completion.")

                    # Log the claimed bounty
                    log_channel = bot.get_channel(log_channel_id)
                    await log_channel.send(f"[*] Bounty claimed by: {user.display_name} - RR: {bounty['rr']}, Rank: {bounty['rank']}, Place: {bounty['place']}, XP: {bounty['xp']}.")
                    break
                
                else:
                    print("No bounty found for the reacted message ID.")

        elif str(reaction.emoji) == '❌' and discord.utils.get(user.roles, id = high_command_id ):
            for bounty in bounties:
                if reaction.message.id == bounty['message_id']:
                    await reaction.message.delete()
                    bounties.remove(bounty)
                    save_bounties_data()
                    
                    # Log the cancelled bounty
                    log_channel = bot.get_channel(log_channel_id)
                    await log_channel.send(f"[-] Bounty cancelled by: {user.display_name} - RR: {bounty['rr']}, Rank: {bounty['rank']}, Place: {bounty['place']}, XP: {bounty['xp']}.")
                    break
            else:
                print("No bounty found for the reacted message ID.")
                
        # Check if the reaction is for unclaiming the bounty and the user is the claimer
        elif str(reaction.emoji) == '❎':
            for bounty in bounties:
                if reaction.message.id == bounty['message_id'] and bounty['claimer'] == user.id:
                    bounty['claimer'] = None
                    save_bounties_data()

                    # Remove the thread associated with the bounty
                    try:
                        thread = await reaction.message.guild.fetch_channel(bounty['thread_id'])
                        await thread.delete()
                        bounty['thread_id'] = None
                        save_bounties_data()
                    except Exception as e:
                        print(f"An error occurred while deleting the thread: {e}")
                    
                    # Send a message confirming the unclaimed bounty
                    log_channel = bot.get_channel(log_channel_id)
                    await log_channel.send(f"[+] Bounty unclaimed by: {user.display_name} - RR: {bounty['rr']}, Rank: {bounty['rank']}, Place: {bounty['place']}, XP: {bounty['xp']}.")
                    break
            else:
                print("No bounty found for the reacted message ID.")
    
    except Exception as e:
        print(f"An error occurred in reaction handling: {str(e)}")

# Event handler for message creation and logging
@bot.event
async def on_message(message):
    try:
        if message.author == bot.user:  
            return

        if isinstance(message.channel, discord.Thread):
            thread = message.channel
            for bounty in bounties:
                if thread.name.startswith("Bounty Claim -") and bounty['person_id'] in thread.name:
                    if message.content.lower() == 'done':
                        await message.reply(f"Bounty completed by {message.author.display_name}.")

                        # Retrieve the user who claimed the bounty
                        claimer_id = bounty['claimer']
                        claimer = await bot.fetch_user(claimer_id)
                        if claimer:
                            # Add XP amount to the claimer's XP level
                            xp_data[str(claimer_id)]['xp'] += bounty['xp']
                            save_xp_data()
                            await message.channel.send(f"{bounty['xp']} XP added to {claimer.display_name}. New total: {xp_data[str(claimer_id)]['xp']} XP.")
                        else:
                            await message.channel.send("No one claimed this bounty.")
                        
                        # Remove the completed bounty
                        bounties.remove(bounty)

                        # Logs bounty completion
                        log_channel = bot.get_channel(log_channel_id)
                        await log_channel.send(f"[**] Bounty completed by: {message.author.display_name} - RR: {bounty['rr']}, Rank: {bounty['rank']}, Place: {bounty['place']}, XP: {bounty['xp']}.")

                        save_bounties_data()
                        return
                    else:
                        await message.channel.send("The 'done' message is required for verification.")
                        return

        print(f"\n[M] ({message.author.display_name}), {message.content}")
        await bot.process_commands(message)
                                     
    except Exception as e:
        print(f"An error occurred in message handling: {str(e)}")
        await message.channel.send("An error occurred while processing the message.")

# Event handler to log command invocations
@bot.event
async def on_command(ctx):
    print(f"\n\t[C] ({ctx.message.author.display_name}), {ctx.message.content}") 

# Event handler for when a member joins the server
@bot.event
async def on_member_join(member):
    if not str(member.id) in xp_data:
        xp_data[str(member.id)] = {'display_name': member.display_name, 'xp': 0}
        save_xp_data()
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"[+] {member.display_name} has joined the server.")

# Event handler to log errors encountered during command execution
@bot.event
async def on_command_error(ctx, error):
    print(f"An error occurred while executing the command '{ctx.message.content}': {error}") 
    await ctx.send(f"An error occurred while executing the command: {error}")

# Event handler for when the bot is stopped
@bot.event
async def on_disconnect():
    print('\n[//] Bot is shutting down. [//]')

    # Save bounties data to file
    save_bounties_data()

    # Save XP data to file
    save_xp_data()

    # Stop the status update task
    status_update_task.cancel()

# Run the bot
bot.run('MTIyMDEzMzcxNDM4MjU1NzE4NA.GWuGyW.yi3FJ0m5nIKOFVOXW0CO1H3pMj2cRgG-v3xex4')
