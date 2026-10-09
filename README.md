# Frenty · F-PDV · Motion de 52 segundos

Vídeo vertical 1080 × 1920, 30 fps, com narração em português do Brasil, legendas incorporadas e trilha original. Identidade clara: fundo marfim, roxo, ciano e azul-marinho. O convite final é para uma demonstração gratuita.

## Usar e editar

Abra `index.html` no navegador e clique em **Reproduzir**. O arquivo contém as imagens, fontes e o áudio; a reprodução funciona sem conexão. O convite da cena final abre o agendamento da Frenty quando há conexão.

- `motion.template.html`: cenas, textos, cores, ilustrações, movimentos e contato.
- `roteiro.json` e `roteiro.txt`: cenas e narração, com tempos.
- `legendas.json` e `legendas.srt`: legendas temporizadas.
- `beats.json`: marcação de batidas e transições.
- `assets/`: logo oficial, ilustração 3D e fontes.
- `work/narracao.wav`: voz isolada.
- `work/trilha-original.wav`: música com efeitos.
- `work/audio-final.wav` e `work/audio-final.m4a`: mixagem aprovada.
- `postagem.txt`: legenda sugerida para a publicação.

Depois de editar o template ou os arquivos JSON, execute `python3 build.py` para atualizar o HTML. Para alterar o texto falado, edite `SEGMENTS` em `narracao.py`, remova somente os trechos `voice-XX.mp3` e `voice-XX.jsonl` que deseja gerar novamente e execute `narracao.py`, `audio.py` e `build.py`, nessa ordem. A geração de voz depende de conexão. Os trechos de voz usados nesta entrega estão incluídos.

## Gerar outro MP4

Requer Python 3 com `numpy`, `scipy`, `Pillow` e `edge-tts`; Node.js com `playwright` e Chromium instalado; FFmpeg e FFprobe disponíveis no PATH. O Chromium pode ser indicado por `CHROME_PATH`.

```bash
python3 build.py
node render.mjs qa 2
python3 contact.py 2
node render.mjs video 2
```

Revise as folhas de contato e atualize `qa-review.json` quando fizer mudanças criativas. O renderizador verifica a revisão e as notas de criação antes da exportação e cria a pasta `output/` automaticamente.

## Entrega aprovada

52 segundos, 1560 quadros, H.264/YUV420p/BT.709, AAC estéreo a 44,1 kHz. Áudio medido no MP4: −14,00 LUFS, pico verdadeiro −2,22 dBTP. Decodificação completa sem erros. Foram revisados 104 quadros por batida e nove cenas extraídas do MP4.

`verification.json` registra a validação técnica; `qa-review.json` registra a avaliação editorial. As notas editoriais avaliam a peça criada e não representam resultados de conversão de campanha.

Os recursos do produto vêm do texto fornecido para este trabalho. O gráfico é ilustrativo e não contém dados comerciais. O logo é o arquivo oficial da Frenty, preservado. O site mostrado é **frenty.com.br** e o WhatsApp é **(11) 9 4841-1000**.
