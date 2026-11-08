# Versionamento e GitHub

## Configuração em outro computador

1. Instale Git e confirme com `git --version`.
2. Defina a identidade local uma única vez: `git config --global user.name "Seu nome"` e `git config --global user.email "seu-email"`.
3. Clone o repositório público:

   ```bash
   git clone https://github.com/DevMantovani/tcc-monitoramento-fv.git
   cd tcc-monitoramento-fv
   ```

Não coloque token, senha, chaves, dados operacionais sensíveis, o ambiente `.venv`, artefatos gerados ou o artigo no repositório. As duas bases públicas explicitamente listadas em `data/raw/README.md` são exceções intencionais: possuem licença CC BY 4.0, são pequenas e permitem reproduzir o experimento principal. O `.gitignore` já protege os itens mais comuns; confirme com `git status` antes de cada commit.

## Fluxo ao trocar de computador

```bash
git pull --ff-only
# editar, executar e verificar
git status
git add src docs tests README.md HANDOFF_TCC.md
git commit -m "feat: descreve a mudança"
git push origin main
```

Use mensagens curtas no imperativo, como `feat: adiciona validação temporal`, `docs: registra fonte externa` ou `fix: rejeita potência negativa`. Um commit deve representar uma alteração coerente e verificável.

Se `git pull --ff-only` indicar divergência, não force nem apague arquivos. Pare, confira `git status` e resolva a divergência antes de continuar.
