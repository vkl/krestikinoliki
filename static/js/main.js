
var t; // timer
var is_my_move;
var is_first;
var user_message;

function errorHandler( xhr, status, errorThrown ) {
    //console.log( "Error: " + errorThrown );
    //console.log( "Status: " + status );
    //console.dir( xhr );
}

function completeHandler( xhr, status ) {
	//
}

function activeUsers( json ) {
	var sActiveUsers = "";
	var status = "";
	for (var i=0; i<json.length; i++) {
	    switch(json[i].userstatus) {
	    	case 0:
	    		status = "free";
	    		break;
	    	case 1:
	    		status = "busy";
	    		break;
	    	default:
	    		status = "";
	    }
	    
	    if (json[i].username != $( "#username" ).attr("val")) {
	    	sActiveUsers += "<a class=\"activeusers "+status+"\" href=\"#\" title=\""+status+"\">"+json[i].username+"</a><br>";
	    } else {
	    	$.ajax({
	    		url: "/status_user/",
	    		method: "GET",
			    dataType: "json",
			    success: function( json ) {
			    	console.log(json);
			    	$( "#gameId" ).val(json.game_id);
			    	
			    	/* Game is over */
			    	if (json.game_id == 0) {
			    		if ($( ".game" ).is(":visible") == 1) {
			    		    $( ".game" ).fadeOut();
			    		    $( "#gameId" ).val(0);
			    		    $( "#gameUserMessage" ).val("");
			    		    $( "#game_field tr td" ).html("");
			    		}
			    	/* Invite for game message box */
			        } else if ((json.game_status == 0)&&(json.player_second_name==$( "#username" ).attr("val"))) {
			    		//clearTimeout(t);
			    		$( "#invitefromuser" ).html(json.player_first_name);
			    		$( "#modalPlay" ).modal("show");
			    		
			    	/* Delete game message box */
			    	} else if ((json.game_status == 2)&&(json.player_first_name==$( "#username" ).attr("val"))) {
			    		//clearTimeout(t);
			    		$( "#invitetouser" ).html(json.player_second_name);
			    		$( "#modalMessageOk" ).modal("show");
			    		
			    	/* Playing game */
			    	} else if (json.game_status == 1) {
			    		$( "#gameStatus" ).val(1);
			    		if ($( ".game" ).is(":visible") == 0) {
			    		    $( ".game" ).fadeIn(); 
			    			$( "#players" ).html(json.player_first_name+" vs "+json.player_second_name);
			    			if (json.player_second_name == $( "#username" ).attr("val"))
			    				is_first = 1;
			    			else
			    				is_first = 0;
			    		}
			    		
			    		if (json.user_message != '0')
			    			user_message = json.user_message;
			    		else
			    			user_message = "";
			    		
			    	    //console.log("Game is started...");
			    	    //console.log("Player first "+json.player_first_name);
			    	    //console.log("Player second "+json.player_second_name);
			    	    //console.log("Game user message "+json.user_message);
			    	    //console.log("User move "+json.is_your_move);
			    	    
			    	    if (is_my_move != json.is_your_move) {
			    			is_my_move = json.is_your_move;
			    		    changeEventsForGame(json.is_your_move);
			    		}
			    	    
			    	    /* refresh game field */
		    	    	for (var p=0; p<user_message.length; p += 4) {
		    	    		currmove = user_message.substr(p, 4);
		    	    		if (currmove.length > 0) { 
			    	    	    y = currmove.substr(1, 1);
			    	    	    x = currmove.substr(3, 1);
			    	    	    sign = currmove.substr(0, 1);
			    	    	    GameMove(y, x, sign);
			    	    	}
		    	    	}
			    	    
			    	    if (is_my_move) {
			    	    	$( "#playermove" ).html("<span class=\"label label-success\">Your move!</span>");
			    	    	
			    	    } else if (json.game_result == -1) {
			    	    	$( "#playermove" ).html("<span class=\"label label-info\">Opponent move!</span>");
			    	    	
			    	    } else if ( ( (json.game_result == 1) && (is_first) ) || ( (json.game_result == 2) && (is_first != 1) ) ) {
			    	    	$( "#playermove" ).html("<span class=\"label label-success\">Congratulations! You are win!</span>");
			    	    	
			    	    } else if ( ( (json.game_result == 1) && (is_first != 1) ) || ( (json.game_result == 2) && (is_first) ) ) {
			    	    	$( "#playermove" ).html("<span class=\"label label-danger\">You are lost!</span>");
			    	    	
			    	    } else if (json.game_result == 0) {
			    	    	$( "#playermove" ).html("<span class=\"label label-success\">Game ended in a tie!</span>");
			    	    }
			    	    
			    	}
			    },
			    error: errorHandler,
			    complete: completeHandler,
	    	});
	    }
	    
	}
	$( "#activeusers" ).html( sActiveUsers );
	
	/* Add event inviting for game */
	if (status == "free") {
	  $( ".activeusers" ).click(function( eventObject ) {
		$( "#inviteToUser" ).val($( this ).text());
		$.ajax({
		    url: "/inviteuser/",
		    type: "POST",
		    data: $( "#inviteForm" ).serialize(),
		    dataType: "json",
		    success: function( json ){
		    	$( "#gameId" ).val(json.game_id);
		    },
		    error: errorHandler,
		    complete: completeHandler,
		});
	  });
	}
	
}

