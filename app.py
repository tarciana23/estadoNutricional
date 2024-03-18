from datetime import datetime
from flask import send_file
from flask import Flask, jsonify, render_template, request, redirect, url_for
from dateutil.relativedelta import relativedelta
import pandas as pd
from flask import Flask, send_file
from openpyxl import Workbook
from openpyxl.styles import Protection
from io import BytesIO


app = Flask(__name__)

wgsData = pd.read_excel('wgsData.xlsx')
sexo_convertido = None

# Lista temporária de alunos
alunos_cadastro = []
alunos_upload = []
nomeTurma = ''
resultado_upload = {}
resultado_cadastro = {}

@app.route('/')
def index():
    return render_template('index.html', alunos=alunos_cadastro)

@app.route('/excluirAluno/<int:index>', methods=['DELETE'])
def excluir_aluno(index):
    try:
        aluno_excluido = alunos_cadastro.pop(index)
        return jsonify(aluno_excluido)
    except IndexError:
        return jsonify({'error': 'Índice inválido'}), 400
    
def verificar_colunas(df):
    colunas_esperadas = ['Nome Instituição', 'Nome Turma', 'Nome cidadão', 'Data de nascimento', 'Data do acompanhamento', 'Sexo', 'Peso (kg)', 'Altura (cm)']
    colunas_presentes = df.columns.tolist()
    if colunas_presentes != colunas_esperadas:
        return False
    return True

##funcao para quando fizerem o upload do arquivo
@app.route('/analise', methods=['POST'])  # Rota para processar o upload do arquivo via POST)
def analisar_excel():
    
    mensagem = 'Por favor, faça o upload de uma planilha no formato correto.'
    alunos_sem_calculo = []
    global alunos_upload
    global resultado_upload

    if request.method == 'POST':
        file = request.files['file']
        if file:
            try:
                df = pd.read_excel(file)
                colunas_esperadas = ['Nome Instituição', 'Nome Turma', 'Nome cidadão', 'Data de nascimento',
                                     'Data do acompanhamento', 'Sexo', 'Peso (kg)', 'Altura (cm)']

                if not all(coluna in df.columns for coluna in colunas_esperadas):
                    return jsonify(mensagem)

                for index, row in df.iterrows():
                    try:
                        nomeInstituicao = row['Nome Instituição']
                        nomeTurma = row['Nome Turma']
                        nomeCrianca = row['Nome cidadão']
                        dataNascimento = row['Data de nascimento']
                        dataAcompanhamento = row['Data do acompanhamento']
                        sexo = row['Sexo']
                        peso = row['Peso (kg)']
                        altura = row['Altura (cm)']

                        dataNascimento = datetime.strptime(str(dataNascimento.date()), '%Y-%m-%d')
                        dataAcompanhamento = datetime.strptime(str(dataAcompanhamento.date()), '%Y-%m-%d')

                        diferenca = relativedelta(dataAcompanhamento, dataNascimento)
                        idade_em_meses = diferenca.years * 12 + diferenca.months + diferenca.days / 30.44
                        idade_em_meses = round(idade_em_meses, 2)
                        idade_formatada = round(idade_em_meses)

                        altura_metros = altura / 100
                        imc = peso / (altura_metros ** 2)

                        sexo_convertido = 1 if sexo == 'M' or sexo == 'm' else 2

                        waz = obterEscoresZ(sexo_convertido, peso, idade_formatada, 'wfa')
                        if waz is None:
                            alunos_sem_calculo.append(nomeCrianca)
                        else:
                            waz = round(waz, 2)

                        whz = obterEscoresZ(sexo_convertido, peso, altura, 'wfh')
                        if whz is None:
                            alunos_sem_calculo.append(nomeCrianca)
                        else:
                            whz = round(whz, 2)

                        haz = obterEscoresZ(sexo_convertido, altura, idade_formatada, 'hfa')
                        if haz is None:
                            alunos_sem_calculo.append(nomeCrianca)
                        else:
                            haz = round(haz, 2)

                        classificacao_waz = ''
                        if waz < -3:
                            classificacao_waz = 'Muito baixo peso'
                        elif waz >= -3 and waz < -2:
                            classificacao_waz = 'Baixo peso'
                        elif waz >= -2 and waz <= 2:
                            classificacao_waz = 'Peso adequado'
                        else:
                            classificacao_waz = 'Peso elevado'

                        classificacao_haz = ''
                        if haz < -3:
                            classificacao_haz = "Muito baixa estatura para idade"
                        elif haz >= -3 and haz < -2:
                            classificacao_haz = "Baixa estatura para a idade"
                        else:
                            classificacao_haz = "Estatura adequada para a idade"

                        classificacao_baz = ''
                        if whz < -3:
                            classificacao_baz = 'Magreza acentuada'
                        elif whz >= -3 and whz < -2:
                            classificacao_baz = 'Magreza'
                        elif whz >= -2 and whz <= 1:
                            classificacao_baz = 'Eutrofia'
                        elif whz > 1 and whz <= 2:
                            classificacao_baz = 'Risco de sobrepeso'
                        elif whz > 2 and whz <= 3:
                            classificacao_baz = 'Sobrepeso'
                        else:
                            classificacao_baz = 'Obesidade'

                        alunos_upload.append({
                            'Instituição': nomeInstituicao,
                            'Turma': nomeTurma,
                            'Nome Aluno': nomeCrianca,
                            'Data de Nascimento': dataNascimento.strftime('%Y-%m-%d'),
                            'Data de Acompanhamento': dataAcompanhamento.strftime('%Y-%m-%d'),
                            'Sexo': sexo,
                            'Peso': peso,
                            'Altura': altura,
                            'Idade em Meses': idade_em_meses,
                            'WAZ': waz,
                            'Peso/Idade': classificacao_waz,
                            'HAZ': haz,
                            'Altura/Idade': classificacao_haz,
                            'WHZ': whz,
                            'IMC/Idade': classificacao_baz
                        })
                    except Exception as e:
                        continue  # Continua para o próximo aluno em caso de erro
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        resultado_upload = {'alunos': alunos_upload}
        if alunos_sem_calculo:
            motivo = 'Desculpe, não foi possível calcular os índices WAZ, HAZ e WHZ do(s) aluno(s) abaixo, devido a discrepâncias nos dados de altura ou peso que não atendem aos padrões estabelecidos pela Organização Mundial da Saúde (OMS) :''\n'
            motivo += '\n'.join(alunos_sem_calculo)
            resultado_upload['motivo'] = motivo
    
        return jsonify(resultado_upload)

