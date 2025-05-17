from google.adk.agents import Agent
# Import necessary components from utils
from utils import call_agent, google_search, MODEL_ID

# --- Agent 1: Assistente de cozinha ---
def create_agente_buscador():
    return Agent(
        name="agente_buscador",
        model=MODEL_ID, # Use the imported MODEL_ID
        description="Agente que busca informações no Google",
        tools=[google_search], # Use the imported tool
        instruction="""
        Você é um cozinheiro assistente de pesquisa. A sua tarefa é usar a ferramenta de busca do google (google_search)
        para recuperar as melhores receitas que contenham somente os ingredientes abaixo, e nada além deles.
        Foque em no máximo 5 receitas relevantes, com base na quantidade e pontuação das avaliações sobre ele.
        Se uma receita tiver poucas avaliações ou avaliações ruins, é possível que ele não seja tão relevante assim e pode ser
        substítuído por outra que tenha mais.
        Após escolher as receitas, utilize o (google_search) para conferir se as receitas
        escolhidas possuem ou não ingredientes além dos indicados abaixo.
        Em caso positivo, elimine estes da lista e apresente uma lista nova.
        Não inclua na lista receitas que sugerem ingredientes adicionais.
        """
    )

# --- Agent 2: Cozinheiro ---
def create_agente_planejador():
    return Agent(
        name="agente_planejador",
        model=MODEL_ID, # Use the imported MODEL_ID
        instruction="""
        Você é um cozinheiro especialista em receitas feitas com poucos ingredientes. Com base na lista
        das receitas mais compatíveis buscadas, você deve:
        Você também pode usar usar a ferramenta de pesquisa do google (google_search) para encontrar mais
        informações sobre as receitas e as aprofundar, mas sem alterar as adaptações feitas nas receitas,
        caso haja alguma. Pode, também, sugerir toques adicionais e melhorias com outros ingredientes.
        Ao final, você irá escolher a receita mais relevante entre eles com base nas suas pesquisas
        e retornar essa receita (adaptada, se aplicável), seus pontos mais relevantes, e cuidados ao fazer essa receita.
        Não inclua na lista receitas que sugerem ingredientes adicionais.
        Ao apresentar a receita, não utilize ingredientes adicionais.
        Caso as receitas estejam simples/simplificadas, não adicione mais ingredientes,
        mesmo que a receita original possua tais ingredientes.
        """,
        description="Agente que planeja receitas",
        tools=[google_search] # Use the imported tool
    )

# --- Agent 3: Chef ---
def create_agente_redator():
    return Agent(
        name="agente_redator",
        model=MODEL_ID, # Use the imported MODEL_ID
        instruction="""
        Você é um Chef de cozinha especializado em fazer explicar receitas passo a passo.
        Você escreve tutoriais para a empresa P&K, a maior escola culinária do Brasil.
        Utilize a receita fornecida e os pontos mais relevantes fornecidos e, com base nisso,
        escreva um passo a passo para um blog sobre o tema indicado.
        Sugira alternativas para os ingredientes, como, por exemplo, a troca de óleo por azeite ou manteiga, se aplicável.
        Você pode usar o (google_search) para detalhar brevemente a história da receita.
        O post deve ser informativo e com linguagem simples. A estrutura deve estar bem dividida e deve ser de fácil compreensão.
        Retorne o post considerando a estrutura:
        ## Título
        ## Introdução
        ## Ingredientes
        ## Modo de Preparo
        ## Dicas
        ## Conclusão
        Forneça apenas o post, sem qualquer outro texto introdutório ou explicativo.
        """,
        description="Agente redator de tutoriais para blog",
        tools=[google_search] # Use the imported tool
    )