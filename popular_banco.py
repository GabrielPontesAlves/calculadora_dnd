from app import Monstro, app, db


def popular():
    # Deleta os registros antigos para não duplicar caso rode duas vezes
    Monstro.query.delete()

    # Lista de monstros com a nova coluna 'descricao' alimentada com os dados dos livros
    monstros = [
        # --- MONSTROS ORIGINAIS ---
        Monstro(
            nome="Goblin", 
            nd=0.25, 
            tipo="Fada", 
            habitat="Floresta", 
            imagem="goblin.png",
            descricao="Goblins são pequenas criaturinhas maliciosas que se reúnem em tribos nas profundezas de florestas e cavernas. Eles são conhecidos por sua covardia em combate singular, preferindo táticas de emboscada, armadilhas cruéis e superioridade numérica para subjugar seus alvos."
        ),
        Monstro(
            nome="Orc", 
            nd=0.5, 
            tipo="Humanoide", 
            habitat="Montanha", 
            imagem="orc.png",
            descricao="Orcs são guerreiros ferozes e de constituição massiva que vivem para o combate. Eles veneram divindades da destruição e costumam pilhar assentamentos vulneráveis. Em termos de mecânica, sua habilidade de 'Agressivo' permite que se movam em direção aos inimigos com velocidade assustadora."
        ),
        Monstro(
            nome="Lobo Atroz", 
            nd=1.0, 
            tipo="Besta", 
            habitat="Floresta", 
            imagem="lobo_atroz.png",
            descricao="Versões gigantescas e ancestrais dos lobos comuns, os Lobos Atrozes são predadores alphas que caçam em alcateias perfeitamente coordenadas. Sua mordida poderosa é capaz de derrubar suas presas no chão, deixando-as vulneráveis a ataques subsequentes."
        ),
        Monstro(
            nome="Ogro", 
            nd=2.0, 
            tipo="Monstruosidade", # Ajustado para bater com seus filtros do select
            habitat="Masmorra", # Ajustado para bater com seus filtros do select
            imagem="ogro.png",
            descricao="Gigantescos, brutos e incrivelmente famintos. Ogros possuem inteligência limitada, mas compensam com uma força devastadora capaz de esmagar aventureiros com uma única investida de sua grande clava de madeira."
        ),
        Monstro(
            nome="Dragão Vermelho Jovem", 
            nd=10.0, 
            tipo="Dragão", 
            habitat="Montanha", 
            imagem="dragao_vermelho_jovem.png",
            descricao="O ápice do terror cromático. Mesmo jovem, um Dragão Vermelho possui uma arrogância sem limites e um sopro de fogo devastador capaz de incinerar grupos inteiros de aventureiros despreparados. Costumam fazer seus covis em vulcões ou picos montanhosos isolados."
        ),
        Monstro(
            nome="Pixie", 
            nd=0.25, 
            tipo="Fada",
            habitat="Floresta", 
            imagem="pixie.png",
            descricao="Pixies se assemelham a minúsculos elfos com asas de libélula. Criaturas naturalmente tímidas, elas usam sua magia de ilusão para ficar invisíveis e guiar viajantes perdidos ou pregar peças inofensivas em intrusos em suas florestas iluminadas pelo luar."
        ),
        Monstro(
            nome="Cocatriz", 
            nd=0.5, 
            tipo="Monstruosidade", 
            habitat="Pântano", 
            imagem="cocatriz.png",
            descricao="Uma abominação bizarra que mistura traços de uma ave com cauda de réptil. Embora pequena, a Cocatriz é temida devido ao seu bico infundido com magia de petrificação; um único arranhão ou mordida desta fera pode começar a transformar a carne da vítima em pedra sólida."
        ),
        Monstro(
            nome="Mímico", 
            nd=2.0, 
            tipo="Monstruosidade", 
            habitat="Masmorra", 
            imagem="mimico.png",
            descricao="O maior pesadelo dos gananciosos. Mímicos são predadores metamorfos capazes de alterar sua estrutura molecular para imitar objetos inanimados de madeira e pedra, assumindo frequentemente a forma de baús de tesouro, portas ou estátuas para atrair aventureiros desavisados."
        ),
        Monstro(
            nome="Comandante Orc", 
            nd=4.0, 
            tipo="Humanoide", 
            habitat="Montanha", 
            imagem="comandante_orc.png",
            descricao="Um veterano calejado que subiu ao topo da hierarquia tribal através de pura brutalidade e perspicácia tática. O Comandante Orc ruge ordens que inspiram seus subordinados a lutarem além de seus limites, portando armaduras pesadas e machados de batalha massivos."
        ),
        Monstro(
            nome="Kitsune", 
            nd=4.0, 
            tipo="Fada", # [HOMEBREW] Adaptado para dnd 5e
            habitat="Floresta", 
            imagem="kitsune.png",
            descricao="Uma criatura mística e ancestral com traços de raposa e habilidades metamórficas. Kitsunes são conjuradoras natas, manipulando ilusões complexas e chamas espirituais azuladas (Fogo de Raposa) para confundir e punir aqueles que profanam seus santuários ocultos."
        ),
        Monstro(
            nome="Sucubbus", 
            nd=4.0, 
            tipo="Morto-Vivo", # Encaixada aqui pelo teor planar/sombrio do seu filtro
            habitat="Masmorra", 
            imagem="sucubbus.png",
            descricao="Um ser infernal de beleza estonteante focado na corrupção de almas mortais. A Sucubbus não depende de força física, mas sim de sussurros hipnóticos, beijos fatais e telepatia, sendo capaz de controlar a mente do guerreiro mais forte e voltá-lo contra seus próprios aliados."
        ),
        Monstro(
            nome="Lagarto de Magma", 
            nd=6.0, 
            tipo="Besta", # [HOMEBREW] Adaptado para dnd 5e
            habitat="Montanha", 
            imagem="lagarto_magma.png",
            descricao="Um réptil colossal cujo habitat natural são rios de lava e caldeiras vulcânicas. Sua carapaça é feita de rocha obsidiana fundida e ele é capaz de expelir rajadas de magma fervente, incinerando instantaneamente metal, madeira e ossos."
        ),
        Monstro(
            nome="Ciclope", 
            nd=6.0, 
            tipo="Monstruosidade", 
            habitat="Montanha", 
            imagem="ciclope.png",
            descricao="Gigantes de um olho só isolados e territoriais. Embora sua percepção de profundidade seja severamente limitada (o que prejudica seus ataques à distância), a força bruta de um Ciclope em combate corpo a corpo ao brandir uma árvore arrancada é o suficiente para partir escudos ao meio."
        ),
        Monstro(
            nome="Golem (Guardião de Ruínas)", 
            nd=10.0, 
            tipo="Construto", # Encaixado aqui como construto exótico
            habitat="Masmorra", 
            imagem="golem_ruinas.png",
            descricao="Um enorme autômato esculpido em blocos de pedra rúnica ancestral. Criado por civilizações há muito esquecidas para proteger tesouros e templos, este Golem não conhece o medo ou a fadiga, esmagando invasores com punhos de pedra pesados e ignorando a maioria das magias básicas."
        ),
        Monstro(
            nome="Wendigo", 
            nd=8.0, 
            tipo="Morto-Vivo", # [HOMEBREW] Adaptado perfeitamente para dnd 5e
            habitat="Pântano", 
            imagem="wendigo.png",
            descricao="Uma entidade cadavérica nascida da fome extrema e de atos de canibalismo em locais amaldiçoados. O Wendigo move-se silenciosamente por entre a névoa, emitindo guinchos que causam pânico paralisante. Ele é movido por uma fome eterna que nunca é saciada, caçando aventureiros sem piedade."
        ),
        Monstro(
            nome="Gigante de Fogo", 
            nd=9.0, 
            tipo="Gigante", # Encaixado como variação de gigante poderoso
            habitat="Montanha", 
            imagem="gigante_fogo.png",
            descricao="Mestres da forja e estrategistas militares implacáveis. Gigantes de Fogo vivem em fortalezas construídas no interior de vulcões, vestindo pesadas armaduras de placas de aço negro forjadas por eles mesmos e arremessando rochas incandescentes contra exércitos inteiros."
        ),
        Monstro(
            nome="Dragão Vermelho Ancião", 
            nd=24.0, 
            tipo="Dragão", 
            habitat="Montanha", 
            imagem="dragao_vermelho_anciao.png",
            descricao="O ápice do poder e da destruição no multiverso. Com séculos de idade, este Dragão Vermelho governa territórios inteiros a partir do topo do vulcão mais alto. Seu sopro de fogo é uma tempestade apocalíptica capaz de derreter fortalezas inteiras de pedra em segundos. Um verdadeiro desafio de nível Lendário."
        )
    ]

    # Salva tudo de uma vez no banco de dados
    db.session.add_all(monstros)
    db.session.commit()
    print("⚔️ Bestiário do Mestre populado com sucesso e com as lores inclusas!")

if __name__ == '__main__':
    with app.app_context():
        popular()