##funcao para quando cadastrarem no formulario
@app.route('/cadastroTurmas', methods=['POST'])
def cadastrar_aluno():

    global alunos_cadastro

    alunos_sem_calculo_cadastro = []
    mensagem = ''

    if request.is_json:
        data = request.get_json()
        instituicao = data.get('nomeInstituicao')
        nomeTurma = data.get('nomeTurma')
        nome = data.get('nomeCrianca', '')
        dataNascimento = data.get('dataNascimento', '')
        dataAcompanhamento = data.get('dataAcompanhamento')
        sexo = data.get('sexo')
        if sexo == 'M':
            sexo_convertido = 1
        else:
            sexo_convertido = 2
        
        peso = data.get('peso')
        altura = data.get('altura')

        # Converte as datas de string para objetos datetime
        dataNascimento = datetime.strptime(dataNascimento, '%Y-%m-%d')
        dataAcompanhamento = datetime.strptime(dataAcompanhamento, '%Y-%m-%d')

        # Converte altura e peso para float
        altura = float(altura)
        peso = float(peso)

        # Calcula a diferença em anos, meses e dias usando a biblioteca relativedelta
        diferenca = relativedelta(dataAcompanhamento, dataNascimento)

        # Calcula a idade total em meses, incluindo as frações
        idade_em_meses = diferenca.years * 12 + diferenca.months + diferenca.days / 30.44

        # Arredonda para duas casas decimais
        idade_em_meses = round(idade_em_meses, 2)
        # Formatando para uma casa decimal
        #idade_formatada = "{:.1f}".format(idade_em_meses)
        idade_formatada = round(idade_em_meses)

        # Calcula o IMC
        altura_metros = altura / 100  # Convertendo altura para metros
        imc = peso / (altura_metros ** 2)

        waz = obterEscoresZ(sexo_convertido, peso, idade_formatada, 'wfa')
        if waz is None:
            alunos_sem_calculo_cadastro.append(nome)
        else:
            waz = round(waz, 2)

        whz = obterEscoresZ(sexo_convertido, peso, altura, 'wfh')
        if whz is None:
            alunos_sem_calculo_cadastro.append(nome)
        else:
            whz = round(whz, 2)

        haz = obterEscoresZ(sexo_convertido, altura, idade_formatada, 'hfa')
        if haz is None:
            alunos_sem_calculo_cadastro.append(nome)
        else:
            haz = round(haz, 2)

        classificacao_waz = ''
        
        if waz < -3:
            classificacao_waz = 'Muito baixo peso'
        elif waz >= -3 and waz < -2:
            classificacao_waz = 'Baixo peso'
        elif waz >= -2 and waz <= 2: 
            classificacao_waz = 'Peso adequado'
        else:
            classificacao_waz = 'Peso elevado'
        
        classificacao_haz = ' '

        if haz < -3:
            classificacao_haz = "Muito baixa estatura para idade"
        elif haz >= -3 and haz < -2:
            classificacao_haz = "Baixa estatura para a idade"
        else:
            classificacao_haz = "Estatura adequada para a idade"

        classificacao_baz = ' '

        if whz < -3:
            classificacao_baz = 'Magreza acentuada'
        elif whz >= -3 and whz < -2:
            classificacao_baz = 'Magreza'
        elif whz >= -2 and whz <= 1: 
            classificacao_baz = 'Eutrofia'
        elif whz > 1 and whz <= 2 :
            classificacao_baz = 'Risco de sobrepeso'
        elif whz > 2 and whz <= 3: 
            classificacao_baz = 'Sobrepeso'
        else:
            classificacao_baz = 'Obesidade'

        # Adiciona o aluno à lista temporária
        alunos_cadastro.append({'Instituição': instituicao,
                        'Turma': nomeTurma, 
                        'Nome Aluno': nome, 
                        'Data de Nascimento': dataNascimento.strftime('%Y-%m-%d'),
                        'Data de Acompanhamento': dataAcompanhamento.strftime('%Y-%m-%d'),
                        'Sexo': sexo,
                        'Peso': peso,
                        'Altura': altura,
                        'Idade em Meses': idade_em_meses,
                        'WAZ': waz,
                        'Peso/Idade':classificacao_waz,
                        'HAZ': haz,
                        'Altura/Idade': classificacao_haz,
                        'WHZ': whz,
                        'IMC/Idade': classificacao_baz

                        })
    
    motivo = 'oi'
    resultado_cadastro = {'alunos': alunos_cadastro, 'motivo': motivo}
    if alunos_sem_calculo_cadastro:
        motivo = 'Desculpe, não foi possível calcular os índices WAZ, HAZ e WHZ do(s) aluno(s) abaixo, devido a discrepâncias nos dados de altura ou peso que não atendem aos padrões estabelecidos pela Organização Mundial da Saúde (OMS) :''\n'
        motivo += '\n'.join(alunos_sem_calculo_cadastro)
        resultado_cadastro['motivo'] = motivo

    return jsonify(resultado_cadastro)
    
