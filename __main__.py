import os
from rockband import app

listen = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('PORT', 10000)

if __name__ == '__main__':
      print('starting {}:{}'.format(listen, port))
      app.run(host=listen, port=int(port))

