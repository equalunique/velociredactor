from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import os

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
server = SimpleXMLRPCServer(("localhost", 8000),
                            requestHandler=RequestHandler)
server.register_introspection_functions()

# Register an instance; all the methods of the instance are
# published as XML-RPC methods.
class MyFuncs: 
    def load_template(x, nosp_tmpl_abs):
	response = "Response"
	# Attempt to load template
	if os.path.isfile(nosp_tmpl_abs):
		response = "\n".join([response, "Verified: %s" % nosp_tmpl_abs])
	else:
		response = "\n".join([response, "Invalid file: %s" % nosp_tmpl_abs])
	# Assign values for template
	if 1 == 1:
		response = "\n".join([response, "Template Registered"])
	else:
		response = "\n".join([response, ""])
	#Send final response
	return response
    def load_png(x, nosp_tpng_abs):
	response = "Response"
	# Attempt to load PNG
	if os.path.isfile(nosp_tpng_abs):
		response = "\n".join([response, "Verified: %s" % nosp_tpng_abs])
	else:
		response = "\n".join([response, "Invalid file: %s" % nosp_tpng_abs])
	# Assign values for PNG
	if 1 == 1:
		response = "\n".join([response, "PNG Registered"])
	else:
		response = "\n".join([response, ""])
	#Send final response
	return response 
    def apply_deskew(x):
	response = "Response"
	# Attempting to perform deskew
	if 1 == 1:
		response = "\n".join([response, "Applied Deskew"])
	else:
		response = "\n".join([response, ""])
	#Send final response
	return response 
    def apply_redactions(x):
	response = "Response"
	# Attempting to perform redactions
	if 1 == 1:
		response = "\n".join([response, "Applied Redactions"])
	else:
		response = "\n".join([response, ""])
	#Send final response
	return response 
    def save_png(x):
	response = "Response"
	# Save PNG file
	if 1 == 1:
		response = "\n".join([response, "Saving PNG File"])
	else:
		response = "\n".join([response, ""])
	#Send final response
	return response 
    def close_png(x):
	response = "Response"
	# Close PNG file
	if 1 == 1:
		response = "\n".join([response, "Closing PNG File"])
	else:
		response = "\n".join([response, ""])
	#Send final response
	return response 
    def close_template(x):
	response = "Response"
	# Close template file
	if 1 == 1:
		response = "\n".join([response, "Closing Template File"])
	else:
		response = "\n".join([response, ""])
	#Send final response
	return response 
    def quit_gimp(x):
	response = "Response"
	# Quit GIMP
	if 1 == 1:
		response = "\n".join([response, "Quiting GIMP"])
	else:
		response = "\n".join([response, ""])
	#Send final response
	return response 

server.register_instance(MyFuncs())

# Run the server's main loop
server.serve_forever()