def obterEscoresZ(sexoObservado, primeiraParte, segundaParte, indice):
    """
    Esta função calcula os escores Z com base nos parâmetros fornecidos.

    Argumentos:
    sexoObservado: sexo observado para o qual os escores Z serão calculados.
    primeiraParte: primeira parte do cálculo dos escores Z.
    segundaParte: segunda parte do cálculo dos escores Z.
    indice: índice para filtrar os dados.

    Retorna:
    O valor do escore Z calculado.
    """

    # Filtra o dataframe wgsData
    linhaConsulta = wgsData[(wgsData['indicator'] == indice) & (wgsData['sex'] == sexoObservado) & (wgsData['given'] == segundaParte)]
    
    # Verifica se a consulta não retornou nenhum resultado
    if linhaConsulta.empty:
        return None

    # Seleciona a primeira linha do resultado da consulta
    linhaConsulta = linhaConsulta.iloc[0]

    # Calcula o escore Z
    z = (((primeiraParte / linhaConsulta['m']) ** linhaConsulta['l']) - 1) / (linhaConsulta['l'] * linhaConsulta['s'])

    # Calcula os desvios padrão para 3 posições acima da média
    SD3pos = linhaConsulta['m'] * (1 + linhaConsulta['l'] * linhaConsulta['s'] * (+3)) ** (1 / linhaConsulta['l'])
    SD2pos = linhaConsulta['m'] * (1 + linhaConsulta['l'] * linhaConsulta['s'] * (+2)) ** (1 / linhaConsulta['l'])
    SD23pos = SD3pos - SD2pos

    # Calcula os desvios padrão para 3 posições abaixo da média
    SD3neg = linhaConsulta['m'] * (1 + linhaConsulta['l'] * linhaConsulta['s'] * (-3)) ** (1 / linhaConsulta['l'])
    SD2neg = linhaConsulta['m'] * (1 + linhaConsulta['l'] * linhaConsulta['s'] * (-2)) ** (1 / linhaConsulta['l'])
    SD23neg = SD2neg - SD3neg

    # Verifica se o escore Z está acima de 3
    if z > 3:
        # Ajusta o escore Z para 3 posições acima da média
        z = 3 + ((primeiraParte - SD3pos) / SD23pos)

    # Verifica se o escore Z está abaixo de -3
    if z < -3:
        # Ajusta o escore Z para 3 posições abaixo da média
        z = -3 + ((primeiraParte - SD3neg) / SD23neg)

    
    return z
