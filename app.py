import os
import json
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)

# Configuração do Banco de Dados SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'rpg_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave_secreta_do_mestre_rpg_123'
db = SQLAlchemy(app)

# --- MODELO DO BANCO DE DADOS ---

class Monstro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nd = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    habitat = db.Column(db.String(50), nullable=False)
    imagem = db.Column(db.String(200), default='default_monstro.jpg')
    descricao = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Monstro {self.nome}>'


class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    qtd_jogadores = db.Column(db.Integer, nullable=False)
    nivel_jogadores = db.Column(db.Integer, nullable=False)
    encontros = db.relationship('Encontro', backref='party', lazy=True)

    def __repr__(self):
        return f'<Party {self.nome}>'


class Encontro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    dificuldade = db.Column(db.String(50), nullable=False)
    monstros_json = db.Column(db.Text, nullable=False)
    party_id = db.Column(db.Integer, db.ForeignKey('party.id'), nullable=False)

    def __repr__(self):
        return f'<Encontro {self.nome}>'

# --- LÓGICA DE CÁLCULO ---
def calcular_encontro(lista_nd_monstros, qtd_jogadores, nivel_jogadores):
    nd_total_monstros = sum(lista_nd_monstros)
    nj_total_base = qtd_jogadores * nivel_jogadores
    
    if nivel_jogadores >= 5:
        nj_final = nj_total_base / 2
    else:
        nj_final = nj_total_base / 4
        
    if nd_total_monstros >= nj_final:
        return "Mortal"
    elif nd_total_monstros >= (nj_final * 0.7):
        return "Difícil"
    else:
        return "Fácil"

# --- ROTAS ---

# 1. Página Inicial (Filtros e Biblioteca)
@app.route('/')
def index():
    filtro_tipo = request.args.get('tipo', '')
    filtro_habitat = request.args.get('habitat', '')
    
    if request.referrer and url_for('index', _external=True) not in request.referrer:
        if 'editando_encontro_id' not in session:
            session.pop('carrinho', None)
    
    busca = Monstro.query
    if filtro_tipo:
        busca = busca.filter_by(tipo=filtro_tipo)
    if filtro_habitat:
        busca = busca.filter_by(habitat=filtro_habitat)
        
    todos_os_monstros = busca.all()
    modo_edicao = 'editando_encontro_id' in session
    
    return render_template('index.html', 
                           monstros=todos_os_monstros, 
                           modo_edicao=modo_edicao,
                           filtro_tipo=filtro_tipo,
                           filtro_habitat=filtro_habitat)

# 2. Carrega um encontro antigo no carrinho e joga o usuário na Home para alterar as criaturas
@app.route('/carregar-encontro-para-editar/<int:id>')
def carregar_encontro_para_editar(id):
    encontro = Encontro.query.get_or_404(id)
    nomes_monstros = json.loads(encontro.monstros_json)
    
    carrinho_preenchido = []
    for nome in nomes_monstros:
        m = Monstro.query.filter_by(nome=nome).first()
        if m:
            carrinho_preenchido.append({'id': m.id, 'nome': m.nome, 'nd': m.nd})
            
    session['carrinho'] = carrinho_preenchido
    session['editando_encontro_id'] = encontro.id
    
    return redirect(url_for('index'))

# 3. Salva as alterações feitas no encontro pulando a tela de configuração de jogadores
@app.route('/salvar-edicao-encontro')
def salvar_edicao_encontro():
    encontro_id = session.get('editando_encontro_id')
    carrinho = session.get('carrinho', [])
    
    if not encontro_id or not carrinho:
        return redirect(url_for('index'))
        
    encontro = Encontro.query.get_or_404(encontro_id)
    party = Party.query.get(encontro.party_id)
    
    lista_nd_monstros = [item['nd'] for item in carrinho]
    nova_dificuldade = calcular_encontro(lista_nd_monstros, party.qtd_jogadores, party.nivel_jogadores)
    
    lista_nomes_monstros = [item['nome'] for item in carrinho]
    encontro.dificuldade = nova_dificuldade
    encontro.monstros_json = json.dumps(lista_nomes_monstros)
    
    db.session.commit()
    
    # 🔥 [CORREÇÃO]: NÃO removemos mais o 'editando_encontro_id' aqui! 
    # Deixamos ele ativo na sessão para que o mestre possa ajustar repetidas vezes consecutivas.
    
    return render_template('resultado.html', 
                           nome_party=party.nome,
                           nome_encontro=encontro.nome,
                           qtd_players=party.qtd_jogadores,
                           nivel_players=party.nivel_jogadores,
                           resultado=nova_dificuldade,
                           carrinho=carrinho)

# 4. Adiciona um monstro ao carrinho
@app.route('/adicionar/<int:monstro_id>')
def adicionar_monstro(monstro_id):
    if 'carrinho' not in session:
        session['carrinho'] = []
    
    monstro = Monstro.query.get_or_404(monstro_id)
    quantidade = int(request.args.get('quantidade', 1))
    filtro_tipo = request.args.get('tipo', '')
    filtro_habitat = request.args.get('habitat', '')
    
    carrinho_atual = session['carrinho']
    for _ in range(quantidade):
        carrinho_atual.append({
            'id': monstro.id,
            'nome': monstro.nome,
            'nd': monstro.nd
        })
        
    session['carrinho'] = carrinho_atual
    return redirect(url_for('index', tipo=filtro_tipo, habitat=filtro_habitat))

