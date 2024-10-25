from myapp import create_app

# Criando uma instância da aplicação usando a factory function "create_app"
# Esse padrão permite maior flexibilidade e facilita a configuração da aplicação
app = create_app()

if __name__ == "__main__":
    # Especificando o host como '0.0.0.0' para que o código possa rodar em qualquer ambiente local
    # e definir uma porta padrão para rodar a aplicação
    app.run(host="0.0.0.0", port=5000)