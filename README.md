# Escultura AR — Crisia

Realidade mista via browser. Bolha luminosa pulsante ancorada na escultura de alumínio.

## Funciona em
- Meta Quest Browser (passthrough)
- Android Chrome
- iOS Safari (limitado)

---

## PASSO 1 — Compilar o marcador (fazer UMA VEZ, leva 2 min)

1. Abrir: https://hiukim.github.io/mind-ar-js-doc/tools/compile
2. Arrastar o arquivo `marker.svg` (ou exportar como PNG primeiro: abrir no browser → Print → Salvar como PDF → converter, ou usar qualquer conversor SVG→PNG online)
3. Clicar em **"Compile"** e aguardar
4. Baixar o arquivo gerado: renomear para `targets.mind`
5. Colocar `targets.mind` nesta pasta (mesma pasta do `index.html`)

## PASSO 2 — Imprimir o marcador

- Imprimir `marker.svg` em papel branco, tamanho A4 ou A3
- Colar/fixar sobre (ou sob) a escultura de alumínio
- O papel deve estar visível para a câmera

## PASSO 3 — Publicar no GitHub Pages

```
git init
git add .
git commit -m "escultura ar"
gh repo create escultura-ar --public --push --source=.
```
Depois ativar GitHub Pages: Settings → Pages → Branch: main → Save

A URL gerada (ex: `https://usuario.github.io/escultura-ar`) é o link para abrir no Quest.

## PASSO 4 — Usar

1. Abrir a URL no Meta Quest Browser ou no celular
2. Clicar em INICIAR e permitir câmera
3. Apontar para o marcador sobre a escultura
4. A bolha aparece e pulsa sobre a forma da escultura

---

## Ajustes rápidos no código

Editar `index.html` para mudar:
- **Cor da bolha:** procurar `colorBody`, `colorRim`, `colorGlow` no shader
- **Velocidade do pulso:** mudar `* 1.8` e `* 3.1` no shader
- **Altura sobre a escultura:** mudar `0.02` em `bubbleMesh.position.set(0, 0, 0.02)` (em metros)
- **Tamanho da bolha:** mudar `new THREE.PlaneGeometry(0.5, 1.0)` — primeiro número = largura, segundo = altura (em metros)
