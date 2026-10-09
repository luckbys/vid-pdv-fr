import fs from 'node:fs';import path from 'node:path';import {fileURLToPath,pathToFileURL} from 'node:url';import {createRequire} from 'node:module';import {spawn} from 'node:child_process';import {once} from 'node:events';
const require=createRequire(import.meta.url),pwRoot=process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES,{chromium}=require(pwRoot?path.join(pwRoot,'playwright'):'playwright');
const root=path.dirname(fileURLToPath(import.meta.url)),story=JSON.parse(fs.readFileSync(path.join(root,'roteiro.json'))),duration=story.duration;
const mode=process.argv[2]||'qa',rev=process.argv[3]||'2';
if(mode!=='qa'){
 const qa=JSON.parse(fs.readFileSync(path.join(root,'qa-review.json')));
 if(qa.revision!==Number(rev)||Object.values(qa.scores).some(v=>v<8))throw new Error('Contact sheet review must score every category at least 8 before full render.');
}
const localChrome=path.resolve(root,'../.pdv-browser/chrome-linux/headless_shell');
const browser=await chromium.launch({headless:true,executablePath:process.env.CHROME_PATH||(fs.existsSync(localChrome)?localChrome:undefined),args:['--no-sandbox','--disable-dev-shm-usage','--hide-scrollbars','--disable-gpu']});
const page=await browser.newPage({viewport:{width:1080,height:1920},deviceScaleFactor:1});
page.on('pageerror',e=>{throw e});await page.goto(pathToFileURL(path.join(root,'index.html')).href+'?render=1');await page.evaluate(()=>window.ready);await page.evaluate(n=>window.setRevision(n),Number(rev));
if(mode==='qa'){
 const dir=path.join(root,'qa','v'+rev);fs.mkdirSync(dir,{recursive:true});const beats=JSON.parse(fs.readFileSync(path.join(root,'beats.json'))).beats;
 for(let i=0;i<beats.length;i++){await page.evaluate(t=>window.seek(t),beats[i]);await page.screenshot({path:path.join(dir,String(i).padStart(3,'0')+'.jpg'),type:'jpeg',quality:88});if(i%30===0)console.log('Contact frames',i,'/',beats.length)}
 const heroes=[0,1.5,...story.segments.map(s=>Math.min(s.end-.5,s.start+2.5)),duration-.5];
 for(const t of heroes){await page.evaluate(t=>window.seek(t),t);await page.screenshot({path:path.join(dir,'hero-'+t+'.png')})}
 console.log('QA render complete',dir);
}else{
 fs.mkdirSync(path.join(root,'output'),{recursive:true});
 const output=path.join(root,'output','frenty-f-pdv-motion-'+duration+'s.mp4'),frames=Math.round(duration*30);
 const ff=spawn('ffmpeg',['-hide_banner','-loglevel','warning','-y','-f','image2pipe','-vcodec','mjpeg','-r','30','-i','pipe:0','-i',path.join(root,'work','audio-final.wav'),'-map','0:v:0','-map','1:a:0','-vf','scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=pc:out_range=tv,format=yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:v','libx264','-preset','fast','-crf','16','-pix_fmt','yuv420p','-threads','4','-c:a','aac','-b:a','192k','-ar','44100','-t',String(duration),'-movflags','+faststart',output],{stdio:['pipe','ignore','pipe']});
 ff.stderr.on('data',x=>process.stderr.write(x));let error=null;ff.on('error',e=>error=e);const completion=once(ff,'close');
 for(let n=0;n<frames;n++){await page.evaluate(t=>window.seek(t),n/30);const buf=await page.screenshot({type:'jpeg',quality:96});if(!ff.stdin.write(buf))await once(ff.stdin,'drain');if(n%120===0)console.log('Rendered',n,'/',frames,'frames')}
 ff.stdin.end();const [code]=await completion;if(error||code)throw error||new Error('FFmpeg failed '+code);console.log('Video ready',output)
}
await browser.close();
