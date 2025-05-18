import streamlit as st
from PIL import Image
import base64
from pathlib import Path # Importar Path

# Função para carregar o CSS
def load_css(file_name="biblioteca_style.css"):
    # Constrói o caminho absoluto para o arquivo CSS
    # Ele assume que o arquivo CSS está na mesma pasta que este script Python (biblioteca.py)
    css_path = Path(__file__).parent / file_name
    try:
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo CSS '{css_path}' não encontrado. Verifique o caminho e a localização do arquivo.")
    except Exception as e:
        st.error(f"Erro ao carregar CSS: {e}")

# Configuração da página
st.set_page_config(page_title="Biblioteca Arcana - Baú de Ingrediente", layout="centered", initial_sidebar_state="collapsed")

# Carrega o CSS (agora com o caminho corrigido)
load_css("biblioteca_style.css")

# --- Cabeçalho (sem navegação interna) ---
# A logo e o título principal da página
try:
    # Tenta carregar a logo. Ajuste o caminho se sua pasta 'assets' estiver em outro lugar
    # relativo ao diretório raiz do seu app (onde app.py está).
    # Se app.py está na raiz e assets é uma pasta na raiz: "assets/logo.png"
    # Se este script (biblioteca.py) está em 'pages' e 'assets' está na raiz,
    # o caminho relativo a partir da raiz do projeto é 'assets/logo.png'
    # Para Path(__file__), você pode precisar de ../assets/logo.png se assets está um nível acima de 'pages'
    
    # Assumindo que 'assets' está no mesmo nível que 'app.py' (raiz do projeto)
    # e 'pages' é uma subpasta.
    project_root = Path(__file__).parent.parent # Volta um nível de 'pages' para a raiz do projeto
    logo_path = project_root / "assets" / "logo.png"

    with open(logo_path, "rb") as img_file:
        logo_base64 = base64.b64encode(img_file.read()).decode()
    
    header_html = f"""
    <div class="custom-header">
        <div class="header-content-single">
            <div class="logo-title">
                <img src="data:image/png;base64,{logo_base64}" alt="Logo Baú de Ingrediente" class="logo-img">
                <span class="page-main-title">📜Biblioteca Arcana: Tomos de Sabedoria📜</span>
            </div>
        </div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

except FileNotFoundError:
    st.warning(f"Logo '{logo_path}' não encontrada. O header pode não exibir a imagem corretamente.")
    # Fallback sem logo se não encontrada
    st.markdown("""
    <div class="custom-header">
        <div class="header-content-single">
            <div class="logo-title">
                <span class="page-main-title">Baú de Ingrediente</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# --- Seção Principal da Biblioteca ---

#st.markdown('<span class="biblioteca-title-st">Biblioteca Arcana: Tomos de Sabedoria</span>', unsafe_allow_html=True)
st.markdown("""
    <p class="biblioteca-intro-st">Explore os conhecimentos ancestrais e modernos sobre a arte de conservar e aproveitar ingredientes. Clique em um tomo para desvendar seus segredos!</p>
""", unsafe_allow_html=True)

# --- Grade de Tomos ---
# Usaremos st.expander para simular os cards colapsáveis

