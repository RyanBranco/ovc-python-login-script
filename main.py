import re
import aiohttp

async def ovcLogin(request):
    username = ''
    password = ''
    accessToken = ''
    entitlementsToken = ''
    userId = ''

    request_json = request.get_json()
    if request_json and 'username' in request_json:
        username = request_json['username']
        password = request_json['password']
    else:
        return {'status': 400, 'message': 'No username or password provided'}

    session = aiohttp.ClientSession()
    data = {
        'client_id': 'play-valorant-web-prod',
        'nonce': '1',
        'redirect_uri': 'https://playvalorant.com/opt_in',
        'response_type': 'token id_token',
    }
    await session.post('https://auth.riotgames.com/api/v1/authorization', json=data)

    data = {
        'type': 'auth',
        'username': username,
        'password': password
    }
    async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data) as r:
        data = await r.json()
    print(data)
    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    data = pattern.findall(data['response']['parameters']['uri'])[0]
    access_token = data[0]
    accessToken = access_token
    id_token = data[1]
    expires_in = data[2]

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
        data = await r.json()
    entitlements_token = data['entitlements_token']
    entitlementsToken = entitlements_token

    async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
        data = await r.json()
    user_id = data['sub']
    userId = user_id
    headers['X-Riot-Entitlements-JWT'] = entitlements_token

    await session.close()

    return {'status': 200, 'response': {
        'entitlementsToken': entitlementsToken,
        'accessToken': accessToken,
        'userId': userId
    }}