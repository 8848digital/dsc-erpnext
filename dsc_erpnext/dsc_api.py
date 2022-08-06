import frappe
from frappe.utils import get_url_to_form, now_datetime, get_fullname, get_bench_path, get_site_path, get_request_site_address
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
from urllib.parse import parse_qs, urlparse
from docusign_esign import EnvelopesApi, EnvelopeDefinition,EventNotification, Document, Signer, CarbonCopy, SignHere, Tabs, Recipients, ApiClient, RecipientViewRequest
import requests
import base64
import os
import json

@frappe.whitelist()
def get_access_code(doctype, docname):
	base_url =  "https://account-d.docusign.com/oauth/auth"
	client_id = frappe.db.get_single_value('Docusign Settings','integration_key')
	#redirect_uri = 'http://192.168.0.100/api/method/dsc_erpnext.dsc_api.auth_login'
	redirect_uri = get_request_site_address() +'/api/method/dsc_erpnext.dsc_api.auth_login'
	auth_url = "{0}?response_type=code&state={1}&scope=signature&client_id={2}&redirect_uri={3}".format(base_url, doctype+'|'+docname,client_id, redirect_uri)
	return auth_url
	
@frappe.whitelist()
def auth_login():
	data = get_access_token()
	if data:
		return ("{0}?token={1}".format(get_signing_url(data['doctype'],data['docname'],data['access_token'],data['code']),data['access_token']))
	
def get_access_token():
	try:
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
			return {'access_token': response['access_token'],'doctype': doctype,'docname': docname, 'code': code }
	except Exception as e:
		frappe.logger("docusign").exception(e)

def get_signing_url(doctype,docname,token,code):
	try:
		ds_doc = frappe.get_doc(doctype,docname)
		ds_doc.code = code
		args = {
			"signer_email"     : frappe.session.user if frappe.session.user!= "Administrator" else "nirali@ascratech.com",
			"signer_name"      : get_fullname(frappe.session.user),
			"client_id"        : frappe.db.get_single_value('Docusign Settings','integration_key'),
			"account_id"       : frappe.db.get_single_value('Docusign Settings','account_id'),
			"base_path"        : frappe.db.get_single_value('Docusign Settings','base_path'),
			"access_token"     : token
		}
		bench_path = get_bench_path()
		site_path = get_site_path().replace(".", "/sites",1)
		base_path = bench_path + site_path
		output = ""

		if ds_doc.documents:
			signed_doc = ""
			for i, document in enumerate(ds_doc.documents):
				if document.document and i + 1 ==  len(ds_doc.documents):
					signed_doc = document.document
					path = base_path + signed_doc
					with open(path,'rb') as file:
						output = file.read()
				else:
					html = frappe.get_print(ds_doc.document_type, ds_doc.document, ds_doc.print_format)
					output = get_pdf(html)
		else:
			html = frappe.get_print(ds_doc.document_type, ds_doc.document, ds_doc.print_format)
			output = get_pdf(html)

		base64_file_content = base64.b64encode(output).decode('ascii')

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
		#return_url = "http://192.168.0.100/api/method/dsc_erpnext.dsc_api.get_signed_document?doctype=" + ds_doc.doctype+"&docname=" + ds_doc.name
		return_url = get_request_site_address() + "/api/method/dsc_erpnext.dsc_api.get_signed_document?doctype=" + ds_doc.doctype+"&docname=" + ds_doc.name
		recipient_view_request = RecipientViewRequest(
			authentication_method="email",client_user_id=args['client_id'],
			recipient_id = 1, return_url = return_url,
			user_name = args['signer_name'], email = args['signer_email']
		)
		
		results = envelope_api.create_recipient_view(args['account_id'],envelope_id,recipient_view_request=recipient_view_request)

		ds_doc.append("documents",{
			'docusign_envelope_id': envelope_id,
		})
		ds_doc.save()
		frappe.db.set_value(ds_doc.document_type,ds_doc.document,'dsc_status',ds_doc.workflow_state)

		frappe.local.response['type'] = 'redirect'
		frappe.local.response['location'] = results.url
		frappe.db.commit()
	except Exception as e:
		frappe.logger("docusign").exception(e)
	
