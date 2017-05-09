# -*- coding: utf-8 -*-
# -*- partnerCheck.py
from openerp import tools
from openerp import models, fields, api
from pygments.lexer import _inherit

class partnerConfirm ( models.Model):
	_inherit = "res.partner"

	x_bConfirm		= fields.Boolean	( string = "Confirmación datos")
	x_dateConfirm	= fields.Date		( string = "F confirmación")
	x_strContacto	= fields.Char		( string = "Contacto")

	@api.one
	def do_confirm ( self, bConfirm, dateConfirm, strContacto):
		self.x_bConfirm     = bConfirm
		self.x_dateConfirm  = dateConfirm
		self.x_strContacto  = strContacto