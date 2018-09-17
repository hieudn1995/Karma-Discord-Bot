import discord
from json import dump, load

class Bot(discord.Client):
    def __init__(self):
        discord.Client.__init__(self)
        self.karma_table = None

    @staticmethod
    def getToken():
        f = open('token.txt', 'r')
        token = f.read().strip()
        f.close()
        return token

    async def on_ready(self):
        print('Connected as:', self.user)

    def load_karma_table(self):
        with open('karma2.json', 'r') as infile:
            self.karma_table = load(infile)
            infile.close()

    def save_karma_table(self):
        with open('karma2.json', 'w') as outfile:
            dump(self.karma_table, outfile)
            outfile.close()

    def karma_lookup(self, word):
        self.load_karma_table()
        if(word in self.karma_table):
            upvotes = self.karma_table[word]['upvotes']
            downvotes = self.karma_table[word]['downvotes']
            net_karma = upvotes - downvotes
            return "{}: {} ({}++/{}--)".format(word, net_karma, upvotes, downvotes)
        else:
            return "{}: 0 (0++/0--)".format(word)

    def addPositiveKarma(self, word, who):
        if(word in self.karma_table):
            #add one point to the upvotes then add one to the user
            self.karma_table[word]['upvotes'] += 1
            if(who in self.karma_table[word]['upvoters']):
                self.karma_table[word]['upvoters'][who] += 1
            else:
                self.karma_table[word]['upvoters'][who] = 1
        else:
            #instantiates new entry in table with all fields
            self.karma_table.update({word: {"upvotes": 1, "downvotes": 0, "upvoters": {who: 1}, "downvoters": {who: 0}}})

    def addNegativeKarma(self, word, who):
        if(word in self.karma_table):
            self.karma_table[word]['downvotes'] += 1
            if(who in self.karma_table[word]['downvoters']):
                self.karma_table[word]['downvoters'][who] += 1
            else:
                self.karma_table[word]['downvoters'][who] = 1
        else:
            self.karma_table.update({word: {"upvotes": 0, "downvotes": 1, "upvoters": {who: 0}, "downvoters": {who: 1}}})

    async def on_message(self, message):
        if(message.content.lower().startswith('!karma')):
            words = message.content.lower().split(' ')
            if(len(words) > 1):
                await self.send_message(message.channel, self.karma_lookup(words[1]))
            else:
                await self.send_message(message.channel, "I can't do that yet")
        else:
            for chunk in message.content.lower().split(' '):
                self.load_karma_table()
                if(chunk.endswith('++') and len(chunk) > 2):
                    word = chunk[:len(chunk)-2]
                    self.addPositiveKarma(word, message.author.display_name)

                if(chunk.endswith('--') and len(chunk) > 2):
                    word = chunk[:len(chunk)-2]
                    self.addNegativeKarma(word, message.author.display_name)
                self.save_karma_table()

