document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('criarUsuarioForm');
    form.addEventListener('submit', enviarFormulario);

    function enviarFormulario(event) {
        event.preventDefault();

        const formData = new URLSearchParams(new FormData(form)).toString();

        $.ajax({
            url: '/criar_usuario',
            method: 'POST',
            contentType: 'application/x-www-form-urlencoded',
            dataType: 'text',
            data: formData,
            success: function (response) {
                alert(response);
                // Redirecionar o usuário ou realizar outras ações
            },
            error: function (xhr, status, error) {
                console.error(error);
                alert('Erro ao criar usuário: ' + xhr.responseText);
            }
        });
    }
});
