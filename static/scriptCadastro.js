let dadosCadastrais = {};
function coletandoDadosCadastrais() {
  var nomeinstituicao = document.getElementById("nomeInstituicao");
  var nomeTurma = document.getElementById("nomeTurma");
  var nomeCrianca = document.getElementById("nomeCrianca");
  var dataNascimento = document.getElementById("dataNascimento");
  var dataAcompanhamento = document.getElementById("dataAcompanhamento");

  const sexoSelect = document.getElementById("sexo");
  const sexo = sexoSelect.value === "default" ? "" : sexoSelect.value;

  var peso = document.getElementById("peso");
  var altura = document.getElementById("altura");

  dadosCadastrais.nomeInstituicao = nomeinstituicao.value;
  dadosCadastrais.nomeTurma = nomeTurma.value;
  dadosCadastrais.nomeCrianca = nomeCrianca.value;
  dadosCadastrais.dataNascimento = dataNascimento.value;
  dadosCadastrais.dataAcompanhamento = dataAcompanhamento.value;
  dadosCadastrais.sexo = sexo;
  dadosCadastrais.peso = peso.value;
  dadosCadastrais.altura = altura.value;
}

function cadastrandoAlunos() {
  coletandoDadosCadastrais();

  fetch("/estadonutricional/cadastroTurmas", {
    method: "POST",
    headers: {
      "Content-type": "application/json",
    },
    body: JSON.stringify(dadosCadastrais),
  })
    .then((response) => response.json())
    .then((data) => {
      try {
        console.log("data oi oi oi :", data);
        console.log(data.motivo);

        const sectionTabela = document.querySelector(
          ".lista_alunos_cadastrados"
        );
        const botaoSalvar = document.querySelector(".salvar_planilha");
        const botaoLimpar = document.querySelector("#limparDados");

        sectionTabela.style.display = "flex";
        const tabelaCorpo = document.querySelector("table tbody");

        botaoSalvar.style.display = "flex";
        botaoLimpar.style.display = "flex";

        // Limpa o conteúdo existente na tabela
        tabelaCorpo.innerHTML = "";
        const tbody = document.querySelector("#tabela tbody");
        if (tbody) {
          tbody.innerHTML = "";
        } else {
          console.error("Erro ao limpar dados.");
        }

        data.alunos.forEach((aluno, index) => {
          const tr = document.createElement("tr");

          // Adiciona CÉLULAS COM DADOS DO ALUNO
          tr.innerHTML = `
                      <td>${aluno["Instituição"]}</td>
                      <td>${aluno["Turma"]}</td>
                      <td>${aluno["Nome Aluno"]}</td>
                      <td>${aluno["Data de Nascimento"]}</td>
                      <td>${aluno["Data de Acompanhamento"]}</td>
                      <td>${aluno["Sexo"]}</td>
                      <td>${aluno["Peso"]}</td>
                      <td>${aluno["Altura"]}</td>
                      <td>${aluno["Idade em Meses"]}</td>
                      <td>${aluno["WAZ"]}</td>
                      <td>${aluno["Peso/Idade"]}</td>
                      <td>${aluno["HAZ"]}</td>
                      <td>${aluno["Altura/Idade"]}</td>
                      <td>${aluno["WHZ"]}</td>
                      <td class="borda">${aluno["IMC/Idade"]}</td>
                      <td class="excluir_col"><button id="botaoExcluir" onclick="excluirLinha(${index})">Excluir</button></td>
                  `;

          // Adiciona a linha à tabela
          tabelaCorpo.appendChild(tr);
        });
      } catch (error) {
        // Em caso de erro, exibe um alerta com a mensagem de erro
        alert(
          "Ocorreu um erro ao processar os dados: " +
            "Desculpe, não foi possível calcular os índices WAZ, HAZ e WHZ do(s) aluno(s) abaixo, devido a discrepâncias nos dados de altura ou peso que não atendem aos padrões estabelecidos pela Organização Mundial da Saúde (OMS)"
        );
      }
    })
    .catch((error) => {
      // Em caso de erro de requisição, exibe um alerta com a mensagem de erro
      alert(
        "Desculpe, não foi possível calcular os índices WAZ, HAZ e WHZ deste aluno, devido a discrepâncias nos dados de altura ou peso que não atendem aos padrões estabelecidos pela Organização Mundial da Saúde (OMS)"
      );
    });
}

function excluirLinha(index) {
  // Remove a linha da tabela com base no índice
  const tabelaCorpo = document.querySelector("table tbody");
  tabelaCorpo.deleteRow(index - 1);

  // Chama a rota do backend para excluir o aluno no lado do servidor
  fetch(`/estadonutricional/excluirAluno/${index}`, {
    method: "DELETE",
  })
    .then((response) => response.json())
    .then((data) => console.log("Aluno excluído:", data))
    .catch((error) => console.error("Erro ao excluir aluno:", error));
}

function limparDados() {
  fetch("/estadonutricional/limparDadosCadastro", {
    method: "POST",
    headers: {
      "Content-type": "application/json",
    },
  })
    .then((response) => {
      if (response.ok) {
        // Limpa os campos do formulário
        document.getElementById("nomeInstituicao").value = "";
        document.getElementById("nomeTurma").value = "";
        document.getElementById("nomeCrianca").value = "";
        document.getElementById("dataNascimento").value = "";
        document.getElementById("dataAcompanhamento").value = "";
        document.getElementById("sexo").selectedIndex = 0;
        document.getElementById("peso").value = "";
        document.getElementById("altura").value = "";

        // Limpa a tabela
        document.querySelector(".lista_alunos_cadastrados").style.display =
          "none";
        // Limpa a tabela
        const tbody = document.querySelector("#tabela tbody");
        if (tbody) {
          tbody.innerHTML = "";
        } else {
          console.error("Erro ao limpar dados.");
        }
      } else {
        console.error("Erro ao limpar dados.");
      }
    })
    .catch((error) => {
      console.error("Erro ao limpar dados:", error);
    });
}

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
