$(document).ready(function(){
	if(isPc()){
		$("#swip").addClass('swip')
		$('li.pcShow').hide();
		$('#home .mShow').show();
	}else{
		$("#swip1").addClass('swip1')
		$('li.pcShow').hide();
		$('#home .mShow').show();
		
	}
	function isPc() { //是否是pc端；
		var userAgentInfo = navigator.userAgent;
		var Agents = new Array("Android", "iPhone", "SymbianOS", "Windows Phone", "iPad", "iPod");
		var flag = true;
		for(var v = 0; v < Agents.length; v++) {
			if(userAgentInfo.indexOf(Agents[v]) > 0) {
				flag = false;
				break;
			}
		}
		return flag;
	};
})