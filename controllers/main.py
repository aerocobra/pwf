# -*- coding: utf-8 -*-
#import email
#import datetime
from openerp import fields
from openerp import http
from openerp.http import request
from openerp import tools
from openerp.tools.translate import _
from openerp.addons.website.controllers.main import Website
from openerp.addons.website_portal.controllers.main import website_account



class website_account(http.Controller):
    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def account(self, **kw):
        partner = request.env.user.partner_id

        # get customer sales rep
        if partner.user_id:
            sales_rep = partner.user_id
        else:
            sales_rep = False
        values = {
            'sales_rep': sales_rep,
            'company': request.website.company_id,
            'user': request.env.user,
            'aut': partner.parent_id
        }

        return request.website.render("website_portal.account", values)

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def details(self, redirect=None, **post):
        partner = request.env['res.users'].browse(request.uid).partner_id
        values = {
            'error': {},
            'error_message': []
        }

        if post:
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                post.update({'zip': post.pop('zipcode', '')})
                if partner.type == "contact":
					#2 update
                    address_fields = {
                        'city': post.pop('city'),
                        'street': post.pop('street'),
                        'street2': post.pop('street2'),
                        'zip': post.pop('zip'),
                        'country_id': post.pop('country_id'),
                        'state_id': post.pop('state_id'),
						'x_strAuthorizationTransport': post.pop('x_strAuthorizationTransport'),
						'x_nAuthorizationTransport': post.pop('x_nAuthorizationTransport'),
						'x_strLicenceEU': post.pop('x_strLicenceEU'),
						'x_strAuthorizationOperator': post.pop('x_strAuthorizationOperator'),
						'x_nEmplyees': post.pop('x_nEmplyees'),
						'email': post.pop('company_email'),
						'phone': post.pop('company_phone'),
						'website': post.pop('company_website'),
						'name': post.pop('company_name')
                    }
                    partner.commercial_partner_id.sudo().write(address_fields)
                partner.sudo().write(post)
				#redirect dice donde hay que ir despues de pulsar el boton Confirmar
                if redirect:
                    return request.redirect(redirect)
                #return request.redirect('/my/home')
                return request.redirect('/')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

		#2 show
        values.update({
			'company_vat': partner.commercial_partner_id.vat,
			'company_name': partner.commercial_partner_id.name,
			'company_website': partner.commercial_partner_id.website,
			'company_email': partner.commercial_partner_id.email,
			'company_phone': partner.commercial_partner_id.phone,
			'x_strAuthorizationTransport': partner.commercial_partner_id.x_strAuthorizationTransport,
			'x_nAuthorizationTransport':  partner.commercial_partner_id.x_nAuthorizationTransport,
			'x_strLicenceEU': partner.commercial_partner_id.x_strLicenceEU,
			'x_strAuthorizationOperator':  partner.commercial_partner_id.x_strAuthorizationOperator,
			'x_nEmplyees': partner.commercial_partner_id.x_nEmplyees,
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
        })

        return request.website.render("website_portal.details", values)

    def details_form_validate(self, data):
        error = dict()
        error_message = []

        mandatory_billing_fields = ["company_name", "company_email", "name", "email", "street", "city", "country_id"]
        optional_billing_fields = ["zipcode",
									"phone",
									"state_id",
									"company_vat",
									"street2",
									"x_strAuthorizationTransport",
									"x_nAuthorizationTransport",
									"x_strLicenceEU",
									"x_strAuthorizationOperator",
									"x_nEmplyees",
									"company_phone",
									"company_website"
									]

        # Validation
        for field_name in mandatory_billing_fields:
            if not data.get(field_name):
                error[field_name] = 'missing'

        # email validation
        if data.get('email') and not tools.single_email_re.match(data.get('email')):
            error["email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        if data.get('company_email') and not tools.single_email_re.match(data.get('company_email')):
            error["company_email"] = 'error'
            error_message.append(_('Invalid Email! Please enter a valid email address.'))

        # vat validation
        if data.get("vat") and hasattr(request.env["res.partner"], "check_vat"):
            if request.website.company_id.vat_check_vies:
                # force full VIES online check
                check_func = request.env["res.partner"].vies_vat_check
            else:
                # quick and partial off-line checksum validation
                check_func = request.env["res.partner"].simple_vat_check
            vat_country, vat_number = request.env["res.partner"]._split_vat(data.get("vat"))
            if not check_func(vat_country, vat_number):  # simple_vat_check
                error["vat"] = 'error'
                error_message.append(_('NIF no válido! Formtato válido: ESA12345678.'))

		# error message for empty required fields
        if [err for err in error.values() if err == 'missing']:
            error_message.append(_('Some required fields are empty.'))

        unknown = [k for k in data.iterkeys() if k not in mandatory_billing_fields + optional_billing_fields]
        if unknown:
            error['common'] = 'Unknown field'
            error_message.append("Unknown field '%s'" % ','.join(unknown))

        # if not error, send a mail 
        if len ( error) == 0 and data.get("email"):
            self.send_mail_note( data.get("email"), data.get('company_name'), data.get('name'))

        if len ( error) == 0:
            self.send_mail_note( 'astic@astic.net', data.get('company_name'), data.get('name'))
            self.send_mail_note( 'igor.kartashov@setir.es', data.get('company_name'), data.get('name'))

        return error, error_message

    def send_mail_note ( self, mail_to, empresa, contacto):
        mail_pool = request.env['mail.mail']

        values={}
        values.update({'subject': 'WEB Portal ASTIC: datos actualizados y/o confirmados'})
        values.update({'email_to': mail_to})
        values.update({'email_from': 'sistemas@astic.net'})
        values.update({'body_html': '<p>Estimado %s:</p> <p>ASTIC le agradece su colaboraci&oacute;n.</p> <p>Los datos de su empresa [%s] han sido actualizados y confirmados.</p> <p>Servicio autom&aacute;tico portal WEB ASTIC. No responda a este correo.</p>' % (contacto, empresa)})
        #values.update({'body': 'partner actualizado' })
		#values.update({'res_id': 'obj.id' }) #[optional] here is the record id, where you want to post that email after sending
		#values.update({'model': ''Object Name }) #[optional] here is the object(like 'project.project')  to whose record id you want to post that email after sending
        msg_id = mail_pool.create(values)
		# And then call send function of the mail.mail,
        if msg_id:
		    mail_pool.send([msg_id])