# 5. Remove um monstro do carrinho
@app.route('/remover/<int:monstro_id>')
def remover_monstro(monstro_id):
    if 'carrinho' in session:
        carrinho_atual = session['carrinho']
        for item in carrinho_atual:
            if item['id'] == monstro_id:
                carrinho_atual.remove(item)
                break
        session['carrinho'] = carrinho_atual
    return redirect(url_for('index'))

# 6. Limpa o carrinho para criar um encontro totalmente NOVO do zero
@app.route('/limpar-carrinho')
def limpar_carrinho():
    session.pop('carrinho', None)
    session.pop('editando_encontro_id', None) # Aqui limpa tudo perfeitamente
    return redirect(url_for('index'))

# 7. Tela de seleção/configuração de Party para novos encontros
@app.route('/jogadores', methods=['GET', 'POST'])
def dados_jogadores():
    carrinho = session.get('carrinho', [])
    if not carrinho:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        nome_encontro = request.form.get('nome_encontro', 'Encontro Sem Nome')
        party_id_selecionada = request.form.get('party_id')
        
        if party_id_selecionada and party_id_selecionada != 'nova':
            party = Party.query.get(int(party_id_selecionada))
            nome_party = party.nome
            qtd_players = party.qtd_jogadores
            nivel_players = party.nivel_jogadores
        else:
            nome_party = request.form.get('nome_party', 'Grupo Sem Nome')
            qtd_players = int(request.form.get('qtd_players', 4))
            nivel_players = int(request.form.get('nivel_players', 1))
            
            party = Party(nome=nome_party, qtd_jogadores=qtd_players, nivel_jogadores=nivel_players)
            db.session.add(party)
            db.session.commit()
        
        lista_nd_monstros = [item['nd'] for item in carrinho]
        resultado_dificuldade = calcular_encontro(lista_nd_monstros, qtd_players, nivel_players)
        
        lista_nomes_monstros = [item['nome'] for item in carrinho]
        novo_encontro = Encontro(
            nome=nome_encontro,
            dificuldade=resultado_dificuldade,
            monstros_json=json.dumps(lista_nomes_monstros),
            party_id=party.id
        )
        db.session.add(novo_encontro)
        db.session.commit()
        
        session['editando_encontro_id'] = novo_encontro.id
        
        return render_template('resultado.html', 
                               nome_party=party.nome,
                               nome_encontro=nome_encontro,
                               qtd_players=qtd_players,
                               nivel_players=nivel_players,
                               resultado=resultado_dificuldade,
                               carrinho=carrinho)

    parties_salvas = Party.query.all()
    return render_template('jogadores.html', parties=parties_salvas)
    
# ==========================================
#         GERENCIAMENTO DE PARTYS
# ==========================================

@app.route('/lista-partys')
def lista_partys():
    # 🌟 [PREVENÇÃO]: Se o usuário navegou para o menu de gerenciamento, limpa o estado de edição anterior
    session.pop('editando_encontro_id', None)
    
    todas_partys = Party.query.all()
    return render_template('lista_partys.html', partys=todas_partys)

@app.route('/editar-party/<int:id>', methods=['GET', 'POST'])
def editar_party(id):
    party = Party.query.get_or_404(id)
    if request.method == 'POST':
        party.nome = request.form.get('nome')
        party.qtd_jogadores = max(1, int(request.form.get('qtd')))
        nivel_enviado = int(request.form.get('nivel'))
        party.nivel_jogadores = max(1, min(20, nivel_enviado))
        
        db.session.commit()
        return redirect(url_for('lista_partys'))
    return render_template('editar_party.html', party=party)

@app.route('/deletar-party/<int:id>')
def deletar_party(id):
    party = Party.query.get_or_404(id)
    Encontro.query.filter_by(party_id=id).delete()
    db.session.delete(party)
    db.session.commit()
    return redirect(url_for('lista_partys'))


# ==========================================
#        GERENCIAMENTO DE ENCONTROS
# ==========================================

@app.route('/lista-encontros')
def lista_encontros():
    # 🌟 [PREVENÇÃO]: Se voltou para a listagem geral, limpa o estado ativo de edição atual
    session.pop('editando_encontro_id', None)
    session.pop('carrinho', None)
    
    todos_encontros = Encontro.query.all()
    return render_template('lista_encontros.html', encontros=todos_encontros, json=json)

@app.route('/deletar-encontro/<int:id>')
def deletar_encontro(id):
    encontro = Encontro.query.get_or_404(id)
    db.session.delete(encontro)
    db.session.commit()
    return redirect(url_for('lista_encontros'))


import os

# ... resto do seu código ...

if __name__ == '__main__':
    # A Render define uma variável de ambiente chamada PORT. Se não achar, usa a 5000 (local)
    porta = int(os.environ.get("PORT", 5000))
    # O host '0.0.0.0' é obrigatório para o site ficar público no servidor
    app.run(host='0.0.0.0', port=porta)