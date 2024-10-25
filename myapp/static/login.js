// login.js

$(document).ready(function() {
    $("#loginForm").submit(function(event){
        event.preventDefault();
        
        const email = $("#email").val();
        const senha = $("#senha").val();
        
        autenticarUsuario(email, senha);
    });
});

function autenticarUsuario(email, senha) {
    $.ajax({
        url: '/login',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ email, senha }),
        success: function(response){
            if(response.status === 'success'){
                redirecionarUsuario('/painel');
            } else {
                mostrarErro(response.message);
            }
        },
        error: function(){
            mostrarErro('Erro ao fazer login. Tente novamente.');
        }
    });
}

function redirecionarUsuario(url) {
    window.location.href = url;
}

function mostrarErro(mensagem) {
    alert(mensagem);
}
