Docusign


Go to the Docusign  website, https://admindemo.docusign.com/.

Signin/Signup with your details.

You will get the Account id and Basic path.

Create project you will get Integration key and secret key.

ERPNEXT 


Add this account details in Docusign Settings.

The Digital Signature Document should include a Sales Invoice or Purchase Order and an assigned role.

Add this {host}/api/method/dsc_erpnext.dsc_api.auth_login in redirect url of Docusign project.

Upon submitting your Sales Invoice or Purchase Order, your Digital Signature Document will appear correspondingly on the DSC Sales Invoice or DSC Purchase Order.
You need to open DSC Sales Invoice or DSC Purchase and click on the appropriate action. 

You will then be redirected to Docusign, where you will need to drag and drop the signature.

If you want add second signaure again a click on action.

