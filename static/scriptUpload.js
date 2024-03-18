//função para aparecer o botao
function VerificarArquivoUsuario() {
  let fileInput = document.getElementById("file");
  /*console.log(fileInput)*/
  let btnSubmit = document.getElementById("submit");
  /* console.log(btnSubmit)*/

  if (fileInput.files.length > 0) {
    btnSubmit.style.display = "block"; // ou 'inline' dependendo do contexto
  } else {
    btnSubmit.style.display = "none";
  }
}
/*Função para adicionar o nome do arquivo quando o usuário enviar*/
function updateLabel() {
  var fileInput = document.getElementById("file");
  var nomeAquivo = document.getElementById("nomeAquivo");

  if (fileInput.files.length > 0) {
    // Pega o nome do arquivo do caminho completo
    var fileName = fileInput.files[0].name;

    // Atualiza o rótulo com o nome do arquivo ao lado do ícone
    nomeAquivo.innerHTML = "Arquivo carregado - " + fileName;
  } else {
    // Se nenhum arquivo for selecionado, volta ao rótulo original
    nomeAquivo.innerHTML = "Selecione um arquivo";
  }
}
document
  .getElementById("downloadButton")
  .addEventListener("click", function () {
    // Redireciona para a rota do Flask que gera o arquivo Excel
    window.location.href = "/download_excel";
  });

function enviarArquivo() {
  let formData = new FormData();
  let fileInput = document.getElementById("file");
  formData.append("file", fileInput.files[0]);

  fetch("/analise", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      // Verifica se a resposta contém a mensagem de erro do backend
      if (
        data === "Por favor, faça o upload de uma planilha no formato correto."
      ) {
        // Exibe alerta informando ao usuário sobre o erro
        alert("Por favor, faça o upload de uma planilha no formato correto.");
        return;
      }

      const alunosProblema = document.querySelector(".alunosProblema");
      alunosProblema.style.display = "flex";

      mensagem = document.getElementById('motivo');

      motivo.innerHTML = data.motivo.replace(/\n/g, "<br> <br>");

      console.log(data.motivo)
      formData.append("file", fileInput.files[0]);

      const exibirTabela = document.getElementById("resultadoDataframe");
      exibirTabela.style.display = "block";

      /* Fazendo desaparecer o campo de enviar arquivo*/
      const dowup = document.querySelector(".downloadEupload");
      dowup.style.display = "none";

      const tabelaCorpo = document.querySelector("table tbody");
      
      // Limpa o conteúdo existente na tabela
      tabelaCorpo.innerHTML = "";
      console.log("motivo upload", data.motivo)
      data.alunos.forEach((alunos) => {
      const tr = document.createElement("tr");

        // Adiciona CÉLULAS COM DADOS DO ALUNO
      tr.innerHTML = `
                  <td>${alunos["Instituição"]}</td>
                  <td>${alunos["Turma"]}</td>
                  <td>${alunos["Nome Aluno"]}</td>
                  <td>${alunos["Data de Nascimento"]}</td>
                  <td>${alunos["Data de Acompanhamento"]}</td>
                  <td>${alunos["Sexo"]}</td>
                  <td>${alunos["Peso"]}</td>
                  <td>${alunos["Altura"]}</td>
                  <td>${alunos["Idade em Meses"]}</td>
                  <td>${alunos["WAZ"]}</td>
                  <td>${alunos["Peso/Idade"]}</td>
                  <td>${alunos["HAZ"]}</td>
                  <td>${alunos["Altura/Idade"]}</td>
                  <td>${alunos["WHZ"]}</td>
                  <td class="borda">${alunos["IMC/Idade"]}</td>
              `;

        // Adiciona a linha à tabela
        tabelaCorpo.appendChild(tr);
      });

      const sectionBotoes = document.querySelector(".salvar_excel");
      sectionBotoes.style.display = "flex";

    })
    .catch((error) => {
      console.error("Erro:", error);
    });
}

function uploadNovaTurma() {
  fetch("/limparDadosUpload", {
    method: "POST",
    headers: {
      "Content-type": "application/json",
    },
  })
  .then((response) => {
    if (response.ok) {
        /*Limpando a area que exibe a tabela"*/
        const sectionTabela = document.getElementById("resultadoDataframe");
        sectionTabela.style.display = "none";

        let tabela = document.getElementById("tabela");
        tbody = tabela.getElementsByTagName("tbody")[0];
        tbody.innerHTML = "";

        const sectionBotoes = document.querySelector(".salvar_excel");
        sectionBotoes.style.display = "none";
        /************************************************* */
        /*Exibindo novamente a area para fazer download ou upload de umarquivo excel */
        const downloadUpload = document.querySelector(".downloadEupload");
        downloadUpload.style.display = "block";
        const alunosProblema = document.querySelector(".alunosProblema");
        alunosProblema.style.display = "none";
        /************************************************** */
        /*Limpando o nome do arquivo anteriormente enviado */
        document.getElementById("file").value = "";
        VerificarArquivoUsuario();
        updateLabel();
        /***************************************************** */
        /*Limpando a mensagem anteriormente exibida */
        mensagem = document.getElementById('motivo');// Assumindo que a mensagem está em um elemento com o ID 'mensagem'
        mensagem.innerHTML = '';
      } else {
        console.error("Erro ao limpar dados.");
      }
    })
    .catch((error) => {
      console.error("Erro ao limpar dados:", error);
    });
}