"""
@app.route('/salvar_planilha_cadastro')
def salvar_planilha_cadastro():
    global alunos_cadastro
    arquivo_nome = (alunos_cadastro[0]['Turma'])
    # Cria um DataFrame pandas com os alunos
    df_cadastro = pd.DataFrame(alunos_cadastro)
    # Salva o DataFrame em uma planilha Excel
    excel_filename = f'{arquivo_nome}.xlsx'
    df_cadastro.to_excel(excel_filename, index=False)

    # Limpa a lista temporária de alunos
    alunos_cadastro.clear()
    
    # Envia o arquivo Excel como resposta
    return send_file(excel_filename, as_attachment=True)

@app.route('/salvar_planilha_upload')
def salvar_planilha_upload():
    global alunos_upload
    arquivo_nome = (alunos_upload[0]['Turma'])
    # Cria um DataFrame pandas com os alunos
    df_upload = pd.DataFrame(alunos_upload)
    # Salva o DataFrame em uma planilha Excel
    excel_filename = f'{arquivo_nome}.xlsx'
    df_upload.to_excel(excel_filename, index=False)

    # Limpa a lista temporária de alunos
    alunos_upload.clear()
    
    # Envia o arquivo Excel como resposta
    return send_file(excel_filename, as_attachment=True)"""


@app.route('/salvar_planilha_cadastro')
def salvar_planilha_cadastro():
    global alunos_cadastro
    arquivo_nome = (alunos_cadastro[0]['Turma'])
    # Cria um DataFrame pandas com os alunos
    df_cadastro = pd.DataFrame(alunos_cadastro)
    # Salva o DataFrame em uma planilha Excel
    excel_buffer = BytesIO()
    df_cadastro.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)  # Volta para o início do buffer

    # Limpa a lista temporária de alunos
    alunos_cadastro.clear()
    
    # Envia o arquivo Excel como resposta
    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=f'{arquivo_nome}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/salvar_planilha_upload')
def salvar_planilha_upload():
    global alunos_upload
    arquivo_nome = (alunos_upload[0]['Turma'])
    # Cria um DataFrame pandas com os alunos
    df_upload = pd.DataFrame(alunos_upload)
    # Salva o DataFrame em uma planilha Excel
    excel_buffer = BytesIO()
    df_upload.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)  # Volta para o início do buffer

    # Limpa a lista temporária de alunos
    alunos_upload.clear()
    
    # Envia o arquivo Excel como resposta
    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name=f'{arquivo_nome}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/cadastroTurmas')
def pagina_cadastro_turmas():
    return render_template('cadastroTurmas.html')

@app.route('/uploadTurmas')
def pagina_upload_turmas():
    return render_template('uploadTurmas.html')

@app.route('/limparDadosCadastro', methods=['POST'])
def limpar_dados_cadastro():

    global resultado_cadastro
    global alunos_cadastro
    
    try:
        resultado_cadastro = {}
        alunos_cadastro = []
        return jsonify(resultado_cadastro)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/limparDadosUpload', methods=['POST'])
def limpar_dados_upload():
    global resultado_upload
    global alunos_upload

    try:
        resultado_upload = {}  # Redefine resultado_upload como um dicionário vazio
        alunos_upload = []     # Limpa a lista de alunos
        return jsonify(resultado_upload)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_excel', methods=['GET'])
def download_excel():
    # Cria um novo workbook do Excel
    wb = Workbook()
    # Ativa a primeira planilha
    ws = wb.active

    # Adiciona cabeçalhos
    headers = ['Nome da Instituição','Turma','Nome Cidadão','Data de nascimento', 'Data do acompanhamento', 'Sexo', 'Peso(kg)', 'Altura(cm)']
    ws.append(headers)

    # Protege as células dos cabeçalhos
    for row in ws.iter_rows(min_row=1, max_row=1):
        for cell in row:
            cell.protection = Protection(locked=True)

    # Salva o arquivo temporário
    temp_file = 'dados_crianca.xlsx'
    wb.save(temp_file)

    # Retorna o arquivo Excel para download
    return send_file(temp_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
