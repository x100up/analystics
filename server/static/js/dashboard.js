function switchAll(cb){
    if (cb.checked)
        $('input.jobcb').attr('checked', 'checked')
    else
        $('input.jobcb').removeAttr('checked')
}