from aiohttp import web


def create_app():
    app = web.Application()

    routes = web.RouteTableDef()
    @routes.get('/')
    async def hello(request):
        return web.Response(text="Hello, world")
    

    app.add_routes(routes)
    return app