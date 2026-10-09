"""Brazilian Portuguese narration and a beat-aligned F-PDV timeline."""
from pathlib import Path
import asyncio, json, math, ssl, subprocess
import edge_tts
import edge_tts.communicate as edge_module

ROOT=Path(__file__).resolve().parent
WORK=ROOT/'work'; WORK.mkdir(parents=True,exist_ok=True)
edge_module._SSL_CTX=ssl.create_default_context()
VOICE='pt-BR-AntonioNeural';RATE='+4%'
SEGMENTS=[
 dict(id='hook',title='Fila no caixa?',text='Fila no caixa?',spoken='Fila no caixa?'),
 dict(id='dor',title='A venda demora.\nO cliente espera.',text='Vendas lentas e tarefas manuais fazem o cliente esperar e aumentam o retrabalho.',spoken='Vendas lentas e tarefas manuais fazem o cliente esperar e aumentam o retrabalho.'),
 dict(id='conexao',title='F-PDV.\nVenda conectada.',text='Com o F-PDV da Frenty, sua loja conecta atendimento, estoque e emissão fiscal.',spoken='Com o éfe pê dê vê da Frenti, sua loja conecta atendimento, estoque e emissão fiscal.'),
 dict(id='agilidade',title='Mais agilidade\nno atendimento.',text='Venda com uma interface intuitiva e automatize a emissão das notas fiscais.',spoken='Venda com uma interface intuitiva e automatize a emissão das notas fiscais.'),
 dict(id='estoque',title='Venda e estoque.\nNo mesmo fluxo.',text='Atualize o estoque em tempo real e acompanhe os produtos disponíveis.',spoken='Atualize o estoque em tempo real e acompanhe os produtos disponíveis.'),
 dict(id='precisao',title='Menos tarefas\nmanuais.',text='Menos digitação repetida. Mais organização e precisão nas informações das vendas.',spoken='Menos digitação repetida. Mais organização e precisão nas informações das vendas.'),
 dict(id='relatorios',title='Enxergue suas\nvendas.',text='Acompanhe relatórios, identifique tendências e decida com mais clareza.',spoken='Acompanhe relatórios, identifique tendências e decida com mais clareza.'),
 dict(id='demo',title='Veja o F-PDV\nna sua loja.',text='Quer ver como funciona na sua loja? Agende uma demonstração gratuita do F-PDV.',spoken='Quer ver como funciona na sua loja? Agende uma demonstração gratuita do éfe pê dê vê.'),
 dict(id='cta',title='Agende sua\ndemonstração.',text='Acesse frenty.com.br e fale com o nosso time.',spoken='Acesse frenti ponto com ponto bê érre e fale com o nosso time.'),
]

def duration(path):
 return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],text=True))

async def generate(i,s,gate):
 path=WORK/f'voice-{i:02d}.mp3';meta=WORK/f'voice-{i:02d}.jsonl'
 async with gate:
  if not path.exists() or path.stat().st_size<1000:
   for attempt in range(3):
    try:
     c=edge_tts.Communicate(s['spoken'],voice=VOICE,rate=RATE,boundary='WordBoundary',connect_timeout=15,receive_timeout=30)
     await asyncio.wait_for(c.save(str(path),str(meta)),timeout=50);break
    except Exception:
     if attempt==2:raise
  s['audio']=path.name;s['duration']=duration(path)
  s['words']=[json.loads(x) for x in meta.read_text().splitlines() if x.strip()]
  print(json.dumps({'segment':i,'duration':s['duration'],'text':s['text']},ensure_ascii=False),flush=True)

async def main():
 gate=asyncio.Semaphore(2)
 await asyncio.gather(*(generate(i,s,gate) for i,s in enumerate(SEGMENTS)))
 at=0
 for i,s in enumerate(SEGMENTS):
  s['start']=at;s['voice_start']=at+.08;s['voice_end']=s['voice_start']+s['duration']
  at=math.ceil((s['voice_end']+.12)*2)/2
  if i==0:at=max(at,3)
  s['end']=at
 total=math.ceil((at+1.5)*2)/2
 if total>60:raise RuntimeError(f'Narration too long: {total}s. Edit script before render.')
 SEGMENTS[-1]['end']=total
 (ROOT/'roteiro.json').write_text(json.dumps(dict(voice=VOICE,rate=RATE,language='pt-BR',duration=total,fps=30,beat_period=.5,segments=SEGMENTS),ensure_ascii=False,indent=2))
 print(json.dumps({'duration':total,'starts':[s['start'] for s in SEGMENTS]}),flush=True)

asyncio.run(main())
