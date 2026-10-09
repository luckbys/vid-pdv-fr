# Frenty · F-PDV · Motion de 52 segundos

Vídeo vertical 1080 × 1920, 30 fps, com narração em português do Brasil, legendas incorporadas e trilha original. Identidade clara: fundo marfim, roxo, ciano e azul-marinho. O convite final é para uma demonstração gratuita.

## Usar e editar

Abra `index.html` no navegador e clique em **Reproduzir**. O arquivo contém as imagens, fontes e o áudio; a reprodução funciona sem conexão. O convite da cena final abre o agendamento da Frenty quando há conexão.

- `motion.template.html`: cenas, textos, cores, ícones, movimentos e contato. O parâmetro `?ss=2` desenha o canvas em 2×; é o que o render usa.
- `roteiro.json` e `roteiro.txt`: cenas e narração, com os tempos de cada palavra.
- `legendas.json` e `legendas.srt`: legendas temporizadas. O destaque por palavra usa os tempos de `roteiro.json`.
- `beats.json`: marcação de batidas e dos cortes entre cenas.
- `assets/`: logo oficial, ilustração 3D e fontes.
- `work/narracao.wav`: voz isolada.
- `work/trilha-original.wav`: música com efeitos.
- `work/audio-final.wav` e `work/audio-final.m4a`: mixagem aprovada. O m4a é a faixa copiada para o MP4.
- `postagem.txt`: legenda sugerida para a publicação.

Depois de editar o template ou os arquivos JSON, execute `python3 build.py` para atualizar o HTML. Para alterar o texto falado, edite `SEGMENTS` em `narracao.py`, remova somente os trechos `voice-XX.mp3` e `voice-XX.jsonl` que deseja gerar novamente e execute `narracao.py`, `audio.py` e `build.py`, nessa ordem. A geração de voz depende de conexão.

Neste repositório, `assets/` e `work/` não estão versionados. O `index.html` incorpora fontes, logo, ilustração e áudio, então ele funciona sozinho. Para regenerar o MP4 a partir do zero, restaure essas pastas.

## Gerar outro MP4

Requer:

- Python 3 com `Pillow` (folhas de contato). Para regenerar voz e mixagem: `numpy`, `scipy` e `edge-tts`.
- Node.js com `playwright` e Chromium instalado.
- FFmpeg e FFprobe no PATH, com `libx264`. O Chromium pode ser indicado por `CHROME_PATH`.

```bash
python3 build.py
node render.mjs qa 3
python3 contact.py 3
node render.mjs video 3
```

Como o render funciona:

- Cada quadro é lido do próprio canvas em PNG, sem perda, desenhado em 2× (2160 × 3840) e reduzido para 1080 × 1920 com Lanczos. `SS=1 node render.mjs video 3` gera uma versão rápida para testar.
- A conversão RGB → YUV usa a matriz BT.709 explícita e intervalo limitado. Sem essa linha, o roxo da marca sai com erro de até 10 níveis.
- H.264 High, nível 4.0, `-preset slow -tune animation -crf 15`.
- A faixa AAC aprovada é copiada para o MP4 sem nova codificação.
- O arquivo final vai para `output/`.

Revise as folhas de contato e atualize `qa-review.json` quando fizer mudanças criativas. O renderizador exige que a revisão informada seja a do arquivo e que todas as notas sejam 8 ou mais antes da exportação. As notas devem refletir a revisão feita, não ser preenchidas para passar no gate.

## Entrega aprovada (revisão 3)

52 segundos, 1560 quadros, H.264 High nível 4.0, yuv420p, BT.709 com intervalo limitado, AAC-LC 44,1 kHz estéreo com a faixa aprovada copiada. Tamanho: 6,7 MB. A entrega anterior tinha 5,8 MB, com CRF 16 e preset `fast`.

Áudio medido no MP4: −14,00 LUFS, pico verdadeiro −2,22 dBTP, faixa de loudness 3,6 LU. Decodificação completa sem erros.

Qualidade medida nas 104 batidas, contra uma referência renderizada em 2× e reduzida com Lanczos, no mesmo template:

- PSNR médio da luminância: 56,98 dB. SSIM médio: 0,99946.
- Roxo `#5B2EAA` no quadro final: erro máximo de 1 nível. Com o pipeline anterior, o mesmo ponto saía com erro de 3 níveis.
- Controle com o pipeline anterior no mesmo template, em SS=1: PSNR médio da luminância de 41,9 dB e SSIM de 0,99635. Essa comparação mistura o efeito da captura e do encode com o do supersampling, porque a referência é em 2×.

Transições: a maior variação de um quadro para o seguinte nos cortes caiu de 40,5 para 15,3 níveis por canal (medido no canvas). A troca de cena agora é um crossfade de 0,3 s.

Revisado: 104 quadros de batida em folhas de contato, verificação em tamanho real da varredura na nota fiscal, do gráfico e do destaque por palavra, e as nove cenas extraídas do próprio MP4.

`verification.json` registra as medições técnicas; `qa-review.json` registra a revisão editorial. As notas editoriais avaliam a peça criada e não representam resultados de conversão de campanha.

## O que mudou na revisão 3

- Títulos com um tamanho comum (o hook é um pouco maior). Texto em tela com no mínimo 30 px, incluindo rodapé e rótulos.
- A varredura da cena 4 corre dentro da nota fiscal. O hero das cenas 4 e 8 ficou menor para não cobrir os chips nem o botão.
- Gráfico com linhas-guia tracejadas. O pico da linha de tendência não é mais cortado.
- Ícones do conjunto Lucide (licença ISC), em roxo sobre discos ciano-claros.
- Destaque por palavra na legenda, com os tempos da narração.
- Crossfade de 0,3 s entre cenas, no lugar do corte seco.
- Player: foco visível pelo teclado e controles adaptados ao celular.

## Ressalvas

- **Zona de interface do app.** Com o layout mantido, a legenda (y ≈ 1490–1636) e o rodapé (y ≈ 1680–1730) ficam na faixa inferior que o Reels e o TikTok podem cobrir com legenda e botões. O badge do topo fica perto da faixa superior. Não há medida oficial para conteúdo orgânico; as estimativas de terceiros vão de ~250 a ~480 px na base. Confira no preview do aplicativo antes de publicar.
- **Destaque por palavra.** 17 das 24 legendas usam os tempos de palavra da narração. As outras 7 têm marcas soletradas na voz ("éfe pê dê vê", "frenti ponto com ponto bê érre"). Nelas, o destaque é distribuído por caractere dentro da janela da legenda e pode adiantar ou atrasar a fala por uma fração de segundo.

## Créditos

Ícones: [Lucide](https://lucide.dev), licença ISC, a partir do pacote `lucide-static` 1.54.0. Os paths foram copiados do pacote e usados na assinatura `icon()`.

---

Os recursos do produto vêm do texto fornecido para este trabalho. O gráfico é ilustrativo e não contém dados comerciais. O logo é o arquivo oficial da Frenty, preservado. O site mostrado é **frenty.com.br** e o WhatsApp é **(11) 9 4841-1000**.
