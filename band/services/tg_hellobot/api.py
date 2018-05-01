from band import dome

@dome.expose(role=dome.HANDLER)
async def main(**data):
    if 'message' in data and 'new_chat_member' in data['message']:
        member = data['message']['new_chat_member']
        chat = data['message']['chat']
        name = member['username'] and '@' + \
            member['username'] or member['first_name']

        return {
            'method': 'sendMessage',
            'chat_id': chat['id'],
            'text': 'Привет, {}!\nРасскажи немного о себе с хештегом #me.'.format(name)
        }