# Tomo 1: Conservação
with st.expander("📜 O Segredo da Conservação Eterna - Desvende rituais e técnicas milenares para preservar ingredientes contra a passagem do tempo."):
    st.markdown("""
    <div class="tomo-detailed-content-st">
        <p>Saudações, valorosos aventureiros da culinária e guardiões de despensas!</p>
        <p>Neste tomo ancestral, compilamos os segredos mais bem guardados pelos antigos mestres do aproveitamento. Aqueles que sabiam que a verdadeira riqueza não reside apenas na coleta abundante, mas na capacidade de preservar os frutos do trabalho contra a inevitável marcha do tempo e a ganância da decadência.</p>
        <p>Aqui, você desvendará os rituais e técnicas que transformam ingredientes perecíveis em relíquias duradouras, garantindo que seu Baú de Ingrediente esteja sempre repleto de recursos, prontos para serem forjados em fórmulas épicas a qualquer momento.</p>

#### O Ritual da Secagem ao Vento Estelar

Uma das magias mais antigas, a secagem, invoca o poder do ar e do sol (ou, em tempos de escuridão, o calor controlado de forjas arcanas) para retirar a umidade que alimenta a ruína.

* **Ervas e Folhas Místicas:** Pendure feixes em locais arejados e sombrios, longe da luz direta que pode drenar sua essência vital. O vento levará a umidade, deixando para trás o sabor concentrado e o aroma potente. Guarde em sacos de tecido ou potes de barro selados.
* **Frutos e Raízes Resistentes:** Corte em fatias finas para acelerar o processo. Espalhe sobre telas ou bandejas e exponha ao calor suave. Quando estiverem quebradiços, estarão prontos para serem armazenados em locais secos.

#### O Encantamento da Salmoura Protetora

A magia do sal, um mineral sagrado de purificação e preservação, cria barreiras impenetráveis contra os agentes da decadência.

* **Carnes e Peixes:** Cubra completamente com sal grosso, garantindo que cada centímetro esteja protegido. O sal extrairá a umidade e criará um ambiente inóspito para micro-organismos. Após o processo, o excesso de sal pode ser removido. Armazene em recipientes herméticos.
* **Vegetais Crocantes:** Uma solução de água e sal (salmoura) pode ser usada para conservar vegetais como pepinos e azeitonas. O processo de fermentação que pode ocorrer na salmoura (veja o próximo ritual!) adiciona camadas complexas de sabor e nutrientes.

#### A Alquimia da Fermentação Selvagem

Este ritual invoca as forças ocultas da transformação, onde micro-organismos benevolentes convertem açúcares em ácidos, criando um ambiente autopreservador e liberando sabores e aromas fascinantes.

* **Vegetais Diversos:** Repolho (para Kraut Mágico), pepinos (para Picles da Resiliência), cenouras e outros podem ser finamente picados ou fatiados e misturados com sal. A pressão libera seus próprios líquidos, criando a salmoura onde a mágica acontece. Armazene em potes de vidro com peso para mantê-los submersos.
* **Grãos e Laticínios:** Culturas de bactérias e leveduras podem transformar leite em iogurte (Néctar Fermentado) ou kefir, e grãos em massas azedas (Pão da Longevidade).

#### O Selo da Cera Mágica (e Outros Invólucros)

Após a preparação, é crucial proteger seus ingredientes de influências externas.

* **Cera de Abelha:** Derreta cera pura e mergulhe queijos curados ou frutas secas para criar um selo protetor contra o ar e a umidade.
* **Potes de Vidro Herméticos:** Recipientes de vidro com tampas que criam vácuo são como baús de tesouro modernos para seus ingredientes conservados.
* **Envoltórios Naturais:** Folhas grandes, cascas e outros materiais naturais podem ser usados para envolver e proteger, especialmente em métodos de secagem.

#### A Câmara Fria da Estabilidade

Embora nem sempre "eterna", a conservação em baixas temperaturas retarda significativamente a decadência. Cavernas profundas, poços gelados ou, em tempos mais recentes, artefatos mágicos de refrigeração (geladeiras) são ideais.

* Mantenha ingredientes frescos e conservados em ambientes frios e estáveis para prolongar sua vida útil.

Dominar estes segredos não apenas garante um suprimento constante para suas aventuras culinárias, mas também honra o ciclo da natureza, transformando o que seria perdido em potencial e sabor.
    </div>
    """, unsafe_allow_html=True)

# Tomo 2: Alquimia
with st.expander("🧪 Tomo da Alquimia de Sobras - Aprenda a arte de transformar sobras e partes 'esquecidas' em novos e deliciosos pratos."):
    st.markdown("""
    <div class="tomo-detailed-content-st">
        <p>Bem-vindo, Alquimista da Cozinha! Este tomo revela a magia de transformar o que muitos descartam em ouro culinário.</p>
        <p>Cada casca, talo ou folha esquecida possui um potencial inexplorado. Com as técnicas corretas, você pode extrair sabores profundos, criar texturas surpreendentes e nutrir seu corpo e o planeta.</p>

#### Essências e Caldos Mágicos

Cascas de vegetais (cenoura, cebola, alho) e talos de ervas são a base perfeita para caldos ricos em sabor. Ferva-os lentamente para extrair sua essência vital.

#### Pós de Poder e Temperos Arcanos

Cascas de frutas cítricas podem ser secas e moídas para criar pós aromáticos. Talos de brócolis podem virar base para sopas cremosas. Folhas de beterraba podem ser refogadas como uma iguaria.

#### Reencarnação de Pães e Bolos

Pão amanhecido pode se tornar croutons crocantes, farinha de rosca para empanados mágicos, ou a base para pudins e torradas. Bolos secos podem ser transformados em "pop" de bolo ou bases para sobremesas.

#### Raízes e Talos Resilientes

Talo de couve, brócolis ou couve-flor podem ser picados finamente e adicionados a refogados, sopas ou saladas. A parte branca do alho-poró, muitas vezes descartada, é cheia de sabor.

Dominando a Alquimia de Sobras, você não apenas reduz o desperdício, mas descobre um universo de novos sabores e texturas, elevando sua culinária a um novo patamar.
    </div>
    """, unsafe_allow_html=True)

