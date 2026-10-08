# Versionamento e GitHub

## Antes do primeiro push

1. Instale Git e confirme com `git --version`.
2. Defina a identidade local uma única vez: `git config --global user.name "Seu nome"` e `git config --global user.email "seu-email"`.
3. Inicialize o repositório e faça o primeiro commit conforme o README.
4. Crie um repositório **vazio** no GitHub, sem README automático, e associe a URL como `origin`.

Não coloque token, senha, chaves, dados operacionais sensíveis ou o ambiente `.venv` no repositório. O `.gitignore` já protege os itens mais comuns; confirme com `git status` antes de cada commit.

## Fluxo ao trocar de computador

```bash
git pull --ff-only
# editar, executar e verificar
git status
git add src docs tests README.md
git commit -m "feat: descreve a mudança"
git push
```

Use mensagens curtas no imperativo, como `feat: adiciona validação temporal`, `docs: registra fonte externa` ou `fix: rejeita potência negativa`. Um commit deve representar uma alteração coerente e verificável.

Se `git pull --ff-only` indicar divergência, não force nem apague arquivos. Pare, confira `git status` e resolva a divergência antes de continuar.
