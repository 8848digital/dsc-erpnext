import requests
import base64
from os import path
from docusign_esign import EnvelopesApi, EnvelopeDefinition, Document, Signer, CarbonCopy, SignHere, Tabs, Recipients, ApiClient, RecipientViewRequest

def get_access_code(request):
	base_url = "https://account-d.docusign.com/oauth/auth"
	client_id = "cd94c959-5b9a-4ac7-bffa-128be6c63639"
	auth_url = "{0}?response_type=code&scope=signature&client_id={1}&redirect_uri={2}".format(base_url,client_id,request.build_absolute_url(reverse('auth_login')))
	return auth_url
	#code_url = "https://account-d.docusign.com/oauth/auth?response_type=code&scope=signature&client_id=cd94c959-5b9a-4ac7-bffa-128be6c63639&&redirect_uri=http://192.168.0.100/"

def auth_login(request):
	base_url = "https://account-d.docusign.com/oauth/token"
	client_id = "cd94c959-5b9a-4ac7-bffa-128be6c63639"
	client_secret_key = "a346d510-cac8-4b54-a14a-5a76c29ed5d0"
	auth_code_string = '{0}:{1}'.format(client_id,client_secret_key)
	auth_token = base64.b64encode(auth_code_string.encode())

	req_headers = {"Authorization":"Basic {0}".format(auth_token.decode('utf-8'))}
	post_data = {'grant_type':'authorization_code','code': request.GET.get('code')}

	r = requests.post(base_url, data=post_data, headers=req_headers)

	response = r.json()

	if not 'error' in response:
		return ("{0}?token={1}".format(reverse('get_signing_url'),response['access_token']))

def get_signing_url():
	"""
	Creates envelope
	args -- parameters for the envelope:
	signer_email, signer_name, signer_client_id
	returns an envelope definition
	"""
	args = {
		"signer_email"     : "nirali@ascratech.com",
		"signer_name"      : "Nirali Satapara",
		"signer_client_id" : "8273d71a-d0fd-4c20-b116-59b001442c9d",
		"client_id"        : "cd94c959-5b9a-4ac7-bffa-128be6c63639",
		"account_id"       : "cb786829-5a13-4001-8128-a06c53ead4c6",
		"base_path"        : "https://demo.docusign.net/restapi",
		"access_token"     : "eyJ0eXAiOiJNVCIsImFsZyI6IlJTMjU2Iiwia2lkIjoiNjgxODVmZjEtNGU1MS00Y2U5LWFmMWMtNjg5ODEyMjAzMzE3In0.AQoAAAABAAUABwCA7cEkb5vZSAgAgC3lMrKb2UgCABrXc4L90CBMsRZZsAFELJ0VAAEAAAAYAAEAAAAFAAAADQAkAAAAY2Q5NGM5NTktNWI5YS00YWM3LWJmZmEtMTI4YmU2YzYzNjM5IgAkAAAAY2Q5NGM5NTktNWI5YS00YWM3LWJmZmEtMTI4YmU2YzYzNjM5MACAgPxXX5vZSDcALxhel0vftE-ZHf5uwbr62A.JFbonC4mZ5yMG3Fl0QwvGJt-XwXkox0E6tBun_sw-wo4AuVPGpcrGEV8xIc9FPB0GL018PPfk0uPbFBgvzp1NLkobAFCFaGxQ0StzOnlM8ywkQTBOLraXxWs29UeFgvOwJPQVgCWc1v-vIFqW_3GEYvhoI85PGHr_BxqwRZ3-HJFkdmCW9Re4g3oF36dRU8H8gsyAMuED4ExyT6eCw49r9gKMmlNpkTxg4oCiNmo6Xp9sR5wpOmVIRg7bg-sskkLu9DJdovM6_TquKvjcITBLnT3JdOAGWlgC2FYFwAD1UVVarG3hR5jLYJWTps7V_CZgXznEwsvoB768hP4WzumNA"
	}
	
	with open(path.join('/home/frappe/frappe-bench/sites/site1.local/public/files', "VACCINE.pdf"),'rb') as file:
		content_bytes = file.read()
	base64_file_content = base64.b64encode(content_bytes).decode('ascii')

	# Create the document model
	document = Document( # create the DocuSign document object
		document_base64 = base64_file_content,
		name = 'Example document', # can be different from actual file name
		file_extension = 'pdf', # many different document types are accepted
		document_id = 1 # a label used to reference the doc
	)
	
	# Create the signer recipient model
	signer = Signer( # The signer
		email = args['signer_email'], name = args['signer_name'],
		recipient_id = "1", routing_order = "1",
		# Setting the client_user_id marks the signer as embedded
		client_user_id = args['client_id']
	)

	# Create a sign_here tab (field on the document)
	sign_here = SignHere( # DocuSign SignHere field/tab
		anchor_string = '/sn1/', anchor_units = 'pixels',
		anchor_y_offset = '10', anchor_x_offset = '20'
	)

	# Add the tabs model (including the sign_here tab) to the signer
	# The Tabs object wants arrays of the different field/tab types
	signer.tabs = Tabs(sign_here_tabs = [sign_here])

	# Next, create the top level envelope definition and populate it.
	envelope_definition = EnvelopeDefinition(
		email_subject = "Please sign this document sent from the Python SDK",
		documents = [document],
		# The Recipients object wants arrays for each recipient type
		recipients = Recipients(signers = [signer]),
		status = "sent" # requests that the envelope be created and sent.
	)
	#return envelope_definition
	api_client = ApiClient()
	api_client.host = args['base_path']
	api_client.set_default_header("Authorization","Bearer " + args['access_token'])

	envelope_api = EnvelopesApi(api_client)
	results = envelope_api.create_envelope(account_id=args['account_id'],envelope_definition=envelope_definition)

	envelope_id = results.envelope_id
	recipient_view_request = RecipientViewRequest(
		authentication_method=None,client_user_id=args['client_id'],
		recipient_id = 1, return_url = "http://192.168.0.100/done",
		user_name = args['signer_name'], email = args['signer_email']
	)
	results = envelope_api.create_recipient_view(args['account_id'],envelope_id,recipient_view_request=recipient_view_request)
	
	return {"envelope_id": envelope_id, "redirect_url": results.url}



	# envelope_args = args["envelope_args"]
	# # Create the envelope request object
	# envelope_definition = cls.make_envelope(envelope_args)

	# # Call Envelopes::create API method
	# # Exceptions will be caught by the calling function
	# api_client = create_api_client(base_path=args["base_path"], access_token=args["access_token"])

	# envelope_api = EnvelopesApi(api_client)
	# results = envelope_api.create_envelope(account_id=args["account_id"], envelope_definition=envelope_definition)

	# envelope_id = results.envelope_id



	# # Create the Recipient View request object
	# recipient_view_request = RecipientViewRequest(
	# 	authentication_method = authentication_method,
	# 	client_user_id = envelope_args['signer_client_id'],
	# 	recipient_id = '1',
	# 	return_url = envelope_args['ds_return_url'],
	# 	user_name = envelope_args['signer_name'], email = envelope_args['signer_email']
	# )


	# # Obtain the recipient_view_url for the signing ceremony
	# # Exceptions will be caught by the calling function
	# results = envelope_api.create_recipient_view(args['account_id'], envelope_id,
	# 	recipient_view_request = recipient_view_request)

	# return {'envelope_id': envelope_id, 'redirect_url': results.url}



	# {
	# "url": "https://demo.docusign.net/Signing/MTRedeem/v1/490a2cc3-xxxx-xxxx-xxxx-e87be7bf44d8?slt=eyJ0eX...GB7oWg"
	# }