@frappe.whitelist()
def get_signed_document(doctype,docname): 
	try:
		ds_doc = frappe.get_doc(doctype ,docname)
		base_path = frappe.db.get_single_value('Docusign Settings','base_path')
		account_id = frappe.db.get_single_value('Docusign Settings','account_id')
		bench_path = get_bench_path()
		site_path = get_site_path().replace(".", "/sites",1)
		base_path_ = bench_path + site_path
		file_name = frappe.generate_hash("",5) + ".pdf"
		cert_file_name = "cert_" + file_name

		if ds_doc.documents:
			docusign_settings = frappe.get_single('Docusign Settings')
			client_id = docusign_settings.integration_key
			client_secret_key = docusign_settings.get_password('secret_key')
			auth_code_string = '{0}:{1}'.format(client_id,client_secret_key)
			auth_token = base64.b64encode(auth_code_string.encode())

			# Generate Authentication token from authorization code
			base_url = "https://account-d.docusign.com/oauth/token"
			req_headers = {"Authorization":"Basic {0}".format(auth_token.decode('utf-8'))}
			post_data = {'grant_type':'authorization_code','code': ds_doc.code}

			for document in ds_doc.documents:
				if not document.document and document.docusign_envelope_id:
					r = requests.post(base_url, data=post_data, headers=req_headers)
					response = r.json()

					if not 'error' in response:
						access_token = response['access_token']
					
					# Envelope Status check API
					url = base_path + "/v2.1/accounts/"+ account_id +"/envelopes/" + document.docusign_envelope_id
					headers = {'Authorization': 'Bearer '+ access_token}
					r = requests.get(url,headers=headers)
					response = r.json()

					if r.status_code == 200 and response['status']=="completed":
						# certificate API
						cert_url = base_path + "/v2.1/accounts/"+ account_id  + response['certificateUri']
						certificate_response = requests.get(cert_url,headers=headers)
						cert_file_path = "/private/files/" + cert_file_name
						cert_file = open(base_path_ + cert_file_path, "wb")
						cert_file.write(certificate_response.content)
						cert_file.close()
						save_file(fname=cert_file_name, content=base64.b64encode(certificate_response.content),dt=ds_doc.doctype, dn=ds_doc.name, decode=True, is_private=1)
						
						# Signed document API
						api_client = ApiClient()
						api_client.host = base_path
						api_client.set_default_header("Authorization","Bearer " + access_token)
						envelope_api = EnvelopesApi(api_client)
						temp_file = envelope_api.get_document(account_id,'1',document.docusign_envelope_id)
						private_file_path = "/private/files/" + file_name
						os.rename(temp_file, base_path_ + private_file_path)
						with open(base_path_ + private_file_path, "rb") as pdf_file:
							encoded_string = base64.b64encode(pdf_file.read())
						save_file(fname=file_name, content=encoded_string,dt=ds_doc.doctype, dn=ds_doc.name, decode=True, is_private=1)
						
						document.db_set('document',private_file_path)
						document.db_set('certificate',cert_file_path)
						document.db_set('user', frappe.session.user)
						document.db_set('timestamp',now_datetime())

						ds_doc.db_set('workflow_state',ds_doc.workflow_state.replace('Signing','Completed'))
						ds_doc.db_set('previous_state',ds_doc.workflow_state.replace('Signing','Completed'))
						frappe.db.set_value(ds_doc.document_type,ds_doc.document,'dsc_status',ds_doc.workflow_state)
					else:
						ds_doc.db_set('workflow_state',ds_doc.previous_state)
						frappe.msgprint("Your transaction is incomplete. Please try after sometime")
						
			frappe.local.response['type'] = 'redirect'
			# frappe.local.response['location'] = get_url_to_form("Digital Signature",ds_doc.name)
			frappe.local.response['location'] = get_url_to_form(doctype,ds_doc.name)
			frappe.db.commit()
	except Exception as e:
		frappe.logger("docusign").exception(e)


def dsc_change_status():
	data = frappe.get_all("Digital Signature","name") 
	for row in data:
		doc = frappe.get_doc("Digital Signature",row['name'])
		if "Signing" in doc.workflow_state and doc.workflow_state != doc.previous_state:
			doc.db_set("workflow_state",doc.previous_state)
			frappe.db.set_value(doc.document_type,doc.document,'dsc_status',doc.previous_state)
	frappe.db.commit()

	data = frappe.get_all("DSC Sales Invoice","name") 
	for row in data:
		doc = frappe.get_doc("DSC Sales Invoice",row['name'])
		if "Signing" in doc.workflow_state and doc.workflow_state != doc.previous_state:
			doc.db_set("workflow_state",doc.previous_state)
			frappe.db.set_value(doc.document_type,doc.document,'dsc_status',doc.previous_state)
	frappe.db.commit()

	data = frappe.get_all("DSC Purchase Order","name") 
	for row in data:
		doc = frappe.get_doc("DSC Purchase Order",row['name'])
		if "Signing" in doc.workflow_state and doc.workflow_state != doc.previous_state:
			doc.db_set("workflow_state",doc.previous_state)
			frappe.db.set_value(doc.document_type,doc.document,'dsc_status',doc.previous_state)
	frappe.db.commit()

def validate(self,event):
	if self.document_type and not frappe.db.exists("Custom Field",{'dt':self.document_type,'fieldname':'dsc_status'}):
		status = frappe.new_doc("Custom Field")
		status.dt = self.document_type
		status.label = 'DSC Status'
		status.fieldname = 'dsc_status'
		status.fieldtype = "Data"
		status.allow_on_submit = 1
		status.read_only = 1
		status.no_copy = 1 
		status.save()
	if self.workflow_state:
		self.previous_state = self.workflow_state