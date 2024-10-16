-- Questao 1 - operação de crédito, a sua faixa de risco no momento da contratação, além disso devem ser retornados apenas os resultados com risco
-- “médio alto” ou superior, pois foram concedidos fora da regra. Ao menos as seguintes colunas devem ser trazidas: “CPF”, “Código do Título”, “Data da Contratação” e “Faixa de Risco”. 

SELECT 
    co.cod_cpf AS "CPF",
    co.cod_titulo_credito AS "Código do Título",
    co.dat_contrat_credito AS "Data da Contratação",
    fr.des_faixa_risco AS "Faixa de Risco"
FROM 
    credito_operacoes co
JOIN 
    faixa_risco fr ON co.cod_cpf = fr.cod_cpf
WHERE 
    co.dat_contrat_credito BETWEEN fr.dat_inicio_faixa AND fr.dat_fim_faixa
    AND fr.cod_faixa_risco >= 5
ORDER BY 
    co.dat_contrat_credito;



-- Questao 2 - Retornar a faixa de risco de cada operação no momento da concessão e todas as faixas subsequentes, 
-- filtrando apenas operações com risco "médio" ou inferior no momento da concessão.

SELECT 
    co.cod_cpf AS "CPF",
    co.cod_titulo_credito AS "Código do Título",
    co.dat_contrat_credito AS "Data da Contratação",
    fr.dat_inicio_faixa AS "Data Inicial da Faixa",
    fr.dat_fim_faixa AS "Data Final da Faixa",
    fr.des_faixa_risco AS "Faixa de Risco"
FROM 
    credito_operacoes co
JOIN 
    faixa_risco fr ON co.cod_cpf = fr.cod_cpf
WHERE 
    fr.dat_inicio_faixa >= co.dat_contrat_credito
    AND EXISTS (
        SELECT 1
        FROM faixa_risco fr_concessao
        WHERE fr_concessao.cod_cpf = co.cod_cpf
            AND co.dat_contrat_credito BETWEEN fr_concessao.dat_inicio_faixa AND fr_concessao.dat_fim_faixa
            AND fr_concessao.cod_faixa_risco <=                                                                                                     4
    )
ORDER BY 
    co.cod_cpf, co.cod_titulo_credito, fr.dat_inicio_faixa;