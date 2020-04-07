from aiohttp import web

def create_app():
    app = web.Application()

    routes = web.RouteTableDef()
    @routes.post('/')
    async def hello(request):
        data = await request.json()
        return web.json_response(data)
    

    app.add_routes(routes)
    return app