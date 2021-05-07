from discord.ext import commands
@client.command()
async def ban(ctx,member:discord.Member, * reason = 'Violating the rules') // banning the members 
	await member.ban(reason=reason)
@client.command()
async def kick(ctx,member:discord.Member, * reason = 'Violating the rules') // kicking the members
	await member.kick(reason=reason)

   