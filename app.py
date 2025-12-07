import streamlit as st
import pandas as pd
import altair as alt

# --------------------------------------------
# 🔧 Funções auxiliares
# --------------------------------------------

def formatar_moeda(valor):
    # Recebe um número (float/int) e retorna uma string formatada em real brasileiro.
    # Exemplo: 2100.5 -> 'R$ 2.100,50'
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_numero(valor, sufixo=""):
    # Formata um número com separador de milhar e decimal no padrão brasileiro
    # e adiciona um sufixo (por exemplo ' L' para litros).
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + sufixo

# --------------------------------------------
# ⛽ Função de Cálculo — Combustível
# --------------------------------------------

def calcular_combustivel(distancia_total, consumo_km_litro, preco_combustivel, num_viajantes):
    # Calcula litros necessários e custos relativos ao combustível.
    # Validações básicas: nenhum dos valores pode ser menor ou igual a zero.
    if distancia_total <= 0 or consumo_km_litro <= 0 or preco_combustivel <= 0 or num_viajantes <= 0:
        return None

    # Litros necessários para percorrer a distância total
    litros_necessarios = distancia_total / consumo_km_litro
    # Custo total de combustível para a viagem
    custo_total = litros_necessarios * preco_combustivel
    # Custo dividido por viajante
    custo_por_pessoa = custo_total / num_viajantes

    # Retorna valores formatados para exibição na interface
    return {
        "distancia_total": distancia_total,
        "litros_necessarios": formatar_numero(litros_necessarios, " L"),
        "preco_combustivel": formatar_moeda(preco_combustivel),
        "custo_total_combustivel": formatar_moeda(custo_total),
        "custo_por_pessoa_combustivel": formatar_moeda(custo_por_pessoa),
        "num_viajantes": num_viajantes
    }

# --------------------------------------------
# ✈️ Função de Cálculo — Viagem Completa
# --------------------------------------------

def calcular_custos_completos(destino, num_dias, num_viajantes, custo_acomodacao_noite,
                              custo_transporte_total, custo_alimentacao_dia_pessoa,
                              custo_atividades_total, percentual_reserva):
    # Calcula o orçamento completo da viagem (acomodação, transporte, alimentação e atividades)
    # - `destino`: string com o nome do destino
    # - `num_dias`: número de dias da viagem
    # - `num_viajantes`: quantidade de pessoas
    # - `custo_acomodacao_noite`: valor do quarto por noite (total)
    # - `custo_transporte_total`: soma dos custos de transporte (voo, trem etc.)
    # - `custo_alimentacao_dia_pessoa`: custo médio de alimentação por dia por pessoa
    # - `custo_atividades_total`: soma dos custos de passeios/atividades
    # - `percentual_reserva`: percentual de reserva/emergência aplicado ao subtotal

    # Validações: dias e viajantes precisam ser maiores que zero
    if num_dias <= 0 or num_viajantes <= 0:
        return None

    # Total gasto com acomodação (por todas as noites)
    total_acomodacao = custo_acomodacao_noite * num_dias
    # Total gasto com alimentação (por dia por pessoa * dias * pessoas)
    total_alimentacao = custo_alimentacao_dia_pessoa * num_dias * num_viajantes

    # Subtotal antes da reserva de emergência
    subtotal = total_acomodacao + custo_transporte_total + total_alimentacao + custo_atividades_total
    # Valor da reserva de emergência em reais
    reserva = subtotal * (percentual_reserva / 100)
    # Custo final já com a reserva
    custo_total_final = subtotal + reserva

    # Retorna todos os valores já formatados para exibição na UI
    return {
        "destino": destino.upper(),
        "num_dias": num_dias,
        "num_viajantes": num_viajantes,
        "total_acomodacao": formatar_moeda(total_acomodacao),
        "total_alimentacao": formatar_moeda(total_alimentacao),
        "custo_transporte_total": formatar_moeda(custo_transporte_total),
        "custo_atividades_total": formatar_moeda(custo_atividades_total),
        "subtotal": formatar_moeda(subtotal),
        "percentual_reserva": f"{percentual_reserva:.0f}%",
        "reserva": formatar_moeda(reserva),
        "custo_total_final": formatar_moeda(custo_total_final),
        "custo_por_pessoa": formatar_moeda(custo_total_final / num_viajantes),
        "custo_por_dia_pessoa": formatar_moeda((custo_total_final / num_viajantes) / num_dias)
    }

# --------------------------------------------
# 🎨 Configuração da Página
# --------------------------------------------

st.set_page_config(page_title="Simulador de Custos de Viagem", layout="wide")
st.title("✈️ Simulador Inteligente de Custos de Viagem")
st.caption("Calcule de forma rápida e fácil o custo total da viagem, combustível e custo por pessoa.")

# --------------------------------------------
# MENU LATERAL
# --------------------------------------------

escolha = st.sidebar.selectbox(
    "Escolha o tipo de simulação:",
    ("Simulação Completa da Viagem", "Simulação de Custo de Combustível")
)

# ============================================
# 🔹 1 — SIMULAÇÃO COMPLETA DA VIAGEM
# ============================================

