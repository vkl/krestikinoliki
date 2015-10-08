
var t; // timer
var ts; // timer 2
var is_my_move;
var is_first;
var user_message;

function errorHandler( xhr, status, errorThrown ) {
	/* if 401 Unauthorized navigate to index for getting logon page */
    if (errorThrown == 'UNAUTHORIZED') {
    	console.log(errorThrown);
    	$( location ).attr("href", "/index/");
    }
}

function completeHandler( xhr, status ) {
	//
}

var gameField = {'show':function(){
					if ($( ".jumbotron").is(":visible") == 1) {
						$( ".jumbotron" ).hide();
					}
					if ($( ".game" ).is(":visible") == 0) {
						$( ".game" ).show();
					}
				},
				'hide':function(){
					if ($( ".jumbotron").is(":visible") == 0) {
						$( ".jumbotron" ).show();
					}
					if ($( ".game" ).is(":visible") == 1) {
						$( ".game" ).hide();
						$( "#players" ).html("");
						$( "#playermove" ).html("");
						$("#game_field tr td").html("");
					}
				},
				'message': function(message, labelType){
					if (labelType == undefined) labelType = 'label-info'
					$( "#players" ).html("<span class=\"label "+labelType+"\">"+message+"</span>");
				},
}

function activeUsers( json ) {

	var sActiveUsers = "";
	var status = "";

	var count_free = 0;

	$( "#userscount" ).html(json.length);

	for (var i=0; i<json.length; i++) {

		/* add user to list*/
	    if (json[i].username != $( "#username" ).attr("val")) {

	    	if (json[i].userstatus == 0) {
	    		sActiveUsers += "<li><a class=\"activeusers\" href=\"#\" title=\""+status+"\"><span class=\"free\">"+json[i].username+"</span></a><li>";
	    		count_free++;
	    	} else if (json[i].userstatus == 1) {
	    		sActiveUsers += "<li class=\"disabled\"><a class=\"activeusers\" href=\"#\" title=\""+status+"\"><span class=\"busy\">"+json[i].username+"</span></a><li>";
	    	}

	    /* get status for self */
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
			    		//$("#game_field tr td").html("");
			    		$("#gameId").val(0);
			    		$("#gameUserMessage").val("");
			    		
			    	/* One player left the game */
			        } else if ((json.game_status == 4)&&(json.user_message != $( "#username" ).attr("val"))) {
			        	clearTimeout(t);
			        	if ($( "#modalPlay" ).is(":visible") == true)
			        		$( "#modalPlay" ).modal("hide");
			    		gameField.show()
			        	$( "#playermove" ).html("<span class=\"label label-danger\">"+dict().s_left+"</span>");
			        	$( "#gameUserMessage" ).val(1); // remove it
			    		postStatus();
			    		
			    	/* Invite for game message box */
			        } else if ((json.game_status == 0)&&(json.player_second_name==$( "#username" ).attr("val"))) {
			        	$("#game_field tr td").html("");
			        	$( "#playermove" ).html("");
			        	if ($( "#modalPlay" ).is(":visible") == 0) {
			        		$( "#invitefromuser" ).html(json.player_first_name);
			        		$( "#modalPlay" ).modal("show");
			        	}
			    		
			    	/* Show game field when user is waiting for replay from another user */
			        } else if ((json.game_status == 0)&&(json.player_second_name!=$( "#username" ).attr("val"))) {
			        	$("#game_field tr td").html("");
			        	$( "#playermove" ).html("");
			        	gameField.show()
			        	gameField.message(dict().s_wait+" "+json.player_second_name, 'label-warning');

			    	/* User rejected game. Delete game message box */
			    	} else if ((json.game_status == 2)&&(json.player_first_name==$( "#username" ).attr("val"))) {
			    		clearTimeout(t);
			    		gameField.show()
			    		gameField.message(dict().s_rejected+" "+json.player_second_name, 'label-warning');
			    		$( "#invitetouser" ).html(json.player_second_name);
			    		$( "#gameUserMessage" ).val(1); // remove it
			    		postStatus();

			    	/* Playing game */
			    	} else if (json.game_status == 1) {
			    		gameField.show()
			    		gameField.message(json.player_first_name+" vs "+json.player_second_name, 'label-info');
			    		(json.player_second_name == $( "#username" ).attr("val")) ? is_first = 1 : is_first = 0;
			    		$( "#gameStatus" ).val(1);

			    		if (json.user_message != '0')
			    			user_message = json.user_message;
			    		else
			    			user_message = "";

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
			    	    	$( "#playermove" ).html("<span class=\"label label-success\">"+dict().s_yourmove+"</span>");

			    	    } else if (json.game_result == -1) {
			    	    	$( "#playermove" ).html("<span class=\"label label-info\">"+dict().s_oppmove+"</span>");

			    	    } else if ( ( (json.game_result == 1) && (is_first) ) || ( (json.game_result == 2) && (is_first != 1) ) ) {
			    	    	$( "#playermove" ).html("<span class=\"label label-success\">"+dict().s_win+"</span>");

			    	    } else if ( ( (json.game_result == 1) && (is_first != 1) ) || ( (json.game_result == 2) && (is_first) ) ) {
			    	    	$( "#playermove" ).html("<span class=\"label label-danger\">"+dict().s_lost+"</span>");

			    	    } else if (json.game_result == 0) {
			    	    	$( "#playermove" ).html("<span class=\"label label-success\">"+dict().s_draw+"</span>");
			    	    }

			    	    /* User who started game should suggest a new game*/
			    	    if ((json.game_result != -1) && (is_first != 1)){
			    	    	clearTimeout(t);
			    	    	$( "#modalMessageYesNo" ).modal("show");
			    	    }

			    	}
			    },
			    error: errorHandler,
			    complete: completeHandler,
	    	});
	    }

	}

	$( "#userscount ").html( "<span class=\"badge\">"+count_free+"/"+(json.length-1)+"</span>" );
	$( "#activeusers" ).html( sActiveUsers );

	/* Add event inviting for game */
	if ( $( "#gameId" ).val() == 0 ) {
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

function postStatus( callbackOnSuccess ) {
  ajax_obj = {
			url: "/set_game/",
			method: "POST",
			dataType: "json",
			data: $( "#gameForm" ).serialize(),
			error: errorHandler,
			complete: completeHandler,
		  }
  if ( callbackOnSuccess ) {
	  ajax_obj.success = callbackOnSuccess; 
  } else {
	  ajax_obj.success = function( json ){
			console.log(json);
			getActiveUsers();
	  }; 
  }
  $.ajax(ajax_obj);
}

/* Events */

/* change language */
/*
$( "#lang" ).click(function(){
	clearTimeout(t);
	console.log($( "#language" ).val( $(this).text() ));
	$( "#language" ).val( $(this).text() );
	$( "#langForm" ).submit();
});
*/

/* logout */
$( "#logout" ).click(function(){
	clearTimeout(t);
	if ($( "#gameId" ).val() != 0 ) {
		$( "#modalMessageYesNo2" ).modal("show");
	} else {
		$( location ).attr("href", "/logout/");
	}
		
});

/* accept game */
$( "#accept" ).click(function(){
	/* Clear game field */
	$( "#game_field tr td" ).html("");
	$( "#playermove" ).html("");
	$( "#gameUserMessage" ).val(0); // clear message
	$( "#gameStatus" ).val(1); // accept game
	postStatus();
});

/* reject */
$( "#reject" ).click(function(){
	gameField.hide();
	$( "#gameUserMessage" ).val(0); // clear message
	$( "#gameStatus" ).val(2); // reject game
	postStatus();
});

/* message box */
$( "#ok" ).click(function(){
	//$( "#gameUserMessage" ).val(1); // remove it
	//postStatus();
	//
});

/* suggest new game */
$( "#yes" ).click(function(){
	/* Clear game field */
	$( "#game_field tr td" ).html("");
	$( "#playermove" ).html("");
	$( "#gameUserMessage" ).val(0); // clear message
	$( "#gameStatus").val(0); // waiting
	postStatus();
});

/* stop game */
$( "#no" ).click(function(){
	$( "#gameUserMessage" ).val(1); // remove game
	postStatus();
});

/* close game */
$( "#close" ).click(function(){
	clearTimeout(t);
	$( "#gameUserMessage" ).val($( "#username" ).attr("val")); // player name who left game
	$( "#gameStatus" ).val(4); // one player left game
	postStatus(function(json){
		gameField.hide();
		getActiveUsers();
	});
});

/* leave game */
$( "#yes2" ).click(function(){
	$( "#gameUserMessage" ).val(0); // clear message
	$( "#gameStatus" ).val(4); // one player left game
	postStatus(function(json){
		console.log(json);
		$( location ).attr("href", "/logout/");
	});
});

/* stay in game */
$( "#no2" ).click(function(){
	getActiveUsers();
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
		  $("#game_field tr td").off("click");
		  postStatus();
	  });
	  $( "#game_field tr:eq(1) td" ).click(function( eventObject ){
		  clearTimeout(t);
		  GameMove(1, eventObject.target.cellIndex, (is_first) ? 'x' : 'o');
		  user_message = user_message + ((is_first) ? 'x' : 'o')+"1:"+eventObject.target.cellIndex;
		  $( "#gameUserMessage" ).val( user_message );
		  $("#game_field tr td").off("click");
		  postStatus();
	  });
	  $( "#game_field tr:eq(2) td" ).click(function( eventObject ){
		  clearTimeout(t);
		  GameMove(2, eventObject.target.cellIndex, (is_first) ? 'x' : 'o');
		  user_message = user_message + ((is_first) ? 'x' : 'o')+"2:"+eventObject.target.cellIndex;
		  $( "#gameUserMessage" ).val( user_message );
		  $("#game_field tr td").off("click");
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

function UpdateSession() {
	  $.ajax({
	    url: "/status_user/",
	    type: "HEAD",
	    error: errorHandler,
	  });
	  ts = setTimeout(function(){UpdateSession()}, 4000);
	}

$( document ).ready(function() {

	/* Check if user logged and get all active users */
	if ($( "#username" ).attr("val")) {
		getActiveUsers();
		UpdateSession();
	}
	
});