function getActiveUsers() {
  $.ajax({
    url: "/active_users/",
    type: "GET",
    dataType: "json",
    success: activeUsers,
    error: errorHandler,
    complete: completeHandler,
  });
  t = setTimeout(function(){getActiveUsers()}, 4000);
}

function getStatus() {
  $.ajax({
	url: "/status/",
	method: "GET",
	dataType: "json",
	success: function( json ){
	   $( "#gameId" ).val(json.game_id);
	   $( "#invitefromuser" ).html(json.player_first_name);
	},
	error: errorHandler,
	complete: completeHandler,
  });
}

function postStatus() {
  console.log($( "#gameUserMessage" ).val());	
  $.ajax({
	url: "/set_game/",
	method: "POST",
	dataType: "json",
	data: $( "#gameForm" ).serialize(), 	  
	success: function( json ){
		console.log(json);
		getActiveUsers();
	},
	error: errorHandler,
	complete: completeHandler,
  });
}

/* Events */

/* logout */
$( "#logout" ).click(function(){
	clearTimeout(t);
});

/* accept game */
$( "#accept" ).click(function(){
	$( "#gameUserMessage" ).val(0); // clear message
	$( "#gameStatus" ).val(1); // accept game
	postStatus();
});

/* reject */
$( "#reject" ).click(function(){
	$( "#gameUserMessage" ).val(0); // clear message
	$( "#gameStatus" ).val(2); // reject game
	postStatus();
});

/* remove game */
$( "#ok" ).click(function(){
	$( "#gameUserMessage" ).val(1); // remove it
	postStatus();
});

/* Events for game field */
function changeEventsForGame(allow) {
	if (allow) {
	  $( "#game_field tr:eq(0) td" ).click(function( eventObject ){
		  console.log(eventObject);
		  clearTimeout(t);
		  GameMove(0, eventObject.target.cellIndex, (is_first) ? 'x' : 'o');
		  user_message = user_message + ((is_first) ? 'x' : 'o')+"0:" + eventObject.target.cellIndex;
		  $( "#gameUserMessage" ).val( user_message );
		  postStatus();
	  });
	  $( "#game_field tr:eq(1) td" ).click(function( eventObject ){
		  clearTimeout(t);
		  GameMove(1, eventObject.target.cellIndex, (is_first) ? 'x' : 'o');
		  user_message = user_message + ((is_first) ? 'x' : 'o')+"1:"+eventObject.target.cellIndex;
		  $( "#gameUserMessage" ).val( user_message );
		  postStatus();
	  });
	  $( "#game_field tr:eq(2) td" ).click(function( eventObject ){
		  clearTimeout(t);
		  GameMove(2, eventObject.target.cellIndex, (is_first) ? 'x' : 'o');
		  user_message = user_message + ((is_first) ? 'x' : 'o')+"2:"+eventObject.target.cellIndex;
		  $( "#gameUserMessage" ).val( user_message );
		  postStatus();
	  });
	} else {
	  $("#game_field tr td").off("click");
	}
}

function GameMove(y, x, sign) {
	$( "#game_field tr:eq("+y+") td:eq("+x+")" ).off("click");
	if (sign == "x") {
		if ($( "#game_field tr:eq("+y+") td:eq("+x+")" ).html() == "") {
			$( "#game_field tr:eq("+y+") td:eq("+x+")" ).html("<div class=\"gamecellcross\"></div>");
			$( "#game_field tr:eq("+y+") td:eq("+x+") div" ).fadeIn("slow");
		}
	}
	else if (sign == "o") {
		if ($( "#game_field tr:eq("+y+") td:eq("+x+")" ).html() == "") {
			$( "#game_field tr:eq("+y+") td:eq("+x+")" ).html("<div class=\"gamecellzero\"></div>");
			$( "#game_field tr:eq("+y+") td:eq("+x+") div" ).fadeIn("slow");
		}
	}
}

$( document ).ready(function() {

	/* Check if user logged and get all active users */
	if ($( "#username" ).attr("val")) {
		getActiveUsers();
	}

});

