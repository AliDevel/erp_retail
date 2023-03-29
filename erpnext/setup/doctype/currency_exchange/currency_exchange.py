# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

# For license information, please see license.txt

import frappe
from frappe import _, throw
from frappe.model.document import Document
from frappe.utils import cint, formatdate, get_datetime_str, nowdate

from frappe.utils import add_days, add_months, cint, cstr, flt, getdate

from erpnext.setup.utils import get_exchange_rate,get_datetime_str
class CurrencyExchange(Document):
	def autoname(self):
		purpose = ""
		if not self.date:
			self.date = nowdate()

		# If both selling and buying enabled
		purpose = "Selling-Buying"
		if cint(self.for_buying) == 0 and cint(self.for_selling) == 1:
			purpose = "Selling"
		if cint(self.for_buying) == 1 and cint(self.for_selling) == 0:
			purpose = "Buying"

		self.name = "{0}-{1}-{2}{3}".format(
			formatdate(get_datetime_str(self.date), "yyyy-MM-dd"),
			self.from_currency,
			self.to_currency,
			("-" + purpose) if purpose else "",
		)

	def validate(self):
		
		self.validate_value("exchange_rate", ">", 0)

		if self.from_currency == self.to_currency:
			throw(_("From Currency and To Currency cannot be same"))

		if not cint(self.for_buying) and not cint(self.for_selling):
			throw(_("Currency Exchange must be applicable for Buying or for Selling."))
	def on_update(self):
		self.update_rate()

	def update_rate(self):
		exchange_rate = get_exchange_rate('USD','TMM')
		price_list='Standard Selling'
		item_prices= frappe.db.get_values('Item Price',
										{'price_list':price_list},
										['name','item_code','foreign_currency_rate','price_list_rate' ], as_dict=1)
		
		for item  in item_prices:
			rate = item['foreign_currency_rate'] * exchange_rate
			values={'price_list_rate':rate, 'name':item['name']}
			frappe.db.sql(""" update 
									`tabItem Price`
							set price_list_rate = %(price_list_rate)s
							where name = %(name)s
			""",values=values, as_dict=0)

		frappe.db.commit()   
		item_prices= frappe.db.get_values('Item Price',
										{'price_list':price_list},
										['item_code','foreign_currency_rate','price_list_rate' ], as_dict=1)
		return item_prices