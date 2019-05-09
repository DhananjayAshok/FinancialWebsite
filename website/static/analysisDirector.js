function initialize(){
	url_base = document.getElementById('computeActions-link').href;
	document.getElementById('computeActions-link').href = url_base +"?command=computeActions&method=bollingerbands";
	url_computeActions = url_base;
    url_simulateAnalysis = url_base;
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
