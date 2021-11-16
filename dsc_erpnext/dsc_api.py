import frappe
import requests
import base64
import os
import json
from frappe.utils import get_url_to_form
from urllib.parse import parse_qs, urlparse
from docusign_esign import EnvelopesApi, EnvelopeDefinition, Document, Signer, CarbonCopy, SignHere, Tabs, Recipients, ApiClient, RecipientViewRequest

@frappe.whitelist()
def get_access_code(doctype, docname):
	base_url = "https://account-d.docusign.com/oauth/auth"
	client_id = frappe.db.get_single_value('Docusign Settings','integration_key')
	auth_url = "{0}?response_type=code&state={1}&scope=signature&client_id={2}&redirect_uri={3}".format(base_url,doctype+'|'+docname,client_id,'http://staging.8848digitalerp.com/api/method/dsc_erpnext.dsc_api.auth_login')
	return auth_url
	
@frappe.whitelist()
def auth_login():
	base_url = "https://account-d.docusign.com/oauth/token"

	docusign_settings = frappe.get_single('Docusign Settings')
	client_id = docusign_settings.integration_key
	client_secret_key = docusign_settings.get_password('secret_key')

	auth_code_string = '{0}:{1}'.format(client_id,client_secret_key)
	auth_token = base64.b64encode(auth_code_string.encode())
	parsed_qs = parse_qs(urlparse(frappe.request.url).query)
	code = parsed_qs['code'][0]
	document = parsed_qs['state'][0]
	doctype = document.split('|')[0]
	docname = document.split('|')[1]
	req_headers = {"Authorization":"Basic {0}".format(auth_token.decode('utf-8'))}
	post_data = {'grant_type':'authorization_code','code': code}

	r = requests.post(base_url, data=post_data, headers=req_headers)
	response = r.json()
	
	if not 'error' in response:
		return ("{0}?token={1}".format(get_signing_url(doctype,docname,response['access_token']),response['access_token']))


def get_signing_url(doctype,docname,token):
	#check if access token exists
	# if yes
	#	if valid
	#		continue
	#	else 
	#		redirect to get access code
	#else no
		#redirect to get_access_code

	ds_doc= frappe.get_doc(doctype,docname)
	"""
	Creates envelope
	args -- parameters for the envelope:
	signer_email, signer_name, signer_client_id
	returns an envelope definition
	"""
	args = {
		"signer_email"     : "nirali@ascratech.com",
		"signer_name"      : "Nirali Satapara",
		"client_id"        : frappe.db.get_single_value('Docusign Settings','integration_key'),
		"account_id"       : frappe.db.get_single_value('Docusign Settings','account_id'),
		"base_path"        : "https://demo.docusign.net/restapi",
		"access_token"     : token
	}
	
	#with open(os.path.join('/home/frappe/frappe-bench/sites/site1.local/public/files', "VACCINE.pdf"),'rb') as file:
	with open(os.path.join('/home/ubuntu/frappe-bench/sites/staging.8848digitalerp.com/public/files', "VACCINE.pdf"),'rb') as file:
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
	return_url = get_url_to_form("Digital Signature",ds_doc.name)
	recipient_view_request = RecipientViewRequest(
		authentication_method="email",client_user_id=args['client_id'],
		recipient_id = 1, return_url = return_url,
		user_name = args['signer_name'], email = args['signer_email']
	)
	results = envelope_api.create_recipient_view(args['account_id'],envelope_id,recipient_view_request=recipient_view_request)
	
	temp_file = envelope_api.get_document(
		account_id=args["account_id"],
		document_id=1,
		envelope_id=envelope_id
	)
	#private_file_path = "/home/frappe/frappe-bench/sites/site1.local/private/files/" + frappe.generate_hash("",5) + ".pdf"
	base_path = "/home/ubuntu/frappe-bench/sites/staging.8848digitalerp.com"
	private_file_path = "/private/files/" + frappe.generate_hash("",5) + ".pdf"
	os.rename(temp_file, base_path + private_file_path)
	ds_doc.db_set('signed_document',private_file_path)
	frappe.local.response['type'] = 'redirect'
	frappe.local.response['location'] = results.url
	frappe.db.commit()
	# return results.url

	# return {"envelope_id": envelope_id, "redirect_url": results.url}