# Tomo 3: Identificação
with st.expander("🔍 Guia de Identificação de Tesouros - Um compêndio visual para identificar ingredientes no auge de seu potencial e reconhecer sinais de desperdício a ser evitado."):
    st.markdown("""
    <div class="tomo-detailed-content-st">
        <p>Guardião(ã) de Despensas, este guia é seu olho de águia na busca por ingredientes valiosos e na prevenção da decadência.</p>
        <p>Saber identificar o potencial de um ingrediente e os sinais de que ele está prestes a se perder é a primeira linha de defesa contra o desperdício.</p>

#### Sinais de Vitalidade (Tesouros a Serem Usados)

* Brilho Sutil: Frutas e vegetais com um brilho natural geralmente indicam frescor.
* Firmeza: Ingredientes firmes ao toque, sem partes moles ou enrugadas (a menos que seja característico deles!).
* Aroma Vibrante: Ervas e especiarias com cheiro forte e característico.
* Cores Ricas: Cores vivas e profundas indicam nutrientes e frescor.

#### Sinais de Alerta (Potencial Oculto ou Perigo Iminente)

* Leve Murchamento: Folhas ou vegetais levemente murchos ainda podem ser revividos em água gelada ou usados em sopas e refogados.
* Pequenas Manchas: Pequenas manchas ou descolorações podem ser removidas, e o restante do ingrediente ainda é utilizável.
* Partes Danificadas: Remova as partes danificadas e utilize o restante.

#### Sinais de Perda (A Decadência Completa)

* Mofo Abundante: Sinais visíveis de mofo em grandes áreas (em alimentos não fermentados intencionalmente).
* Odor Desagradável: Cheiros fortes e putrefatos.
* Textura Viscosa ou Mole Excessiva: Perda completa de firmeza e textura.

Confie em seus sentidos e na sabedoria deste guia para tomar decisões informadas e garantir que nenhum tesouro culinário seja perdido para as sombras do desperdício.
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Fecha o biblioteca-container-st

# --- Rodapé ---
st.markdown("---")
st.markdown("""
<div class="footer-custom-st">
    <p>&copy; 2025 Baú de Ingrediente. Todos os direitos reservados. Forjado com Consciência e Aproveitamento.</p>
""", unsafe_allow_html=True)

# --- Chatbot Widget ---
try:
    project_root = Path(__file__).parent.parent
    chapeu_path = project_root / "assets" / "chapeu.png"
    with open(chapeu_path, "rb") as img_file:
        chapeu_base64 = base64.b64encode(img_file.read()).decode()
    chatbot_widget_html = f"""
    <div class="chatbot-widget-st" title="Converse com o Sábio do Aproveitamento!">
        <img src="data:image/png;base64,{chapeu_base64}" style="border-radius: 50%; object-fit: cover; width: 100%; height: 100%; max-width: 60px; max-height: 60px; display: block;" />
    </div>
    """
    st.markdown(chatbot_widget_html, unsafe_allow_html=True)
except FileNotFoundError:
    st.markdown("""
    <div class="chatbot-widget-st" title="Converse com o Sábio do Aproveitamento!">
         <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="white" viewBox="0 0 256 256"><path d="M208,80H172.32l-28.9-65.0 EligibleForAsPath eligibleForAsPath-group-id="0" eligibleForAsPath eligibleForAsPath-decoration-id="0" eligibleForAsPath eligibleForAsPath-eligibleForAsPath-id="0" d="m136,20.75a12,12,0,0,0-16,0L91.68,80H48a20,20,0,0,0-20,20V192a20,20,0,0,0,20,20H208a20,20,0,0,0,20-20V100A20,20,0,0,0,208,80Zm4,112H44V100A4,4,0,0,1,48,96H99.08a12,12,0,0,0,11.25-7.38L128,48.06l17.67,40.56A12,12,0,0,0,156.92,96H208a4,4,0,0,1,4,4Z"></path></svg>
    </div>
    """, unsafe_allow_html=True) # Placeholder SVG