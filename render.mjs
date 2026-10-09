import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createRequire} from 'node:module';import {spawn} from 'node:child_process';import {once} from 'node:events';
const require=createRequire(import.meta.url),pwRoot=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,{chromium}=require(pwRoot?path.join(pwRoot,'playwright'):'playwright');
const root=path.dirname(fileURLToPath(import.meta.url)),story=JSON.parse(fs.readFileSync(path.join(root,'roteiro.json'))),duration=story.duration;
const mode=process.argv[2]||'qa',rev=process.argv[3]||'2',ss=Number(process.env.SS||(mode==='qa'?1:2));
if(mode!=='qa'){
 const qa=JSON.parse(fs.readFileSync(path.join(root,'qa-review.json')));
 if(qa.revision!==Number(rev)||Object.values(qa.scores).some(v=>v<8))throw new Error('Contact sheet review must score every category at least 8 before full render.');
}
const localChrome=path.resolve(root,'../.pdv-browser/chrome-linux/headless_shell');
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(fs.existsSync(localChrome)?localChrome:undefined),args:['--no-sandbox','--disable-dev-shm-usage','--hide-scrollbars','--disable-gpu']});
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
page.on('pageerror',e=>{throw e});await page.goto(pathToFileURL(path.join(root,'index.html')).href+'?render=1&ss='+ss);await page.evaluate(()=>window.ready);await page.evaluate(n=>window.setRevision(n),Number(rev));
// Lossless PNG straight from the canvas backing store: 1080x1920 at ss=1, 2160x3840 at ss=2
const frame=async()=>Buffer.from((await page.evaluate(()=>document.getElementById('c').toDataURL('image/png'))).split(',')[1],'base64');
console.log('Supersampling ss='+ss);
if(mode==='qa'){
 const dir=path.join(root,'qa','v'+rev);fs.mkdirSync(dir,{recursive:true});const beats=JSON.parse(fs.readFileSync(path.join(root,'beats.json'))).beats;
 for(let i=0;i<beats.length;i++){await page.evaluate(t=>window.seek(t),beats[i]);fs.writeFileSync(path.join(dir,String(i).padStart(3,'0')+'.png'),await frame());if(i%30===0)console.log('Contact frames',i,'/',beats.length)}
 const heroes=[0,1.5,...story.segments.map(s=>Math.min(s.end-.5,s.start+2.5)),duration-.5];
 for(const t of heroes){await page.evaluate(t=>window.seek(t),t);fs.writeFileSync(path.join(dir,'hero-'+t+'.png'),await frame())}
 // Review frames for the crossfade (u = 0 to 0.29 s after each cut) and for the first word of each caption
 for(const s of story.segments.slice(1))for(const d of [0,.1,.2,.29]){await page.evaluate(t=>window.seek(t),s.start+d);fs.writeFileSync(path.join(dir,'cut-'+s.start+'-'+d+'.png'),await frame())}
 const caps=JSON.parse(fs.readFileSync(path.join(root,'legendas.json'))).map(c=>c.start);
 for(const t of caps){await page.evaluate(x=>window.seek(x),t+.01);fs.writeFileSync(path.join(dir,'word-'+t.toFixed(3)+'.png'),await frame())}
 console.log('QA render complete',dir);
}else{
 fs.mkdirSync(path.join(root,'output'),{recursive:true});
 const output=path.join(root,'output','frenty-f-pdv-motion-'+duration+'s.mp4'),silent=path.join(root,'output','video-only.mp4'),frames=Math.round(duration*30);
 const ff=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','image2pipe','-c:v','png','-framerate','30','-i','pipe:0','-vf','scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int:out_color_matrix=bt709:out_range=tv,format=yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:v','libx264','-preset','slow','-tune','animation','-crf','15','-profile:v','high','-level','4.0','-an','-movflags','+faststart',silent],{stdio:['pipe','ignore','pipe']});
 ff.stderr.on('data',x=>process.stderr.write(x));let error=null;ff.on('error',e=>error=e);const completion=once(ff,'close');
 for(let n=0;n<frames;n++){await page.evaluate(t=>window.seek(t),n/30);const buf=await frame();if(!ff.stdin.write(buf))await once(ff.stdin,'drain');if(n%120===0)console.log('Rendered',n,'/',frames,'frames')}
 ff.stdin.end();const [code]=await completion;if(error||code)throw error||new Error('FFmpeg failed '+code);
 // The approved AAC track is copied as-is: no second encode of the narrated mix
 const mux=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-i',silent,'-i',path.join(root,'work','audio-final.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-t',String(duration),'-movflags','+faststart',output],{stdio:['ignore','ignore','pipe']});
 mux.stderr.on('data',x=>process.stderr.write(x));const [muxCode]=await once(mux,'close');if(muxCode)throw new Error('Mux failed '+muxCode);
 fs.unlinkSync(silent);console.log('Video ready',output)
}
await browser.close();
