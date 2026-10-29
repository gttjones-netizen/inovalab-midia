// Uso:
//   node render.js <workdir> stills 1.5,8.2,14.0   -> <workdir>/still_<t>.jpg + contact sheet via scripts/contact.py
//   node render.js <workdir> video <saida.mp4>     -> vídeo mudo 1080x1920 30fps
// <workdir> precisa ter roteiro.json, v/f0001.jpg... e os quadros limpos citados no roteiro.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const http = require('http'), fs = require('fs'), path = require('path');
const SKILL = path.resolve(__dirname, '..');
const WORK = path.resolve(process.argv[2] || '.');
const mode = process.argv[3] || 'stills';
const TYPES = { '.html': 'text/html', '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png', '.woff2': 'font/woff2', '.js': 'text/javascript' };
const srv = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split('?')[0]);
  let p = null;
  if (u.startsWith('/skill/')) p = path.join(SKILL, u.slice(7));
  else if (u.startsWith('/work/')) p = path.join(WORK, u.slice(6));
  if (!p) { res.writeHead(404); return res.end(); }
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); return res.end(); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(d); });
});
srv.listen(0, async () => {
  const port = srv.address().port;
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  pg.on('pageerror', e => console.log('ERRO NA PÁGINA:', e.message));
  await pg.goto(`http://localhost:${port}/skill/engine/index.html`);
  const info = await pg.evaluate(() => preload());
  console.log('preload', JSON.stringify(info));
  if (info.missing) console.log(`ATENÇÃO: ${info.missing} imagens não encontradas`);
  const grab = async () => Buffer.from((await pg.evaluate(() => document.getElementById('c').toDataURL('image/jpeg', 0.95))).split(',')[1], 'base64');
  if (mode === 'stills') {
    for (const t of process.argv[4].split(',').map(Number)) {
      await pg.evaluate(t => render(t), t);
      fs.writeFileSync(path.join(WORK, `still_${t.toFixed(2)}.jpg`), await grab());
    }
  } else {
    const out = path.resolve(process.argv[4]);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = Math.round(info.dur * 30);
    for (let f = 0; f < N; f++) {
      await pg.evaluate(t => render(t), f / 30);
      const buf = await grab();
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (f % 90 === 0) console.log('quadro', f, '/', N);
    }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
    console.log('ok', out);
  }
  await b.close(); srv.close();
});
