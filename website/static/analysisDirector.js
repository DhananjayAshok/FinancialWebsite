function initialize(){
	url_base = document.getElementById('computeActions-link').href;
	document.getElementById('computeActions-link').href = url_base +"?command=computeActions&method=bollingerbands";
	url_computeActions = url_base;
    url_simulateAnalysis = url_base;
    stock_change_url_base = document.getElementById('stock_change_base-link').href;
}
document.addEventListener('DOMContentLoaded', initialize);

function set_computeActions_url(){
	method = document.getElementById('computeActions-methods').value
	url_computeActions = url_base+"?command=computeActions&method="+method;
	document.getElementById('computeActions-link').href=url_computeActions;
	
};

function set_simulateAnalysis_url(){
	method = document.getElementById('simulateAnalysis-methods').value
	date = document.getElementById('simulateAnalysis-date').value
	frequency = document.getElementById('simulateAnalysis-frequency').value
	url_simulateAnalysis = url_base+"?command=simulateAnalysis&method="+method+"&start_date="+date+"&frequency="+frequency;
	document.getElementById('simulateAnalysis-link').href=url_simulateAnalysis	

}

function set_stock_buy_url(id){
	var command = "buy"
	var stock_id = id
	var n = document.getElementById('buy_stock-n('+id+')').value
	var free_url = stock_change_url_base + "?command="+command+"&free=True&stock_id="+stock_id+"&n="+n;
	var money_url = stock_change_url_base + "?command="+command+"&free=False&stock_id="+stock_id+"&n="+n;

	document.getElementById('add_stock-link('+id+')').href = free_url
	document.getElementById('buy_stock-link('+id+')').href = money_url
}

function set_stock_sell_url(id){
	var command = "sell"
	var stock_id = id
	var n = document.getElementById('sell_stock-n('+id+')').value
	var free_url = stock_change_url_base + "?command="+command+"&free=True&stock_id="+stock_id+"&n="+n;
	var money_url = stock_change_url_base + "?command="+command+"&free=False&stock_id="+stock_id+"&n="+n;

	document.getElementById('remove_stock-link('+id+')').href = free_url
	document.getElementById('sell_stock-link('+id+')').href = money_url
}