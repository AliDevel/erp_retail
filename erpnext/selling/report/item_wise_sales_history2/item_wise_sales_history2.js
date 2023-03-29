// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Item-wise Sales History2"] = {
	"filters": [
		{fieldname:"warehouse",label:__("Warehouse"),fieldtype:"Link",options:"Warehouse",default:"",get_query:function(){const company=frappe.query_report.get_filter_value('company');return{filters:{'company':company}}}},
		{fieldname:"item_group",label:__("Item Group"),fieldtype:"Link",options:"Item Group"},
		{fieldname:"item_code",label:__("Item"),fieldtype:"Link",options:"Item",get_query:()=>{return{query:"erpnext.controllers.queries.item_query"}}},
		{fieldname:"from_date",label:__("FromDate"),fieldtype:"Date",default:frappe.defaults.get_global_default("year_start_date"),reqd:1},
		{fieldname:"to_date",label:__("ToDate"),fieldtype:"Date",default:frappe.defaults.get_global_default("year_end_date"),reqd:1},
	
	]
};
