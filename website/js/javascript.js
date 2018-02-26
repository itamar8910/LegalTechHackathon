	//display letter by letter
	var showText = function (target, message, index, interval) {   
	  if (index < message.length) {
	    $(target).append(message[index++]);
	    setTimeout(function () { showText(target, message, index, interval); }, interval);
	  } else {
	  	   //wait a second and refere
		  setTimeout(refere, 1000); 
	  }
	}
	
	//interval every second
	var currentText = "";
	var isFirst = 1;
    var pageType = "index"; 
    
     //---load page
    function refere() {
   	   var allData = currentText.split("\n");
   	   var text = allData[0];
   	   var type = allData[1];	
   	   		   
	   //if judge data
	   if(type == 1) {
		   $("#banner").hide();
		   $(".main").fadeIn( "slow", function() {});
			
			//load data						   
		   $( ".main" ).load( "judgeData.html?gil=5", function() { });
		   
		 //if answer type
	   } else if (type == 2) {
		   $("#banner").hide();
		   $(".main").fadeIn( "slow", function() {});
			
			//load data						   
			$.get('result.txt', function(data) {
				$(".main").html('<h1 dir="rtl" id="commandPar">' + data + '</h1>');
			}, 'text');
	   //if table of relevant
	   } else if (type == 3) {
		   $("#banner").hide();
		   $(".main").fadeIn( "slow", function() {});
			
			//load data						   
		   $( ".main" ).load( "releventData.html?gil=5", function() { });

	   }
    }
   

	setInterval(function(){
	 	//read text file and check if chainged
	 	$.ajaxSetup({
	    cache: false
	  });
	 	$.get('currentCommand.txt', function(data) {
		 	console.log("Current data : " + data);
		   //if data has changed 
		   if (currentText != data) {
			   currentText = data;
			   
			   //if not first -> action
			   if (!isFirst) {
			   	   var allData = currentText.split("\n");
			   	   var text = allData[0];
			   	   var type = allData[1];
			   
				   if (pageType == "index") {
					   //display text
					   $("#commandPar").html("");
					   showText("#commandPar", text, 0, 100);   
					   pageType = "second";
					   
	
					//if to bring home page again
				   } else {
					   $(".main").hide();
					   $("#banner").fadeIn( "slow", function() {});
					   $("#commandPar").html("");
					   showText("#commandPar", text, 0, 100);   
				   }
				
				   
				   
				
				}
		   }
		   
		   	//set is first
		   	isFirst = 0;
		}, 'text');
		
		
	}, 2000);
	
	
	
	
	
	
	
	