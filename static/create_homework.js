$('#add-task').click(function () {
    let new_task = $('.task:hidden').clone();
    let num_tasks = $('.task:visible').length;

    new_task.find('input, textarea').each(function() {
        $(this).val('');
        $(this).attr('name', $(this).attr('name').replace('0', num_tasks));
        $(this).attr('id', $(this).attr('id').replace('0', num_tasks));
    });

    new_task.find('label').each(function() {
        $(this).attr('for', $(this).attr('for').replace('0', num_tasks));
    });

    new_task.find('.task-number').text('Задание ' + (num_tasks + 1));

    new_task.show().appendTo('#tasks-container');
});

$(document).on('click', '.remove-task', function() {
    if ($('.task:visible').length > 1) {
        $(this).closest('.task').remove();
        $('.task:visible').each(function(index) {
            $(this).find('.task-number').text('Задание ' + (index + 1));
        });
    } else {
        alert('Должно быть по крайней мере одно задание!');
    }
});

$('form').submit(function(e) {
    let tasks = [];
    $('.task:visible').each(function() {
        let exercise = $(this).find('[name$=exercise]').val();
        let answer = $(this).find('[name$=answer]').val();
        tasks.push({exercise: exercise, answer: answer});
    });

    $('<input>').attr({
        type: 'hidden',
        name: 'tasks',
        value: JSON.stringify(tasks),
    }).appendTo('form');
});
