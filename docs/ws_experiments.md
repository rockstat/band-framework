    async def start_ws(loop, reconnect_interval=1, reconnect=True):
        session = aiohttp.ClientSession(loop=loop, **session_params)

        async def dispatch():
            while True:
                msg = await ws.receive()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print('Text: ', msg.data.strip())
                    response = await methods.dispatch(msg.data)
                    if not response.is_notification:
                        await ws.send_json(response)
                    ws.send_json(test_msg)
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    print('Binary: ', msg.data)
                elif msg.type == aiohttp.WSMsgType.PING:
                    ws.pong()
                elif msg.type == aiohttp.WSMsgType.PONG:
                    print('Pong received')
                else:
                    if msg.type == aiohttp.WSMsgType.CLOSE:
                        await ws.close()
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        print('Error during receive %s' % ws.exception())
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        pass
                    break

        # WS Handler
        while True:
            try:
                async with session.ws_connect(option('kernelURL'), ssl=sslcontext, autoclose=False, autoping=True) as ws:
                    logger.info("connected to kernel")
                    await dispatch()
            except Exception as exc:
                logger.error("runner err: %s", exc)

            if reconnect:
                await asyncio.sleep(reconnect_interval)
            else:
                await session.close()
                # await ws.close()
                # loop.stop()
                break




    # loop.add_signal_handler(signal.SIGINT, loop.stop)
    # loop.add_signal_handler(signal.SIGTERM, loop.stop)
    # # loop.create_task(start_client(loop))
    # loop.run_forever()
    # loop.run_until_complete(start_client(loop, **params))
    # loop.run_until_complete(asyncio.sleep(0.250))
    # loop.close()