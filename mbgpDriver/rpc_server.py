__author__ = 'milad'


from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import myDB
# Restrict to a particular path.


def parseRoutes():
    p=myDB.RouteParser('../Datasets/routes/CN/all.txt')
    p.startParsing()
    return p.getRouteManager()

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()


x=parseRoutes()
#
def adder_function(x,y):
    return x + y
server.register_function(adder_function, 'add')

# Register an instance; all the methods of the instance are
# published as XML-RPC methods (in this case, just 'div').

server.register_instance(x)

# Run the server's main loop
print 'Server Started'
server.serve_forever()
