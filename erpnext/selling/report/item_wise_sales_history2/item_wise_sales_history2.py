# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub

from frappe.utils import get_first_day as get_first_day_of_month
from frappe.utils import get_first_day_of_week, get_quarter_start, getdate
from operator import itemgetter
from typing import Any, Dict, List, Optional, TypedDict

import frappe
from frappe import _
from frappe.query_builder.functions import CombineDatetime
from frappe.utils import cint, date_diff, flt, getdate
from frappe.utils.nestedset import get_descendants_of

import erpnext
from erpnext.stock.doctype.inventory_dimension.inventory_dimension import get_inventory_dimensions
from erpnext.stock.doctype.warehouse.warehouse import apply_warehouse_filter
from erpnext.stock.report.stock_ageing.stock_ageing import FIFOSlots, get_average_age
from erpnext.stock.utils import add_additional_uom_columns, is_reposting_item_valuation_in_progress

class StockBalanceFilter(TypedDict):
	company: Optional[str]
	from_date: str
	to_date: str
	item_group: Optional[str]
	item: Optional[str]
	warehouse: Optional[str]
	warehouse_type: Optional[str]
	include_uom: Optional[str]  # include extra info in converted UOM
	show_stock_ageing_data: bool
	show_variant_attributes: bool


SLEntry = Dict[str, Any]
def execute(filters=None):
	columns, data = [], []

   
	columns = get_columns(filters)
	data = get_items(filters)
	#sle = get_stock_ledger_entries(filters, items)
	return columns, data 


def get_columns(filters):
	return [
		
		{"label": _("Item Group"),"fieldtype": "Link","fieldname": "item_group","options": "Item Group","width": 120},
		{"label": _("Item Code"),"fieldtype": "Link","fieldname": "item_code","options": "Item","width": 120},
		{"label": _("Item Name"), "fieldtype": "Data", "fieldname": "item_name", "width": 140},
		{"label": _("Selling Rate"), "fieldtype": "Data", "fieldname": "selling_rate", "width": 140},
		{"label": _("In Qty"),"fieldname": "in_qty","fieldtype": "Float","width": 80,"convertible": "qty",},

	
	]

def get_items(filters: StockBalanceFilter) -> List[str]:
	sales_items = frappe.qb.DocType("Sales Invoice Item")
	query =( frappe.qb.from_(sales_items).
	select('item_code','item_name','item_group','price_list_rate').g

	)
	
	items = frappe.db.sql("""
    SELECT item_code, item_name, item_group, sum(qty) as sold_qty, price_list_rate
     
    FROM `tabSales Invoice Item` si
    
    group by item_code
""",  as_dict=1)
	
	
	data=[]    
	for item in items:
		row = {'item_code':item['item_code'],
			  'item_name':item['item_name'],
			  'item_group':item['item_group'],
			  'selling_rate':item['price_list_rate'],
			  'in_qty':item['sold_qty']		}
		data.append(row)

	return data

def get_stock_ledger_entries(filters: StockBalanceFilter, items: List[str]) -> List[SLEntry]:
	sle = frappe.qb.DocType("Stock Ledger Entry")

	query = (
		frappe.qb.from_(sle)
		.select(
			sle.item_code,
			sle.warehouse,
			sle.posting_date,
			sle.actual_qty,
			sle.valuation_rate,
			sle.company,
			sle.voucher_type,
			sle.qty_after_transaction,
			sle.stock_value_difference,
			sle.item_code.as_("name"),
			sle.voucher_no,
			sle.stock_value,
			sle.batch_no,
		)
		.where((sle.docstatus < 2) & (sle.is_cancelled == 0))
		.orderby(CombineDatetime(sle.posting_date, sle.posting_time))
		.orderby(sle.creation)
		.orderby(sle.actual_qty)
	)
	return query.run(as_dict=True)

