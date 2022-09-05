<div align="center">
<a href="https://admindemo.docusign.com/"><img src="https://user-images.githubusercontent.com/49873594/183577549-d4750f7e-b927-4ec0-9cd9-f52e63a65a18.png"></a>
</div>
										
<hr>
<ul>
	<li><h2><a href="#step1">Step 1</a></h2></li>
	<li><h2><a href="#step2">Step 2</a></h2></li>
</ul> 

<div id="step1">
	<h2>Docusign</h2>
Go to the Docusign <a href="https://admindemo.docusign.com/">Website</a>

Signin/Signup with your details.

You will get the Account id and Basic path.

Create project you will get Integration key and secret key.<br><br>
	<img src="https://user-images.githubusercontent.com/49873594/183821469-b14f53f5-6417-44e3-9912-2a3e27bb2786.png" width="50%"><br><br>
</div> 

<div id="step2">
	<h2>ERPNEXT</h2>
Add this account details in Docusign Settings.<br><br>
<img src="https://user-images.githubusercontent.com/49873594/183580378-36e60023-ca35-40ed-bd39-528df9eaa2a8.png" width="50%"><br><br>

The Digital Signature Document should include a Sales Invoice or Purchase Order and an assigned role.<br><br>
<img src="https://user-images.githubusercontent.com/49873594/183580732-2ef4fe23-455c-4756-ad18-3a94c4595685.png" width="50%"><br><br>
Add this {host}/api/method/dsc_erpnext.dsc_api.auth_login in redirect url of Docusign project.<br><br>
	<img src="https://user-images.githubusercontent.com/49873594/183581152-e5e011c5-8ed7-4749-8f8c-b8ccb09a008d.png" width="50%"><br><br>
Upon submitting your Sales Invoice or Purchase Order, your Digital Signature Document will appear correspondingly on the DSC Sales Invoice or DSC Purchase Order.<br><br>
	<img src="https://user-images.githubusercontent.com/49873594/183580849-0109af84-37cd-43a2-8b4a-4bcac4457a3d.png" width="50%"><br><br>
You need to open DSC Sales Invoice or DSC Purchase and click on the appropriate action. <br><br>
<img src="https://user-images.githubusercontent.com/49873594/183581259-39273a75-e9b1-4849-8e8e-350ca4b17242.png" width="50%"><br><br>
You will then be redirected to Docusign, where you will need to drag and drop the signature.<br><br>
<img src="https://user-images.githubusercontent.com/49873594/183581412-220e491e-440e-463a-b6bd-4e07265dfdb0.png" width="50%"><br><br>
If you want add second signaure again a click on action.
</div>
