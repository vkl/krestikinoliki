
var dict = function(){
		if ($( "#lang" ).attr('val') == 'ENG')
		return {
			s_wait: 'Waiting for opponent',
			s_yourmove: 'Your move!',
			s_oppmove: 'Opponent move!',
			s_win: 'Congratulations! You are win!',
			s_lost: 'You are lost!',
			s_draw: 'Game ended in a tie!',
			s_rejected: 'Game was rejected by ',
			s_left: 'Opponent has just left the game',
		};
		else if ($( "#lang" ).attr('val') == 'RUS')
		return {
			s_wait: 'Ждем ответа от ',
			s_yourmove: 'Ваш ход!',
			s_oppmove: 'Соперник делает ход!',
			s_win: 'Поздравляю! Вы победили!',
			s_lost: 'Вы проиграли!',
			s_draw: 'Игра окончена вничью!',
			s_rejected: 'Приглашение было отклонено пользователем ',
			s_left: 'Соперник покинул игру',
		};
};