function switchAllow(self, userId, appId){
    $.ajax({
            'url':'/admin/rules/switch',
            'data': {'userId':userId, 'appId':appId, 'action': self.checked ? 'ALLOW' : 'DENY'},
            'type': 'POST',
            'success': function(data){

            },
            'error':function(){
                alert('Ошибка запроса. Рекомендуется обновить страницу')
            }
        }
    );
}