if escolha == "Simulação Completa da Viagem":

    st.header("🧳 Simulação Completa da Viagem")

    col1, col2, col3 = st.columns(3)
    destino = col1.text_input("Destino:", "Paris")
    num_dias = col2.number_input("Número de dias:", min_value=1, value=7)
    num_viajantes = col3.number_input("Número de viajantes:", min_value=1, value=2)

    st.subheader("💰 Custos da Viagem (R$)")
    colA, colB = st.columns(2)
    custo_acomodacao_noite = colA.number_input("Acomodação por noite (quarto total):", min_value=0.0, value=300.0)
    custo_transporte_total = colB.number_input("Transporte total (voos, trens etc.):", min_value=0.0, value=2500.0)

    colC, colD = st.columns(2)
    custo_alimentacao_dia_pessoa = colC.number_input("Alimentação por dia por pessoa:", min_value=0.0, value=80.0)
    custo_atividades_total = colD.number_input("Atividades e passeios (total):", min_value=0.0, value=500.0)

    percentual_reserva = st.slider("Reserva de emergência (%)", 0, 100, 10)

    if st.button("Calcular Custo Total"):
        resultado = calcular_custos_completos(
            destino, num_dias, num_viajantes, custo_acomodacao_noite,
            custo_transporte_total, custo_alimentacao_dia_pessoa,
            custo_atividades_total, percentual_reserva
        )

        if resultado:
            st.success(f"Orçamento de viagem para **{resultado['destino']}** gerado com sucesso!")

            st.subheader("📌 Resumo Geral")
            colR1, colR2 = st.columns(2)
            colR1.metric("Custo Total da Viagem", resultado["custo_total_final"])
            colR2.metric("Custo por Pessoa", resultado["custo_por_pessoa"])

            # ---------------------------
            # 📊 Tabela e Gráfico
            # ---------------------------
            st.markdown("---")
            st.subheader("📊 Detalhamento dos Custos")

            df = pd.DataFrame({
                "Categoria": [
                    f"Acomodação ({resultado['num_dias']} noites)",
                    "Transporte",
                    f"Alimentação ({resultado['num_viajantes']} pessoas)",
                    "Atividades",
                    f"Reserva ({resultado['percentual_reserva']})"
                ],
                "Custo (R$)": [
                    resultado["total_acomodacao"],
                    resultado["custo_transporte_total"],
                    resultado["total_alimentacao"],
                    resultado["custo_atividades_total"],
                    resultado["reserva"]
                ]
            })

            st.table(df)

            # Valores numéricos para o gráfico
            valores_numericos = [
                float(resultado["total_acomodacao"].replace("R$ ", "").replace(".", "").replace(",", ".")),
                float(resultado["custo_transporte_total"].replace("R$ ", "").replace(".", "").replace(",", ".")),
                float(resultado["total_alimentacao"].replace("R$ ", "").replace(".", "").replace(",", ".")),
                float(resultado["custo_atividades_total"].replace("R$ ", "").replace(".", "").replace(",", ".")),
                float(resultado["reserva"].replace("R$ ", "").replace(".", "").replace(",", "."))
            ]

            df_grafico = pd.DataFrame({
                "Categoria": [
                    f"Acomodação ({resultado['num_dias']} noites)",
                    "Transporte",
                    f"Alimentação ({resultado['num_viajantes']} pessoas)",
                    "Atividades",
                    f"Reserva ({resultado['percentual_reserva']})"
                ],
                "Custo": valores_numericos
            })

            chart = alt.Chart(df_grafico).mark_bar().encode(
                x="Categoria",
                y="Custo"
            ).properties(height=400)

            st.altair_chart(chart, use_container_width=True)

            st.info(f"💡 Custo por dia por pessoa: **{resultado['custo_por_dia_pessoa']}**")

# ============================================
# 🔹 2 — SIMULAÇÃO DE COMBUSTÍVEL
# ============================================

else:
    st.header("⛽ Simulação de Custo de Combustível")

    col1, col2 = st.columns(2)
    distancia_total = col1.number_input("Distância total (km):", min_value=1, value=500)
    consumo_km_litro = col2.number_input("Consumo do veículo (km/l):", min_value=1, value=12)

    col3, col4 = st.columns(2)
    preco_combustivel = col3.number_input("Preço do combustível (R$/L):", min_value=0.1, value=5.99)
    num_viajantes = col4.number_input("Número de viajantes:", min_value=1, value=2)

    if st.button("Calcular Combustível"):
        resultado = calcular_combustivel(distancia_total, consumo_km_litro, preco_combustivel, num_viajantes)

        if resultado:
            st.success("Cálculo realizado com sucesso!")

            st.metric("Custo Total", resultado["custo_total_combustivel"])
            st.metric("Custo por Pessoa", resultado["custo_por_pessoa_combustivel"])

            with st.expander("Detalhamento completo"):
                st.write(f"Litros necessários: **{resultado['litros_necessarios']}**")
                st.write(f"Preço por litro: **{resultado['preco_combustivel']}**")
                st.write(f"Total de viajantes: **{resultado['num_viajantes']}**")
