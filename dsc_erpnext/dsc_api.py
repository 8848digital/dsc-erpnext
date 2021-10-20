import requests
from frappe.model.document import Document

# def get_access_code(request):
#   base_url = "https://account-d.docusign.com/oauth/auth"

def make_envelope(args):
	"""
	Creates envelope
	args -- parameters for the envelope:
	signer_email, signer_name, signer_client_id
	returns an envelope definition
	"""
	args = {
	  "signer_email"     : "nirali@ascratech.com",
	  "signer_name"      : "Nirali Satapara"
	  "signer_client_id" : "edc4ba15-ba4a-404f-b95c-5c1bf5cc4b18"
	}

	with open(path.join(demo_docs_path, ds_config.DS_CONFIG['doc_pdf']), "rb") as file:
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
		client_user_id = args['signer_client_id']
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

	return envelope_definition






	envelope_args = args["envelope_args"]
	# Create the envelope request object
	envelope_definition = cls.make_envelope(envelope_args)

	# Call Envelopes::create API method
	# Exceptions will be caught by the calling function
	api_client = create_api_client(base_path=args["base_path"], access_token=args["access_token"])

	envelope_api = EnvelopesApi(api_client)
	results = envelope_api.create_envelope(account_id=args["account_id"], envelope_definition=envelope_definition)

	envelope_id = results.envelope_id



	# Create the Recipient View request object
	recipient_view_request = RecipientViewRequest(
		authentication_method = authentication_method,
		client_user_id = envelope_args['signer_client_id'],
		recipient_id = '1',
		return_url = envelope_args['ds_return_url'],
		user_name = envelope_args['signer_name'], email = envelope_args['signer_email']
	)


	# Obtain the recipient_view_url for the signing ceremony
	# Exceptions will be caught by the calling function
	results = envelope_api.create_recipient_view(args['account_id'], envelope_id,
		recipient_view_request = recipient_view_request)

	return {'envelope_id': envelope_id, 'redirect_url': results.url}



	{
	"url": "https://demo.docusign.net/Signing/MTRedeem/v1/490a2cc3-xxxx-xxxx-xxxx-e87be7bf44d8?slt=eyJ0eX...GB7oWg"
	}